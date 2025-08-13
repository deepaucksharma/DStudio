/*
Linearizability Tester
Verifies if operations appear atomic and instantaneous
Example: Database transactions, Distributed locks, Banking systems
*/

package main

import (
	"fmt"
	"log"
	"math/rand"
	"sort"
	"sync"
	"time"
)

// Operation represents a single operation in the system
type Operation struct {
	ID         string
	Type       string      // READ, WRITE, CAS (Compare-And-Swap)
	Key        string
	Value      interface{}
	OldValue   interface{} // For CAS operations
	Result     interface{} // Operation result
	StartTime  time.Time
	EndTime    time.Time
	NodeID     string
	ClientID   string
	Success    bool
}

// Duration returns the operation duration
func (op *Operation) Duration() time.Duration {
	return op.EndTime.Sub(op.StartTime)
}

// History represents a sequence of operations
type History []*Operation

// SortByStartTime sorts operations by start time
func (h History) SortByStartTime() {
	sort.Slice(h, func(i, j int) bool {
		return h[i].StartTime.Before(h[j].StartTime)
	})
}

// SortByEndTime sorts operations by end time
func (h History) SortByEndTime() {
	sort.Slice(h, func(i, j int) bool {
		return h[i].EndTime.Before(h[j].EndTime)
	})
}

// LinearizableNode represents a node that claims to be linearizable
type LinearizableNode struct {
	NodeID   string
	Data     map[string]interface{}
	mutex    sync.RWMutex
	OpDelay  time.Duration // Simulated operation delay
	IsOnline bool
}

// NewLinearizableNode creates a new node
func NewLinearizableNode(nodeID string, opDelay time.Duration) *LinearizableNode {
	return &LinearizableNode{
		NodeID:   nodeID,
		Data:     make(map[string]interface{}),
		OpDelay:  opDelay,
		IsOnline: true,
	}
}

// Read performs a read operation
func (n *LinearizableNode) Read(key, clientID string) *Operation {
	op := &Operation{
		ID:        fmt.Sprintf("%s_%d", clientID, time.Now().UnixNano()),
		Type:      "READ",
		Key:       key,
		StartTime: time.Now(),
		NodeID:    n.NodeID,
		ClientID:  clientID,
	}

	if !n.IsOnline {
		op.EndTime = time.Now()
		op.Success = false
		op.Result = fmt.Errorf("node %s offline", n.NodeID)
		return op
	}

	// Simulate operation delay
	time.Sleep(n.OpDelay)

	n.mutex.RLock()
	value, exists := n.Data[key]
	n.mutex.RUnlock()

	op.EndTime = time.Now()
	op.Success = true

	if exists {
		op.Result = value
		op.Value = value
	} else {
		op.Result = nil
		op.Value = nil
	}

	log.Printf("[%s] READ %s: %v (client: %s)", n.NodeID, key, op.Result, clientID)
	return op
}

// Write performs a write operation
func (n *LinearizableNode) Write(key string, value interface{}, clientID string) *Operation {
	op := &Operation{
		ID:        fmt.Sprintf("%s_%d", clientID, time.Now().UnixNano()),
		Type:      "WRITE",
		Key:       key,
		Value:     value,
		StartTime: time.Now(),
		NodeID:    n.NodeID,
		ClientID:  clientID,
	}

	if !n.IsOnline {
		op.EndTime = time.Now()
		op.Success = false
		op.Result = fmt.Errorf("node %s offline", n.NodeID)
		return op
	}

	// Simulate operation delay
	time.Sleep(n.OpDelay)

	n.mutex.Lock()
	n.Data[key] = value
	n.mutex.Unlock()

	op.EndTime = time.Now()
	op.Success = true
	op.Result = "OK"

	log.Printf("[%s] WRITE %s = %v (client: %s)", n.NodeID, key, value, clientID)
	return op
}

// CompareAndSwap performs an atomic compare-and-swap operation
func (n *LinearizableNode) CompareAndSwap(key string, oldValue, newValue interface{}, clientID string) *Operation {
	op := &Operation{
		ID:        fmt.Sprintf("%s_%d", clientID, time.Now().UnixNano()),
		Type:      "CAS",
		Key:       key,
		OldValue:  oldValue,
		Value:     newValue,
		StartTime: time.Now(),
		NodeID:    n.NodeID,
		ClientID:  clientID,
	}

	if !n.IsOnline {
		op.EndTime = time.Now()
		op.Success = false
		op.Result = fmt.Errorf("node %s offline", n.NodeID)
		return op
	}

	// Simulate operation delay
	time.Sleep(n.OpDelay)

	n.mutex.Lock()
	currentValue, exists := n.Data[key]
	
	if !exists && oldValue == nil {
		// Setting new value when key doesn't exist
		n.Data[key] = newValue
		op.Success = true
		op.Result = true
	} else if exists && currentValue == oldValue {
		// Value matches, update
		n.Data[key] = newValue
		op.Success = true
		op.Result = true
	} else {
		// Value doesn't match, no update
		op.Success = true
		op.Result = false
	}
	n.mutex.Unlock()

	op.EndTime = time.Now()

	log.Printf("[%s] CAS %s: %v->%v = %v (client: %s)", 
		n.NodeID, key, oldValue, newValue, op.Result, clientID)
	return op
}

// SetOnline sets the node's online status
func (n *LinearizableNode) SetOnline(online bool) {
	n.mutex.Lock()
	defer n.mutex.Unlock()
	n.IsOnline = online
	
	status := "ONLINE"
	if !online {
		status = "OFFLINE"
	}
	log.Printf("[%s] Status: %s", n.NodeID, status)
}

// LinearizabilityTester tests linearizability of operations
type LinearizabilityTester struct {
	Nodes   map[string]*LinearizableNode
	History History
	mutex   sync.RWMutex
}

// NewLinearizabilityTester creates a new tester
func NewLinearizabilityTester() *LinearizabilityTester {
	return &LinearizabilityTester{
		Nodes:   make(map[string]*LinearizableNode),
		History: make(History, 0),
	}
}

// AddNode adds a node to test
func (t *LinearizabilityTester) AddNode(node *LinearizableNode) {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	t.Nodes[node.NodeID] = node
	log.Printf("Added node for testing: %s", node.NodeID)
}

// RecordOperation records an operation in history
func (t *LinearizabilityTester) RecordOperation(op *Operation) {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	t.History = append(t.History, op)
}

// PerformRead performs a read operation and records it
func (t *LinearizabilityTester) PerformRead(nodeID, key, clientID string) *Operation {
	t.mutex.RLock()
	node, exists := t.Nodes[nodeID]
	t.mutex.RUnlock()

	if !exists {
		return &Operation{
			Success: false,
			Result:  fmt.Errorf("node %s not found", nodeID),
		}
	}

	op := node.Read(key, clientID)
	t.RecordOperation(op)
	return op
}

// PerformWrite performs a write operation and records it
func (t *LinearizabilityTester) PerformWrite(nodeID, key string, value interface{}, clientID string) *Operation {
	t.mutex.RLock()
	node, exists := t.Nodes[nodeID]
	t.mutex.RUnlock()

	if !exists {
		return &Operation{
			Success: false,
			Result:  fmt.Errorf("node %s not found", nodeID),
		}
	}

	op := node.Write(key, value, clientID)
	t.RecordOperation(op)
	return op
}

// PerformCAS performs a compare-and-swap operation and records it
func (t *LinearizabilityTester) PerformCAS(nodeID, key string, oldValue, newValue interface{}, clientID string) *Operation {
	t.mutex.RLock()
	node, exists := t.Nodes[nodeID]
	t.mutex.RUnlock()

	if !exists {
		return &Operation{
			Success: false,
			Result:  fmt.Errorf("node %s not found", nodeID),
		}
	}

	op := node.CompareAndSwap(key, oldValue, newValue, clientID)
	t.RecordOperation(op)
	return op
}

// CheckLinearizability analyzes the operation history for linearizability violations
func (t *LinearizabilityTester) CheckLinearizability() map[string]interface{} {
	t.mutex.RLock()
	history := make(History, len(t.History))
	copy(history, t.History)
	t.mutex.RUnlock()

	violations := make([]map[string]interface{}, 0)
	warnings := make([]string, 0)

	// Group operations by key
	keyOps := make(map[string]History)
	for _, op := range history {
		keyOps[op.Key] = append(keyOps[op.Key], op)
	}

	// Check each key separately
	for key, ops := range keyOps {
		keyViolations, keyWarnings := t.checkKeyLinearizability(key, ops)
		violations = append(violations, keyViolations...)
		warnings = append(warnings, keyWarnings...)
	}

	// Additional global checks
	globalViolations, globalWarnings := t.checkGlobalProperties(history)
	violations = append(violations, globalViolations...)
	warnings = append(warnings, globalWarnings...)

	return map[string]interface{}{
		"is_linearizable":   len(violations) == 0,
		"violations":        violations,
		"warnings":          warnings,
		"total_operations":  len(history),
		"analyzed_keys":     len(keyOps),
		"analysis_time":     time.Now(),
	}
}

// checkKeyLinearizability checks linearizability for operations on a single key
func (t *LinearizabilityTester) checkKeyLinearizability(key string, ops History) ([]map[string]interface{}, []string) {
	violations := make([]map[string]interface{}, 0)
	warnings := make([]string, 0)

	if len(ops) < 2 {
		return violations, warnings
	}

	// Sort operations by start time
	ops.SortByStartTime()

	// Track the logical state sequence
	var logicalSequence []interface{}
	
	// Build a timeline of non-overlapping operations
	nonOverlapping := make(History, 0)
	for _, op := range ops {
		if op.Success && (op.Type == "WRITE" || op.Type == "CAS") {
			nonOverlapping = append(nonOverlapping, op)
		}
	}

	// Check for basic consistency violations
	for i, op := range ops {
		if !op.Success {
			continue
		}

		switch op.Type {
		case "READ":
			// Check if read value is consistent with known writes
			violation := t.checkReadConsistency(key, op, ops[:i])
			if violation != nil {
				violations = append(violations, violation)
			}

		case "WRITE":
			logicalSequence = append(logicalSequence, op.Value)

		case "CAS":
			if op.Result.(bool) {
				logicalSequence = append(logicalSequence, op.Value)
			}
		}
	}

	// Check for ordering violations
	orderViolations := t.checkOperationOrdering(key, ops)
	violations = append(violations, orderViolations...)

	return violations, warnings
}

// checkReadConsistency checks if a read operation is consistent with previous writes
func (t *LinearizabilityTester) checkReadConsistency(key string, readOp *Operation, priorOps History) map[string]interface{} {
	// Find the most recent write that completed before this read started
	var lastWrite *Operation
	
	for i := len(priorOps) - 1; i >= 0; i-- {
		op := priorOps[i]
		if (op.Type == "WRITE" || (op.Type == "CAS" && op.Result.(bool))) && 
		   op.Success && op.EndTime.Before(readOp.StartTime) {
			lastWrite = op
			break
		}
	}

	// Check if read value matches expected value
	expectedValue := interface{}(nil)
	if lastWrite != nil {
		expectedValue = lastWrite.Value
	}

	if readOp.Result != expectedValue {
		// Check if there might be a concurrent write that could explain this
		for _, op := range priorOps {
			if (op.Type == "WRITE" || (op.Type == "CAS" && op.Result.(bool))) &&
			   op.Success && t.operationsOverlap(op, readOp) && op.Value == readOp.Result {
				// Concurrent write found, this might be acceptable
				return nil
			}
		}

		return map[string]interface{}{
			"type":         "read_consistency_violation",
			"key":          key,
			"operation":    readOp.ID,
			"read_value":   readOp.Result,
			"expected":     expectedValue,
			"description":  "Read returned value inconsistent with known writes",
		}
	}

	return nil
}

// checkOperationOrdering checks for ordering violations
func (t *LinearizabilityTester) checkOperationOrdering(key string, ops History) []map[string]interface{} {
	violations := make([]map[string]interface{}, 0)

	// Check for operations that should be ordered but appear out of order
	for i := 0; i < len(ops)-1; i++ {
		for j := i + 1; j < len(ops); j++ {
			op1, op2 := ops[i], ops[j]

			// If op1 finishes before op2 starts, they should be ordered
			if op1.EndTime.Before(op2.StartTime) && op1.Success && op2.Success {
				// Check specific ordering constraints
				if violation := t.checkOrderingConstraint(key, op1, op2); violation != nil {
					violations = append(violations, violation)
				}
			}
		}
	}

	return violations
}

// checkOrderingConstraint checks specific ordering constraints between two operations
func (t *LinearizabilityTester) checkOrderingConstraint(key string, op1, op2 *Operation) map[string]interface{} {
	// Write-Read constraint: If write completes before read starts, read should see the write
	if op1.Type == "WRITE" && op2.Type == "READ" {
		if op2.Result != op1.Value {
			// Check if there's an intervening write
			// This is a simplified check - full linearizability checking is NP-complete
			return map[string]interface{}{
				"type":        "write_read_ordering_violation",
				"key":         key,
				"write_op":    op1.ID,
				"read_op":     op2.ID,
				"write_value": op1.Value,
				"read_value":  op2.Result,
				"description": "Read did not see preceding write",
			}
		}
	}

	return nil
}

// checkGlobalProperties checks global linearizability properties
func (t *LinearizabilityTester) checkGlobalProperties(history History) ([]map[string]interface{}, []string) {
	violations := make([]map[string]interface{}, 0)
	warnings := make([]string, 0)

	// Check for very long operations (might indicate system issues)
	for _, op := range history {
		if op.Duration() > 5*time.Second {
			warnings = append(warnings, fmt.Sprintf("Operation %s took %v (very long)", 
				op.ID, op.Duration()))
		}
	}

	// Check for operations on offline nodes
	for _, op := range history {
		if !op.Success && op.Result != nil {
			if err, ok := op.Result.(error); ok && err.Error() == fmt.Sprintf("node %s offline", op.NodeID) {
				// This is expected behavior
				continue
			}
		}
	}

	return violations, warnings
}

// operationsOverlap checks if two operations have overlapping time intervals
func (t *LinearizabilityTester) operationsOverlap(op1, op2 *Operation) bool {
	return op1.StartTime.Before(op2.EndTime) && op2.StartTime.Before(op1.EndTime)
}

// GetStatistics returns statistics about the operation history
func (t *LinearizabilityTester) GetStatistics() map[string]interface{} {
	t.mutex.RLock()
	defer t.mutex.RUnlock()

	stats := map[string]interface{}{
		"total_operations": len(t.History),
		"operations_by_type": make(map[string]int),
		"operations_by_node": make(map[string]int),
		"success_rate": 0.0,
	}

	successful := 0
	for _, op := range t.History {
		// Count by type
		if counts, ok := stats["operations_by_type"].(map[string]int); ok {
			counts[op.Type]++
		}

		// Count by node
		if counts, ok := stats["operations_by_node"].(map[string]int); ok {
			counts[op.NodeID]++
		}

		if op.Success {
			successful++
		}
	}

	if len(t.History) > 0 {
		stats["success_rate"] = float64(successful) / float64(len(t.History))
	}

	return stats
}

// bankingScenario simulates a banking scenario with transfers
func bankingScenario(tester *LinearizabilityTester) {
	fmt.Println("\n=== Banking Transfer Scenario ===")

	// Initialize accounts
	tester.PerformWrite("primary", "account:alice", 1000, "system")
	tester.PerformWrite("primary", "account:bob", 500, "system")
	time.Sleep(100 * time.Millisecond)

	// Simulate concurrent transfers
	var wg sync.WaitGroup

	// Alice transfers to Bob
	wg.Add(1)
	go func() {
		defer wg.Done()
		
		// Alice reads her balance
		balance1 := tester.PerformRead("primary", "account:alice", "alice")
		if balance1.Success && balance1.Result.(int) >= 200 {
			// Try to transfer 200
			success := tester.PerformCAS("primary", "account:alice", 1000, 800, "alice")
			if success.Success && success.Result.(bool) {
				// Credit Bob's account
				bobBalance := tester.PerformRead("primary", "account:bob", "alice")
				if bobBalance.Success {
					tester.PerformCAS("primary", "account:bob", bobBalance.Result, 
						bobBalance.Result.(int)+200, "alice")
				}
			}
		}
	}()

	// Bob transfers to Alice
	wg.Add(1)
	go func() {
		defer wg.Done()
		
		time.Sleep(50 * time.Millisecond) // Slight delay
		
		// Bob reads his balance
		balance2 := tester.PerformRead("primary", "account:bob", "bob")
		if balance2.Success && balance2.Result.(int) >= 100 {
			// Try to transfer 100
			success := tester.PerformCAS("primary", "account:bob", balance2.Result, 
				balance2.Result.(int)-100, "bob")
			if success.Success && success.Result.(bool) {
				// Credit Alice's account
				aliceBalance := tester.PerformRead("primary", "account:alice", "bob")
				if aliceBalance.Success {
					tester.PerformCAS("primary", "account:alice", aliceBalance.Result,
						aliceBalance.Result.(int)+100, "bob")
				}
			}
		}
	}()

	wg.Wait()

	// Final balance check
	fmt.Println("Final balances:")
	aliceFinal := tester.PerformRead("primary", "account:alice", "system")
	bobFinal := tester.PerformRead("primary", "account:bob", "system")

	if aliceFinal.Success {
		fmt.Printf("Alice: %v\n", aliceFinal.Result)
	}
	if bobFinal.Success {
		fmt.Printf("Bob: %v\n", bobFinal.Result)
	}
}

// counterScenario simulates concurrent counter increments
func counterScenario(tester *LinearizabilityTester) {
	fmt.Println("\n=== Concurrent Counter Scenario ===")

	// Initialize counter
	tester.PerformWrite("primary", "counter", 0, "system")
	time.Sleep(50 * time.Millisecond)

	// Multiple clients increment counter concurrently
	var wg sync.WaitGroup
	clientCount := 5
	incrementsPerClient := 3

	for i := 0; i < clientCount; i++ {
		wg.Add(1)
		go func(clientID int) {
			defer wg.Done()
			
			clientName := fmt.Sprintf("client_%d", clientID)
			
			for j := 0; j < incrementsPerClient; j++ {
				// Read current value
				current := tester.PerformRead("primary", "counter", clientName)
				if current.Success {
					// Try to increment
					newValue := current.Result.(int) + 1
					tester.PerformCAS("primary", "counter", current.Result, newValue, clientName)
				}
				
				// Small random delay
				time.Sleep(time.Duration(rand.Intn(20)+10) * time.Millisecond)
			}
		}(i)
	}

	wg.Wait()

	// Final counter value
	final := tester.PerformRead("primary", "counter", "system")
	if final.Success {
		expected := clientCount * incrementsPerClient
		actual := final.Result.(int)
		fmt.Printf("Counter final value: %d (expected max: %d)\n", actual, expected)
		
		if actual > expected {
			fmt.Printf("❌ Counter value exceeds maximum possible!\n")
		} else if actual < expected {
			fmt.Printf("⚠️ Some increments may have been lost due to contention\n")
		} else {
			fmt.Printf("✅ All increments successful\n")
		}
	}
}

// demonstrateLinearizability demonstrates linearizability testing
func demonstrateLinearizability() {
	fmt.Println("=== Linearizability Tester Demo ===")
	fmt.Println("Testing atomic operations and consistency")

	// Create tester
	tester := NewLinearizabilityTester()

	// Add nodes
	primaryNode := NewLinearizableNode("primary", 10*time.Millisecond)
	backupNode := NewLinearizableNode("backup", 15*time.Millisecond)

	tester.AddNode(primaryNode)
	tester.AddNode(backupNode)

	fmt.Println("\n=== Basic Operations Test ===")

	// Basic operation sequence
	tester.PerformWrite("primary", "x", 1, "client1")
	tester.PerformRead("primary", "x", "client2")
	tester.PerformCAS("primary", "x", 1, 2, "client1")
	tester.PerformRead("primary", "x", "client2")

	time.Sleep(100 * time.Millisecond)

	// Run banking scenario
	bankingScenario(tester)

	// Run counter scenario
	counterScenario(tester)

	fmt.Println("\n=== Network Partition Test ===")

	// Simulate network partition
	fmt.Println("Simulating network partition (backup node offline)...")
	backupNode.SetOnline(false)

	// Operations during partition
	tester.PerformWrite("primary", "partition_test", "online_write", "client1")
	tester.PerformWrite("backup", "partition_test", "offline_write", "client2") // Should fail

	time.Sleep(100 * time.Millisecond)

	// Restore network
	backupNode.SetOnline(true)
	fmt.Println("Network partition resolved")

	fmt.Println("\n=== Stress Test ===")

	// Stress test with many concurrent operations
	var stressWG sync.WaitGroup
	stressClients := 10
	operationsPerClient := 5

	for i := 0; i < stressClients; i++ {
		stressWG.Add(1)
		go func(clientID int) {
			defer stressWG.Done()
			
			clientName := fmt.Sprintf("stress_client_%d", clientID)
			
			for j := 0; j < operationsPerClient; j++ {
				key := fmt.Sprintf("stress_key_%d", j%3) // Use 3 different keys
				value := fmt.Sprintf("value_%d_%d", clientID, j)
				
				// Random operation type
				switch rand.Intn(3) {
				case 0:
					tester.PerformRead("primary", key, clientName)
				case 1:
					tester.PerformWrite("primary", key, value, clientName)
				case 2:
					// Read first, then CAS
					current := tester.PerformRead("primary", key, clientName)
					if current.Success {
						tester.PerformCAS("primary", key, current.Result, value, clientName)
					}
				}
				
				time.Sleep(time.Duration(rand.Intn(10)+5) * time.Millisecond)
			}
		}(i)
	}

	stressWG.Wait()
	fmt.Printf("Stress test completed: %d clients, %d operations each\n", 
		stressClients, operationsPerClient)

	fmt.Println("\n=== Linearizability Analysis ===")

	// Analyze linearizability
	analysis := tester.CheckLinearizability()

	fmt.Printf("Total operations analyzed: %d\n", analysis["total_operations"])
	fmt.Printf("Keys analyzed: %d\n", analysis["analyzed_keys"])
	fmt.Printf("Is linearizable: %t\n", analysis["is_linearizable"])

	if violations, ok := analysis["violations"].([]map[string]interface{}); ok {
		if len(violations) > 0 {
			fmt.Printf("\n❌ Linearizability violations found (%d):\n", len(violations))
			for i, violation := range violations {
				fmt.Printf("  %d. %s: %s\n", i+1, violation["type"], violation["description"])
				if key, ok := violation["key"]; ok {
					fmt.Printf("     Key: %s\n", key)
				}
			}
		} else {
			fmt.Printf("✅ No linearizability violations found\n")
		}
	}

	if warnings, ok := analysis["warnings"].([]string); ok && len(warnings) > 0 {
		fmt.Printf("\n⚠️ Warnings (%d):\n", len(warnings))
		for i, warning := range warnings {
			fmt.Printf("  %d. %s\n", i+1, warning)
		}
	}

	fmt.Println("\n=== Operation Statistics ===")

	stats := tester.GetStatistics()
	fmt.Printf("Total operations: %d\n", stats["total_operations"])
	fmt.Printf("Success rate: %.1f%%\n", stats["success_rate"].(float64)*100)

	if opsByType, ok := stats["operations_by_type"].(map[string]int); ok {
		fmt.Println("Operations by type:")
		for opType, count := range opsByType {
			fmt.Printf("  %s: %d\n", opType, count)
		}
	}

	if opsByNode, ok := stats["operations_by_node"].(map[string]int); ok {
		fmt.Println("Operations by node:")
		for nodeID, count := range opsByNode {
			fmt.Printf("  %s: %d\n", nodeID, count)
		}
	}

	fmt.Println("\n✅ Linearizability Testing demo completed!")
	fmt.Println("\nKey Insights:")
	fmt.Println("- Linearizability ensures operations appear instantaneous")
	fmt.Println("- Critical for systems requiring strong consistency")
	fmt.Println("- CAS operations help avoid race conditions")
	fmt.Println("- Testing helps verify distributed system correctness")
	fmt.Println("- Network partitions can break linearizability")
}

func main() {
	// Set random seed
	rand.Seed(time.Now().UnixNano())
	
	// Configure logging
	log.SetFlags(log.Ltime | log.Lmicroseconds)
	
	// Run demonstration
	demonstrateLinearizability()
}