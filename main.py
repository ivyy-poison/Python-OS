from cpu import CPU
from scheduler import RoundRobinScheduler, SimpleScheduler
from process import Process
from io_manager import IOManager

if __name__ == "__main__":
    scheduler = RoundRobinScheduler(quantum=3)
    # scheduler = SimpleScheduler()
    io_manager = IOManager()

    processes = [Process(arrival_time=0) for i in range(1, 6)]
    for process in processes:
        scheduler.add_process(process)
        print(f"Added process with PID {process.pid} to the scheduler and time to completion: {process.time_to_completion}")

    cpu = CPU(scheduler, io_manager)
    cpu.run()