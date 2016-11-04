#!/bin/bash -l
#SBATCH
#SBATCH --job-name=test
#SBATCH --time=6:0:0
#SBATCH -N 1
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=6
#SBATCH --exclusive
#SBATCH --partition=gpu
#SBATCH --gres=gpu:4
#

source ~/opt/bin//GMXRC
export OMP_NUM_THREADS=6
cd ~/scratch/Mario/pep-2-11/
gmx_mpi grompp -f ../mdp/md.mdp -o md_2.tpr -c md_1.gro -p topol.top -t md_1.cpt
~/opt/bin//mpirun -np 4 gmx_mpi mdrun -ntomp 6 -pin on -v -deffnm md_2 -dlb no -gpu_id 0123
