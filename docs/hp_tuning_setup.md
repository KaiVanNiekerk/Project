# HP tuning setup: Exchange-S on a fresh PC

Goal: set up this repo (K2VAE, PyTorch) on a machine with nothing installed, then run a two-phase wandb hyperparameter sweep on the **Exchange-S** dataset. Follow the steps in order. All commands run from the **project root** (the folder containing `pyproject.toml`).

Requirements: Windows/Linux, Python 3.11+, git, an NVIDIA GPU with a recent driver (CPU works but is slow), internet **while running the sweep** (wandb sweeps need the W&B server), and a free wandb account (https://wandb.ai, key at https://wandb.ai/authorize).

## 1. Get the code

```
git clone https://github.com/orljos001-cyber/Project.git
cd Project
```

Make sure the latest `main` is checked out (`src/sweep.py` and `configs/sweep_*_small.yaml` must be present).

## 2. Install dependencies

The project uses `uv` and `uv.lock` (torch is pinned to the CUDA 12.4 wheel index in `pyproject.toml`).

```
pip install uv
uv sync
```

Check that it works:

```
uv run python -c "import torch, wandb; print(torch.cuda.is_available(), wandb.__version__)"
```

`True` means the GPU is visible. If `False` on a GPU machine, update the NVIDIA driver (CUDA 12.4 needs driver >= 551).

## 3. Add the dataset (not in git)

The dataset is gitignored and must be copied manually to exactly:

```
datasets/exchange_rate/exchange_rate.csv
```

The first line must be `date,0,1,2,3,4,5,6,OT`.

## 4. Log in to wandb (once)

```
uv run wandb login
```

Paste the API key.

## 5. Select the dataset (important)

`src/sweep.py` defaults to the ETTh1-L dataset. Every shell that runs `wandb agent` or `sweep.py` must first set:

PowerShell:
```
$env:DATASET_CONFIG = "configs/datasets_yaml/Exchange-S.yaml"
```
bash:
```
export DATASET_CONFIG=configs/datasets_yaml/Exchange-S.yaml
```

Optional: `MAX_EPOCHS` (default 60) caps epochs per run; early stopping usually ends runs sooner.

## 6. Phase 1: continuous hyperparameters (lr, kl_weight, lambda_rec)

```
uv run wandb sweep configs/sweep_continuous_small.yaml
```

This prints a line like `wandb agent <entity>/<project>/<sweep_id>`. Copy that full path. Then start an agent **in the same shell as step 5** and leave it running:

```
uv run wandb agent --count 20 <entity>/<project>/<sweep_id>
```

When it finishes, analyze (plots go to `artifacts/plots/`, best values to `artifacts/sweeps/<entity>_<project>_<sweep_id>_best.json`):

```
uv run python src/sweep.py --analyze <entity>/<project>/<sweep_id>
```

## 7. Phase 2: architecture (d, hidden_dim, hidden_layers)

Fix Phase 1's winners by pointing `BASE_HP_OVERRIDES` at the JSON from step 6, set in the shell that runs the agent:

PowerShell:
```
$env:BASE_HP_OVERRIDES = "artifacts/sweeps/<entity>_<project>_<phase1_sweep_id>_best.json"
```
bash:
```
export BASE_HP_OVERRIDES=artifacts/sweeps/<entity>_<project>_<phase1_sweep_id>_best.json
```

Then:

```
uv run wandb sweep configs/sweep_architecture_small.yaml
uv run wandb agent <entity>/<project>/<phase2_sweep_id>
uv run python src/sweep.py --analyze <entity>/<project>/<phase2_sweep_id>
```

The grid is 27 runs; the agent stops when all are done.

## 8. Bring results back

Copy `artifacts/plots/` and `artifacts/sweeps/` back to the main PC (or commit them). The winning values are then copied by hand into the `hyperparameters` block of `configs/datasets_yaml/Exchange-S.yaml`.

## Troubleshooting: sweep is created but no runs/agent appear

`wandb sweep` only *registers* the sweep on the server. Nothing runs until `wandb agent` is started on a machine. Check, in order:

1. **Was `wandb agent <entity>/<project>/<sweep_id>` actually started, and is it still running?** Use the full path printed by `wandb sweep`; a bare id can look in the wrong project/entity.
2. **Read the agent's terminal output.** If runs start and crash immediately, the agent gives up after several consecutive failures. The error is printed there.
3. **`uv` missing:** the sweep YAMLs contain `command: [uv, run, python, ${program}, ${args}]`. If `uv` is not on PATH the agent's runs fail instantly. Install uv (step 2) or delete the `command:` block from the YAML to fall back to the default `python src/sweep.py` (then activate an environment that has the dependencies).
4. **Wrong working directory:** the agent must be started from the project root, since `program: src/sweep.py` and `datasets/` are relative paths.
5. **Not logged in / no internet:** run `uv run wandb login`; check `uv run wandb status`.
6. **Grid already exhausted:** an agent exits immediately if every combination has already run. Create a fresh sweep with `wandb sweep`.
7. **Run a single trial by hand to see the real error:** `uv run python src/sweep.py` (with step 5 set) starts one trial with default values and shows any traceback.
