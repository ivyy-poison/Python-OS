import random
from python_os.process import Process, ProcessState

class IOManager:
    """
    A simple I/O manager to simulate I/O completion using a simulation clock.
    It processes one I/O request at a time.
    """
    def __init__(self) -> None:
        self.waiting_processes = []
        self.next_free_time: int = 0

    def add_waiting_process(self, process: Process, clock_time: int) -> None:
        """
        Add a process to the waiting list and simulate I/O completion.
        
        Args:    
        process (Process): The process that is waiting for I/O.
        clock_time (int): The current simulation clock time.
        """
        assert process.state == ProcessState.WAITING, (
            f"Process {process.pid} cannot wait for I/O because it is in state {process.state}"
        )
        io_service_time = random.randint(2, 5)

        start_time = max(clock_time, self.next_free_time)
        completion_time = start_time + io_service_time
        self.waiting_processes.append((process, completion_time))

        self.next_free_time = completion_time
        print(f"I/O Manager: Process {process.pid} will complete I/O at simulation clock {completion_time}.")

    def update(self, clock_time: int) -> list[Process]:
        """
        Check waiting processes based on the simulation clock and return the processes
        that have completed I/O.

        Args:
        clock_time (int): The current simulation clock time.
        
        Returns:
        list[Process]: A list of processes that have completed I/O.
        """
        ready_processes = []
        still_waiting = []
        for process, completion in self.waiting_processes:
            if clock_time >= completion:
                process.state = ProcessState.READY
                ready_processes.append(process)
            else:
                still_waiting.append((process, completion))
        self.waiting_processes = still_waiting
        return ready_processes