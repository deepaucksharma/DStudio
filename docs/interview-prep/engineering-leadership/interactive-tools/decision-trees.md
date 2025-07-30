# Interactive Decision Tree Navigator

## Overview

Navigate complex behavioral scenarios with guided decision trees. Practice making leadership decisions and see the consequences of different approaches.

<div class="decision-tree-container">

## 🌳 Select a Scenario

<div class="scenario-selector">
<button class="scenario-btn" data-scenario="underperformer">Managing an Underperformer</button>
<button class="scenario-btn" data-scenario="conflict">Team Conflict Resolution</button>
<button class="scenario-btn" data-scenario="reorg">Organizational Restructure</button>
<button class="scenario-btn" data-scenario="crisis">Production Crisis</button>
<button class="scenario-btn" data-scenario="hiring">Difficult Hiring Decision</button>
</div>

## 🎯 Decision Navigator

<div id="decision-tree" class="tree-container">
<div class="scenario-intro" id="scenario-intro">
<h3>Select a scenario above to begin</h3>
<p>Each scenario presents real-world leadership challenges with multiple decision points. Your choices will lead to different outcomes and learning opportunities.</p>
</div>
</div>

## 📊 Decision Analysis

<div class="analysis-panel" id="analysis-panel" style="display: none;">
<h3>Your Decision Path</h3>
<div id="decision-path"></div>
<h3>Outcome Analysis</h3>
<div id="outcome-analysis"></div>
<h3>Alternative Approaches</h3>
<div id="alternatives"></div>
<button class="restart-btn" onclick="restartScenario()">Try Another Path</button>
</div>

</div>

## 🎭 Scenario Library

### 1. Managing an Underperformer
**Complexity**: High  
**Key Skills**: Performance management, empathy, documentation, legal awareness

**Starting Situation**: Your senior engineer (L5, 5 years tenure) has been underperforming for 3 months. Previously a top performer, their code quality has dropped, they're missing deadlines, and team members are complaining.

**Decision Points**:
- Initial approach (1:1 vs team meeting vs HR involvement)
- Root cause investigation
- Support vs accountability balance
- Timeline and milestones
- Team communication strategy

### 2. Team Conflict Resolution
**Complexity**: Very High  
**Key Skills**: Mediation, cultural awareness, team dynamics, fairness

**Starting Situation**: Two senior engineers on your team aren't speaking to each other after a heated code review. The team is splitting into factions, impacting productivity.

**Decision Points**:
- Immediate intervention strategy
- Individual vs group approach
- Technical vs interpersonal focus
- Long-term team structure
- Prevention measures

### 3. Organizational Restructure
**Complexity**: Extreme  
**Key Skills**: Strategic thinking, communication, change management

**Starting Situation**: Company pivoting from B2C to B2B. Your 40-person org needs restructuring from functional teams to business-aligned teams. Morale is low due to rumors.

**Decision Points**:
- Communication strategy
- Team formation approach
- Timeline decisions
- People placement
- Managing resistance

### 4. Production Crisis
**Complexity**: High  
**Key Skills**: Crisis management, technical judgment, communication

**Starting Situation**: Major outage affecting 50% of users. Root cause unknown. CEO asking for updates every 30 minutes. Team is panicking.

**Decision Points**:
- Incident commander selection
- Communication cadence
- Resource allocation
- Risk decisions
- Post-mortem approach

### 5. Difficult Hiring Decision
**Complexity**: Medium  
**Key Skills**: Hiring judgment, team dynamics, diversity awareness

**Starting Situation**: Final round candidate is technically brilliant but multiple interviewers flagged culture concerns. Team desperately needs senior talent.

**Decision Points**:
- Weighting of feedback
- Additional assessment
- Team involvement
- Offer decisions
- Risk mitigation

## 🧭 Decision Framework

### The DECIDE Model
- **D**efine the problem clearly
- **E**stablish criteria for solutions
- **C**onsider alternatives
- **I**dentify best alternatives
- **D**evelop implementation plan
- **E**valuate and monitor

### Key Principles
1. **Reversible vs Irreversible**: One-way vs two-way doors
2. **Blast Radius**: Who/what is affected?
3. **Time Sensitivity**: Urgent vs Important matrix
4. **Information Completeness**: Known unknowns
5. **Stakeholder Impact**: RACI analysis

## 📈 Learning Outcomes

Track your decision patterns:

| Scenario | Attempts | Best Path Found | Key Learning |
|----------|----------|-----------------|--------------|
| Underperformer | 0 | ❌ | - |
| Team Conflict | 0 | ❌ | - |
| Reorg | 0 | ❌ | - |
| Crisis | 0 | ❌ | - |
| Hiring | 0 | ❌ | - |

<script>
const scenarios = {
    underperformer: {
        title: "Managing an Underperformer",
        intro: "Your senior engineer Alex (L5, 5 years tenure) has been underperforming for 3 months. Previously a top performer with critical knowledge of your authentication system, their code quality has dropped, they're missing deadlines, and team members are complaining. What's your first move?",
        decisions: {
            start: {
                text: "Your senior engineer Alex (L5, 5 years tenure) has been underperforming for 3 months. What's your first move?",
                options: [
                    {
                        text: "Schedule immediate 1:1 to discuss performance",
                        next: "immediate_meeting",
                        score: 8,
                        feedback: "Good: Direct approach shows urgency and care"
                    },
                    {
                        text: "Gather more data from team members first",
                        next: "gather_data",
                        score: 9,
                        feedback: "Excellent: Getting full context prevents assumptions"
                    },
                    {
                        text: "Involve HR immediately",
                        next: "hr_early",
                        score: 4,
                        feedback: "Too early: Try direct management first"
                    },
                    {
                        text: "Address it in team meeting",
                        next: "public_shame",
                        score: 1,
                        feedback: "Poor: Never address performance publicly"
                    }
                ]
            },
            immediate_meeting: {
                text: "In the 1:1, Alex seems defensive and says 'everything is fine.' How do you proceed?",
                options: [
                    {
                        text: "Push harder with specific examples",
                        next: "confrontational",
                        score: 5,
                        feedback: "Risky: May damage relationship"
                    },
                    {
                        text: "Switch to asking 'How can I support you?'",
                        next: "supportive",
                        score: 9,
                        feedback: "Excellent: Opens dialogue, shows care"
                    },
                    {
                        text: "End meeting and document concerns",
                        next: "document_only",
                        score: 6,
                        feedback: "Incomplete: Missing opportunity to help"
                    }
                ]
            },
            gather_data: {
                text: "Team feedback reveals: code reviews taking 3x longer, Alex seems distracted, arriving late. One teammate mentions Alex going through a divorce. What now?",
                options: [
                    {
                        text: "1:1 focusing on work impact only",
                        next: "work_only",
                        score: 6,
                        feedback: "Good but incomplete approach"
                    },
                    {
                        text: "1:1 with empathy for personal situation",
                        next: "empathetic",
                        score: 10,
                        feedback: "Excellent: Balances care with accountability"
                    },
                    {
                        text: "Suggest Alex take time off",
                        next: "time_off",
                        score: 7,
                        feedback: "Good option but needs discussion first"
                    }
                ]
            },
            empathetic: {
                text: "Alex opens up about divorce and custody battle. They want to improve but are struggling. What support do you offer?",
                options: [
                    {
                        text: "Flexible schedule + reduced workload temporarily",
                        next: "accommodation",
                        score: 9,
                        feedback: "Great: Practical support with boundaries"
                    },
                    {
                        text: "EAP referral + regular check-ins",
                        next: "eap_support",
                        score: 8,
                        feedback: "Good: Professional help + ongoing support"
                    },
                    {
                        text: "Just empathy, no work changes",
                        next: "no_action",
                        score: 4,
                        feedback: "Insufficient: Need concrete support"
                    }
                ]
            },
            accommodation: {
                text: "After 4 weeks with accommodations, there's 30% improvement but still below standards. Team patience wearing thin. Next step?",
                options: [
                    {
                        text: "Formal PIP with HR involvement",
                        next: "pip",
                        score: 8,
                        feedback: "Appropriate: Clear expectations needed"
                    },
                    {
                        text: "Extend accommodations another month",
                        next: "extend",
                        score: 5,
                        feedback: "Risk: Team morale may suffer"
                    },
                    {
                        text: "Move Alex to less critical project",
                        next: "reassign",
                        score: 7,
                        feedback: "Pragmatic but doesn't solve core issue"
                    }
                ]
            },
            pip: {
                text: "PIP clearly outlines 30-60-90 day goals. Alex is motivated but anxious. How do you manage team dynamics during PIP?",
                options: [
                    {
                        text: "Transparency with team about support plan",
                        next: "transparent",
                        score: 8,
                        feedback: "Good: Reduces speculation, shows leadership"
                    },
                    {
                        text: "Keep PIP confidential, redistribute work quietly",
                        next: "confidential",
                        score: 9,
                        feedback: "Better: Protects Alex's dignity"
                    },
                    {
                        text: "Team meeting about performance standards",
                        next: "team_standards",
                        score: 6,
                        feedback: "OK but may feel targeted"
                    }
                ]
            },
            confidential: {
                text: "Day 60 of PIP: Alex met goals, quality improved 70%, team relationships healing. Custody settled. What's your recommendation?",
                options: [
                    {
                        text: "Successfully complete PIP, full duties restored",
                        next: "success",
                        score: 10,
                        feedback: "Excellent outcome: Patience paid off"
                    },
                    {
                        text: "Extend PIP for extra certainty",
                        next: "extend_pip",
                        score: 6,
                        feedback: "Unnecessary: May damage trust"
                    },
                    {
                        text: "Complete PIP but monitor closely",
                        next: "conditional",
                        score: 8,
                        feedback: "Reasonable but show more confidence"
                    }
                ]
            },
            success: {
                text: "SUCCESS: Alex returns to high performance, becomes advocate for mental health support. Team stronger than before. What long-term changes do you implement?",
                options: [
                    {
                        text: "Mental health awareness program",
                        next: "final",
                        score: 10,
                        feedback: "Excellent: Systemic improvement"
                    },
                    {
                        text: "Better early warning systems",
                        next: "final",
                        score: 9,
                        feedback: "Great: Proactive approach"
                    },
                    {
                        text: "Document process for future",
                        next: "final",
                        score: 8,
                        feedback: "Good: Learning captured"
                    }
                ]
            }
        }
    },
    conflict: {
        title: "Team Conflict Resolution",
        intro: "Two senior engineers, Sarah and Marcus, haven't spoken since a heated code review two weeks ago. The team is dividing into camps. Sprint velocity down 40%. How do you intervene?",
        decisions: {
            start: {
                text: "Two senior engineers haven't spoken since a heated code review. Team is taking sides. Sprint velocity down 40%. Your first action?",
                options: [
                    {
                        text: "Meet with both engineers together immediately",
                        next: "joint_meeting",
                        score: 4,
                        feedback: "Risky: May escalate without preparation"
                    },
                    {
                        text: "1:1 with each engineer separately first",
                        next: "separate_meetings",
                        score: 10,
                        feedback: "Excellent: Understand both perspectives"
                    },
                    {
                        text: "Team meeting to address the elephant",
                        next: "team_meeting",
                        score: 3,
                        feedback: "Poor: Public forum may worsen conflict"
                    },
                    {
                        text: "Let them work it out themselves",
                        next: "no_action",
                        score: 1,
                        feedback: "Failure: Leadership intervention needed"
                    }
                ]
            },
            separate_meetings: {
                text: "Sarah says Marcus 'brutally attacked' her design. Marcus says Sarah 'can't take technical feedback.' Both have examples. What's your focus?",
                options: [
                    {
                        text: "Focus on communication styles",
                        next: "communication",
                        score: 9,
                        feedback: "Great: Address how, not just what"
                    },
                    {
                        text: "Determine who was technically correct",
                        next: "technical_focus",
                        score: 4,
                        feedback: "Missing point: It's about respect"
                    },
                    {
                        text: "Focus on team impact",
                        next: "team_impact",
                        score: 8,
                        feedback: "Good: Highlights consequences"
                    }
                ]
            },
            communication: {
                text: "Both acknowledge communication breakdown. Sarah values collaboration; Marcus values directness. Neither wants to compromise their style. How proceed?",
                options: [
                    {
                        text: "Facilitate style appreciation workshop",
                        next: "workshop",
                        score: 8,
                        feedback: "Good: Educational approach"
                    },
                    {
                        text: "Create team communication norms",
                        next: "team_norms",
                        score: 10,
                        feedback: "Excellent: Systematic solution"
                    },
                    {
                        text: "Mediated conversation with ground rules",
                        next: "mediation",
                        score: 9,
                        feedback: "Very good: Direct resolution"
                    }
                ]
            },
            team_norms: {
                text: "Team creates norms: 'Critique code, not people' and 'Assume positive intent.' Sarah and Marcus agree intellectually but still tense. Next step?",
                options: [
                    {
                        text: "Pair them on non-critical task",
                        next: "pair_work",
                        score: 9,
                        feedback: "Excellent: Rebuilding through action"
                    },
                    {
                        text: "Keep them separated for now",
                        next: "separation",
                        score: 5,
                        feedback: "Delays inevitable reconciliation"
                    },
                    {
                        text: "Public acknowledgment of progress",
                        next: "public_praise",
                        score: 7,
                        feedback: "Good but may feel forced"
                    }
                ]
            },
            pair_work: {
                text: "After initial awkwardness, they complete task successfully. Code review goes well with new norms. Team cautiously optimistic. How do you reinforce?",
                options: [
                    {
                        text: "Regular retrospectives on communication",
                        next: "retrospectives",
                        score: 10,
                        feedback: "Excellent: Continuous improvement"
                    },
                    {
                        text: "Private praise to both",
                        next: "private_praise",
                        score: 8,
                        feedback: "Good: Positive reinforcement"
                    },
                    {
                        text: "Move on, problem solved",
                        next: "no_followup",
                        score: 4,
                        feedback: "Premature: Needs reinforcement"
                    }
                ]
            },
            retrospectives: {
                text: "SUCCESS: Three months later, Sarah and Marcus model healthy debate. Team psychological safety scores improve 40%. They jointly mentor juniors on communication. What systemic changes do you make?",
                options: [
                    {
                        text: "Conflict resolution training for all",
                        next: "final",
                        score: 10,
                        feedback: "Excellent: Preventive measure"
                    },
                    {
                        text: "Add communication to performance reviews",
                        next: "final",
                        score: 9,
                        feedback: "Great: Incentivizes behavior"
                    },
                    {
                        text: "Document case study for organization",
                        next: "final",
                        score: 8,
                        feedback: "Good: Shares learning"
                    }
                ]
            }
        }
    },
    reorg: {
        title: "Organizational Restructure",
        intro: "Company pivoting from B2C to B2B. Your 40-person org structured by function (frontend, backend, data) needs to become business-aligned teams. Rumors causing anxiety.",
        decisions: {
            start: {
                text: "Company announced B2C to B2B pivot. Your 40-person functional org needs restructuring. Rumors already spreading. What's your first 48-hour priority?",
                options: [
                    {
                        text: "All-hands to share what you know",
                        next: "immediate_allhands",
                        score: 9,
                        feedback: "Excellent: Transparency reduces anxiety"
                    },
                    {
                        text: "1:1s with all team leads first",
                        next: "leads_first",
                        score: 8,
                        feedback: "Good: Build coalition but act fast"
                    },
                    {
                        text: "Design new org structure first",
                        next: "design_first",
                        score: 5,
                        feedback: "Too slow: Address anxiety immediately"
                    },
                    {
                        text: "Wait for executive guidance",
                        next: "wait",
                        score: 2,
                        feedback: "Poor: Shows lack of leadership"
                    }
                ]
            },
            immediate_allhands: {
                text: "All-hands done. You shared timeline, principles, and commitment to transparency. Team appreciates honesty but worried about their roles. Several top performers updating LinkedIn. Next?",
                options: [
                    {
                        text: "1:1s with flight risks immediately",
                        next: "retention",
                        score: 10,
                        feedback: "Excellent: Protect key talent"
                    },
                    {
                        text: "Form transition team with volunteers",
                        next: "transition_team",
                        score: 9,
                        feedback: "Great: Involve people in solution"
                    },
                    {
                        text: "Start skills mapping exercise",
                        next: "skills_map",
                        score: 7,
                        feedback: "Good but address retention first"
                    }
                ]
            },
            retention: {
                text: "Met with 8 key people. 6 committed to seeing through transition if involved in planning. 2 have offers elsewhere. You have retention budget. How to use it?",
                options: [
                    {
                        text: "Counter-offers for the 2 with offers",
                        next: "counter",
                        score: 6,
                        feedback: "OK but sets precedent"
                    },
                    {
                        text: "Retention bonuses for all key players",
                        next: "retention_bonus",
                        score: 9,
                        feedback: "Fair and forward-looking"
                    },
                    {
                        text: "Invest in transition success bonuses",
                        next: "success_bonus",
                        score: 10,
                        feedback: "Excellent: Aligns incentives"
                    }
                ]
            },
            success_bonus: {
                text: "Announced transition bonuses tied to milestones. Morale improved. Now designing structure: 4 business teams + 1 platform. How do you form teams?",
                options: [
                    {
                        text: "Let people choose teams/submit preferences",
                        next: "self_selection",
                        score: 9,
                        feedback: "Excellent: Maximizes buy-in"
                    },
                    {
                        text: "Leaders draft teams sports-style",
                        next: "draft",
                        score: 4,
                        feedback: "Degrading and divisive"
                    },
                    {
                        text: "You assign based on skills/needs",
                        next: "assignment",
                        score: 6,
                        feedback: "Efficient but less buy-in"
                    }
                ]
            },
            self_selection: {
                text: "Self-selection process: 80% got first choice, 20% negotiated. One team oversubscribed (payments), one under (compliance). How handle imbalance?",
                options: [
                    {
                        text: "Incentivize moves to compliance team",
                        next: "incentivize",
                        score: 9,
                        feedback: "Smart: Voluntary adjustment"
                    },
                    {
                        text: "Make case for compliance impact/growth",
                        next: "sell_vision",
                        score: 10,
                        feedback: "Excellent: Appeal to purpose"
                    },
                    {
                        text: "Mandate some moves",
                        next: "mandate",
                        score: 5,
                        feedback: "Breaks trust in process"
                    }
                ]
            },
            sell_vision: {
                text: "Your compliance vision pitch worked! 3 senior engineers volunteered to switch. Teams balanced. Week 8: New structure live but friction at boundaries. How address?",
                options: [
                    {
                        text: "Weekly cross-team sync meetings",
                        next: "sync_meetings",
                        score: 7,
                        feedback: "Good but may become ritual"
                    },
                    {
                        text: "Rotation program between teams",
                        next: "rotation",
                        score: 10,
                        feedback: "Excellent: Builds empathy"
                    },
                    {
                        text: "Joint OKRs requiring collaboration",
                        next: "joint_okrs",
                        score: 9,
                        feedback: "Great: Structural incentive"
                    }
                ]
            },
            rotation: {
                text: "SUCCESS: 6 months later - velocity up 60%, employee NPS up 20 points, successful B2B pivot with 10 enterprise clients. What made the difference?",
                options: [
                    {
                        text: "Transparency and involvement throughout",
                        next: "final",
                        score: 10,
                        feedback: "Key insight: People support what they help create"
                    },
                    {
                        text: "Focus on retention and stability",
                        next: "final",
                        score: 9,
                        feedback: "Important: Change needs continuity"
                    },
                    {
                        text: "Clear vision and communication",
                        next: "final",
                        score: 9,
                        feedback: "Critical: People need to see the why"
                    }
                ]
            }
        }
    },
    crisis: {
        title: "Production Crisis Management",
        intro: "It's 2 PM Friday. Major outage affecting 50% of users for 30 minutes. Revenue impact: $50K/minute. Root cause unknown. CEO texting you. Team starting to panic.",
        decisions: {
            start: {
                text: "Major outage, 30 min in, 50% users affected, $50K/min loss. CEO texting. Team panicking. Your immediate action?",
                options: [
                    {
                        text: "Take incident command yourself",
                        next: "self_command",
                        score: 6,
                        feedback: "OK but consider delegation"
                    },
                    {
                        text: "Assign best SRE as incident commander",
                        next: "delegate_command",
                        score: 10,
                        feedback: "Excellent: Right person, you manage up"
                    },
                    {
                        text: "All-hands on deck in war room",
                        next: "war_room",
                        score: 4,
                        feedback: "Chaos: Too many cooks"
                    },
                    {
                        text: "Respond to CEO first",
                        next: "ceo_first",
                        score: 3,
                        feedback: "Wrong priority: Fix first, communicate second"
                    }
                ]
            },
            delegate_command: {
                text: "Alex (senior SRE) takes command. Sets up channels: #incident-command, #incident-public. Initial theory: recent deploy. Rollback didn't help. CEO calling you. What now?",
                options: [
                    {
                        text: "Take CEO call, give honest update",
                        next: "ceo_honest",
                        score: 9,
                        feedback: "Good: Manage up while team works"
                    },
                    {
                        text: "Text CEO 'on it', focus on incident",
                        next: "ceo_defer",
                        score: 8,
                        feedback: "OK but CEO needs info"
                    },
                    {
                        text: "Have PR handle CEO",
                        next: "pr_handle",
                        score: 5,
                        feedback: "No: Your responsibility"
                    }
                ]
            },
            ceo_honest: {
                text: "Told CEO: 'Major outage, 45 min, best team on it, updates every 15 min.' CEO tense but trusts you. Team found issue: database connection pool exhausted. Fix options?",
                options: [
                    {
                        text: "Quick restart of DB connections",
                        next: "quick_fix",
                        score: 8,
                        feedback: "Good: Fast relief"
                    },
                    {
                        text: "Proper fix: Scale connection pool",
                        next: "proper_fix",
                        score: 6,
                        feedback: "Right but too slow now"
                    },
                    {
                        text: "Both: Restart then proper fix",
                        next: "both_fixes",
                        score: 10,
                        feedback: "Excellent: Quick relief + permanent fix"
                    }
                ]
            },
            both_fixes: {
                text: "Restart worked! 50% → 10% affected. Team implementing proper fix. 65 minutes total downtime. Customer complaints flooding in. How handle comms?",
                options: [
                    {
                        text: "Immediate detailed post-mortem blog",
                        next: "immediate_blog",
                        score: 7,
                        feedback: "Good impulse but too early"
                    },
                    {
                        text: "Status page update + CEO email customers",
                        next: "status_email",
                        score: 10,
                        feedback: "Excellent: Right channels and level"
                    },
                    {
                        text: "Wait until full resolution",
                        next: "wait_comms",
                        score: 4,
                        feedback: "Too slow: Customers need info"
                    }
                ]
            },
            status_email: {
                text: "Full resolution at 75 min. Customer comms sent. Team exhausted but system stable. It's 4 PM Friday. What's your immediate next step?",
                options: [
                    {
                        text: "Thank team, send them home",
                        next: "send_home",
                        score: 7,
                        feedback: "Kind but need minimal coverage"
                    },
                    {
                        text: "Quick retro while fresh, then rest",
                        next: "quick_retro",
                        score: 10,
                        feedback: "Perfect: Capture lessons, then rest"
                    },
                    {
                        text: "Start detailed investigation now",
                        next: "investigate_now",
                        score: 5,
                        feedback: "No: Team needs break"
                    }
                ]
            },
            quick_retro: {
                text: "15-min retro captured key facts. Team going home with on-call coverage. Monday: Full post-mortem reveals connection leak in new service. What systemic changes?",
                options: [
                    {
                        text: "Chaos engineering program",
                        next: "final",
                        score: 10,
                        feedback: "Excellent: Proactive failure discovery"
                    },
                    {
                        text: "Better monitoring and alerts",
                        next: "final",
                        score: 9,
                        feedback: "Great: Earlier detection"
                    },
                    {
                        text: "Stricter deploy processes",
                        next: "final",
                        score: 6,
                        feedback: "OK but may slow innovation"
                    }
                ]
            }
        }
    },
    hiring: {
        title: "Difficult Hiring Decision",
        intro: "Final candidate for senior role: brilliant technically (designed distributed systems at FAANG), but 3 interviewers flagged 'aggressive communication style.' Team desperate for senior talent.",
        decisions: {
            start: {
                text: "Final candidate: Technical genius but 3 of 5 interviewers concerned about 'aggressive communication.' Team desperate for senior help. Your move?",
                options: [
                    {
                        text: "Decline - culture fit is non-negotiable",
                        next: "quick_no",
                        score: 7,
                        feedback: "Safe but possibly hasty"
                    },
                    {
                        text: "Discuss concerns with candidate directly",
                        next: "address_directly",
                        score: 10,
                        feedback: "Excellent: Give them chance to address"
                    },
                    {
                        text: "Additional interview focused on collaboration",
                        next: "extra_interview",
                        score: 9,
                        feedback: "Very good: More data needed"
                    },
                    {
                        text: "Hire with coaching plan",
                        next: "hire_with_plan",
                        score: 5,
                        feedback: "Risky: Setting up for failure?"
                    }
                ]
            },
            address_directly: {
                text: "Call with candidate: 'I've been told I'm direct. At [FAANG], it was valued. I can adapt but won't pretend to be someone I'm not.' Seems genuine. Now what?",
                options: [
                    {
                        text: "Reference checks focusing on collaboration",
                        next: "references",
                        score: 10,
                        feedback: "Smart: Get external perspective"
                    },
                    {
                        text: "Trial project with team",
                        next: "trial",
                        score: 8,
                        feedback: "Good but time-consuming"
                    },
                    {
                        text: "Trust your gut - hire them",
                        next: "gut_hire",
                        score: 5,
                        feedback: "Need more data"
                    }
                ]
            },
            references: {
                text: "References reveal: 'Brilliant but impatient with slower folks. Improved with feedback. Best architect I've worked with. Wouldn't hesitate to hire again.' Mixed signals. Decision?",
                options: [
                    {
                        text: "Hire with explicit expectations",
                        next: "conditional_hire",
                        score: 9,
                        feedback: "Good: Clear boundaries"
                    },
                    {
                        text: "Pass - too risky for team dynamics",
                        next: "pass",
                        score: 7,
                        feedback: "Valid: Protecting team"
                    },
                    {
                        text: "Offer contractor-to-hire",
                        next: "contract",
                        score: 10,
                        feedback: "Excellent: Trial period for both"
                    }
                ]
            },
            contract: {
                text: "Candidate accepts 3-month contract-to-hire. Week 2: Brilliant technical contributions but interrupted junior engineer in meeting. How address?",
                options: [
                    {
                        text: "Immediate private feedback",
                        next: "quick_feedback",
                        score: 10,
                        feedback: "Perfect: Quick correction"
                    },
                    {
                        text: "Wait to see pattern",
                        next: "wait_pattern",
                        score: 5,
                        feedback: "No: Address immediately"
                    },
                    {
                        text: "Public correction in moment",
                        next: "public_correct",
                        score: 3,
                        feedback: "Harsh: Private is better"
                    }
                ]
            },
            quick_feedback: {
                text: "Candidate responded well: 'Thanks for direct feedback. Working on patience.' Month 2: Technical impact huge, communication improving. Team warming up. Final decision time?",
                options: [
                    {
                        text: "Full-time offer with mentorship",
                        next: "offer_with_mentor",
                        score: 10,
                        feedback: "Excellent: Set up for success"
                    },
                    {
                        text: "Extend contract 3 more months",
                        next: "extend_contract",
                        score: 6,
                        feedback: "Unfair: They've proven themselves"
                    },
                    {
                        text: "Pass - still too risky",
                        next: "final_pass",
                        score: 4,
                        feedback: "Overly cautious"
                    }
                ]
            },
            offer_with_mentor: {
                text: "SUCCESS: 1 year later - Now tech lead, mentoring juniors, team performance up 40%. Still direct but respectfully so. What lesson learned?",
                options: [
                    {
                        text: "Great talent can grow with support",
                        next: "final",
                        score: 10,
                        feedback: "Key insight: Growth mindset matters"
                    },
                    {
                        text: "Cultural add > cultural fit",
                        next: "final",
                        score: 9,
                        feedback: "Important: Diversity of styles valuable"
                    },
                    {
                        text: "Trust but verify works",
                        next: "final",
                        score: 8,
                        feedback: "Good: Structured evaluation"
                    }
                ]
            }
        }
    }
};

let currentScenario = null;
let currentNode = null;
let decisionPath = [];
let totalScore = 0;

document.addEventListener('DOMContentLoaded', function() {
    // Scenario button handlers
    document.querySelectorAll('.scenario-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const scenarioKey = this.dataset.scenario;
            startScenario(scenarioKey);
        });
    });
});

function startScenario(scenarioKey) {
    currentScenario = scenarios[scenarioKey];
    currentNode = 'start';
    decisionPath = [];
    totalScore = 0;
    
    document.querySelectorAll('.scenario-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.scenario === scenarioKey);
    });
    
    displayDecision();
    document.getElementById('analysis-panel').style.display = 'none';
}

function displayDecision() {
    const tree = document.getElementById('decision-tree');
    const decision = currentScenario.decisions[currentNode];
    
    if (!decision) {
        showFinalAnalysis();
        return;
    }
    
    let html = `
        <div class="decision-node">
            <h3>${currentScenario.title}</h3>
            <div class="situation">${decision.text}</div>
            <div class="options">
    `;
    
    decision.options.forEach((option, index) => {
        html += `
            <button class="option-btn" onclick="makeDecision('${option.next}', ${option.score}, '${option.text.replace(/'/g, "\\'")}', '${option.feedback.replace(/'/g, "\\'")}')">
                ${String.fromCharCode(65 + index)}. ${option.text}
            </button>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    tree.innerHTML = html;
}

function makeDecision(next, score, choice, feedback) {
    decisionPath.push({
        node: currentNode,
        choice: choice,
        score: score,
        feedback: feedback
    });
    
    totalScore += score;
    currentNode = next;
    
    // Show immediate feedback
    showImmediateFeedback(feedback, score);
    
    // Continue or end
    if (next === 'final') {
        showFinalAnalysis();
    } else {
        setTimeout(() => displayDecision(), 1500);
    }
}

function showImmediateFeedback(feedback, score) {
    const tree = document.getElementById('decision-tree');
    const feedbackHtml = `
        <div class="immediate-feedback ${score >= 8 ? 'good' : score >= 5 ? 'ok' : 'poor'}">
            <div class="score">Score: ${score}/10</div>
            <div class="feedback">${feedback}</div>
        </div>
    `;
    
    tree.insertAdjacentHTML('beforeend', feedbackHtml);
}

function showFinalAnalysis() {
    const analysisPanel = document.getElementById('analysis-panel');
    const pathDiv = document.getElementById('decision-path');
    const outcomeDiv = document.getElementById('outcome-analysis');
    const altDiv = document.getElementById('alternatives');
    
    // Show decision path
    let pathHtml = '<ol>';
    decisionPath.forEach(decision => {
        pathHtml += `
            <li>
                <strong>${decision.choice}</strong><br>
                <span class="path-feedback">${decision.feedback} (${decision.score}/10)</span>
            </li>
        `;
    });
    pathHtml += '</ol>';
    pathDiv.innerHTML = pathHtml;
    
    // Calculate average score
    const avgScore = totalScore / decisionPath.length;
    let outcome = '';
    
    if (avgScore >= 8) {
        outcome = '<div class="outcome excellent">🌟 Excellent Leadership! You navigated the situation with wisdom and empathy.</div>';
    } else if (avgScore >= 6) {
        outcome = '<div class="outcome good">✅ Good Decisions! Some room for improvement in certain areas.</div>';
    } else {
        outcome = '<div class="outcome poor">⚠️ Learning Opportunity! Review alternative approaches below.</div>';
    }
    
    outcome += `<div class="final-score">Average Score: ${avgScore.toFixed(1)}/10</div>`;
    outcomeDiv.innerHTML = outcome;
    
    // Show alternatives
    altDiv.innerHTML = `
        <ul>
            <li><strong>Key Learning</strong>: ${getKeyLearning(currentScenario.title, avgScore)}</li>
            <li><strong>Alternative Approach</strong>: ${getAlternativeApproach(currentScenario.title)}</li>
            <li><strong>Real-World Tip</strong>: ${getRealWorldTip(currentScenario.title)}</li>
        </ul>
    `;
    
    analysisPanel.style.display = 'block';
    document.getElementById('decision-tree').scrollIntoView({ behavior: 'smooth' });
}

function getKeyLearning(scenario, score) {
    const learnings = {
        "Managing an Underperformer": score >= 8 ? 
            "You balanced empathy with accountability perfectly. People issues often have personal roots." :
            "Remember to explore root causes before jumping to performance management.",
        "Team Conflict Resolution": score >= 8 ?
            "You understood that conflict is about respect, not just technical disagreement." :
            "Focus on communication patterns and mutual respect, not determining who's 'right'.",
        "Organizational Restructure": score >= 8 ?
            "Transparency and involvement are key to successful change management." :
            "People need to be part of the solution, not have change done to them.",
        "Production Crisis Management": score >= 8 ?
            "You delegated effectively while managing stakeholders. Perfect crisis leadership." :
            "Remember: delegate incident command, manage communications, support the team.",
        "Difficult Hiring Decision": score >= 8 ?
            "You found a way to assess fit while giving talented people a chance to grow." :
            "Culture fit matters, but so does cultural add. Look for growth potential."
    };
    
    return learnings[scenario] || "Every leadership situation is a learning opportunity.";
}

function getAlternativeApproach(scenario) {
    const alternatives = {
        "Managing an Underperformer": "Consider a 'support first, accountability second' approach with clear timelines.",
        "Team Conflict Resolution": "Try 'appreciative inquiry' - focus on when they work well together.",
        "Organizational Restructure": "Use 'open space technology' for self-organizing teams.",
        "Production Crisis Management": "Implement 'incident command system' with clear role separation.",
        "Difficult Hiring Decision": "Use 'working interview' or pair programming to see real collaboration."
    };
    
    return alternatives[scenario] || "There's always another way to approach leadership challenges.";
}

function getRealWorldTip(scenario) {
    const tips = {
        "Managing an Underperformer": "Document everything, but lead with humanity. HR is your partner, not first resort.",
        "Team Conflict Resolution": "The goal isn't to make them friends, but to work professionally together.",
        "Organizational Restructure": "Over-communicate by 10x. People can handle change, not uncertainty.",
        "Production Crisis Management": "Your calm is contagious. If you panic, everyone panics.",
        "Difficult Hiring Decision": "A bad hire costs 3x their salary. But fear of bad hires can cost you great people."
    };
    
    return tips[scenario] || "Real leadership is learned through experience and reflection.";
}

function restartScenario() {
    if (currentScenario) {
        currentNode = 'start';
        decisionPath = [];
        totalScore = 0;
        displayDecision();
        document.getElementById('analysis-panel').style.display = 'none';
    }
}

// Track progress
function saveProgress() {
    const progress = {
        scenarios: {}
    };
    
    // Save completion status for each scenario
    Object.keys(scenarios).forEach(key => {
        progress.scenarios[key] = {
            attempted: false,
            bestScore: 0,
            completions: 0
        };
    });
    
    localStorage.setItem('decision-tree-progress', JSON.stringify(progress));
}
</script>

<style>
.decision-tree-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
}

.scenario-selector {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 30px;
}

.scenario-btn {
    padding: 12px 20px;
    border: 2px solid #5448C8;
    background: white;
    color: #5448C8;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 600;
}

.scenario-btn:hover,
.scenario-btn.active {
    background: #5448C8;
    color: white;
}

.tree-container {
    min-height: 400px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 12px;
    margin-bottom: 30px;
}

.decision-node {
    animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.situation {
    font-size: 18px;
    line-height: 1.6;
    margin: 20px 0;
    padding: 20px;
    background: white;
    border-radius: 8px;
    border-left: 4px solid #5448C8;
}

.options {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-top: 20px;
}

.option-btn {
    text-align: left;
    padding: 16px 20px;
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 16px;
}

.option-btn:hover {
    border-color: #5448C8;
    background: #f8f7ff;
    transform: translateX(5px);
}

.immediate-feedback {
    margin-top: 20px;
    padding: 15px;
    border-radius: 8px;
    animation: slideIn 0.5s ease;
}

@keyframes slideIn {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

.immediate-feedback.good {
    background: #E8F5E9;
    border-left: 4px solid #4CAF50;
}

.immediate-feedback.ok {
    background: #FFF3E0;
    border-left: 4px solid #FFC107;
}

.immediate-feedback.poor {
    background: #FFEBEE;
    border-left: 4px solid #F44336;
}

.score {
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 8px;
}

.analysis-panel {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.analysis-panel h3 {
    color: #5448C8;
    margin-bottom: 15px;
}

#decision-path ol {
    padding-left: 20px;
}

#decision-path li {
    margin-bottom: 15px;
}

.path-feedback {
    color: #666;
    font-size: 14px;
}

.outcome {
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 18px;
}

.outcome.excellent {
    background: #E8F5E9;
    color: #2E7D32;
}

.outcome.good {
    background: #FFF3E0;
    color: #E65100;
}

.outcome.poor {
    background: #FFEBEE;
    color: #C62828;
}

.final-score {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    margin-top: 20px;
    color: #5448C8;
}

.restart-btn {
    display: block;
    margin: 20px auto;
    padding: 12px 30px;
    background: #5448C8;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    font-weight: 600;
}

.restart-btn:hover {
    background: #4339A5;
}

/* Responsive design */
@media (max-width: 600px) {
    .scenario-selector {
        flex-direction: column;
    }
    
    .option-btn {
        font-size: 14px;
        padding: 12px 16px;
    }
    
    .situation {
        font-size: 16px;
    }
}
</style>

---

**Pro Tip**: The best leaders make decisions with incomplete information. These scenarios help you practice judgment calls and learn from different approaches. There's rarely one "perfect" answer.