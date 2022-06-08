"""
Multi Layer Perceptron
"""
from typing import Tuple, Optional

import torch
from torch import nn
from torchtyping import TensorType

from pyrad.fields.modules.base import FieldModule


class MLP(FieldModule):
    """Multilayer perceptron

    Args:
        in_dim (int): Input layer dimension
        num_layers (int): Number of network layers
        layer_width (int): Width of each MLP layer
        out_dim (int, optional): Ouput layer dimension. Defaults to layer_width
        activation (Optional[nn.Module], optional): intermediate layer activation function. Defaults to nn.ReLU.
        out_activation (Optional[nn.Module], optional): output activation function. Defaults to None.
    """

    def __init__(
        self,
        in_dim: int,
        num_layers: int,
        layer_width: int,
        out_dim: Optional[int] = None,
        skip_connections: Tuple[int] = (),
        activation: Optional[nn.Module] = nn.ReLU(),
        out_activation: Optional[nn.Module] = None,
    ) -> None:

        super().__init__()
        self.in_dim = in_dim
        assert self.in_dim > 0
        self.out_dim = out_dim if out_dim is not None else layer_width
        self.num_layers = num_layers
        self.layer_width = layer_width
        self.skip_connections = skip_connections
        self.activation = activation
        self.out_activation = out_activation
        self.net = None
        self.build_nn_modules()

    def build_nn_modules(self) -> None:
        """Initialize multi-layer perceptron."""
        layers = []
        if self.num_layers == 1:
            layers.append(nn.Linear(self.in_dim, self.out_dim))
        else:
            for i in range(self.num_layers - 1):
                if i == 0:
                    assert i not in list(self.skip_connections), "Skip connection at layer 0 doesn't make sense."
                    layers.append(nn.Linear(self.in_dim, self.layer_width))
                elif i in self.skip_connections:
                    layers.append(nn.Linear(self.layer_width + self.in_dim, self.layer_width))
                else:
                    layers.append(nn.Linear(self.layer_width, self.layer_width))
            layers.append(nn.Linear(self.layer_width, self.out_dim))
        self.layers = nn.ModuleList(layers)

    def forward(self, in_tensor: TensorType[..., "in_dim"]) -> TensorType[..., "out_dim"]:
        """Process input with a multilayer perceptron.

        Args:
            in_tensor (TensorType[..., "in_dim]): Network input

        Returns:
            TensorType[..., "out_dim"]: MLP network output
        """
        x = in_tensor
        for i, layer in enumerate(self.layers):
            if i in self.skip_connections:
                x = torch.cat([in_tensor, x], -1)
            x = layer(x)
            if self.activation:
                x = self.activation(x)
        return x