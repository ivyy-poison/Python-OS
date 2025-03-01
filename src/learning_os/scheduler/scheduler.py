import abc
from collections import deque
from learning_os.process import Process, ProcessState
from typing import Dict, List, Deque

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

class RoundRobinScheduler(Scheduler):
    """
    A class to represent a round-robin scheduler in an operating system. This scheduler will 
    allot a fixed time quantum to each process in the queue.
    """

    def __init__(self, quantum: int = 3) -> None:
        self.quantum: int = quantum
        self.queue: Deque[Process] = deque()

    def get_alloted_time(self, process: Process) -> int:
        return self.quantum

    def add_process(self, process: Process) -> None:
        assert process.state == ProcessState.READY, (
            f"Process {process.pid} cannot be added because it is in state {process.state}"
        )
        self.queue.append(process)

    def get_next_process(self) -> Process:
        if not self.queue:
            raise Exception("No processes available")
        return self.queue.popleft()

    def has_processes(self) -> bool:
        return bool(self.queue)
    
class SimpleScheduler(Scheduler):
    """
    A class to represent a simple scheduler in an operating system. This scheduler will 
    run processes to completion in the order they arrive.
    """

    def __init__(self) -> None:
        self.queue: Deque[Process] = deque()

    def get_alloted_time(self, process: Process) -> int:
        return process.time_to_completion

    def add_process(self, process: Process) -> None:
        assert process.state == ProcessState.READY, (
            f"Process {process.pid} cannot be added because it is in state {process.state}"
        )
        self.queue.append(process)

    def get_next_process(self) -> Process:
        if not self.queue:
            raise Exception("No processes available")
        return self.queue.popleft()

    def has_processes(self) -> bool:
        return bool(self.queue)
    