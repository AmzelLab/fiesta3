"""Classes to generate a slurm batch file

Classes in this file with take a structured meta
data of a single job and generate the corresponding
SLURM batch script.
"""

from abc import ABCMeta
from abc import abstractmethod

__author__ = 'davislong198833@gmail.com (Yunlong Liu)'


def _dump_exclusion_list(job_data):
    """Dump the BatchFile's list to the designated file.

    Args:
        job_data: dict, the json job data.
    """
    with open(job_data["exclusion"], 'w') as excluded_file:
        for node in job_data["exclusionList"]:
            excluded_file.write(node + '\n')


def add_exclusion_node(job_data, node_id):
    """Add a newly discovered node to the job's exclusion list

    Args:
        job_data: dict, the json job data.
        node_id: string, the node's id.
    """
    if "exclusion" not in job_data:
        # give a default naming to the exclusion file of this job.
        job_data["exclusion"] = job_data["name"] + "_exclusion"
        job_data["exclusionList"] = []

    job_data["exclusionList"].append(node_id)
    job_data["exclusionList"] = list(set(job_data["exclusionList"]))
    job_data["exclusionList"].sort()

    _dump_exclusion_list(job_data)


class BatchFile(object):
    """An interface for generating batch files from job data.
    """
    __metaclass__ = ABCMeta

    REQUIRED = ["name", "timeLimit", "numOfNodes", "binaryPath",
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

        if "exclusion" in self._data and "exclusionList" not in self._data:
            self._data["exclusionList"] = []

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

    def __load_exclusion_list(self):
        """Always load eagerly from a file"""
        with open(self._data["exclusion"], 'r') as excluded_file:
            for line in excluded_file:
                self._data["exclusionList"].append(line.rstrip())

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
                 "#SBATCH -N %d\n"               \
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

        if "exclusionList" in self._data:
            if not self._data["exclusionList"]:
                self.__load_exclusion_list()
            header += "#SBATCH --exclude=%s\n" % ",".join(
                self._data["exclusionList"])

        return header + "#\n\n"

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

    def __init__(self, data, file_name="batch", makeup=False):
        """Init with a structured data of the batch job for Gromacs.

        Args:
            data: dict type, all params for the batch jobs.
            file_name: string, the file name of the batch file we will
            generate.
            makeup: Boolean, generate a makeup batchfile.
        """
        super(GromacsBatchFile, self).__init__(data, file_name)

        self.__makeup = makeup
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
            gpu_flag += str(i) * int(self._data["numOfProcs"] /
                                     self._data["numOfGPUs"])

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
        # Eventually should be user defined. But for simpilicity,
        # hard code it here.
        return "module load gcc\n"           \
               "module load intel-mpi\n"     \
               "module load cuda/7.5\n\n"    \
               "source %s/GMXRC\n"           \
               "export OMP_NUM_THREADS=%d\n" \
               "cd %s\n" % (self._data["binaryPath"],
                            self._data["numOfThrs"],
                            self._data["directory"])

    def __grompp(self):
        """Generate grompp command"""

        # TODO(yliu120): dependency injection for the configuration later.
        grompp = "mdrun -np 1 gmx_mpi grompp -f %s -o %s.tpr -c %s.gro" \
                 "-p topol.top" % (self._data["mdp"], self.__next_sec_name(),
                                   self.__curr_sec_name())

        if "index" in self._data:
            grompp += " -n %s.ndx" % self._data["index"]

        if "continuation" in self._data:
            grompp += " -t %s.cpt\n" % self.__curr_sec_name()
        else:
            grompp += "\n"

        return grompp

    def __mdrun(self):
        """Generate makeup command"""
        mdrun = "mpirun -np %d gmx_mpi mdrun -ntomp %d -pin on -v" % (
            self._data["numOfProcs"],
            self._data["numOfThrs"])

        if self.__makeup:
            mdrun += " -deffnm %s -cpi %s.cpt -append" % (
                self.__curr_sec_name(), self.__curr_sec_name())
        else:
            mdrun += " -deffnm %s" % self.__next_sec_name()

        if self._data["partition"] == "gpu":
            mdrun += " -dlb no -gpu_id %s\n" % self.__gpu_flag()
        else:
            mdrun += "\n"

        return mdrun

    def _binary(self):
        """Generate binary command line for Gromacs job.

        Returns:
            binary commands content of string type.
        """
        if self.__makeup:
            return self.__mdrun()
        return self.__grompp() + self.__mdrun()


def batch_file_factory(job, file_name):
    """A factory method for generating batch files.

    Args:
        job: the job dict parsed from json.
        file_name: the batch file's file name.
    """
    if job["kind"] == "Gromacs":
        GromacsBatchFile(job, file_name, job["makeup"]).file()
