"""Classes to generate a slurm batch file

Classes in this file with take a structured meta
data of a single job and generate the corresponding
SLURM batch script.
"""

from abc import ABCMeta
from abc import abstractmethod

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


class BatchFile(object):
    """An interface for generating batch files from job data.
    """
    __metaclass__ = ABCMeta

    REQUIRED = ["name", "timeLimit", "numOfNodes", "binaryFolder",
                "numOfProcs", "numOfThrs", "partition"]

    def __init__(self, data, file_name="batch"):
        """Init with a structured data of the batch job.

        Args:
            data: dict type, all params for the batch jobs.
            file_name: string, the file name of the batch file we will
            generate.
        """
        self._data = data
        self.__check_data()

        self._file_name = file_name

    @property
    def file_name(self):
        """Getter method for the file name.
        Returns:
            The file name
        """
        return self._file_name

    @file_name.setter
    def file_name(self, fname):
        """Setter for _file_name

        Args:
            fname: file name
        """
        self._file_name = fname

    def __check_data(self):
        """Check whether the structured data has all required fields.

        Returns:
            Returns void or raise exceptions
        """
        for name in BatchFile.REQUIRED:
            if name not in self._data:
                raise ValueError("% s is a required field but not shown"
                                 " your json configuration file." % name)

    @abstractmethod
    def _header(self):
        """Generate header lines in the batch file from
        the given data

        Returns:
            header content in a string
        """
        header = "#!/bin/bash -l\n"               \
                 "#SBATCH\n"                      \
                 "#SBATCH --job-name=%s\n"        \
                 "#SBATCH --time=%s\n"            \
                 "#SBATCH --N %d\n"               \
                 "#SBATCH --ntasks-per-node=%d\n" \
                 "#SBATCH --cpus-per-task=%d\n"   \
                 "#SBATCH --exclusive\n"          \
                 "#SBATCH --partition=%s\n" %     \
                 (self._data["name"], self._data["timeLimit"],
                  self._data["numOfNodes"], self._data["numOfProcs"],
                  self._data["numOfThrs"], self._data["partition"])

        if self._data["partition"] == "gpu":
            if "numOfGPUs" not in self._data:
                raise ValueError("numOfGPUs is a required field when "
                                 "submitting to GPU.")

            num_gpus = int(self._data["numOfGPUs"])
            num_tasks = int(self._data["numOfProcs"])

            if num_gpus > num_tasks:
                raise ValueError("Requesting redundant GPUs")
            if num_tasks % num_gpus != 0:
                raise ValueError("Tasks can't be evenly distributed to GPUs")

            header += "#SBATCH --gres=gpu:%d\n" % self._data["numOfGPUs"]

        return header

    @abstractmethod
    def _environments(self):
        """Generate environment lines in the batch file from
        the given data

        Returns:
            environments content in a string
        """
        pass

    @abstractmethod
    def _binary(self):
        """Generate binary command line in the batch file.

        Returns:
            binary commands content of string type.
        """
        pass

    def file(self):
        """Call this method to get the file generated.
        """
        with open(self._file_name, 'w+') as batch_file:
            batch_file.write(self._header())
            batch_file.write(self._environments())
            batch_file.write(self._binary())


class GromacsBatchFile(BatchFile):
    """Generating batch file for Gromacs job.
    """

    REQUIRED = ["mdp", "continuation"]

    def __init__(self, data, file_name="batch"):
        """Init with a structured data of the batch job for Gromacs.

        Args:
            data: dict type, all params for the batch jobs.
            file_name: string, the file name of the batch file we will
            generate.
        """
        super(GromacsBatchFile, self).__init__(data, file_name)
        self.__check_data()

    def __check_data(self):
        """Check whether the structured data has all required fields,
        specifically for Gromacs MDrun jobs

        Returns:
            Returns void or raise exceptions
        """
        for name in GromacsBatchFile.REQUIRED:
            if name not in self._data:
                raise ValueError("Item %s (Gromacs Job) requires %s field "
                                 "to be set" % (self._data["name"], name))

    def __gpu_flag(self):
        """Generate gpu flag for -gpu_id command line flag

        Returns:
            gpu flag string
        """
        gpu_flag = ""
        for i in range(0, self._data["numOfGPUs"]):
            gpu_flag += str(i) * self._data["numOfProcs"] / \
                self._data["numOfGPUs"]

        return gpu_flag

    def __curr_sec_name(self):
        """Generate the full file name with the current section id.
        Returns:
            The file name for next MD section run.
        """
        return "%s_%d" % (self._data["nameBase"], self._data["sectionNum"])

    def __next_sec_name(self):
        """Generate the full file name with the next section id.
        Returns:
            The file name for next MD section run.
        """
        return "%s_%d" % (self._data["nameBase"], self._data["sectionNum"] + 1)

    def _header(self):
        """Generate header for Gromacs's batch file

        Returns:
            a string header
        """
        return super(GromacsBatchFile, self)._header()

    def _environments(self):
        """Generate environments for Gromacs

        Returns:
            a string env
        """
        return "source %s/GMXRC\n" \
               "export OMP_NUM_THREADS=%d" % (self._data["binaryFolder"],
                                              self._data["numOfThrs"])

    def _binary(self):
        """Generate binary command line for Gromacs job.

        Returns:
            binary commands content of string type.
        """
        grompp = "gmx_mpi grompp -f %s -o %s.tpr -c %s.gro -p topol.top" \
                 "-n index.ndx" % (self._data["mdp"], self.__next_sec_name(),
                                   self.__curr_sec_name())
        if self._data["continuation"]:
            grompp += " -t %s.cpt\n" % self.__curr_sec_name()
        else:
            grompp += "\n"

        mdrun = "%s/mpirun -np %d gmx_mpi mdrun -ntomp %d -pin on -v -dlb no" \
                " -deffnm %s" % (self._data["binaryPath"],
                                 self._data["numOfProcs"],
                                 self._data["numOfThrs"],
                                 self.__next_sec_name())
        if self._data["partition"] == "gpu":
            mdrun += " -gpu_id %s\n" % self.__gpu_flag()
        else:
            mdrun += "\n"

        return grompp + mdrun
