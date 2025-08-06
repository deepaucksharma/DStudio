---
title: Coding Interview Strategy & Tips
description: | Aspect | Coding Interviews | System Design Interviews | |--------|-------------------|--------------------------|
type: interview-guide
---

# Coding Interview Strategy & Tips

## Coding vs System Design Interviews

### Key Differences

| Aspect | Coding Interviews | System Design Interviews |
|--------|-------------------|--------------------------|
| **Time Pressure** | 30-45 minutes per problem | 45-60 minutes for full design |
| **Communication** | Code-focused, concise explanations | Architecture-focused, extensive discussion |
| **Evaluation** | Correctness, efficiency, clean code | Design decisions, trade-offs, scalability |
| **Mistakes** | Bugs are critical | Imperfect solutions acceptable if well-reasoned |
| **Preparation** | Pattern memorization + practice | Broad system knowledge + experience |

### Transitioning Between Modes
- **System design mindset**: "What are the trade-offs?"
- **Coding mindset**: "What's the most efficient solution?"
- **Integration**: Use coding skills to validate system design feasibility

---

## The REACTO Method

### R - Repeat
**Clarify the problem before coding**

```
"Let me make sure I understand:
- Input: Array of integers, target sum
- Output: Indices of two numbers that add to target
- Constraints: Exactly one solution exists
- Follow-up: Can I assume no duplicate indices?"
```

**Questions to Ask:**
- What are the input constraints? (size, range, edge cases)
- What should I return for invalid inputs?
- Are there time/space complexity requirements?
- Can I modify the input array?

### E - Examples
**Work through test cases**

```python
# Example walkthrough
arr = [2, 7, 11, 15], target = 9
# Expected output: [0, 1] because arr[0] + arr[1] = 2 + 7 = 9

# Edge cases to consider:
# - Empty array: []
# - Single element: [5]
# - No solution exists (if not guaranteed)
# - Negative numbers: [-1, -2, -3]
```

### A - Approach
**Explain your strategy before coding**

```
"I'll use a hash map approach:
1. Iterate through the array once
2. For each element, calculate complement = target - element
3. Check if complement exists in hash map
4. If yes, return indices; if no, add current element to map
5. Time: O(n), Space: O(n)"
```

### C - Code
**Write clean, readable code**

```python
def two_sum(nums, target):
    """
    Find indices of two numbers that add up to target.
    
    Args:
        nums: List of integers
        target: Target sum
    
    Returns:
        List[int]: Indices of the two numbers
    """
    num_to_index = {}
    
    for i, num in enumerate(nums):
        complement = target - num
        
        if complement in num_to_index:
            return [num_to_index[complement], i]
        
        num_to_index[num] = i
    
    # Problem guarantees solution exists
    return []
```

### T - Test
**Verify with examples**

```python
# Test with provided example
result = two_sum([2, 7, 11, 15], 9)
print(result)  # [0, 1] ✓

# Test edge case
result = two_sum([3, 3], 6)  
print(result)  # [0, 1] ✓
```

### O - Optimize
**Discuss improvements**

```
"Current solution is optimal for time complexity O(n).
Space optimization: If array can be modified and we only need 
to find if solution exists (not indices), we could sort first 
and use two pointers for O(1) space."
```

---

## Communication Best Practices

### Think Aloud Protocol
```
✅ Good: "I need to find two numbers that sum to target. 
         A brute force approach would be nested loops, 
         but that's O(n²). Let me think of a better way..."

❌ Bad: *Silent coding for 5 minutes*
```

### Explain Trade-offs
```
✅ Good: "Hash map gives us O(1) lookup but uses O(n) extra space.
         Two pointers on sorted array uses O(1) space but 
         requires O(n log n) sorting time."

❌ Bad: "This is the fastest way."
```

### Handle Uncertainty
```
✅ Good: "I'm not sure about this edge case. Let me think...
         Actually, let me code the main logic first and 
         come back to edge cases."

❌ Bad: *Gets stuck and stops talking*
```

### Debug Systematically
```
✅ Good: "Let me trace through with the example:
         i=0, num=2, complement=7, not in map, add 2→0
         i=1, num=7, complement=2, found at index 0, return [0,1]"

❌ Bad: "Hmm, this isn't working. Let me try something else."
```

---

## Common Mistakes & How to Avoid

### Mistake 1: Jumping to Code
**Problem**: Starting to code without understanding the problem
**Solution**: Always clarify requirements and work through examples first

```python
# ❌ Bad: Start coding immediately
def solution(arr):
    # Wait, what exactly am I solving?

# ✅ Good: Clarify first
"""
Problem: Find two indices where elements sum to target
Input: [2, 7, 11, 15], target = 9
Output: [0, 1]
Approach: Hash map for O(n) solution
"""
```

### Mistake 2: Poor Variable Names
```python
# ❌ Bad
def f(a, t):
    d = {}
    for i, x in enumerate(a):
        y = t - x
        if y in d:
            return [d[y], i]
        d[x] = i

# ✅ Good  
def two_sum(nums, target):
    num_to_index = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_to_index:
            return [num_to_index[complement], i]
        num_to_index[num] = i
```

### Mistake 3: Ignoring Edge Cases
```python
# ❌ Missing edge case handling
def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) / 2  # Integer overflow risk!
        # ... rest of logic

# ✅ Handle edge cases
def binary_search(arr, target):
    if not arr:  # Empty array
        return -1
    
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) / 2  # Avoid overflow
        # ... rest of logic
```

### Mistake 4: Not Testing Code
```python
# After writing solution, always test:
print(two_sum([2, 7, 11, 15], 9))     # [0, 1]
print(two_sum([3, 2, 4], 6))          # [1, 2]  
print(two_sum([3, 3], 6))             # [0, 1]
```

### Mistake 5: Overcomplicating Solutions
```python
# ❌ Overthinking
def is_palindrome(s):
    # Complex regex and multiple passes
    import re
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', s).lower()
    return cleaned == cleaned[::-1]

# ✅ Simple and clear
def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if not s[left].isalnum():
            left += 1
        elif not s[right].isalnum():
            right -= 1
        elif s[left].lower() != s[right].lower():
            return False
        else:
            left += 1
            right -= 1
    return True
```

---

## What Interviewers Look For

### Technical Skills (60%)
1. **Problem Solving**: Can you break down complex problems?
2. **Algorithm Knowledge**: Do you know common patterns?
3. **Code Quality**: Is your code clean and readable?
4. **Debugging**: Can you find and fix issues?
5. **Optimization**: Do you understand time/space trade-offs?

### Communication Skills (30%)
1. **Clarification**: Do you ask good questions?
2. **Explanation**: Can you explain your approach clearly?
3. **Collaboration**: Are you easy to work with?
4. **Adaptability**: Can you take hints and adjust?

### Attitude & Approach (10%)
1. **Persistence**: Do you push through challenges?
2. **Humility**: Do you admit when you don't know something?
3. **Growth Mindset**: Do you learn from feedback?

---

## Interview Timeline & Strategy

### Before the Interview (30 min)
- [ ] Review common patterns for the company
- [ ] Practice 2-3 problems similar to expected difficulty
- [ ] Set up environment (IDE, whiteboard, markers)
- [ ] Prepare clarifying questions template

### During the Interview

#### First 5 minutes
- Listen carefully to problem statement
- Ask clarifying questions
- Work through 1-2 examples
- Confirm understanding with interviewer

#### Next 10-15 minutes
- Explain approach at high level
- Discuss time/space complexity
- Get approval before coding
- Write clean, well-commented code

#### Next 10-15 minutes
- Test code with examples
- Debug any issues systematically
- Discuss optimizations
- Handle follow-up questions

#### Last 5 minutes
- Summarize solution and complexity
- Ask questions about the problem/company
- Thank interviewer

### Red Flags to Avoid
- ❌ Silent for more than 2 minutes
- ❌ Writing code without explaining approach
- ❌ Defensive about mistakes or suggestions
- ❌ Giving up when stuck
- ❌ Not testing the solution

### Green Flags to Demonstrate
- ✅ Clear communication throughout
- ✅ Systematic problem-solving approach
- ✅ Clean, readable code with good naming
- ✅ Proactive testing and debugging
- ✅ Open to feedback and collaboration

---

## Mock Interview Checklist

### Practice Setup
- [ ] Use unfamiliar problems
- [ ] Time yourself strictly
- [ ] Code on whiteboard or basic editor
- [ ] Practice explaining while coding
- [ ] Record yourself for review

### Self-Assessment Questions
1. Did I clarify the problem before coding?
2. Was my approach explanation clear?
3. Is my code readable and bug-free?
4. Did I test with multiple examples?
5. How was my communication throughout?

### Common Practice Mistakes
- Using IDE features (autocomplete, debugging)
- Looking up solutions when stuck
- Not timing yourself
- Practicing alone without feedback
- Only doing problems you're comfortable with

---

## Integration with System Design Skills

### Coding Skills That Help System Design
- **Algorithm analysis** → Performance estimation
- **Data structure knowledge** → Storage design decisions  
- **Optimization thinking** → Bottleneck identification
- **Edge case handling** → Failure mode analysis

### System Design Skills That Help Coding
- **Trade-off analysis** → Algorithm selection
- **Scalability thinking** → Efficient solution design
- **Component interaction** → Clean code architecture
- **Requirement clarification** → Better problem understanding

Use coding interviews as an opportunity to demonstrate systematic thinking and technical depth that will serve you well in system design and leadership roles.