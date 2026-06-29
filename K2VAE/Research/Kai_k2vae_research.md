# K2VAE Research Notes

## Purpose
This file will hold our research notes, paper analysis, implementation ideas, and reflections on K2VAE.

## Paper Overview
- Paper title: K2VAE: A Koopman-Kalman Enhanced Variational AutoEncoder for Probabilistic Time Series Forecasting
- Main topic: probabilistic time-series forecasting using Koopman-inspired linearisation and Kalman-style refinement
- Why it matters: combines structured dynamics, uncertainty modelling, and VAE-based forecasting

## Article Analysis
### Problem Statement
- Long-horizon probabilistic forecasting is difficult because nonlinear dynamics cause error accumulation.
- Diffusion and flow-based approaches are expensive and inefficient for long horizons.

### Core Idea
- Use a KoopmanNet to transform the nonlinear time series into a more linear measurement space.
- Use a KalmanNet to refine the resulting linear system and model uncertainty.
- Use a VAE-style structure to produce the final probabilistic forecasting distribution.

### Key Contributions
- Efficient VAE-based architecture for long-horizon probabilistic forecasting
- Koopman-inspired linearisation to simplify nonlinear dynamics
- Kalman-style uncertainty refinement to reduce error accumulation
- Experimental results suggesting strong short- and long-term forecasting performance

### Strengths
- Clear motivation tied to probabilistic forecasting
- Structured dynamics approach rather than purely black-box forecasting
- Good fit for long-horizon forecasting settings
- Recent and relevant paper in the forecasting literature

### Limitations / Questions
- The method is more forecasting-focused than latent-state-recovery-focused
- The Koopman mapping may be difficult to interpret in some settings
- The approach may be less directly aligned with partial-observability and latent-state recovery than EKVAE-style work

## Relevance to Our Project
- Useful for understanding how Koopman methods and Kalman-style refinement can be combined
- Good comparison point for our own work and for future experiments
- Potentially useful for a thesis direction focused on structured latent dynamics and forecasting

## Implementation Notes
- Needs datasets for multivariate time-series forecasting
- Potential baselines: standard VAE, Kalman filter, state-space baselines, and forecasting benchmarks
- Useful to compare short-term and long-term forecasting performance

## Open Questions
- How much of the performance comes from the Koopman structure versus the Kalman refinement?
- How sensitive is the method to noise and sequence length?
- How does it compare with simpler latent-state models in our target setting?

## Summary
K2VAE is an interesting and relevant paper because it combines structured dynamics, uncertainty modelling, and generative forecasting in a modern framework. It is a strong candidate for deeper study and possible replication.
