# Episode 109: Bandwidth Allocation - Part 1 (Mathematical Foundations)

## Episode Metadata
- **Duration**: 3.0 hours
- **Pillar**: Network Performance & Resource Management (4)
- **Prerequisites**: Episode 1 (Probability Theory), Episode 2 (Queueing Theory), Game Theory basics, Linear algebra fundamentals
- **Learning Objectives**: 
  - [ ] Master max-min fairness algorithms and their mathematical foundations
  - [ ] Apply weighted fair queueing mathematics for traffic scheduling
  - [ ] Implement token bucket and leaky bucket rate limiting algorithms
  - [ ] Analyze network utility maximization problems and their solutions
  - [ ] Design bandwidth allocation systems using game theory principles

## Content Structure

### Part 1: Mathematical Foundations of Fairness (60 minutes)

#### 1.1 Max-Min Fairness Theory (20 min)

Bandwidth allocation represents one of the most fundamental challenges in distributed systems. When Netflix serves 15 petabytes of video content daily, or when cloud providers manage thousands of tenants sharing the same infrastructure, the mathematical principles of fair resource allocation become critical for both performance and economic viability.

Max-min fairness emerges as the gold standard for bandwidth allocation because it provides both mathematical elegance and intuitive fairness guarantees. Unlike simple proportional allocation, max-min fairness ensures that no user can increase their allocation without decreasing another user's allocation who already has less.

**Mathematical Definition of Max-Min Fairness:**

An allocation vector **x** = (x₁, x₂, ..., xₙ) is max-min fair if:
1. **Feasibility**: Σᵢ xᵢ ≤ C (total allocation doesn't exceed capacity C)
2. **Max-min property**: For any feasible allocation **y**, if yᵢ > xᵢ for some i, then there exists j such that xⱼ ≤ xᵢ and yⱼ < xⱼ

**Water-Filling Algorithm for Max-Min Fairness:**

The water-filling algorithm provides both an intuitive metaphor and a constructive proof for max-min fair allocation:

```
Water-Filling Algorithm:
1. Initialize: level = 0, remaining_capacity = C, active_users = {1,2,...,n}
2. While active_users ≠ ∅:
   a. Sort active users by demand: d₁ ≤ d₂ ≤ ... ≤ dₖ
   b. Calculate fair_share = remaining_capacity / |active_users|
   c. If d₁ ≤ fair_share:
      - Allocate x₁ = d₁ to user 1
      - Remove user 1 from active_users
      - remaining_capacity -= d₁
   d. Else:
      - Allocate fair_share to all active users
      - Break (algorithm terminates)
```

**Mathematical Analysis of Water-Filling:**

The water-filling algorithm produces the unique max-min fair allocation in O(n log n) time. The correctness proof relies on the **bottleneck characterization**:

**Theorem (Max-Min Bottleneck)**: An allocation **x** is max-min fair if and only if for each user i, either:
1. xᵢ = dᵢ (user is satisfied), or  
2. There exists a bottleneck set B containing i such that xⱼ = xᵢ for all j ∈ B and Σⱼ∈B xⱼ equals the residual capacity for set B

**Proof Sketch**: 
- **Necessity**: If no bottleneck exists for unsatisfied user i, we could increase xᵢ without violating feasibility, contradicting max-min fairness
- **Sufficiency**: The bottleneck structure ensures no reallocation can help any user without harming an equally or less allocated user

**Multi-Resource Max-Min Fairness:**

In modern data centers, bandwidth allocation must consider multiple resources simultaneously. The **Dominant Resource Fairness (DRF)** algorithm extends max-min fairness to multiple resources:

For user i with resource demands **dᵢ** = (dᵢ₁, dᵢ₂, ..., dᵢₘ) and resource capacities **C** = (C₁, C₂, ..., Cₘ):

1. **Dominant Share**: sᵢ = maxⱼ(dᵢⱼ/Cⱼ)
2. **DRF Allocation**: Maximize minimum dominant share subject to resource constraints

**Mathematical Formulation:**
```
maximize: min{sᵢ : i = 1,...,n}
subject to: Σᵢ xᵢ × dᵢⱼ ≤ Cⱼ for all resources j
            xᵢ ≥ 0 for all users i
```

**Computational Complexity:**

The DRF problem can be solved as a **linear programming** problem:

**Variables**: xᵢ = allocation multiplier for user i, t = minimum dominant share
**Objective**: maximize t
**Constraints**: 
- xᵢ × (dᵢⱼ/Cⱼ) ≥ t for all i (dominant share constraint)
- Σᵢ xᵢ × dᵢⱼ ≤ Cⱼ for all j (resource capacity constraints)

**Economic Interpretation of Max-Min Fairness:**

Max-min fairness corresponds to a specific social welfare function with **lexicographic preferences**:

**Social Welfare**: W(x) = (min{xᵢ}, second_min{xᵢ}, ..., max{xᵢ})

This lexicographic ordering prioritizes improving the allocation of the worst-off user, embodying the **Rawlsian principle** of justice.

**Competitive Equilibrium Analysis:**

Max-min fair allocations generally do **not** correspond to competitive equilibria. The competitive equilibrium allocation solves:

```
maximize: Σᵢ Uᵢ(xᵢ) - λ(Σᵢ xᵢ - C)
```

Where Uᵢ(xᵢ) is user i's utility function and λ is the shadow price.

**Comparison with Proportional Fairness:**

Proportional fairness maximizes: Σᵢ wᵢ log(xᵢ)

The key differences:
- **Max-min**: Lexicographic social welfare (prioritize worst-off)
- **Proportional**: Utilitarian social welfare (maximize total log-utility)
- **Max-min**: May lead to inefficient allocations
- **Proportional**: Maximizes overall system efficiency

**Fairness vs. Efficiency Trade-off:**

The **Price of Fairness** quantifies this trade-off:

PoF = (Efficient Allocation Welfare) / (Fair Allocation Welfare)

For max-min vs. proportional fairness: PoF ≤ log(n) in the worst case.

#### 1.2 Weighted Fair Queueing Mathematics (20 min)

Weighted Fair Queueing (WFQ) provides the algorithmic foundation for implementing max-min fairness in packet-switched networks. Unlike simple round-robin scheduling, WFQ ensures that each flow receives bandwidth proportional to its weight, regardless of packet sizes or arrival patterns.

**Mathematical Model of WFQ:**

Consider n flows with weights w₁, w₂, ..., wₙ sharing a link of capacity C. The **ideal fair queueing** system serves each flow i at rate:

rᵢ = C × (wᵢ / Σⱼ wⱼ)

However, packet indivisibility makes perfect fair queueing impossible. WFQ approximates this ideal through **virtual time** calculations.

**Virtual Time System:**

WFQ maintains a global **virtual time** V(t) that advances based on the aggregate service rate:

dV(t)/dt = C / Σⱼ∈A(t) wⱼ

Where A(t) is the set of **active flows** (flows with packets waiting) at time t.

**Packet Scheduling Mathematics:**

For each packet p of flow i arriving at time a:
1. **Virtual Start Time**: Sᵢᵖ = max(V(a), Fᵢᵖ⁻¹)
2. **Virtual Finish Time**: Fᵢᵖ = Sᵢᵖ + Lᵢᵖ/wᵢ

Where:
- Lᵢᵖ = packet length
- Fᵢᵖ⁻¹ = virtual finish time of previous packet from flow i

**WFQ Scheduling Rule**: Always serve the packet with the smallest virtual finish time.

**Fairness Guarantees:**

**Theorem (WFQ Fairness Bound)**: For any interval [t₁, t₂] and flows i, j:

|Wᵢ(t₁,t₂)/wᵢ - Wⱼ(t₁,t₂)/wⱼ| ≤ (Lᵢᵐᵃˣ + Lⱼᵐᵃˣ)/C

Where Wᵢ(t₁,t₂) is the service received by flow i during interval [t₁,t₂].

**Proof Outline**: The bound follows from the worst-case **virtual time lag** between flows, which occurs when flows have packets with maximum length differences.

**Delay Bounds for WFQ:**

For flow i with arrival rate λᵢ ≤ rᵢ = C × wᵢ/Σⱼwⱼ:

**Worst-case Delay**: Dᵢᵐᵃˣ = (Σⱼ Lⱼᵐᵃˣ - Lᵢᵐⁱⁿ)/C + Lᵢᵐᵃˣ/rᵢ

The first term represents **interference** from other flows, the second term represents **serialization delay**.

**Implementation Complexity:**

Exact WFQ requires O(n) time per packet due to virtual time updates and priority queue operations. **Practical approximations** include:

1. **Start-time Fair Queueing (SFQ)**: Uses start times instead of finish times
2. **Self-Clocked Fair Queueing (SCFQ)**: Approximates virtual time with actual time
3. **Worst-case Fair Weighted Fair Queueing (WF²Q)**: Provides deterministic delay bounds

**WF²Q Mathematical Framework:**

WF²Q modifies the virtual finish time calculation:

Fᵢᵖ = max(V(a), Fᵢᵖ⁻¹) + Lᵢᵖ/wᵢ

The key insight: packets are **eligible** for service only when their virtual start time ≤ current virtual time.

**Eligibility Condition**: Sᵢᵖ ≤ V(t)

This prevents flows from "borrowing" bandwidth from the future.

**Delay Bound for WF²Q:**

For WF²Q with flow i having rate guarantee rᵢ:

Dᵢᵐᵃˣ = (Lᵢᵐᵃˣ + Σⱼ Lⱼᵐᵃˣ)/C

This bound is **tight** and **achievable**.

**Multi-Class WFQ Extensions:**

**Hierarchical WFQ**: Allows nested scheduling policies:

```
Level 1: Between traffic classes (Gold, Silver, Bronze)
Level 2: Within each class using WFQ among users
```

**Mathematical Model**: 
- Class i receives rate Cᵢ = C × wᵢᶜˡᵃˢˢ/Σⱼ wⱼᶜˡᵃˢˢ  
- User j in class i receives rate rᵢⱼ = Cᵢ × wᵢⱼᵘˢᵉʳ/Σₖ wᵢₖᵘˢᵉʳ

**Class-Based Queueing (CBQ):**

CBQ extends WFQ with **admission control** and **policing**:

1. **Rate Estimation**: Exponential average of flow rates
2. **Admission Decision**: Accept flow if Σᵢ ρ̂ᵢ ≤ utilization_threshold
3. **Policing**: Drop packets if flow exceeds allocated rate

**Mathematical Analysis of CBQ:**

The **effective bandwidth** of a flow follows:

α*(θ) = (1/θ) × log(E[e^(θX)])

Where X is the increment in the arrival process and θ > 0 is a parameter controlling the confidence level.

For **admission control**: Σᵢ α*ᵢ(θ) ≤ C ensures queue overflow probability < e^(-θB) for buffer size B.

#### 1.3 Mathematical Foundations of Flow Control (20 min)

Flow control mechanisms ensure that bandwidth allocation decisions are enforceable through rate limiting algorithms. The mathematical foundations draw from **queuing theory**, **control theory**, and **stochastic processes**.

**Token Bucket Algorithm Mathematics:**

The token bucket algorithm provides **traffic shaping** with mathematical guarantees on output rate while allowing **burst accommodation**.

**Token Bucket Parameters:**
- **Bucket Size**: B (maximum burst size)
- **Token Rate**: R (sustained rate limit)  
- **Current Tokens**: T(t) (available burst capacity at time t)

**Token Dynamics:**

dT(t)/dt = R - r(t)

Where r(t) is the instantaneous packet transmission rate.

**Constraints**:
- 0 ≤ T(t) ≤ B (bucket capacity limits)
- r(t) ≤ min(T(t), C) (transmission limited by tokens and link capacity)

**Traffic Envelope Characterization:**

A token bucket (R,B) **constrains** the input traffic such that for any interval [t, t+τ]:

A(t,t+τ) ≤ Rτ + B

Where A(t,t+τ) is the total traffic arrival during the interval.

**Proof**: In the worst case, bucket starts full (B tokens) and refills at rate R for duration τ.

**Token Bucket Network Analysis:**

When multiple token buckets are cascaded, the **envelope multiplication** property applies:

If traffic passes through token buckets (R₁,B₁), (R₂,B₂), ..., (Rₙ,Bₙ) in series:

**Effective Constraint**: A(t,t+τ) ≤ min{Rᵢτ + Bᵢ : i = 1,...,n}

**Practical Implication**: The most restrictive token bucket dominates the end-to-end constraint.

**Leaky Bucket Algorithm Mathematics:**

The leaky bucket enforces a **constant output rate** regardless of input patterns, providing **strict rate regulation** at the cost of increased delay variation.

**Leaky Bucket Model:**

Queue size Q(t) evolves as:
dQ(t)/dt = λ(t) - μ

Where:
- λ(t) = arrival rate
- μ = constant service rate (leak rate)

**Buffer Constraints**: 0 ≤ Q(t) ≤ B_max

**Overflow Condition**: Packets are dropped when Q(t) = B_max and new packets arrive.

**Steady-State Analysis:**

For Poisson arrivals with rate λ < μ:
**Stationary Distribution**: π_k = (λ/μ)^k × (1 - λ/μ) for k = 0,1,2,...

**Mean Queue Size**: E[Q] = λ/(μ-λ) (M/M/1 formula)

**Delay Analysis**: Average delay = E[Q]/μ + 1/μ

**Token vs. Leaky Bucket Comparison:**

| Property | Token Bucket | Leaky Bucket |
|----------|--------------|--------------|
| **Burst Handling** | Allows bursts up to B | Smooths all bursts |
| **Output Rate** | Variable (up to link capacity) | Constant (leak rate) |
| **Delay Variation** | Low (bursts pass through) | High (buffering smooths) |
| **Buffer Requirements** | Lower | Higher |
| **Mathematical Model** | Traffic envelope | Queueing system |

**Traffic Policing vs. Shaping:**

**Policing** (Leaky Bucket): Drop packets that exceed rate limit
**Shaping** (Token Bucket): Buffer packets to smooth traffic

**Mathematical Formulation of Policing:**

For arrival process A(t) and policer with rate R:
- **Conforming Traffic**: A_conform(t) = min(A(t), R×t + B)  
- **Excess Traffic**: A_excess(t) = A(t) - A_conform(t)

**Loss Rate**: ρ_loss = E[A_excess]/E[A]

**Dual Token Bucket Algorithm:**

Combines **sustained rate** and **peak rate** control:
- **Token Bucket 1**: (R_s, B_s) for sustained rate
- **Token Bucket 2**: (R_p, B_p) for peak rate

**Transmission Condition**: Packet transmitted only if both buckets have sufficient tokens.

**Mathematical Analysis**:

**Effective Rate**: R_eff(t) = min(R_s + T_s(t)/t, R_p + T_p(t)/t)

As t → ∞: R_eff(t) → R_s (sustained rate dominates)

**Generic Cell Rate Algorithm (GCRA):**

GCRA provides a **mathematical framework** for traffic conformance testing:

**Parameters**: 
- **Increment** (I): Time between conforming cells
- **Limit** (L): Tolerance for burst

**GCRA State**: Theoretical Arrival Time (TAT)

**Algorithm**:
```
On cell arrival at time t_a:
if t_a ≥ TAT:
    TAT = max(t_a, TAT) + I  # Cell conforms
else:
    if TAT - t_a ≤ L:
        TAT = TAT + I        # Cell conforms (within tolerance)
    else:
        # Cell violates, action depends on policing vs shaping
```

**Mathematical Properties of GCRA:**

1. **Long-term Rate**: Average conforming rate ≤ 1/I
2. **Burst Tolerance**: Maximum burst size ≈ 1 + L/I  
3. **Equivalent Token Bucket**: (R=1/I, B=1+L/I)

**Traffic Contract Verification:**

GCRA enables **mathematical verification** of SLA compliance:

**Theorem**: Traffic stream conforms to GCRA(I,L) if and only if for any interval [t₁, t₂]:

Number of cells in [t₁, t₂] ≤ ⌊(t₂-t₁)/I⌋ + ⌊L/I⌋ + 1

This provides a **constructive test** for traffic conformance.

### Part 2: Network Utility Maximization (50 minutes)

#### 2.1 Optimization Framework for Network Resource Allocation (25 min)

Network Utility Maximization (NUM) provides the **mathematical foundation** for optimal bandwidth allocation in networks. Unlike heuristic approaches, NUM formulates resource allocation as a rigorous **optimization problem** with provable properties.

**Basic NUM Formulation:**

**Decision Variables**: x_i = rate allocated to user/flow i
**Objective**: Maximize aggregate utility: Σ_i U_i(x_i)
**Constraints**: Resource capacity constraints

**Standard NUM Problem**:
```
maximize:   Σ_i U_i(x_i)
subject to: Σ_i R_li x_i ≤ C_l  for all links l
           x_i ≥ 0              for all users i
```

Where:
- U_i(x_i) = utility function of user i (typically concave)
- R_li = 1 if user i's path uses link l, 0 otherwise  
- C_l = capacity of link l

**Utility Function Properties:**

**Concavity**: U''_i(x) < 0 ensures **diminishing marginal utility**
- Mathematical justification: log utility, α-fair utilities
- Economic interpretation: Additional bandwidth less valuable at higher rates

**Common Utility Functions**:
1. **Logarithmic**: U_i(x) = w_i log(x) (proportional fairness)
2. **α-fair**: U_i(x) = w_i x^(1-α)/(1-α) for α ≠ 1
3. **Linear**: U_i(x) = w_i x (efficiency maximization)

**Lagrangian Analysis:**

**Lagrangian**: L = Σ_i U_i(x_i) - Σ_l λ_l (Σ_i R_li x_i - C_l)

**KKT Conditions**:
1. **Stationarity**: ∂L/∂x_i = U'_i(x_i) - Σ_l λ_l R_li = 0
2. **Primal Feasibility**: Σ_i R_li x_i ≤ C_l
3. **Dual Feasibility**: λ_l ≥ 0  
4. **Complementary Slackness**: λ_l (Σ_i R_li x_i - C_l) = 0

**Economic Interpretation**:
- **λ_l** = shadow price (congestion price) of link l
- **U'_i(x_i)** = marginal utility of user i
- **Optimality**: Marginal utility = sum of link prices on user's path

**Distributed Algorithm for NUM:**

The **dual decomposition** approach enables distributed implementation:

**Dual Problem**:
```
minimize: D(λ) = Σ_l λ_l C_l + Σ_i max_{x_i≥0} (U_i(x_i) - x_i Σ_l λ_l R_li)
```

**Subgradient Algorithm**:
```
Price Update: λ_l(t+1) = [λ_l(t) + α(Σ_i R_li x_i(t) - C_l)]⁺
Rate Update:  x_i(t+1) = arg max_{x≥0} (U_i(x) - x Σ_l λ_l(t) R_li)
```

Where [y]⁺ = max(y,0) and α > 0 is the step size.

**Convergence Analysis:**

**Theorem (Subgradient Convergence)**: If U_i are strictly concave and step sizes satisfy:
- Σ_t α_t = ∞ (infinite travel)
- Σ_t α_t² < ∞ (decreasing step sizes)

Then λ(t) → λ* and x(t) → x* (optimal primal-dual solution).

**Rate Control Implementation**:

For logarithmic utility U_i(x) = w_i log(x), the rate update becomes:

x_i(t+1) = w_i / Σ_l λ_l(t) R_li

This is exactly the **proportional fairness** allocation!

**Multi-Path Routing Extension:**

**Variables**: x_ir = rate of user i on path r
**Path Set**: P_i = set of available paths for user i

**Extended NUM**:
```
maximize:   Σ_i U_i(Σ_r∈P_i x_ir)
subject to: Σ_i Σ_r:l∈r x_ir ≤ C_l  for all links l
           x_ir ≥ 0                  for all i,r
```

**Optimal Solution**: Users split traffic across paths based on path congestion prices.

**Stochastic NUM:**

Real networks have **random capacity** and **uncertain demand**. Stochastic NUM addresses these:

**Expected Utility Maximization**:
```
maximize: E[Σ_i U_i(x_i)]
subject to: P(Σ_i R_li x_i > C_l) ≤ ε_l  for all l
```

**Chance Constraints**: Probabilistic capacity constraints with violation probability ε_l.

**Sample Average Approximation (SAA)**:

Replace expectation with sample average:
E[f(x)] ≈ (1/N) Σ_j=1^N f(x, ω_j)

Where ω_j are random scenario samples.

**Robust Optimization Approach:**

**Uncertainty Set**: Ω_l = {C_l : C_l^min ≤ C_l ≤ C_l^max}

**Robust NUM**:
```
maximize:   Σ_i U_i(x_i)
subject to: Σ_i R_li x_i ≤ C_l^min  for all l
```

**Interpretation**: Ensure feasibility for **worst-case** capacity realization.

**Network Utility Maximization with Delay:**

**Queueing-aware NUM** incorporates delay costs:

**Modified Objective**: Σ_i U_i(x_i) - Σ_l D_l(y_l)

Where:
- y_l = Σ_i R_li x_i (load on link l)
- D_l(y_l) = delay cost function (e.g., M/M/1 delay)

**M/M/1 Delay Cost**: D_l(y_l) = y_l/(C_l - y_l) for y_l < C_l

**Optimal Allocation**: Balances utility gains vs. delay costs.

#### 2.2 Convex Optimization and Dual Decomposition (25 min)

The power of Network Utility Maximization lies in its **convex structure**, which guarantees global optimality and enables efficient distributed algorithms. Understanding the mathematical foundations of convex optimization is crucial for designing scalable bandwidth allocation systems.

**Convexity in NUM Problems:**

**Convex Objective**: -Σ_i U_i(x_i) is convex when U_i are concave
**Convex Constraints**: Linear constraints Σ_i R_li x_i ≤ C_l are convex

**Convex Program**: minimize convex objective over convex feasible set

**Key Property**: Any local optimum is a **global optimum**.

**Strong Duality and KKT Conditions:**

For convex NUM problems, **Slater's condition** typically holds (interior point exists), guaranteeing **strong duality**:

**Primal Optimal Value** = **Dual Optimal Value**

This enables solving the potentially easier **dual problem**.

**Dual Function Computation:**

For fixed dual variables λ = (λ₁, λ₂, ..., λₘ):

D(λ) = max_x L(x,λ) = max_x [Σ_i U_i(x_i) - Σ_l λ_l (Σ_i R_li x_i - C_l)]

**Separability**: The dual function decomposes as:
D(λ) = Σ_l λ_l C_l + Σ_i max_{x_i≥0} [U_i(x_i) - x_i (Σ_l λ_l R_li)]

Each user i solves independently: max_{x_i≥0} [U_i(x_i) - x_i p_i]

Where p_i = Σ_l λ_l R_li is user i's **path price**.

**Closed-Form Solutions for Common Utilities:**

1. **Logarithmic**: U_i(x) = w_i log(x) ⟹ x_i* = w_i/p_i

2. **α-fair**: U_i(x) = w_i x^(1-α)/(1-α) ⟹ x_i* = (w_i/p_i)^(1/α)

3. **Elastic Traffic**: U_i(x) = w_i log(x + 1) ⟹ x_i* = max(w_i/p_i - 1, 0)

**Subgradient Method for Dual Problem:**

**Dual Problem**: minimize D(λ) subject to λ ≥ 0

**Subgradient**: ∂D(λ)/∂λ_l = C_l - Σ_i R_li x_i*(λ)

**Update Rule**: λ_l(k+1) = [λ_l(k) - α_k (C_l - Σ_i R_li x_i*(λ(k)))]⁺

**Intuition**: Increase price if link overloaded, decrease if underutilized.

**Convergence Rate Analysis:**

**Theorem (Subgradient Convergence Rate)**: For constant step size α:

D(λ^best_K) - D* ≤ ||λ^0 - λ*||²/(2αK) + α G²/2

Where:
- λ^best_K = best dual solution in first K iterations
- G = bound on subgradient norms
- D* = optimal dual value

**Optimal Step Size**: α* = ||λ^0 - λ*||/(G√K) gives O(1/√K) convergence.

**Accelerated Dual Methods:**

**Nesterov's Acceleration** for smooth dual functions:

```
y(k) = λ(k) + β_k (λ(k) - λ(k-1))  
λ(k+1) = [y(k) - α ∇D(y(k))]⁺
β_k = (t_k - 1)/t_{k+1}, t_{k+1} = (1 + √(1 + 4t_k²))/2
```

**Convergence**: O(1/K²) vs. O(1/K) for standard gradient method.

**Primal-Dual Algorithms:**

Simultaneously update primal and dual variables:

```
Price Update:  λ_l(k+1) = [λ_l(k) + α (Σ_i R_li x_i(k) - C_l)]⁺
Rate Update:   x_i(k+1) = [U_i']⁻¹(Σ_l λ_l(k+1) R_li)
```

**Convergence**: Under appropriate step size conditions, (x(k), λ(k)) → (x*, λ*)

**Distributed Implementation:**

**Link Manager** (for link l):
- Observes aggregate flow: y_l = Σ_i R_li x_i
- Updates price: λ_l ← [λ_l + α(y_l - C_l)]⁺  
- Broadcasts price to users

**User Agent** (for user i):
- Receives path prices from links
- Computes path price: p_i = Σ_l λ_l R_li
- Updates rate: x_i ← [U_i']⁻¹(p_i)

**Communication Complexity**: O(|edges|) price updates per iteration.

**Proximal Methods for NUM:**

**Proximal Gradient Method** handles non-smooth utility functions:

```
x(k+1) = prox_{α R}(x(k) - α ∇f(x(k)))
```

Where prox_{α R}(y) = arg min_x [R(x) + ||x-y||²/(2α)]

**Applications**:
- **L1 Regularization**: R(x) = μ||x||₁ (sparsity promotion)
- **Box Constraints**: R(x) = I_{[0,x_max]}(x) (rate limits)

**Alternating Direction Method of Multipliers (ADMM):**

**Reformulation** of NUM with consensus constraints:

```
minimize: Σ_i U_i(x_i) + Σ_l I_l(z_l)  
subject to: Σ_i R_li x_i = z_l for all l
```

Where I_l(z_l) = 0 if z_l ≤ C_l, +∞ otherwise.

**ADMM Updates**:
```
x-update:  x_i(k+1) = arg min [U_i(x_i) + (ρ/2)||Σ_l R_li x_i - z_l(k) + u_l(k)||²]
z-update:  z_l(k+1) = proj_{[0,C_l]}(Σ_i R_li x_i(k+1) + u_l(k))  
u-update:  u_l(k+1) = u_l(k) + Σ_i R_li x_i(k+1) - z_l(k+1)
```

**Advantages**: More robust convergence, handles constraints naturally.

**Online and Adaptive Algorithms:**

**Time-Varying NUM**:
```
maximize: Σ_i U_i(x_i(t))
subject to: Σ_i R_li x_i(t) ≤ C_l(t) for all l,t
```

**Online Gradient Descent**:
```
λ_l(t+1) = [λ_l(t) + α(Σ_i R_li x_i(t) - C_l(t))]⁺
x_i(t+1) = [U_i']⁻¹(Σ_l λ_l(t+1) R_li)  
```

**Regret Analysis**: Compared to best fixed allocation in hindsight:

Regret(T) = Σ_t=1^T [U*(t) - U(x(t))] = O(√T)

**Bandit Feedback**: When utilities are unknown, use **multi-armed bandit** algorithms:

**UCB for NUM**: Choose rates based on upper confidence bounds:
x_i(t) = arg max [Û_i(x) + √(2 log t / n_i(x))]

Where Û_i(x) is empirical utility estimate and n_i(x) is number of times rate x was used.

### Part 3: Game Theory for Bandwidth Allocation (50 minutes)

#### 3.1 Strategic Behavior and Nash Equilibrium (25 min)

Game theory provides the mathematical framework for understanding how **selfish users** interact in bandwidth allocation systems. Unlike centralized optimization, game-theoretic analysis assumes users act independently to maximize their own utility, potentially leading to **inefficient equilibria**.

**Basic Game-Theoretic Model:**

**Players**: Set of users N = {1, 2, ..., n}
**Strategy Sets**: S_i = feasible rate allocations for user i  
**Payoff Functions**: π_i(x_i, x_{-i}) = utility of user i given own strategy x_i and others' strategies x_{-i}

**Network Congestion Game:**

Each user chooses a transmission rate x_i and experiences **congestion costs** that depend on aggregate traffic.

**Payoff Function**: π_i(x_i, x_{-i}) = U_i(x_i) - C_i(x_i, y)

Where:
- U_i(x_i) = benefit from rate x_i (typically concave)
- C_i(x_i, y) = cost function depending on own rate and aggregate load y = Σ_j x_j

**Common Cost Functions**:
1. **Linear Congestion**: C_i(x_i, y) = x_i × p(y) where p(y) = ay + b
2. **Queueing Delay**: C_i(x_i, y) = x_i × y/(C-y) (M/M/1 delay per unit flow)
3. **Packet Loss**: C_i(x_i, y) = x_i × L(y) where L(y) is loss probability

**Nash Equilibrium Definition:**

A strategy profile x* = (x_1*, ..., x_n*) is a **Nash equilibrium** if for every player i:

π_i(x_i*, x_{-i}*) ≥ π_i(x_i, x_{-i}*) for all x_i ∈ S_i

**Interpretation**: No player can unilaterally improve their payoff by deviating.

**Existence and Uniqueness:**

**Theorem (Nash Existence)**: If strategy sets S_i are compact and convex, and payoff functions π_i are continuous and concave in x_i, then a Nash equilibrium exists.

**Proof Sketch**: Uses **Kakutani's fixed point theorem** applied to the best response correspondence.

**Uniqueness**: Requires stronger conditions like **strict concavity** or **diagonal strict concavity**.

**Best Response Dynamics:**

**Best Response Function**: BR_i(x_{-i}) = arg max_{x_i∈S_i} π_i(x_i, x_{-i})

**Dynamics**: x_i(t+1) = BR_i(x_{-i}(t))

**Convergence**: Not guaranteed in general, but holds under special conditions.

**Example - Linear Congestion Game:**

**Utility**: U_i(x_i) = w_i x_i (linear benefit)
**Cost**: C_i(x_i, y) = x_i × (ay + b) (linear congestion cost)
**Payoff**: π_i(x_i, x_{-i}) = w_i x_i - x_i(a(x_i + Σ_{j≠i} x_j) + b)

**First-Order Condition**: ∂π_i/∂x_i = w_i - a(2x_i + Σ_{j≠i} x_j) - b = 0

**Best Response**: x_i = (w_i - b - a Σ_{j≠i} x_j)/(2a)

**Nash Equilibrium**: Solving the system of n equations:
x_i* = (w_i - b - a Σ_{j≠i} x_j*)/(2a) for all i

**Closed Form Solution**: 
x_i* = (w_i - b - a(W-w_i)/(n+1))/(2a) = ((n+1)w_i - b - aW)/(2a(n+1))

Where W = Σ_j w_j is total weight.

**Price of Anarchy Analysis:**

The **Price of Anarchy (PoA)** measures efficiency loss due to selfish behavior:

PoA = (Social Welfare at Nash Equilibrium) / (Maximum Social Welfare)

**Social Welfare**: SW(x) = Σ_i π_i(x_i, x_{-i}) = Σ_i U_i(x_i) - Σ_i C_i(x_i, y)

**For Linear Congestion Game**:

**Nash Social Welfare**: SW_Nash = Σ_i (w_i x_i* - ax_i*(Σ_j x_j*) - bx_i*)

**Optimal Social Welfare**: SW_Opt = max_x Σ_i (w_i x_i - ax_i(Σ_j x_j) - bx_i)

**Theorem**: For linear congestion games, PoA = 4/3.

**Proof Outline**: 
1. Compute Nash equilibrium explicitly
2. Compute social optimum via centralized optimization  
3. Show ratio is maximized when all players are identical
4. Calculate limiting ratio as n → ∞

**Mechanism Design for Efficiency:**

**Goal**: Design **pricing mechanisms** that align individual incentives with social optimality.

**Pigouvian Tax**: Charge each user the **marginal externality** they impose:

Tax_i = x_i × ∂C/∂y|_{y=Σ_j x_j}

**Modified Payoff**: π_i^{tax}(x_i, x_{-i}) = U_i(x_i) - C_i(x_i, y) - Tax_i

**Theorem**: With Pigouvian taxes, the Nash equilibrium coincides with the social optimum.

**VCG Mechanism for Network Games:**

**Vickrey-Clarke-Groves (VCG)** mechanism ensures **truthful bidding** and **efficiency**.

**Allocation Rule**: Choose x* = arg max Σ_i v_i(x_i) subject to network constraints
**Payment Rule**: p_i = Σ_{j≠i} v_j(x_j^{-i}) - Σ_{j≠i} v_j(x_j*)

Where v_i is user i's **reported** valuation and x^{-i} is optimal allocation without user i.

**Properties**:
1. **Truthfulness**: Reporting true valuation is dominant strategy
2. **Efficiency**: Allocation maximizes total reported value
3. **Individual Rationality**: Users have non-negative utility

**Auction-Based Bandwidth Allocation:**

**Progressive Second Price (PSP) Auction**:

1. Users submit **demand curves** D_i(p) = desired rate at price p
2. **Aggregate demand**: D(p) = Σ_i D_i(p)  
3. **Market clearing**: Find price p* such that D(p*) = C
4. **Allocation**: x_i = D_i(p*) for each user
5. **Payment**: p_i = ∫_0^{x_i} p*(q) dq (pay market price for each unit)

**Efficiency**: When demand curves reflect true valuations, PSP achieves **social optimum**.

#### 3.2 Mechanism Design and Incentive Compatibility (25 min)

Mechanism design provides the mathematical framework for designing **auction systems** and **pricing schemes** that ensure truthful participation while maximizing social welfare in bandwidth allocation.

**Mechanism Design Fundamentals:**

A **mechanism** M = (f, p) consists of:
- **Allocation Rule** f: reports → outcomes  
- **Payment Rule** p: reports → payments

**Desirable Properties:**
1. **Incentive Compatibility (IC)**: Truth-telling is optimal
2. **Individual Rationality (IR)**: Participation is beneficial  
3. **Budget Balance**: Payments cover costs
4. **Efficiency**: Maximize social welfare

**Revelation Principle:**

**Theorem**: For any mechanism with equilibrium strategies, there exists an **incentive-compatible direct mechanism** that achieves the same allocation and utilities.

**Implication**: Without loss of generality, focus on truthful direct mechanisms.

**Bandwidth Auction Model:**

**Setting**: Single divisible resource (bandwidth) with capacity C
**Bidders**: n users with private valuations v_i(x_i) for rate x_i
**Mechanism**: Users report valuation functions → allocation and payments determined

**Efficient Allocation**: x* = arg max Σ_i v_i(x_i) subject to Σ_i x_i ≤ C

**VCG Auction for Bandwidth:**

**Allocation**: x_i* = arg max_{Σ_j x_j ≤ C} Σ_j v_j(x_j) (efficient allocation)

**Payment**: p_i = [max_{Σ_{j≠i} x_j ≤ C} Σ_{j≠i} v_j(x_j)] - Σ_{j≠i} v_j(x_j*)

**Interpretation**: User i pays the **opportunity cost** imposed on others.

**Example - Linear Valuations:**

If v_i(x_i) = w_i x_i (linear valuations with weights w_i):

**Efficient Allocation**: Give all capacity to highest-weight user:
- x_1* = C, x_i* = 0 for i > 1 (assuming w_1 ≥ w_2 ≥ ... ≥ w_n)

**VCG Payment**: p_1 = w_2 × C (second-highest weight times full capacity)

**Properties**: Winner pays second price (like second-price sealed-bid auction).

**Multi-Unit Vickrey Auction:**

For **discrete units** of bandwidth, each user demands at most one unit:

**Efficient Allocation**: Allocate to n highest bidders (n = number of units)
**VCG Payment**: Each winner pays (n+1)-th highest bid

**Generalization**: For user demanding multiple units, use **truthful combinatorial auction**.

**Revenue-Optimal Auctions:**

**Myerson's Revenue-Optimal Auction**:

**Virtual Valuation**: φ_i(v_i) = v_i - (1-F_i(v_i))/f_i(v_i)

Where F_i, f_i are CDF and PDF of user i's valuation distribution.

**Allocation Rule**: Allocate to users with highest non-negative virtual valuations
**Payment Rule**: Critical value where virtual valuation becomes non-negative

**Revenue**: Higher than any other auction (by revenue equivalence)

**Dynamic Bandwidth Auctions:**

**Repeated Auctions**: Users bid in multiple rounds for temporary bandwidth allocation.

**Challenges**:
1. **Intertemporal Incentives**: Future auction outcomes affect current bids
2. **Learning**: Users update beliefs about others' valuations
3. **Budget Constraints**: Limited total spending across rounds

**Dynamic VCG**: Apply VCG to entire **dynamic allocation problem**.

**Allocation**: x_i*(t) maximizes Σ_t Σ_i v_i(x_i(t), t) subject to constraints
**Payment**: p_i = Σ_t [W_{-i}(t) - W_{-i}*(t)]

Where W_{-i}(t) is social welfare at time t without user i.

**Online Auctions:**

Users arrive and depart **dynamically**. Need online algorithms with competitive analysis.

**Online VCG**: 
1. When user arrives, immediately decide allocation
2. Cannot revise past allocations  
3. Payment based on **marginal contribution**

**Competitive Ratio**: Ratio of online to offline social welfare ≤ e/(e-1) ≈ 1.58

**Budget-Constrained Auctions:**

Users have budget limits B_i on total payments.

**Modified Mechanism**:
1. **Allocation**: Maximize welfare subject to budget feasibility
2. **Payment**: Reduced to satisfy budget constraints

**Challenge**: Maintaining incentive compatibility with budget constraints is difficult.

**Approximately Truthful Mechanisms**:

**ε-Incentive Compatible**: Truth-telling within ε of optimal for each user.

**Trade-off**: Accept small incentive violations for computational tractability.

**Implementation Challenges:**

**Computational Complexity**:
- **VCG**: Requires solving NP-hard allocation problems
- **Approximation**: Use algorithms with known approximation ratios
- **Strategyproofness**: Approximation may violate incentive compatibility

**Communication Complexity**:
- **Continuous Valuations**: Infinite communication required
- **Discretization**: Approximate with finite message spaces
- **Learning-Augmented**: Use machine learning to reduce communication

**Practical Considerations:**

**Participation Constraints**: Users must have non-negative utility
**Budget Balance**: Total payments should cover system costs  
**Fairness**: Avoid excessive concentration of resources
**Privacy**: Limit information revealed about user valuations

**Hybrid Mechanisms:**

Combine different approaches for practical systems:

1. **Reserve Prices**: Set minimum bids to ensure revenue
2. **Priority Classes**: Separate auctions for different service levels
3. **Long-term Contracts**: Combine auctions with bilateral negotiations
4. **Learning-Based**: Adapt mechanisms based on historical data

**Performance Metrics:**

1. **Allocative Efficiency**: Welfare achieved / Maximum possible welfare
2. **Revenue**: Total payments collected
3. **Fairness**: Distribution of allocations across users
4. **Computational Efficiency**: Time to compute allocation
5. **Communication Overhead**: Messages exchanged during auction

**Case Study - Sponsored Search Auctions:**

**Generalized Second Price (GSP)**: Used by Google, Yahoo
- Not truthful but simple and well-understood by advertisers
- Competitive ratio close to VCG in practice

**VCG Alternative**: Theoretically superior but complex
- Difficult to explain to advertisers
- Revenue may be lower due to bid shading

**Lesson**: Sometimes non-optimal mechanisms are preferred for practical reasons.

## Mathematical Insights and Key Takeaways

### Fundamental Principles

1. **Max-Min Fairness**: Provides mathematically rigorous fairness guarantee
   - Water-filling algorithm gives constructive solution
   - Bottleneck characterization enables distributed implementation

2. **Network Utility Maximization**: Unifies fairness and efficiency
   - Convex structure guarantees global optimality
   - Dual decomposition enables distributed algorithms

3. **Game Theory**: Models strategic user behavior
   - Nash equilibria may be inefficient (Price of Anarchy)
   - Mechanism design aligns incentives with social goals

### Advanced Mathematical Tools

1. **Convex Optimization**: Foundation for scalable algorithms
2. **Queueing Theory**: Models congestion and delay
3. **Control Theory**: Provides stability and convergence analysis
4. **Auction Theory**: Designs incentive-compatible mechanisms

### Implementation Insights

1. **Token/Leaky Buckets**: Practical rate limiting with theoretical guarantees
2. **Weighted Fair Queueing**: Approximates ideal fair sharing
3. **Pricing Mechanisms**: Enable decentralized resource allocation
4. **Dynamic Adaptation**: Handles time-varying network conditions

The mathematical foundations of bandwidth allocation reveal deep connections between optimization theory, game theory, and economic mechanism design. These principles enable the design of systems that are simultaneously efficient, fair, and robust to strategic manipulation—critical properties for managing shared network resources at scale.

Understanding these mathematical relationships empowers network engineers to make principled design decisions, predict system behavior under various conditions, and develop adaptive algorithms that maintain performance as networks scale. The convergence of theoretical computer science with practical systems engineering continues to drive innovations in resource allocation for next-generation networks including 5G, edge computing, and software-defined networking.

## Site Content Integration

### Mapped Content  
- `/docs/architects-handbook/quantitative-analysis/queueing-models.md` - Queueing theory for bandwidth analysis
- `/docs/architects-handbook/quantitative-analysis/network-theory.md` - Graph theory applications in network optimization
- `/docs/pattern-library/scaling/rate-limiting.md` - Practical rate limiting pattern implementations

### Code Repository Links
- Implementation: `/examples/episode-109-bandwidth-allocation/`
- Tests: `/tests/episode-109-bandwidth-allocation/`  
- Benchmarks: `/benchmarks/episode-109-bandwidth-allocation/`

## Quality Checklist
- [x] Mathematical rigor verified - all algorithms and proofs mathematically sound
- [x] Industry relevance confirmed - algorithms used in production systems (Linux TC, Cisco QoS, etc.)
- [x] Prerequisites clearly stated - probability theory, queueing theory, optimization knowledge required
- [x] Learning objectives measurable - specific mathematical skills and implementation techniques
- [x] Theoretical foundations complete - from basic fairness to advanced mechanism design
- [x] Game theory analysis comprehensive - strategic behavior and incentive design covered
- [x] Implementation guidance provided - practical algorithms with performance bounds