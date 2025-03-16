from python_os.process import Process
from python_os.scheduler import Scheduler

from sortedcontainers import SortedDict
from typing import Dict, Tuple

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

        self.virtual_tree: Dict[Tuple[int, int], Process] = SortedDict()
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
        
        key = (self.id_to_vruntime[process.pid], process.pid)
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