#!/usr/bin/env python
from __future__ import print_function
import argparse
import numpy as np

import chainer
import chainer.functions as F
import chainer.links as L
from chainer import training, Variable, cuda
from chainer.training import extensions

from neural_net import MLP, Classifier
from data import othello_data
from othello import Othello


def main():
  parser = argparse.ArgumentParser(description='Othello')
  parser.add_argument('--batchsize', '-b', type=int, default=100,
                      help='Number of othello recodes in each mini-batch')
  parser.add_argument('--epoch', '-e', type=int, default=20,
                      help='Number of sweeps over the dataset to train')
  parser.add_argument('--gpu', '-g', type=int, default=0,
                      help='GPU ID (negative value indicates CPU)')
  parser.add_argument('--out', '-o', default='result',
                      help='Directory to output the result')
  parser.add_argument('--resume', '-r', default='',
                      help='Resume the training from snapshot')
  parser.add_argument('--train', '-t', type=int, default=0,
                      help='train flag')
  args = parser.parse_args()

  unit = [1000, 1000, 64]

  print('GPU: {}'.format(args.gpu))
  print('# unit: {}'.format(unit))
  print('# Minibatch-size: {}'.format(args.batchsize))
  print('# epoch: {}'.format(args.epoch))
  print('')

  model = Classifier(MLP(unit))
  if args.gpu >= 0:
    chainer.cuda.get_device(args.gpu).use()
    model.to_gpu()
  optimizer = chainer.optimizers.Adam()
  optimizer.setup(model)

  if args.resume:
    chainer.serializers.load_npz(args.resume, model)

  if args.train == True:
    train, test = othello_data()
    train_iter = chainer.iterators.SerialIterator(train, args.batchsize)
    test_iter = chainer.iterators.SerialIterator(test, args.batchsize,
                                                repeat=False, shuffle=False)
    updater = training.StandardUpdater(train_iter, optimizer, device=args.gpu)
    trainer = training.Trainer(updater, (args.epoch, 'epoch'), out=args.out)
    trainer.extend(extensions.Evaluator(test_iter, model, device=args.gpu))
    trainer.extend(extensions.dump_graph('main/loss'))
    trainer.extend(extensions.snapshot(), trigger=(args.epoch, 'epoch'))
    trainer.extend(extensions.LogReport())
    trainer.extend(extensions.PrintReport(
      ['epoch', 'main/loss', 'validation/main/loss',
        'main/accuracy', 'validation/main/accuracy']))
    trainer.extend(extensions.ProgressBar())
    trainer.run()
    chainer.serializers.save_npz('othello_model.npz', model)

  othello = Othello()
  for _ in range(60):
    print(othello)
    X1 = np.array([othello.board.cells], dtype=np.float32)
    if args.gpu >= 0:
      X1 = cuda.to_gpu(X1, device=args.gpu)
    y = F.softmax(model.predictor(X1))
    y_ = int(y.data.argmax(1)[0])
    y = y_ // 8 * 10 + y_ % 8 + 11
    print("y = {}\n".format(y))
    move = int(input('move: '))
    othello.make_move((move // 10, move % 10))

if __name__ == '__main__':
  import time
  s = time.time()
  main()
  print("{}s".format(time.time() - s))
