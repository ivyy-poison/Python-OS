from learning_os.process import Process, ProcessState
from learning_os.scheduler import Scheduler

from collections import deque
from typing import Dict, List, Deque

class MultiLevelFeedbackQueueScheduler(Scheduler):
    """
    A multi-level feedback queue scheduler implementation. In this model:
    
    - Processes are assigned to different priority levels with their own time quanta.
    - The scheduler tracks how much time a process has spent at its current level.
    - If a process consumes its entire quantum at a given level, it is demoted.
    - An auto bump resets all processes back to the highest priority level at fixed intervals to avoid starvation.
    """
    def __init__(self, quanta: list[int] = None, auto_bump_interval: int = 5, boost_threshold: int = 50) -> None:
        """
        Args:
        quanta (list[int], optional): A list of time quanta for each level. If not provided, defaults to [3,6,12].
        auto_bump_interval (int): The simulation time interval at which all processes are bumped to the top level.
        """
        if quanta is None:
            quanta = [3, 6, 12]
        self.levels = quanta
        self.queues: List[Deque[Process]] = [deque() for _ in range(len(quanta))]
        self.process_levels: Dict[int, int] = {}                        # process.pid -> current level
        self.process_time_in_level: Dict[int, int] = {}                 # process.pid -> accumulated usage time at current level
        self.process_previous_cumulative_runtime: Dict[int, int] = {}   # process.pid -> previous cumulative runtime

        self.process_last_boost: Dict[int, int] = {}                    # process.pid -> last time the process was boosted
        self.auto_bump_interval = auto_bump_interval
        self.boost_threshold = boost_threshold
        self.last_bump_time = 0

    def get_alloted_time(self, process: Process) -> int:
        """
        Return the quantum for a process based on its current level.
        """
        level = self.process_levels.get(process.pid, 0)
        return self.levels[level]

    def add_process(self, process: Process) -> None:
        assert process.state == ProcessState.READY, (
            f"Process {process.pid} cannot be added because it is in state {process.state}"
        )

        if process.pid not in self.process_levels:
            self.process_levels[process.pid] = 0
            self.process_time_in_level[process.pid] = 0
            from learning_os.cpu import CPU 
            curr_time = CPU.get_current_time()
            self.process_last_boost[process.pid] = curr_time

        else:
            time_used = process.cumulative_time_ran - self.process_previous_cumulative_runtime[process.pid]
            self.update_usage_time(process, time_used)

        self.process_previous_cumulative_runtime[process.pid] = process.cumulative_time_ran
        level = self.process_levels[process.pid]
        queue = self.queues[level]
        queue.append(process)

    def auto_boost_processes(self) -> None:
        """
        For every process in all queues (except the top-level),
        check if the time elapsed since its last boost (as stored in process_last_boost)
        is greater than or equal to boost_threshold. If so, move it to the highest priority.
        """
        from learning_os.cpu import CPU  
        curr_time = CPU.get_current_time()  

        for level in range(1, len(self.queues)):
            new_queue = deque()
            while self.queues[level]:
                process = self.queues[level].popleft()
                pid = process.pid
                last_boost = self.process_last_boost.get(pid)
                assert last_boost is not None, "Process should have a last boost time."

                if curr_time - last_boost >= self.boost_threshold:
                    self.process_levels[pid] = 0
                    self.process_time_in_level[pid] = 0
                    self.process_last_boost[pid] = curr_time
                    self.queues[0].append(process)
                    print(f"Auto boost: Process {pid} boosted to top priority at time {curr_time}.")
                
                else:
                    new_queue.append(process)

            self.queues[level] = new_queue

    def get_next_process(self) -> Process:
        """
        Search the queues starting from the highest priority level and return the first process found.
        """
        ## Cleanup the existing scheduler ##
        self.cleanup()
        self.auto_boost_processes()
        ## Cleanup the existing scheduler ##

        for q in self.queues:
            if q:
                return q.popleft()
        raise Exception("No processes available")

    def has_processes(self) -> bool:
        """
        Return True if any of the queues has processes.
        """
        return any(q for q in self.queues)

    def update_usage_time(self, process: Process, time_used: int) -> None:
        """
        Update the accumulated time for the process in its current level. If the process has exhausted its quantum,
        demote it.
        """
        pid = process.pid
        current_level = self.process_levels.get(pid, 0)
        self.process_time_in_level[pid] = self.process_time_in_level.get(pid, 0) + time_used
        
        quantum = self.levels[current_level]
        if self.process_time_in_level[pid] >= quantum:
            # Demote the process if possible.
            if current_level < len(self.levels) - 1:
                self.process_levels[pid] = current_level + 1
            # Reset its accumulated time at this new level.
            self.process_time_in_level[pid] = 0

    def cleanup(self):
        for level in range(len(self.queues)):
            self.queues[level] = deque(
                process for process in self.queues[level] if not process.is_terminated() 
            )

        for pid in list(self.process_levels.keys()):
            process = Process.process_table.get(pid)
            if process is None or process.is_terminated():
                self.process_levels.pop(pid, None)
                self.process_time_in_level.pop(pid, None)
                self.process_previous_cumulative_runtime.pop(pid, None)
                self.process_last_boost.pop(pid, None)