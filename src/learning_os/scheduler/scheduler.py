import abc
from learning_os.process import Process

class Scheduler(abc.ABC):
    """
    A class to represent a scheduler in an operating system. It will provide a common interface
    from which all scheduler models will inherit, providing methods for adding processes, getting
    the next process to run, and determining if there are processes left to run.
    """

    @abc.abstractmethod
    def get_alloted_time(self, process: Process) -> int:
        """
        Return the amount of time to allot to a process.
        
        Args:
        process (Process): The process to allot time to.
        """
        pass

    @abc.abstractmethod
    def add_process(self, process: Process) -> None:
        """Add a process to the scheduler."""
        pass

    @abc.abstractmethod
    def get_next_process(self) -> Process:
        """Return the next process to run."""
        pass

    @abc.abstractmethod
    def has_processes(self) -> bool:
        """Return True if there are processes waiting to be scheduled."""
        pass
    

    