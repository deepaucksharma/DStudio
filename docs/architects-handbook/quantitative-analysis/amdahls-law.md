---
title: Amdahl & Gustafson Laws
description: Laws governing parallel computing speedup - understanding the limits
  of parallelization and scalability
type: quantitative
difficulty: intermediate
reading_time: 40 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---


# Amdahl & Gustafson Laws

**The limits of parallelization**

!!! abstract "📊 Amdahl's Law Formula"

 <div>
 <div>
 <h3>$$\text{Speedup} = \frac{1}{s + p/n}$$</h3>
 
 <table class="responsive-table">
 <thead>
 <tr>
 <th>Variable</th>
 <th>Meaning</th>
 <th>Constraint</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Variable"><strong>s</strong></td>
 <td data-label="Meaning">Serial fraction (can't parallelize)</td>
 <td data-label="Constraint">0 ≤ s ≤ 1</td>
 </tr>
 <tr>
 <td data-label="Variable"><strong>p</strong></td>
 <td data-label="Meaning">Parallel fraction (can parallelize)</td>
 <td data-label="Constraint">0 ≤ p ≤ 1</td>
 </tr>
 <tr>
 <td data-label="Variable"><strong>n</strong></td>
 <td data-label="Meaning">Number of processors</td>
 <td data-label="Constraint">n ≥ 1</td>
 </tr>
 <tr>
 <td data-label="Variable"><strong>s + p</strong></td>
 <td data-label="Meaning">Total work</td>
 <td data-label="Constraint">= 1</td>
 </tr>
 </tbody>
</table>
 
 <div>
 <strong>💡 Key Insight:</strong> Serial bottlenecks dominate - even 5% serial work limits speedup to 20x maximum!
 </div>
</div>
</div>

## Examples

### Example 1: 95% Parallelizable
!!! note "📋 Example: 95% Parallelizable Code"
 <div>
 <div>
 <strong>Given:</strong> s = 0.05 (5% serial), p = 0.95 (95% parallel)
 
 <table class="responsive-table">
 <thead>
 <tr>
 <th>Processors</th>
 <th>Speedup</th>
 <th>Efficiency</th>
 <th>Visual Speedup</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Processors"><strong>1</strong></td>
 <td data-label="Speedup">1.0x</td>
 <td data-label="Efficiency">100%</td>
 <td data-label="Visual Speedup">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Processors"><strong>2</strong></td>
 <td data-label="Speedup">1.9x</td>
 <td data-label="Efficiency">95%</td>
 <td data-label="Visual Speedup">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Processors"><strong>4</strong></td>
 <td data-label="Speedup">3.5x</td>
 <td data-label="Efficiency">87%</td>
 <td data-label="Visual Speedup">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Processors"><strong>8</strong></td>
 <td data-label="Speedup">5.9x</td>
 <td data-label="Efficiency">74%</td>
 <td data-label="Visual Speedup">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Processors"><strong>16</strong></td>
 <td data-label="Speedup">8.4x</td>
 <td data-label="Efficiency">53%</td>
 <td data-label="Visual Speedup">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Processors"><strong>32</strong></td>
 <td data-label="Speedup">10.3x</td>
 <td data-label="Efficiency">32%</td>
 <td data-label="Visual Speedup">
 <div></div>
 </td>
 </tr>
 <tr>
 <td data-label="Processors"><strong>∞</strong></td>
 <td data-label="Speedup">20x</td>
 <td data-label="Efficiency">0%</td>
 <td data-label="Visual Speedup">
 <div></div>
 </td>
 </tr>
 </tbody>
</table>
 
 <div>
 <svg viewBox="0 0 500 300" role="img" aria-label="Speedup vs Processors chart showing performance scaling with 95% parallel code">
 <title>Speedup vs Processors (95% Parallel)</title>
 <desc>Chart showing how speedup increases with processor count for 95% parallelizable code, plateauing at 20x speedup due to 5% serial bottleneck</desc>
 <text x="250" y="20" text-anchor="middle" font-weight="bold">Speedup vs Processors (95% Parallel)</text>
 
 <!-- Axes -->
 <line x1="50" y1="250" x2="450" y2="250" stroke="#333" stroke-width="2"/>
 <line x1="50" y1="250" x2="50" y2="50" stroke="#333" stroke-width="2"/>
 
 <!-- Theoretical limit line -->
 <line x1="50" y1="70" x2="450" y2="70" stroke="#B71C1C" stroke-width="2" stroke-dasharray="5,5"/>
 <text x="460" y="75" font-size="10" fill="#B71C1C">20x limit</text>
 
 <!-- Speedup curve -->
 <path d="M 50 250 Q 150 150, 250 100 T 450 75" 
 stroke="#4CAF50" stroke-width="3" fill="none"/>
 
 <!-- Data points -->
 <circle cx="50" cy="250" r="3" fill="#4CAF50"/>
 <circle cx="100" cy="200" r="3" fill="#4CAF50"/>
 <circle cx="150" cy="150" r="3" fill="#66BB6A"/>
 <circle cx="200" cy="120" r="3" fill="#FF9800"/>
 <circle cx="250" cy="100" r="3" fill="#FF5722"/>
 <circle cx="300" cy="90" r="3" fill="#F44336"/>
 
 <!-- Labels -->
 <text x="50" y="270" text-anchor="middle" font-size="10">1</text>
 <text x="150" y="270" text-anchor="middle" font-size="10">4</text>
 <text x="250" y="270" text-anchor="middle" font-size="10">16</text>
 <text x="350" y="270" text-anchor="middle" font-size="10">64</text>
 <text x="450" y="270" text-anchor="middle" font-size="10">∞</text>
 <text x="250" y="290" text-anchor="middle" font-size="12">Processors</text>
 
 <text x="30" y="250" text-anchor="middle" font-size="10">1x</text>
 <text x="30" y="150" text-anchor="middle" font-size="10">10x</text>
 <text x="30" y="70" text-anchor="middle" font-size="10">20x</text>
 <text x="20" y="150" text-anchor="middle" font-size="12" transform="rotate(-90 20 150)">Speedup</text>
 </svg>
 </div>
 
 <div>
 <strong>🚨 Critical Insight:</strong> Even with infinite processors, maximum speedup = 1/0.05 = 20x
 </div>
</div>
</div>

### Quick Examples
```python
# Web request: 10ms auth + 90ms queries + 10ms format
Serial = 20/110 = 18% → Max speedup = 5.5x

# Data pipeline: 5% read + 80% transform + 10% aggregate + 5% write
Serial = 10% → Max speedup = 10x (even with 1000 cores!)
```

## Gustafson's Law

!!! abstract "🌐 Gustafson's Law Formula"

 <div>
 <div>
 <h3>$$\text{Speedup} = s + p \times n$$</h3>
 
 <table class="responsive-table">
 <thead>
 <tr>
 <th>Variable</th>
 <th>Meaning</th>
 <th>Key Difference</th>
 </tr>
 </thead>
 <tbody>
 <tr>
 <td data-label="Variable"><strong>s</strong></td>
 <td data-label="Meaning">Serial fraction of parallel execution</td>
 <td data-label="Key Difference">Based on parallel time</td>
 </tr>
 <tr>
 <td data-label="Variable"><strong>p</strong></td>
 <td data-label="Meaning">Parallel fraction</td>
 <td data-label="Key Difference">Scales with problem</td>
 </tr>
 <tr>
 <td data-label="Variable"><strong>n</strong></td>
 <td data-label="Meaning">Number of processors</td>
 <td data-label="Key Difference">Same as Amdahl</td>
 </tr>
 </tbody>
</table>
 
 <div>
 <strong>💡 Key Insight:</strong> Scale the problem, not just processors - larger problems often have better parallelism!
 </div>
 
 <div>
 <svg viewBox="0 0 400 200" role="img" aria-label="Comparison of Amdahl's Law and Gustafson's Law perspectives on parallel computing">
 <title>Amdahl vs Gustafson Perspective</title>
 <desc>Visual comparison showing Amdahl's pessimistic fixed-problem view versus Gustafson's optimistic scaled-problem approach to parallel computing</desc>
 <text x="200" y="20" text-anchor="middle" font-weight="bold">Amdahl vs Gustafson Perspective</text>
 
 <!-- Amdahl box -->
 <rect x="20" y="50" width="160" height="120" fill="#FFEBEE" stroke="#F44336" stroke-width="2" rx="5"/>
 <text x="100" y="70" text-anchor="middle" font-weight="bold">Amdahl</text>
 <text x="100" y="90" text-anchor="middle" font-size="12">Fixed problem size</text>
 <text x="100" y="110" text-anchor="middle" font-size="12">How fast can we</text>
 <text x="100" y="130" text-anchor="middle" font-size="12">solve it?</text>
 <text x="100" y="155" text-anchor="middle" font-size="10" fill="#F44336">Pessimistic</text>
 
 <!-- Gustafson box -->
 <rect x="220" y="50" width="160" height="120" fill="#E8F5E9" stroke="#4CAF50" stroke-width="2" rx="5"/>
 <text x="300" y="70" text-anchor="middle" font-weight="bold">Gustafson</text>
 <text x="300" y="90" text-anchor="middle" font-size="12">Scaled problem size</text>
 <text x="300" y="110" text-anchor="middle" font-size="12">How big a problem</text>
 <text x="300" y="130" text-anchor="middle" font-size="12">can we solve?</text>
 <text x="300" y="155" text-anchor="middle" font-size="10" fill="#4CAF50">Optimistic</text>
 </svg>
 </div>
</div>
</div>

## Examples

### Quick Examples
```python
# Image: 100x100 vs 1000x1000
Small: 10ms setup + 100ms process = 9% serial
Large: 10ms setup + 10,000ms process = 0.1% serial

# Database: 1GB vs 1TB
Small: 17% serial (100+100 of 1200ms)
Large: 0.01% serial (bigger data scales better!)
```

## Applying Both Laws

**Amdahl**: "20% serial → 5x max speedup"
**Gustafson**: "Scale problem to reduce serial %"

### Real Example: Video Encoding
!!! info "🎬 Real Example: Video Encoding Platform"
 <div>
 <div>
 <div>
 <h5>Amdahl View: Single Video</h5>
 <table class="responsive-table">
 <tr>
 <td>Read file</td>
 <td>5%</td>
 <td>(serial)</td>
 </tr>
 <tr>
 <td>Encode frames</td>
 <td>90%</td>
 <td>(parallel)</td>
 </tr>
 <tr>
 <td>Write output</td>
 <td>5%</td>
 <td>(serial)</td>
 </tr>
 </table>
 <div>
 <strong>Max speedup: 10x</strong>
 <span>Limited by 10% serial work</span>
 </div>
 
 <div>
 <h5>Gustafson View: Platform</h5>
 <div>
 <div>
 🎥 Process 1000s of videos</div>
 <div>
 📈 Serial overhead amortized</div>
 <div>
 🚀 Near-linear scaling</div>
 </div>
 <div>
 <strong>Speedup: ~0.95 × n</strong><br>
 <span>Limited only by coordination</span>
 </div>
 </div>
 </div>
 
 <div>
 <svg viewBox="0 0 500 300" role="img" aria-label="Video processing timeline comparing single video encoding versus platform-wide batch processing">
 <title>Video Processing: Two Perspectives</title>
 <desc>Timeline visualization showing how video encoding scales differently when processing a single video (Amdahl's view) versus processing many videos in parallel (Gustafson's view)</desc>
 <text x="250" y="20" text-anchor="middle" font-weight="bold">Video Processing: Two Perspectives</text>
 
 <!-- Timeline for single video -->
 <text x="50" y="60" font-size="12" font-weight="bold">Single Video:</text>
 <rect x="50" y="70" width="20" height="30" fill="#F44336"/>
 <text x="60" y="115" text-anchor="middle" font-size="10">R</text>
 <rect x="70" y="70" width="180" height="30" fill="#4CAF50"/>
 <text x="160" y="115" text-anchor="middle" font-size="10">Encode</text>
 <rect x="250" y="70" width="20" height="30" fill="#F44336"/>
 <text x="260" y="115" text-anchor="middle" font-size="10">W</text>
 
 <!-- Multiple videos -->
 <text x="50" y="160" font-size="12" font-weight="bold">Video Platform:</text>
 <g transform="translate(50, 170)">
 <!-- Video 1 -->
 <rect x="0" y="0" width="5" height="20" fill="#F44336"/>
 <rect x="5" y="0" width="45" height="20" fill="#4CAF50"/>
 <rect x="50" y="0" width="5" height="20" fill="#F44336"/>
 <!-- Video 2 -->
 <rect x="60" y="0" width="5" height="20" fill="#F44336"/>
 <rect x="65" y="0" width="45" height="20" fill="#4CAF50"/>
 <rect x="110" y="0" width="5" height="20" fill="#F44336"/>
 <!-- Video 3 -->
 <rect x="120" y="0" width="5" height="20" fill="#F44336"/>
 <rect x="125" y="0" width="45" height="20" fill="#4CAF50"/>
 <rect x="170" y="0" width="5" height="20" fill="#F44336"/>
 <!-- More indicator -->
 <text x="185" y="15" font-size="12">...</text>
 </g>
 
 <!-- Speedup comparison -->
 <line x1="300" y1="50" x2="300" y2="250" stroke="#666" stroke-width="1"/>
 <text x="350" y="60" font-size="12" font-weight="bold">Speedup</text>
 
 <!-- Amdahl limit -->
 <rect x="350" y="70" width="100" height="30" fill="#FFCDD2"/>
 <text x="400" y="90" text-anchor="middle" font-size="12">10x max</text>
 
 <!-- Gustafson scaling -->
 <rect x="350" y="170" width="100" height="80" fill="#C8E6C9"/>
 <text x="400" y="210" text-anchor="middle" font-size="12">~1000x</text>
 <text x="400" y="225" text-anchor="middle" font-size="10">(with 1000 cores)</text>
 </svg>
 </div>
</div>

!!! info
 💡 <strong>Lesson</strong>: Don't just parallelize tasks - parallelize workloads!
</div>

## Real-World Patterns

```python
# Microservices: 1000ms → 190ms (5x speedup)
# Sharding: 100ms → 20ms with 10 shards (5x)
# MapReduce: Scales well for large data, poor for small
```

## Optimization Strategies

1. **Reduce serial**: Use thread-local counters vs global locks
2. **Pipeline**: A→B→C becomes parallel A₁→B₁, A₂→B₂
3. **Data parallel**: Partition → Process → Merge
4. **Speculative**: Execute both branches, discard one

## Breaking Limits

**When Amdahl limits**: Cache auth | Overlap I/O | Batch vs stream | Use GPUs

**When Gustafson shines**: Batch workloads | Big analytics | ML training

## Practical Guidelines

### Choosing Parallelization Strategy
!!! note "🎯 Parallelization Strategy Guide"
 <div>
 <div>
 <div>
 <h5>Serial < 5%</h5>
 <div>
 <div>🚀
 </div>
 <div>
 <strong>Strategy:</strong> Aggressive parallelization
 <ul>
 <li>Scale to many cores</li>
 <li>Distributed systems</li>
 <li>GPU acceleration</li>
 </ul>
 <div>
 <strong>Worth it!</strong>
 </div>
 </div>
 </div>
 
 <div>
 <h5>Serial 5-20%</h5>
 <div>
 <div>⚡</div>
 </div>
 <div>
 <strong>Strategy:</strong> Moderate parallelization
 <ul>
 <li>4-8 cores optimal</li>
 <li>Thread pools</li>
 <li>Local parallelism</li>
 </ul>
 <div>
 <strong>Good ROI</strong>
 </div>
 </div>
 </div>
 
 <div>
 <h5>Serial > 20%</h5>
 <div>
 <div>🔧</div>
 </div>
 <div>
 <strong>Strategy:</strong> Fix serial bottlenecks
 <ul>
 <li>Algorithm redesign</li>
 <li>Better data structures</li>
 <li>I/O optimization</li>
 </ul>
 <div>
 <strong>Fix first!</strong>
 </div>
 </div>
 </div>
 </div>
 
 <div>
 <svg viewBox="0 0 500 200" role="img" aria-label="Bar chart showing maximum practical speedup achievable based on serial code fraction">
 <title>Maximum Practical Speedup by Serial Fraction</title>
 <desc>Bar chart demonstrating how serial code percentage limits maximum achievable speedup: less than 5% serial allows 20-100x speedup, 5-20% allows 5-20x, and over 20% serial limits speedup to less than 5x</desc>
 <text x="250" y="20" text-anchor="middle" font-weight="bold">Maximum Practical Speedup by Serial Fraction</text>
 
 <!-- Bars -->
 <rect x="50" y="50" width="80" height="120" fill="#4CAF50"/>
 <text x="90" y="45" text-anchor="middle" font-size="10">&lt;5%</text>
 <text x="90" y="110" text-anchor="middle" fill="white" font-weight="bold">20-100x</text>
 
 <rect x="180" y="90" width="80" height="80" fill="#FFB74D"/>
 <text x="220" y="85" text-anchor="middle" font-size="10">5-20%</text>
 <text x="220" y="130" text-anchor="middle" fill="white" font-weight="bold">5-20x</text>
 
 <rect x="310" y="130" width="80" height="40" fill="#EF5350"/>
 <text x="350" y="125" text-anchor="middle" font-size="10">&gt;20%</text>
 <text x="350" y="155" text-anchor="middle" fill="white" font-weight="bold">&lt;5x</text>
 
 <!-- Base line -->
 <line x1="40" y1="170" x2="410" y2="170" stroke="#333" stroke-width="2"/>
 </svg>
 </div>
 
 <div>
 <strong>📐 Quick Reference Formula:</strong>
 <div>
 $$\text{Max Speedup} \approx \frac{1}{\text{Serial Fraction}}$$
 </div>
 <div>
 Example: 10% serial → max 10x speedup
 </div>
 </div>
</div>
</div>

### Investment Decision
!!! note "💰 Investment Decision Example"
 <div>
 <div>
 <h5>Current Situation</h5>
 <table class="responsive-table">
 <tr>
 <td>Current speedup:</td>
 <td>4x with 8 cores</td>
 </tr>
 <tr>
 <td>Amdahl limit:</td>
 <td>10x maximum</td>
 </tr>
 </table>
 
 <div>
 <div>
 <h5>❌ Option 1: More Cores</h5>
 <table class="responsive-table">
 <tr>
 <td>16 cores:</td>
 <td>5.7x</td>
 <td>(+1.7x)</td>
 </tr>
 <tr>
 <td>32 cores:</td>
 <td>7.5x</td>
 <td>(+3.5x)</td>
 </tr>
 <tr>
 <td colspan="3"><strong>Verdict:</strong> Diminishing returns!</td>
 </tr>
 </table>
 </div>
 
 <div>
 <h5>✅ Option 2: Reduce Serial</h5>
 <table class="responsive-table">
 <tr>
 <td>10% → 5%:</td>
 <td>10x → 20x</td>
 <td>(2x limit!)</td>
 </tr>
 <tr>
 <td>Same cores:</td>
 <td>4x → 7x</td>
 <td>(+3x)</td>
 </tr>
 <tr>
 <td colspan="3"><strong>Verdict:</strong> Better ROI!</td>
 </tr>
 </table>
 </div>
 </div>
 
 <div>
 <svg viewBox="0 0 500 250" role="img" aria-label="Chart comparing speedup improvement strategies: adding more cores versus reducing serial bottlenecks">
 <title>Speedup Improvement Strategies</title>
 <desc>Comparison chart showing two paths from current 8-core, 4x speedup state: adding more cores yields diminishing returns, while reducing serial bottlenecks provides better ROI</desc>
 <text x="250" y="20" text-anchor="middle" font-weight="bold">Speedup Improvement Strategies</text>
 
 <!-- Axes -->
 <line x1="50" y1="200" x2="450" y2="200" stroke="#333" stroke-width="2"/>
 <line x1="50" y1="200" x2="50" y2="50" stroke="#333" stroke-width="2"/>
 
 <!-- Current state -->
 <circle cx="150" cy="140" r="5" fill="#2196F3"/>
 <text x="150" y="130" text-anchor="middle" font-size="10">Current</text>
 <text x="150" y="120" text-anchor="middle" font-size="10">8 cores, 4x</text>
 
 <!-- More cores path -->
 <path d="M 150 140 L 250 120 L 350 110" stroke="#F44336" stroke-width="2" stroke-dasharray="5,5"/>
 <circle cx="250" cy="120" r="3" fill="#F44336"/>
 <circle cx="350" cy="110" r="3" fill="#F44336"/>
 <text x="300" y="100" font-size="10" fill="#F44336">More cores</text>
 
 <!-- Reduce serial path -->
 <path d="M 150 140 L 250 90 L 350 70" stroke="#4CAF50" stroke-width="2"/>
 <circle cx="250" cy="90" r="3" fill="#4CAF50"/>
 <circle cx="350" cy="70" r="3" fill="#4CAF50"/>
 <text x="300" y="60" font-size="10" fill="#4CAF50">Reduce serial</text>
 
 <!-- Labels -->
 <text x="50" y="220" text-anchor="middle" font-size="10">8</text>
 <text x="150" y="220" text-anchor="middle" font-size="10">16</text>
 <text x="250" y="220" text-anchor="middle" font-size="10">32</text>
 <text x="350" y="220" text-anchor="middle" font-size="10">64</text>
 <text x="250" y="240" text-anchor="middle" font-size="12">Cores</text>
 
 <text x="30" y="200" text-anchor="middle" font-size="10">1x</text>
 <text x="30" y="140" text-anchor="middle" font-size="10">5x</text>
 <text x="30" y="80" text-anchor="middle" font-size="10">10x</text>
 <text x="20" y="125" text-anchor="middle" font-size="12" transform="rotate(-90 20 125)">Speedup</text>
 </svg>
 </div>
 
 <div>
 <strong>🎯 Recommendation: Focus on reducing serial bottlenecks first!</strong>
 <div>Hardware is easy to buy, but algorithmic improvements multiply its value.</div>
 </div>
</div>
</div>

## Key Takeaways

1. **Serial fraction determines ceiling** (measure it!)
2. **Bigger problems parallelize better** (Gustafson)
3. **Optimize serial parts first** (biggest impact)
4. **Use both laws** (limits + opportunities)

Remember: Perfect parallelization is rare. Design for it.
---
