import random

from learning_os.process import Process, ProcessState
from learning_os.scheduler import Scheduler

from typing import Dict

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