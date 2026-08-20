from pathlib import Path
from torch.utils.data import DataLoader
from torch.utils.data.dataloader import default_collate
 
from preprocessing import load_csv, split, scale, swDataset, k2vae_integration
from sklearn.preprocessing import StandardScaler
 
"""
Paper-specified (T, L) settings, Table 1 / Appendix C.1 (K^2VAE, Wu et al.).
Not wired in yet, T and L are passed explicitly to CLI.load() for now so
the pipeline can be smoke-tested end-to-end. Once stable this becomes a
YAML/JSON dataset registry (RoadMap.md Phase 0 checklist).
 
Short-term (T = L, single fixed horizon):
    ETTh1-S, ETTh2-S, ETTm1-S, ETTm2-S : T = L = 24
    Solar-S, Electricity-S, Traffic-S  : T = L = 24
    Exchange-S                         : T = L = 30
 
Long-term (T fixed, L swept over four horizons):
    ILI-L                              : T = 36, L in {24, 36, 48, 60}
    ETTh1-L, ETTh2-L, ETTm1-L, ETTm2-L,
    Electricity-L, Traffic-L,
    Exchange-L, Weather-L              : T = 96, L in {96, 192, 336, 720}
"""

def _patched_collate(patch_size: int):
    # swDataset yields raw (T, N) / (L, N) pairs. K2VAE.forward and elbo.py's
    # loss functions both expect (B, input_dim, patches) for X_C AND X_H
    # (input_dim = N * patch_size). k2vae_integration does patchify+flatten
    # without projection, so it's applied identically to both windows here,
    # at collate time, rather than inside swDataset itself.
    def collate(batch):
        X_C, X_H = default_collate(batch)          # (B, T, N), (B, L, N)
        X_C = k2vae_integration(X_C, patch_size)   # (B, input_dim, n)
        X_H = k2vae_integration(X_H, patch_size)   # (B, input_dim, m)
        return X_C, X_H
    return collate

class CLI:
    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = Path(datasets_dir)
        if not self.datasets_dir.exists():
            raise FileNotFoundError(f"datasets dir not found: {self.datasets_dir.resolve()}")
 
    # turns name into a path allows the CLI to be agnostic to the actual dataset file structure, 
    # and allows for easy extension to new datasets in the future
    # User will just enter ETTh1, the directory will be organised after.
    def scan(self) -> list[str]:
        return sorted(
            p.relative_to(self.datasets_dir).as_posix()
            for p in self.datasets_dir.rglob("*.csv")
        )
        
    # Returns error message if file not found, otherwise returns the path to the dataset file
    def resolve(self, csv_path: str) -> Path:
        path = self.datasets_dir / csv_path
        if not path.exists():
            available = ", ".join(self.scan()) or "(none found)"
            raise FileNotFoundError(f"'{csv_path}' not found under {self.datasets_dir}. Available: {available}")
        return path
 
    def load(
        self,
        csv_path: str,
        T: int,
        L: int,
        patch_size: int,
        train_frac: float = 0.7,
        val_frac: float = 0.15,
        batch_size: int = 32,
    ) -> tuple[DataLoader, DataLoader, DataLoader, int, int, StandardScaler]:
        
        # FLAG!!!!
        # Bring up with jake and kai: the resulting n = T // patch_size and m = L // patch_size
        # are NOT returned here, but K2VAE's constructor takes n and m as
        # explicit args and must be built with these exact values, or the
        # model will silently instantiate for the wrong shapes. Whoever
        # builds the model from this loader is responsible for recomputing
        # n = T // patch_size, m = L // patch_size to match.
        
        # n = T/patch_size and m = L/patch_size must both be integers,
        # enforced here, before swDataset construction, so a bad (T, L,
        # patch_size) combo fails loudly at the entry point rather than
        # deep inside patchify() during the first training step.
        if T % patch_size != 0:
            raise ValueError(f"T={T} not divisible by patch_size={patch_size} (n = T/patch_size must be an int)")
        if L % patch_size != 0:
            raise ValueError(f"L={L} not divisible by patch_size={patch_size} (m = L/patch_size must be an int)")
        
        n = T // patch_size
        m = L // patch_size
        
        df = load_csv(str(self.resolve(csv_path)))
        train_df, val_df, test_df = split(df, train_frac, val_frac)
        train_arr, val_arr, test_arr, scaler = scale(train_df, val_df, test_df)
 
        collate = _patched_collate(patch_size)
        train_loader = DataLoader(swDataset(train_arr, T, L), batch_size=batch_size, shuffle=True, collate_fn=collate)
        val_loader = DataLoader(swDataset(val_arr, T, L), batch_size=batch_size, shuffle=False, collate_fn=collate)
        test_loader = DataLoader(swDataset(test_arr, T, L), batch_size=batch_size, shuffle=False, collate_fn=collate)
 
        # scaler is returned so callers can inverse-transform predictions
        # back to the original data scale (needed by
        # plot_data.PlotDataCollector for plot-ready outputs).
        return train_loader, val_loader, test_loader, n, m, scaler
        
def smoke_test():
    cli = CLI(datasets_dir="datasets")
    print("found datasets:", cli.scan())
 
    csv_path = cli.scan()[0]
    train_loader, val_loader, test_loader, n, m, scaler = cli.load(csv_path, T=96, L=96, patch_size=16)
 
    X_C, X_H = next(iter(train_loader))
    print(f"X_C (context, patched) shape: {X_C.shape}")   # (B, input_dim, n)
    print(f"X_H (horizon, patched) shape: {X_H.shape}")    # (B, input_dim, m)
    print(f"batches, train: {len(train_loader)}, val: {len(val_loader)}, test: {len(test_loader)}")
 
 
if __name__ == "__main__":
    smoke_test()