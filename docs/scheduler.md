# Schedulers

## Overview
The scheduler is responsible for scheduling the next ready task to run. The choice of which task to run next is determined by the scheduling algorithm implemented by the scheduler.

My goal is to create a model for the scheduler that is easy to extend and modify. As such, I have created an abstract base class for the scheduler, which can be extended to explore different scheduling algorithms.

## Scheduler Interface

All schedulers in my existing OS model inherits from the `Scheduler` abstract base class, which defines the following methods:

- `get_alloted_time(process: Process) -> int`: This method returns the amount of time to allot to a process. The specific time quantum varies based on the scheduling algorithm and is used to let the CPU know the maximum time a process can run before having to yield. (We claim maximum because the process could possibly yield earlier due to an I/O operation).

- `add_process(process: Process) -> None`: This method adds a process to the scheduler. 

- `get_next_process() -> Process`: This method returns the next process to run. The selection of the next process is determined by the scheduling algorithm implemented by the scheduler.

- `has_processes() -> bool`: This method returns `True` if there are processes waiting to be scheduled, and `False` otherwise. It helps the CPU determine if there are any processes to execute.

## Types of Schedulers

1. **Round-Robin Scheduler**
    - **Description**: The Round-Robin scheduler assigns a fixed time quantum to each process in the queue. Processes are executed in a cyclic order, and if a process does not complete within its allotted time quantum, it is preempted and placed at the end of the queue.
    - **Use Case**: This scheduler is commonly used in time-sharing systems where fairness and responsiveness are important.
    - **Implementation**: In our implementation, the `RoundRobinScheduler` class maintains a queue of processes and assigns a fixed quantum to each process.

2. **Simple Scheduler**
    - **Description**: The Simple Scheduler runs processes to completion in the order they arrive. It does not preempt processes, meaning each process runs until it finishes before the next process starts.
    - **Use Case**: This scheduler is suitable for batch processing systems where processes are expected to run to completion without interruption.
    - **Implementation**: In our implementation, the `SimpleScheduler` class maintains a queue of processes and runs each process to completion based on its `time_to_completion`. The only difference between this and the `RoundRobinScheduler` is that the `SimpleScheduler` returns the `time_to_completion` of the process instead of a fixed quantum. 
        - However, this implementation isn't fully realistic as it is impossible to know the `time_to_completion` of a process in advance. 

3. **Multi-Level Feedback Queue (MLFQ) Scheduler**
    - **Description**: The MLFQ scheduler uses multiple queues with different priority levels. Processes start at the highest priority level and are demoted to lower levels if they use up their time quantum without completing or yielding control of the CPU. This allows the scheduler to prioritise short processes that do not hog the CPU over long-running processes.

    As described in OStep, measures have also been implemented to avoid allowing certain short-running process from "gaming the system" by repeatedly yielding control right before a time quantum expires. I implemented this by tracking the cumulative time a process has spent at each level. If a process has spent more than a certain threshold time at a level, it is demoted to the next lower level.

    In addition, to avoid starvation of long running process as a result of a repeated continuous addition of short running process that are preferrentially scheduled, I implemented a mechanism to periodically promote long running processes that have been waiting in the lower levels of the queue for a long time.

    - **Implementation**: In our implementation, the `MultiLevelFeedbackQueueScheduler` class maintains multiple queues and tracks the time each process spends at each level.

4. **Lottery Scheduler**
    - **Description**: The Lottery Scheduler assigns a number of tickets to each process. When selecting the next process to run, a lottery is held where the process with the winning ticket gets to run. The number of tickets a process has determines its chances of winning the lottery.
        - The idea here is that suppose we had a means of gauging priority of processes, we could theoretically assign more tickets to a particular process to increase its chances of winning the lottery. In the long run, the process with more tickets will get to run more often than processes with fewer tickets. 
        
    Note: _This feature has yet to be implemented as I am still exploring the best way to gauge priority of processes._

    - **Implementation**: In our implementation, the `LotteryScheduler` class maintains a mapping of processes currently scheduled to their ticket counts and performs a lottery draw to select the next process.

5. **Completely Fair Scheduler (CFS)**
    - **Description**: The CFS aims to allocate CPU time fairly among processes by maintaining a virtual runtime for each process. Processes with lower virtual runtimes are given higher priority. The scheduler ensures that no process lags too far behind by adjusting the virtual runtime based on the actual runtime.

    - In addition, as described in OStep, the CFS also implements a mechanism to prevent starvation of processes by ensuring that no process is allowed to run for too long without yielding control of the CPU to others. This is done by adjusting the virtual runtime of processes that have not been running for an extended period, possibly due to a longrunning I/O operation by setting the virtual runtime of the process to `max(process.cumulative_time_run, min(vruntime for all processes))`

    - **Challenge**: 

        - Use of `SortedDict` from the `sortedcontainers` library to maintain a sorted order of processes based on their virtual runtimes means that I have to store keys as (vruntime, pid) tuples. This is because the `SortedDict` does not allow duplicate keys, and since multiple processes can have the same virtual runtime. This would probably solved if I implement my own version of a self-balancing tree (eg: Red-Black tree).

    - **Implementation**: In our implementation, the `CompletelyFairScheduler` class uses a sorted dictionary to manage processes based on their virtual runtime.

## Miscellaneous

### Designing preemption
 **Preemption**: Preemption is the act of interrupting a currently running process to allow another process to run. In the context of scheduling, preemption occurs when a process exceeds its time quantum or when a higher-priority process becomes ready to run.

I believe that the existing design of the scheduler is sufficient to handle preemption. The `get_next_process` method of the scheduler is responsible for selecting the next process to run, and it can take into account the time quantum and priority of processes. Presumably, a future component responsible for receiving new processes and managing the CPU can simply add both the new process and the currently running process to the scheduler, and then call `get_next_process` to select the next process to run.
