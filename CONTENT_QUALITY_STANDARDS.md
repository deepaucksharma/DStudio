# Content Quality Standards

## Core Principles

### 1. Specificity Over Generalization
- **Always include concrete numbers**: latencies, scale, percentages
- **Use real production examples**: with dates, companies, impact
- **Avoid vague terms**: "high performance" → "sub-10ms p99 latency"

### 2. Dense Information Architecture
- **Tables > Paragraphs**: Use comparison tables for features, trade-offs
- **Bullet points > Prose**: For lists, steps, characteristics  
- **Diagrams > Descriptions**: Mermaid for architectures, flows
- **Code > Concepts**: Show actual implementation patterns

### 3. Cross-Reference Everything
Every major topic should include:
```markdown
## Related Topics

### Related Laws & Axioms
- [Law N: Name](/part1-axioms/lawN/) - How it relates

### Related Patterns  
- [Pattern Name](/patterns/pattern/) - Connection explained

### Related Pillars
- [Pillar N: Name](/part2-pillars/pillar/) - Relationship

### Case Studies
- [Company System](/case-studies/study/) - Real implementation
```

### 4. Visual Hierarchy
- Use icons consistently (Material Design icons)
- Grid cards for navigation sections
- Custom boxes (axiom-box, decision-box) for key concepts
- Maintain visual breathing room

### 5. Technical Accuracy
- Include mathematical formulas where relevant
- Show complexity analysis (Big O)
- Provide performance benchmarks
- Reference academic papers

## Anti-Patterns to Avoid

1. **Removing Quantitative Data**: Never replace numbers with qualitative descriptions
2. **Over-Styling**: Don't sacrifice readability for mobile optimization
3. **Verbose Explanations**: Every sentence must add unique value
4. **Generic Examples**: Use real company failures and successes
5. **Isolated Content**: Every page should link to related concepts

## Quality Checklist

Before committing any content:
- [ ] All metrics have specific numbers
- [ ] Real-world examples with dates/impact
- [ ] Comparison tables for trade-offs
- [ ] Mermaid diagrams for architecture
- [ ] Related Topics section complete
- [ ] Mobile and desktop readable
- [ ] No redundant explanations
- [ ] Cross-references verified