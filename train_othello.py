from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import tensorflow as tf

import input_data
import data

FLAGS = None


def main(_):
  # Create the model
  x = tf.placeholder(tf.float32, [None, 64])
  W = tf.Variable(tf.zeros([64, 64]))
  b = tf.Variable(tf.zeros([64]))
  y = tf.matmul(x, W) + b

  # Define loss and optimizer
  y_ = tf.placeholder(tf.float32, [None, 64])

  cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y, y_))
  train_step = tf.train.GradientDescentOptimizer(20).minimize(cross_entropy)

  sess = tf.InteractiveSession()
  # Train
  tf.initialize_all_variables().run()
  train_data = data.get_data()

  for i in range(27):
    batch_xs = train_data['data'][i * 100: (i + 1) * 100]
    batch_ys = train_data['target'][i * 100: (i + 1) * 100]
    sess.run(train_step, feed_dict={ x: batch_xs, y_: batch_ys })

  # # Test trained model
  # correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
  # accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
  # print(sess.run(accuracy, feed_dict={x: mnist.test.images, y_: mnist.test.labels}))


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--data_dir', type=str, default='/tmp/data',
                      help='Directory for storing data')
  FLAGS = parser.parse_args()
  tf.app.run()
