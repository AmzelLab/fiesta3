#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
testing whether a gromacs traj file removes pbc successfully.
Usage:
    python test_pbc.py ref.gro *.xtc
"""

import sys

from MDAnalysis import Universe
from MDAnalysis.analysis.align import alignto

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'

THRESHOLD = 10


def main():
    """Entry to validate_pbc.py"""

    if len(sys.argv) < 3:
        print "Please provide at least a reference file and a trajectory" \
              " for validation"
        sys.exit(1)

    argv = sys.argv[1:]
    ref_name = argv.pop(0)

    for xtc_name in argv:
        print "checking file " + xtc_name
        judger = True
        ref = Universe(ref_name)
        xtc = Universe(ref_name, xtc_name)

        total = 0.0
        count = 0

        for frame in xtc.trajectory:
            rmsd = alignto(xtc, ref, select='protein and name CA')
            if rmsd[1] > THRESHOLD:
                print "At " + str(frame.frame) + " violates the criterion."
                print "trajectory file " + xtc_name + " is invalid."
                judger = False
                break
            total += rmsd[1]
            count += 1

        if judger:
            print "pass" + " - " + "average rmsd: " + str(total / count)

if __name__ == "__main__":
    main()
