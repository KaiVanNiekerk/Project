from __future__ import annotations

import dataclasses
import json
import os
import sys
from pathlib import Path

import torch
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from baselines.baseline_trainer import BaselineTrainer
from baselines.koopa_model import ProbabilisticKoopa
from baselines.patchtst_model import ProbabilisticPatchTST
from CLI import CLI
from metrics import nmae
from plot_data import PlotDataCollector
from plotting import EpochHistory, PlotManager


# Long-term forecasting horizons used in the paper's tables.
DEFAULT_HORIZONS = [96, 192, 336, 720]


def run_horizon(model_name: str, config_path: Path, config: dict, target_window: int) -> dict:
    """Train one isolated baseline at one horizon using the shared CLI splits and plot contract."""
    max_epochs = int(os.environ.get("MAX_EPOCHS", "10"))
    batch_size = int(os.environ.get("BATCH_SIZE", "32"))
    use_wandb = os.environ.get("USE_WANDB", "false").lower() in ("true", "1", "yes")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tag = f"L{target_window}"

    hp = config["hyperparameters"]
    context_window = config["input_window"]

    cli = CLI(datasets_dir="datasets")
    train_loader, val_loader, test_loader, _, _, scaler = cli.load(
        config["csv_path"], context_window, target_window, config["patch_size"], batch_size=batch_size
    )
    x_context, _ = next(iter(train_loader))
    num_features = x_context.shape[2]

    if model_name == "koopa":
        model = ProbabilisticKoopa(
            c_in=num_features,
            context_window=context_window,
            target_window=target_window,
            seg_len=int(os.environ.get("KOOPA_SEG_LEN", str(config["patch_size"]))),
            dynamic_dim=int(os.environ.get("KOOPA_DYNAMIC_DIM", "64")),
            num_blocks=int(os.environ.get("KOOPA_NUM_BLOCKS", "2")),
            sigma_floor=0.05,
        )
    elif model_name == "patchtst":
        patch_len = int(os.environ.get("PATCH_LEN", str(config["patch_size"])))
        model = ProbabilisticPatchTST(
            c_in=num_features,
            context_window=context_window,
            target_window=target_window,
            patch_len=patch_len,
            stride=int(os.environ.get("PATCH_STRIDE", str(max(1, patch_len // 2)))),
            dropout=hp.get("integrator", {}).get("dropout", 0.1),
            sigma_floor=0.05,
            d_model=128,
            n_heads=8,
            n_layers=3,
            d_ff=256,
        )
    else:
        raise ValueError("BASELINE_MODEL must be 'patchtst' or 'koopa'")

    run_name = f"{model_name.title()}-{config['dataset_name']}"
    trainer = BaselineTrainer(
        model=model,
        optimizer=torch.optim.Adam(model.parameters(), lr=hp["lr"], weight_decay=1e-4),
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        use_wandb=use_wandb,
        checkpoint_name=f"{model_name}_{config['dataset_name']}_{tag}.pt",
    )

    result = trainer.fit(max_epochs)
    trainer.load_checkpoint()
    evaluation = trainer.evaluate(test_loader, compute_crps=True, crps_samples=100)

    # Detach and move to CPU before conversion to numpy
    y = evaluation["X_H"].detach().cpu().numpy()
    prediction = evaluation["mu"].detach().cpu().numpy()
    features = y.shape[-1]

    y_original = scaler.inverse_transform(y.reshape(-1, features))
    prediction_original = scaler.inverse_transform(prediction.reshape(-1, features))
    original_nmae = nmae(torch.from_numpy(y_original), torch.from_numpy(prediction_original))

    # Defensive lookup for best validation loss/NLL
    best_val_loss = result.get("best_val_nll", result.get("best_val_loss", 0.0))

    print({
        "model": model_name,
        "device": device,
        "best_epoch": result.get("best_epoch", -1),
        "best_val_loss": best_val_loss,
        "test_losses": evaluation["losses"],
        "original_nmae": float(original_nmae),
        "skipped_batches": evaluation["n_skipped"],
    })

    metrics = {
        "model": model_name,
        "dataset": config["dataset_name"],
        "input_window": context_window,
        "horizon": target_window,
        "nmae": float(original_nmae),
        "crps": float(evaluation["losses"]["crps"]),
        "test_losses": {k: float(v) for k, v in evaluation["losses"].items()},
        "best_epoch": result.get("best_epoch", -1),
    }
    results_dir = Path("artifacts/results") / run_name
    results_dir.mkdir(parents=True, exist_ok=True)
    with (results_dir / f"{tag}.json").open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)

    plot_config = dataclasses.replace(
        PlotDataCollector.load_dataset_plot_config(config_path), horizon_window=target_window
    )
    plot_manager = PlotManager(plot_config, run_id=run_name)

    # Populate skipped_batches to satisfy EpochHistory dataclass
    history = EpochHistory(
        epoch=trainer.history.epoch,
        train_total=trainer.history.train_nll,
        val_total=trainer.history.val_nll,
        train_elbo=trainer.history.train_nll,
        val_elbo=trainer.history.val_nll,
        train_nll=trainer.history.train_nll,
        val_nll=trainer.history.val_nll,
        train_kl=[0.0] * len(trainer.history.epoch),
        val_kl=[0.0] * len(trainer.history.epoch),
        train_rec=[0.0] * len(trainer.history.epoch),
        val_rec=[0.0] * len(trainer.history.epoch),
        skipped_batches=getattr(trainer.history, "skipped_batches", [0] * len(trainer.history.epoch)),
    )

    for index, figure in enumerate(plot_manager.plot_loss_curves(history)):
        plot_manager.save(figure, f"loss_curves_{index}_{tag}")

    forecast = PlotDataCollector(scaler=scaler).collect_forecast_batch(
        x_h_true=evaluation["X_H"],
        x_h_mu=evaluation["mu"],
        x_h_sigma=evaluation["sigma"],
        x_c_true=evaluation["X_C"],
        num_features=features,
        patch_size=config["patch_size"],
        inverse_scale=True,
        patched=False,
    )
    plot_manager.save(plot_manager.plot_forecast_vs_truth(forecast, feature_idx=list(range(min(6, features)))), f"forecast_vs_truth_{tag}")
    plot_manager.save(plot_manager.plot_residual_by_horizon(PlotDataCollector.compute_horizon_residuals(forecast)), f"residual_by_horizon_{tag}")
    return metrics


def main() -> None:
    model_name = os.environ.get("BASELINE_MODEL", "patchtst").lower()
    config_path = Path(os.environ.get("DATASET_CONFIG", "configs/datasets_yaml/Etth1-L.yaml"))
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    # HORIZONS="96,192" restricts the sweep, e.g. for smoke tests.
    horizons = [
        int(h) for h in os.environ.get("HORIZONS", "").split(",") if h.strip()
    ] or DEFAULT_HORIZONS

    all_metrics = []
    for horizon in horizons:
        print(f"\n===== {model_name} | {config['dataset_name']} | horizon L={horizon} =====")
        all_metrics.append(run_horizon(model_name, config_path, config, horizon))

    print("\nHorizon | NMAE | CRPS")
    for m in all_metrics:
        print(f"{m['horizon']:>7} | {m['nmae']:.4f} | {m['crps']:.4f}")
    summary_dir = Path("artifacts/results") / f"{model_name.title()}-{config['dataset_name']}"
    with (summary_dir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(all_metrics, handle, indent=2)


if __name__ == "__main__":
    main()