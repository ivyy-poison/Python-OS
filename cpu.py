from scheduler import Scheduler
from process import Process

class CPU:
    """
    A class to represent a CPU in an operating system. It will run processes
    in a loop until there are no processes left.
    """

    def __init__(self, scheduler: Scheduler) -> None:
        self.scheduler: Scheduler = scheduler

    def run(self) -> None:
        """
        Run the processes in a loop until there are no processes left.
        """
        print("CPU starting...")
        order_of_processes = []

        while self.scheduler.has_processes():
            process: Process = self.scheduler.get_next_process()
            
            time_to_run = self.scheduler.get_alloted_time(process)
            time_ran = process.run_for(time_to_run)
            if not process.is_terminated():
                self.scheduler.add_process(process)
            order_of_processes.append(f"{process}:  {time_ran}")

        print("CPU has finished running all processes.")
        print(f"Order of processes run:")
        for process in order_of_processes:
            print(process)

