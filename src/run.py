# MADE BY CLAUDE TO SEE IF WORKS!!!
import torch

from CLI import CLI
from k2vae import K2VAE
from train import Trainer


def main():
    # ---- config, the values a person actually changes per run ----
    DATASET = "Synthetic"
    T, L, patch_size = 96, 96, 16
    D = 64
    HIDDEN_DIM = 128
    BATCH_SIZE = 32
    LR = 1e-3
    MAX_EPOCHS = 100
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

    # ---- data ----
    cli = CLI(datasets_dir="datasets")
    train_loader, val_loader, test_loader = cli.load(
        DATASET, T=T, L=L, patch_size=patch_size, batch_size=BATCH_SIZE
    )

    n, m = T // patch_size, L // patch_size

    X_C, _ = next(iter(train_loader))
    input_dim = X_C.shape[1]

    # ---- model ----
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
        lambda_rec=1.0,
        device=DEVICE,
        use_wandb=False,
    )

    result = trainer.fit(max_epochs=MAX_EPOCHS)
    print(result)


if __name__ == "__main__":
    main()