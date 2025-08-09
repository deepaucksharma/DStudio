# Hindi Terminology Consistency Guide

## Master Dictionary - Technical Terms

### System Architecture (सिस्टम ढांचा)

| English Term | Primary Hindi | Alternative | Usage Context | Example |
|-------------|---------------|-------------|---------------|---------|
| Distributed System | बंटा हुआ सिस्टम | फैला हुआ सिस्टम | General | "पूरा सिस्टम अलग-अलग जगह बंटा है" |
| Microservices | छोटी-छोटी सर्विसेज़ | अलग-अलग दुकानें | Mumbai metaphor | "हर दुकान अपना काम करती है" |
| Monolith | एक बड़ा सिस्टम | सब कुछ एक साथ | Comparison | "पहले सब एक ही जगह था" |
| API | दरवाज़ा | संपर्क द्वार | Communication | "दो सिस्टम के बीच का दरवाज़ा" |
| Endpoint | अंतिम बिंदु | आखिरी पॉइंट | Technical | "जहाँ request पहुँचती है" |
| Service Mesh | सर्विस जाल | कनेक्शन नेटवर्क | Infrastructure | "सब services का जाल" |

### Data Management (डेटा प्रबंधन)

| English Term | Primary Hindi | Alternative | Usage Context | Example |
|-------------|---------------|-------------|---------------|---------|
| Database | डेटाबेस | गोदाम | Storage metaphor | "सारा डेटा के गोदाम में" |
| Cache | तुरंत मिलने वाला | पास का सामान | Speed context | "बार-बार काम आने वाला पास रखो" |
| Queue | कतार | लाइन | Ordering | "सब अपनी बारी का इंतज़ार करें" |
| Transaction | लेन-देन | कारोबार | Business | "पैसे का लेन-देन" |
| Consistency | एकरूपता | समानता | Data state | "सब जगह same डेटा" |
| Replication | नकल | कॉपी | Backup | "कई जगह कॉपी रखना" |

### Performance & Scale (प्रदर्शन और विस्तार)

| English Term | Primary Hindi | Alternative | Usage Context | Example |
|-------------|---------------|-------------|---------------|---------|
| Latency | देरी | विलंब | Time | "Response में देरी" |
| Throughput | रफ्तार | काम की गति | Speed | "प्रति सेकंड कितने काम" |
| Bandwidth | बैंडविड्थ | डेटा की सड़क | Network | "कितना डेटा जा सकता है" |
| Load | भार | बोझ | Pressure | "सिस्टम पर भार" |
| Scale | बढ़ाना/घटाना | विस्तार/संकुचन | Growth | "ज़रूरत के हिसाब से बढ़ाना" |
| Bottleneck | अड़चन | रुकावट | Problem | "जहाँ काम अटक जाता है" |

### Resilience Patterns (मजबूती के तरीके)

| English Term | Primary Hindi | Alternative | Usage Context | Example |
|-------------|---------------|-------------|---------------|---------|
| Circuit Breaker | MCB | सर्किट तोड़ने वाला | Electrical metaphor | "ज्यादा load पर MCB गिरा दो" |
| Retry | फिर कोशिश | दोबारा try | Attempts | "थोड़ी देर बाद फिर कोशिश" |
| Timeout | समय सीमा | टाइम खत्म | Deadline | "इतनी देर तक wait, फिर छोड़ दो" |
| Fallback | बैकअप प्लान | दूसरा रास्ता | Alternative | "ये नहीं तो वो" |
| Bulkhead | अलग डिब्बे | विभाजन | Isolation | "एक डिब्बे की आग दूसरे में ना जाए" |
| Throttling | गति नियंत्रण | स्पीड कंट्रोल | Rate limiting | "धीरे-धीरे requests लो" |

### Cloud & Infrastructure (बादल और ढांचा)

| English Term | Primary Hindi | Alternative | Usage Context | Example |
|-------------|---------------|-------------|---------------|---------|
| Cloud | क्लाउड | बादल सर्वर | Remote | "दूर के servers पर" |
| Region | क्षेत्र | इलाका | Geographic | "Mumbai region, Delhi region" |
| Zone | ज़ोन | एरिया | Availability | "अलग-अलग zones में" |
| Container | कंटेनर | डिब्बा | Packaging | "App का डिब्बा" |
| Virtual Machine | वर्चुअल मशीन | नकली कंप्यूटर | Virtualization | "एक मशीन में कई मशीनें" |
| Load Balancer | भीड़ बांटने वाला | लोड बैलेंसर | Distribution | "Traffic को बांटना" |

### Security (सुरक्षा)

| English Term | Primary Hindi | Alternative | Usage Context | Example |
|-------------|---------------|-------------|---------------|---------|
| Authentication | पहचान | सत्यापन | Identity | "तू कौन है?" |
| Authorization | अनुमति | इजाज़त | Permission | "तुझे ये करने की इजाज़त है?" |
| Encryption | ताला लगाना | कोड में बदलना | Protection | "डेटा पर ताला लगाना" |
| Token | टोकन | पास | Access | "Entry का पास" |
| Certificate | प्रमाण पत्र | सर्टिफिकेट | Verification | "पहचान का सबूत" |
| Firewall | दीवार | सुरक्षा दीवार | Protection | "बाहरी खतरों से बचाने वाली दीवार" |

### Operations (संचालन)

| English Term | Primary Hindi | Alternative | Usage Context | Example |
|-------------|---------------|-------------|---------------|---------|
| Deploy | तैनात करना | लगाना | Release | "नया version लगाना" |
| Rollback | वापस जाना | पुराने पर लौटना | Revert | "Problem हो तो पुराने version पर" |
| Monitor | निगरानी | नज़र रखना | Watching | "System पर नज़र" |
| Debug | गलती ढूंढना | डिबग करना | Troubleshoot | "कहाँ problem है" |
| Log | रिकॉर्ड | लॉग | History | "क्या-क्या हुआ का record" |
| Alert | चेतावनी | अलर्ट | Warning | "कुछ गड़बड़ है की चेतावनी" |

### Development (विकास)

| English Term | Primary Hindi | Alternative | Usage Context | Example |
|-------------|---------------|-------------|---------------|---------|
| Code | कोड | प्रोग्राम | Programming | "Program लिखना" |
| Bug | गलती | बग | Error | "Code में गलती" |
| Feature | फीचर | सुविधा | Functionality | "नई सुविधा" |
| Version | संस्करण | वर्जन | Release | "नया version" |
| Test | जांच | टेस्ट | Verification | "काम कर रहा है की जांच" |
| Release | रिलीज़ | जारी करना | Launch | "Public के लिए जारी करना" |

## Metaphor Consistency Rules

### Mumbai/City Metaphors
```
Distributed System = पूरा शहर
Service = मोहल्ला/दुकान
Database = गोदाम
Cache = पास की दुकान
Load Balancer = Traffic Police
Circuit Breaker = Building MCB
Message Queue = Post Office
API Gateway = Mall का main gate
Region = दूसरा शहर
Zone = अलग-अलग इलाके
```

### Train Metaphors
```
System = पूरी train
Service = अलग-अलग डिब्बे
Load = भीड़
Platform = Entry point
Signal = Control system
Track = Network path
Junction = Router
Station = Server
Ticket = Token/Authentication
```

### Daily Life Metaphors
```
Database = अलमारी/गोदाम
Cache = Fridge (तुरंत काम आने वाला)
Queue = Bank/Movie की line
Transaction = Shop में लेन-देन
Backup = Duplicate चाबी
Password = घर की चाबी
Firewall = घर की दीवार
Bug = गाड़ी में खराबी
```

## Usage Guidelines

### When to Use Hindi vs English

#### Always Hindi
- Basic concepts (देरी, रफ्तार, गलती)
- Actions (लगाना, हटाना, बदलना)
- Descriptions (बड़ा, छोटा, तेज़, धीमा)

#### Always English
- Brand names (AWS, Netflix, Google)
- Specific technologies (Kubernetes, Docker)
- Industry standard terms (API, HTTP, TCP/IP)

#### Context Dependent
- Technical terms - Use Hindi when explaining, English when referring
- Example: "Circuit Breaker जो है वो MCB की तरह काम करता है"

### Sentence Construction Patterns

#### Explaining Technical Concepts
```hindi
Pattern: [Technical term] + "मतलब" + [Simple explanation]
Example: "Latency मतलब response में देरी"

Pattern: [Technical term] + "यानी" + [Metaphor]
Example: "Database यानी सारे data का गोदाम"

Pattern: "जैसे" + [Daily example] + "वैसे ही" + [Technical concept]
Example: "जैसे घर में MCB गिरता है, वैसे ही Circuit Breaker"
```

#### Describing Actions
```hindi
Pattern: [Subject] + [Hindi verb] + [Object]
Example: "Server को restart करना पड़ेगा"

Pattern: [Condition] + "तो" + [Action]
Example: "Load बढ़े तो और servers लगा दो"
```

## Common Phrases Bank

### Opening Phrases
```hindi
- "चल, आज समझते हैं..."
- "कभी सोचा है कि..."
- "तेरे साथ भी हुआ होगा..."
- "आज की कहानी ये है कि..."
```

### Transition Phrases
```hindi
- "अब आता है असली पेंच..."
- "पर रुक, अभी और है..."
- "यहाँ से कहानी में twist..."
- "तो फिर क्या हुआ..."
```

### Explanation Phrases
```hindi
- "सीधी भाषा में..."
- "आसान शब्दों में..."
- "Example से समझो..."
- "तेरे घर में भी..."
```

### Closing Phrases
```hindi
- "बस यही है पूरा चक्कर"
- "समझ गया ना?"
- "अब तू भी कर सकता है"
- "यही है आज की सीख"
```

## Regional Variations

### Pan-India Terms
Use these for wider appeal:
- सिस्टम (not yantra)
- सर्वर (not seva-ganак)
- डेटा (not sankhya)
- नेटवर्क (not jaal)

### City-Specific Examples
Rotate between cities:
- Mumbai: Local train, Dabbawalas
- Delhi: Metro, Connaught Place
- Bangalore: IT Park, Traffic
- Kolkata: Tram, Howrah Bridge

## Quality Checklist

### Per Episode
- [ ] Consistent terminology throughout
- [ ] Same metaphor family used
- [ ] No mixing of formal/informal
- [ ] Regional balance maintained
- [ ] Technical accuracy preserved

### Cross-Episode
- [ ] Term consistency across series
- [ ] Metaphor evolution logical
- [ ] Complexity progression smooth
- [ ] Language maturity consistent

---

*Version*: 1.0
*Last Updated*: 2025-01-09
*For*: Hindi Content Production Team