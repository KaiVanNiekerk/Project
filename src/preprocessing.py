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
def patchify(x: torch.Tensor, patch_size: int) -> torch.Tensor:
    # Rearrange the tensor to create patches
    # Thus splitting the mulivariate batch into distinct patches of size patch_size
    # x shape: (batch_size (B), input_window (T), num_features (N))
    # output shape: (batch_size (B), num_patches (n), patch_size (S), num_features (N), where n = T // S)
    return rearrange(x, 'B (n s) N -> B n s N', s=patch_size)

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
    return rearrange(x, 'B n s N -> B (n s) N', s=patch_size)

## Add test patching and then create the tokensEmbedding and flatten the array
class TokenEmbedding():
    pass

if __name__ == "__main__":
    # Example usage
    df = load_csv(r"datasets\electricity\electricity.csv") #raw string to geta round \ errors
    #print("great success")
    train_df, val_df, test_df = split(df, train_frac=0.7, val_frac=0.15)
    print(train_df)
    train_scaled, val_scaled, test_scaled, scaler = scale(train_df, val_df, test_df)
    print(train_scaled)
    
