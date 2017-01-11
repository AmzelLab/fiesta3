#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Implement a basic classical autoencoder for experimental purposes"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import argparse
import numpy as np
import tensorflow as tf

__author__ = 'Yunlong Liu (davislong198833@gmail.com)'

DESCRIPTION = "Experiment 2-layer Autoencoder with tensorflow"

INPUT_DIM = 1024
HIDDEN_1_DIM = 256
HIDDEN_2_DIM = 32

NUM_BATCH = 20
NUM_EPOCH = 50

WEIGHTS = {
    'encoder_h1': tf.Variable(tf.random_normal(INPUT_DIM, HIDDEN_1_DIM)),
    'encoder_h2': tf.Variable(tf.random_normal(HIDDEN_1_DIM, HIDDEN_2_DIM)),
    'decoder_h1': tf.Variable(tf.random_normal(HIDDEN_2_DIM, HIDDEN_1_DIM)),
    'decoder_h2': tf.Variable(tf.random_normal(HIDDEN_1_DIM, INPUT_DIM)),
}

BIASE = {
    'encoder_b1': tf.Variable(tf.random_normal([HIDDEN_1_DIM])),
    'encoder_b2': tf.Variable(tf.random_normal([HIDDEN_2_DIM])),
    'decoder_b1': tf.Variable(tf.random_normal([HIDDEN_1_DIM])),
    'decoder_b2': tf.Variable(tf.random_normal([INPUT_DIM])),
}


def encoder(dummy_x):
    """Build the encoder graph

    Args:
        dummy_x: the input x placeholder.

    Returns:
        The output dummy layer.
    """
    hidden_1 = tf.nn.sigmoid(tf.add(tf.matmul(dummy_x, WEIGHTS['encoder_h1']),
                                    BIASE['encoder_b1']))
    hidden_2 = tf.nn.sigmoid(tf.add(tf.matmul(hidden_1, WEIGHTS['encoder_h2']),
                                    BIASE['encoder_b2']))
    return hidden_2


def decoder(dummy_z):
    """Build the decoder graph

    Args:
        dummy_z: the input z placeholder

    Returns:
        The reconstruction of X, original data.
    """
    hidden_1 = tf.nn.sigmoid(tf.add(tf.matmul(dummy_z, WEIGHTS['decoder_h1']),
                                    BIASE['decoder_b1']))
    hidden_2 = tf.nn.sigmoid(tf.add(tf.matmul(hidden_1, WEIGHTS['decoder_h2']),
                                    BIASE['decoder_b2']))
    return hidden_2


def model(dummy_x):
    """Build the entire autoencoder graph"""
    encoder_graph = encoder(dummy_x)
    decoder_graph = decoder(encoder_graph)

    reconstruction = decoder_graph
    original = dummy_x

    loss_function = tf.reduce_mean(tf.pow(original - reconstruction, 2))
    optimizer = tf.train.AdamOptimizer().minimize(loss_function)

    return (loss_function, optimizer)


def train(input_data):
    """Train the autoencoder with the input data array.
    The data array should be a two-dimensional array.

    Args:
        input_data: np array. 2-dim.
    """
    input_x = tf.placeholder(tf.float32, shape=(None, INPUT_DIM))

    # Put input_x in our model
    loss, optimizer = model(input_x)

    # Initialize tf Session
    init = tf.initialize_all_variables()

    # Launch training process
    with tf.Session() as session:
        session.run(init)

        # Training cycle
        for epoch in range(NUM_EPOCH):
            for batch in range(NUM_BATCH):
                batch_x = input_data[batch::NUM_BATCH]
                session.run(optimizer, feed_dict={input_x: batch_x})

            # output logs per epoch
            loss_per_epoch = session.run(loss, feed_dict={
                input_x: input_data[:NUM_BATCH * NUM_EPOCH:1]})
            print("Epoch: ", '%02d' % (epoch + 1),
                  " cost: ", "{:.6f}".format(loss_per_epoch))


def main():
    """The whole work flow of training the encoder"""
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    # Positional Args
    parser.add_argument('data', metavar='DATA', nargs='?',
                        help='compressed Numpy data')
    args = parser.parse_args()

    train(np.load(args.data))


if __name__ == "__main__":
    main()
