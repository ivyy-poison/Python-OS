from learning_os.scheduler.scheduler import Scheduler
from learning_os.process import Process, ProcessState
from learning_os.io_manager import IOManager

class CPU:
    """
    A class to represent a CPU in an operating system. It will run processes
    in a loop until there are no processes left.
    """
    global_clock = 0

    def __init__(self, scheduler: Scheduler, io_manager: IOManager) -> None:
        self.scheduler: Scheduler = scheduler
        self.io_manager: IOManager = io_manager
        
    @classmethod
    def increment_global_clock(cls, time: int) -> None:
        """
        Simulate the passage of time by incrementing the global clock.
        
        Args:
        time (int): The amount of time to increment the clock by.
        """
        CPU.global_clock += time

    @classmethod
    def get_current_time(self) -> int:
        """
        Get the current time of the simulation clock.
        
        Returns:
        int: The current time of the simulation clock.
        """
        return self.global_clock

    def run(self) -> None:
        """
        Run the processes in a loop until there are no processes left.
        """
        print("CPU starting...")

        while self.scheduler.has_processes() or self.io_manager.waiting_processes:

            for process in self.io_manager.update(self.get_current_time()):
                self.scheduler.add_process(process)

            if self.scheduler.has_processes():
                
                process: Process = self.scheduler.get_next_process()
                process.state = ProcessState.RUNNING
                time_to_run = self.scheduler.get_alloted_time(process)
                time_ran = process.run_for(time_to_run)
                print(f"{self.get_current_time()}: Process {process.pid} ran for {time_ran} time units.")
                self.increment_global_clock(time_ran)
                
                if process.is_in_io_state():
                    self.io_manager.add_waiting_process(process, self.get_current_time())
                    continue
                elif process.is_terminated():
                    continue

                process.state = ProcessState.READY
                self.scheduler.add_process(process)
                
   
            else:
                self.increment_global_clock(1)
                
        print("CPU has finished running all processes.")

