#!/usr/bin/env python3
"""
Create comprehensive Engineering Leadership interview content
"""

import os
from pathlib import Path

def create_leadership_content():
    """Create key content files for engineering leadership interviews"""
    
    base_path = Path('docs/interview-prep/engineering-leadership')
    
    # Main index content
    main_index = '''# Engineering Leadership Interview Guide

> Master the art of Engineering Manager and Director interviews at FAANG and top tech companies

## 🎯 Who This Guide Is For

This comprehensive guide is designed for:
- **Senior Engineers** transitioning to Engineering Manager roles (L5→L6)
- **Engineering Managers** targeting senior positions (L6→L7)
- **Senior Managers** aspiring to Director roles (L7→L8)
- **Directors** preparing for Senior Director or VP positions (L8+)

## 📊 Interview Components Breakdown

<div class="grid cards" markdown>

- :material-account-group:{ .lg } **[People Management](people-management/)** - 40%
    
    ---
    
    Master behavioral interviews focused on team leadership, performance management, and organizational growth
    
    **Key Topics**: Team building, conflict resolution, performance coaching, diversity & inclusion

- :material-rocket-launch:{ .lg } **[Technical Leadership](technical-leadership/)** - 25%
    
    ---
    
    Demonstrate technical depth while leading at scale
    
    **Key Topics**: Architecture reviews, technical strategy, platform thinking, innovation

- :material-sitemap:{ .lg } **[Organizational Design](organizational-design/)** - 15%
    
    ---
    
    Design and scale engineering organizations effectively
    
    **Key Topics**: Team topologies, Conway's Law, communication patterns, decision frameworks

- :material-chart-line:{ .lg } **[Business Acumen](business-product/)** - 10%
    
    ---
    
    Connect engineering excellence to business outcomes
    
    **Key Topics**: OKRs, resource allocation, cost optimization, stakeholder management

- :material-architecture:{ .lg } **[System Design](system-design-leadership/)** - 10%
    
    ---
    
    System design from a leadership perspective
    
    **Key Topics**: Organizational systems, cross-team dependencies, platform strategies

</div>

## 🏢 Company-Specific Preparation

<div class="grid cards" markdown>

- **[Amazon](company-specific/amazon/)** - Leadership Principles mastery
- **[Google](company-specific/google/)** - Googleyness & technical excellence  
- **[Meta](company-specific/meta/)** - Move fast culture & impact
- **[Apple](company-specific/apple/)** - Quality bar & functional excellence
- **[Microsoft](company-specific/microsoft/)** - Growth mindset & transformation
- **[Netflix](company-specific/netflix/)** - Freedom & responsibility culture

</div>

## 📈 Success Metrics You'll Need to Demonstrate

### Engineering Productivity
| Metric | Senior Manager | Director | Senior Director |
|--------|---------------|----------|-----------------|
| Team Size | 10-20 engineers | 30-50 engineers | 100+ engineers |
| Deployment Frequency | Weekly → Daily | Daily → Continuous | Platform-level CI/CD |
| Lead Time | Days → Hours | Hours → Minutes | Automated pipelines |
| MTTR | Hours → Minutes | Minutes → Seconds | Self-healing systems |

### Business Impact
| Level | Revenue Impact | Cost Optimization | User Scale |
|-------|---------------|-------------------|------------|
| L6/M1 | $1-5M | 10-20% efficiency | 100K-1M users |
| L7/M2 | $5-50M | 20-30% efficiency | 1M-10M users |
| L8+ | $50M+ | 30%+ efficiency | 10M+ users |

### People Leadership
- **Retention**: 90%+ top performer retention
- **Growth**: 20%+ annual team promotions
- **Diversity**: 30%+ underrepresented groups
- **Engagement**: 80%+ satisfaction scores

## 🎓 Preparation Journey

### Phase 1: Foundation (Weeks 1-4)
1. **Gap Analysis** - Assess your experience against target level
2. **Story Building** - Develop 15-20 STAR stories
3. **Company Research** - Deep dive into culture and values
4. **Technical Refresh** - Update on latest technologies

### Phase 2: Practice (Weeks 5-8)
1. **Mock Interviews** - 2-3 per week with peers
2. **Case Studies** - Work through scenarios
3. **Presentation Skills** - Executive communication
4. **Feedback Integration** - Iterate on weak areas

### Phase 3: Final Prep (Weeks 9-12)
1. **Company Specific** - Tailor stories to each company
2. **Question Practice** - 100+ behavioral questions
3. **System Design** - Leadership-focused problems
4. **Confidence Building** - Visualization and prep

## 🔑 Key Differentiators

### What Separates Good from Great

#### Good Candidates
- ✓ Manage teams effectively
- ✓ Deliver projects on time
- ✓ Handle day-to-day operations
- ✓ Resolve conflicts

#### Great Candidates
- ✓ Transform organizations
- ✓ Drive strategic initiatives
- ✓ Build lasting cultures
- ✓ Develop future leaders
- ✓ Create multiplier effects
- ✓ Influence without authority

## 📚 Essential Resources

### Must-Read Books
1. **"The Manager's Path"** by Camille Fournier
2. **"An Elegant Puzzle"** by Will Larson
3. **"Team Topologies"** by Skelton & Pais
4. **"Accelerate"** by Forsgren, Humble & Kim
5. **"The Culture Map"** by Erin Meyer

### Online Resources
- **[StaffEng.com](https://staffeng.com)** - Staff+ engineering stories
- **[LeadDev.com](https://leaddev.com)** - Engineering leadership content
- **[The Pragmatic Engineer](https://blog.pragmaticengineer.com)** - Industry insights

## 🚀 Quick Start Guide

### Week 1 Checklist
- [ ] Complete [Level Assessment](level-specific/level-expectations)
- [ ] Read [Company Cultures Overview](company-specific/)
- [ ] Start [Story Portfolio](behavioral-interviews/leadership-stories-framework)
- [ ] Review [Common Anti-patterns](assessment-rubrics/red-flags)

### First Mock Interview
1. Choose a [Practice Scenario](practice-scenarios/)
2. Use [STAR+ Framework](behavioral-interviews/star-method-advanced)
3. Record yourself for review
4. Get feedback from peers

## 💡 Pro Tips

### From Successful Candidates

> "The key is showing system-level thinking. Every story should demonstrate impact beyond your immediate team." - *L7 at Google*

> "They want to see that you can handle ambiguity. Don't always have the perfect answer ready." - *Director at Meta*

> "Culture fit is real. I spent 40% of my prep time understanding Amazon's leadership principles deeply." - *Senior Manager at Amazon*

---

**Ready to begin?** Start with [Understanding Interview Formats](interview-formats/) or jump directly to [Behavioral Interview Mastery](behavioral-interviews/).'''
    
    (base_path / 'index.md').write_text(main_index)
    print("Created main engineering leadership index")
    
    # Create key behavioral interview content
    behavioral_content = '''# STAR+ Method for Leadership Scenarios

## Overview

The STAR+ method extends the traditional STAR framework with crucial elements for leadership interviews at FAANG companies.

## The STAR+ Framework

### Traditional STAR
- **S**ituation - Context and background
- **T**ask - Your responsibility  
- **A**ction - What you did
- **R**esult - The outcome

### The "+" Additions for Leadership
- **L**earnings - What you learned and applied
- **S**cale - Size and complexity demonstrated
- **I**mpact - Long-term effects beyond immediate results

## Leadership Dimensions to Highlight

### 1. Scale and Complexity
Always quantify:
- Team size (direct and indirect reports)
- Budget responsibility
- User impact (MAU, revenue)
- Technical complexity (services, data volume)
- Timeline and constraints

### 2. Stakeholder Management
Demonstrate interaction with:
- Executive leadership (VP, C-level)
- Cross-functional partners (Product, Design, Sales)
- External partners and customers
- Board members (for senior roles)

### 3. Decision Making Under Ambiguity
Show how you:
- Gathered incomplete information
- Made reversible vs irreversible decisions  
- Balanced speed vs accuracy
- Communicated uncertainty

## Example: Scaling Engineering Team

### Situation
"At [Company], our engineering team of 12 was struggling to meet product demands as we grew from 100K to 1M users in 6 months."

### Task  
"As Engineering Manager, I needed to triple the team size while maintaining quality bar and team culture."

### Action
"I implemented a three-pronged approach:
1. **Hiring Strategy**: Partnered with recruiting to build a dedicated pipeline, implemented structured interviews, and trained 8 engineers as interviewers
2. **Onboarding Excellence**: Created a 2-week bootcamp reducing ramp time from 3 months to 6 weeks
3. **Team Structure**: Introduced pod model with tech leads, enabling autonomous execution"

### Result
"Successfully scaled to 38 engineers in 9 months, maintained 95% offer acceptance rate, and improved deployment frequency from weekly to daily"

### Learning
"I learned that scaling isn't just about hiring—it's about building systems. This experience led me to create a company-wide scaling playbook used by 5 other teams."

### Scale
"This transformation impacted 200+ employees across Product and Engineering, enabled $15M in new revenue, and became the blueprint for scaling from Series B to C."

### Impact
"Two years later, 6 of those engineers became managers themselves, and the pod structure is still used across the 150-person engineering org."

## Common Leadership Scenarios

### 1. Performance Management
- Turning around underperformers
- Managing out senior engineers
- Handling brilliant jerks
- Promoting high performers

### 2. Organizational Change
- Team reorganizations
- Merger integrations
- Pivoting technical direction
- Cultural transformations

### 3. Crisis Management
- Production outages
- Security breaches
- PR disasters
- Team conflicts

### 4. Strategic Initiatives
- Platform migrations
- New product launches
- Technical debt reduction
- Innovation programs

## Power Phrases for Leadership

### Demonstrating Ownership
- "I took responsibility for..."
- "I owned the outcome of..."
- "The buck stopped with me on..."

### Showing Strategic Thinking
- "I zoomed out to see..."
- "The long-term implication was..."
- "I considered second-order effects..."

### Highlighting People Leadership
- "I coached the team to..."
- "I created space for..."
- "I empowered engineers to..."

## Practice Framework

### Story Development Process
1. **Brainstorm** - List 20-30 situations
2. **Categorize** - Map to leadership competencies
3. **Quantify** - Add all metrics
4. **Rehearse** - Practice 2-minute versions
5. **Adapt** - Tailor to company values

### Mock Interview Script
```
Interviewer: "Tell me about a time you had to make a difficult decision"

You: "I'll share an example from [Company] that demonstrates [specific leadership principle].

[Situation - 20 seconds]
[Task - 10 seconds] 
[Action - 60 seconds with 3 specific steps]
[Result - 20 seconds with metrics]
[Learning - 10 seconds]

The scale of this was [quantify] and the long-term impact was [describe].

Would you like me to elaborate on any part of this experience?"
```

## Red Flags to Avoid

### In Your Stories
- ❌ Being the hero who saved everything alone
- ❌ Throwing team members under the bus
- ❌ Not acknowledging mistakes or learnings
- ❌ Focusing only on technical solutions

### In Your Delivery
- ❌ Rambling without structure
- ❌ Being too brief (under 90 seconds)
- ❌ Not reading interviewer cues
- ❌ Using too much jargon

## Company-Specific Adaptations

### Amazon - Leadership Principles
Focus on 2-3 principles per story:
- Ownership → "I owned the P&L..."
- Deliver Results → "We achieved 115% of target..."
- Dive Deep → "I personally reviewed the code..."

### Google - Collaboration
Emphasize cross-functional work:
- "Partnered with 4 product teams..."
- "Led virtual team of 20 across 3 offices..."
- "Influenced without direct authority..."

### Meta - Impact
Highlight velocity and scale:
- "Shipped in 6 weeks..."
- "Impacted 50M daily active users..."
- "Moved key metric by 12%..."

---

**Next Steps**: Build your story portfolio using our [Leadership Stories Framework](leadership-stories-framework) and practice with [Common Behavioral Questions](../practice-scenarios/).'''
    
    (base_path / 'behavioral-interviews' / 'star-method-advanced.md').write_text(behavioral_content)
    print("Created STAR+ method guide")
    
    # Create people management scenario
    people_mgmt = '''# Managing Underperformers - Practice Scenario

## Scenario Overview

You have a senior engineer (L5/E5) on your team who was previously a high performer but has been underperforming for the past 3 months. Their code quality has declined, they're missing deadlines, and other team members are starting to complain. This engineer has been with the company for 4 years and has critical knowledge of legacy systems.

## Key Information
- **Your Role**: Engineering Manager with 15 direct reports
- **Engineer Profile**: 
  - Name: Alex
  - Tenure: 4 years
  - Previous rating: Exceeds Expectations
  - Current performance: Below Expectations
  - Critical knowledge: Payment processing system
- **Timeline**: Q4 (performance reviews in 6 weeks)
- **Context**: Company recently went through layoffs

## Interview Questions You Might Face

### 1. Initial Approach
**Question**: "How would you first address this situation with Alex?"

**Strong Answer Framework**:
```
1. Private 1:1 meeting within 48 hours
2. Lead with curiosity, not judgment
3. Acknowledge previous strong performance
4. Ask open-ended questions:
   - "I've noticed some changes in your work recently. How are you feeling about things?"
   - "Is there anything going on that I should know about?"
   - "How can I better support you?"
5. Listen actively and take notes
```

### 2. Root Cause Analysis
**Question**: "What might be causing this performance change?"

**Potential Causes to Explore**:
- **Personal**: Health, family, financial stress
- **Professional**: Burnout, lack of growth, post-layoff anxiety
- **Team**: Conflicts, changing dynamics
- **Technical**: Skill gaps, unclear requirements
- **Organizational**: Role clarity, competing priorities

### 3. Performance Improvement Plan
**Question**: "Walk me through creating a PIP for this engineer."

**Comprehensive PIP Structure**:

#### Week 1-2: Discovery and Alignment
- Document current performance gaps
- Set clear, measurable goals
- Agree on check-in cadence (weekly)
- Identify support resources

#### 30-Day Goals
- Code Quality: 0 critical bugs in PR reviews
- Delivery: Complete 2 medium-complexity tasks
- Communication: Daily standups, weekly 1:1s
- Collaboration: Pair program 2x/week

#### 60-Day Goals  
- Lead one feature end-to-end
- Mentor junior engineer
- Document one legacy system
- Receive "Meets" on all competencies

#### 90-Day Goals
- Return to full productivity
- Positive peer feedback
- Clear growth trajectory

### 4. Balancing Team Impact
**Question**: "How do you manage the team's concerns while supporting Alex?"

**Leadership Approach**:
1. **Protect Privacy**: Never discuss Alex's situation
2. **Redistribute Work**: Temporarily rebalance without overloading others
3. **Address Concerns**: "I'm aware of the situation and actively addressing it"
4. **Monitor Morale**: Weekly team health checks
5. **Celebrate Wins**: Highlight when Alex improves

### 5. Difficult Decisions
**Question**: "What if Alex doesn't improve after the PIP?"

**Decision Framework**:
```
1. Evaluate Progress
   - Met 0-50% of goals → Transition planning
   - Met 50-80% of goals → Extend with modifications
   - Met 80%+ of goals → Continue support

2. Transition Planning (if needed)
   - 4-week knowledge transfer
   - Document critical systems
   - Pair with team members
   - Respectful exit

3. Team Communication
   - "Alex has decided to pursue opportunities outside the company"
   - Focus on smooth transition
   - Acknowledge contributions
```

## Advanced Considerations

### Legal and HR Aspects
- Document everything in writing
- Include HR from day 1
- Follow company PIP process
- Consider protected class implications
- Maintain confidentiality

### Knowledge Transfer Risk
- Start documentation immediately
- Assign backup for critical systems
- Create runbooks
- Record architecture decisions
- Pair programming for knowledge sharing

### Team Dynamics
- Prevent resentment buildup
- Maintain fairness perception
- Continue team building
- Address survivor syndrome
- Celebrate team resilience

## Role-Play Practice

### Interviewer Challenge Questions

**Q**: "What if Alex says they're dealing with depression?"
**A**: "I'd express empathy, suggest EAP resources, work with HR on accommodations, and adjust the PIP timeline while maintaining performance standards."

**Q**: "How do you handle if other team members threaten to leave?"
**A**: "I'd have individual conversations to understand concerns, share what I can about addressing the situation, and ensure they feel valued while maintaining Alex's privacy."

**Q**: "What if Alex has critical knowledge no one else has?"
**A**: "I'd immediately start risk mitigation: assign a backup, begin documentation, schedule knowledge transfer sessions, and consider extending timeline if progress is shown."

## Success Metrics

### For Alex
- Performance improvement trajectory
- Engagement score increase
- Code quality metrics
- On-time delivery rate

### For Team
- Team morale scores
- Productivity maintenance
- Knowledge distribution
- Retention of other members

### For You as Manager
- Following process correctly
- Maintaining team productivity
- Showing empathy and fairness
- Making timely decisions

## Key Takeaways

### What Great Looks Like
- ✅ Balances empathy with accountability
- ✅ Protects team productivity
- ✅ Follows proper process
- ✅ Develops contingency plans
- ✅ Maintains confidentiality

### Common Pitfalls
- ❌ Avoiding the conversation
- ❌ Being too soft or too harsh
- ❌ Surprising Alex with feedback
- ❌ Ignoring team impact
- ❌ Not involving HR early

---

**Practice Tip**: Role-play this scenario focusing on different aspects - the initial conversation, team meeting, HR discussion, and final decision. Each requires different skills and approaches.'''
    
    (base_path / 'practice-scenarios' / 'underperformer-scenario.md').write_text(people_mgmt)
    print("Created underperformer scenario")
    
    # Create Amazon-specific content
    amazon_content = '''# Amazon Leadership Principles Deep Dive for Engineering Leaders

## Overview

Amazon's interview process for engineering leaders (L6+) heavily focuses on Leadership Principles (LPs). You'll face 4-6 behavioral interviews, each targeting 2-3 specific LPs. Success requires demonstrating these principles at scale.

## The Bar Raiser Process

### What to Expect
- One interviewer is a trained Bar Raiser
- They have veto power over hiring decisions
- Focus on long-term potential, not just current skills
- Will dig deep with "Tell me more" follow-ups

### How to Prepare
- Have 2-3 stories per Leadership Principle
- Include failure stories (Learn and Be Curious)
- Quantify everything with data
- Show increasing scope over time

## L6+ Leadership Principles Deep Dive

### 1. Ownership (Critical for L6+)

**What It Means at Scale**:
- Own outcomes beyond your immediate team
- Think like a General Manager
- No "that's not my job" mentality
- Long-term thinking (3+ years)

**L6 Example Story Structure**:
"When our payment system reliability dropped to 97.5%, affecting $2M daily transactions, I owned the resolution despite payments being outside my direct scope. I formed a virtual team across 3 organizations, led the architecture review, and implemented a new monitoring system. Result: 99.99% reliability, saving $500K annually in failed transaction costs."

**Interview Questions**:
- "Tell me about a time you took ownership of something outside your area"
- "Describe a situation where you had to make a decision with long-term implications"
- "When have you sacrificed short-term gains for long-term value?"

### 2. Deliver Results (Table Stakes)

**L7+ Expectations**:
- Deliver business impact, not just features
- Handle multiple competing priorities
- Drive results through influence
- Overcome significant obstacles

**Key Metrics to Highlight**:
- Revenue impact ($X million)
- Cost savings (X% reduction)
- Performance improvements (Xms → Yms)
- Team productivity (X% increase)

**Power Story Framework**:
"Despite [major obstacle], I delivered [specific result] by [innovative approach], resulting in [business impact] and [long-term benefit]."

### 3. Hire and Develop the Best

**Leadership Demonstration**:
- Building diverse teams from scratch
- Developing future leaders
- Creating talent pipelines
- Improving hiring processes

**L6 Story Example**:
"I raised our hiring bar by implementing structured interviews, resulting in offer acceptance increasing from 60% to 85% and new hire performance ratings improving by 30%. I personally mentored 5 engineers to promotion, with 2 becoming managers."

### 4. Think Big (L7+ Differentiator)

**Scale of Thinking**:
- L6: Transform your product area
- L7: Transform your organization  
- L8: Transform the company

**Story Elements**:
- Ambitious vision (10x, not 10%)
- Challenge status quo
- Inspire others to join
- Deliver step-function change

### 5. Earn Trust (Stakeholder Management)

**Engineering Leader Focus**:
- Transparent communication during outages
- Building credibility with non-technical leaders
- Admitting mistakes and showing growth
- Data-driven decision making

**Anti-patterns to Avoid**:
- Blaming others or circumstances
- Hiding problems until too late
- Over-promising and under-delivering
- Not admitting knowledge gaps

### 6. Have Backbone; Disagree and Commit

**Senior Leadership Nuance**:
- Disagree with senior leaders respectfully
- Know when to escalate vs commit
- Build coalition when needed
- Document decisions and rationale

**Story Structure**:
"I respectfully disagreed with [senior leader] about [technical decision] because [data/reasoning]. I proposed [alternative] and after healthy debate, we agreed to [outcome]. I then fully committed by [specific actions]."

### 7. Dive Deep (Technical Credibility)

**L6+ Balance**:
- Stay technical enough to make informed decisions
- Know when to dive deep vs delegate
- Use technical knowledge to unblock teams
- Identify systemic issues from details

## Interview Day Strategy

### Interview Loop Structure
1. **Hiring Manager**: Overall fit + 2-3 LPs
2. **Skip Level**: Think Big, Ownership
3. **Peer Managers**: Earn Trust, Deliver Results  
4. **Bar Raiser**: Any LPs, culture fit
5. **Technical**: Dive Deep, Think Big

### STAR Story Bank

Create 15-20 stories covering:
- Scaling teams (Hire and Develop)
- Technical migrations (Ownership, Think Big)
- Conflict resolution (Earn Trust, Backbone)
- Failure recovery (Learn and Be Curious)
- Process improvements (Insist on High Standards)

### The "Tell Me More" Technique

Be prepared for 3-4 follow-ups:
1. Initial story (2 minutes)
2. "What was your specific role?" (30 seconds)
3. "What would you do differently?" (30 seconds)
4. "How did you measure success?" (30 seconds)
5. "What was the lasting impact?" (30 seconds)

## Red Flags for Amazon

### Avoid These
- 🚫 "My team did X" without your specific contribution
- 🚫 Perfect success stories with no learnings
- 🚫 Blaming AWS/tools/process for failures
- 🚫 Not knowing your metrics/data
- 🚫 Short-term thinking

### Embrace These
- ✅ "I failed at X, learned Y, applied it to Z"
- ✅ Specific mechanisms you created
- ✅ Customer obsession in every story
- ✅ Data-driven decisions
- ✅ Bias for action examples

## L6 vs L7 vs L8 Expectations

### L6 (Senior Manager)
- Team: 10-20 engineers
- Scope: Single product/service
- Impact: $1-10M
- Focus: Execution excellence

### L7 (Principal/Director)
- Team: 30-50 engineers  
- Scope: Multiple products/platform
- Impact: $10-50M
- Focus: Strategy and vision

### L8 (Senior Principal/Senior Director)
- Team: 100+ engineers
- Scope: Business unit
- Impact: $50M+
- Focus: Organizational transformation

## Practice Questions Bank

### Ownership
1. Tell me about a time you owned something end-to-end
2. Describe a situation where you went beyond your job description
3. When have you made a decision that wasn't popular but was right for the long term?

### Deliver Results
1. Tell me about your most challenging project delivery
2. How do you handle competing priorities?
3. Describe a time you delivered results despite significant obstacles

### Hire and Develop
1. How have you raised the hiring bar?
2. Tell me about someone you developed into a leader
3. How do you build diverse teams?

### Think Big
1. What's the biggest idea you've implemented?
2. How do you inspire teams to think beyond constraints?
3. Tell me about a time you transformed an organization

## Final Tips

### Preparation Timeline
- **8 weeks out**: Map stories to all 14 LPs
- **6 weeks out**: Practice with Amazonians
- **4 weeks out**: Refine based on feedback
- **2 weeks out**: Mock interview loops
- **1 week out**: Review and polish

### Day-of Success Factors
1. Bring printed story matrix (LP x Story)
2. Have water and take pauses
3. Ask clarifying questions
4. Close each interview strong
5. Send thank you notes

---

**Remember**: Amazon wants leaders who can scale. Every story should demonstrate increasing scope, complexity, and impact. Show that you're ready for the next level, not just maintaining at current level.'''
    
    (base_path / 'company-specific' / 'amazon' / 'index.md').write_text(amazon_content)
    print("Created Amazon-specific content")
    
    # Create technical leadership content
    tech_leadership = '''# Technical Strategy for Engineering Leaders

## Overview

As an engineering leader at L6+, you must balance staying technical enough to make informed decisions while operating at a strategic level. This guide covers how to demonstrate technical leadership in interviews.

## The Technical Leadership Paradox

### The Challenge
- Too technical → "Why aren't you an IC?"
- Too high-level → "Do you still understand the tech?"
- Just right → Strategic thinking grounded in technical reality

### The Sweet Spot
Show you can:
1. Understand technical implications of business decisions
2. Translate between engineering and business stakeholders  
3. Make architectural decisions with long-term thinking
4. Guide technical direction without micromanaging

## Core Technical Strategy Topics

### 1. Platform vs Product Thinking

**Key Interview Question**: "How do you decide when to build a platform?"

**Framework Answer**:
```
1. Current State Analysis
   - 3+ teams solving similar problems
   - 30%+ duplicate effort across teams
   - Inconsistent user experience

2. Platform Investment Criteria  
   - ROI positive within 18 months
   - Enables 5x velocity after adoption
   - Reduces operational overhead 50%

3. Migration Strategy
   - Start with willing early adopters
   - Build migration tools, not mandates
   - Measure adoption and satisfaction
```

**Real Example Structure**:
"At [Company], 5 teams were building separate authentication systems. I led the platform initiative that consolidated into a single identity platform, reducing authentication bugs by 70% and enabling SSO across all products. The 6-month investment paid back in 8 months through reduced duplicate work."

### 2. Technical Debt Strategy

**Leadership Approach to Tech Debt**:

#### Classification Framework
1. **Critical**: Security vulnerabilities, data corruption risks
2. **High**: Performance degradation, maintenance burden
3. **Medium**: Developer experience, minor inefficiencies  
4. **Low**: Code cleanup, nice-to-haves

#### Investment Strategy
- Allocate 20% of capacity to debt reduction
- Tie debt work to business outcomes
- Create "Tech Debt Friday" culture
- Measure debt impact in dollars

#### Story Example
"I inherited a team where deployment took 4 hours due to technical debt. Rather than a big rewrite, I implemented a quarterly 'Tech Debt Sprint' where we'd fix the highest-ROI items. After 1 year, deployment time dropped to 15 minutes, saving 100 engineering hours/month."

### 3. Build vs Buy Decisions

**Decision Framework**:

```mermaid
graph TD
    A[New Capability Needed] --> B{Core to Business?}
    B -->|Yes| C{Existing Solutions?}
    B -->|No| D[Buy/SaaS]
    C -->|Yes| E{Meets 80% Needs?}
    C -->|No| F[Build]
    E -->|Yes| G{TCO Analysis}
    E -->|No| F
    G -->|Build Cheaper| F
    G -->|Buy Cheaper| D
```

**Interview Answer Template**:
"When evaluating [specific technology], I consider:
1. Strategic importance (is this our differentiator?)
2. Total cost of ownership over 3 years
3. Opportunity cost of engineering time
4. Vendor lock-in risks
5. Security and compliance requirements"

### 4. Architecture Reviews

**How to Run Effective Architecture Reviews**:

#### Pre-Review (L6+ Leader Actions)
- Set clear decision criteria
- Ensure right stakeholders included
- Pre-read documents
- Identify key risks

#### During Review
- Ask probing questions, don't prescribe solutions
- Focus on non-functional requirements
- Challenge assumptions respectfully
- Document decisions and rationale

#### Post-Review
- Clear action items with owners
- Follow-up on implementation
- Share learnings broadly
- Update architecture guidelines

### 5. Innovation Framework

**Creating Space for Innovation**:

#### 20% Time Reality
"I implemented 'Innovation Fridays' where engineers could work on anything that might benefit the company. Rules: Demo monthly, measure impact, ship if successful. Result: 3 major features came from this, including our ML-based error detection saving $2M annually."

#### Hackathon Strategy  
- Theme-based (e.g., "Developer Productivity")
- Cross-functional teams required
- Executive judging panel
- Winner gets resourced for production

#### Innovation Metrics
- Ideas generated per quarter
- % of ideas reaching production
- Revenue from innovation projects
- Patent applications filed

## System Design for Leaders

### Different Focus Areas

#### IC System Design
- API design
- Database schemas  
- Algorithm efficiency
- Caching strategies

#### Leadership System Design
- Team boundaries (Conway's Law)
- Service ownership models
- Cross-team dependencies
- Organizational scaling

### Example: Designing a Notification System

**IC Approach**:
"I'd use Redis for queuing, PostgreSQL for templates, and websockets for real-time delivery..."

**Leadership Approach**:
"I'd first identify which teams need notifications - likely 5-6 teams. Rather than each building their own, I'd create a platform team owning a notification service. Key decisions:
- API design that prevents abuse
- SLA guarantees for different priority levels
- Cost model for internal charging
- Migration path for existing systems
- Team size: 4 engineers, 1 PM, 1 designer"

## Technical Competency Demonstrations

### 1. Staying Current

**Interview Question**: "How do you stay technical as a leader?"

**Strong Answer**:
"I maintain technical relevance through:
- Monthly architecture reviews where I ask deep questions
- Quarterly hack days where I code alongside the team
- Reading one technical paper/week in our domain
- Maintaining a side project in emerging tech
- Regular 1:1s with principal engineers"

### 2. Technical Decision Making

**Framework for Technical Decisions**:
1. **Gather Context**: Understand problem space
2. **Identify Options**: Usually 3-4 viable approaches
3. **Evaluate Trade-offs**: Performance vs cost vs time
4. **Prototype if Needed**: Spike highest-risk elements
5. **Decide and Document**: Clear rationale for future
6. **Measure Results**: Did we achieve intended outcomes?

### 3. Managing Technical Leaders

**Challenge**: Leading senior engineers who know more than you

**Approach**:
- Leverage their expertise, don't compete
- Focus on removing obstacles
- Connect their work to business impact
- Create growth opportunities
- Be the umbrella, not the expert

## Red Flags to Avoid

### In Technical Discussions
- ❌ Pretending to know technologies you don't
- ❌ Making decisions without consulting experts
- ❌ Using outdated technical references
- ❌ Micromanaging implementation details

### In Leadership Context  
- ❌ "I told the team exactly how to build it"
- ❌ "I don't need to understand the technical details"
- ❌ "We always use [specific technology]"
- ❌ "Technical debt isn't a priority"

## Practice Scenarios

### Scenario 1: Platform Migration
"Your company has 50 microservices on a deprecated platform. How do you lead the migration?"

### Scenario 2: AI/ML Investment  
"The CEO wants every team using AI. How do you implement this directive responsibly?"

### Scenario 3: Security Incident
"A critical vulnerability is discovered on Friday afternoon. Walk through your response."

### Scenario 4: Technical Hiring
"You need to hire 5 senior engineers in a competitive market. What's your strategy?"

---

**Key Takeaway**: Technical leadership isn't about being the best coder—it's about making informed decisions, creating the right environment for technical excellence, and translating between technology and business value.'''
    
    (base_path / 'technical-leadership' / 'technical-strategy.md').write_text(tech_leadership)
    print("Created technical leadership content")
    
    # Create level-specific guide
    level_guide = '''# Engineering Leadership Levels Across Tech Companies

## Level Mapping Across Companies

| Level | Amazon | Google | Meta | Apple | Microsoft | Typical Scope |
|-------|--------|--------|------|-------|-----------|--------------|
| Senior Engineer | L5 (SDE II) | L4 | E4 | ICT3 | 62 | Tech lead for 2-3 engineers |
| Staff/Lead | L6 (SDE III) | L5 | E5 | ICT4 | 63 | Tech lead for 5-8 engineers |
| Senior Manager | L6 | L6 | M1 | M1 | 64 | Manage 10-20 engineers |
| Principal/Director | L7 | L7 | M2 | M2 | 65 | Manage 30-50 engineers |
| Senior Director | L8 | L8 | D1 | M3 | 66 | Manage 100+ engineers |
| VP | L10 | L9 | D2 | M4 | 67 | Manage 200+ engineers |

## L6 / Senior Manager Expectations

### Scope and Impact
- **Team Size**: 10-20 direct reports or 2-3 team leads
- **Budget**: $2-5M annual (salaries + resources)
- **Product Scope**: Single product or major feature area
- **User Impact**: 100K - 1M users affected
- **Revenue Impact**: $1-10M influenced

### Core Competencies

#### People Leadership
- Hire and onboard 10+ engineers/year
- Conduct calibrations and performance reviews
- Coach 2-3 engineers to promotion annually
- Maintain 90%+ team retention of top performers
- Build inclusive team culture

#### Technical Leadership
- Own technical roadmap for area
- Make architectural decisions
- Review critical PRs and designs
- Stay hands-on enough to unblock team
- Drive best practices adoption

#### Business Partnership
- Work directly with PM/Design leads
- Present to director+ leadership
- Own team OKRs and metrics
- Make trade-off decisions
- Manage stakeholder expectations

### Interview Focus Areas
1. **Team scaling stories** (5→15 engineers)
2. **Performance management** (improvement & termination)
3. **Technical decision making** with business impact
4. **Cross-functional collaboration** examples
5. **Crisis management** and incident response

## L7 / Director Expectations

### Scope and Impact
- **Team Size**: 30-50 engineers (3-5 managers)
- **Budget**: $10-20M annual
- **Product Scope**: Multiple products or platform
- **User Impact**: 1M - 10M users
- **Revenue Impact**: $10-50M influenced

### Core Competencies

#### Organizational Leadership
- Design and implement org structures
- Lead managers and grow leadership bench
- Drive cultural change initiatives
- Navigate complex reorgs
- Build cross-company influence

#### Strategic Thinking
- Set 1-3 year technical vision
- Make build/buy/partner decisions
- Drive step-function improvements
- Identify new business opportunities
- Balance innovation with execution

#### Executive Communication
- Present to VP+ and board level
- Translate technical → business value
- Influence without authority
- Manage up effectively
- Represent engineering externally

### Interview Focus Areas
1. **Organizational transformation** stories
2. **Strategy development and execution**
3. **Managing managers** and leadership development
4. **Complex stakeholder management**
5. **Business acumen** and P&L understanding

## L8 / Senior Director Expectations

### Scope and Impact
- **Team Size**: 100+ engineers (5-10 managers)
- **Budget**: $30M+ annual  
- **Product Scope**: Business unit or major platform
- **User Impact**: 10M+ users
- **Revenue Impact**: $50M+ influenced

### Additional Competencies

#### Executive Leadership
- Report directly to VP/SVP
- Participate in company strategy
- Drive M&A technical evaluation
- Speak at industry conferences
- Shape company technical direction

#### Business Ownership
- Own P&L for area
- Drive new revenue streams
- Make strategic investments
- Partner with sales/marketing
- Influence product strategy

### Interview Focus Areas
1. **Executive presence** and communication
2. **P&L ownership** experience
3. **Industry influence** and thought leadership
4. **Large-scale transformations**
5. **Board/investor interactions**

## Compensation Ranges (2024)

### Total Compensation Packages

| Level | Base Salary | Equity/Year | Bonus | Total Comp |
|-------|------------|-------------|-------|------------|
| L6/M1 | $200-250K | $150-250K | 20-30% | $400-600K |
| L7/M2 | $275-350K | $300-500K | 25-35% | $650-950K |
| L8/D1 | $350-450K | $500-900K | 30-40% | $1-1.5M |
| VP | $400-600K | $1-2M | 40-50% | $1.5-3M |

*Note: Varies significantly by company, location, and negotiation*

### Negotiation Strategies

#### For L6/M1
- Highlight team size and scope
- Show revenue/cost impact
- Competing offers help most
- Sign-on bonus negotiable
- Refresh grants possible

#### For L7/M2
- Executive recruiter involvement
- Multiple competing offers expected
- Negotiate total package, not components
- Ask for accelerated vesting
- Consider non-monetary benefits

#### For L8+
- Work with executive search firms
- Negotiate reporting structure
- Discuss board observation rights
- Include severance terms
- Consider geographic flexibility

## Growth Trajectory Planning

### Typical Timeline
- **IC → Manager**: 1-2 years
- **Manager → Senior Manager**: 2-3 years
- **Senior Manager → Director**: 3-4 years
- **Director → Senior Director**: 3-5 years
- **Senior Director → VP**: 4-6 years

### Accelerators
1. **Scope Expansion**: Take on sister teams
2. **Crisis Leadership**: Lead through major incidents
3. **Revenue Generation**: Create new products
4. **Talent Development**: Build future leaders
5. **Strategic Initiatives**: Drive company-wide changes

### Common Blockers
1. **Limited Scope**: No room to grow in current role
2. **Technical Depth**: Losing touch with technology
3. **People Skills**: Struggling with leadership
4. **Business Acumen**: Not understanding commercial side
5. **Executive Presence**: Communication gaps

## Interview Preparation by Level

### L6 Preparation Focus
- 15-20 STAR stories ready
- Deep dive on people management
- Know your metrics cold
- Practice with L7+ leaders
- Research team you'll inherit

### L7 Preparation Focus
- Strategy case studies
- Organizational design scenarios
- Executive communication practice
- Industry trends knowledge
- Vision presentation ready

### L8+ Preparation Focus
- Board-level communication
- P&L discussions
- Industry thought leadership
- Transformation stories
- References from executives

## Red Flags by Level

### L6 Red Flags
- No direct management experience
- Can't articulate team metrics
- Blames others for failures
- No hiring experience
- Too technical/in the weeds

### L7 Red Flags
- Never managed managers
- No strategy experience
- Poor executive communication
- Limited business understanding
- No organizational change experience

### L8+ Red Flags
- No P&L responsibility
- Limited external presence
- Can't influence peers
- No transformation experience
- Weak executive network

---

**Action Items**: 
1. Identify your current level and target level
2. Gap analysis on competencies
3. Build experience in missing areas
4. Network with people at target level
5. Practice with level-appropriate scenarios'''
    
    (base_path / 'level-specific' / 'level-expectations.md').write_text(level_guide)
    print("Created level expectations guide")
    
    return "Engineering leadership interview content created successfully!"

# Run the creation
if __name__ == "__main__":
    result = create_leadership_content()
    print(result)