#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Analysis code for PI3K Project: Interaction time series.
This program reads in a trajectory with the corresponding topology file.
The user should specify a group of residues using MDAnalysis's selection
string, and a distance cutoff. For example,
--group1 "protein and resid 1 2 3"
--cutoff 4.0
Then the program will determine the atoms that are present within the cutoff
distance throughout the trajectory and output this data into a readable file.
"""

import argparse

import glog as log
from MDAnalysis import Universe

__author__ = 'mchakra8@jhu.edu (Mayukh Chakrabarti)'

DESCRIPTION = 'interaction time series for selected atoms'

log.setLevel("INFO")

def process_trajectory(universe, group1, cutoff, timestep):
    """process the trajectory and determine the interacting residues
    Args:
        universe: Universe Object
        group1: selection group1
        cutoff: cutoff distance in angstroms
    Returns:
        interaction_data: list type, [(time, list [string containing atom name, resname, residue id])]
    """

    interaction_data = []

    for time_step in universe.trajectory:

        if time_step.frame % timestep == 0:
            interacting_atoms = universe.select_atoms("around " + str(cutoff) + " " + group1)
            atom_data = ["%s" % ("\t\t\tAtom " + atom.name + " in residue " + atom.resname + str(atom.resid)) for atom in interacting_atoms]
            
            interaction_data.append((time_step.frame, atom_data))

	    if time_step.frame % 100 == 0:
		log.info("processing frame %d.", time_step.frame)

    return interaction_data

def process_data(data):

    """Return a list with a formatted output of the atoms interacting at each timestep
    Args:
        data: a list of interaction data
    Returns:
        formatted_list: a list of string representations for the interaction output
    """

    atom_list = []
    time_list = []
    formatted_list = []

    for data_tuple in data:
	time, atoms = data_tuple
        time_list.append(time)

        temp_string = "\n".join(atoms)
        atom_list.append(temp_string)
         
    for i in range(len(data)):
         formatted_list.append("\n" + str(time_list[i]) + atom_list[i] + "\n")

    return formatted_list

def main():
    """Main entry to the program
    Parse the command line args and hand it into trajectory processor.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)

    parser.add_argument('topology', metavar='TOPOLOGY', nargs='?',
                        help='input topology file (.gro)')
    parser.add_argument('trajectory', metavar='TRAJECTORY', nargs='?',
                        help='input trajectory file (.xtc/.trr)')

    parser.add_argument('--output', help='output data file in readable format (e.g., *.dat, *.txt)')
    parser.add_argument('--group1', help='selection string for group one')
    parser.add_argument('--cutoff', default=4.0, type=float, help='cutoff distance for interactions in Angstroms')
    parser.add_argument('--timestep', default=10, type=int, help='time interval for analysis of interactions (frames)')

    args = parser.parse_args()

    log.info("Initializing analysis")
    # I/O, read in the trajectory
    try:
        universe = Universe(args.topology, args.trajectory)
    except IOError:
        log.error("Cannot open input file. [topology: %s, trajectory: %s]",
                  args.topology, args.trajectory)
        exit()

    log.info("read trajectory %s", args.trajectory)
    data = process_trajectory(universe, args.group1, args.cutoff, args.timestep)
    formatted_data = process_data(data)
    
    with open(args.output, "w") as outfile:
        outfile.write("Interaction data based on a cutoff distance of " + str(args.cutoff) + " Angstroms\n\n")
	outfile.write("The group used for the cutoff analysis is: " + args.group1 + "\n\n")
        outfile.write("Frame\t\t\tResidues\n")
        for line in formatted_data:
            outfile.write(line)
            
    outfile.close()
    log.info("Time series program has successfully terminated.")


if __name__ == "__main__":
    main()
