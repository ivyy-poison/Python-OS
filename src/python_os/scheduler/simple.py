from collections import deque
from python_os.process import Process, ProcessState
from python_os.scheduler import Scheduler
from typing import Dict, List, Deque

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