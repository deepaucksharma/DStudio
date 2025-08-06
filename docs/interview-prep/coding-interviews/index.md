---
title: Coding Interviews
description: Coding Interviews overview and navigation
---

# Coding Interview Quick Reference

!!! note "Lightweight Guide"
    This is a focused reference guide. For comprehensive coding prep, we recommend dedicated platforms like LeetCode, HackerRank, or Cracking the Coding Interview.

## Overview

While this site focuses on **distributed systems** and **engineering leadership**, coding interviews remain a gatekeeper for many tech roles. This section provides:

- **Quick reference** for common algorithmic patterns
- **External resource** recommendations
- **Interview strategy** specific to coding challenges
- **Time/space complexity** cheat sheets

## When You Need This

- **System design-focused** candidates who need coding interview refreshers
- **Senior engineers** who haven't coded algorithms recently
- **Leadership track** candidates facing coding rounds
- **Quick review** before technical screens

## Learning Path

| Phase | Focus | Resources |
|-------|-------|-----------|
| **Foundation** | Data structures & core algorithms | [Algorithm Patterns](../interview-prep/coding-interviews/algorithm-patterns.md) |
| **Practice** | Pattern recognition & implementation | External platforms |
| **Strategy** | Interview communication & debugging | [Interview Tips](../interview-prep/coding-interviews/interview-tips.md) |

## External Resources

### Primary Platforms
- **[LeetCode](https://leetcode.com/index.md)** - Industry standard with company-specific questions
- **[NeetCode](https://neetcode.io/index.md)** - Curated problem lists with video explanations
- **[AlgoExpert](https://www.algoexpert.io/index.md)** - Structured curriculum with detailed explanations
- **[Educative](https://www.educative.io/courses/grokking-the-coding-interview/index.md)** - Pattern-based learning approach

### Books & References
- **Cracking the Coding Interview** by Gayle McDowell
- **Elements of Programming Interviews** by Aziz, Lee, Prakash
- **Algorithm Design Manual** by Steven Skiena

### Company-Specific Prep
- **[Blind 75](https://www.teamblind.com/post/New-Year-Gift---Curated-List-of-Top-75-LeetCode-Questions-to-Save-Your-Time-wR0fSmqQ/index.md)** - Essential problems for FAANG interviews
- **[Grind 75](https://www.techinterviewhandbook.org/grind75/index.md)** - Structured 75-problem curriculum

## Core Competencies

### Data Structures (Must Know)
- Arrays & Strings
- Hash Tables/Maps
- Linked Lists
- Stacks & Queues
- Trees (Binary, BST, Balanced)
- Heaps/Priority Queues
- Graphs (Adjacency List/Matrix)

### Algorithms (Must Know)
- Two Pointers
- Sliding Window
- Binary Search
- Tree Traversals (DFS/BFS)
- Dynamic Programming (1D/2D)
- Sorting & Searching
- Graph Algorithms (DFS/BFS, Union-Find)

### Advanced Topics (Nice to Have)
- Trie
- Segment Trees
- Topological Sort
- Advanced DP (Interval, Bitmask)
- String Algorithms (KMP, Rolling Hash)

## Complexity Cheat Sheet

### Time Complexity Hierarchy
```
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2ⁿ) < O(n!)
```

### Common Operations
| Data Structure | Access | Search | Insert | Delete |
|----------------|--------|--------|--------|--------|
| Array | O(1) | O(n) | O(n) | O(n) |
| Hash Table | O(1) | O(1) | O(1) | O(1) |
| Binary Search Tree | O(log n) | O(log n) | O(log n) | O(log n) |
| Binary Heap | O(1) | O(n) | O(log n) | O(log n) |

### Algorithm Complexities
| Algorithm | Best | Average | Worst | Space |
|-----------|------|---------|-------|-------|
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) |
| Binary Search | O(1) | O(log n) | O(log n) | O(1) |
| DFS/BFS | O(V + E) | O(V + E) | O(V + E) | O(V) |

## Interview Timeline

### 1-2 Weeks Before
- [ ] Review algorithm patterns
- [ ] Practice 2-3 problems daily
- [ ] Time yourself on easy/medium problems
- [ ] Review data structure implementations

### 1 Week Before
- [ ] Focus on weak areas
- [ ] Practice with whiteboard/no IDE
- [ ] Review complexity analysis
- [ ] Mock interview with friends

### Day Before
- [ ] Light review of patterns
- [ ] Get good sleep
- [ ] Prepare questions for interviewer
- [ ] Set up interview environment

## Success Metrics

- **Easy problems**: Solve in 10-15 minutes
- **Medium problems**: Solve in 20-30 minutes  
- **Pattern recognition**: Identify approach within 2-3 minutes
- **Bug-free code**: First submission works 80% of the time
- **Clean communication**: Explain approach clearly while coding

## Next Steps

1. **Start with patterns**: Review [Algorithm Patterns](../interview-prep/coding-interviews/algorithm-patterns.md)
2. **Practice regularly**: 30-60 minutes daily on external platforms
3. **Focus on communication**: Practice [Interview Tips](../interview-prep/coding-interviews/interview-tips.md)
4. **System design integration**: Connect coding skills to architecture decisions

---

!!! tip "Integration with System Design"
    Strong coding skills enhance system design interviews by demonstrating implementation feasibility and technical depth. Use coding patterns to validate architectural decisions.