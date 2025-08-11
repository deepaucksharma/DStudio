# 🚀 STREAMLINED EXECUTION GUIDE
## Practical Implementation of Consolidated Podcast Framework
### Version 2.0 - January 11, 2025

---

## 🎯 QUICK START: EPISODE PRODUCTION WORKFLOW

### AGENT COMMAND TEMPLATES

#### 📚 RESEARCH AGENT COMMAND
```markdown
Create comprehensive research for Episode [X]: [Topic Name]

Requirements:
1. Output location: /home/deepak/DStudio/episodes/episode-[XXX]-[topic]/research/research-notes.md
2. Minimum 5,000 words of research content
3. Include:
   - 10+ academic papers/articles
   - 5+ production case studies (2020-2025)
   - 30%+ Indian context (Flipkart, Paytm, IRCTC, Zomato, Ola examples)
   - Cost analysis in INR and USD
4. Reference these docs/ pages:
   - docs/core-principles/[relevant-topic].md
   - docs/architects-handbook/case-studies/[relevant-cases]/
   - docs/pattern-library/[relevant-patterns]/
5. Format: Clear sections with headers
6. Verify word count before completion: wc -w research-notes.md

CRITICAL: Save to exact path specified. Do NOT create files elsewhere.
```

#### ✍️ CONTENT WRITER AGENT COMMAND
```markdown
Write complete Episode [X]: [Topic Name] script in Mumbai style

Input: /home/deepak/DStudio/episodes/episode-[XXX]-[topic]/research/research-notes.md
Output: /home/deepak/DStudio/episodes/episode-[XXX]-[topic]/script/episode-script.md

Requirements:
1. EXACTLY 20,000+ words (verify 3 times)
2. Structure: 3 parts (60 min each = 3 hours total)
   - Part 1: Introduction & Basics (6,500+ words)
   - Part 2: Deep Dive & Examples (7,000+ words)  
   - Part 3: Advanced & Future (6,500+ words)
3. Language: 70% Hindi/Roman Hindi, 30% Technical English
4. Include throughout:
   - Mumbai metaphors (local trains, dabbawala, traffic)
   - Indian company examples (30%+ content)
   - Street-style storytelling (not academic)
   - Progressive difficulty curve
5. Verification commands:
   - Word count: wc -w episode-script.md
   - Structure: grep "^## Part" episode-script.md

CRITICAL: Must be EXACTLY 20,000+ words. Do NOT proceed if less.
```

#### 💻 CODE DEVELOPER AGENT COMMAND
```markdown
Create production-ready code examples for Episode [X]: [Topic Name]

Input: /home/deepak/DStudio/episodes/episode-[XXX]-[topic]/script/episode-script.md
Output: /home/deepak/DStudio/episodes/episode-[XXX]-[topic]/code/

Requirements:
1. Create 15+ complete, runnable examples
2. Languages: Python (10+), Java (3+), Go (2+)
3. Directory structure:
   code/
   ├── python/
   │   ├── 01_example_name.py
   │   ├── 02_example_name.py
   │   └── ...
   ├── java/
   │   ├── Example01.java
   │   └── ...
   ├── go/
   │   ├── example01.go
   │   └── ...
   └── tests/
       ├── test_python_examples.py
       └── ...
4. Each example must:
   - Be production-ready
   - Include Hindi comments
   - Have corresponding test
   - Use Indian context where possible
5. Verification:
   - Count: ls -la code/*/*.{py,java,go} | wc -l
   - Tests: python -m pytest code/tests/

CRITICAL: All code must be tested and runnable.
```

#### 🔍 TECHNICAL REVIEWER AGENT COMMAND
```markdown
Review Episode [X]: [Topic Name] for technical accuracy

Inputs:
- Research: /home/deepak/DStudio/episodes/episode-[XXX]-[topic]/research/
- Script: /home/deepak/DStudio/episodes/episode-[XXX]-[topic]/script/
- Code: /home/deepak/DStudio/episodes/episode-[XXX]-[topic]/code/

Tasks:
1. Verify all technical facts and figures
2. Test all code examples
3. Validate case study details
4. Check mathematical formulas
5. Verify references and citations
6. Create review report: quality/technical-review.md

Output format:
- ✅ Verified: [list of verified items]
- ❌ Issues found: [list of issues with corrections]
- 📝 Recommendations: [improvements needed]
```

#### ✅ QUALITY ASSURANCE AGENT COMMAND
```markdown
Final quality check for Episode [X]: [Topic Name]

Location: /home/deepak/DStudio/episodes/episode-[XXX]-[topic]/

Checklist:
□ Word count: Script ≥ 20,000 words
□ Research: ≥ 5,000 words
□ Code examples: ≥ 15 working examples
□ Language ratio: 70% Hindi, 30% English
□ Indian context: ≥ 30% of examples
□ Mumbai metaphors: Present throughout
□ 3-part structure: Properly divided
□ Tests: All passing
□ Technical accuracy: Verified
□ References: All cited properly

Create: quality/qa-report.md with all metrics

GATE: Episode is BLOCKED if any requirement fails.
```

---

## 📁 DIRECTORY SETUP COMMANDS

### Create Episode Structure
```bash
#!/bin/bash
# create_episode.sh

EPISODE_NUM=$1
EPISODE_TOPIC=$2

# Format episode number with leading zeros
EPISODE_DIR="episodes/episode-$(printf "%03d" $EPISODE_NUM)-${EPISODE_TOPIC}"

# Create directory structure
mkdir -p "$EPISODE_DIR"/{research,script,code/{python,java,go,tests},quality}

# Create README with template
cat > "$EPISODE_DIR/README.md" << EOF
# Episode ${EPISODE_NUM}: ${EPISODE_TOPIC}

## Status
- Research: ⏳ PENDING
- Script: ⏳ PENDING  
- Code: ⏳ PENDING
- Review: ⏳ PENDING
- QA: ⏳ PENDING

## Metrics
- Research words: 0/5,000
- Script words: 0/20,000
- Code examples: 0/15

## Timeline
- Started: $(date +"%Y-%m-%d")
- Target: [DATE]
- Completed: -
EOF

echo "Created structure for Episode ${EPISODE_NUM}: ${EPISODE_TOPIC}"
echo "Location: ${EPISODE_DIR}"
```

### Verify Episode Completeness
```python
#!/usr/bin/env python3
# verify_episode.py

import os
import sys
import glob

def count_words(filepath):
    try:
        with open(filepath, 'r') as f:
            return len(f.read().split())
    except:
        return 0

def count_code_files(directory):
    patterns = ['*.py', '*.java', '*.go']
    total = 0
    for pattern in patterns:
        files = glob.glob(f"{directory}/**/{pattern}", recursive=True)
        total += len(files)
    return total

def verify_episode(episode_num):
    # Find episode directory
    episode_dirs = glob.glob(f"episodes/episode-{episode_num:03d}-*/")
    if not episode_dirs:
        print(f"❌ Episode {episode_num} directory not found")
        return False
    
    episode_dir = episode_dirs[0]
    print(f"\n📋 Verifying {episode_dir}")
    print("="*50)
    
    passed = True
    
    # Check research
    research_words = count_words(f"{episode_dir}research/research-notes.md")
    if research_words >= 5000:
        print(f"✅ Research: {research_words:,} words")
    else:
        print(f"❌ Research: {research_words:,}/5,000 words")
        passed = False
    
    # Check script
    script_words = count_words(f"{episode_dir}script/episode-script.md")
    if script_words >= 20000:
        print(f"✅ Script: {script_words:,} words")
    else:
        print(f"❌ Script: {script_words:,}/20,000 words")
        passed = False
    
    # Check code
    code_count = count_code_files(f"{episode_dir}code")
    if code_count >= 15:
        print(f"✅ Code: {code_count} examples")
    else:
        print(f"❌ Code: {code_count}/15 examples")
        passed = False
    
    print("="*50)
    if passed:
        print(f"✅ Episode {episode_num} COMPLETE!")
    else:
        print(f"❌ Episode {episode_num} INCOMPLETE")
    
    return passed

if __name__ == "__main__":
    if len(sys.argv) > 1:
        episode_num = int(sys.argv[1])
        verify_episode(episode_num)
    else:
        # Verify all episodes
        for i in range(1, 151):
            if os.path.exists(f"episodes/episode-{i:03d}-*/"):
                verify_episode(i)
```

---

## 📊 MASTER TRACKER TEMPLATE

```markdown
# PODCAST_MASTER_TRACKER.md
## Hindi Podcast Series - Production Dashboard
### Last Updated: [AUTO_DATE]

---

## 📈 OVERALL PROGRESS
- **Total Episodes**: 150 target
- **Completed**: X/150 (X%)
- **In Progress**: Y episodes
- **Total Words Written**: X,XXX,XXX
- **Total Code Examples**: X,XXX

---

## 📋 EPISODE STATUS

| # | Episode Title | Research | Script | Code | Review | QA | Status |
|---|--------------|----------|--------|------|--------|----|----|
| 001 | Probability & Failures | ✅ 5,234 | ✅ 20,063 | ✅ 15 | ✅ | ✅ | **COMPLETE** |
| 002 | Chaos Engineering | ✅ 5,102 | ✅ 20,114 | ✅ 16 | ✅ | ✅ | **COMPLETE** |
| 003 | Human Factor | ✅ 3,247 | ⚠️ 7,825 | ⏳ 0 | ⏳ | ⏳ | **IN PROGRESS** |
| 004 | CAP Theorem | ⚠️ 2,100 | ⏳ 0 | ⚠️ 8 | ⏳ | ⏳ | **BLOCKED** |
| ... | ... | ... | ... | ... | ... | ... | ... |

---

## 🎯 CURRENT SPRINT (Week of [DATE])

### Priority 1: Complete Episode 3
- [ ] Add 12,175 words to script
- [ ] Create 15 code examples
- [ ] Complete technical review
- [ ] Pass QA verification

### Priority 2: Start Episode 4
- [ ] Complete research (add 2,900 words)
- [ ] Begin script writing
- [ ] Integrate existing code

### Priority 3: Pipeline Validation
- [ ] Test new directory structure
- [ ] Validate verification scripts
- [ ] Document lessons learned
```

---

## 🔄 DAILY EXECUTION ROUTINE

### Morning Standup (9 AM)
```markdown
1. Check PODCAST_MASTER_TRACKER.md
2. Identify today's episodes and phases
3. Launch research agents for new episodes
4. Review overnight agent work
```

### Midday Check (1 PM)
```markdown
1. Verify research word counts
2. Launch writing agents for completed research
3. Launch code agents for completed scripts
4. Update tracker with progress
```

### Evening Review (5 PM)
```markdown
1. Run verification scripts
2. Launch review/QA agents
3. Update master tracker
4. Plan next day's work
```

---

## 🛠️ TROUBLESHOOTING GUIDE

### Common Issues and Solutions

#### Issue: Agent creates files in wrong location
```bash
# Solution: Move files to correct location
mv /wrong/path/file.md /home/deepak/DStudio/episodes/episode-XXX-topic/correct/path/
```

#### Issue: Word count below requirement
```bash
# Solution: Calculate deficit and instruct agent
CURRENT=$(wc -w < episode-script.md)
REQUIRED=20000
DEFICIT=$((REQUIRED - CURRENT))
echo "Need $DEFICIT more words"
# Then instruct agent to add specific content
```

#### Issue: Code examples not running
```bash
# Solution: Debug and fix
cd episodes/episode-XXX/code/python
python3 -m py_compile *.py  # Check syntax
python3 -m pytest ../tests/  # Run tests
```

---

## 📱 MONITORING COMMANDS

### Quick Status Check
```bash
# Show all episode statuses
find episodes -name "README.md" -exec grep -H "^- Script:" {} \; | sort
```

### Word Count Summary
```bash
# Total words across all episodes
find episodes -name "*.md" -exec wc -w {} + | tail -1
```

### Code Example Count
```bash
# Count all code examples
find episodes -path "*/code/*" -name "*.py" -o -name "*.java" -o -name "*.go" | wc -l
```

### Find Incomplete Episodes
```bash
# Episodes with script < 20,000 words
for dir in episodes/*/; do
  script="$dir/script/episode-script.md"
  if [ -f "$script" ]; then
    words=$(wc -w < "$script")
    if [ $words -lt 20000 ]; then
      echo "$dir: $words words (need $((20000-words)) more)"
    fi
  fi
done
```

---

## 🎖️ QUALITY STANDARDS ENFORCEMENT

### Automated Quality Gates

```python
# quality_gate.py
class EpisodeQualityGate:
    def __init__(self, episode_path):
        self.path = episode_path
        self.requirements = {
            'research_words': 5000,
            'script_words': 20000,
            'code_examples': 15,
            'hindi_percent': 70,
            'indian_context_percent': 30
        }
    
    def check_all(self):
        checks = {
            'research': self.check_research(),
            'script': self.check_script(),
            'code': self.check_code(),
            'language': self.check_language_ratio(),
            'context': self.check_indian_context()
        }
        
        return all(checks.values()), checks
    
    def generate_report(self):
        passed, checks = self.check_all()
        
        report = f"""
# Quality Gate Report
Episode: {self.path}
Status: {'PASSED ✅' if passed else 'FAILED ❌'}

## Checks:
- Research: {'✅' if checks['research'] else '❌'}
- Script: {'✅' if checks['script'] else '❌'}
- Code: {'✅' if checks['code'] else '❌'}
- Language: {'✅' if checks['language'] else '❌'}
- Context: {'✅' if checks['context'] else '❌'}

Generated: {datetime.now()}
        """
        
        with open(f"{self.path}/quality/gate-report.md", 'w') as f:
            f.write(report)
        
        return passed
```

---

## 🚦 GO/NO-GO DECISION MATRIX

| Requirement | Threshold | Action if Failed |
|------------|-----------|------------------|
| Research words | < 5,000 | BLOCK writing phase |
| Script words | < 20,000 | BLOCK code phase |
| Code examples | < 15 | BLOCK review phase |
| Tests passing | < 100% | BLOCK QA phase |
| QA approval | Failed | BLOCK publication |

---

## 📝 AGENT COORDINATION PROTOCOL

### Handoff Template
```markdown
## Agent Handoff Document
**From**: [Research Agent]
**To**: [Content Writer Agent]
**Episode**: [XXX - Topic]
**Date**: [DATE]

### Deliverables Completed:
- ✅ Research notes: 5,234 words
- ✅ Location: episodes/episode-XXX/research/research-notes.md
- ✅ References: 12 papers, 6 case studies
- ✅ Indian context: 35% of content

### Key Insights for Writing:
1. [Key point 1]
2. [Key point 2]
3. [Key point 3]

### Recommended Structure:
- Part 1: Focus on [topic]
- Part 2: Deep dive into [topic]
- Part 3: Advanced [topic]

### Next Agent Action:
Write 20,000+ word script using research provided.
```

---

## 🎯 SUCCESS METRICS

### Daily Targets
- Research: 2 episodes (10,000+ words)
- Scripts: 1 episode (20,000+ words)
- Code: 2 episodes (30+ examples)
- Reviews: 2 episodes
- QA: 1 episode ready for publication

### Weekly Targets
- 5 complete episodes
- 100,000+ words content
- 75+ code examples
- 100% quality compliance

### Monthly Targets
- 20 complete episodes
- 400,000+ words content
- 300+ code examples
- Zero quality issues

---

## 🔑 KEY COMMANDS REFERENCE

```bash
# Create new episode structure
./create_episode.sh 4 "cap-theorem"

# Verify episode completeness
python3 verify_episode.py 3

# Check all episodes status
python3 verify_all_episodes.py

# Generate quality report
python3 quality_gate.py episodes/episode-003-human-factor/

# Update master tracker
python3 update_tracker.py

# Archive old content
mv old_file.md archive/

# Find incomplete work
grep -r "PENDING" episodes/*/README.md

# Count total progress
find episodes -name "episode-script.md" -exec wc -w {} + | tail -1
```

---

## 📞 ESCALATION PROTOCOL

If blocked or confused:
1. Check this guide first
2. Verify file locations are correct
3. Run verification scripts
4. Check CLAUDE.md for requirements
5. Update master tracker with blocker
6. Request specific clarification

---

*This guide is your single source of truth for episode production.*
*Follow it exactly for consistent, high-quality output.*
*Update it with lessons learned to improve the process.*

---

**Version**: 2.0
**Updated**: January 11, 2025
**Status**: ACTIVE PRODUCTION GUIDE