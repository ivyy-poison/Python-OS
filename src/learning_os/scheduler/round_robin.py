from collections import deque
from learning_os.process import Process, ProcessState
from learning_os.scheduler import Scheduler
from typing import Dict, List, Deque

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