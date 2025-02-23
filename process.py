import enum
import random

class ProcessState(enum.Enum):
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"

class Process:
    """
    A class to represent a process in an operating system.
    """
    _next_pid: int = 1

    def __increment_global_pid(self) -> None:
        Process._next_pid += 1

    def __init__(self, priority: int = 0, arrival_time: int = 0) -> None:
        self.pid: int = Process._next_pid
        self.priority: int = priority
        self.arrival_time: int = arrival_time
        self.time_to_completion = random.randint(5, 15)
        self.state: ProcessState = ProcessState.READY

        self.__increment_global_pid()

    def run_for(self, time_slice: int) -> None:
        """
        Run the process for a given time slice. Decrements the time to completion and
        terminates the process if completed.
        """
        assert self.state in {ProcessState.READY, ProcessState.RUNNING}, (
            f"Process {self.pid} cannot run because it is in state {self.state}"
        )
        self.state = ProcessState.RUNNING
        self.time_to_completion -= time_slice

        if self.time_to_completion <= 0:
            self.terminate()

    def run_to_completion(self) -> None:
        """
        Run the process to completion.
        """
        assert self.state in {ProcessState.READY, ProcessState.RUNNING}, (
            f"Process {self.pid} cannot run because it is in state {self.state}"
        )
        self.state = ProcessState.RUNNING
        self.time_to_completion = 0
        self.terminate()

    def terminate(self) -> None:
        assert self.state != ProcessState.TERMINATED, f"Process {self.pid} is already terminated."
        self.state = ProcessState.TERMINATED

    def is_terminated(self) -> bool:
        return self.state == ProcessState.TERMINATED