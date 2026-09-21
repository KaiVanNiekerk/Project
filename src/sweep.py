import argparse
import json
import math
import os
import torch
import wandb
import yaml
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from CLI import CLI
from k2vae import K2VAE
from train import Trainer

"""
wandb sweep entry point, kept separate from run.py so hyperparameter tuning
runs never share a code path with normal single-config training/eval/plotting
runs.

Staged two-phase sweep (see configs/sweep_continuous.yaml and
configs/sweep_architecture.yaml for the search spaces and full per-phase
usage): continuous params (lr, kl_weight, lambda_rec) are tuned first via
Bayes with architecture held at the ETTh1-L.yaml reference values; then
architecture (d, hidden_dim, hidden_layers) is tuned via grid with the
continuous params held at Phase 1's winner. Chained via BASE_HP_OVERRIDES,
a JSON file of {param: value} that --analyze writes out after a phase
finishes and that main() reads back in as the "fixed" values for anything
not swept in the current phase:

    wandb sweep configs/sweep_continuous.yaml
    wandb agent --count 25 <sweep_id>
    python src/sweep.py --analyze <entity>/<project>/<sweep_id>
        -> artifacts/sweeps/<sweep_id>_best.json

    $env:BASE_HP_OVERRIDES = "artifacts/sweeps/<phase1_sweep_id>_best.json"
    wandb sweep configs/sweep_architecture.yaml
    wandb agent <sweep_id>
    python src/sweep.py --analyze <entity>/<project>/<sweep_id>

No test-set evaluation here, that stays a manual step once the sweep has
picked a winner (copy its values into the dataset YAML's hyperparameters
block, then run run.py normally).
"""

SWEPT_PARAMS = ["lr", "kl_weight", "lambda_rec", "d", "hidden_dim", "hidden_layers"]

DATASET_CONFIG_PATH = Path(os.environ.get("DATASET_CONFIG", "configs/datasets_yaml/ETTh1-L.yaml"))


def main():
    with DATASET_CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    CSV_PATH = cfg["csv_path"]
    DATASET_NAME = cfg["dataset_name"]
    T, L, patch_size = cfg["input_window"], cfg["horizon_window"], cfg["patch_size"]
    hp = cfg["hyperparameters"]
    integ = hp["integrator"]

    # Values a previous sweep phase already settled on (e.g. Phase 1's best
    # lr/kl_weight/lambda_rec), so Phase 2 fixes them instead of silently
    # falling back to the dataset YAML's original reference values.
    base_overrides_path = os.environ.get("BASE_HP_OVERRIDES")
    base_overrides = {}
    if base_overrides_path:
        with open(base_overrides_path, "r", encoding="utf-8") as f:
            base_overrides = json.load(f)

    wandb.init()
    sweep_cfg = wandb.config

    # Priority per hyperparameter: this phase's swept value > a previous
    # phase's winner (BASE_HP_OVERRIDES) > the dataset YAML's reference value.
    LR = sweep_cfg.get("lr", base_overrides.get("lr", hp["lr"]))
    D = sweep_cfg.get("d", base_overrides.get("d", hp["d"]))
    HIDDEN_DIM = sweep_cfg.get("hidden_dim", base_overrides.get("hidden_dim", hp["hidden_dim"]))
    HIDDEN_LAYERS = sweep_cfg.get("hidden_layers", base_overrides.get("hidden_layers", hp["hidden_layers"]))
    LAMBDA_REC = sweep_cfg.get("lambda_rec", base_overrides.get("lambda_rec", hp["lambda_rec"]))
    KL_WEIGHT = sweep_cfg.get("kl_weight", base_overrides.get("kl_weight", hp["kl_weight"]))

    # Record the full effective hyperparameter set on every run, not just
    # whatever this phase swept, so --analyze can compare Phase 1 and Phase 2
    # runs the same way regardless of which params were fixed vs swept.
    wandb.config.update(
        {
            "lr": LR, "d": D, "hidden_dim": HIDDEN_DIM, "hidden_layers": HIDDEN_LAYERS,
            "lambda_rec": LAMBDA_REC, "kl_weight": KL_WEIGHT,
        },
        allow_val_change=True,
    )

    MAX_EPOCHS = int(os.environ.get("MAX_EPOCHS", "60"))
    BATCH_SIZE = 32
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    cli = CLI(datasets_dir="datasets")
    train_loader, val_loader, test_loader, n, m, scaler = cli.load(
        CSV_PATH, T=T, L=L, patch_size=patch_size, batch_size=BATCH_SIZE
    )

    X_C, _ = next(iter(train_loader))
    num_features = X_C.shape[2]
    input_dim = num_features * patch_size

    integrator_args = dict(
        d=D, d_model=integ["d_model"], n_heads=integ["n_heads"],
        d_ff=integ["d_ff"], n_layers=integ["n_layers"],
        n=n, m=m, dropout=integ["dropout"],
    )
    model = K2VAE(
        input_dim=input_dim, d=D, m=m, n=n, integrator_args=integrator_args,
        num_vars=num_features, patch_size=patch_size,
        hidden_dim=HIDDEN_DIM, hidden_layers=HIDDEN_LAYERS,
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)

    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        lambda_rec=LAMBDA_REC,
        kl_weight=KL_WEIGHT,
        device=DEVICE,
        use_wandb=True,
        checkpoint_name=f"k2vae_{DATASET_NAME}_{wandb.run.id}.pt",
    )

    result = trainer.fit(maxEpochs=MAX_EPOCHS)
    wandb.log({"final_best_val_loss": result["best_val_loss"]})


# ---------------------------------------------------------------------------
# Sweep analysis: pulls finished runs back from the wandb API and plots how
# each swept hyperparameter relates to final val_total, to help pick a
# winner. This is a separate mode (--analyze), never called by wandb agent.
# ---------------------------------------------------------------------------

def _save_fig(fig: plt.Figure, out_dir: Path, name: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{name}.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out_path


def _sweep_results_df(sweep_path: str) -> pd.DataFrame:
    """One row per finished run: its swept hyperparameters + final_best_val_loss."""
    api = wandb.Api()
    sweep = api.sweep(sweep_path)

    rows = []
    for run in sweep.runs:
        if run.state != "finished":
            continue
        val_loss = run.summary.get("final_best_val_loss")
        if val_loss is None:
            continue
        row = {p: run.config.get(p) for p in SWEPT_PARAMS}
        row["val_total"] = val_loss
        row["run_id"] = run.id
        rows.append(row)

    return pd.DataFrame(rows)


def plot_param_sweeps(df: pd.DataFrame, out_dir: Path) -> Path:
    """One subplot per swept param: its value vs. every run's final val_total.

    Shows spread/trend per value (e.g. does lr=2e-3 cluster lower than
    lr=5e-4 across the other params), not just a single best point.
    """
    params = [p for p in SWEPT_PARAMS if p in df.columns]
    ncols = 3
    nrows = math.ceil(len(params) / ncols)
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5 * ncols, 4 * nrows))
    axes = np.array(axes).reshape(-1)

    for ax, param in zip(axes, params):
        ax.scatter(df[param].astype(str), df["val_total"], alpha=0.6)
        ax.set_xlabel(param)
        ax.set_ylabel("val_total")
        ax.set_title(param)
        ax.grid(alpha=0.3)
    for ax in axes[len(params):]:
        ax.axis("off")

    fig.suptitle("HP sweep: parameter value vs. final val_total")
    return _save_fig(fig, out_dir, "sweep_param_scatter")


def plot_top_runs(df: pd.DataFrame, out_dir: Path, top_k: int = 15) -> Path:
    """Bar chart of the best `top_k` runs by val_total, labeled by run id."""
    best = df.nsmallest(min(top_k, len(df)), "val_total")

    fig, ax = plt.subplots(figsize=(max(8, len(best) * 0.6), 4))
    ax.bar(best["run_id"], best["val_total"])
    ax.set_title(f"Top {len(best)} sweep runs by val_total")
    ax.set_ylabel("val_total")
    ax.tick_params(axis="x", labelrotation=45)
    ax.grid(axis="y", alpha=0.3)
    return _save_fig(fig, out_dir, "sweep_top_runs")


def analyze_sweep(sweep_path: str, output_root: str = "artifacts/plots") -> None:
    df = _sweep_results_df(sweep_path)
    if df.empty:
        print(f"No finished runs with a logged final_best_val_loss found for sweep {sweep_path}")
        return

    out_dir = Path(output_root) / sweep_path.replace("/", "_")
    scatter_path = plot_param_sweeps(df, out_dir)
    top_path = plot_top_runs(df, out_dir)

    best = df.loc[df["val_total"].idxmin()]
    best_hp = {
        p: (best[p].item() if hasattr(best[p], "item") else best[p])
        for p in SWEPT_PARAMS
        if p in df.columns and pd.notna(best[p])
    }

    # Every run now logs the full 6-param set (see main()'s wandb.config.update),
    # so this file is a complete hyperparameter snapshot usable as the next
    # phase's BASE_HP_OVERRIDES regardless of which params this phase swept.
    overrides_dir = Path("artifacts/sweeps")
    overrides_dir.mkdir(parents=True, exist_ok=True)
    overrides_path = overrides_dir / f"{sweep_path.replace('/', '_')}_best.json"
    with overrides_path.open("w", encoding="utf-8") as f:
        json.dump(best_hp, f, indent=2)

    print(f"{len(df)} finished run(s) analyzed")
    print(f"Saved: {scatter_path}")
    print(f"Saved: {top_path}")
    print(f"Saved: {overrides_path}")
    print(f"Best run: {best['run_id']} val_total={best['val_total']:.4f}")
    print(best_hp)
    print(f"Feed into the next phase with: BASE_HP_OVERRIDES={overrides_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--analyze",
        metavar="ENTITY/PROJECT/SWEEP_ID",
        default=None,
        help="Skip training; fetch a sweep's finished runs via the wandb API and save comparison plots instead.",
    )
    # wandb agent invokes this script with no extra args, so unknown args
    # (none expected, but future-proofing) are ignored rather than erroring.
    args, _ = parser.parse_known_args()

    if args.analyze:
        analyze_sweep(args.analyze)
    else:
        main()
