import numpy as np
from chainer.datasets import TupleDataset
from zipfile import ZipFile


def othello_data():
  print('loading othello datasets.')
  with ZipFile('othello.zip', 'r') as zf:
    for name in zf.namelist():
      data = str(zf.read(name), 'utf-8').splitlines()
  x, _y = [], []
  for d in data:
    e = d.split()
    x.append(list(e[0]))
    _y.append(e[1])
  x = np.array(x, dtype=np.float32)
  _y = np.array(_y, dtype=np.int32)
  return (TupleDataset(x[:-100], _y[:-100]),
          TupleDataset(x[-100:], _y[-100:]))
