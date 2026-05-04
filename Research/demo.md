# Demo

## proposed opening combinging opening and the problem

Many real systems can only be partially observed. You measure noisy signals, but the true state driving the system is hidden. Think of a swinging pendulum, you can see the images, but you don't directly observe the angle or velocity governing its motion. Our goal is to learn the hidden state well enough to predict the system over time. This turns out to be surprisingly hard for three reasons shown here, standard variational approaches fail to recover true dynamics, RNN-based models break the Markov assumption, and simply maximising the ELBO doesn't guarantee any of this gets fixed.

## Opening

Today we are presenting our project on learning hidden dynamics from partial observations. In many real systems, we can measure what is happening, but we do not directly see the state that drives the system over time. *i dont like this tbh but we can think of something.*

A good example is the pendulum dataset. If we observe a moving pendulum only through noisy images, we can see the motion, but we do not directly observe the underlying state that drives it. Our goal is to learn that hidden state well enough to predict the system over time, not just to reconstruct the individual frames.

## The problem

The broader challenge in our project is that many real systems are only partially observed, so the model has to infer latent dynamics from incomplete and noisy data. We want a method that is not only accurate, but also stable over time and meaningful in terms of the hidden state that it learns.

## Background models

The first building block in this space is the Variational Autoencoder. A VAE encodes observations into a distribution over a structured latent space and decodes from it, giving us a compact probabilistic representation. But a VAE treats every observation independently, it has no notion of time and no ability to model how the system evolves. So on its own it is not enough.

*I think we should move this elsewhere* Training is usually done by maximising the Evidence Lower Bound, or ELBO, which balances reconstruction quality against regularisation. Constrained optimisation builds on this idea by adding a reconstruction constraint to the ELBO, which pushes the model to learn latent states that better capture the underlying system dynamics.

To handle sequential data, VAEs have been extended into Deep State-Space Models, which learn both the transition and observation models using neural networks, incorporating a Kalman-style predict and update structure. However, these models rely on RNNs which violate the Markov assumption. 

This leads us to our other key idea the Kalman Filter. Kalman filters estimate a hidden state over time by alternating between a prediction step and an update step using the next observation. They are interpretable and principled, but they assume the system dynamics are known and usually linear, which makes them too restrictive for many modern problems.

## KVAE and EKVAE

KVAE attempts to get the best out of these two ideas. It keeps the structured latent representation from the VAE and uses closed-form Kalman-style filtering to handle sequences. *What I want to add This is a significant improvement over standard DSSMs. However the KVAE still retains an LSTM in its transition model, meaning part of the system state is stored in the LSTM rather than the latent state, so the Markov problem persists. (This would take away next sentence and paragraph)* That makes it a much better fit for time series and video data than a standard VAE.

But KVAE still has limitations. In particular, recurrent parts of the model can store information in hidden states in a way that weakens the Markov assumption, and that can make the learned dynamics less accurate compared to the real system's dynamics. *This all goes*

EKVAE is an extension that tries to improve this. It keeps the Kalman-style structure but replaces the recurrent transition component with a learned neural linearisation. The idea is to keep the benefits of filtering while making the transition model more flexible and more closely tied to the current latent state.

*Potential replacement: also brings up LSTM, The EKVAE fixes this by replacing the LSTM with neural linearisation — learning the local dynamics directly as a function of the current latent state rather than through a recurrent memory. This restores the Markov property while retaining closed-form Kalman filtering. Combined with constrained optimisation, which enforces reconstruction quality during training to ensure the transition model is properly learned, this is the model we are replicating and extending.*

## Why this combination matters *Can take this out*

So the reason we combine these methods is that each one solves only part of the problem. VAEs give us a probabilistic latent space, Kalman filters give us sequential inference, and the KVAE and EKVAE try to connect those ideas in a way that works for hidden dynamical systems. Our question is whether that combination actually gives us better latent dynamics recovery and forecasting.

## Hypotheses

Our main hypothesis is that KVAE-style models will improve latent-state recovery and forecasting compared with DSSM-style baselines. A second hypothesis is that constrained optimisation will improve system identification relative to standard ELBO training. A third is that the KVAE-style models will perform best on cleaner benchmark data, meaning data that upholds the Markov assumptions and has minimal noise or variation between points.

## Evaluation and data

We will evaluate prediction accuracy measured by mean squared error and R-squared, latent-state recovery, and long-horizon prediction consistency. We will start with the paper benchmarks including the pendulum and reacher datasets for direct comparison, then run robustness tests by varying sequence length, observation dimensionality, and noise level. *asking whether the EKVAE's advantages hold beyond the paper's controlled benchmarks*

## Closing *Dont think we need this but must ask jake*

So in short, our project aims to identify whether these models can learn hidden dynamics more effectively than standard approaches. The goal is not only to compare models, but also to understand why they work and where they start to fail. Finally, displayed is our current timeline and milestone plan for the overall project. *this might also need to be cleared up.*
