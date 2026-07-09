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
4. Sliding Window 
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

"""A custom dataset for handling sliding window data."""
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
    


if __name__ == "__main__":
    # Example usage
    df = load_csv(r"datasets\electricity\electricity.csv") #raw string to geta round \ errors
    #print("great success")
    train_df, val_df, test_df = split(df, train_frac=0.7, val_frac=0.15)
    print(train_df)
    train_scaled, val_scaled, test_scaled, scaler = scale(train_df, val_df, test_df)
    print(train_scaled)
    
