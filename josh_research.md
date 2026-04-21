# Issues I think we should address in proposal

## What is a kalman filter

## What is a VAE

## Combining the two

## EKVAE

## Neural linearisation

## EKVAE vs KVAE
### Problem with KVAE not being truly markovian
This should act as a reason as to why we use EKVAEs over KVAEs
Firstly we can see that the KVAE and DSSM, are not entirely markovian. Soem of the important prediction information is lost to the hidden state $h_t$. This is shown when looking in the research paper that the KVAE is unable to acccurately predict the udnerlying states like velocity when only given $z_t$ it also needs to be given $h_t$ in order to have an accurate prediction. 
Our EKVAE solves this as it is truly markovian. There is no $h_t$ for our prediction data to escape into. In the KVAE model the hidden state is unconstrained and thus the RNN sees this as the path of least resisitance and thus puts important prediction data into here.

#### For KVAE what exactly is the hidden state $h_t$
Kalman filters need state transitions to be linear. Which in many cases they are not. This transition is called F, KVAEs "fixed" this issue by allowing F to vary over time and using RNNs to predict how it changes. This is done by instead of havign a fixed F matrix we have different matrix $F_t$ at each time step. This is then predicted by a NN. This RNN uses all previosu inputs to make this prediction thus creating our hidden state $h_t$

So concretely, at each time step the KVAE does something like:
The RNN takes the previous auxiliary observation $a_{t-1}$ as input
It updates its hidden state: $h_t$ = RNN($a_{t-1}$, $h_{t-1}$)
It uses $h_t$ to produce the transition matrix: $F_t$ = g($h_t$)
The Kalman filter then uses $F-t$ to propagate the belief about $z_t$

So $h_t$ becomes the RNN internal memory. This is the compressed history of the system used to predict $F-t$
$h_t$ is not a distribution, it is not part of the generative model. It sits along side the latent state $z_t$. Our predictive model then says that everyhting is explained from the previous time step which is no longer true as the $F_t$ is predicted using this hidden state, breaking the markovian property.
The model is trained to minimise ELBO during training, but z and h are avaliable at each step. h is easier to write information to as it is NOT regularised, the KL term in the ELBO pushes z down towards the prior, thus penalising the model for encoding too much info into z. h has no such penalty. h is deterministic while z is not. the model is NEVER explicity told to store everything in z and thus can store vital information into h causing our predictions to be dependant on both z and h.
EKVAEs do not use ht solving this entirely.

### Problems with EKVAEs on unimodal data
Our extended kalman filter is reliant on a gaussian belief over the latent states. Gaussians are unimodal and thus onyl have 1 best guess about where the state is. When using data that is non unimodal we should thus bump into problems. We could explore this. 
In our neural linearisation we use a $F\psi$ that "approximates the local jacobian". We then propogate this approximation. This only makes sense if the data is gaussian, if it is multimodal a linear approximation would not be representative. We assume that at each time step our uncertainty about the latent state is represented by a single gaussian. 
This is less of an issue if the multimodal model has its two heads close together as then the gaussian prediction would not be the worst possibility. But as the heads spread apart our results become increasily worse. 
We need to ensure that if we want accurate results the data we use to evaluate our EKVAE must be unimodal. We can also prove that it does indeed perform badly on multimodal data, meaning a standard NN might be a better solution.
#### Worst issue
The particularly insidious version is when the multimodality is intermittent. Most of the time the posterior is roughly unimodal and the model works fine, but occasionally — at certain ambiguous observations or transition points — the posterior splits into multiple modes and the model confidently picks the wrong one. The error from that single moment then propagates forward through the rollout, corrupting all subsequent predictions. This kind of failure is very hard to diagnose because average metrics look acceptable.

#### Examples of multimodal
Ambiguous observations are the clearest case. Imagine a robot arm that looks identical from a camera whether it's at +45° or -45° due to symmetry. A single image gives you two equally plausible states. The true posterior has two modes. The EKF will average them and confidently place the estimated state somewhere in the middle — which is actually the least plausible location.
Switching dynamics are another major case. If a system can be in one of several qualitatively different regimes — a pendulum that might be swinging clockwise or counterclockwise, a physical system with multiple attractors, a process that transitions between fast and slow dynamics — then at transition points the posterior over which regime you're in becomes multimodal.
Partial observability with symmetry is closely related. When you can only observe part of the system state and the unobserved part has multiple plausible values consistent with what you can see, the posterior over the full state inherits that multimodality.

# When Would an EKVAE be best?
the EKVAE sits in a specific niche where the system dynamics are approximately Markovian, the posterior is approximately unimodal (or can be made so with a good enough observation model), and you need interpretable states and principled uncertainty. Outside that niche — particularly with multimodal posteriors or strongly non-Gaussian noise — you're either forced to use approximations that degrade performance, or you need a fundamentally different approach like particle filters, mixture models in latent space, or normalising flows for the posterior.