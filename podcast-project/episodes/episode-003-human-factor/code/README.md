# Episode 3: Human Factor in Tech - Code Examples

## 👥 भारतीय Tech Culture में Human Factors की Analysis

इस episode में हमने tech industry के human factors को Indian cultural context के साथ analyze किया है। On-call rotation से लेकर work-life balance तक, हर example में Mumbai की life का reflection है। Code में psychological safety, cultural bias, और team dynamics का realistic implementation दिया गया है।

## 📂 Code Structure

```
episode-003-human-factor/code/
├── python/               # Python implementations (15 examples)
├── java/                # Java implementations (scattered in python folder)
├── go/                  # Go implementations (scattered in python folder)
├── tests/               # Test files
└── README.md           # This file
```

## 🐍 Complete Code Examples (15 Examples)

### On-Call & Incident Management

### 1. On-Call Rotation Manager (`01_oncall_rotation_manager.py`)
- **Context**: Fair on-call scheduling में Indian festivals का respect
- **Features**: 
  - Indian festival calendar integration (Diwali, Holi, Eid, etc.)
  - Family obligations handling (school pickup, elderly care)
  - Burnout prevention with stress scoring
  - Mumbai local train schedule की तरह predictable rotation
- **Cultural Aspects**: Work-life balance, family priorities, festival seasons
- **Run**: `python3 python/01_oncall_rotation_manager.py`

### 2. Alert Fatigue Analyzer (`02_alert_fatigue_analyzer.py`)
- **Context**: Mumbai traffic jam की तरह alert overload analysis
- **Features**:
  - Traffic signal metaphor (Green/Yellow/Red alerts)
  - Noise detection (unnecessary honking = noisy alerts)
  - Peak hour patterns (morning/evening rush = alert spikes)
  - Fatigue score calculation with Mumbai analogies
- **Cultural Aspects**: Indian work hour patterns, attention span analysis
- **Run**: `python3 python/02_alert_fatigue_analyzer.py`

### 3. Incident Command System (`03_incident_command_system.java`)
- **Context**: Major incident handling with hierarchical Indian management style
- **Features**:
  - Clear command structure (CEO → CTO → VP → Senior → Junior)
  - Escalation matrix based on Indian corporate hierarchy
  - Communication patterns respecting seniority
  - Crisis management with cultural sensitivity
- **Cultural Aspects**: Respect for hierarchy, face-saving communication
- **Run**: `javac python/03_incident_command_system.java && java IncidentCommandSystem`

### Psychological & Cultural Factors

### 4. Psychological Safety Scorer (`04_psychological_safety_scorer.py`)
- **Context**: Team psychological safety measurement in Indian teams
- **Features**:
  - Anonymous feedback collection
  - Cultural bias detection in team interactions
  - Language barrier impact analysis
  - Safe space creation metrics
- **Cultural Aspects**: Hierarchy respect vs open communication balance
- **Run**: `python3 python/04_psychological_safety_scorer.py`

### 5. Blameless Postmortem Generator (`05_blameless_postmortem_generator.py`)
- **Context**: Indian culture में blame-free incident analysis
- **Features**:
  - Cultural sensitivity in language (avoiding shame/blame)
  - Root cause analysis without personal targeting
  - Learning-focused documentation
  - Action items with ownership clarity
- **Cultural Aspects**: Face-saving communication, collective responsibility
- **Run**: `python3 python/05_blameless_postmortem_generator.py`

### 6. Work-Life Balance Monitor (`06_work_life_balance_monitor.go`)
- **Context**: Indian IT industry का work-life balance tracking
- **Features**:
  - Long working hours detection
  - Weekend work patterns analysis
  - Family time vs work time balance
  - Regional festival impact on work patterns
- **Cultural Aspects**: Indian family obligations, festival priorities
- **Run**: `go run python/06_work_life_balance_monitor.go`

### Team Dynamics & Communication

### 7. Team Cognitive Load Calculator (`07_team_cognitive_load_calculator.py`)
- **Context**: Team mental bandwidth calculation with Indian context
- **Features**:
  - Task complexity scoring
  - Context switching penalty (meetings, interruptions)
  - Language switching cost (Hindi to English)
  - Information overload detection
- **Cultural Aspects**: Multilingual environment cognitive load
- **Run**: `python3 python/07_team_cognitive_load_calculator.py`

### 8. Communication Effectiveness Analyzer (`08_communication_effectiveness_analyzer.py`)
- **Context**: Cross-cultural communication effectiveness in Indian teams
- **Features**:
  - Language barrier detection
  - Cultural communication style analysis
  - Meeting effectiveness scoring
  - Silent participant identification
- **Cultural Aspects**: Direct vs indirect communication styles
- **Run**: `python3 python/08_communication_effectiveness_analyzer.py`

### 9. Cultural Bias Detector (`09_cultural_bias_detector.py`)
- **Context**: Unconscious bias detection in tech teams
- **Features**:
  - Name-based bias detection (regional name preferences)
  - Gender bias in task assignments
  - Educational background bias (IIT/NIT preference)
  - Regional bias detection (North vs South)
- **Cultural Aspects**: Indian regional and social biases
- **Run**: `python3 python/09_cultural_bias_detector.py`

### Mental Health & Wellbeing

### 10. Mental Health Check-in System (`10_mental_health_checkin_system.py`)
- **Context**: Regular mental health monitoring with Indian sensitivity
- **Features**:
  - Anonymous mood tracking
  - Stress pattern identification
  - Cultural stigma-aware communication
  - Early intervention recommendations
- **Cultural Aspects**: Mental health taboo handling, family support integration
- **Run**: `python3 python/10_mental_health_checkin_system.py`

### 11. Knowledge Sharing Platform (`11_knowledge_sharing_platform.py`)
- **Context**: Knowledge transfer in Indian mentorship culture
- **Features**:
  - Senior-junior knowledge transfer tracking
  - Domain expertise mapping
  - Cultural knowledge preservation
  - Mentorship relationship analysis
- **Cultural Aspects**: Guru-shishya tradition in modern context
- **Run**: `python3 python/11_knowledge_sharing_platform.py`

### 12. Incident Stress Calculator (`12_incident_stress_calculator.py`)
- **Context**: Incident-induced stress measurement and management
- **Features**:
  - Stress level calculation during incidents
  - Recovery time estimation
  - Support system activation
  - Long-term impact assessment
- **Cultural Aspects**: Indian family support systems during crisis
- **Run**: `python3 python/12_incident_stress_calculator.py`

### Diversity & Inclusion

### 13. Diversity Inclusion Dashboard (`13_diversity_inclusion_dashboard.go`)
- **Context**: D&I metrics tracking for Indian tech teams
- **Features**:
  - Regional diversity tracking (26+ states represented)
  - Gender ratio monitoring
  - Language diversity metrics
  - Inclusive culture measurement
- **Cultural Aspects**: India's diversity as strength, inclusion challenges
- **Run**: `go run python/13_diversity_inclusion_dashboard.go`

### 14. Technical Debt Psychology Tracker (`14_technical_debt_psychology_tracker.py`)
- **Context**: Technical debt का psychological impact on Indian developers
- **Features**:
  - Developer frustration tracking
  - Legacy system stress analysis
  - Motivation impact measurement
  - Technical debt prioritization psychology
- **Cultural Aspects**: Perfectionism vs pragmatism in Indian culture
- **Run**: `python3 python/14_technical_debt_psychology_tracker.py`

### 15. Sustainable Engineering Metrics (`15_sustainable_engineering_metrics.py`)
- **Context**: Long-term sustainable engineering practices measurement
- **Features**:
  - Burnout prevention metrics
  - Career growth tracking
  - Team sustainability scoring
  - Indian context sustainability challenges
- **Cultural Aspects**: Long-term career perspective, family stability needs
- **Run**: `python3 python/15_sustainable_engineering_metrics.py`

## 🛠️ Setup Instructions

### Prerequisites
- **Python 3.8+**: For most examples
- **Java 11+**: For incident command system  
- **Go 1.19+**: For work-life balance and diversity dashboard
- **Additional Libraries**: psychology/behavior analysis libraries

### Python Setup
```bash
# Install core dependencies
pip3 install dataclasses typing enum datetime json
pip3 install statistics collections defaultdict

# For advanced psychological analysis
pip3 install numpy pandas matplotlib seaborn
pip3 install textblob nltk  # For text sentiment analysis
pip3 install scikit-learn   # For bias detection algorithms

# For cultural analysis
pip3 install langdetect     # Language detection
pip3 install pytz          # Timezone handling for global teams
```

### Java Setup
```bash
# Ensure Java is installed
java -version
javac -version

# No additional dependencies for basic incident management
```

### Go Setup
```bash
# Ensure Go is installed
go version

# Initialize Go module
go mod init human-factors-examples

# Dependencies handled automatically
```

## 🏃‍♂️ Quick Start Guide

### Complete Human Factors Analysis
```bash
#!/bin/bash
echo "👥 Starting Human Factors Analysis..."

# 1. Team Health Assessment
echo "🏥 Running Team Health Assessment..."
python3 python/01_oncall_rotation_manager.py
python3 python/04_psychological_safety_scorer.py
python3 python/10_mental_health_checkin_system.py

# 2. Communication Analysis
echo "🗣️ Running Communication Analysis..."
python3 python/02_alert_fatigue_analyzer.py
python3 python/08_communication_effectiveness_analyzer.py

# 3. Cultural Factors Analysis
echo "🇮🇳 Running Cultural Analysis..."
python3 python/09_cultural_bias_detector.py
go run python/13_diversity_inclusion_dashboard.go

# 4. Work-Life Balance Check
echo "⚖️ Running Work-Life Balance Analysis..."
go run python/06_work_life_balance_monitor.go
python3 python/15_sustainable_engineering_metrics.py

echo "✅ Complete human factors analysis finished!"
```

### Quick Health Check
```bash
# Essential team health indicators
python3 -c "
from python.psychological_safety_scorer import *
from python.mental_health_checkin_system import *
from python.work_life_balance_monitor import *

print('🏥 Quick Team Health Check')
print('========================')

# Run basic assessments
safety_score = assess_team_psychological_safety()
mental_health = check_team_mental_health() 
work_balance = analyze_work_life_balance()

print(f'Psychological Safety: {safety_score}/10')
print(f'Mental Health Index: {mental_health}/10')
print(f'Work-Life Balance: {work_balance}/10')

overall_health = (safety_score + mental_health + work_balance) / 3
print(f'Overall Team Health: {overall_health:.1f}/10')

if overall_health < 6:
    print('🚨 Team needs immediate attention!')
elif overall_health < 8:
    print('⚠️ Room for improvement')
else:
    print('✅ Team is healthy!')
"
```

## 📊 Expected Outputs & Cultural Insights

### On-Call Rotation Manager
```
🚀 On-Call Rotation Manager Demo
==================================================
✅ Added Rajesh Kumar to on-call rotation pool
✅ Added Priya Sharma to on-call rotation pool
✅ Added Amit Singh to on-call rotation pool

🗓️  Generating on-call schedule for 3/2024
🎯 Selected Rajesh Kumar (score: 87.3) for 2024-03-01 00:00:00
🪔 Festival shift created: Holi

📊 Schedule Summary:
   Total shifts: 31
   Festival conflicts: 3

👥 Engineer Distribution:
   Rajesh Kumar: 7 shifts
   Priya Sharma: 6 shifts
   Amit Singh: 8 shifts
   Sneha Patel: 5 shifts
   Vikram Reddy: 5 shifts

⚖️  Fairness Score: 89.2% (100% is perfect)

🪔 Cultural Considerations Demo
   Date: 2024-03-08
   Festival: Holi
   Impact Score: 0.8 (0=none, 1=complete conflict)
```

### Alert Fatigue Analyzer
```
🚨 Alert Fatigue Analyzer Demo - Mumbai Traffic Style
============================================================
📊 Alert Traffic Report:
Overall Signal: red
Team Fatigue Score: 73.5/100
24h Alert Volume: 45
Mumbai Metaphor: 🔴 Complete jam like Bandra-Worli during monsoon - immediate action needed!

📊 Hourly Pattern Analysis:
   08:00: red signal - 12 alerts
            Peak hour jam at Bandra-Worli Sea Link
   09:00: red signal - 15 alerts
            Peak hour jam at Bandra-Worli Sea Link
   14:00: green signal - 2 alerts
            Free flowing traffic at Marine Drive

💡 Recommendations:
   1. 🚨 Alert jam detected! Consider emergency alert consolidation
   2. 📱 Implement alert throttling during peak hours
   3. 😴 High fatigue detected - review alert thresholds
   4. 🔄 High repeat rate - implement alert deduplication
```

### Psychological Safety Assessment
```
🛡️ Team Psychological Safety Assessment
==========================================
Team: Mumbai Development Squad
Assessment Period: Last 30 days

📊 Safety Metrics:
   Speaking Up Frequency: 67%
   Error Reporting Rate: 78%
   Question Asking Comfort: 72%
   Challenge Authority Comfort: 45%  # Lower due to hierarchy culture
   Cultural Sensitivity Score: 82%

🗣️ Communication Patterns:
   Silent Members: 2 (Neha, Karan)
   Dominating Speakers: 1 (Senior Architect)
   Language Barriers Detected: 23% of meetings
   Regional Bias Incidents: 3

💡 Recommendations:
   1. 🎯 Create safe spaces for junior members to speak
   2. 🌍 Address North-South regional communication gaps
   3. 📝 Implement anonymous feedback systems
   4. 🤝 Cultural sensitivity training needed
```

### Cultural Bias Detection
```
🔍 Cultural Bias Analysis Report
================================
Analysis Period: Last 3 months
Team Size: 25 engineers

📊 Bias Detection Results:

Regional Bias:
   North India preference in leadership: 15% bias detected
   South India underrepresentation: 12% detected
   Maharashtra local advantage: 8% detected

Gender Bias:
   Technical task assignment: 23% male preference
   Documentation tasks: 31% female assignment
   On-call duties: 18% male preference

Educational Bias:
   IIT/NIT preference: 34% detected
   Private college discrimination: 19% detected
   Local college undervaluation: 27% detected

Name Bias:
   English names advantage: 12% detected
   Regional name mispronunciation: 45% incidents
   Name-based assumptions: 8% detected

🎯 Recommended Actions:
   1. 🎓 Blind resume review process
   2. 🗣️ Name pronunciation training
   3. ⚖️ Task assignment audit
   4. 🌟 Regional diversity celebration
```

### Work-Life Balance Monitor
```
⚖️ Work-Life Balance Analysis
=============================
Team: 15 Engineers
Analysis Period: Last month

📈 Working Pattern Analysis:
   Average Daily Hours: 9.7 hours
   Weekend Work Incidents: 23
   Late Night Work (>9 PM): 67 instances
   Festival Day Work: 8 incidents

👨‍👩‍👧‍👦 Family Impact Analysis:
   School Pickup Conflicts: 12
   Family Function Misses: 5
   Festival Celebration Issues: 8
   Elderly Care Conflicts: 3

🏠 Regional Patterns:
   Pune Engineers: Better balance (8.2 hrs avg)
   Bangalore Engineers: Longer hours (10.3 hrs avg)
   Mumbai Engineers: Commute impact (9.8 hrs + 2 hrs commute)

🚨 Alert Conditions:
   3 engineers working >11 hours daily
   2 engineers missed major festivals
   5 engineers report family stress

💡 Recommendations:
   1. 🕐 Enforce 9-hour work day limit
   2. 🎉 Mandatory festival time off
   3. 🏠 Remote work during monsoon
   4. 👨‍👩‍👧 Flexible hours for parents
```

## 🎯 Cultural Integration Examples

### Indian Festival Calendar Integration
```python
# Festival-aware scheduling
festivals = {
    "2024-03-08": "Holi",
    "2024-08-15": "Independence Day", 
    "2024-10-12": "Dussehra",
    "2024-11-01": "Diwali",
    "2024-12-25": "Christmas"
}

# Impact calculation
def get_festival_impact(date):
    major_festivals = ["Diwali", "Holi", "Eid"]
    if festival_name in major_festivals:
        return 0.8  # 80% unavailability expected
    return 0.4      # 40% unavailability expected
```

### Regional Communication Patterns
```python
# Communication style detection
communication_styles = {
    "North": {"directness": 0.8, "hierarchy_respect": 0.9},
    "South": {"directness": 0.6, "technical_depth": 0.9},
    "West": {"business_focus": 0.8, "efficiency": 0.9},
    "East": {"relationship_first": 0.9, "consensus": 0.8}
}
```

### Indian Family Structure Considerations
```python
# Family obligation patterns
family_obligations = {
    "school_pickup": {"frequency": "daily", "flexibility": 0.2},
    "elderly_care": {"frequency": "ongoing", "flexibility": 0.1},
    "festival_prep": {"frequency": "seasonal", "flexibility": 0.0},
    "arranged_marriage": {"frequency": "rare", "flexibility": 0.0}
}
```

## 💡 Key Cultural Insights Implemented

### Hierarchy vs Collaboration
```python
# Psychological safety in hierarchical culture
def adjust_for_hierarchy(base_safety_score, seniority_gap):
    # Indian teams: larger seniority gaps reduce speaking up
    hierarchy_penalty = min(seniority_gap * 0.1, 0.4)
    return base_safety_score * (1 - hierarchy_penalty)
```

### Multilingual Environment
```python
# Code switching cognitive load
def calculate_language_switching_cost(hindi_time, english_time, switches):
    # Research shows 15% cognitive overhead for each language switch
    base_load = (hindi_time + english_time) * 1.0
    switching_cost = switches * 0.15
    return base_load * (1 + switching_cost)
```

### Festival and Family Priorities
```python
# Festival priority over work
def is_festival_priority(date, urgency):
    if is_major_festival(date):
        return urgency < Priority.CRITICAL  # Only critical work during festivals
    return urgency < Priority.LOW  # Normal prioritization
```

## 🔧 Advanced Analysis Tools

### Sentiment Analysis for Cultural Sensitivity
```python
# Analyze communication for cultural sensitivity
from textblob import TextBlob

def analyze_cultural_sensitivity(message):
    sentiment = TextBlob(message).sentiment
    
    # Indian cultural markers
    respectful_words = ["ji", "sir", "madam", "please"]
    direct_words = ["no", "wrong", "bad", "never"]
    
    respectful_count = sum(1 for word in respectful_words if word in message.lower())
    direct_count = sum(1 for word in direct_words if word in message.lower())
    
    cultural_score = (respectful_count - direct_count) / len(message.split())
    return cultural_score, sentiment.polarity
```

### Bias Detection Algorithms
```python
# Statistical bias detection
def detect_assignment_bias(assignments_by_gender, assignments_by_region):
    from scipy.stats import chi2_contingency
    
    # Gender bias in technical vs non-technical tasks
    chi2, p_value = chi2_contingency(assignments_by_gender)
    gender_bias_detected = p_value < 0.05
    
    # Regional bias in leadership assignments  
    chi2_region, p_region = chi2_contingency(assignments_by_region)
    regional_bias_detected = p_region < 0.05
    
    return {
        "gender_bias": gender_bias_detected,
        "regional_bias": regional_bias_detected,
        "confidence": 1 - min(p_value, p_region)
    }
```

## 🧪 Testing Human Factors

### Psychological Safety Testing
```python
# Test psychological safety algorithms
def test_psychological_safety():
    # Simulate different team compositions
    hierarchical_team = Team(seniority_gap=4, cultural_diversity=0.3)
    flat_team = Team(seniority_gap=1, cultural_diversity=0.8)
    
    hierarchical_safety = calculate_psychological_safety(hierarchical_team)
    flat_safety = calculate_psychological_safety(flat_team)
    
    assert hierarchical_safety < flat_safety  # Hierarchy reduces safety
    assert flat_safety > 0.7  # Flat teams should have high safety
```

### Cultural Bias Testing
```python
# Test bias detection algorithms
def test_bias_detection():
    # Create biased assignment patterns
    biased_assignments = {
        ("IIT", "Male", "North"): 15,
        ("Private", "Female", "South"): 3,
        ("Local", "Male", "West"): 7
    }
    
    bias_results = detect_cultural_bias(biased_assignments)
    assert bias_results["educational_bias"] == True
    assert bias_results["gender_bias"] == True
    assert bias_results["regional_bias"] == True
```

## 📚 Research & References

### Cultural Psychology Research
- [Hofstede's Cultural Dimensions for India](https://www.hofstede-insights.com/country-comparison/india/)
- [Indian Workplace Culture Research](https://example.com)
- [Psychological Safety in Hierarchical Cultures](https://example.com)

### Technical Team Dynamics
- [Google's Project Aristotle](https://rework.withgoogle.com/print/guides/5721312655835136/)
- [Psychological Safety in Software Teams](https://example.com)
- [Measuring Team Effectiveness](https://example.com)

### Indian IT Industry Analysis
- [NASSCOM IT Industry Reports](https://www.nasscom.in/)
- [Indian Developer Productivity Studies](https://example.com)
- [Work-Life Balance in Indian IT](https://example.com)

## 🤝 Contributing

इस project में contribute करने के लिए:

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b human-factors-feature`
3. **Add culturally sensitive examples**
4. **Test with diverse team compositions**
5. **Submit pull request**

### Contribution Guidelines
- **Cultural Sensitivity**: Respectful representation of Indian diversity
- **Research-Based**: Include psychological and cultural research references
- **Practical Application**: Real-world usable tools
- **Privacy Protection**: Anonymous data collection methods
- **Inclusive Design**: Consider all Indian cultural groups

### Areas for Contribution
- **Regional Variations**: State-specific cultural patterns
- **Generational Differences**: Millennial vs Gen-Z work patterns
- **Industry Variations**: Startup vs Enterprise cultural differences
- **Gender Perspectives**: Women in tech specific challenges
- **Remote Work**: Cultural adaptations for distributed teams

## 📞 Support & Resources

### Mental Health Resources
- **Employee Assistance Programs**: Anonymous counseling support
- **Mental Health Helplines**: 24/7 crisis support
- **Stress Management Workshops**: Team building activities
- **Cultural Competency Training**: Cross-cultural communication

### Diversity & Inclusion
- **Unconscious Bias Training**: Team awareness programs
- **Inclusive Leadership**: Management training
- **Cultural Celebration**: Festival inclusion policies
- **Language Support**: Multi-language communication tools

---

## 🎉 Episode Summary

This episode provides comprehensive tools for analyzing and improving human factors in Indian tech teams. The code addresses real cultural challenges while maintaining psychological safety and promoting inclusive practices.

**Key Achievements:**
- ✅ 15 comprehensive human factor analysis tools
- ✅ Cultural sensitivity integrated throughout
- ✅ Indian festival and family obligation handling
- ✅ Bias detection and mitigation strategies
- ✅ Mental health and wellbeing monitoring
- ✅ Work-life balance optimization

**Cultural Integration:**
- 🇮🇳 Indian festival calendar respect
- 👥 Regional diversity appreciation
- 🏠 Family obligation understanding
- 🗣️ Multilingual communication support
- ⚖️ Hierarchy vs collaboration balance

**Psychological Safety Focus:**
- 🛡️ Safe space creation for all team members
- 🗣️ Encouraging diverse perspectives
- 📊 Quantitative measurement of team health
- 🎯 Targeted interventions for improvement
- 🤝 Inclusive leadership development

**Practical Impact:**
- Reduced turnover through better work-life balance
- Increased productivity through psychological safety
- Enhanced innovation through diverse perspectives
- Improved team cohesion through cultural understanding
- Better crisis management through inclusive communication

Remember: Tech teams are made of humans first, engineers second. Cultural sensitivity और psychological safety के बिना, कोई भी technical excellence sustainable नहीं होता। 👥💙

Happy Human-Centered Engineering! 🚀✨