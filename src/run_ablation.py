from __future__ import annotations

import dataclasses
import json
import os
from pathlib import Path

import numpy as np
import torch
import yaml
from torch.utils.data import DataLoader

from CLI import CLI
from k2vae import K2VAE
from metrics import nmae
from plot_data import PlotDataCollector
from plotting import PlotManager
from train import Trainer


DEFAULT_ABLATIONS = [
    {"name": "beta-yaml-lambda-yaml", "koopman_mode": "mixed", "use_revin": True},
    {"name": "koopman-static", "koopman_mode": "static", "use_revin": True},
    {"name": "koopman-dynamic", "koopman_mode": "dynamic", "use_revin": True},
    {"name": "beta-0-lambda-yaml", "koopman_mode": "mixed", "use_revin": True, "beta": 0.0},
    {"name": "beta-1-lambda-1", "koopman_mode": "mixed", "use_revin": True, "beta": 1.0, "lambda_rec": 1.0},
    {"name": "beta-yaml-lambda-0", "koopman_mode": "mixed", "use_revin": True, "lambda_rec": 0.0},
    {"name": "beta-0-lambda-0", "koopman_mode": "mixed", "use_revin": True, "beta": 0.0, "lambda_rec": 0.0},
    {"name": "no-revin", "koopman_mode": "mixed", "use_revin": False},
]


def run_ablation(cfg: dict, ablation: dict, config_path: Path, seed: int) -> dict:
    """Train one ETTh1 ablation and persist its metrics and plots."""
    torch.manual_seed(seed)
    np.random.seed(seed)

    hp = cfg["hyperparameters"]
    beta = hp["kl_weight"] if "beta" not in ablation else ablation["beta"]
    lambda_rec = hp["lambda_rec"] if "lambda_rec" not in ablation else ablation["lambda_rec"]
    cli = CLI(datasets_dir="datasets")
    train_loader, val_loader, test_loader, n, m, scaler = cli.load(
        cfg["csv_path"], T=cfg["input_window"], L=cfg["horizon_window"],
        patch_size=cfg["patch_size"], batch_size=int(os.environ.get("BATCH_SIZE", "32")),
    )
    # CRPS constructs pairwise differences across predictive samples, so use a
    # smaller evaluation batch than training to keep that metric within GPU memory.
    eval_loader = DataLoader(
        test_loader.dataset,
        batch_size=int(os.environ.get("EVAL_BATCH_SIZE", "32")),
        shuffle=False,
    )
    x_context, _ = next(iter(train_loader))
    num_features = x_context.shape[2]
    integrator = {**hp["integrator"], "d": hp["d"], "n": n, "m": m}
    model = K2VAE(
        input_dim=num_features * cfg["patch_size"], d=hp["d"], m=m, n=n,
        integrator_args=integrator, num_vars=num_features,
        patch_size=cfg["patch_size"], hidden_dim=hp["hidden_dim"],
        hidden_layers=hp["hidden_layers"], sigma_floor=0.05,
        use_revin=ablation["use_revin"], koopman_mode=ablation["koopman_mode"],
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    run_id = ablation["name"]
    trainer = Trainer(
        model=model,
        optimizer=torch.optim.Adam(model.parameters(), lr=hp["lr"], weight_decay=1e-4),
        train_loader=train_loader, val_loader=val_loader,
        lambda_rec=lambda_rec, kl_weight=beta, device=device,
        use_wandb=False, seed=seed,
        checkpoint_dir=f"checkpoints/ablations/{cfg['dataset_name']}",
        checkpoint_name=f"{run_id}.pt",
    )
    result = trainer.fit(maxEpochs=int(os.environ.get("MAX_EPOCHS", "100")))
    trainer.load_checkpoint()
    evaluation = trainer.evaluate(eval_loader, compute_crps=True, crps_samples=100)
    y = evaluation["X_H"].numpy()
    prediction = evaluation["mu"].numpy()
    variables = y.shape[-1]
    y_original = scaler.inverse_transform(y.reshape(-1, variables))
    prediction_original = scaler.inverse_transform(prediction.reshape(-1, variables))
    metrics = {
        "dataset": cfg["dataset_name"], "ablation": run_id, "seed": seed,
        "koopman_mode": ablation["koopman_mode"], "use_revin": ablation["use_revin"],
        "beta": beta, "lambda_rec": lambda_rec,
        "best_epoch": result["best_epoch"], "best_val_total": result["best_val_loss"],
        "test_losses": {key: float(value) for key, value in evaluation["losses"].items()},
        "test_nmae_original": float(nmae(torch.from_numpy(y_original), torch.from_numpy(prediction_original))),
        "skipped_batches": result["nan_batches_skipped"],
    }
    results_dir = Path("artifacts/ablations") / cfg["dataset_name"] / run_id
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    plot_cfg = dataclasses.replace(PlotDataCollector.load_dataset_plot_config(config_path))
    plot_manager = PlotManager(plot_cfg, run_id=f"ablations/{cfg['dataset_name']}/{run_id}")
    for index, figure in enumerate(plot_manager.plot_loss_curves(trainer.history)):
        plot_manager.save(figure, f"loss_curves_{index}")
    forecast = PlotDataCollector(scaler=scaler).collect_forecast_batch(
        x_h_true=evaluation["X_H"], x_h_mu=evaluation["mu"], x_h_sigma=evaluation["sigma"],
        x_c_true=evaluation["X_C"], x_c_mu=evaluation["X_Rec"], num_features=variables,
        patch_size=cfg["patch_size"], inverse_scale=True, patched=False,
    )
    plot_manager.save(plot_manager.plot_forecast_vs_truth(forecast, feature_idx=list(range(min(6, variables)))), "forecast_vs_truth")
    plot_manager.save(plot_manager.plot_residual_by_horizon(PlotDataCollector.compute_horizon_residuals(forecast)), "residual_by_horizon")
    return metrics


def main() -> None:
    """Run the configured ETTh1 ablation matrix."""
    config_path = Path(os.environ.get("DATASET_CONFIG", "configs/datasets_yaml/ETTh1-L.yaml"))
    with config_path.open("r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle)
    seed = int(os.environ.get("SEED", "2026"))
    requested = os.environ.get("ABLATIONS", "").strip()
    selected = [item for item in DEFAULT_ABLATIONS if not requested or item["name"] in requested.split(",")]
    all_metrics = []
    for item in selected:
        print(f"\nETTh1-L ablation: {item['name']}", flush=True)
        all_metrics.append(run_ablation(cfg, item, config_path, seed))
    summary_dir = Path("artifacts/ablations") / cfg["dataset_name"]
    summary_dir.mkdir(parents=True, exist_ok=True)
    (summary_dir / "summary.json").write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()