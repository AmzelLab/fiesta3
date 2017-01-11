#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Implement a basic classical autoencoder for experimental purposes"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import numpy as np
import tensorflow as tf

__author__ = 'Yunlong Liu (davislong198833@gmail.com)'

INPUT_DIM = 1024
HIDDEN_1_DIM = 256
HIDDEN_2_DIM = 32
BATCH_SIZE = 256

WEIGHTS = {
    'encoder_h1': tf.Variable(tf.random_normal())
}

def encoder(dummy_x):
    """Build the encoder graph

    Args:
        dummy_x: the input x placeholder.

    Returns:
        The output dummy layer.
    """
    pass

def decoder(dummy_z):
    """Build the decoder graph

    Args:
        dummy_z: the input z placeholder

    Returns:
        The reconstruction of X, original data.
    """
    pass


def train(input_data):
    """Train the autoencoder with the input data array.
    The data array should be a two-dimensional array.

    Args:
        input_data: np array. 2-dim.
    """
    input_x = tf.placeholder(tf.float32, shape=(BATCH_SIZE, input_dim))


def main():
    """The whole work flow of training the encoder"""
    pass

if __name__ == "__main__":
   main()
