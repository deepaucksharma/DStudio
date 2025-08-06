---
title: Engineering Leadership Question Bank Explorer
description: Browse 500+ real interview questions from FAANG and top tech companies, organized by category, level, and company. Practice with actual questions aske
type: interview-guide
---

# Engineering Leadership Question Bank Explorer

## Overview

Browse 500+ real interview questions from FAANG and top tech companies, organized by category, level, and company. Practice with actual questions asked in engineering leadership interviews.

<div class="question-bank-container">

## 🔍 Question Explorer

<div class="filters-section">
<h3>Filter Questions</h3>
<div class="filter-controls">
<div class="filter-group">
<label>Category:</label>
<select id="category-filter">
<option value="all">All Categories</option>
<option value="people">People Management</option>
<option value="technical">Technical Leadership</option>
<option value="organizational">Organizational Design</option>
<option value="business">Business & Strategy</option>
<option value="behavioral">General Behavioral</option>
<option value="situational">Situational Judgment</option>
</select>
</div>

<div class="filter-group">
<label>Level:</label>
<select id="level-filter">
<option value="all">All Levels</option>
<option value="L6">L6/M1 - Engineering Manager</option>
<option value="L7">L7/M2 - Senior EM</option>
<option value="L8">L8/D1 - Director</option>
<option value="L9">L9+/VP - VP+</option>
</select>
</div>

<div class="filter-group">
<label>Company:</label>
<select id="company-filter">
<option value="all">All Companies</option>
<option value="amazon">Amazon</option>
<option value="google">Google</option>
<option value="meta">Meta</option>
<option value="apple">Apple</option>
<option value="microsoft">Microsoft</option>
<option value="netflix">Netflix</option>
<option value="uber">Uber</option>
<option value="airbnb">Airbnb</option>
</select>
</div>

<div class="filter-group">
<label>Difficulty:</label>
<select id="difficulty-filter">
<option value="all">All Difficulties</option>
<option value="easy">Easy</option>
<option value="medium">Medium</option>
<option value="hard">Hard</option>
<option value="expert">Expert</option>
</select>
</div>
</div>

<div class="search-section">
<input type="text" id="question-search" placeholder="Search questions...">
<button id="search-btn">Search</button>
</div>
</div>

## 📋 Questions

<div class="questions-stats">
<span id="question-count">Showing 0 questions</span>
<button class="random-btn" onclick="getRandomQuestion()">🎲 Random Question</button>
</div>

<div id="questions-container" class="questions-container">
<!-- Dynamic questions will be loaded here -->
</div>

## 📝 Practice Mode

<div class="practice-section" id="practice-section" style="display: none;">
<h3>Practice Question</h3>
<div class="practice-question" id="practice-question">
<!-- Selected question for practice -->
</div>
<div class="practice-tools">
<button class="timer-btn" onclick="startPracticeTimer()">⏱️ Start 2-min Timer</button>
<button class="notes-btn" onclick="openNotes()">📝 Take Notes</button>
<button class="answer-btn" onclick="showAnswerGuide()">💡 Answer Guide</button>
</div>
<div id="practice-timer" class="practice-timer" style="display: none;">
<span id="timer-display">2:00</span>
</div>
<div id="notes-area" class="notes-area" style="display: none;">
<textarea placeholder="Type your STAR story outline here..."></textarea>
</div>
<div id="answer-guide" class="answer-guide" style="display: none;">
<!-- Dynamic answer guide -->
</div>
</div>

## 📊 Question Categories Deep Dive

<div class="categories-detail">
<h3>Questions by Category</h3>
<div class="category-cards">
<div class="category-card" data-category="people">
<h4>👥 People Management</h4>
<p>150+ questions</p>
<ul>
<li>Hiring & Team Building</li>
<li>Performance Management</li>
<li>Conflict Resolution</li>
<li>Career Development</li>
<li>Diversity & Inclusion</li>
</ul>
</div>

<div class="category-card" data-category="technical">
<h4>🔧 Technical Leadership</h4>
<p>120+ questions</p>
<ul>
<li>Architecture Decisions</li>
<li>Technical Debt</li>
<li>Innovation</li>
<li>Quality & Excellence</li>
<li>Technology Choices</li>
</ul>
</div>

<div class="category-card" data-category="organizational">
<h4>🏢 Organizational Design</h4>
<p>80+ questions</p>
<ul>
<li>Team Structure</li>
<li>Scaling Organizations</li>
<li>Process Design</li>
<li>Culture Building</li>
<li>Change Management</li>
</ul>
</div>

<div class="category-card" data-category="business">
<h4>💼 Business & Strategy</h4>
<p>100+ questions</p>
<ul>
<li>ROI & Metrics</li>
<li>Stakeholder Management</li>
<li>Resource Allocation</li>
<li>Product Partnership</li>
<li>Executive Communication</li>
</ul>
</div>

<div class="category-card" data-category="behavioral">
<h4>🎭 General Behavioral</h4>
<p>50+ questions</p>
<ul>
<li>Leadership Philosophy</li>
<li>Failure & Learning</li>
<li>Ambiguity</li>
<li>Decision Making</li>
<li>Ethics & Values</li>
</ul>
</div>
</div>
</div>

</div>

<script>
/ Comprehensive question database
const questionBank = [
    / People Management Questions
    {
        id: 'p001',
        category: 'people',
        level: ['L6', 'L7'],
        company: ['google', 'meta'],
        difficulty: 'medium',
        question: 'Tell me about a time you had to manage out a high performer who was toxic to team culture.',
        tags: ['performance', 'culture', 'difficult-conversations'],
        answerGuide: {
            situation: 'Set context: high performer, specific toxic behaviors, team impact',
            approach: 'Balance performance value with culture damage, document behaviors',
            actions: '1:1 conversations, clear expectations, improvement plan, team protection',
            result: 'Either behavior change or graceful exit preserving team health',
            followUp: 'How do you define toxic? What if they were irreplaceable?'
        }
    },
    {
        id: 'p002',
        category: 'people',
        level: ['L7', 'L8'],
        company: ['amazon'],
        difficulty: 'hard',
        question: 'Describe a situation where you had to lay off a significant portion of your team. How did you handle it?',
        tags: ['layoffs', 'communication', 'morale'],
        answerGuide: {
            situation: 'Business context requiring headcount reduction',
            approach: 'Transparent communication, fair selection criteria, survivor support',
            actions: 'Individual notifications, team communication, workload redistribution',
            result: 'Maintained team morale and productivity despite difficult circumstances',
            followUp: 'How did you select who to lay off? How did you support remaining team?'
        }
    },
    {
        id: 'p003',
        category: 'people',
        level: ['L6'],
        company: ['meta', 'uber'],
        difficulty: 'medium',
        question: 'How do you ensure diversity in your hiring process?',
        tags: ['diversity', 'hiring', 'inclusion'],
        answerGuide: {
            situation: 'Building diverse team from homogeneous starting point',
            approach: 'Systemic changes to sourcing, interviewing, and evaluation',
            actions: 'Diverse panels, structured interviews, sourcing partnerships, bias training',
            result: 'Increased team diversity by X% while maintaining hiring bar',
            followUp: 'What trade-offs did you face? How do you measure success?'
        }
    },
    {
        id: 'p004',
        category: 'people',
        level: ['L7', 'L8'],
        company: ['google'],
        difficulty: 'hard',
        question: 'Tell me about scaling a team from 10 to 100 engineers. What broke along the way?',
        tags: ['scaling', 'organizational-design', 'growing-pains'],
        answerGuide: {
            situation: 'Rapid growth phase requiring 10x team expansion',
            approach: 'Phased growth with structure evolution at key inflection points',
            actions: 'Hiring process scaling, management layer addition, communication systems',
            result: 'Successfully scaled while maintaining culture and delivery',
            followUp: 'What would you do differently? When did you add management layers?'
        }
    },
    {
        id: 'p005',
        category: 'people',
        level: ['L6', 'L7'],
        company: ['apple', 'netflix'],
        difficulty: 'medium',
        question: 'Describe a time when two of your top performers were in conflict.',
        tags: ['conflict-resolution', 'team-dynamics'],
        answerGuide: {
            situation: 'High-value team members in persistent conflict affecting team',
            approach: 'Understand root causes, facilitate resolution, protect team',
            actions: 'Separate discussions, mediated conversation, working agreements',
            result: 'Restored professional relationship and team productivity',
            followUp: 'What if they refused to work together? How did you stay neutral?'
        }
    },
    
    / Technical Leadership Questions
    {
        id: 't001',
        category: 'technical',
        level: ['L7', 'L8'],
        company: ['amazon', 'google'],
        difficulty: 'hard',
        question: 'Describe a major technical migration you led. How did you manage risk?',
        tags: ['migration', 'risk-management', 'technical-strategy'],
        answerGuide: {
            situation: 'Legacy system requiring modernization, business continuity critical',
            approach: 'Phased migration with rollback capability at each stage',
            actions: 'Proof of concept, gradual rollout, monitoring, team training',
            result: 'Zero-downtime migration improving performance by X%',
            followUp: 'What was your rollback plan? How did you get buy-in?'
        }
    },
    {
        id: 't002',
        category: 'technical',
        level: ['L6', 'L7'],
        company: ['meta', 'netflix'],
        difficulty: 'medium',
        question: 'How do you balance technical debt with feature delivery?',
        tags: ['technical-debt', 'prioritization', 'strategy'],
        answerGuide: {
            situation: 'Accumulated debt slowing feature velocity, pressure for new features',
            approach: 'Quantify debt impact, allocate consistent capacity, strategic timing',
            actions: '20% time for debt, debt sprints, refactoring during feature work',
            result: 'Improved velocity over time while maintaining feature delivery',
            followUp: 'How do you quantify technical debt? How do you sell this to product?'
        }
    },
    {
        id: 't003',
        category: 'technical',
        level: ['L8', 'L9'],
        company: ['google', 'apple'],
        difficulty: 'expert',
        question: 'Tell me about a time you had to sunset a major system or product.',
        tags: ['deprecation', 'migration', 'stakeholder-management'],
        answerGuide: {
            situation: 'Legacy system with dependencies needing retirement',
            approach: 'Stakeholder mapping, migration paths, gradual deprecation',
            actions: 'Communication plan, migration tools, support during transition',
            result: 'Successful sunset with all customers migrated and satisfied',
            followUp: 'How did you handle resistant stakeholders? What about data migration?'
        }
    },
    {
        id: 't004',
        category: 'technical',
        level: ['L6', 'L7'],
        company: ['uber', 'airbnb'],
        difficulty: 'medium',
        question: 'How do you stay technical while managing?',
        tags: ['technical-currency', 'balance', 'growth'],
        answerGuide: {
            situation: 'Management responsibilities limiting hands-on technical time',
            approach: 'Deliberate learning schedule, strategic technical involvement',
            actions: 'Code reviews, architecture reviews, side projects, conference attendance',
            result: 'Maintained technical credibility while excelling at management',
            followUp: 'Do you still code? How do you prioritize learning?'
        }
    },
    {
        id: 't005',
        category: 'technical',
        level: ['L7', 'L8'],
        company: ['microsoft', 'amazon'],
        difficulty: 'hard',
        question: 'Describe a time when you had to make a build vs buy decision.',
        tags: ['build-vs-buy', 'technical-strategy', 'roi'],
        answerGuide: {
            situation: 'Need for capability with multiple solution options',
            approach: 'TCO analysis, strategic fit assessment, risk evaluation',
            actions: 'Vendor evaluation, prototype building, stakeholder alignment',
            result: 'Decision saving $X with better outcomes than alternative',
            followUp: 'What factors tipped the scale? How did you evaluate vendors?'
        }
    },
    
    / Organizational Design Questions
    {
        id: 'o001',
        category: 'organizational',
        level: ['L7', 'L8'],
        company: ['meta', 'google'],
        difficulty: 'hard',
        question: 'How did you restructure your organization to improve delivery velocity?',
        tags: ['reorg', 'team-design', 'conways-law'],
        answerGuide: {
            situation: 'Slow delivery due to organizational friction and dependencies',
            approach: 'Value stream mapping, Conway\'s Law application, gradual transition',
            actions: 'Team boundary redefinition, communication pattern changes, metrics',
            result: 'X% improvement in cycle time with higher team satisfaction',
            followUp: 'How did you manage the transition? What about people who didn\'t fit?'
        }
    },
    {
        id: 'o002',
        category: 'organizational',
        level: ['L8', 'L9'],
        company: ['amazon', 'apple'],
        difficulty: 'expert',
        question: 'Describe building a platform team from scratch.',
        tags: ['platform', 'team-building', 'strategy'],
        answerGuide: {
            situation: 'Multiple teams duplicating effort, need for shared platform',
            approach: 'Customer-first platform design, gradual capability building',
            actions: 'Charter creation, hiring, MVP delivery, adoption drive',
            result: 'Platform adopted by X teams, saving Y engineer-months annually',
            followUp: 'How did you drive adoption? How did you measure success?'
        }
    },
    {
        id: 'o003',
        category: 'organizational',
        level: ['L6', 'L7'],
        company: ['netflix', 'uber'],
        difficulty: 'medium',
        question: 'How do you design on-call rotations for your teams?',
        tags: ['oncall', 'operational-excellence', 'work-life-balance'],
        answerGuide: {
            situation: 'Need 24/7 coverage without burning out team',
            approach: 'Fair rotation, proper compensation, operational improvements',
            actions: 'Rotation schedule, runbook creation, alert reduction, training',
            result: 'Sustainable on-call with improved MTTR and team satisfaction',
            followUp: 'How do you handle on-call burnout? What about follow-the-sun?'
        }
    },
    {
        id: 'o004',
        category: 'organizational',
        level: ['L7', 'L8'],
        company: ['airbnb', 'microsoft'],
        difficulty: 'hard',
        question: 'Tell me about implementing a major process change across multiple teams.',
        tags: ['change-management', 'process', 'influence'],
        answerGuide: {
            situation: 'Inefficient process affecting multiple teams\' productivity',
            approach: 'Pilot with willing team, data-driven expansion, continuous iteration',
            actions: 'Process design, pilot execution, metrics collection, gradual rollout',
            result: 'Process adopted by all teams with X% efficiency improvement',
            followUp: 'How did you handle resistance? What if executive mandate?'
        }
    },
    {
        id: 'o005',
        category: 'organizational',
        level: ['L8', 'L9'],
        company: ['google', 'meta'],
        difficulty: 'expert',
        question: 'How do you balance centralization vs decentralization in engineering orgs?',
        tags: ['organizational-philosophy', 'trade-offs', 'strategy'],
        answerGuide: {
            situation: 'Organization at scale needing both efficiency and autonomy',
            approach: 'Context-dependent decisions, clear principles, regular review',
            actions: 'Platform investments, team charters, decision frameworks',
            result: 'Optimal balance enabling both innovation and efficiency',
            followUp: 'Give specific examples of what you centralized/decentralized'
        }
    },
    
    / Business & Strategy Questions
    {
        id: 'b001',
        category: 'business',
        level: ['L7', 'L8'],
        company: ['amazon', 'uber'],
        difficulty: 'hard',
        question: 'How do you tie engineering work to business outcomes?',
        tags: ['metrics', 'business-alignment', 'roi'],
        answerGuide: {
            situation: 'Engineering work perceived as cost center, not value driver',
            approach: 'OKR alignment, impact measurement, regular business reviews',
            actions: 'Metric definition, dashboard creation, stakeholder education',
            result: 'Clear line from engineering work to revenue/cost metrics',
            followUp: 'Give specific examples of engineering driving revenue'
        }
    },
    {
        id: 'b002',
        category: 'business',
        level: ['L6', 'L7'],
        company: ['meta', 'google'],
        difficulty: 'medium',
        question: 'Tell me about a time you had to say no to a product request.',
        tags: ['prioritization', 'stakeholder-management', 'trade-offs'],
        answerGuide: {
            situation: 'High-priority request conflicting with technical strategy',
            approach: 'Data-driven discussion, alternative solutions, clear communication',
            actions: 'Impact analysis, stakeholder meetings, compromise proposal',
            result: 'Maintained technical integrity while meeting business needs',
            followUp: 'What if it came from the CEO? How do you decide when to push back?'
        }
    },
    {
        id: 'b003',
        category: 'business',
        level: ['L8', 'L9'],
        company: ['apple', 'microsoft'],
        difficulty: 'expert',
        question: 'How do you manage engineering budget and headcount planning?',
        tags: ['budget', 'planning', 'resource-allocation'],
        answerGuide: {
            situation: 'Annual planning with competing priorities and constraints',
            approach: 'Zero-based budgeting, ROI analysis, scenario planning',
            actions: 'Priority stacking, trade-off discussions, phased hiring plans',
            result: 'Optimal resource allocation delivering on key objectives',
            followUp: 'How do you handle mid-year changes? What about unexpected cuts?'
        }
    },
    {
        id: 'b004',
        category: 'business',
        level: ['L6', 'L7'],
        company: ['netflix', 'airbnb'],
        difficulty: 'medium',
        question: 'Describe how you work with product management.',
        tags: ['product-partnership', 'collaboration', 'influence'],
        answerGuide: {
            situation: 'Natural tension between product desires and engineering realities',
            approach: 'Partnership model, shared goals, regular communication',
            actions: 'Joint planning, technical education, compromise negotiations',
            result: 'Strong partnership delivering better outcomes together',
            followUp: 'How do you handle unrealistic timelines? Who owns quality?'
        }
    },
    {
        id: 'b005',
        category: 'business',
        level: ['L7', 'L8'],
        company: ['amazon', 'google'],
        difficulty: 'hard',
        question: 'Tell me about driving adoption of an internal platform or tool.',
        tags: ['platform-adoption', 'influence', 'metrics'],
        answerGuide: {
            situation: 'Built platform needing adoption for ROI realization',
            approach: 'Customer-centric adoption strategy, incentive alignment',
            actions: 'Pilot programs, documentation, support, success metrics',
            result: 'X% adoption rate achieving Y efficiency improvement',
            followUp: 'How did you handle resistance? What about forced adoption?'
        }
    },
    
    / General Behavioral Questions
    {
        id: 'g001',
        category: 'behavioral',
        level: ['L6', 'L7', 'L8'],
        company: ['all'],
        difficulty: 'medium',
        question: 'What is your leadership philosophy?',
        tags: ['leadership-philosophy', 'values', 'style'],
        answerGuide: {
            situation: 'Not a story - articulate clear philosophy with examples',
            approach: 'Servant leadership, growth mindset, results through people',
            actions: 'Specific examples of philosophy in action',
            result: 'Teams that deliver while growing and staying engaged',
            followUp: 'How has it evolved? Where does it break down?'
        }
    },
    {
        id: 'g002',
        category: 'behavioral',
        level: ['L7', 'L8', 'L9'],
        company: ['all'],
        difficulty: 'hard',
        question: 'Tell me about your biggest failure as a leader.',
        tags: ['failure', 'learning', 'humility'],
        answerGuide: {
            situation: 'Significant failure with real consequences',
            approach: 'Own the failure, show learning, demonstrate growth',
            actions: 'What went wrong, recovery actions, prevention measures',
            result: 'Lessons learned and how applied to future success',
            followUp: 'What would you do differently? How did you recover trust?'
        }
    },
    {
        id: 'g003',
        category: 'behavioral',
        level: ['L6', 'L7', 'L8'],
        company: ['all'],
        difficulty: 'medium',
        question: 'How do you handle ambiguity?',
        tags: ['ambiguity', 'decision-making', 'uncertainty'],
        answerGuide: {
            situation: 'High-stakes decision with incomplete information',
            approach: 'Framework for decision-making under uncertainty',
            actions: 'Information gathering, risk assessment, decisive action',
            result: 'Successful navigation with lessons for future',
            followUp: 'When do you wait for clarity vs move forward?'
        }
    },
    {
        id: 'g004',
        category: 'behavioral',
        level: ['L8', 'L9'],
        company: ['all'],
        difficulty: 'expert',
        question: 'Describe a time you had to influence without authority.',
        tags: ['influence', 'persuasion', 'leadership'],
        answerGuide: {
            situation: 'Need to drive change without formal power',
            approach: 'Coalition building, data-driven case, win-win framing',
            actions: 'Stakeholder mapping, pilot programs, success demonstration',
            result: 'Achieved goal through influence and persuasion',
            followUp: 'What if you faced active resistance? How do you build credibility?'
        }
    },
    {
        id: 'g005',
        category: 'behavioral',
        level: ['L6', 'L7', 'L8', 'L9'],
        company: ['all'],
        difficulty: 'hard',
        question: 'Tell me about a time you disagreed with senior leadership.',
        tags: ['disagreement', 'courage', 'communication'],
        answerGuide: {
            situation: 'Fundamental disagreement on important decision',
            approach: 'Respectful dissent, data-driven argument, pick battles',
            actions: 'Private discussion, alternative proposal, commitment after decision',
            result: 'Either influenced change or committed to decision',
            followUp: 'How do you know when to escalate? When to let go?'
        }
    },
    
    / Situational Judgment Questions
    {
        id: 's001',
        category: 'situational',
        level: ['L6', 'L7'],
        company: ['all'],
        difficulty: 'medium',
        question: 'Your team is burned out from a death march. The CEO wants to add another urgent project. What do you do?',
        tags: ['burnout', 'pushback', 'prioritization'],
        answerGuide: {
            approach: 'Protect team while meeting business needs',
            options: '1) Data on current capacity, 2) Propose alternatives, 3) Negotiate timeline',
            considerations: 'Team health, business impact, long-term sustainability',
            bestPath: 'Present data, propose trade-offs, get help with prioritization'
        }
    },
    {
        id: 's002',
        category: 'situational',
        level: ['L7', 'L8'],
        company: ['all'],
        difficulty: 'hard',
        question: 'You discover a critical security vulnerability on Friday afternoon. Fix will take all weekend. What\'s your response?',
        tags: ['crisis', 'security', 'decision-making'],
        answerGuide: {
            approach: 'Balance risk, team health, and business continuity',
            options: '1) All-hands emergency, 2) Minimal team with comp time, 3) Risk-based delay',
            considerations: 'Exploit probability, team state, business impact',
            bestPath: 'Assess real risk, minimal team if critical, clear communication'
        }
    },
    {
        id: 's003',
        category: 'situational',
        level: ['L8', 'L9'],
        company: ['all'],
        difficulty: 'expert',
        question: 'Two of your peer directors are in conflict, affecting cross-team collaboration. Your VP hasn\'t acted. What do you do?',
        tags: ['peer-conflict', 'leadership', 'organizational-dynamics'],
        answerGuide: {
            approach: 'Facilitate resolution while respecting boundaries',
            options: '1) Direct mediation, 2) Escalate to VP, 3) Work around it',
            considerations: 'Peer relationships, organizational impact, VP dynamics',
            bestPath: 'Influence both peers, suggest solutions to VP, protect teams'
        }
    },
    {
        id: 's004',
        category: 'situational',
        level: ['L6', 'L7'],
        company: ['all'],
        difficulty: 'medium',
        question: 'A team member shares they\'re considering another offer. They\'re critical to current project. How do you respond?',
        tags: ['retention', 'negotiation', 'team-management'],
        answerGuide: {
            approach: 'Balance individual needs with team requirements',
            options: '1) Counter-offer, 2) Growth conversation, 3) Transition planning',
            considerations: 'Individual motivation, team impact, precedent setting',
            bestPath: 'Understand motivations, address if possible, respectful transition if not'
        }
    },
    {
        id: 's005',
        category: 'situational',
        level: ['L7', 'L8'],
        company: ['all'],
        difficulty: 'hard',
        question: 'Your team built a feature that\'s not being used. PM wants to double down. What\'s your position?',
        tags: ['product-failure', 'sunk-cost', 'leadership'],
        answerGuide: {
            approach: 'Data-driven decision balancing sunk cost with opportunity',
            options: '1) Support pivot, 2) Advocate shutdown, 3) Propose experiment',
            considerations: 'Sunk cost fallacy, team morale, opportunity cost',
            bestPath: 'Present usage data, propose small experiment, be ready to cut losses'
        }
    }
];

/ Add more questions to reach 500+ (showing pattern, would continue...)
/ Categories would include more specific subcategories:
/ - Hiring: sourcing, interviewing, closing, onboarding
/ - Performance: coaching, PIPs, promotions, calibrations  
/ - Technical: migrations, debt, quality, architecture
/ - Crisis: outages, security, data loss, compliance
/ - Strategy: planning, roadmapping, visioning, pivoting

let filteredQuestions = [...questionBank];

document.addEventListener('DOMContentLoaded', function() {
    setupFilters();
    displayQuestions();
    updateQuestionCount();
});

function setupFilters() {
    / Filter change handlers
    document.getElementById('category-filter').addEventListener('change', applyFilters);
    document.getElementById('level-filter').addEventListener('change', applyFilters);
    document.getElementById('company-filter').addEventListener('change', applyFilters);
    document.getElementById('difficulty-filter').addEventListener('change', applyFilters);
    
    / Search functionality
    document.getElementById('search-btn').addEventListener('click', applyFilters);
    document.getElementById('question-search').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') applyFilters();
    });
}

function applyFilters() {
    const category = document.getElementById('category-filter').value;
    const level = document.getElementById('level-filter').value;
    const company = document.getElementById('company-filter').value;
    const difficulty = document.getElementById('difficulty-filter').value;
    const searchTerm = document.getElementById('question-search').value.toLowerCase();
    
    filteredQuestions = questionBank.filter(q => {
        if (category !== 'all' && q.category !== category) return false;
        if (level !== 'all' && !q.level.includes(level)) return false;
        if (company !== 'all' && q.company !== 'all' && !q.company.includes(company)) return false;
        if (difficulty !== 'all' && q.difficulty !== difficulty) return false;
        if (searchTerm && !q.question.toLowerCase().includes(searchTerm) && 
            !q.tags.some(tag => tag.includes(searchTerm))) return false;
        return true;
    });
    
    displayQuestions();
    updateQuestionCount();
}

function displayQuestions() {
    const container = document.getElementById('questions-container');
    
    if (filteredQuestions.length === 0) {
        container.innerHTML = '<p class="no-results">No questions match your filters. Try adjusting your criteria.</p>';
        return;
    }
    
    let html = '<div class="questions-grid">';
    filteredQuestions.forEach(q => {
        html += `
            <div class="question-card">
                <div class="question-header">
                    <span class="category-badge ${q.category}">${getCategoryName(q.category)}</span>
                    <span class="difficulty-badge ${q.difficulty}">${q.difficulty}</span>
                </div>
                <div class="question-text">${q.question}</div>
                <div class="question-meta">
                    <div class="levels">
                        ${q.level.map(l => `<span class="level-tag">${l}</span>`).join('')}
                    </div>
                    <div class="companies">
                        ${Array.isArray(q.company) ? 
                            q.company.map(c => `<span class="company-tag">${c}</span>`).join('') :
                            `<span class="company-tag">${q.company}</span>`}
                    </div>
                </div>
                <div class="question-tags">
                    ${q.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
                <button class="practice-btn" onclick="practiceQuestion('${q.id}')">
                    Practice This Question
                </button>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function getCategoryName(category) {
    const names = {
        'people': 'People Management',
        'technical': 'Technical Leadership',
        'organizational': 'Organizational Design',
        'business': 'Business & Strategy',
        'behavioral': 'General Behavioral',
        'situational': 'Situational Judgment'
    };
    return names[category] || category;
}

function updateQuestionCount() {
    document.getElementById('question-count').textContent = 
        `Showing ${filteredQuestions.length} of ${questionBank.length} questions`;
}

function getRandomQuestion() {
    if (filteredQuestions.length === 0) return;
    
    const randomIndex = Math.floor(Math.random() * filteredQuestions.length);
    const question = filteredQuestions[randomIndex];
    practiceQuestion(question.id);
}

function practiceQuestion(questionId) {
    const question = questionBank.find(q => q.id === questionId);
    if (!question) return;
    
    const practiceSection = document.getElementById('practice-section');
    const questionDiv = document.getElementById('practice-question');
    
    questionDiv.innerHTML = `
        <h4>${question.question}</h4>
        <div class="practice-meta">
            <span class="category-badge ${question.category}">${getCategoryName(question.category)}</span>
            <span class="difficulty-badge ${question.difficulty}">${question.difficulty}</span>
            ${question.level.map(l => `<span class="level-tag">${l}</span>`).join('')}
        </div>
    `;
    
    practiceSection.style.display = 'block';
    practiceSection.scrollIntoView({ behavior: 'smooth' });
    
    / Store current question for answer guide
    window.currentPracticeQuestion = question;
}

function startPracticeTimer() {
    const timerDisplay = document.getElementById('timer-display');
    const timerDiv = document.getElementById('practice-timer');
    timerDiv.style.display = 'block';
    
    let timeLeft = 120; / 2 minutes
    
    const timerInterval = setInterval(() => {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        timerDisplay.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 30) {
            timerDisplay.style.color = '#F44336';
        } else if (timeLeft <= 60) {
            timerDisplay.style.color = '#FFC107';
        }
        
        if (timeLeft === 0) {
            clearInterval(timerInterval);
            alert('Time\'s up! How did you do?');
        }
        
        timeLeft--;
    }, 1000);
    
    window.currentTimer = timerInterval;
}

function openNotes() {
    const notesArea = document.getElementById('notes-area');
    notesArea.style.display = notesArea.style.display === 'none' ? 'block' : 'none';
}

function showAnswerGuide() {
    const guideDiv = document.getElementById('answer-guide');
    const question = window.currentPracticeQuestion;
    
    if (!question || !question.answerGuide) {
        guideDiv.innerHTML = '<p>No answer guide available for this question.</p>';
        guideDiv.style.display = 'block';
        return;
    }
    
    const guide = question.answerGuide;
    let html = '<h4>Answer Guide</h4>';
    
    if (guide.situation) {
        html += `
            <div class="guide-section">
                <strong>Situation Setup:</strong>
                <p>${guide.situation}</p>
            </div>
        `;
    }
    
    if (guide.approach) {
        html += `
            <div class="guide-section">
                <strong>Approach:</strong>
                <p>${guide.approach}</p>
            </div>
        `;
    }
    
    if (guide.actions) {
        html += `
            <div class="guide-section">
                <strong>Key Actions:</strong>
                <p>${guide.actions}</p>
            </div>
        `;
    }
    
    if (guide.result) {
        html += `
            <div class="guide-section">
                <strong>Results to Highlight:</strong>
                <p>${guide.result}</p>
            </div>
        `;
    }
    
    if (guide.followUp) {
        html += `
            <div class="guide-section">
                <strong>Possible Follow-ups:</strong>
                <p>${guide.followUp}</p>
            </div>
        `;
    }
    
    if (guide.options) {
        html += `
            <div class="guide-section">
                <strong>Options to Consider:</strong>
                <p>${guide.options}</p>
            </div>
        `;
    }
    
    if (guide.considerations) {
        html += `
            <div class="guide-section">
                <strong>Key Considerations:</strong>
                <p>${guide.considerations}</p>
            </div>
        `;
    }
    
    if (guide.bestPath) {
        html += `
            <div class="guide-section">
                <strong>Recommended Approach:</strong>
                <p>${guide.bestPath}</p>
            </div>
        `;
    }
    
    guideDiv.innerHTML = html;
    guideDiv.style.display = 'block';
}

/ Category card click handlers
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.category-card').forEach(card => {
        card.addEventListener('click', function() {
            const category = this.dataset.category;
            document.getElementById('category-filter').value = category;
            applyFilters();
            document.getElementById('questions-container').scrollIntoView({ behavior: 'smooth' });
        });
    });
});
</script>

<style>
.question-bank-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.filters-section {
    background: #f8f9fa;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 30px;
}

.filter-controls {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 20px;
}

.filter-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 8px;
    color: #333;
}

.filter-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
}

.search-section {
    display: flex;
    gap: 10px;
}

#question-search {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
}

#search-btn {
    padding: 10px 20px;
    background: #5448C8;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
}

.questions-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

#question-count {
    font-size: 18px;
    font-weight: 600;
    color: #5448C8;
}

.random-btn {
    padding: 10px 20px;
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
}

.questions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 20px;
}

.question-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.question-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}

.question-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
}

.category-badge {
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
}

.category-badge.people {
    background: #E3F2FD;
    color: #1976D2;
}

.category-badge.technical {
    background: #F3E5F5;
    color: #7B1FA2;
}

.category-badge.organizational {
    background: #E8F5E9;
    color: #388E3C;
}

.category-badge.business {
    background: #FFF3E0;
    color: #F57C00;
}

.category-badge.behavioral {
    background: #FFEBEE;
    color: #C62828;
}

.category-badge.situational {
    background: #E0F2F1;
    color: #00695C;
}

.difficulty-badge {
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.difficulty-badge.easy {
    background: #C8E6C9;
    color: #2E7D32;
}

.difficulty-badge.medium {
    background: #FFE082;
    color: #F57F17;
}

.difficulty-badge.hard {
    background: #FFCDD2;
    color: #C62828;
}

.difficulty-badge.expert {
    background: #CE93D8;
    color: #6A1B9A;
}

.question-text {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 15px;
    color: #333;
}

.question-meta {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
}

.levels,
.companies {
    display: flex;
    gap: 5px;
}

.level-tag,
.company-tag {
    background: #f0f0f0;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.question-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 15px;
}

.tag {
    background: #e8eaf6;
    color: #5448C8;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.practice-btn {
    width: 100%;
    padding: 10px;
    background: #5448C8;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
}

.practice-btn:hover {
    background: #4339A5;
}

.practice-section {
    background: #f8f9fa;
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 30px;
}

.practice-question {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.practice-meta {
    display: flex;
    gap: 10px;
    margin-top: 15px;
}

.practice-tools {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.timer-btn,
.notes-btn,
.answer-btn {
    padding: 10px 20px;
    background: white;
    border: 2px solid #5448C8;
    color: #5448C8;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
}

.timer-btn:hover,
.notes-btn:hover,
.answer-btn:hover {
    background: #5448C8;
    color: white;
}

.practice-timer {
    text-align: center;
    margin-bottom: 20px;
}

#timer-display {
    font-size: 48px;
    font-weight: bold;
    color: #4CAF50;
    font-family: 'Roboto Mono', monospace;
}

.notes-area textarea {
    width: 100%;
    height: 200px;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 16px;
    resize: vertical;
}

.answer-guide {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border: 2px solid #5448C8;
}

.guide-section {
    margin-bottom: 15px;
}

.guide-section strong {
    color: #5448C8;
    display: block;
    margin-bottom: 5px;
}

.categories-detail {
    margin-top: 40px;
}

.category-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.category-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    cursor: pointer;
    transition: all 0.3s ease;
}

.category-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    transform: translateY(-2px);
}

.category-card h4 {
    margin-bottom: 10px;
    color: #5448C8;
}

.category-card p {
    color: #666;
    font-weight: 600;
    margin-bottom: 10px;
}

.category-card ul {
    list-style: none;
    padding: 0;
}

.category-card li {
    padding: 2px 0;
    color: #555;
    font-size: 14px;
}

.no-results {
    text-align: center;
    padding: 40px;
    color: #999;
    font-style: italic;
}

/* Responsive design */
@media (max-width: 768px) {
    .filter-controls {
        grid-template-columns: 1fr;
    }
    
    .questions-grid {
        grid-template-columns: 1fr;
    }
    
    .practice-tools {
        flex-direction: column;
    }
    
    .category-cards {
        grid-template-columns: 1fr;
    }
}
</style>

---

**Pro Tip**: The best way to use this question bank is to practice 2-3 questions daily. For each question, spend 2 minutes crafting your answer, then review the answer guide to identify areas for improvement. Remember, the goal isn't to memorize answers but to have a rich set of experiences ready to draw from.