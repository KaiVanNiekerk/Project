# Demo

## opening and problem with example

Many real systems can only be partially observed. You measure noisy signals, but the true state driving the system is hidden. Think of a swinging pendulum, you can see the images, but you don't directly observe the angle or velocity governing its motion. Our goal is to learn the hidden state well enough to predict the system over time. This turns out to be surprisingly hard for three reasons shown here, standard variational approaches fail to recover true dynamics, RNN-based models break the Markov assumption, and simply Maximising the ELBO does not guarantee the model learns the true system dynamics.

## Background models

The first building block in this space is the Variational Autoencoder. A VAE encodes observations into a distribution over a structured latent space and decodes from it. However VAEs treats every observation independently, it has no notion of time and no ability to model how the system evolves. So on its own it is not enough. In the simple context of number matching, VAEs will group different numbers together like 4 and 5 shown here and owing to it being structured interpolating between digit clusters in latent space produces smooth transitions, as you can see at this point it is a mix of a 4 and a 5.

To handle sequential data, VAEs have been extended into Deep State-Space Models, which learn both the transition and observation models using neural networks, incorporating a Kalman-style predict and update structure. However, these models rely on RNNs which violate the Markov assumption.

This leads us to the kalman filter.  It estimates a hidden state over time by alternating between a prediction step and an update step using the next observation. It's interpretable and principled, but it assumes the dynamics are known and linear, which makes it too restrictive for many modern problems. The linearity can be seen in its equation, we thus introduce the Extended Kalman Filter which relaxes this by making F a function of the current state, allowing it to handle nonlinear dynamics

## KVAE and EKVAE

KVAE attempts to get the best out of these two ideas. It keeps the structured latent representation from the VAE and uses closed-form Kalman-style filtering to handle sequences which is a significant improvement over standard DSSMs and makes it a much better fit for time series and video data than a standard VAE. But KVAE still has it's limitations. In particular, recurrent parts of the model can store information in hidden states in a way that weakens the Markov assumption, and that can make the learned dynamics less accurate compared to the real system's dynamics.

The EKVAE fixes this by learning the local dynamics directly as a function of the current latent state rather than through a recurrent memory via neural linearisation. This restores the Markov property while retaining closed-form Kalman filtering. Training is usually done by maximising the Evidence Lower Bound, which balances reconstruction quality against regularisation, but simply maximising the ELBO does not quarantee that the underyling dynamics have been properly learned. Constrained optimisation builds on this idea by adding a reconstruction constraint to the ELBO, which pushes the model to learn latent states that better capture the underlying system dynamics.

## Hypotheses

Our main hypothesis is that KVAE-style models will improve latent-state recovery and forecasting compared with DSSM-style baselines. A second hypothesis is that constrained optimisation will improve system identification relative to standard ELBO training. A third is that the KVAE-style models will perform best on cleaner benchmark data, meaning data that upholds the Markov assumptions and has minimal noise or variation between points.

## Evaluation and data

We will evaluate prediction accuracy measured by mean squared error and R-squared. We will start with the paper benchmarks including the pendulum and reacher datasets for direct comparison, then run robustness tests by varying sequence length, observation dimensionality, and noise level. Thus asking whether the EKVAE's advantages hold beyond the paper's controlled benchmarks. Finally, displayed is our current timeline and milestone plan for the overall project.
