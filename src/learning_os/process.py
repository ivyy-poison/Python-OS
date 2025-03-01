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
    process_table: dict[int, "Process"] = {} 

    def __increment_global_pid(self) -> None:
        """ Increment the global PID counter."""
        Process._next_pid += 1

    def __init__(
        self,
        arrival_time: int = 0,
        io_probability: float = 0.3,
        time_to_completion: int = None,
    ) -> None:
        assert(0 <= io_probability <= 1), "I/O probability must be between 0 and 1"
        assert(time_to_completion is None or time_to_completion > 0), "Time to completion must be greater than 0"

        self.pid: int = Process._next_pid
        self.arrival_time: int = arrival_time
        self.time_to_completion: int = time_to_completion if time_to_completion else random.randint(5, 10)
        self.cumulative_time_ran: int = 0
        self.io_probability: float = io_probability
        self.state: ProcessState = ProcessState.READY

        Process.process_table[self.pid] = self
        self.__increment_global_pid()

    def run_for(self, time_slice: int) -> int:
        """
        Run the process for a given time slice. Decrements the time to completion and, 
        with some probability, simulates an I/O event. Note: only a process that is currently
        in the RUNNING state can run.

        Args:
        time_slice (int): The time slice to run the process for.

        Returns:
        int: The actual time the process ran.
        """
        assert self.state in {ProcessState.RUNNING}, (
            f"Process {self.pid} cannot run because it is in state {self.state}"
        )
        self.state = ProcessState.RUNNING

        max_run = min(time_slice, self.time_to_completion)
    
        if random.random() < self.io_probability and max_run > 1:
            ## An I/O Event has occurred
            effective_run_time = random.randint(1, max_run - 1)
            self.time_to_completion -= effective_run_time
            self.cumulative_time_ran += effective_run_time
            self.state = ProcessState.WAITING
            print(f"Process {self.pid} triggered I/O after running for {effective_run_time} time units.")
            return effective_run_time
        else:
            ## An I/O Event has not occurred
            actual_time = max_run
            self.time_to_completion -= actual_time
            self.cumulative_time_ran += actual_time
            if self.time_to_completion <= 0:
                self.terminate()
            print(f"Process {self.pid} ran for {actual_time} time units without I/O.")
            return actual_time
    
    def is_in_io_state(self) -> bool:
        """
        Check if the process is in the I/O state.
        
        Returns:
        bool: True if the process is in the I/O state, False otherwise.
        """
        return self.state == ProcessState.WAITING

    def terminate(self) -> None:
        """ Terminate the process."""
        assert self.state != ProcessState.TERMINATED, f"Process {self.pid} is already terminated."
        self.state = ProcessState.TERMINATED

        if self.pid in Process.process_table:
            del Process.process_table[self.pid]

    def is_terminated(self) -> bool:
        """
        Check if the process is terminated.
        
        Returns:
        bool: True if the process is terminated, False otherwise.
        """
        return self.state == ProcessState.TERMINATED
    
    def __repr__(self) -> str:
        return (f"Process(pid={self.pid}, "
                f"arrival_time={self.arrival_time}, time_to_completion={self.time_to_completion}, "
                f"state={self.state})")

    def __str__(self) -> str:
        return (f"<{self.pid}>")