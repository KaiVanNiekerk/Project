# MADE BY CLAUDE TO SEE IF WORKS!!!
import torch
import yaml
from pathlib import Path

from CLI import CLI
from k2vae import K2VAE
from metrics import nmae
from train import Trainer
from plot_data import PlotDataCollector
from plotting import PlotManager


def main():
    # ---- config, the values a person actually changes per run ----
    #DATASET = "Synthetic.csv"
    #DATASET_NAME = Path(DATASET).stem
    #T, L, patch_size = 96, 96, 16
    #D = 64 # Tune
    #HIDDEN_DIM = 128
    #BATCH_SIZE = 32
    #LR = 1e-3  # Tune
    
    DATASET_CONFIG_PATH = Path("configs/datasets/ETTh1-S.yaml")
    with DATASET_CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    CSV_PATH = cfg["csv_path"]
    DATASET_NAME = cfg["dataset_name"]
    T, L, patch_size = cfg["input_window"], cfg["horizon_window"], cfg["patch_size"]

    hp = cfg["hyperparameters"]
    D = hp["d"]
    HIDDEN_DIM = hp["hidden_dim"]
    LR = hp["lr"]
    LAMBDA_REC = hp["lambda_rec"]
    #integ = hp["integrator"]
    
    MAX_EPOCHS = 4
    BATCH_SIZE = 32
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    GENERATE_PLOTS = False  # flip off for quick smoke tests
    LOG_TO_WANDB = False  # flip on for hyperparameter tuning runs (e.g., wandb sweeps)
    # ---- data ----
    cli = CLI(datasets_dir="datasets")
    train_loader, val_loader, test_loader, n, m, scaler = cli.load(
        CSV_PATH, T=T, L=L, patch_size=patch_size, batch_size=BATCH_SIZE
    )

    X_C, _ = next(iter(train_loader))
    input_dim = X_C.shape[1]
    num_features = input_dim // patch_size

    # ---- model ----
    # Might need to change this if we do want to tune for optimal params here, will use integ from above
    integrator_args = dict(
        d=D, d_model=D, n_heads=4, d_ff=D * 4, n_layers=2, n=n, m=m, dropout=0.05
    )
    model = K2VAE(input_dim=input_dim, d=D, m=m, n=n, integrator_args=integrator_args, hidden_dim=HIDDEN_DIM)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)

    # ---- train ----
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        train_loader=train_loader,
        val_loader=val_loader,
        lambda_rec=LAMBDA_REC, # tuned
        device=DEVICE,
        use_wandb=LOG_TO_WANDB,
        checkpoint_name=f"k2vae_{DATASET_NAME}.pt",
    )

    result = trainer.fit(maxEpochs=MAX_EPOCHS)
    print(result)
    
    # Load best checkpoint and evaluate on test set
    trainer.load_checkpoint()
    test_result = trainer.evaluate(test_loader, compute_crps=True, crps_samples=100)
    print(f"test losses: {test_result['losses']}")
    print(f"test batches: {test_result['n_batches']} (skipped {test_result['n_skipped']})")
    
    test_nmae = nmae(test_result["X_H"], test_result["mu"])
    print(f"test NMAE: {test_nmae.item():.4f}")
    print(f"test CRPS: {test_result['losses']['crps']:.4f}")
    
    # ---- plotting ----
    # NOTE: DatasetPlotConfig is hand-built here as a placeholder. Item 6
    # (dataset plot config YAML) will replace this with
    # plot_data.load_dataset_plot_config(path) once that YAML exists.
    if GENERATE_PLOTS:
        plot_cfg = PlotDataCollector.load_dataset_plot_config(DATASET_CONFIG_PATH)
        plot_manager = PlotManager(cfg=plot_cfg, run_id=DATASET_NAME)

        # Loss curves, from EpochHistory accumulated in Trainer.fit()
        loss_figs = plot_manager.plot_loss_curves(trainer.history)
        for i, fig in enumerate(loss_figs):
            plot_manager.save(fig, f"loss_curves_{i}")

        # Forecast vs truth + residuals, from the test-set tensors
        collector = PlotDataCollector(scaler=scaler)
        forecast_batch = collector.collect_forecast_batch(
            x_h_true=test_result["X_H"],
            x_h_mu=test_result["mu"],
            x_h_sigma=test_result["sigma"],
            x_c_true=test_result["X_C"],
            x_c_mu=test_result["X_Rec"],
            num_features=num_features,
            patch_size=patch_size,
            inverse_scale=True,
        )

        forecast_fig = plot_manager.plot_forecast_vs_truth(forecast_batch, feature_idx=0)
        plot_manager.save(forecast_fig, "forecast_vs_truth")

        residuals = PlotDataCollector.compute_horizon_residuals(forecast_batch)
        residual_fig = plot_manager.plot_residual_by_horizon(residuals)
        plot_manager.save(residual_fig, "residual_by_horizon")


if __name__ == "__main__":
    main()