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
        self.time_to_completion = random.randint(5, 5)
        self.state: ProcessState = ProcessState.READY

        self.io_probability = 1
        self.__increment_global_pid()

    def run_for(self, time_slice: int) -> int:
        """
        Run the process for a given time slice.
        Decrements the time to completion and, with some probability, simulates an I/O event.
        If an I/O event occurs, the process only runs for part of the time slice,
        an I/O delay is added to the time_to_completion, and the process is set to the WAITING state.
        Returns the actual time the process ran for.
        """
        assert self.state in {ProcessState.READY, ProcessState.RUNNING}, (
            f"Process {self.pid} cannot run because it is in state {self.state}"
        )
        self.state = ProcessState.RUNNING

        max_run = min(time_slice, self.time_to_completion)
    
        if random.random() < self.io_probability and max_run > 1:
            ## An I/O Event has occurred
            effective_run_time = random.randint(1, max_run - 1)
            self.time_to_completion -= effective_run_time
            self.state = ProcessState.WAITING
            print(f"Process {self.pid} triggered I/O after running for {effective_run_time} time units.")
            return effective_run_time
        else:
            ## An I/O Event has not occurred
            actual_time = max_run
            self.time_to_completion -= actual_time
            if self.time_to_completion <= 0:
                self.terminate()
            print(f"Process {self.pid} ran for {actual_time} time units without I/O.")
            return actual_time
    
    def is_in_io_state(self) -> bool:
        return self.state == ProcessState.WAITING

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