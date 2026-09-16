from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

# Make the existing src modules available without changing their imports.
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from baselines.baseline_trainer import BaselineTrainer
from baselines.patchtst_model import ProbabilisticPatchTST
from CLI import CLI
from metrics import nmae
from plot_data import PlotDataCollector
from plotting import DatasetPlotConfig, EpochHistory, PlotManager


def main() -> None:
    """Train PatchTST on the same split and metric contract as K2VAE."""
    config_path = Path(
        os.environ.get("DATASET_CONFIG", "configs/datasets_yaml/ETTh1-L.yaml")
    )
    max_epochs = int(os.environ.get("MAX_EPOCHS", "10"))
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    hp = config["hyperparameters"]
    context_window = config["input_window"]
    target_window = config["horizon_window"]
    patch_len = int(os.environ.get("PATCH_LEN", str(config["patch_size"])))
    stride = int(os.environ.get("PATCH_STRIDE", str(max(1, patch_len // 2))))
    batch_size = int(os.environ.get("BATCH_SIZE", "32"))
    device = "cuda" if torch.cuda.is_available() else "cpu"

    cli = CLI(datasets_dir="datasets")
    train_loader, val_loader, test_loader, _, _, scaler = cli.load(
        config["csv_path"],
        T=context_window,
        L=target_window,
        patch_size=config["patch_size"],
        batch_size=batch_size,
    )
    x_context, _ = next(iter(train_loader))
    num_features = x_context.shape[2]

    model = ProbabilisticPatchTST(
        c_in=num_features,
        context_window=context_window,
        target_window=target_window,
        patch_len=patch_len,
        stride=stride,
        dropout=hp["integrator"]["dropout"],
        sigma_floor=0.05,
        d_model=128,
        n_heads=8,
        n_layers=3,
        d_ff=256,
    )
    trainer = BaselineTrainer(
        model=model,
        optimizer=torch.optim.Adam(model.parameters(), lr=hp["lr"], weight_decay=1e-4),
        train_loader=train_loader,
        val_loader=val_loader,
        device=device,
        checkpoint_name=f"patchtst_{config['dataset_name']}.pt",
    )
    result = trainer.fit(max_epochs)
    trainer.load_checkpoint()
    evaluation = trainer.evaluate(test_loader, compute_crps=True, crps_samples=100)

    y = evaluation["X_H"].numpy()
    prediction = evaluation["mu"].numpy()
    batch, horizon, variables = y.shape
    y_original = scaler.inverse_transform(y.reshape(-1, variables))
    prediction_original = scaler.inverse_transform(prediction.reshape(-1, variables))
    original_nmae = nmae(
        torch.from_numpy(y_original), torch.from_numpy(prediction_original)
    )
    print({
        "device": device,
        "best_epoch": result["best_epoch"],
        "best_val_nll": result["best_val_nll"],
        "test_losses": evaluation["losses"],
        "original_nmae": float(original_nmae),
        "skipped_batches": evaluation["n_skipped"],
    })

    plot_config = PlotDataCollector.load_dataset_plot_config(config_path)
    plot_manager = PlotManager(plot_config, run_id=f"PatchTST-{config['dataset_name']}")
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
    )
    for index, figure in enumerate(plot_manager.plot_loss_curves(history)):
        plot_manager.save(figure, f"loss_curves_{index}")

    collector = PlotDataCollector(scaler=scaler)
    forecast = collector.collect_forecast_batch(
        x_h_true=evaluation["X_H"],
        x_h_mu=evaluation["mu"],
        x_h_sigma=evaluation["sigma"],
        x_c_true=evaluation["X_C"],
        num_features=num_features,
        patch_size=config["patch_size"],
        inverse_scale=True,
        patched=False,
    )
    plot_manager.save(
        plot_manager.plot_forecast_vs_truth(
            forecast, feature_idx=list(range(min(6, num_features)))
        ),
        "forecast_vs_truth",
    )
    plot_manager.save(
        plot_manager.plot_residual_by_horizon(
            PlotDataCollector.compute_horizon_residuals(forecast)
        ),
        "residual_by_horizon",
    )


if __name__ == "__main__":
    main()
