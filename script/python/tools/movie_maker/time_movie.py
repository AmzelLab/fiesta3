#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A small utility program to add time label to the a set of images. This utility
serves at the downstream of the VMD's movie maker. VMD's movie maker generates
a set of images labeled with [NAME].[STEP].ppm (e.g. untitled.00000.ppm). We
defaultly consider all images labeled like this.

Usage:
    ./time_movie --step_size [STEP_SIZE] your_working_folder
"""

import argparse
import os

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


DEFAULT_STEP_SIZE = 0.02
FONT_SIZE = 20
DESCRIPTION = 'add time label to frames'


class MovieFrames(object):
    """Iterator class of movie frames in the working folder."""

    def __init__(self, working_folder, step_size):
        """Constructor of the MovieFrames Iterator.

        Args:
            working_folder: the folder user uses to store frames
            step_size: step size for each frame
        """
        self._work_dir = working_folder
        self._curr = None
        self._step_size = step_size
        self._frames = iter(sorted([f_name for f_name in os.listdir('.')
                                    if f_name.endswith('ppm')]))

    def __iter__(self):
        """Iterator implementation."""
        return self

    def __next__(self):
        """Iterator implementation."""
        return self.next()

    def next(self):
        """return the next metadata of the movie frames

        Backward compatibility to python 2.
        """
        self._curr = next(self._frames)
        f_index = int(self._curr.split('.')[1]) + 1

        img = Image.open(self._curr)
        label = '{:8.2f}'.format(f_index * self._step_size) + ' ns'

        return (label, img)

    @property
    def current_file(self):
        """return the current file name

        Returns:
            string, the filename of the current frame
        """
        return self._curr


def add_time_to_frames(folder, font, step_size=DEFAULT_STEP_SIZE):
    """Add time labels to all frames

    Args:
        folder: the working folder
        font: font file to load
        step_size: float, step size for each frame.
    """
    font = ImageFont.truetype(font, FONT_SIZE)

    frames = MovieFrames(folder, step_size)
    for (label, frame) in frames:
        draw = ImageDraw.Draw(frame)
        draw.text((0, 10), label, font=font, fill=(255, 255, 255, 128))
        frame.save(frames.current_file)
        frame.close()


def main():
    """Main entry for this utility program."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    # Positional Args
    parser.add_argument('working_folder', metavar='WORKING_FOLDER', nargs='?',
                        help='working folder for movie generation')

    # Non-positional Args
    parser.add_argument('--step_size', type=float, default=DEFAULT_STEP_SIZE,
                        help='step size for each frame')
    parser.add_argument('--font', required=True,
                        help='font file for creating label')

    args = parser.parse_args()

    add_time_to_frames(args.working_folder, args.font, args.step_size)


if __name__ == "__main__":
    main()
