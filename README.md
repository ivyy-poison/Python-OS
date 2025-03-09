# learning-os
bro claims he wants to learn about os but programs in python 

## Reason for doing this
This is my second time going through OStep, yet I can't quite seem to get my fundamentals down. Must be reason for unemployability. booboo. Will add design decisions in the future once I get a formal idea of how to model this and how far I wish to go.

Todo:
- ~~Implement I/O simulation~~
- ~~Implement MLFQ Scheduler~~
- ~~Implement Lottery scheduler~~
- ~~Implement Completely Fair Scheduler (CFS)~~
  - Potentially implement own red-black tree
  - Potentially incorporate priority
- ~~Implement basic File System~~
  - Separate out file system and storage manager class, for potentially exploring RAID, SSD, disk, WAL, etc.
- Build extensible design for IOManager, then potentially expand into memory and disk management simulations
- Further away type of goals include: Simulating memory management and file systems (If I even get that far)
- Improve logging for monitoring of various components
  - Note: Stretch goals because I presently have no intentions of incorporating external dependencies into this model yet.
  - But ideally I wish to be able to isolate logging not only by levels but by components as well.
