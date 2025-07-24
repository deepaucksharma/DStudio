#!/usr/bin/env python3
"""
Add structured exercises to files that are missing them
"""

import os
import re
from pathlib import Path
import json

class ExerciseAdder:
    def __init__(self, base_dir="."):
        self.base_dir = Path(base_dir)
        self.docs_dir = self.base_dir / "docs"
        self.exercises_added = 0
        self.files_modified = 0
        
        # Exercise templates by content type
        self.exercise_templates = {
            'axiom': self.get_axiom_exercises,
            'pattern': self.get_pattern_exercises,
            'quantitative': self.get_quantitative_exercises,
            'case-study': self.get_case_study_exercises,
            'human-factors': self.get_human_factors_exercises,
            'general': self.get_general_exercises
        }
    
    def get_content_type(self, file_path):
        """Determine content type from file path"""
        path_str = str(file_path).lower()
        
        if 'axiom' in path_str and 'index.md' in path_str:
            return 'axiom'
        elif 'patterns' in path_str and not 'index.md' in path_str:
            return 'pattern'
        elif 'quantitative' in path_str:
            return 'quantitative'
        elif 'case-studies' in path_str:
            return 'case-study'
        elif 'human-factors' in path_str:
            return 'human-factors'
        else:
            return 'general'
    
    def extract_title(self, content):
        """Extract title from content"""
        # Try frontmatter first
        fm_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', content, re.MULTILINE)
        if fm_match:
            return fm_match.group(1)
        
        # Try first H1
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1)
            
        return "Unknown Topic"
    
    def get_axiom_exercises(self, file_path, content):
        """Generate exercises for axiom files"""
        title = self.extract_title(content)
        axiom_name = title.replace('Axiom', '').strip()
        
        exercises = f"""
---

## 💪 Exercises & Application

### Exercise 1: Real-World Analysis ⭐⭐
**Time**: ~15 minutes  
**Objective**: Identify how {axiom_name} manifests in systems you know

**Task**: 
1. Think of 3 software systems you use daily (web apps, mobile apps, games)
2. For each system, identify one way {axiom_name} affects the user experience
3. Describe what happens when this constraint is violated

**Example Framework**:
- **System**: Netflix video streaming
- **Constraint**: [Describe how {axiom_name} applies]
- **User Impact**: [What users experience when constraint is hit]
- **Mitigation**: [How the system handles it]

### Exercise 2: Design Challenge ⭐⭐⭐
**Time**: ~25 minutes  
**Objective**: Apply {axiom_name} principles to system design

**Scenario**: You're designing a real-time chat application that needs to support 1 million concurrent users.

**Task**:
1. Identify 3 specific ways {axiom_name} will impact your design
2. For each impact, propose a concrete solution
3. Explain the trade-offs of your solutions

**Consider**:
- Message delivery requirements
- User experience expectations
- System resource constraints
- Scalability requirements

### Exercise 3: Failure Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes  
**Objective**: Debug real-world system issues using {axiom_name}

**Case Study**: A social media platform experiences performance degradation during peak hours.

**Your Analysis**:
1. **Hypothesis**: How might {axiom_name} be involved in this issue?
2. **Investigation**: What metrics would you examine first?
3. **Root Cause**: Propose 2-3 possible root causes related to this axiom
4. **Solutions**: Design both immediate fixes and long-term improvements

**Deliverable**: A 3-paragraph incident analysis report

---

## 🧠 Quick Knowledge Check

**Question 1**: What makes {axiom_name} a fundamental constraint rather than just a design consideration?

**Question 2**: Give an example of a system that appears to "violate" this axiom and explain how it actually confirms it.

**Question 3**: How does {axiom_name} interact with the other fundamental laws?

---

## 🔗 Apply Your Learning

**Mini-Project**: Choose one of these applications:
1. **For Developers**: Implement a simple system that demonstrates this axiom's effects
2. **For Architects**: Design a service that optimally handles this constraint  
3. **For Operators**: Create monitoring that detects when this constraint is being violated

**Time Investment**: 1-2 hours
**Share**: Post your results and learnings to build understanding

---
"""
        return exercises
    
    def get_pattern_exercises(self, file_path, content):
        """Generate exercises for pattern files"""
        title = self.extract_title(content)
        pattern_name = title.replace('Pattern', '').strip()
        
        exercises = f"""
---

## 💪 Hands-On Exercises

### Exercise 1: Pattern Recognition ⭐⭐
**Time**: ~15 minutes  
**Objective**: Identify {pattern_name} in existing systems

**Task**: 
Find 2 real-world examples where {pattern_name} is implemented:
1. **Example 1**: A well-known tech company or service
2. **Example 2**: An open-source project or tool you've used

For each example:
- Describe how the pattern is implemented
- What problems it solves in that context
- What alternatives could have been used

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes  
**Objective**: Design an implementation of {pattern_name}

**Scenario**: You need to implement {pattern_name} for an e-commerce checkout system processing 10,000 orders/hour.

**Requirements**:
- 99.9% availability required
- Payment processing must be reliable
- Orders must not be lost or duplicated

**Your Task**:
1. Design the architecture using {pattern_name}
2. Identify key components and their responsibilities
3. Define interfaces between components
4. Consider failure scenarios and mitigation strategies

**Deliverable**: Architecture diagram + 1-page implementation plan

### Exercise 3: Trade-off Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes  
**Objective**: Evaluate when NOT to use {pattern_name}

**Challenge**: You're consulting for a startup building their first product.

**Analysis Required**:
1. **Context Assessment**: Under what conditions would {pattern_name} be overkill?
2. **Cost-Benefit**: Compare implementation costs vs. benefits
3. **Alternatives**: What simpler approaches could work initially?
4. **Evolution Path**: How would you migrate to {pattern_name} later?

**Anti-Pattern Warning**: Identify one common mistake teams make when implementing this pattern.

---

## 🛠️ Code Challenge

### Beginner: Basic Implementation
Implement a minimal version of {pattern_name} in your preferred language.
- Focus on core functionality
- Include basic error handling
- Add simple logging

### Intermediate: Production Features  
Extend the basic implementation with:
- Configuration management
- Metrics collection
- Unit tests
- Documentation

### Advanced: Performance & Scale
Optimize for production use:
- Handle concurrent access
- Implement backpressure
- Add monitoring hooks
- Performance benchmarks

---

## 🎯 Real-World Application

**Project Integration**: 
- How would you introduce {pattern_name} to an existing system?
- What migration strategy would minimize risk?
- How would you measure success?

**Team Discussion Points**:
1. When team members suggest this pattern, what questions should you ask?
2. How would you explain the value to non-technical stakeholders?
3. What monitoring would indicate the pattern is working well?

---
"""
        return exercises
    
    def get_quantitative_exercises(self, file_path, content):
        """Generate exercises for quantitative content"""
        title = self.extract_title(content)
        
        exercises = f"""
---

## 📊 Practical Calculations

### Exercise 1: Basic Application ⭐⭐
**Time**: ~15 minutes  
**Objective**: Apply the concepts to a simple scenario

**Scenario**: A web API receives 1,000 requests per second with an average response time of 50ms.

**Calculate**:
1. Apply the concepts from {title} to this scenario
2. What happens if response time increases to 200ms?
3. What if request rate doubles to 2,000 RPS?

**Show your work** and explain the practical implications.

### Exercise 2: System Design Math ⭐⭐⭐
**Time**: ~25 minutes  
**Objective**: Use quantitative analysis for design decisions

**Problem**: Design capacity for a new service with these requirements:
- Peak load: 50,000 RPS
- 99th percentile latency < 100ms
- 99.9% availability target

**Your Analysis**:
1. Calculate the capacity needed using the principles from {title}
2. Determine how many servers/instances you need
3. Plan for growth and failure scenarios
4. Estimate costs and resource requirements

### Exercise 3: Performance Debugging ⭐⭐⭐⭐
**Time**: ~20 minutes  
**Objective**: Use quantitative methods to diagnose issues

**Case**: Production metrics show:
- Response times increasing over the last week
- Error rate climbing from 0.1% to 2%
- User complaints about slow performance

**Investigation**:
1. What quantitative analysis would you perform first?
2. Apply the concepts to identify potential bottlenecks
3. Calculate the impact of proposed solutions
4. Prioritize fixes based on mathematical impact

---

## 🧮 Mathematical Deep Dive

### Problem Set A: Fundamentals
Work through these step-by-step:

1. **Basic Calculation**: [Specific problem related to the topic]
2. **Real-World Application**: [Industry scenario requiring calculation]
3. **Optimization**: [Finding the optimal point or configuration]

### Problem Set B: Advanced Analysis
For those wanting more challenge:

1. **Multi-Variable Analysis**: [Complex scenario with multiple factors]
2. **Sensitivity Analysis**: [How changes in inputs affect outputs]
3. **Modeling Exercise**: [Build a mathematical model]

---

## 📈 Monitoring & Measurement

**Practical Setup**:
1. What metrics would you collect to validate these calculations?
2. How would you set up alerting based on the thresholds?
3. Create a dashboard to track the key indicators

**Continuous Improvement**:
- How would you use data to refine your calculations?
- What experiments would validate your mathematical models?
- How would you communicate findings to stakeholders?

---
"""
        return exercises
    
    def get_case_study_exercises(self, file_path, content):
        """Generate exercises for case study content"""
        title = self.extract_title(content)
        
        exercises = f"""
---

## 🔍 Case Study Analysis

### Exercise 1: Deep Dive Analysis ⭐⭐
**Time**: ~20 minutes  
**Objective**: Extract key learnings from {title}

**Analysis Framework**:
1. **Problem Statement**: What core challenge was being solved?
2. **Solution Approach**: What was unique about their solution?
3. **Technical Details**: What specific technologies/patterns were used?
4. **Results & Impact**: What were the measurable outcomes?

**Critical Thinking**:
- What assumptions did they make?
- What trade-offs did they accept?
- How might this approach fail?

### Exercise 2: Alternative Solutions ⭐⭐⭐
**Time**: ~25 minutes  
**Objective**: Explore different approaches to the same problem

**Challenge**: Solve the same problem with different constraints:

**Scenario A: Startup Constraints**
- Limited budget (< $10K/month)
- Small team (2-3 engineers)
- MVP timeline (3 months)

**Scenario B: Enterprise Constraints**  
- High compliance requirements
- Integration with legacy systems
- 99.99% availability needed

**Your Task**:
For each scenario, design an alternative solution and compare:
- Technical approach differences
- Resource requirements
- Risk factors
- Implementation timeline

### Exercise 3: Future Evolution ⭐⭐⭐⭐
**Time**: ~20 minutes  
**Objective**: Predict how this solution might evolve

**Trend Analysis**:
1. **Technology Evolution**: How might new technologies change this approach?
2. **Scale Challenges**: What would break if load increased 100x?
3. **Business Evolution**: How would changing business requirements affect the solution?

**Your Prediction**:
- What would this system look like in 5 years?
- What parts would need complete redesign?
- What principles would remain constant?

---

## 🛠️ Implementation Challenge

### Miniature Version
**Goal**: Build a simplified version that demonstrates the core concepts

**Requirements**:
- 1/1000th the scale of the original
- Same fundamental architecture
- Focus on the innovative aspects

**Deliverables**:
- Working prototype
- Documentation explaining the parallels
- Performance measurements

### Architecture Review
**Peer Learning**: Present your mini-implementation to others and:
- Explain design decisions
- Discuss trade-offs made
- Get feedback on approach
- Identify improvement opportunities

---

## 🎯 Application to Your Context

**Personal Reflection**:
1. **Current Projects**: Where could you apply insights from this case study?
2. **Team Discussions**: What aspects would be most valuable to share with your team?
3. **Technology Choices**: How does this influence your technology evaluation criteria?

**Action Items**:
- One thing you'll investigate further
- One practice you'll adopt in your next project
- One assumption you'll question in your current work

---
"""
        return exercises
    
    def get_human_factors_exercises(self, file_path, content):
        """Generate exercises for human factors content"""
        title = self.extract_title(content)
        
        exercises = f"""
---

## 👥 Practical Application

### Exercise 1: Current State Assessment ⭐⭐
**Time**: ~15 minutes  
**Objective**: Evaluate your team's current practices related to {title}

**Self-Assessment**:
1. **Current Practice**: How does your team currently handle this area?
2. **Effectiveness**: What works well? What causes friction?
3. **Gaps**: Where do you see the biggest improvement opportunities?
4. **Cultural Fit**: How well would the practices from {title} fit your organization?

**Scoring**: Rate each area 1-5 and identify the top 2 areas for improvement.

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes  
**Objective**: Create an actionable improvement plan

**Planning Framework**:
1. **Quick Wins** (< 1 month): What could you implement immediately?
2. **Medium-term Changes** (1-3 months): What requires some process changes?
3. **Cultural Shifts** (3-6 months): What needs sustained effort to change?

**For each timeframe**:
- Specific actions to take
- Success metrics
- Potential obstacles
- Required resources/support

### Exercise 3: Simulation Exercise ⭐⭐⭐⭐
**Time**: ~30 minutes  
**Objective**: Practice the concepts in a realistic scenario

**Scenario**: Your team just experienced a significant production incident related to {title}.

**Role-Play Elements**:
- You're leading the response/improvement effort
- Team members have different experience levels
- There's pressure to prevent recurrence quickly
- Budget and time constraints exist

**Your Response**:
1. **Immediate Actions**: What would you do in the first 24 hours?
2. **Investigation Process**: How would you analyze what went wrong?
3. **Improvement Plan**: What systematic changes would you implement?
4. **Communication**: How would you keep stakeholders informed?

---

## 🔄 Process Development

### Team Workshop Design
**Goal**: Create a workshop to share these concepts with your team

**Workshop Structure** (90 minutes):
- **Opening** (15 min): Why this matters
- **Current State** (20 min): Team assessment
- **Concepts** (30 min): Key principles from {title}
- **Application** (20 min): How to apply in your context
- **Action Planning** (5 min): Next steps

**Facilitation Tips**:
- Keep it interactive and practical
- Use real examples from your team's experience
- Focus on actionable outcomes

### Measurement & Iteration
**Success Metrics**:
- How will you measure improvement in this area?
- What leading indicators will show progress?
- How often will you review and adjust?

**Continuous Learning**:
- What experiments will you run?
- How will you gather feedback?
- What would success look like in 6 months?

---

## 🎯 Leadership Application

**For Individual Contributors**:
- How can you influence positive change without formal authority?
- What skills from {title} would make you more effective?
- How can you support team improvement efforts?

**For Team Leads**:
- What cultural changes would have the biggest impact?
- How do you balance individual and team needs?
- What systems would sustain these practices long-term?

**For Organizations**:
- How do these practices scale across multiple teams?
- What policies or standards would support adoption?
- How do you measure ROI on human factors improvements?

---
"""
        return exercises
    
    def get_general_exercises(self, file_path, content):
        """Generate generic exercises for other content types"""
        title = self.extract_title(content)
        
        exercises = f"""
---

## 💡 Knowledge Application

### Exercise 1: Concept Exploration ⭐⭐
**Time**: ~15 minutes  
**Objective**: Deepen understanding of {title}

**Reflection Questions**:
1. What are the 3 most important concepts from this content?
2. How do these concepts relate to systems you work with?
3. What examples from your experience illustrate these ideas?
4. What questions do you still have?

**Application**: Choose one concept and explain it to someone else in your own words.

### Exercise 2: Real-World Connection ⭐⭐⭐
**Time**: ~20 minutes  
**Objective**: Connect theory to practice

**Research Task**:
1. Find 2 real-world examples where these concepts apply
2. Analyze how the concepts manifest in each example
3. Identify what would happen if these principles were ignored

**Examples could be**:
- Open source projects
- Well-known tech companies
- Systems you use daily
- Historical technology decisions

### Exercise 3: Critical Thinking ⭐⭐⭐⭐
**Time**: ~25 minutes  
**Objective**: Develop deeper analytical skills

**Challenge Scenarios**:
1. **Constraint Analysis**: What limitations or constraints affect applying these concepts?
2. **Trade-off Evaluation**: What trade-offs are involved in following these principles?
3. **Context Dependency**: In what situations might these concepts not apply?
4. **Evolution Prediction**: How might these concepts change as technology evolves?

**Deliverable**: A brief analysis addressing each scenario with specific examples.

---

## 🔗 Cross-Topic Connections

**Integration Exercise**:
- How does {title} relate to other topics in this documentation?
- What patterns or themes do you see across different sections?
- Where do you see potential conflicts or tensions between different concepts?

**Systems Thinking**:
- How would you explain the role of these concepts in the broader context of distributed systems?
- What other knowledge areas complement what you've learned here?

---

## 🎯 Next Steps

**Immediate Actions**:
1. One thing you'll research further
2. One practice you'll try in your current work
3. One person you'll share this knowledge with

**Longer-term Learning**:
- What related topics would be valuable to study next?
- How will you stay current with developments in this area?
- What hands-on experience would solidify your understanding?

---
"""
        return exercises
    
    def needs_exercises(self, content):
        """Check if content already has exercises"""
        exercise_indicators = [
            'exercise', 'exercises', 'practice', 'hands-on',
            'try it', 'challenge', 'problem set', 'application'
        ]
        
        content_lower = content.lower()
        for indicator in exercise_indicators:
            if indicator in content_lower:
                return False
        
        return True
    
    def add_exercises_to_file(self, file_path):
        """Add exercises to a single file if needed"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not self.needs_exercises(content):
                return False
            
            content_type = self.get_content_type(file_path)
            exercise_generator = self.exercise_templates.get(content_type, self.exercise_templates['general'])
            
            exercises = exercise_generator(file_path, content)
            
            # Add exercises before any final quotes or closing sections
            if content.rstrip().endswith('"') and '*"' in content:
                # Find the last quote block
                last_quote = content.rfind('\n*"')
                if last_quote > 0:
                    new_content = content[:last_quote] + exercises + content[last_quote:]
                else:
                    new_content = content.rstrip() + exercises
            else:
                new_content = content.rstrip() + exercises
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.exercises_added += exercises.count('Exercise')
            self.files_modified += 1
            return True
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def add_exercises_to_all(self):
        """Add exercises to all files that need them"""
        print("💪 Adding exercises to files that need them...\n")
        
        files_processed = 0
        
        for md_file in sorted(self.docs_dir.rglob("*.md")):
            # Skip template and meta files
            if any(x in str(md_file) for x in ['TEMPLATE', 'GUIDE', 'STYLE', 'REPORT', 'exercises.md']):
                continue
            
            relative_path = md_file.relative_to(self.docs_dir)
            
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if self.needs_exercises(content):
                print(f"Processing {relative_path}...")
                
                if self.add_exercises_to_file(md_file):
                    print(f"  ✅ Added exercises")
                else:
                    print(f"  ❌ Failed to add exercises")
            
            files_processed += 1
        
        print(f"\n✅ Processed {files_processed} files")
        print(f"💪 Added exercises to {self.files_modified} files")
        print(f"📝 Total exercises created: {self.exercises_added}")
        
        # Save summary
        summary = {
            'files_processed': files_processed,
            'files_modified': self.files_modified,
            'exercises_added': self.exercises_added
        }
        
        with open('exercises_addition_report.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📄 Report saved to: exercises_addition_report.json")


if __name__ == "__main__":
    adder = ExerciseAdder()
    adder.add_exercises_to_all()