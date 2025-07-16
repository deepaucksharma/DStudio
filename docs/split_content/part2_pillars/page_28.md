Page 28: Consistency Dial Slider
The Consistency Spectrum Interface:
Consistency Level Selector:

STRONG ●────────────────────○ EVENTUAL
       ↑                    ↑
    Your DB              Your Cache

[================|----] 80% Strong

Settings:
├─ Read Preference:  [Primary Only ▼]
├─ Write Concern:    [Majority     ▼]
├─ Read Concern:     [Linearizable ▼]
└─ Timeout:          [5000ms       ]

Trade-offs at current setting:
✓ Guaranteed latest data
✓ No stale reads
✗ Higher latency (200ms vs 20ms)
✗ Lower availability (99.9% vs 99.99%)
✗ Higher cost ($$$$ vs $)
Consistency Levels Explained:
1. LINEARIZABLE (Strongest)
   - Real-time ordering
   - Like single-threaded execution
   - Cost: Multiple round trips
   - Use: Financial transactions

2. SEQUENTIAL  
   - Operations appear in program order
   - May not reflect real-time
   - Cost: Coordination per client
   - Use: User session state

3. CAUSAL
   - Preserves cause → effect
   - Allows concurrent operations
   - Cost: Vector clocks
   - Use: Social media comments

4. EVENTUAL (Weakest)
   - Converges eventually
   - No ordering guarantees
   - Cost: Minimal
   - Use: View counters
Real-World Consistency Trade-offs:
YouTube View Counter:
- Eventual consistency
- Updates batched hourly
- Trade-off: Accuracy for scale

Bank Balance:
- Strong consistency  
- Every read sees all writes
- Trade-off: Scale for correctness

Twitter Timeline:
- Causal consistency
- Replies after original tweets
- Trade-off: Some ordering for speed

Shopping Cart:
- Session consistency
- User sees own updates
- Trade-off: Global consistency for UX