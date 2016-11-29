#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Analysis code for NIS project: distance histograms.
"""

import argparse
import itertools
import pickle

import glog as log
import numpy as np
from MDAnalysis import Universe
from MDAnalysis.lib.distances import distance_array

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'

DESCRIPTION = 'pair wise distance histograms for selected atoms'

log.setLevel("INFO")


def plot_data(data, frames, file_name):

    # plotting data
    num_plots = len(data)
    columns = 3
    rows = num_plots / 3

    # figure handle
    fig = plt.figure(figsize=(columns * 4, rows * 4))
    keys = sorted(data.keys())

    for i in xrange(0, num_plots):
        '''r is the row index, c is the col index'''
        r = i / columns
        c = i % columns

        ax = plt.subplot2grid((rows, columns), (r, c))
        resname_id = keys[i]
        counts, bins = np.histogram(np.array(data[resname_id]), [
                                    0.2 * x for x in range(10, 40)])
        normed_counts = map(lambda x: float(x) / frames, counts)
        ax.plot(bins, normed_counts + [0], 'b-')
        ax.set_xlabel("Residue " + resname_id + "          (A)",
                      fontsize=10, color='blue', variant='small-caps')
        ax.set_ylabel(r'Frequency' + ' in ' + str(frames) + ' frames',
                      fontsize=10, color='blue', variant='small-caps')
        ax.set_xlim(left=1, right=8)
        ax.set_ylim(0, max(normed_counts) * 2)

        fig.suptitle(r'histogram of contact', fontsize=20,
                     color='blue', weight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(file_name + ".png")
        plt.close()

fid = 0


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

        i = 0
        for (res_one, res_two) in itertools.product(group_one, group_two):
            raw_data[time_step.frame][i] = np.amin(
                distance_array(res_one.positions, res_two.positions))
            i += 1

    raw_data = np.transpose(raw_data)

    i = 0
    for (res_one, res_two) in itertools.product(group_one, group_two):
        key = ("%s_%d_1" % (res_one.resname, res_one.resid),
               "%s_%d_2" % (res_one.resname, res_two.resid))
        data[key] = raw_data[i]
        i += 1

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
    plot_data(data, 1000, args.png)


if __name__ == "__main__":
    main()
