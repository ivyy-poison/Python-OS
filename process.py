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

    def __init__(self, arrival_time: int = 0) -> None:
        self.pid: int = Process._next_pid
        self.arrival_time: int = arrival_time
        self.time_to_completion = random.randint(5, 15)
        self.state: ProcessState = ProcessState.READY

        self.__increment_global_pid()

    def run_for(self, time_slice: int) -> int:
        """
        Run the process for a given time slice.
        Decrements the time to completion and terminates the process if completed.
        Returns the actual time the process ran for.
        """
        assert self.state in {ProcessState.READY, ProcessState.RUNNING}, (
            f"Process {self.pid} cannot run because it is in state {self.state}"
        )
        self.state = ProcessState.RUNNING
        actual_time = min(time_slice, self.time_to_completion)
        self.time_to_completion -= actual_time

        if self.time_to_completion <= 0:
            self.terminate()

        return actual_time

    def run_to_completion(self) -> int:
        """
        Run the process to completion.
        Returns the total time the process ran for during this call.
        """
        assert self.state in {ProcessState.READY, ProcessState.RUNNING}, (
            f"Process {self.pid} cannot run because it is in state {self.state}"
        )
        self.state = ProcessState.RUNNING
        actual_time = self.time_to_completion
        self.time_to_completion = 0
        self.terminate()
        return actual_time

    def terminate(self) -> None:
        assert self.state != ProcessState.TERMINATED, f"Process {self.pid} is already terminated."
        self.state = ProcessState.TERMINATED

    def is_terminated(self) -> bool:
        return self.state == ProcessState.TERMINATED
    
    def __repr__(self) -> str:
        return (f"Process(pid={self.pid}, "
                f"arrival_time={self.arrival_time}, time_to_completion={self.time_to_completion}, "
                f"state={self.state})")

    def __str__(self) -> str:
        return (f"<{self.pid}>")