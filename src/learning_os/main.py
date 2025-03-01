from learning_os.cpu import CPU
from learning_os.scheduler import (
    RoundRobinScheduler, 
    SimpleScheduler, 
    MultiLevelFeedbackQueueScheduler, 
    LotteryScheduler,
    CompletelyFairScheduler
)
from learning_os.process import Process
from learning_os.io_manager import IOManager

def main():
    scheduler = RoundRobinScheduler()
    scheduler = SimpleScheduler()
    scheduler = LotteryScheduler()
    scheduler = CompletelyFairScheduler()
    scheduler = MultiLevelFeedbackQueueScheduler()

    io_manager = IOManager()

    processes = [Process(arrival_time=0) for i in range(1, 6)]
    for process in processes:
        scheduler.add_process(process)
        print(f"Added process with PID {process.pid} to the scheduler and time to completion: {process.time_to_completion}")

    cpu = CPU(scheduler, io_manager)
    cpu.run()
    