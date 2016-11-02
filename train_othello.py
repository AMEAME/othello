#!/usr/bin/env python
from __future__ import print_function
import argparse

import chainer
import chainer.functions as F
import chainer.links as L
from chainer import training
from chainer.training import extensions

from neural_net import MLP
from data import othello_data


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
  args = parser.parse_args()

  unit = [15000, 15000, 64]

  print('GPU: {}'.format(args.gpu))
  print('# unit: {}'.format(unit))
  print('# Minibatch-size: {}'.format(args.batchsize))
  print('# epoch: {}'.format(args.epoch))
  print('')

  # Set up a neural network to train
  # Classifier reports softmax cross entropy loss and accuracy at every
  # iteration, which will be used by the PrintReport extension below.
  model = L.Classifier(MLP(unit))
  if args.gpu >= 0:
    chainer.cuda.get_device(args.gpu).use()  # Make a specified GPU current
    model.to_gpu()  # Copy the model to the GPU

  # Setup an optimizer
  optimizer = chainer.optimizers.Adam()
  optimizer.setup(model)

  # Load the othello dataset
  train, test = othello_data()

  train_iter = chainer.iterators.SerialIterator(train, args.batchsize)
  test_iter = chainer.iterators.SerialIterator(test, args.batchsize,
                                               repeat=False, shuffle=False)

  # Set up a trainer
  updater = training.StandardUpdater(train_iter, optimizer, device=args.gpu)
  trainer = training.Trainer(updater, (args.epoch, 'epoch'), out=args.out)

  # Evaluate the model with the test dataset for each epoch
  trainer.extend(extensions.Evaluator(test_iter, model, device=args.gpu))

  # Dump a computational graph from 'loss' variable at the first iteration
  # The "main" refers to the target link of the "main" optimizer.
  trainer.extend(extensions.dump_graph('main/loss'))

  # Take a snapshot at each epoch
  trainer.extend(extensions.snapshot(), trigger=(args.epoch, 'epoch'))

  # Write a log of evaluation statistics for each epoch
  trainer.extend(extensions.LogReport())

  # Print selected entries of the log to stdout
  # Here "main" refers to the target link of the "main" optimizer again, and
  # "validation" refers to the default name of the Evaluator extension.
  # Entries other than 'epoch' are reported by the Classifier link, called by
  # either the updater or the evaluator.
  trainer.extend(extensions.PrintReport(
    ['epoch', 'main/loss', 'validation/main/loss',
      'main/accuracy', 'validation/main/accuracy']))

  # Print a progress bar to stdout
  trainer.extend(extensions.ProgressBar())

  if args.resume:
    # Resume from a snapshot
    chainer.serializers.load_npz(args.resume, trainer)
  # Run the training
  trainer.run()
  chainer.serializers.save_npz('othello_model.npz', model)

  X1_ = [0] * 64

  X1_[3 * 8 + 4] = 1
  X1_[4 * 8 + 3] = 1
  X1_[3 * 8 + 3] = 2
  X1_[4 * 8 + 4] = 2

  X1_[3 * 8 + 2] = 3
  X1_[2 * 8 + 3] = 3
  X1_[4 * 8 + 5] = 3
  X1_[5 * 8 + 4] = 3

  X1 = np.array(X1_, dtype=np.float32)
  y1 = F.softmax(model.predictor(X1))
  print("y1 = " + str(y1.data.argmax(1)) + '\n')

if __name__ == '__main__':
  import time
  s = time.time()
  main()
  print("{}s".format(time.time - s))
