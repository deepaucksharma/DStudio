# CLAUDE.md - Hindi Podcast Execution Instructions
## Multi-Agent Parallel Content Creation System

---

## CRITICAL REQUIREMENTS - MUST READ

### Episode Standards (NON-NEGOTIABLE)
- **Minimum Word Count**: 20,000 words per episode (3-hour content)
- **Language**: 70% Hindi/Roman Hindi, 30% Technical English terms only
- **Style**: Mumbai street-style storytelling, NOT academic
- **Examples**: 30% MUST be Indian context (Paytm, Flipkart, Ola, Zomato, IRCTC)
- **Code**: 15+ working examples per episode (Python, Java, Go)
- **Case Studies**: 5+ production failures with timeline and costs
- **2025 Focus**: All examples must be 2020-2025, no outdated content

### Agent Responsibilities

#### Research Agent
```yaml
Task: Deep research for each episode
Requirements:
  - Minimum 5,000 words research notes
  - 10+ academic papers reviewed
  - 5+ company case studies analyzed
  - Indian context examples mandatory
  - Cost analysis in both USD and INR
  - MUST reference relevant docs/ pages for technical accuracy
Documentation Sources:
  - Case studies: docs/architects-handbook/case-studies/
  - Core principles: docs/core-principles/
  - Patterns: docs/pattern-library/
  - Human factors: docs/architects-handbook/human-factors/
  - Laws: docs/core-principles/laws/
  - Migrations: docs/excellence/migrations/
Verification:
  - Word count check: MUST exceed 5,000
  - Source quality check: Recent (2020+)
  - Indian relevance: 30%+ content
  - Documentation referenced: YES
```

#### Content Writer Agent
```yaml
Task: Write complete episode script
Requirements:
  - Minimum 20,000 words per episode
  - 3-hour structure (60min + 60min + 60min)
  - Mumbai metaphors throughout
  - Progressive difficulty curve
Verification:
  - Word count: EXACTLY verify 20,000+ words
  - Structure check: 3 clear parts
  - Readability: Street-level language
```

#### Code Developer Agent
```yaml
Task: Create production-ready code examples
Requirements:
  - 15+ complete code examples
  - Multiple languages (Python, Java, Go)
  - All code MUST be runnable
  - Include tests for each example
Verification:
  - Code count: Minimum 15 examples
  - Syntax check: All must compile/run
  - Comments: Hindi comments included
```

#### Technical Reviewer Agent
```yaml
Task: Verify technical accuracy
Requirements:
  - Check all mathematical formulas
  - Verify production metrics
  - Validate case study facts
  - Test all code examples
Verification:
  - Accuracy: 100% correct
  - References: All cited properly
  - Metrics: Real-world validated
```

#### Quality Assurance Agent
```yaml
Task: Final quality check
Requirements:
  - Word count verification (20,000+)
  - Mumbai style consistency
  - Time duration check (3 hours)
  - Engagement factor assessment
Verification:
  - HARD STOP if <20,000 words
  - Style guide compliance
  - Practical value confirmed
```

---

## PARALLEL EXECUTION FRAMEWORK

### Batch Processing Rules
```markdown
1. Launch 5 agents maximum per batch
2. Each agent MUST complete verification before proceeding
3. Progress tracking mandatory at every stage
4. No episode moves forward without 20,000 words verified
5. Quality > Speed (but maintain timeline)
```

### Episode Creation Pipeline

#### Phase 1: Research (3 agents parallel)
```yaml
Agent 1: Academic Research
  - Papers, theorems, proofs
  - Reference docs/core-principles/ for theoretical foundations
  - Reference docs/analysis/ for mathematical models
  - Minimum 2,000 words
  
Agent 2: Industry Research  
  - Company cases, failures
  - Use docs/architects-handbook/case-studies/ for real examples
  - Check docs/case-studies/ for major system designs
  - Reference docs/architects-handbook/human-factors/ for incidents
  - Minimum 2,000 words
  
Agent 3: Indian Context Research
  - Local examples, metaphors
  - Cross-reference with global cases in docs/
  - Map to Indian equivalents
  - Minimum 1,000 words

GATE: Combined 5,000+ words research + docs referenced
```

#### Phase 2: Content Creation (2 agents parallel)
```yaml
Agent 4: Script Writing
  - Complete episode narrative
  - MUST produce 20,000+ words
  - Verify word count 3 times
  
Agent 5: Code Development
  - 15+ examples minimum
  - Test each example
  - Document thoroughly

GATE: 20,000 words + 15 code examples
```

#### Phase 3: Review (2 agents parallel)
```yaml
Agent 6: Technical Review
  - Accuracy verification
  - Reference checking
  - Metric validation
  
Agent 7: Quality Assurance
  - Final word count (MUST be 20,000+)
  - Style consistency
  - Engagement check

GATE: All checks passed
```

---

## WORD COUNT VERIFICATION PROTOCOL

### Mandatory Checks
```python
def verify_episode_word_count(episode_content):
    """
    CRITICAL: This function MUST be run by EVERY agent
    """
    word_count = len(episode_content.split())
    
    if word_count < 20000:
        raise Exception(f"FAILED: Only {word_count} words. Need 20,000+")
    
    # Check each section
    sections = episode_content.split("## ")
    for section in sections:
        section_words = len(section.split())
        if section_words < 2000:
            print(f"WARNING: Section has only {section_words} words")
    
    print(f"✅ PASSED: {word_count} words")
    return True
```

### Progress Tracking Template
```markdown
Episode: [NUMBER] - [TITLE]
Status: [RESEARCH | WRITING | REVIEW | COMPLETE]

Word Count Progress:
- Research Notes: [X]/5,000 words
- Main Script: [X]/20,000 words  
- Code Examples: [X]/15 examples
- Case Studies: [X]/5 studies

Verification Checkpoints:
□ Research word count verified (5,000+)
□ Script word count verified (20,000+)
□ Code examples tested (15+)
□ Indian context included (30%+)
□ 2025 examples used (100%)
□ Mumbai style confirmed
□ Technical accuracy verified
□ Final QA passed

Agent Sign-offs:
- Research Agent: [PENDING/COMPLETE]
- Writer Agent: [PENDING/COMPLETE]
- Code Agent: [PENDING/COMPLETE]
- Review Agent: [PENDING/COMPLETE]
- QA Agent: [PENDING/COMPLETE]
```

---

## DOCUMENTATION REFERENCE GUIDE

### Priority Documentation for Research
Each episode MUST incorporate content from relevant docs/ sections:

#### Core Technical Foundations
```yaml
CAP Theorem & Consistency:
  - docs/core-principles/cap-theorem.md
  - docs/core-principles/impossibility-results.md
  - docs/pattern-library/data-management/tunable-consistency.md

Distributed System Laws:
  - docs/core-principles/laws/asynchronous-reality.md
  - docs/core-principles/laws/correlated-failure.md
  - docs/core-principles/laws/distributed-knowledge.md
  - docs/core-principles/laws/emergent-chaos.md

System Analysis:
  - docs/analysis/queueing-models.md
  - docs/analysis/littles-law.md
  - docs/analysis/cap-theorem.md
```

#### Production Case Studies
```yaml
Elite Engineering:
  - docs/architects-handbook/case-studies/elite-engineering/
  - Netflix, Discord, Figma, Stripe examples

Database Systems:
  - docs/architects-handbook/case-studies/databases/
  - DynamoDB, Cassandra, MongoDB, Redis

Messaging & Streaming:
  - docs/architects-handbook/case-studies/messaging-streaming/
  - Kafka, Netflix streaming, Event-driven

Social & Communication:
  - docs/architects-handbook/case-studies/social-communication/
  - WhatsApp, Slack, Twitter, YouTube
```

#### Pattern Library
```yaml
Resilience Patterns:
  - docs/pattern-library/resilience/
  - Circuit breaker, Bulkhead, Chaos engineering

Data Management:
  - docs/pattern-library/data-management/
  - CQRS, Event sourcing, Saga pattern

Scaling Patterns:
  - docs/pattern-library/scaling/
  - Sharding, Caching, Load balancing

Architecture Patterns:
  - docs/pattern-library/architecture/
  - Microservices, Event-driven, Service mesh
```

#### Human & Operational Factors
```yaml
Incident Management:
  - docs/architects-handbook/human-factors/incident-response.md
  - docs/architects-handbook/human-factors/blameless-postmortems.md

Operational Excellence:
  - docs/architects-handbook/human-factors/sre-practices.md
  - docs/architects-handbook/human-factors/oncall-culture.md
  - docs/architects-handbook/human-factors/chaos-engineering.md
```

### Documentation Integration Rules
1. Every episode MUST cite at least 5 docs/ pages
2. Map theoretical concepts to practical case studies
3. Connect patterns to real implementations
4. Reference human factors for every technical topic
5. Use migration guides for evolution stories

---

## THINKING REQUIREMENTS

### Deep Thinking Checklist (MANDATORY)
Each agent MUST consider:

1. **Conceptual Depth**
   - Why does this concept exist?
   - What problem does it solve?
   - What are the alternatives?
   - Why do companies choose this?
   - What are the trade-offs?

2. **Indian Context Integration**
   - How does Flipkart use this?
   - What would Ola do differently?
   - How does this apply to UPI scale?
   - What are Indian-specific challenges?
   - Cost implications in INR?

3. **Production Reality**
   - What breaks in production?
   - How much does it cost to implement?
   - What are the maintenance nightmares?
   - How many engineers needed?
   - What's the ROI timeline?

4. **Mumbai Metaphor Mapping**
   - Local train analogy?
   - Dabba system parallel?
   - Monsoon flooding comparison?
   - Street vendor example?
   - Traffic signal similarity?

5. **Code Practicality**
   - Will this run on a laptop?
   - Cloud costs for testing?
   - Open source alternatives?
   - Indian cloud providers?
   - Jugaad solutions?

---

## EPISODE PRIORITIES

### Immediate Focus (Episodes 1-10)
```yaml
Episode 1: Probability & System Failures
  - Target: 22,000 words (buffer included)
  - Facebook 2021 + Zomato NYE 2024
  - Code: Python chaos engineering
  - Reference: docs/core-principles/laws/correlated-failure.md

Episode 2: Chaos Engineering & Queues  
  - Target: 22,000 words
  - IRCTC Tatkal + Mumbai Local
  - Code: Litmus Chaos setup
  - Reference: docs/pattern-library/resilience/chaos-engineering-mastery.md
  - Reference: docs/analysis/queueing-models.md

Episode 3: Human Factor in Tech
  - Target: 22,000 words
  - Indian IT culture + On-call
  - Code: Alert management systems
  - Reference: docs/architects-handbook/human-factors/

Episode 4: Distribution Laws (CAP etc)
  - Target: 22,000 words  
  - Banking vs E-commerce trade-offs
  - Code: Consistency simulators
  - Reference: docs/core-principles/cap-theorem.md
  - Reference: docs/core-principles/impossibility-results.md

Episode 5: AI at Scale
  - Target: 22,000 words
  - ChatGPT architecture + Indian AI
  - Code: Distributed training
  - Reference: docs/pattern-library/ml-infrastructure/
```

### Quality Gates Per Episode
1. Research complete: 5,000+ words ✓
2. Script complete: 20,000+ words ✓
3. Code complete: 15+ examples ✓
4. Review complete: All accurate ✓
5. QA complete: Ready to publish ✓

---

## AGENT COORDINATION

### Communication Protocol
```markdown
Agent Start Message:
"Starting [TASK] for Episode [X]: [Title]
Target: [WORD_COUNT] words
Estimated completion: [TIME]"

Progress Update (every 30 min):
"Progress: [X]/[TARGET] words
Current section: [SECTION]
Blockers: [ANY]"

Completion Message:
"Completed [TASK] for Episode [X]
Final word count: [COUNT] (verified)
Quality checks: PASSED
Ready for next stage"
```

### Failure Handling
```markdown
If word count < 20,000:
1. STOP immediately
2. Identify gap areas
3. Add more case studies
4. Expand code explanations
5. Include more Indian examples
6. Re-verify word count
7. Only proceed when 20,000+ confirmed
```

---

## TOOLS AND RESOURCES

### Word Count Tools
```bash
# Bash command for word count
wc -w episode-*.md

# Python verification
python -c "import sys; content=open(sys.argv[1]).read(); words=len(content.split()); print(f'{words} words'); exit(0 if words>=20000 else 1)" episode.md
```

### Research Sources
- Papers: Google Scholar, arXiv
- Cases: Engineering blogs, Postmortems
- Indian: YourStory, Inc42, TechCircle
- Global: High Scalability, InfoQ
- Code: GitHub, GitLab, Bitbucket
- **Internal Documentation (PRIORITY)**:
  - docs/architects-handbook/case-studies/ - Production case studies
  - docs/core-principles/ - Theoretical foundations
  - docs/pattern-library/ - Design patterns and implementations
  - docs/architects-handbook/human-factors/ - Human and operational aspects
  - docs/excellence/migrations/ - Migration strategies
  - docs/core-principles/laws/ - Fundamental laws and principles
  - docs/analysis/ - Mathematical models and analysis

### Style References
- Mumbai style: Local train announcements
- Technical terms: Consistent Hindi translations
- Metaphors: Street food, traffic, monsoon
- Tone: Friend explaining, not professor

---

## SUCCESS METRICS

### Per Episode Requirements
- [ ] 20,000+ words (HARD MINIMUM)
- [ ] 15+ code examples (TESTED)
- [ ] 5+ case studies (VERIFIED)
- [ ] 30%+ Indian context
- [ ] 100% 2020+ examples
- [ ] 3-hour audio duration
- [ ] Mumbai style throughout
- [ ] Zero technical errors
- [ ] High engagement value
- [ ] Practical takeaways

### Series Goals
- 200 episodes total
- 4,000,000+ words total
- 3,000+ code examples
- 1,000+ case studies
- 100,000+ engineers impacted

---

## ENFORCEMENT RULES

1. **NO EPISODE PROCEEDS WITHOUT 20,000 WORDS**
2. **NO CODE EXAMPLES WITHOUT TESTING**
3. **NO CASE STUDIES WITHOUT VERIFICATION**
4. **NO TECHNICAL CONTENT WITHOUT REVIEW**
5. **NO PUBLISHING WITHOUT QA APPROVAL**

---

## AGENT LAUNCH COMMANDS

### For Research Phase
```markdown
Launch 3 agents in parallel:
- Agent 1: "Research theoretical foundations for Episode X, minimum 2000 words. MUST reference relevant docs/core-principles/, docs/analysis/, and docs/pattern-library/ pages"
- Agent 2: "Research industry cases for Episode X, minimum 2000 words. MUST use docs/architects-handbook/case-studies/ and docs/case-studies/ for examples"  
- Agent 3: "Research Indian context for Episode X, minimum 1000 words. Cross-reference with docs/ examples and map to Indian equivalents"
```

### For Writing Phase
```markdown
Launch 2 agents in parallel:
- Agent 4: "Write complete Episode X script, MUST BE 20,000+ words"
- Agent 5: "Create 15+ code examples for Episode X, all tested"
```

### For Review Phase
```markdown
Launch 2 agents in parallel:
- Agent 6: "Technical review Episode X, verify all facts"
- Agent 7: "Quality assurance Episode X, verify 20,000+ words"
```

---

## DAILY TRACKING TEMPLATE

```markdown
Date: [DATE]
Episodes in Progress: [COUNT]

Episode Status:
- E001: [Research|Writing|Review] - [X]/20,000 words
- E002: [Research|Writing|Review] - [X]/20,000 words
- E003: [Research|Writing|Review] - [X]/20,000 words

Agents Active:
- Research: [COUNT] agents
- Writing: [COUNT] agents  
- Review: [COUNT] agents

Blockers:
- [List any blockers]

Completed Today:
- [List completed episodes]

Tomorrow's Plan:
- [List planned episodes]
```

---

## FINAL NOTES

Remember: Quality > Speed, but maintain discipline. Every episode represents 3 hours of someone's learning time. Make it worth it. Make it memorable. Make it Mumbai.

**The 20,000 word minimum is NON-NEGOTIABLE.**

---

*Last Updated: 2025-01-10*
*Version: 1.1*
*Status: ACTIVE - ENFORCEMENT MODE*
*Change: Added documentation reference requirements for research agents*

---

## UPDATED DIRECTORY STRUCTURE (As of Jan 11, 2025)

ALL podcast work is now consolidated in the `podcast-project/` directory:

```
podcast-project/
├── PODCAST_MASTER_TRACKER.md      # Single source of truth
├── STREAMLINED_EXECUTION_GUIDE.md # Production guide
├── episodes/                       # All episode content
│   ├── episode-001-probability/
│   │   ├── research/              # Research notes (5,000+ words)
│   │   ├── script/                # Episode script (20,000+ words)
│   │   ├── code/                  # Code examples (15+ examples)
│   │   │   ├── python/
│   │   │   ├── java/
│   │   │   └── go/
│   │   └── quality/               # QA reports
│   └── [episodes 002-150...]
├── documentation/                  # All reports and docs
├── scripts/                       # Utility scripts
├── shared-resources/              # Common resources
└── archive/                       # Old/deprecated content
```

### IMPORTANT PATH UPDATES:
- Research output: `podcast-project/episodes/episode-XXX-topic/research/research-notes.md`
- Script output: `podcast-project/episodes/episode-XXX-topic/script/episode-script.md`
- Code output: `podcast-project/episodes/episode-XXX-topic/code/`
- Master tracker: `podcast-project/PODCAST_MASTER_TRACKER.md`

### Agent Commands Must Use New Paths:
Replace all paths in agent commands:
- Old: `episodes/episode-XXX/...`
- New: `podcast-project/episodes/episode-XXX/...`
