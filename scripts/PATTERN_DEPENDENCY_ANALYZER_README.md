# Pattern Dependency Analyzer

A comprehensive tool for analyzing pattern relationships and building dependency graphs in the DStudio pattern library.

## Overview

This analyzer examines all pattern files in the pattern library, extracts relationship information, builds a directed dependency graph, and generates insights about pattern connectivity. It identifies hub patterns, isolated patterns, and provides recommendations for improving pattern interconnectivity.

## Features

### 🔍 Analysis Capabilities
- **Pattern Parsing**: Extracts metadata and relationships from 150+ pattern markdown files
- **Dependency Graph**: Builds directed graph showing pattern relationships  
- **Hub Detection**: Identifies most connected and influential patterns
- **Isolation Analysis**: Finds patterns with no documented relationships
- **Category Analysis**: Examines connectivity within and across categories
- **Relationship Extraction**: Parses "Related Patterns", "See Also", and "References" sections

### 📊 Export Formats
- **JSON**: Complete analysis data for programmatic access
- **GraphML**: Graph data for visualization in Gephi, Cytoscape, etc.
- **Markdown**: Human-readable summary reports
- **PNG**: Network visualization charts and heatmaps

### 🎯 Key Metrics
- Graph connectivity metrics (density, components, degree distribution)
- Pattern hub scores and rankings
- Cross-category relationship mapping  
- Isolated pattern identification
- Bidirectional relationship detection

## Generated Files

### Core Analysis Files

#### `pattern_dependency_analysis.json`
Complete analysis data in JSON format containing:
- Metadata (150 patterns, 21 relationships, 11 categories)
- Graph metrics (density: 0.001, components: 137)
- Pattern statistics (most referenced, hub rankings)
- Category analysis (internal/external connections)
- Isolated patterns list (134 patterns)
- Recommendations for improvement

#### `pattern_dependency_graph.graphml`
NetworkX-compatible GraphML file for visualization in:
- **Gephi**: Interactive network exploration
- **Cytoscape**: Detailed node analysis
- **yEd**: Professional graph layouts
- **Networkx**: Python analysis

#### `pattern_dependency_report.md`
Human-readable summary report with:
- Executive summary of findings
- Top hub patterns and their connections
- Category distribution and connectivity
- List of isolated patterns needing attention
- Actionable recommendations

### Visualization Files

#### `pattern_network_overview.png`
Four-panel overview showing:
- Network graph (connected components only)
- Category distribution bar chart
- Hub pattern rankings
- Connectivity metrics summary

#### `pattern_category_heatmap.png`
Cross-category relationship heatmap revealing:
- Internal category connections (diagonal)
- Cross-category relationship flows
- Connectivity gaps between categories

#### `isolated_patterns_chart.png`
Analysis of isolated patterns:
- Count of isolated patterns per category
- Comparison of total vs connected patterns by category

### Insights Report

#### `pattern_ecosystem_insights.md`
Comprehensive ecosystem analysis including:
- Critical issues identified (89% patterns isolated)
- Actionable recommendations by priority
- Impact assessment of improvements
- Visualization strategy guidance
- Implementation roadmap

## Usage

### Basic Analysis
```bash
# Run with default settings
python3 pattern_dependency_analyzer.py

# Custom paths
python3 pattern_dependency_analyzer.py \
  --library-path /path/to/patterns \
  --output-dir /path/to/output
```

### Generate Visualizations
```bash
# Creates PNG charts (requires matplotlib)
python3 visualize_pattern_network.py
```

### Command Line Options
```
--library-path    Path to pattern library (default: docs/pattern-library)
--output-dir      Output directory (default: scripts)
--json-output     JSON filename (default: pattern_dependency_analysis.json)
--graphml-output  GraphML filename (default: pattern_dependency_graph.graphml)
--report-output   Report filename (default: pattern_dependency_report.md)
```

## Key Findings

### 🚨 Critical Issues
- **89% patterns isolated**: 134 out of 150 patterns have no relationships
- **Category silos**: Most categories have zero internal connections
- **Low connectivity**: Graph density of only 0.001
- **137 components**: Highly fragmented ecosystem

### 🏆 Top Hub Patterns
1. **Circuit Breaker** (Hub Score: 16) - Most referenced resilience pattern
2. **Health Check** (Hub Score: 8) - Key monitoring pattern  
3. **Bulkhead** (Hub Score: 6) - Important isolation pattern
4. **Timeout** (Hub Score: 5) - Fundamental resilience mechanism
5. **Saga** (Hub Score: 4) - Distributed transaction pattern

### 📈 Category Analysis
- **Resilience**: Best connected (15 internal connections)
- **Data Management**: Some connectivity (4 internal connections)
- **Architecture**: Zero internal connections despite 20 patterns
- **Scaling**: Zero internal connections despite 25 patterns

## Dependencies

### Python Requirements
```
networkx>=2.0    # Graph analysis and algorithms
pyyaml>=5.0      # YAML frontmatter parsing
matplotlib>=3.0  # Visualization (optional)
```

### Install Dependencies
```bash
pip install networkx pyyaml matplotlib
```

## Architecture

### Class Structure
- **`PatternDependencyAnalyzer`**: Main analysis engine
- **`Pattern`**: Data class for pattern metadata
- **`PatternNetworkVisualizer`**: Visualization generator

### Analysis Pipeline
1. **Discovery**: Find all pattern markdown files
2. **Parsing**: Extract frontmatter and relationships
3. **Graph Building**: Create NetworkX directed graph
4. **Analysis**: Calculate metrics and identify patterns
5. **Export**: Generate JSON, GraphML, and reports
6. **Visualization**: Create charts and network diagrams

### Relationship Extraction
The analyzer uses regex patterns to extract relationships from:
- `## Related Patterns` sections
- `## See Also` sections  
- `## References` sections
- Inline markdown links to pattern files

## Visualization Strategy

### Network Analysis Tools
- **Gephi**: Best for interactive exploration and community detection
- **Cytoscape**: Excellent for biological-style network analysis
- **yEd**: Professional graph layout algorithms
- **D3.js**: Web-based interactive visualizations

### Recommended Layouts
- **Force-directed**: Shows natural clustering
- **Hierarchical**: Reveals hub-spoke relationships
- **Circular**: Good for category-based grouping
- **Geographic**: Can map to system architecture

### Visual Encoding
- **Node Color**: Pattern category
- **Node Size**: Hub score (degree centrality)  
- **Edge Color**: Relationship type
- **Edge Width**: Relationship strength
- **Clustering**: Community detection results

## Improvement Recommendations

### Immediate Actions (High Priority)
1. **Add relationships for top hub patterns** (Circuit Breaker, Health Check, etc.)
2. **Create internal connections within categories** (Architecture, Scaling)
3. **Bridge category boundaries** (Resilience ↔ Architecture)

### Medium Term
4. **Implement pattern tagging system**
5. **Create pattern combination guides**  
6. **Build pattern decision trees**

### Long Term
7. **Establish pattern quality metrics**
8. **Create interactive pattern explorer**
9. **Implement smart pattern recommendations**

## Examples

### Finding Most Referenced Patterns
```python
from pattern_dependency_analyzer import PatternDependencyAnalyzer

analyzer = PatternDependencyAnalyzer('docs/pattern-library')
analysis = analyzer.analyze_patterns()

# Top 5 most referenced patterns
top_patterns = analysis['pattern_statistics']['most_referenced'][:5]
for pattern, count in top_patterns:
    print(f"{pattern}: {count} references")
```

### Identifying Missing Relationships
```python
# Find patterns that should be related but aren't
isolated = analysis['isolated_patterns']
important_isolated = [p for p in isolated if 'event' in p['name'].lower()]
print("Important isolated patterns:", important_isolated)
```

### Export for Gephi Analysis
```python
# Export GraphML for advanced network analysis
analyzer.export_graphml('pattern_network.graphml')
```

## Contributing

### Adding New Analysis Features
1. Fork and create feature branch
2. Add analysis methods to `PatternDependencyAnalyzer`
3. Update `generate_analysis()` method
4. Add tests and documentation
5. Submit pull request

### Improving Relationship Extraction
1. Add new regex patterns to `relationship_patterns`
2. Test against sample pattern files
3. Update pattern normalization logic if needed

### Adding Visualizations
1. Extend `PatternNetworkVisualizer` class
2. Follow existing naming conventions
3. Use consistent color scheme from `category_colors`

## Troubleshooting

### Common Issues

**GraphML Export Fails**
```
Error: GraphML writer does not support <NoneType>
```
Solution: The analyzer filters None values before export

**Low Relationship Count**
- Check regex patterns match your markdown format
- Verify pattern files have "Related Patterns" sections
- Ensure markdown links use correct format

**Missing Categories**
- Update `category_colors` dict for new categories
- Check file path structure matches expected format

### Performance
- Analysis of 150 patterns takes ~5 seconds
- GraphML generation takes ~1 second
- Visualization creation takes ~10 seconds

## Future Enhancements

### Planned Features
- **Semantic relationship analysis** using NLP
- **Pattern complexity scoring** based on content
- **Automatic relationship suggestion**
- **Interactive web dashboard**
- **Pattern evolution tracking over time**
- **Integration with pattern template validation**

### Research Opportunities
- **Community detection algorithms** for pattern grouping
- **Centrality measures** for identifying critical patterns
- **Graph evolution analysis** over multiple versions
- **Pattern dependency cycles** detection and resolution

---

*Generated by Pattern Dependency Analyzer v1.0 - Part of DStudio Pattern Library Ecosystem*