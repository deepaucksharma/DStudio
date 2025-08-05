---
title: STAR Story Matcher - Find Your Perfect Interview Stories
description: Match your experiences to common interview questions. This tool helps you identify which stories from your career best demonstrate specific leadership
type: interview-guide
---

# STAR Story Matcher - Find Your Perfect Interview Stories

## Overview

Match your experiences to common interview questions. This tool helps you identify which stories from your career best demonstrate specific leadership competencies.

<div class="star-matcher-container">

## 📝 Story Bank Builder

### Step 1: Add Your Stories
<div class="story-input-section">
<h4>New Story Entry</h4>
<form id="story-form">
<div class="form-group">
<label>Story Title:</label>
<input type="text" id="story-title" placeholder="e.g., Scaled team from 5 to 25 engineers">
</div>

<div class="form-group">
<label>Situation (Context):</label>
<textarea id="story-situation" rows="3" placeholder="What was the context? What challenge did you face?"></textarea>
</div>

<div class="form-group">
<label>Task (Your Role):</label>
<textarea id="story-task" rows="2" placeholder="What was your responsibility?"></textarea>
</div>

<div class="form-group">
<label>Action (What You Did):</label>
<textarea id="story-action" rows="4" placeholder="What specific steps did you take?"></textarea>
</div>

<div class="form-group">
<label>Result (Outcome):</label>
<textarea id="story-result" rows="3" placeholder="What was the measurable impact?"></textarea>
</div>

<div class="form-group">
<label>Key Competencies (select all that apply):</label>
<div class="competency-checkboxes">
<label><input type="checkbox" value="hiring"> Hiring & Team Building</label>
<label><input type="checkbox" value="performance"> Performance Management</label>
<label><input type="checkbox" value="conflict"> Conflict Resolution</label>
<label><input type="checkbox" value="technical"> Technical Leadership</label>
<label><input type="checkbox" value="strategy"> Strategic Thinking</label>
<label><input type="checkbox" value="change"> Change Management</label>
<label><input type="checkbox" value="influence"> Influence Without Authority</label>
<label><input type="checkbox" value="scale"> Scaling Teams/Systems</label>
<label><input type="checkbox" value="culture"> Culture Building</label>
<label><input type="checkbox" value="crisis"> Crisis Management</label>
<label><input type="checkbox" value="innovation"> Innovation</label>
<label><input type="checkbox" value="diversity"> Diversity & Inclusion</label>
<label><input type="checkbox" value="business"> Business Impact</label>
<label><input type="checkbox" value="failure"> Learning from Failure</label>
</div>
</div>

<div class="form-group">
<label>Impact Level:</label>
<select id="story-impact">
<option value="">Select...</option>
<option value="team">Team Level (5-15 people)</option>
<option value="org">Organization Level (20-50 people)</option>
<option value="division">Division Level (50-100 people)</option>
<option value="company">Company Level (100+ people)</option>
</select>
</div>

<button type="submit" class="add-story-btn">Add Story to Bank</button>
</form>
</div>

## 📚 Your Story Bank

<div id="story-bank" class="story-bank">
<p class="empty-state">No stories added yet. Add your first story above!</p>
</div>

## 🎯 Question Matcher

### Step 2: Find Matching Stories for Common Questions

<div class="question-matcher">
<h4>Select a Question Category:</h4>
<div class="category-tabs">
<button class="category-tab active" data-category="people">People Management</button>
<button class="category-tab" data-category="technical">Technical Leadership</button>
<button class="category-tab" data-category="business">Business & Strategy</button>
<button class="category-tab" data-category="leadership">General Leadership</button>
</div>

<div class="questions-list" id="questions-list">
<!-- Dynamic question list -->
</div>

<div class="matched-stories" id="matched-stories">
<h4>Matching Stories from Your Bank:</h4>
<div class="matches-container">
<p class="select-question">Select a question above to see matching stories</p>
</div>
</div>
</div>

## 📊 Coverage Analysis

<div class="coverage-analysis">
<h3>Your Story Coverage</h3>
<div class="coverage-grid" id="coverage-grid">
<!-- Dynamic coverage visualization -->
</div>
<div class="coverage-gaps" id="coverage-gaps">
<h4>Gap Analysis</h4>
<p>Add stories to see your coverage gaps</p>
</div>
</div>

</div>

## 💡 STAR+ Framework Reminder

### What Makes a Great Story?

#### Situation (20%)
- Specific context and constraints
- Business impact/urgency
- Team size and dynamics
- Timeline pressure

#### Task (10%)
- Your specific role
- Authority level
- Success criteria
- Stakeholders involved

#### Action (40%)
- **Specific steps** you took
- Decision-making process
- How you influenced others
- Trade-offs you considered
- Mistakes and course corrections

#### Result (20%)
- Quantifiable outcomes
- Business metrics improved
- Team/culture impact
- Lessons learned

#### + Scale & Impact (10%)
- Number of people affected
- Revenue/cost impact
- Long-term sustainability
- Broader organizational influence

## 🎯 Common Interview Questions by Category

### People Management
1. Tell me about a time you had to let someone go
2. How do you build high-performing teams?
3. Describe managing a difficult employee
4. How do you handle team conflicts?
5. Tell me about developing someone's career
6. How do you drive diversity & inclusion?
7. Describe scaling a team rapidly
8. How do you maintain culture during growth?

### Technical Leadership
1. Tell me about a major technical decision
2. How do you balance technical debt?
3. Describe leading a migration/transformation
4. How do you stay technical as a manager?
5. Tell me about a system failure you handled
6. How do you drive technical excellence?
7. Describe introducing new technology
8. How do you make build vs buy decisions?

### Business & Strategy
1. Tell me about driving business impact
2. How do you prioritize competing initiatives?
3. Describe influencing product strategy
4. How do you manage stakeholder expectations?
5. Tell me about a budget/resource decision
6. How do you measure engineering productivity?
7. Describe a cross-functional initiative
8. How do you communicate with executives?

### General Leadership
1. Tell me about your biggest failure
2. Describe a time you influenced without authority
3. How do you handle ambiguity?
4. Tell me about driving organizational change
5. Describe your leadership philosophy
6. How do you make decisions with incomplete info?
7. Tell me about a time you disagreed with leadership
8. How do you balance competing priorities?

## 🔄 Story Development Process

### Phase 1: Brain Dump
- List all major projects/initiatives
- Note team sizes and timelines
- Capture key metrics and outcomes

### Phase 2: Story Mining
- Look for inflection points
- Find conflict/resolution pairs
- Identify learning moments
- Highlight culture impacts

### Phase 3: Story Crafting
- Add specific details
- Quantify everything possible
- Include names (anonymized)
- Practice 2-minute versions

### Phase 4: Story Mapping
- Match to competencies
- Identify versatile stories
- Note follow-up angles
- Prepare deep-dive details

<script>
// Question database
const questionDatabase = {
    people: [
        { id: 'p1', question: 'Tell me about a time you had to let someone go', tags: ['performance', 'conflict'] },
        { id: 'p2', question: 'How do you build high-performing teams?', tags: ['hiring', 'culture', 'scale'] },
        { id: 'p3', question: 'Describe managing a difficult employee', tags: ['performance', 'conflict'] },
        { id: 'p4', question: 'How do you handle team conflicts?', tags: ['conflict', 'culture'] },
        { id: 'p5', question: 'Tell me about developing someone\'s career', tags: ['performance', 'culture'] },
        { id: 'p6', question: 'How do you drive diversity & inclusion?', tags: ['diversity', 'hiring', 'culture'] },
        { id: 'p7', question: 'Describe scaling a team rapidly', tags: ['scale', 'hiring', 'change'] },
        { id: 'p8', question: 'How do you maintain culture during growth?', tags: ['culture', 'scale', 'change'] }
    ],
    technical: [
        { id: 't1', question: 'Tell me about a major technical decision', tags: ['technical', 'strategy'] },
        { id: 't2', question: 'How do you balance technical debt?', tags: ['technical', 'strategy', 'business'] },
        { id: 't3', question: 'Describe leading a migration/transformation', tags: ['technical', 'change', 'scale'] },
        { id: 't4', question: 'How do you stay technical as a manager?', tags: ['technical', 'innovation'] },
        { id: 't5', question: 'Tell me about a system failure you handled', tags: ['crisis', 'technical'] },
        { id: 't6', question: 'How do you drive technical excellence?', tags: ['technical', 'culture'] },
        { id: 't7', question: 'Describe introducing new technology', tags: ['technical', 'innovation', 'change'] },
        { id: 't8', question: 'How do you make build vs buy decisions?', tags: ['technical', 'strategy', 'business'] }
    ],
    business: [
        { id: 'b1', question: 'Tell me about driving business impact', tags: ['business', 'strategy'] },
        { id: 'b2', question: 'How do you prioritize competing initiatives?', tags: ['strategy', 'business'] },
        { id: 'b3', question: 'Describe influencing product strategy', tags: ['influence', 'strategy', 'business'] },
        { id: 'b4', question: 'How do you manage stakeholder expectations?', tags: ['influence', 'business'] },
        { id: 'b5', question: 'Tell me about a budget/resource decision', tags: ['business', 'strategy'] },
        { id: 'b6', question: 'How do you measure engineering productivity?', tags: ['business', 'technical'] },
        { id: 'b7', question: 'Describe a cross-functional initiative', tags: ['influence', 'strategy'] },
        { id: 'b8', question: 'How do you communicate with executives?', tags: ['influence', 'business'] }
    ],
    leadership: [
        { id: 'l1', question: 'Tell me about your biggest failure', tags: ['failure'] },
        { id: 'l2', question: 'Describe a time you influenced without authority', tags: ['influence'] },
        { id: 'l3', question: 'How do you handle ambiguity?', tags: ['strategy', 'change'] },
        { id: 'l4', question: 'Tell me about driving organizational change', tags: ['change', 'influence', 'scale'] },
        { id: 'l5', question: 'Describe your leadership philosophy', tags: ['culture'] },
        { id: 'l6', question: 'How do you make decisions with incomplete info?', tags: ['strategy', 'crisis'] },
        { id: 'l7', question: 'Tell me about disagreeing with leadership', tags: ['influence', 'conflict'] },
        { id: 'l8', question: 'How do you balance competing priorities?', tags: ['strategy', 'business'] }
    ]
};

// Story bank storage
let storyBank = JSON.parse(localStorage.getItem('star-story-bank') || '[]');

document.addEventListener('DOMContentLoaded', function() {
    renderStoryBank();
    renderCoverageAnalysis();
    setupEventHandlers();
    
    // Load initial questions
    showQuestions('people');
});

function setupEventHandlers() {
    // Story form submission
    document.getElementById('story-form').addEventListener('submit', function(e) {
        e.preventDefault();
        addStory();
    });
    
    // Category tabs
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            showQuestions(this.dataset.category);
        });
    });
}

function addStory() {
    const story = {
        id: Date.now().toString(),
        title: document.getElementById('story-title').value,
        situation: document.getElementById('story-situation').value,
        task: document.getElementById('story-task').value,
        action: document.getElementById('story-action').value,
        result: document.getElementById('story-result').value,
        impact: document.getElementById('story-impact').value,
        competencies: Array.from(document.querySelectorAll('.competency-checkboxes input:checked'))
            .map(cb => cb.value),
        created: new Date().toISOString()
    };
    
    if (!story.title || !story.situation || !story.action || !story.result) {
        alert('Please fill in all required STAR fields');
        return;
    }
    
    if (story.competencies.length === 0) {
        alert('Please select at least one competency');
        return;
    }
    
    storyBank.push(story);
    localStorage.setItem('star-story-bank', JSON.stringify(storyBank));
    
    // Reset form
    document.getElementById('story-form').reset();
    
    // Update displays
    renderStoryBank();
    renderCoverageAnalysis();
    
    // Show success message
    showToast('Story added successfully!');
}

function renderStoryBank() {
    const container = document.getElementById('story-bank');
    
    if (storyBank.length === 0) {
        container.innerHTML = '<p class="empty-state">No stories added yet. Add your first story above!</p>';
        return;
    }
    
    let html = '<div class="story-cards">';
    storyBank.forEach(story => {
        html += `
            <div class="story-card" data-id="${story.id}">
                <div class="story-header">
                    <h4>${story.title}</h4>
                    <button class="delete-story" onclick="deleteStory('${story.id}')">×</button>
                </div>
                <div class="story-summary">
                    <strong>S:</strong> ${story.situation.substring(0, 100)}...<br>
                    <strong>T:</strong> ${story.task.substring(0, 50)}...<br>
                    <strong>A:</strong> ${story.action.substring(0, 100)}...<br>
                    <strong>R:</strong> ${story.result.substring(0, 100)}...
                </div>
                <div class="story-meta">
                    <span class="impact-badge ${story.impact}">${story.impact || 'Not specified'}</span>
                    <div class="competency-tags">
                        ${story.competencies.map(c => `<span class="tag">${c}</span>`).join('')}
                    </div>
                </div>
                <button class="expand-story" onclick="expandStory('${story.id}')">View Full Story</button>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function deleteStory(id) {
    if (confirm('Delete this story?')) {
        storyBank = storyBank.filter(s => s.id !== id);
        localStorage.setItem('star-story-bank', JSON.stringify(storyBank));
        renderStoryBank();
        renderCoverageAnalysis();
    }
}

function expandStory(id) {
    const story = storyBank.find(s => s.id === id);
    if (!story) return;
    
    // In real implementation, show modal with full story
    alert(`Full Story:\n\nSituation:\n${story.situation}\n\nTask:\n${story.task}\n\nAction:\n${story.action}\n\nResult:\n${story.result}`);
}

function showQuestions(category) {
    const container = document.getElementById('questions-list');
    const questions = questionDatabase[category];
    
    let html = '<div class="questions">';
    questions.forEach(q => {
        html += `
            <div class="question-item" onclick="matchStories('${q.id}', '${category}')">
                <p>${q.question}</p>
                <div class="question-tags">
                    ${q.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function matchStories(questionId, category) {
    const question = questionDatabase[category].find(q => q.id === questionId);
    if (!question) return;
    
    // Highlight selected question
    document.querySelectorAll('.question-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.currentTarget.classList.add('selected');
    
    // Find matching stories
    const matches = storyBank.filter(story => {
        return question.tags.some(tag => story.competencies.includes(tag));
    });
    
    // Sort by relevance (number of matching tags)
    matches.sort((a, b) => {
        const aMatches = a.competencies.filter(c => question.tags.includes(c)).length;
        const bMatches = b.competencies.filter(c => question.tags.includes(c)).length;
        return bMatches - aMatches;
    });
    
    // Display matches
    const container = document.querySelector('.matches-container');
    
    if (matches.length === 0) {
        container.innerHTML = '<p class="no-matches">No matching stories. Consider adding stories with these competencies: ' + 
            question.tags.join(', ') + '</p>';
        return;
    }
    
    let html = '<div class="matched-story-list">';
    matches.forEach(story => {
        const matchingTags = story.competencies.filter(c => question.tags.includes(c));
        const relevance = Math.round((matchingTags.length / question.tags.length) * 100);
        
        html += `
            <div class="matched-story">
                <div class="match-header">
                    <h5>${story.title}</h5>
                    <span class="relevance">${relevance}% match</span>
                </div>
                <div class="matching-competencies">
                    Relevant because: ${matchingTags.map(t => `<span class="tag highlight">${t}</span>`).join('')}
                </div>
                <div class="story-preview">
                    <strong>Key Result:</strong> ${story.result.substring(0, 150)}...
                </div>
                <button class="use-story" onclick="showStoryTips('${story.id}', '${questionId}')">
                    How to Use This Story
                </button>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function showStoryTips(storyId, questionId) {
    const story = storyBank.find(s => s.id === storyId);
    
    const tips = `
Tips for using this story:

1. Start with the business context
2. Emphasize your specific role
3. Focus on the "how" in your actions
4. Quantify the results
5. Connect back to the question theme

Time allocation (2 minutes):
- Situation: 20 seconds
- Task: 10 seconds
- Action: 50 seconds
- Result: 30 seconds
- Lesson/Impact: 10 seconds
    `;
    
    alert(tips);
}

function renderCoverageAnalysis() {
    const allCompetencies = [
        'hiring', 'performance', 'conflict', 'technical', 'strategy',
        'change', 'influence', 'scale', 'culture', 'crisis',
        'innovation', 'diversity', 'business', 'failure'
    ];
    
    const coverage = {};
    allCompetencies.forEach(comp => {
        coverage[comp] = storyBank.filter(s => s.competencies.includes(comp)).length;
    });
    
    // Render coverage grid
    const gridContainer = document.getElementById('coverage-grid');
    let gridHtml = '<div class="coverage-items">';
    
    allCompetencies.forEach(comp => {
        const count = coverage[comp];
        const status = count === 0 ? 'empty' : count === 1 ? 'minimal' : 'good';
        
        gridHtml += `
            <div class="coverage-item ${status}">
                <div class="comp-name">${comp}</div>
                <div class="comp-count">${count} ${count === 1 ? 'story' : 'stories'}</div>
            </div>
        `;
    });
    
    gridHtml += '</div>';
    gridContainer.innerHTML = gridHtml;
    
    // Identify gaps
    const gaps = allCompetencies.filter(comp => coverage[comp] === 0);
    const weak = allCompetencies.filter(comp => coverage[comp] === 1);
    
    const gapsContainer = document.getElementById('coverage-gaps');
    let gapsHtml = '<h4>Gap Analysis</h4>';
    
    if (gaps.length > 0) {
        gapsHtml += '<div class="gap-section"><strong>Missing Coverage:</strong><ul>';
        gaps.forEach(gap => {
            gapsHtml += `<li>${gap} - Add stories demonstrating this competency</li>`;
        });
        gapsHtml += '</ul></div>';
    }
    
    if (weak.length > 0) {
        gapsHtml += '<div class="gap-section"><strong>Weak Coverage (only 1 story):</strong><ul>';
        weak.forEach(w => {
            gapsHtml += `<li>${w} - Consider adding backup stories</li>`;
        });
        gapsHtml += '</ul></div>';
    }
    
    if (gaps.length === 0 && weak.length === 0) {
        gapsHtml += '<p class="all-covered">✅ Excellent coverage! You have multiple stories for all competencies.</p>';
    }
    
    gapsContainer.innerHTML = gapsHtml;
}

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}
</script>

<style>
.star-matcher-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.story-input-section {
    background: #f8f9fa;
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 30px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 8px;
    color: #333;
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
}

.form-group textarea {
    resize: vertical;
}

.competency-checkboxes {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
}

.competency-checkboxes label {
    display: flex;
    align-items: center;
    font-weight: normal;
}

.competency-checkboxes input {
    width: auto;
    margin-right: 8px;
}

.add-story-btn {
    background: #5448C8;
    color: white;
    padding: 12px 30px;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
}

.add-story-btn:hover {
    background: #4339A5;
}

.story-bank {
    margin-bottom: 40px;
}

.story-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
}

.story-card {
    background: white;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.story-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: 15px;
}

.story-header h4 {
    margin: 0;
    color: #5448C8;
}

.delete-story {
    background: none;
    border: none;
    font-size: 24px;
    color: #999;
    cursor: pointer;
}

.delete-story:hover {
    color: #F44336;
}

.story-summary {
    font-size: 14px;
    line-height: 1.6;
    color: #666;
    margin-bottom: 15px;
}

.story-meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.impact-badge {
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.impact-badge.team {
    background: #E3F2FD;
    color: #1976D2;
}

.impact-badge.org {
    background: #F3E5F5;
    color: #7B1FA2;
}

.impact-badge.division {
    background: #FFF3E0;
    color: #F57C00;
}

.impact-badge.company {
    background: #E8F5E9;
    color: #388E3C;
}

.competency-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}

.tag {
    background: #f0f0f0;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.tag.highlight {
    background: #FFE082;
}

.expand-story {
    width: 100%;
    padding: 8px;
    background: white;
    border: 1px solid #5448C8;
    color: #5448C8;
    border-radius: 6px;
    cursor: pointer;
}

.expand-story:hover {
    background: #5448C8;
    color: white;
}

.question-matcher {
    background: #f8f9fa;
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 40px;
}

.category-tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.category-tab {
    padding: 10px 20px;
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 600;
}

.category-tab.active {
    background: #5448C8;
    color: white;
    border-color: #5448C8;
}

.questions {
    margin-bottom: 30px;
}

.question-item {
    background: white;
    padding: 15px;
    margin-bottom: 10px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.question-item:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.question-item.selected {
    border: 2px solid #5448C8;
    background: #f8f7ff;
}

.question-tags {
    margin-top: 8px;
}

.matched-stories {
    background: white;
    padding: 20px;
    border-radius: 8px;
}

.matched-story {
    border: 1px solid #e0e0e0;
    padding: 15px;
    margin-bottom: 15px;
    border-radius: 8px;
}

.match-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.relevance {
    background: #4CAF50;
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 600;
}

.matching-competencies {
    margin-bottom: 10px;
    font-size: 14px;
}

.story-preview {
    color: #666;
    font-size: 14px;
    margin-bottom: 10px;
}

.use-story {
    background: #5448C8;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 14px;
}

.coverage-analysis {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.coverage-items {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
}

.coverage-item {
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    border: 2px solid #e0e0e0;
}

.coverage-item.empty {
    background: #FFEBEE;
    border-color: #F44336;
}

.coverage-item.minimal {
    background: #FFF3E0;
    border-color: #FFC107;
}

.coverage-item.good {
    background: #E8F5E9;
    border-color: #4CAF50;
}

.comp-name {
    font-weight: 600;
    margin-bottom: 5px;
    text-transform: capitalize;
}

.comp-count {
    font-size: 14px;
    color: #666;
}

.gap-section {
    margin-bottom: 20px;
}

.all-covered {
    color: #4CAF50;
    font-size: 18px;
    text-align: center;
    padding: 20px;
}

.empty-state {
    text-align: center;
    color: #999;
    padding: 40px;
    font-style: italic;
}

.no-matches {
    color: #F44336;
    font-style: italic;
}

.select-question {
    color: #999;
    font-style: italic;
    text-align: center;
    padding: 20px;
}

/* Toast notification */
.toast {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 15px 25px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 1000;
}

.toast.show {
    opacity: 1;
}

/* Responsive design */
@media (max-width: 768px) {
    .story-cards {
        grid-template-columns: 1fr;
    }
    
    .category-tabs {
        flex-wrap: wrap;
    }
    
    .competency-checkboxes {
        grid-template-columns: 1fr;
    }
}
</style>

---

**Pro Tip**: The best stories are versatile. A single story about scaling a team can demonstrate hiring, culture building, technical leadership, and business impact. Practice telling the same story with different emphasis depending on the question.