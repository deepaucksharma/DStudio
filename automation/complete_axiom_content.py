#!/usr/bin/env python3
"""
Complete Axiom Content Script

Adds missing fundamental sections to axiom files:
- The Constraint (core physics principle)
- Why It Matters (business impact)
- Common Misconceptions (clarify confusion)
- Practical Implications (engineering guidance)

These sections are critical for establishing the foundational
nature of axioms in distributed systems.
"""

import os
import re
from pathlib import Path

class AxiomContentCompleter:
    def __init__(self, docs_dir="/Users/deepaksharma/syc/DStudio/docs"):
        self.docs_dir = Path(docs_dir)
        self.axiom_definitions = {
            "axiom1-latency": {
                "title": "Latency (Speed of Light)",
                "constraint": "Information cannot travel faster than the speed of light in any medium",
                "physics_basis": "Einstein's special relativity + Maxwell's equations",
                "practical_limit": "~200,000 km/s in fiber optic cable",
                "why_matters": "Every network call pays a physics tax that no engineering can eliminate",
                "misconceptions": [
                    "5G or better networks can eliminate latency",
                    "Caching solves all latency problems",
                    "Latency only matters for real-time applications"
                ],
                "implications": [
                    "Design for geography: place computation close to users",
                    "Cache strategically: balance hit rates vs staleness",
                    "Optimize for round trips: minimize network calls",
                    "Budget latency: treat it like financial budget"
                ]
            },
            "axiom2-capacity": {
                "title": "Finite Capacity",
                "constraint": "Every resource has a maximum throughput or storage limit",
                "physics_basis": "Thermodynamics: energy and matter are finite",
                "practical_limit": "CPU cycles, memory bytes, network bandwidth, disk IOPS",
                "why_matters": "Systems hit hard limits and degrade non-linearly beyond 70-80% utilization",
                "misconceptions": [
                    "Cloud resources are infinite",
                    "Adding more servers always improves performance",
                    "Capacity problems can be solved by better algorithms alone"
                ],
                "implications": [
                    "Monitor utilization AND saturation metrics",
                    "Implement backpressure and load shedding",
                    "Plan capacity with safety margins (70% rule)",
                    "Design for graceful degradation"
                ]
            },
            "axiom3-failure": {
                "title": "Inevitable Failure",
                "constraint": "All components will fail eventually with non-zero probability",
                "physics_basis": "Second law of thermodynamics: entropy always increases",
                "practical_limit": "Hardware MTBF, software bugs, human errors, network partitions",
                "why_matters": "Failure is not an exception case—it's the normal operating condition",
                "misconceptions": [
                    "Good engineering can prevent all failures",
                    "Redundancy eliminates failure risk",
                    "Cloud providers handle all failure scenarios"
                ],
                "implications": [
                    "Design for failure as the default case",
                    "Implement circuit breakers and timeouts",
                    "Practice chaos engineering and failure injection",
                    "Build observable and debuggable systems"
                ]
            },
            "axiom4-concurrency": {
                "title": "Coordination Overhead",
                "constraint": "Coordinating concurrent operations requires communication overhead",
                "physics_basis": "Information theory: coordination requires message passing",
                "practical_limit": "Consensus protocols, locks, synchronization primitives",
                "why_matters": "Coordination overhead grows non-linearly with participants",
                "misconceptions": [
                    "More threads always improve performance",
                    "Distributed consensus is just like local locking",
                    "Eventual consistency is always acceptable"
                ],
                "implications": [
                    "Minimize coordination points in design",
                    "Use eventual consistency where possible",
                    "Partition data to reduce coordination scope",
                    "Understand CAP theorem trade-offs"
                ]
            },
            "axiom5-coordination": {
                "title": "Time and Ordering",
                "constraint": "There is no global clock in distributed systems",
                "physics_basis": "Einstein's relativity: simultaneity is relative",
                "practical_limit": "Network delays, clock drift, Byzantine failures",
                "why_matters": "Cannot determine absolute ordering of events across nodes",
                "misconceptions": [
                    "NTP synchronization provides perfect time",
                    "Logical clocks solve all ordering problems",
                    "Database timestamps are globally consistent"
                ],
                "implications": [
                    "Use vector clocks or logical timestamps",
                    "Design for eventual consistency",
                    "Avoid distributed transactions when possible",
                    "Accept that some operations cannot be perfectly ordered"
                ]
            },
            "axiom6-observability": {
                "title": "Limited Observability",
                "constraint": "You cannot observe everything in a distributed system",
                "physics_basis": "Heisenberg uncertainty principle + information theory limits",
                "practical_limit": "Observer effect, finite bandwidth, sampling limits",
                "why_matters": "Debugging and monitoring have fundamental limitations",
                "misconceptions": [
                    "More metrics always improve observability",
                    "Distributed tracing captures everything",
                    "Perfect monitoring is achievable"
                ],
                "implications": [
                    "Design systems to be inherently observable",
                    "Use structured logging and distributed tracing",
                    "Focus on business metrics, not just technical ones",
                    "Accept uncertainty in distributed debugging"
                ]
            },
            "axiom7-human": {
                "title": "Human Interface Constraints",
                "constraint": "Humans have cognitive and physical limitations",
                "physics_basis": "Neuroscience: working memory, reaction time, attention limits",
                "practical_limit": "7±2 items in working memory, 250ms reaction time",
                "why_matters": "System complexity must match human cognitive capacity",
                "misconceptions": [
                    "Users will read documentation",
                    "More features always improve user experience",
                    "Cognitive load doesn't affect system design"
                ],
                "implications": [
                    "Design simple, intuitive interfaces",
                    "Minimize cognitive load and decision fatigue",
                    "Provide clear error messages and recovery paths",
                    "Consider human factors in architecture decisions"
                ]
            },
            "axiom8-economics": {
                "title": "Economic Constraints",
                "constraint": "All resources have finite economic cost",
                "physics_basis": "Scarcity: limited resources vs unlimited wants",
                "practical_limit": "Budget, time-to-market, opportunity cost",
                "why_matters": "Technical decisions have economic consequences",
                "misconceptions": [
                    "Engineer for perfect solution regardless of cost",
                    "Premature optimization is always bad",
                    "Free services have no cost"
                ],
                "implications": [
                    "Optimize for business value, not technical perfection",
                    "Consider total cost of ownership (TCO)",
                    "Make trade-offs explicit and measurable",
                    "Design for cost efficiency from the start"
                ]
            }
        }
        
        self.processed_files = []
        self.skipped_files = []
        self.errors = []

    def find_axiom_files(self):
        """Find all axiom index.md files"""
        axiom_pattern = self.docs_dir / "part1-axioms" / "axiom*" / "index.md"
        return list(self.docs_dir.glob("part1-axioms/axiom*/index.md"))

    def has_constraint_section(self, content):
        """Check if file already has constraint section"""
        patterns = [
            r"##\s+The Constraint",
            r"##\s+.*Constraint.*",
            r"###\s+The Constraint",
            r"###\s+.*Constraint.*"
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False

    def extract_axiom_id(self, file_path):
        """Extract axiom ID from file path"""
        parts = file_path.parts
        for part in parts:
            if part.startswith("axiom") and "-" in part:
                return part
        return None

    def generate_constraint_section(self, axiom_id):
        """Generate the constraint section content for an axiom"""
        if axiom_id not in self.axiom_definitions:
            return None
            
        axiom = self.axiom_definitions[axiom_id]
        
        section = f"""
## 🔥 The Constraint

### The Fundamental Limit

**{axiom['constraint']}**

This constraint emerges from **{axiom['physics_basis']}**. No amount of engineering can violate this fundamental principle—we can only work within its boundaries.

### Physics Foundation

The practical manifestation of this constraint:
- **Theoretical basis**: {axiom['physics_basis']}
- **Practical limit**: {axiom['practical_limit']}
- **Real-world impact**: {axiom['why_matters']}

### Why This Constraint Exists

Unlike software bugs or implementation details, this is a fundamental law of our universe. Understanding this constraint helps us:

1. **Set realistic expectations** - Know what's physically impossible
2. **Make better trade-offs** - Optimize within the possible
3. **Design robust systems** - Work with the constraint, not against it
4. **Avoid false solutions** - Don't chase impossible optimizations

!!! warning "Common Misconception"
    This constraint cannot be "solved" or "eliminated"—only managed and optimized within its boundaries.

---

## 💡 Why It Matters

{axiom['why_matters']}

### Business Impact

This constraint directly affects:
- **User experience**: Performance and reliability
- **Development velocity**: Time-to-market and maintenance
- **Operational costs**: Infrastructure and support
- **Competitive advantage**: System capabilities and scalability

### Technical Implications

Every engineering decision must account for this constraint:
- **Architecture patterns**: Choose designs that work with the constraint
- **Technology selection**: Pick tools that optimize within the boundaries
- **Performance optimization**: Focus on what's actually improvable
- **Monitoring and alerting**: Track metrics related to the constraint

---

## 🚫 Common Misconceptions

Many engineers hold false beliefs about this constraint:

"""
        
        for i, misconception in enumerate(axiom['misconceptions'], 1):
            section += f"{i}. **\"{misconception}\"**\n   - This violates the fundamental constraint\n   - Reality: {self.get_reality_check(axiom_id, misconception)}\n\n"
        
        section += f"""
### Reality Check

The constraint is absolute—these misconceptions arise from:
- **Wishful thinking**: Hoping engineering can overcome physics
- **Local optimization**: Solving one problem while creating others
- **Vendor marketing**: Oversimplified claims about complex systems
- **Incomplete understanding**: Not seeing the full system implications

---

## ⚙️ Practical Implications

How this constraint shapes real system design:

"""
        
        for i, implication in enumerate(axiom['implications'], 1):
            section += f"{i}. **{implication}**\n"
        
        section += f"""

### Engineering Guidelines

When designing systems, always:
- **Start with the constraint**: Acknowledge it in your architecture
- **Measure the constraint**: Monitor relevant metrics
- **Design around the constraint**: Use patterns that work with it
- **Communicate the constraint**: Help stakeholders understand limitations

### Success Patterns

Teams that respect this constraint:
- Set realistic performance goals
- Choose appropriate architectural patterns
- Invest in proper monitoring and observability
- Make trade-offs explicit and data-driven

---

"""
        return section

    def get_reality_check(self, axiom_id, misconception):
        """Get reality check for specific misconceptions"""
        reality_checks = {
            "axiom1-latency": {
                "5G or better networks can eliminate latency": "Speed of light still applies—5G reduces last-mile latency but can't overcome physics",
                "Caching solves all latency problems": "Cache misses still pay the full latency cost, and invalidation creates complexity",
                "Latency only matters for real-time applications": "Even batch systems are affected by latency in coordination and data movement"
            },
            "axiom2-capacity": {
                "Cloud resources are infinite": "Cloud providers have finite capacity and you pay for what you use",
                "Adding more servers always improves performance": "Coordination overhead can make more servers slower",
                "Capacity problems can be solved by better algorithms alone": "Better algorithms help but can't exceed hardware limits"
            },
            "axiom3-failure": {
                "Good engineering can prevent all failures": "Even redundant systems can fail in correlated ways",
                "Redundancy eliminates failure risk": "Redundancy reduces risk but adds complexity and new failure modes",
                "Cloud providers handle all failure scenarios": "You still need to design for application-level failures"
            }
        }
        
        return reality_checks.get(axiom_id, {}).get(misconception, "The constraint makes this impossible")

    def find_insertion_point(self, content):
        """Find where to insert constraint section"""
        # Look for the end of the quick links/navigation section
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # After quick links section
            if "Quick Links" in line:
                # Find the end of this section (next ## or ---)
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith('---') or lines[j].strip().startswith('## '):
                        return j
            
            # After navigation section  
            if "Navigation -->" in line:
                # Skip a few lines and find next section
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith('## '):
                        return j
        
        # Fallback: after first heading
        for i, line in enumerate(lines):
            if line.startswith('# ') and i > 10:  # Skip frontmatter
                # Find next section
                for j in range(i + 1, len(lines)):
                    if lines[j].strip().startswith('## '):
                        return j
        
        return len(lines)  # Insert at end if can't find good spot

    def process_axiom_file(self, file_path):
        """Process a single axiom file"""
        try:
            print(f"Processing {file_path}")
            
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already has constraint section
            if self.has_constraint_section(content):
                print(f"  ↳ Already has constraint section, skipping")
                self.skipped_files.append(str(file_path))
                return False
            
            # Extract axiom ID
            axiom_id = self.extract_axiom_id(file_path)
            if not axiom_id or axiom_id not in self.axiom_definitions:
                print(f"  ↳ Unknown axiom ID: {axiom_id}")
                self.errors.append(f"Unknown axiom ID: {axiom_id} in {file_path}")
                return False
            
            # Generate constraint section
            constraint_section = self.generate_constraint_section(axiom_id)
            if not constraint_section:
                print(f"  ↳ Could not generate constraint section")
                self.errors.append(f"Could not generate constraint section for {axiom_id}")
                return False
            
            # Find insertion point
            lines = content.split('\n')
            insertion_point = self.find_insertion_point(content)
            
            # Insert the new section
            lines.insert(insertion_point, constraint_section)
            new_content = '\n'.join(lines)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✓ Added constraint section for {axiom_id}")
            self.processed_files.append(str(file_path))
            return True
            
        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            print(f"  ✗ {error_msg}")
            self.errors.append(error_msg)
            return False

    def run(self):
        """Main execution function"""
        print("=== Axiom Content Completion Script ===\n")
        
        # Find all axiom files
        axiom_files = self.find_axiom_files()
        print(f"Found {len(axiom_files)} axiom files to process\n")
        
        if not axiom_files:
            print("No axiom files found!")
            return
        
        # Process each file
        for file_path in axiom_files:
            self.process_axiom_file(file_path)
            print()  # Add spacing
        
        # Generate summary report
        self.generate_report()

    def generate_report(self):
        """Generate summary report"""
        print("\n" + "="*60)
        print("AXIOM CONTENT COMPLETION REPORT")
        print("="*60)
        
        print(f"\n✅ SUCCESSFULLY PROCESSED: {len(self.processed_files)}")
        for file_path in self.processed_files:
            print(f"   • {file_path}")
        
        if self.skipped_files:
            print(f"\n⏭️  SKIPPED (already complete): {len(self.skipped_files)}")
            for file_path in self.skipped_files:
                print(f"   • {file_path}")
        
        if self.errors:
            print(f"\n❌ ERRORS: {len(self.errors)}")
            for error in self.errors:
                print(f"   • {error}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   • Total files found: {len(self.processed_files) + len(self.skipped_files) + len(self.errors)}")
        print(f"   • Successfully enhanced: {len(self.processed_files)}")
        print(f"   • Already complete: {len(self.skipped_files)}")
        print(f"   • Errors: {len(self.errors)}")
        
        if len(self.processed_files) > 0:
            print(f"\n🎉 SUCCESS: Added foundational constraint sections to {len(self.processed_files)} axiom files!")
            print("   These sections establish the physics-based foundation of distributed systems.")
        else:
            print(f"\n⚠️  No files were modified. All axiom files may already be complete.")

if __name__ == "__main__":
    completer = AxiomContentCompleter()
    completer.run()