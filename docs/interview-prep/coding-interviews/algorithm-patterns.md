# Common Algorithm Patterns

This reference covers the most frequently tested algorithmic patterns in coding interviews.

## Array & String Patterns

### Two Pointers
**Use when**: Array/string problems involving pairs, reversals, or partitioning.

#### Template
```python
def two_pointers(arr):
    left, right = 0, len(arr) - 1
    
    while left < right:
        # Process current pair
        if condition:
            # Move pointers based on condition
            left += 1
        else:
            right -= 1
    
    return result
```

#### Common Problems
- **Two Sum (sorted array)** - Find pair with target sum
- **Palindrome check** - Verify if string reads same forwards/backwards  
- **Container with most water** - Find maximum area between two lines
- **3Sum** - Find triplets that sum to zero

---

### Sliding Window
**Use when**: Subarray/substring problems with contiguous elements.

#### Template (Fixed Size)
```python
def sliding_window_fixed(arr, k):
    window_sum = sum(arr[:k])
    max_sum = window_sum
    
    for i in range(k, len(arr)):
        window_sum = window_sum - arr[i-k] + arr[i]
        max_sum = max(max_sum, window_sum)
    
    return max_sum
```

#### Template (Variable Size)
```python
def sliding_window_variable(arr, condition):
    left = 0
    result = 0
    
    for right in range(len(arr)):
        # Expand window
        # Update window state
        
        while window_invalid():
            # Shrink window
            left += 1
        
        # Update result
        result = max(result, right - left + 1)
    
    return result
```

#### Common Problems
- **Maximum sum subarray of size K** - Fixed window
- **Longest substring without repeating characters** - Variable window
- **Minimum window substring** - Variable window with character frequency
- **Permutation in string** - Fixed window with character matching

---

### Prefix Sum
**Use when**: Range sum queries or subarray sum problems.

#### Template
```python
def prefix_sum(arr):
    prefix = [0]
    for num in arr:
        prefix.append(prefix[-1] + num)
    
    # Range sum from i to j (inclusive)
    def range_sum(i, j):
        return prefix[j+1] - prefix[i]
    
    return range_sum
```

#### Common Problems
- **Subarray sum equals K** - Hash map + prefix sum
- **Range sum query** - Direct prefix sum application
- **Continuous subarray sum** - Modular arithmetic with prefix sum

---

## Tree & Graph Patterns

### Tree Traversal (DFS)
**Use when**: Processing tree nodes with different visit orders.

#### Templates
```python
# Preorder (Root → Left → Right)
def preorder(root):
    if not root:
        return []
    
    result = [root.val]
    result.extend(preorder(root.left))
    result.extend(preorder(root.right))
    return result

# Inorder (Left → Root → Right) 
def inorder(root):
    if not root:
        return []
    
    result = inorder(root.left)
    result.append(root.val)
    result.extend(inorder(root.right))
    return result

# Postorder (Left → Right → Root)
def postorder(root):
    if not root:
        return []
    
    result = postorder(root.left)
    result.extend(postorder(root.right))
    result.append(root.val)
    return result
```

#### Common Problems
- **Binary tree paths** - Preorder with path tracking
- **Validate BST** - Inorder with sorted check
- **Tree diameter** - Postorder with height calculation

---

### Tree Traversal (BFS)
**Use when**: Level-order processing or shortest path in trees.

#### Template
```python
from collections import deque

def level_order(root):
    if not root:
        return []
    
    result = []
    queue = deque([root])
    
    while queue:
        level_size = len(queue)
        level = []
        
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        result.append(level)
    
    return result
```

#### Common Problems
- **Binary tree level order traversal** - Standard BFS
- **Binary tree right side view** - BFS with rightmost node per level
- **Minimum depth of binary tree** - BFS early termination

---

### Graph DFS
**Use when**: Path finding, cycle detection, or connected components.

#### Template
```python
def dfs_recursive(graph, start, visited=None):
    if visited is None:
        visited = set()
    
    visited.add(start)
    result = [start]
    
    for neighbor in graph[start]:
        if neighbor not in visited:
            result.extend(dfs_recursive(graph, neighbor, visited))
    
    return result

def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    result = []
    
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            result.append(node)
            
            # Add neighbors in reverse order for consistent traversal
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return result
```

#### Common Problems
- **Number of islands** - DFS on 2D grid
- **Course schedule** - Cycle detection in directed graph
- **Clone graph** - DFS with node cloning

---

### Graph BFS
**Use when**: Shortest path or minimum steps problems.

#### Template
```python
from collections import deque

def bfs(graph, start):
    visited = set([start])
    queue = deque([start])
    result = []
    
    while queue:
        node = queue.popleft()
        result.append(node)
        
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return result

def bfs_shortest_path(graph, start, target):
    if start == target:
        return 0
    
    visited = set([start])
    queue = deque([(start, 0)])
    
    while queue:
        node, distance = queue.popleft()
        
        for neighbor in graph[node]:
            if neighbor == target:
                return distance + 1
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))
    
    return -1  # No path found
```

#### Common Problems
- **Word ladder** - BFS for minimum transformations
- **Rotting oranges** - Multi-source BFS on 2D grid
- **Shortest path in binary matrix** - BFS with obstacle avoidance

---

## Dynamic Programming Patterns

### 1D DP
**Use when**: Optimal substructure with single parameter.

#### Template
```python
def dp_1d(arr):
    n = len(arr)
    dp = [0] * n
    
    # Base case
    dp[0] = arr[0]
    
    # Fill dp table
    for i in range(1, n):
        dp[i] = max(dp[i-1], arr[i])  # Example recurrence
    
    return dp[n-1]
```

#### Common Problems
- **Climbing stairs** - Fibonacci sequence
- **House robber** - Max non-adjacent sum
- **Maximum subarray** - Kadane's algorithm
- **Coin change** - Minimum coins for amount

---

### 2D DP
**Use when**: Optimal substructure with two parameters.

#### Template
```python
def dp_2d(grid):
    m, n = len(grid), len(grid[0])
    dp = [[0] * n for _ in range(m)]
    
    # Base cases
    dp[0][0] = grid[0][0]
    
    # Fill first row and column
    for i in range(1, m):
        dp[i][0] = dp[i-1][0] + grid[i][0]
    for j in range(1, n):
        dp[0][j] = dp[0][j-1] + grid[0][j]
    
    # Fill dp table
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = min(dp[i-1][j], dp[i][j-1]) + grid[i][j]
    
    return dp[m-1][n-1]
```

#### Common Problems
- **Unique paths** - Grid path counting
- **Minimum path sum** - Grid with minimum cost
- **Edit distance** - String transformation cost
- **Longest common subsequence** - String matching

---

## Searching & Sorting Patterns

### Binary Search
**Use when**: Searching in sorted space or finding boundaries.

#### Template (Exact Match)
```python
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1
```

#### Template (Find Boundary)
```python
def find_first_occurrence(arr, target):
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            result = mid
            right = mid - 1  # Continue searching left
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result
```

#### Common Problems
- **Search in rotated sorted array** - Modified binary search
- **Find peak element** - Binary search on unsorted array
- **Sqrt(x)** - Binary search on answer space
- **Kth smallest element** - Binary search with counting

---

## Backtracking Pattern

**Use when**: Exploring all possible solutions with pruning.

#### Template
```python
def backtrack(candidates, path, result, start=0):
    # Base case - found valid solution
    if is_valid_solution(path):
        result.append(path[:])  # Make copy
        return
    
    # Try each candidate
    for i in range(start, len(candidates)):
        candidate = candidates[i]
        
        # Skip invalid candidates
        if not is_valid_candidate(candidate, path):
            continue
        
        # Make choice
        path.append(candidate)
        
        # Recurse
        backtrack(candidates, path, result, i + 1)
        
        # Undo choice
        path.pop()
```

#### Common Problems
- **Subsets** - Generate all possible subsets
- **Permutations** - Generate all arrangements
- **N-Queens** - Place queens without attacking
- **Sudoku solver** - Fill valid numbers in grid

---

## Complexity Quick Reference

### Time Complexities by Pattern
| Pattern | Typical Complexity | Example |
|---------|-------------------|---------|
| Two Pointers | O(n) | Two Sum II |
| Sliding Window | O(n) | Longest Substring |
| Binary Search | O(log n) | Search Insert Position |
| Tree DFS | O(n) | Binary Tree Paths |
| Tree BFS | O(n) | Level Order Traversal |
| Graph DFS/BFS | O(V + E) | Number of Islands |
| 1D DP | O(n) | Climbing Stairs |
| 2D DP | O(m × n) | Unique Paths |
| Backtracking | O(2ⁿ) | Subsets |

### Space Complexities
- **In-place algorithms**: O(1) extra space
- **Single array/string**: O(n) space
- **2D problems**: O(m × n) space  
- **Recursive calls**: O(depth) call stack space
- **Memoization**: O(state space) for cache

---

## Pattern Recognition Guide

| Problem Keywords | Likely Pattern |
|------------------|----------------|
| "Two elements", "pair" | Two Pointers |
| "Subarray", "substring" | Sliding Window |
| "Range sum", "prefix" | Prefix Sum |
| "Tree traversal" | DFS/BFS |
| "Shortest path", "minimum steps" | BFS |
| "All paths", "combinations" | DFS/Backtracking |
| "Optimal solution", "minimum/maximum" | Dynamic Programming |
| "Sorted array", "search" | Binary Search |
| "Generate all", "permutations" | Backtracking |

Use this guide to quickly identify the appropriate pattern for each problem during interviews.