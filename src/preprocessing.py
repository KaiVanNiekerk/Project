import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from einops import rearrange

"""
We have to perform preprocessing on our data which consists of these steps:
1. Load the CSV file into a pandas DataFrame.
2. Split the dataset into training, validation and testing sets.
3. Scale the training, validation and testing datasets using StandardScaler.
4. Sliding Window, to create many overlapping context windows of size T, and for each context window we have a target window of size L
5. Patchify, to split the context window into smaller distinct patches of size S, which will be used as input to the transformer model.
6. Token embedding to flatten the patch and then make it usable by pytorch through a general size d.
"""

"""
    Load a CSV file into a pandas DataFrame.
    Args:
        path (str): The file path to the CSV file.
    Returns:
        pd.DataFrame: The loaded DataFrame.
"""
def load_csv(path: str) -> pd.DataFrame:
    # Note only works with numeric fields for now as otherwise scale function breaks.
    return pd.read_csv(path).select_dtypes(include="number")  # Select only numeric columns
    
"""
    Split the dataset into training, validation and testing sets.
    Returns:
        tuple: A tuple containing the training and testing DataFrames.
"""
def split(df: pd.DataFrame, train_frac: float, val_frac: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:    
    n = len(df)
    train_end = int(n * train_frac)
    val_end = train_end + int(n * val_frac)
    # iloc is used to select rows by index position, this is an important distinct as it preserves rows
    # Note we also do not do random splitting as that would ruin the time series nature of the data
    return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]

"""
    Scale the training, validation and testing datasets using StandardScaler.
    Args:
        train_df (pd.DataFrame): The training DataFrame.
        val_df (pd.DataFrame): The validation DataFrame.
        test_df (pd.DataFrame): The testing DataFrame.
    Returns:
        tuple: A tuple containing the scaled training, validation and testing datasets as numpy arrays, and the fitted scaler.
    """
def scale(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, StandardScaler]:
    scaler = StandardScaler()
    scaler.fit(train_df.values) # only train on trainign data
    train_scaled = scaler.transform(train_df)
    val_scaled = scaler.transform(val_df)
    test_scaled = scaler.transform(test_df)
    return train_scaled, val_scaled, test_scaled, scaler

"""A custom dataset for creating sliding window data.
    We will start with a sldiing window of some length starting at position i
    then move to start at position i+1, thus mvoing the context window time step by time step
    But we still have lots of overlap
    This si the batching process"""
class swDataset(Dataset):
    
    # Input window = T
    # Output window = L
    def __init__(self, data: np.ndarray, input_window: int, output_window: int):
        self.data = data
        self.input_window = input_window
        self.output_window = output_window

    # Number of windows
    def __len__(self):
        return len(self.data) - self.input_window - self.output_window + 1

    # Extract single window 
    def __getitem__(self, idx) -> tuple[torch.Tensor, torch.Tensor]:
        # i to i + T
        x = self.data[idx:idx + self.input_window]
        # i + T to i + T + L
        y = self.data[idx + self.input_window:idx + self.input_window + self.output_window]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)
    
"""Patching now happens inside a sliding window to ensure there is no overlapping 
    within a context window.
    Args:
        x (torch.Tensor): Input tensor of shape (batch_size, input_window, num_features).
        patch_size (int): Size of each patch.
    Returns:
        torch.Tensor: Patched tensor of shape (batch_size, num_patches, patch_size, num_features).
    """
# Note patch size needs to be picked, IN paper they dont specify.
def patchify(x: torch.Tensor, patch_size: int) -> torch.Tensor:
    # Rearrange the tensor to create patches
    # Thus splitting the mulivariate batch into distinct patches of size patch_size
    # x shape: (batch_size (B), input_window (T), num_features (N))
    # output shape: (batch_size (B), num_patches (n), patch_size (S), num_features (N), where n = T // S)
    return rearrange(x, 'B (n s) N -> B N s n', s=patch_size)

"""Reconstruct the original sequence from patches.
    Args:
        x (torch.Tensor): Patched tensor of shape (batch_size, num_patches, patch_size, num_features).
        patch_size (int): Size of each patch.
    Returns:
        torch.Tensor: Reconstructed tensor of shape (batch_size, input_window, num_features).
    """
def unpatchify(x: torch.Tensor, patch_size: int) -> torch.Tensor:
    # Rearrange the tensor to reconstruct the original sequence
    # x shape: (batch_size (B), num_patches (n), patch_size (S), num_features (N))
    # output shape: (batch_size (B), input_window (T), num_features (N)), where T = n * S
    return rearrange(x, 'B N s n -> B (n s) N', s=patch_size)

"""
    Have to make this make sense...
    This class is used to project our inputs into the required output values for our K^2. 
    We make use of a NN to do this projection.
    This will be used to project the flattened patches into a d-dimensional space, which is suitable for input to a transformer model.
    Additionally this d is chosen by use as a hyper parameter and the linear combination of the raw values learned through back prop.
    For example this allows us to have variable numbers in out datasets as they are always 
    forced into n meaningful patches of d numbers which will then be feed into the K^2VAE
"""
class TokenEmbedding(nn.Module):
    # Initialise and project NN,
    # d (We must decide its value) is the desired embedding dimension
    # num_vars * patch size is number of inputs
    def __init__(self, num_vars: int, patch_size: int, d: int):
        super().__init__() # must initalising super as to define necessary dicts for NN to work.
        self.patch_size = patch_size
        self.proj = nn.Linear(num_vars * patch_size, d) # creation of NN

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # X: (B, T, N) — swDataset's native output
        Xp = patchify(x, self.patch_size)          # (B, N, s, n)
        Xp = rearrange(Xp, "B N s n -> B n (N s)") # flatten (N,s) per patch
        Xp = self.proj(Xp)                          # (B, n, d)
        return rearrange(Xp, "B n d -> B d n")      # (B, d, n)

def test_run():
    B, T, N = 2, 8, 3
    s = 2
    n = T // s
    d = 16

    # 1. Splitting
    df = pd.DataFrame(np.random.randn(100, N))
    train_df, val_df, test_df = split(df, train_frac=0.7, val_frac=0.15)
    assert len(train_df) + len(val_df) + len(test_df) == len(df), \
        f"split sizes don't sum to total: {len(train_df)}+{len(val_df)}+{len(test_df)} != {len(df)}"
    assert len(train_df) > 0 and len(val_df) > 0 and len(test_df) > 0, "one of the splits is empty"

    # 2. Scaling
    train_scaled, val_scaled, test_scaled, scaler = scale(train_df, val_df, test_df)
    # atol = absolute tolerance amount
    assert np.allclose(train_scaled.mean(axis=0), 0, atol=1e-6), \
        f"train mean not ~0: {train_scaled.mean(axis=0)}"
    assert np.allclose(train_scaled.std(axis=0), 1, atol=1e-6), \
        f"train std not ~1: {train_scaled.std(axis=0)}"

    # 3. Sliding window dataset
    input_window, output_window = 8, 2
    ds = swDataset(train_scaled, input_window, output_window)
    expected_len = len(train_scaled) - input_window - output_window + 1
    assert len(ds) == expected_len, f"dataset len {len(ds)} != expected {expected_len}"

    x_win, y_win = ds[0]
    assert x_win.shape == (input_window, N), f"x window shape {x_win.shape} != {(input_window, N)}"
    assert y_win.shape == (output_window, N), f"y window shape {y_win.shape} != {(output_window, N)}"

    # 4. Patchify (synthetic tensor with known dims, independent of CSV)
    x = torch.randn(B, T, N)
    xp = patchify(x, s)
    assert xp.shape == (B, N, s, n), f"patchify shape {xp.shape} != {(B, N, s, n)}"

    # 5. Round-trip: patchify -> unpatchify should be an EXACT match (pure reshape, no float ops)
    x_recon = unpatchify(xp, s)
    assert torch.equal(x, x_recon), "patchify/unpatchify round-trip mismatch"

    # 6. TokenEmbedding
    embed = TokenEmbedding(num_vars=N, patch_size=s, d=d)
    tokens = embed(x)
    assert tokens.shape == (B, d, n), f"token embedding shape {tokens.shape} != {(B, d, n)}"

    print("All sanity checks passed.")
    print(f"  patch shape: {xp.shape}")
    print(f"  token shape: {tokens.shape}")
    
def vis_test():
    B, T, N = 1, 8, 2
    s = 2

    # x[0, t, v] = t * 10 + v, so you can read off (timestep, variable) at a glance
    x = torch.arange(B * T * N, dtype=torch.float32).reshape(B, T, N)
    for v in range(N):
        x[0, :, v] = torch.arange(T) * 10 + v

    print("=== Input (B, T, N) ===")
    print(f"shape: {x.shape}")
    print(x)

    # Sliding window — show one window explicitly
    data_np = x[0].numpy()  # (T, N), pretend this is the full series
    input_window, output_window = 4, 2
    ds = swDataset(data_np, input_window, output_window)
    x_win, y_win = ds[0]
    print("\n=== Sliding window 0 ===")
    print(f"x (context) shape {x_win.shape}:\n{x_win}")
    print(f"y (target) shape {y_win.shape}:\n{y_win}")

    # Patchify — now operates on the CONTEXT WINDOW, not the raw full series.
    # x_win is (input_window, N); patchify expects (B, T, N), so add the batch dim.
    x_ctx = x_win.unsqueeze(0)  # (1, input_window, N)
    n = input_window // s
    xp = patchify(x_ctx, s)  # (B, N, s, n)
    print("\n=== Patchified context window (B, N, s, n) ===")
    print(f"shape: {xp.shape}")
    for var in range(N):
        print(f"-- variable {var} --")
        for patch_idx in range(n):
            print(f"  patch {patch_idx}: {xp[0, var, :, patch_idx].tolist()}")

    # Round-trip check, visually — reconstructs the CONTEXT WINDOW, not the raw x
    x_recon = unpatchify(xp, s)
    print("\n=== Reconstructed context window (should match x_win) ===")
    print(x_recon)
    print("exact match:", torch.equal(x_ctx, x_recon))

if __name__ == "__main__":
    # Both test methods from claude, verified by author
    test_run() 
    vis_test()