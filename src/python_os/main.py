from python_os.cpu import CPU
from python_os.scheduler import (
    RoundRobinScheduler, 
    SimpleScheduler, 
    MultiLevelFeedbackQueueScheduler, 
    LotteryScheduler,
    CompletelyFairScheduler
)
from python_os.process import Process
from python_os.io_manager import IOManager
from python_os.file_system import BasicFileSystem

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

def main():
    fs = BasicFileSystem("storage.json")
    fs.create_directory("/dir1")
    fs.create_directory("/dir1/dir2")
    fs.create_directory("/dir2")
    fs.create_file("/dir1/file1.txt")
    fs.create_file("/file2.txt")
    fs.write_file("/dir1/file1.txt", "abcdefghijklmnopqrstuvwxyz")
    fs.read_file("/dir1/file1.txt", 2, 10)
    fs.list_directory("/dir1")
    # fs.delete_file("/dir1/file1.txt")
    # fs.delete_file("/dir1/file1.txt")
    # fs.delete_directory("/dir2")
    # fs.delete_directory("/dir1")
    