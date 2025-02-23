from cpu import CPU
from scheduler import RoundRobinScheduler, SimpleScheduler
from process import Process

if __name__ == "__main__":
    scheduler = RoundRobinScheduler(quantum=3)

    processes = [Process(arrival_time=0) for i in range(1, 6)]
    for process in processes:
        scheduler.add_process(process)

    cpu = CPU(scheduler)
    cpu.run()