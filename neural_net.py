import chainer
import chainer.functions as F
import chainer.links as L

import re


class MLP(chainer.Chain):
  def __init__(self, n_units):
    create_layers = "super(MLP, self).__init__("
    for i, units in enumerate(n_units):
      create_layers += "l{}=L.Linear(None, {}), ".format(i + 1, units)
    exec(create_layers + ')')

  def __call__(self, x):
    layers = []
    for var in sorted(self.__dict__.keys()):
      if re.search(r'^l[1-9]*' , var) is not None:
        exec('layers.append(self.{})'.format(var))
    layer_out = x
    for layer in layers[:-1]:
      layer_out = F.relu(layer(layer_out))
    return layers[-1](layer_out)
