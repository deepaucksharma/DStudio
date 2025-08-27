#!/usr/bin/env python3
"""
Quantum Hello World - First Quantum Circuit
क्वांटम हैलो वर्ल्ड - पहला क्वांटम सर्किट

Mumbai Local Train Analogy: Qubit like train compartment - can be in superposition
टिकेट चेकर आने से पहले आप किसी भी कम्पार्टमेंट में हो सकते हैं

Author: System Design Hindi Podcast
Cost: Free on simulators, ~₹100/hour on real quantum computers
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MumbaiQuantumIntro:
    """
    Mumbai Local Train के analogy से quantum computing का introduction
    बहुत ही simple examples से शुरुआत करके advanced concepts तक
    """
    
    def __init__(self):
        """Initialize quantum computing playground"""
        self.simulator = AerSimulator()
        logger.info("Mumbai Quantum Computing Introduction initialized")
        print("🚆 Mumbai Local Train meets Quantum Computing!")
        print("=" * 50)
    
    def basic_qubit_demo(self):
        """
        Basic qubit demonstration
        Mumbai Local Train compartment analogy - superposition state
        """
        print("\n🎯 Basic Qubit Demo - Mumbai Local Train Compartment")
        print("-" * 55)
        
        # Create a single qubit circuit
        qc = QuantumCircuit(1, 1)
        
        # Initially qubit is in |0⟩ state (like being in general compartment)
        print("Step 1: Qubit starts in |0⟩ state (General Compartment)")
        print("Initial state: |0⟩ = General compartment (definite)")
        
        # Apply Hadamard gate to create superposition
        qc.h(0)  # Hadamard gate creates superposition
        
        print("\nStep 2: Apply Hadamard gate (टिकेट चेकर अभी नहीं आया)")
        print("Superposition state: |+⟩ = (|0⟩ + |1⟩)/√2")
        print("You are simultaneously in General AND Ladies compartment!")
        print("Until टिकेट चेकर checks, you exist in both states")
        
        # Measure the qubit
        qc.measure(0, 0)
        
        print("\nStep 3: Measurement (टिकेट चेकर आ गया!)")
        print("Quantum superposition collapses to definite state")
        
        # Execute the circuit
        transpiled_qc = transpile(qc, self.simulator)
        job = self.simulator.run(transpiled_qc, shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        print(f"\nResults after 1000 measurements:")
        for state, count in counts.items():
            compartment = "General" if state == "0" else "Ladies"
            percentage = (count / 1000) * 100
            print(f"  {compartment} Compartment: {count} times ({percentage:.1f}%)")
        
        print("\n🎭 Mumbai Analogy Explanation:")
        print("- Before measurement: You're in superposition (both compartments)")
        print("- During measurement: टिकेट चेकर forces you to choose")
        print("- After measurement: You're definitely in one compartment")
        print("- 50-50 probability: Quantum randomness, not classical uncertainty")
        
        # Draw the circuit
        print(f"\nQuantum Circuit:")
        print(qc.draw())
        
        return qc, counts
    
    def mumbai_entanglement_demo(self):
        """
        Quantum entanglement demonstration
        Mumbai friends going to different stations but connected
        """
        print("\n💑 Quantum Entanglement - Mumbai Friends Connection")
        print("-" * 55)
        
        print("Scenario: राम and श्याम are quantum friends")
        print("If राम gets off at Dadar, श्याम instantly gets off at Bandra")
        print("If राम gets off at Bandra, श्याम instantly gets off at Dadar")
        print("They are 'entangled' - spooky action at a distance!")
        
        # Create two-qubit circuit for entanglement
        qc = QuantumCircuit(2, 2)
        
        # Create Bell state (maximally entangled state)
        print("\nStep 1: राम starts in superposition")
        qc.h(0)  # राम in superposition
        
        print("Step 2: राम and श्याम become entangled")
        qc.cx(0, 1)  # CNOT gate creates entanglement
        
        print("Step 3: Measure both friends")
        qc.measure_all()
        
        # Execute the circuit
        transpiled_qc = transpile(qc, self.simulator)
        job = self.simulator.run(transpiled_qc, shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        print(f"\nEntanglement Results (1000 measurements):")
        for state, count in counts.items():
            ram_station = "Dadar" if state[1] == "0" else "Bandra"  # Note: reversed order
            shyam_station = "Bandra" if state[0] == "0" else "Dadar"
            percentage = (count / 1000) * 100
            print(f"  राम at {ram_station}, श्याम at {shyam_station}: {count} times ({percentage:.1f}%)")
        
        print("\n🤝 Entanglement Properties:")
        print("- Perfect correlation: राम and श्याम always at different stations")
        print("- Instantaneous: No matter how far apart, connection is instant")
        print("- Quantum magic: Einstein called it 'spooky action at distance'")
        print("- Cannot be replicated classically")
        
        print(f"\nQuantum Circuit for Entanglement:")
        print(qc.draw())
        
        return qc, counts
    
    def mumbai_superposition_traffic(self):
        """
        Superposition demonstration using Mumbai traffic analogy
        """
        print("\n🚦 Quantum Superposition - Mumbai Traffic Signal")
        print("-" * 52)
        
        print("Mumbai Traffic Scenario:")
        print("🚦 Signal can be Red AND Green simultaneously")
        print("Until you look at it, traffic flows in superposition!")
        
        # Create 2-qubit circuit representing traffic signals
        qc = QuantumCircuit(2, 2)
        qc.label = "Mumbai Traffic Superposition"
        
        # Both signals start in |0⟩ (Red)
        print("\nStep 1: Both signals start Red |00⟩")
        
        # Apply Hadamard to create superposition
        print("Step 2: Apply superposition (Mumbai magic!)")
        qc.h(0)  # Signal 1 in superposition
        qc.h(1)  # Signal 2 in superposition
        
        print("Now signals are in ALL possible states:")
        print("- |00⟩: Both Red (25%)")
        print("- |01⟩: Signal1 Red, Signal2 Green (25%)")
        print("- |10⟩: Signal1 Green, Signal2 Red (25%)")
        print("- |11⟩: Both Green (25%)")
        
        # Measure
        qc.measure_all()
        
        # Execute
        transpiled_qc = transpile(qc, self.simulator)
        job = self.simulator.run(transpiled_qc, shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        print(f"\nTraffic Signal Results (1000 observations):")
        signal_states = {
            "00": "Both Red 🔴🔴",
            "01": "Red-Green 🔴🟢", 
            "10": "Green-Red 🟢🔴",
            "11": "Both Green 🟢🟢"
        }
        
        for state, count in counts.items():
            description = signal_states.get(state, "Unknown")
            percentage = (count / 1000) * 100
            print(f"  {description}: {count} times ({percentage:.1f}%)")
        
        print("\n🌟 Mumbai Quantum Traffic Insights:")
        print("- Superposition allows all traffic states simultaneously")
        print("- Measurement collapses to one definite traffic state")
        print("- Quantum parallelism: Process all possibilities at once")
        print("- Real Mumbai traffic is almost as chaotic! 😄")
        
        print(f"\nQuantum Circuit:")
        print(qc.draw())
        
        return qc, counts
    
    def mumbai_quantum_coin_flip(self):
        """
        Quantum coin flip using Mumbai train ticket analogy
        """
        print("\n🪙 Quantum Coin Flip - Mumbai Train Ticket")
        print("-" * 45)
        
        print("Mumbai Scenario: Online train ticket booking")
        print("🎫 Ticket can be 'Confirmed' or 'Waitlisted' in superposition")
        print("Until IRCTC server responds, you're in both states!")
        
        qc = QuantumCircuit(1, 1)
        
        # Create quantum coin flip
        print("\nStep 1: Start with definite state |0⟩ (No ticket)")
        
        print("Step 2: Apply Hadamard (Click 'Book Ticket' button)")
        qc.h(0)  # Creates superposition
        
        print("Superposition: √(Confirmed + Waitlisted)")
        print("You simultaneously have AND don't have the ticket!")
        
        print("Step 3: IRCTC server responds (Measurement)")
        qc.measure(0, 0)
        
        # Run multiple experiments
        results = {}
        for experiment in range(5):
            transpiled_qc = transpile(qc, self.simulator)
            job = self.simulator.run(transpiled_qc, shots=1)
            result = job.result()
            counts = result.get_counts()
            
            ticket_status = "Confirmed 🎫" if '0' in counts else "Waitlisted 😞"
            results[f"Attempt {experiment + 1}"] = ticket_status
            print(f"  Booking Attempt {experiment + 1}: {ticket_status}")
        
        print("\n🎲 Quantum vs Classical Coin:")
        print("Classical coin: Either heads OR tails")
        print("Quantum coin: Both heads AND tails until measured")
        print("Mumbai IRCTC: Both confirmed AND waitlisted until server responds!")
        
        # Demonstrate true randomness
        print(f"\nQuantum True Randomness Test (1000 flips):")
        transpiled_qc = transpile(qc, self.simulator)
        job = self.simulator.run(transpiled_qc, shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        for state, count in counts.items():
            status = "Confirmed" if state == "0" else "Waitlisted"
            percentage = (count / 1000) * 100
            print(f"  {status}: {count} times ({percentage:.1f}%)")
        
        print(f"\nQuantum Circuit:")
        print(qc.draw())
        
        return qc, results
    
    def mumbai_quantum_interference(self):
        """
        Quantum interference demonstration using Mumbai monsoon analogy
        """
        print("\n🌧️ Quantum Interference - Mumbai Monsoon Waves")
        print("-" * 52)
        
        print("Mumbai Monsoon Scenario:")
        print("🌊 Two waves meet at Marine Drive")
        print("Constructive interference: Bigger waves (High tide)")
        print("Destructive interference: Waves cancel out (Low tide)")
        
        # Create circuit demonstrating interference
        qc = QuantumCircuit(1, 1)
        
        print("\nStep 1: Start with |0⟩ (Calm sea)")
        
        print("Step 2: First wave (Hadamard)")
        qc.h(0)  # First superposition
        
        print("Step 3: Second wave (Another Hadamard)")
        qc.h(0)  # Second Hadamard causes interference
        
        print("Step 4: Measure final wave state")
        qc.measure(0, 0)
        
        # Execute to show interference effect
        transpiled_qc = transpile(qc, self.simulator)
        job = self.simulator.run(transpiled_qc, shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        print(f"\nInterference Results (1000 measurements):")
        for state, count in counts.items():
            wave_state = "Calm sea 🌊" if state == "0" else "Rough sea ⛈️"
            percentage = (count / 1000) * 100
            print(f"  {wave_state}: {count} times ({percentage:.1f}%)")
        
        print("\n🔬 Quantum Interference Analysis:")
        print("Two Hadamards in sequence:")
        print("H|0⟩ = |+⟩ = (|0⟩ + |1⟩)/√2")
        print("H|+⟩ = |0⟩ (Perfect constructive interference!)")
        print("Result: Always returns to |0⟩ (100% calm sea)")
        
        print("\n🌟 Key Insights:")
        print("- Quantum amplitudes can cancel out (destructive interference)")
        print("- Quantum amplitudes can add up (constructive interference)")
        print("- This is how quantum algorithms gain speedup")
        print("- Mumbai monsoon waves behave similarly!")
        
        # Show the mathematical explanation
        print("\n📊 Mathematical Explanation:")
        print("After first H: ψ = (1/√2)(|0⟩ + |1⟩)")
        print("After second H: ψ = (1/√2)((1/√2)(|0⟩ + |1⟩) + (1/√2)(|0⟩ - |1⟩))")
        print("                 = (1/2)(2|0⟩) = |0⟩")
        print("Perfect interference brings us back to start!")
        
        print(f"\nQuantum Circuit:")
        print(qc.draw())
        
        return qc, counts
    
    def run_all_mumbai_demos(self):
        """
        Run all Mumbai quantum computing demonstrations
        """
        print("🎪 Complete Mumbai Quantum Computing Showcase")
        print("=" * 55)
        
        demos = [
            ("Basic Qubit", self.basic_qubit_demo),
            ("Entanglement", self.mumbai_entanglement_demo),
            ("Superposition Traffic", self.mumbai_superposition_traffic),
            ("Quantum Coin Flip", self.mumbai_quantum_coin_flip),
            ("Quantum Interference", self.mumbai_quantum_interference)
        ]
        
        results = {}
        
        for demo_name, demo_func in demos:
            print(f"\n" + "="*60)
            try:
                circuit, demo_results = demo_func()
                results[demo_name] = {
                    "circuit": circuit,
                    "results": demo_results,
                    "success": True
                }
                print(f"✅ {demo_name} completed successfully")
            except Exception as e:
                print(f"❌ {demo_name} failed: {str(e)}")
                results[demo_name] = {
                    "error": str(e),
                    "success": False
                }
        
        # Summary
        print(f"\n🎯 MUMBAI QUANTUM COMPUTING SUMMARY")
        print("=" * 40)
        
        successful_demos = sum(1 for result in results.values() if result.get("success", False))
        total_demos = len(demos)
        
        print(f"Completed Demos: {successful_demos}/{total_demos}")
        print(f"Success Rate: {(successful_demos/total_demos)*100:.1f}%")
        
        print(f"\n🌟 Key Quantum Concepts Learned:")
        print("1. 🎭 Superposition: Being in multiple states simultaneously")
        print("2. 💑 Entanglement: Spooky connections between particles")
        print("3. 🎲 Quantum Randomness: True randomness from quantum mechanics")
        print("4. 🌊 Interference: Quantum amplitudes can cancel or reinforce")
        print("5. 📏 Measurement: Observation collapses quantum superposition")
        
        print(f"\n🚆 Mumbai Analogies Used:")
        print("- Local train compartments ↔ Qubit states")
        print("- Traffic signals ↔ Superposition")
        print("- IRCTC booking ↔ Quantum measurement")
        print("- Marine Drive waves ↔ Quantum interference")
        print("- Connected friends ↔ Quantum entanglement")
        
        print(f"\n💰 Quantum Computing Costs in India:")
        print("- Simulators: Free (unlimited)")
        print("- Real quantum computers: ₹100-500/hour")
        print("- Quantum cloud access: ₹5,000-25,000/month")
        print("- Learning resources: Free (IBM Qiskit, Google Cirq)")
        
        print(f"\n🚀 Next Steps for Learning:")
        print("1. Practice with more complex circuits")
        print("2. Learn quantum algorithms (Shor's, Grover's)")
        print("3. Explore quantum machine learning")
        print("4. Build quantum applications")
        print("5. Join quantum computing communities")
        
        return results

def main():
    """
    Main function to demonstrate Mumbai-style quantum computing
    """
    # Initialize the Mumbai quantum introduction
    mumbai_quantum = MumbaiQuantumIntro()
    
    # Run all demonstrations
    results = mumbai_quantum.run_all_mumbai_demos()
    
    print(f"\n🎉 Mumbai Quantum Computing Journey Complete!")
    print("From Local Trains to Quantum Bits - What a ride! 🚆➡️⚛️")
    
    return mumbai_quantum, results

if __name__ == "__main__":
    mumbai_quantum, results = main()
    print("\n📚 Ready to explore the quantum universe with Mumbai analogies!")