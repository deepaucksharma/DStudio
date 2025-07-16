Page 24: Work-Stealing Animation
Visual Step-Through of Work Stealing:
Step 1: Initial State (Uneven Distribution)
Worker 1: [████████████████] 16 tasks
Worker 2: [████] 4 tasks  
Worker 3: [██] 2 tasks
Worker 4: [ ] 0 tasks

Step 2: Worker 4 Steals from Worker 1
Worker 1: [████████] 8 tasks (stolen!)
Worker 2: [████] 4 tasks
Worker 3: [██] 2 tasks  
Worker 4: [████████] 8 tasks

Step 3: Worker 3 Steals from Worker 1
Worker 1: [████] 4 tasks
Worker 2: [████] 4 tasks
Worker 3: [██████] 6 tasks
Worker 4: [████████] 8 tasks

Step 4: Balanced State
Worker 1: [█████] 5 tasks
Worker 2: [█████] 5 tasks
Worker 3: [██████] 6 tasks
Worker 4: [██████] 6 tasks

Total time: 6 units (vs 16 without stealing)
Work Stealing Decision Logic:
WORKER LOOP:
1. Check local queue
   ├─ Has work? → Process it
   └─ Empty? → Continue to 2

2. Check steal candidates
   ├─ Find busiest worker
   ├─ Steal half their queue
   └─ No candidates? → Sleep briefly

3. Stealing strategy
   ├─ Steal from back (LIFO) for cache locality
   ├─ Steal in batches to reduce contention
   └─ Exponential backoff on conflict
Performance Comparison:
Scenario: 1000 tasks, varying sizes

No Stealing:          Work Stealing:
Worker 1: ████████    Worker 1: ████
Worker 2: ██          Worker 2: ████  
Worker 3: ████        Worker 3: ████
Worker 4: ██████      Worker 4: ████

Time: 800ms           Time: 400ms
Efficiency: 50%       Efficiency: 95%