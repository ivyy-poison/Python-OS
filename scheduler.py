import abc
import random
from collections import deque
from sortedcontainers import SortedDict
from process import Process, ProcessState
from typing import Dict, List, Deque, Tuple

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

    def __init__(self, quantum: int) -> None:
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
        else:
            time_used = process.cumulative_time_ran - self.process_previous_cumulative_runtime[process.pid]
            self.update_usage_time(process, time_used)

        self.process_previous_cumulative_runtime[process.pid] = process.cumulative_time_ran
        level = self.process_levels[process.pid]
        queue = self.queues[level]
        queue.append(process)

    def auto_boost_processes(self) -> None:
        """
        For every process in all queues, check if it has run an additional boost_threshold units
        since its last priority boost. If so, move it to the highest priority.
        """
        for level in range(1, len(self.queues)):
            new_queue = deque()
            while self.queues[level]:
                process = self.queues[level].popleft()
                pid = process.pid
                last_boost = self.process_last_boost.get(pid, 0)
                # If the cumulative time ran has increased by at least boost_threshold since last boost,
                # move the process to top priority.
                if process.cumulative_time_ran - last_boost >= self.boost_threshold:
                    self.process_levels[pid] = 0
                    self.process_time_in_level[pid] = 0
                    self.process_last_boost[pid] = process.cumulative_time_ran
                    self.queues[0].append(process)
                    print(f"Auto boost: Process {pid} boosted to top priority.")
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

class LotteryScheduler(Scheduler):
    """
    A scheduler that implements the lottery algorithm.
    
    Each process is assigned a number of tickets upon insertion. 
    When selecting the next process, a ticket is drawn uniformly at random over
    the total tickets, and the process holding that ticket wins the lottery.
    """
    def __init__(self, default_quantum: int = 5) -> None:
        """
        Args:
            default_quantum (int): Fixed quantum allotted to each process.
        """
        self.default_quantum = default_quantum
        self.processes: Dict[int, Process] = {}          # Mapping from pid to process.
        self.tickets: Dict[int, int] = {}                # Mapping from pid to ticket count.
        self.total_tickets = 0
    
    def get_alloted_time(self, process: Process) -> int:
        """
        Return the fixed quantum for a process.
        """
        return self.default_quantum

    def add_process(self, process: Process, tickets: int = 10) -> None:
        """
        Add a process to the scheduler.
        
        Args:
            process (Process): The process to be scheduled.
            tickets (int, optional): Number of tickets assigned to the process. Defaults to 10.
            
        Note:
            The process should be in READY state.
        """
        assert process.state == ProcessState.READY, (
            f"Process {process.pid} cannot be added because it is in state {process.state}"
        )
        self.processes[process.pid] = process
        self.tickets[process.pid] = tickets
        self.total_tickets += tickets

    def get_next_process(self) -> Process:
        """
        Perform a lottery draw to select the next process to run based on its ticket weight.
        """

        ## Cleanup the existing scheduler ##
        self.cleanup()
        ## Cleanup the existing scheduler ##

        if not self.has_processes():
            raise Exception("No processes available")
        
        winning_ticket = random.randint(1, self.total_tickets)
        
        cum_sum = 0
        for pid, ticket_count in self.tickets.items():
            cum_sum += ticket_count
            if winning_ticket <= cum_sum:
                chosen = self.processes.pop(pid)
                self.total_tickets -= self.tickets.pop(pid)
                return chosen
        
        # Fallback (should not happen)
        raise Exception("Lottery draw failed to select a process")

    def has_processes(self) -> bool:
        return len(self.processes) > 0
    
    def cleanup(self):
        for pid in list(self.processes.keys()):
            process = Process.process_table.get(pid)
            if process is None or process.is_terminated():
                self.processes.pop(pid, None)
                self.total_tickets -= self.tickets.pop(pid, 0)
    
class CompletelyFairScheduler(Scheduler):
    """
    A scheduler that approximates the Completely Fair Scheduler (CFS).
    
    Each process is assigned a virtual runtime (vruntime). When added, a process’s vruntime is
    set to max(current min_vruntime, its own vruntime). The available CPU time (quantum) is shared
    equally among all processes with a lower bound of min_quantum.
    
    Note: For simplicity we assume equal weighting for all processes.
    """
    def __init__(self, base_quantum: int = 10, min_quantum: int = 2) -> None:
        """
        Args:
            base_quantum (int): Total quantum available when only one process is in the scheduler.
            min_quantum (int): A lower bound on the quantum allotted per process.
        """
        self.base_quantum = base_quantum
        self.min_quantum = min_quantum

        self.virtual_tree: SortedDict = SortedDict()
        self.id_to_vruntime: Dict[int, int] = {}
    
    def get_alloted_time(self, process: Process) -> int:
        """
        Return the quantum for the process, calculated as the fair share of the base quantum by dividing it 
        by the number of processes in the scheduler plus one (the current process), and taking the maximum
        with the minimum quantum.
        """
        quantum = self.base_quantum // ( len(self.virtual_tree) + 1 ) 
        return max(quantum, self.min_quantum)
    
    def add_process(self, process: Process) -> None:
        """
        Add a process to the scheduler. Its virtual runtime is set to:
            max(current_min_vruntime, process.vruntime)
        We store the process in the virtual tree with key (vruntime, pid).
        """        
        if self.virtual_tree:
            (min_vruntime, _), _ = self.virtual_tree.peekitem(0) ## Get the smallest runtime
            self.id_to_vruntime[process.pid] = max(process.cumulative_time_ran, min_vruntime)
        else:
            self.id_to_vruntime[process.pid] = process.cumulative_time_ran
        
        key: Tuple[int, int] = (self.id_to_vruntime[process.pid], process.pid)
        self.virtual_tree[key] = process

    def get_next_process(self) -> Process:
        """
        Retrieve and remove the process with the lowest virtual runtime.
        """
        ## Cleanup the existing scheduler ##
        self.cleanup()
        ## Cleanup the existing scheduler ##
        
        if not self.has_processes():
            raise Exception("No processes available")
        _, process = self.virtual_tree.popitem(0)
        return process

    def has_processes(self) -> bool:
        return len(self.virtual_tree) > 0
    
    def cleanup(self):
        for (vruntime, pid) in list(self.virtual_tree.keys()):
            process = Process.process_table.get(pid)
            if process is None or process.is_terminated():
                self.virtual_tree.pop((vruntime, pid), None)
                self.id_to_vruntime.pop(pid, None)

        for pid in list(self.id_to_vruntime.keys()):
            process = Process.process_table.get(pid)
            if process is None or process.is_terminated():
                self.id_to_vruntime.pop(pid, None)
    

