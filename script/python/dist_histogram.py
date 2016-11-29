#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Analysis code for NIS project: pair-wise distance histograms.

This program reads in a trajectory with the corresponding topology file.
The user should specify two groups of residues using MDAnalysis's selection
string. For example,

--group1 "protein and resid 1 2 3"
--group2 "protein and resid 4 5 6"

Then the program will calculate the minimun contact distances for every pair
of residues defined in the product space of group1 and group2. The program will
plot the distance with a banch of histograms and will calculate a fitting curve
for each histograms.
"""

import argparse
import itertools
import pickle

import glog as log
import numpy as np
from MDAnalysis import Universe
from MDAnalysis.lib.distances import distance_array

from scipy.interpolate import interp1d

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


__author__ = 'davislong198833@gmail.com (Yunlong Liu)'

DESCRIPTION = 'pair wise distance histograms for selected atoms'

log.setLevel("INFO")

# Global constants for plotting data.
_NUM_COLUMNS = 3
_COLUMN_WIDTH = 4
_NUM_BINS = 50

_LEFT_LIM = 0
_RIGHT_LIM = 10
_NUM_SAMPLE = 200


def plot_data(data, file_name):
    """plot data to histograms.

    Args:
        data: dict type, (name, numpy-array [float32])
        file_name: figure file name
    """
    num_rows = int(np.ceil(float(len(data)) / _NUM_COLUMNS))

    # create figure handle
    plt.figure(figsize=(_NUM_COLUMNS * _COLUMN_WIDTH,
                        num_rows * _COLUMN_WIDTH))

    for (plt_index, (name, dist_data)) in enumerate(data.iteritems()):
        row_index = plt_index / _NUM_COLUMNS
        col_index = plt_index % _NUM_COLUMNS

        axe = plt.subplot2grid((num_rows, _NUM_COLUMNS),
                               (row_index, col_index))

        weights = np.ones_like(dist_data) / len(dist_data)
        counts, bins, _ = axe.hist(dist_data, _NUM_BINS, weights=weights,
                                   range=(_LEFT_LIM, _RIGHT_LIM),
                                   facecolor='green', alpha=0.25)

        fitting_curve = interp1d(bins, np.append(counts, 0.0), kind='cubic')
        fitting_x = np.linspace(_LEFT_LIM, _RIGHT_LIM,
                                _NUM_SAMPLE, endpoint=True)
        axe.plot(fitting_x, fitting_curve(fitting_x), 'r-', linewidth=2.0)

        axe.set_xlabel("%s vs. %s (A)" % (name[0][:-2], name[1][:-2]),
                       fontsize=10, color='blue', variant='small-caps')
        axe.set_ylabel(r"Frequency in %d frames" % len(dist_data),
                       fontsize=10, color='blue', variant='small-caps')
        axe.set_xlim(left=_LEFT_LIM, right=_RIGHT_LIM)

    plt.tight_layout()
    plt.savefig(file_name)
    log.info("save figure to file %s", file_name)
    plt.close()


def process_trajectory(universe, group1, group2):
    """process the trajectory and calculate the pair-wise min distances

    Args:
        universe: Universe Object
        group1: selection group1
        group2: selection group2

    Returns:
        data: dict type, (name, numpy-array [float32])

    """
    data = {}
    group_one = universe.select_atoms(group1).residues
    group_two = universe.select_atoms(group2).residues

    raw_data = np.empty([universe.trajectory.n_frames,
                         len(group_one) * len(group_two)], dtype=float)

    for time_step in universe.trajectory:
        if time_step.frame % 100 == 0:
            log.info("processing frame %d.", time_step.frame)

        for (index, (res_one, res_two)) in enumerate(
                itertools.product(group_one, group_two)):
            min_dist = np.amin(
                distance_array(res_one.positions, res_two.positions,
                               backend="OpenMP"))
            raw_data[time_step.frame][index] = \
                min_dist if min_dist < _RIGHT_LIM else _RIGHT_LIM

    raw_data = np.transpose(raw_data)

    for (index, (res_one, res_two)) in enumerate(itertools.product(group_one,
                                                                   group_two)):
        key = ("%s_%d_1" % (res_one.resname, res_one.resid),
               "%s_%d_2" % (res_one.resname, res_two.resid))
        data[key] = raw_data[index]

    return data


def main():
    """Main entry to the program

    Parse the command line args and hand it into trajectory processor.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('topology', metavar='TOPOLOGY', nargs='?',
                        help='input topology file (.gro)')
    parser.add_argument('trajectory', metavar='TRAJECTORY', nargs='?',
                        help='input trajectory file (.xtc/.trr)')

    parser.add_argument('--png', help='output figure file (.png)')
    parser.add_argument('--group1', help='selection string for group one')
    parser.add_argument('--group2', help='selection string for group two')
    parser.add_argument('--dump', help='binary data file to dump')

    args = parser.parse_args()

    log.info("dist_histogram inits")
    # I/O, read in the trajectory
    try:
        universe = Universe(args.topology, args.trajectory)
    except IOError:
        log.error("Cannot open input file. [topology: %s, trajectory: %s]",
                  args.topology, args.trajectory)
        exit()

    log.info("read trajectory %s", args.trajectory)
    data = process_trajectory(universe, args.group1, args.group2)

    if args.dump:
        with open(args.dump, 'wb') as output:
            pickle.dump(data, output, pickle.HIGHEST_PROTOCOL)

    log.info("start to plot histogram")
    plot_data(data, args.png)
    log.info("dist_histogram terminates")


if __name__ == "__main__":
    main()
