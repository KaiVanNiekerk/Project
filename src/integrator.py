import torch
import torch.nn as nn

# Claude aided a lot here
class Integrator(nn.Module):
    """
    Phase 2 Integrator: maps the Koopman residual X^Res (context, measurement
    space) to a control-input sequence U over the prediction horizon m.

    Variables:
        d = measurement dimension
        d_model = transformer working dimension (new hyper parameter for us to find, just transformers working dimension can set to equal d)
        n = num context patches (Patches we have)
        m = num horizon patches (Patches we predict)
        input  X^Res : (B, n, d)   
        output U      : (B, m, d)   
    """

    def __init__(self, d, d_model, n_heads, d_ff, n_layers, n, m, dropout=0.05):
        # 1. adaptation: Linear(d -> d_model)
        # 2. encoder: nn.TransformerEncoder wrapping n_layers of
        #    nn.TransformerEncoderLayer(d_model, n_heads, d_ff, dropout, batch_first=True)
        # 3. head: Linear(n * d_model -> m * d)
        super(Integrator, self).__init__()
        self.d = d
        self.d_model = d_model
        self.n = n
        self.m = m
 
        # adaptation: project measurement dim -> transformer working dim
        # Makes similar rows of observations more similar and pushes dissimilar rows of observations further apart in the transformer working dimension
        # Allowing us to see patterns in the context window more easily
        self.adaptation = nn.Linear(d, d_model)
        
        # Encoder: stack of transformer encoder layers to process the adapted input sequence
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=d_ff,
            dropout=dropout,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        
        # Head: project the encoded sequence to the control input dimension
        self.head = nn.Linear(n * d_model, m * d)

    def forward(self, x_res):
        # x_res: (B, n, d)
        # 1. adapt -> (B, n, d_model)
        # 2. encode -> (B, n, d_model)
        # 3. flatten -> (B, n * d_model)
        # 4. project -> (B, m * d), reshape -> (B, m, d)
        B = x_res.shape[0]
 
        x = self.adaptation(x_res)                          # B n d_model
        x = self.encoder(x)                                 # B n d_model
        x = x.reshape(B, self.n * self.d_model)             # B (n*d_model)
        u = self.head(x)                                    # B (m*d)
        u = u.reshape(B, self.m, self.d)                    # B m d
 
        return u