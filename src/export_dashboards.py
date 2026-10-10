import os
import matplotlib.pyplot as plt
import pandas as pd
import wandb

SWEEPS = {
    "vnkkai001-university-of-cape-town/Project-src/sdvjdz94": "01_ETTh1-L_Phase1_Bayesian",
    "vnkkai001-university-of-cape-town/Project-src/6mtimrqv": "02_ETTh1-L_Phase2_Grid",
    "vnkkai001-university-of-cape-town/Project-src/pqfcuflj": "03_Exchange-S_Phase1_Bayesian",
    "vnkkai001-university-of-cape-town/Project-src/qpyawoag": "04_Exchange-S_Phase2_Grid"
}

METRICS = ["val_total", "val_rec", "val_nll", "val_kl", "val_elbo", "train_total"]
OUTPUT_DIR = "artifacts/plots/sweep_dashboards"

os.makedirs(OUTPUT_DIR, exist_ok=True)
api = wandb.Api()

for sweep_path, clean_name in SWEEPS.items():
    print(f"Processing sweep: {clean_name}")
    sweep = api.sweep(sweep_path)
    
    # Fetch data and find the best run based on minimum val_total
    runs_data = []
    best_run_name = None
    min_val_total = float('inf')
    
    for run in sweep.runs:
        hist = pd.DataFrame(list(run.scan_history(keys=["_step"] + METRICS)))
        if not hist.empty and "val_total" in hist.columns:
            runs_data.append({"name": run.name, "data": hist})
            run_min = hist["val_total"].min()
            if run_min < min_val_total:
                min_val_total = run_min
                best_run_name = run.name

    if not runs_data:
        continue

    # Set a clean, professional plot style
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()
    
    for idx, metric in enumerate(METRICS):
        ax = axes[idx]
        
        # Plot background (suboptimal) runs first
        for run_dict in runs_data:
            if run_dict["name"] != best_run_name:
                df = run_dict["data"]
                if metric in df.columns:
                    clean_df = df[["_step", metric]].dropna().sort_values("_step")
                    ax.plot(clean_df["_step"], clean_df[metric], color='gray', alpha=0.3, linewidth=1.0)
        
        # Plot the single best run on top
        for run_dict in runs_data:
            if run_dict["name"] == best_run_name:
                df = run_dict["data"]
                if metric in df.columns:
                    clean_df = df[["_step", metric]].dropna().sort_values("_step")
                    ax.plot(clean_df["_step"], clean_df[metric], color='#d62728', alpha=1.0, linewidth=2.0, label=f"Best: {best_run_name}")

        ax.set_title(metric, fontweight="bold", pad=10)
        ax.set_xlabel("Epoch Step")
        
        # Add a single, small legend only to the first subplot
        if idx == 0:
            ax.plot([], [], color='gray', alpha=0.4, linewidth=1.0, label='Other Runs')
            ax.legend(fontsize=10, loc='upper right', framealpha=0.9, edgecolor='black')

    plt.tight_layout()
    
    # Export as PNG
    png_path = os.path.join(OUTPUT_DIR, f"{clean_name}_dashboard.png")
    plt.savefig(png_path, format="png", bbox_inches='tight')
    plt.close()
    
    print(f"Saved: {png_path}")