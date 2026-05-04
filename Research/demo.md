# Demo

## Opening

Today we are presenting our project on learning hidden dynamics from partial observations. In many real systems, we can measure what is happening, but we do not directly see the state that drives the system over time. *i dont like this tbh but we can think of something.*

A good example is the pendulum dataset. If we observe a moving pendulum only through noisy images, we can see the motion, but we do not directly observe the underlying state that drives it. Our goal is to learn that hidden state well enough to predict the system over time, not just to reconstruct the individual frames.

## The problem

The broader challenge in our project is that many real systems are only partially observed, so the model has to infer latent dynamics from incomplete and noisy data. We want a method that is not only accurate, but also stable over time and meaningful in terms of the hidden state that it learns.

## Background models

The first idea in this space is the Variational Autoencoder, or VAE. A VAE learns a latent representation by encoding observations into a distribution and decoding from that latent space. This gives us a compact and probabilistic representation, but a standard VAE does not model time, so by itself it is not enough to handle sequential data. Training is usually done by maximising the Evidence Lower Bound, or ELBO, which balances reconstruction quality against regularisation. Constrained optimisation builds on this idea by adding a reconstruction constraint to the ELBO, which pushes the model to learn latent states that better capture the underlying system dynamics.

The other key idea is the Kalman filter. Kalman filters estimate a hidden state over time by alternating between a prediction step and an update step using the next observation. They are interpretable and principled, but they assume the system dynamics are known and usually linear, which makes them too restrictive for many modern problems.

## KVAE and EKVAE

KVAE combines these two ideas. It keeps the latent representation from the VAE and uses Kalman-style filtering to handle sequences. That makes it a much better fit for time series and video data than a standard VAE.

But KVAE still has limitations. In particular, recurrent parts of the model can store information in hidden states in a way that weakens the Markov assumption, and that can make the learned dynamics less accurate compared to the real system's dynamics .

EKVAE is an extension that tries to improve this. It keeps the Kalman-style structure but replaces the recurrent transition component with a learned neural linearisation. The idea is to keep the benefits of filtering while making the transition model more flexible and more closely tied to the current latent state.

## Why this combination matters

So the reason we combine these methods is that each one solves only part of the problem. VAEs give us a probabilistic latent space, Kalman filters give us sequential inference, and the KVAE and EKVAE try to connect those ideas in a way that works for hidden dynamical systems. Our question is whether that combination actually gives us better latent dynamics recovery and forecasting.

## Hypotheses

Our main hypothesis is that KVAE-style models will improve latent-state recovery and forecasting compared with DSSM-style baselines. A second hypothesis is that constrained optimisation will improve system identification relative to standard ELBO training. A third is that the KVAE-style models will perform best on cleaner benchmark data, meaning data that upholds the Markov assumptions and has minimal noise or variation between points.

## Evaluation and data

We will evaluate prediction accuracy measured by mean squared error and R-squared, latent-state recovery, and long-horizon prediction consistency. We will start with the paper benchmarks including the pendulum and reacher datasets for direct comparison, then run robustness tests by varying sequence length, observation dimensionality, and noise level.

## Closing

So in short, our project aims to identify whether these models can learn hidden dynamics more effectively than standard approaches. The goal is not only to compare models, but also to understand why they work and where they start to fail. Finally, displayed is our current timeline and milestone plan for the overall project. *this might also need to be cleared up.*
