#!/usr/bin/env python3
"""
Quantum Superposition Demo - Mumbai Local Train Analogy
क्वांटम सुपरपोजीशन डेमो - मुंबई लोकल ट्रेन एनालॉजी

Advanced superposition concepts using Mumbai train system
Mumbai peak hours, multiple tracks, and passenger behavior

Author: System Design Hindi Podcast
Cost: Free on simulators, educational purpose
"""

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram, plot_bloch_vector
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Any
import seaborn as sns
from datetime import datetime, timedelta
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MumbaiTrainSuperposition:
    """
    Mumbai Local Train system के through quantum superposition concepts
    Peak hours, multiple lines, और passenger behavior का quantum analogy
    """
    
    def __init__(self):
        """Initialize Mumbai train quantum system"""
        self.simulator = AerSimulator()
        
        # Mumbai train lines
        self.train_lines = {
            'western': ['Churchgate', 'Marine Lines', 'Charni Road', 'Grant Road', 'Mumbai Central',
                       'Mahalaxmi', 'Lower Parel', 'Prabhadevi', 'Dadar', 'Matunga', 'Mahim',
                       'Bandra', 'Khar', 'Santacruz', 'Vile Parle', 'Andheri', 'Jogeshwari',
                       'Ram Mandir', 'Goregaon', 'Malad', 'Kandivali', 'Borivali'],
            'central': ['CST', 'Masjid', 'Sandhurst Road', 'Chinchpokli', 'Currey Road',
                       'Parel', 'Dadar', 'Matunga', 'Sion', 'Kurla', 'Vidyavihar',
                       'Ghatkopar', 'Vikhroli', 'Kanjurmarg', 'Bhandup', 'Nahur',
                       'Mulund', 'Thane', 'Kalva', 'Mumbra'],
            'harbour': ['CST', 'Dockyard Road', 'Reay Road', 'Cotton Green', 'Sewri',
                       'Wadala Road', 'King Circle', 'Mahim', 'Bandra', 'Khar Road',
                       'Santacruz', 'Vile Parle', 'Andheri', 'Jogeshwari', 'Goregaon',
                       'Malad', 'Kandivali', 'Borivali', 'Dahisar']
        }
        
        logger.info("Mumbai Train Superposition System initialized")
        print("🚆 Mumbai Local Train Quantum Superposition Demo")
        print("=" * 55)
    
    def single_passenger_superposition(self):
        """
        Single passenger in superposition across multiple stations
        एक यात्री कई स्टेशनों पर एक साथ - जब तक टिकेट चेकर न आए
        """
        print("\n👤 Single Passenger Superposition Demo")
        print("-" * 42)
        
        print("Scenario: राहुल Mumbai में कहीं भी हो सकता है")
        print("Until GPS पर check नहीं करते, he exists everywhere!")
        
        # Create circuit for 3 qubits = 8 possible locations
        n_qubits = 3
        qc = QuantumCircuit(n_qubits, n_qubits)
        
        # Mumbai stations for our demo
        mumbai_stations = [
            'Churchgate', 'Marine Lines', 'Charni Road', 'Grant Road',
            'Mumbai Central', 'Mahalaxmi', 'Lower Parel', 'Prabhadevi'
        ]
        
        print(f"\nPossible stations: {mumbai_stations}")
        
        # Create uniform superposition (राहुल can be anywhere)
        print("\nStep 1: राहुल enters Mumbai train system")
        for i in range(n_qubits):
            qc.h(i)  # Hadamard on each qubit
        
        print("Step 2: राहुल is now in superposition across ALL stations!")
        print("Quantum state: |ψ⟩ = (1/√8) Σ|station_i⟩")
        
        # Let's check the statevector before measurement
        statevector = Statevector.from_instruction(qc)
        
        print("\nSuperposition probabilities:")
        for i, amplitude in enumerate(statevector.data):
            probability = abs(amplitude) ** 2
            station = mumbai_stations[i] if i < len(mumbai_stations) else f"Station_{i}"
            print(f"  {station}: {probability:.3f} ({probability*100:.1f}%)")
        
        # Now measure (GPS check करते हैं)
        print("\nStep 3: GPS check करते हैं (Measurement)")
        qc.measure_all()
        
        # Execute circuit
        transpiled_qc = transpile(qc, self.simulator)
        job = self.simulator.run(transpiled_qc, shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        print(f"\nGPS Results (1000 checks):")
        for binary_state, count in sorted(counts.items()):
            station_index = int(binary_state, 2)
            station = mumbai_stations[station_index] if station_index < len(mumbai_stations) else f"Unknown_{station_index}"
            percentage = (count / 1000) * 100
            print(f"  Found at {station}: {count} times ({percentage:.1f}%)")
        
        print(f"\n🔍 Superposition Analysis:")
        print(f"- Before GPS: राहुल exists at ALL stations simultaneously")
        print(f"- Equal probability: 1/8 = 12.5% for each station")
        print(f"- After measurement: राहुल collapses to ONE definite location")
        print(f"- Quantum magic: राहुल was literally everywhere at once!")
        
        print(f"\nQuantum Circuit:")
        print(qc.draw())
        
        return qc, counts, mumbai_stations
    
    def peak_hour_superposition(self):
        """
        Peak hour superposition: Passengers in multiple trains simultaneously
        Peak hour में यात्री कई trains में एक साथ
        """
        print("\n🕘 Peak Hour Superposition - Multiple Trains")
        print("-" * 48)
        
        print("Mumbai Peak Hour Scenario (9 AM):")
        print("🚆 Western, Central, and Harbour lines all packed!")
        print("यात्री सभी trains में simultaneously travel कर रहे हैं")
        
        # 3 qubits for 3 train lines
        qc = QuantumCircuit(3, 3)
        
        train_lines = ['Western', 'Central', 'Harbour']
        
        print(f"\nAvailable train lines: {train_lines}")
        
        # Create superposition for peak hour chaos
        print("\nStep 1: Peak hour starts - All trains available")
        qc.h(0)  # Western line superposition
        qc.h(1)  # Central line superposition  
        qc.h(2)  # Harbour line superposition
        
        print("Step 2: Every passenger is in ALL trains simultaneously!")
        
        # Add some peak hour "entanglement" (correlated delays)
        print("Step 3: Train delays become correlated (Rush hour effect)")
        qc.cx(0, 1)  # Western affects Central
        qc.cx(1, 2)  # Central affects Harbour
        
        # Measure which trains people actually catch
        print("Step 4: 9:15 AM - People board specific trains (Measurement)")
        qc.measure_all()
        
        # Execute
        transpiled_qc = transpile(qc, self.simulator)
        job = self.simulator.run(transpiled_qc, shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        print(f"\nPeak Hour Results (1000 commuters):")
        
        # Decode results
        line_combinations = {}
        for binary_state, count in counts.items():
            lines_taken = []
            for i, bit in enumerate(binary_state[::-1]):  # Reverse for correct order
                if bit == '1':
                    lines_taken.append(train_lines[i])
            
            if not lines_taken:
                combination = "Walked to office 🚶"
            else:
                combination = " + ".join(lines_taken)
            
            line_combinations[combination] = count
            percentage = (count / 1000) * 100
            print(f"  {combination}: {count} commuters ({percentage:.1f}%)")
        
        print(f"\n📊 Peak Hour Analysis:")
        print(f"- Superposition allows being in multiple trains at once")
        print(f"- Entanglement creates correlated delays between lines")
        print(f"- Measurement forces choice of specific route")
        print(f"- Real Mumbai: People do try multiple routes simultaneously!")
        
        # Calculate efficiency
        total_line_usage = sum(count for combo, count in line_combinations.items() 
                              if combo != "Walked to office 🚶")
        if total_line_usage > 0:
            efficiency = (total_line_usage / 1000) * 100
            print(f"- Train system efficiency: {efficiency:.1f}%")
        
        print(f"\nQuantum Circuit:")
        print(qc.draw())
        
        return qc, counts, line_combinations
    
    def mumbai_weather_superposition(self):
        """
        Weather-dependent superposition: Mumbai monsoon affects train states
        मुंबई मानसून का trains पर quantum effect
        """
        print("\n🌧️ Mumbai Monsoon Superposition - Weather Quantum Effects")
        print("-" * 58)
        
        print("Mumbai Monsoon Scenario:")
        print("☀️ Sunny: All trains running perfectly")
        print("🌧️ Light rain: Some delays expected")
        print("⛈️ Heavy rain: Major disruptions")
        print("🌊 Flooding: Trains in superposition of running/stopped")
        
        # 4 qubits for comprehensive weather-train state
        qc = QuantumCircuit(4, 4)
        
        # Weather states and train responses
        weather_conditions = ['Sunny', 'Light Rain', 'Heavy Rain', 'Flooding']
        train_states = ['Running', 'Delayed', 'Cancelled', 'Flooded']
        
        print(f"\nWeather conditions: {weather_conditions}")
        print(f"Possible train states: {train_states}")
        
        # Create weather-dependent superposition
        print("\nStep 1: Mumbai weather forecast is uncertain")
        qc.h(0)  # Weather in superposition
        qc.h(1)  # Weather severity in superposition
        
        print("Step 2: Train states depend on weather (Quantum correlation)")
        # Weather affects train operations
        qc.cx(0, 2)  # Weather influences train status
        qc.cx(1, 3)  # Weather severity influences service level
        
        # Add monsoon-specific quantum effects
        print("Step 3: Mumbai monsoon adds extra uncertainty")
        qc.h(2)  # Additional train state uncertainty
        
        # Controlled operations based on weather
        print("Step 4: Weather-train entanglement (Mumbai style)")
        qc.ccx(0, 1, 3)  # Toffoli gate for complex weather-train correlation
        
        # Measure the final state
        print("Step 5: Check actual weather and train status")
        qc.measure_all()
        
        # Execute
        transpiled_qc = transpile(qc, self.simulator)
        job = self.simulator.run(transpiled_qc, shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        print(f"\nMumbai Monsoon Results (1000 observations):")
        
        # Decode weather-train combinations
        weather_train_map = {}
        for binary_state, count in counts.items():
            # Extract weather and train states from binary
            weather_bits = binary_state[2:]  # First 2 bits for weather
            train_bits = binary_state[:2]    # Last 2 bits for train
            
            weather_index = int(weather_bits, 2) % 4
            train_index = int(train_bits, 2) % 4
            
            weather = weather_conditions[weather_index]
            train_status = train_states[train_index]
            
            combination = f"{weather} → {train_status}"
            weather_train_map[combination] = count
            percentage = (count / 1000) * 100
            
            # Add emoji for better visualization
            weather_emoji = {'Sunny': '☀️', 'Light Rain': '🌧️', 
                           'Heavy Rain': '⛈️', 'Flooding': '🌊'}
            train_emoji = {'Running': '🚆', 'Delayed': '⏰', 
                          'Cancelled': '❌', 'Flooded': '💧'}
            
            print(f"  {weather_emoji.get(weather, '🌤️')} {weather} → "
                  f"{train_emoji.get(train_status, '🚂')} {train_status}: "
                  f"{count} times ({percentage:.1f}%)")
        
        print(f"\n🌪️ Mumbai Monsoon Quantum Effects:")
        print(f"- Weather and trains exist in entangled superposition")
        print(f"- Measurement reveals correlated weather-transport state")
        print(f"- Mumbai monsoon creates maximum quantum uncertainty")
        print(f"- Real Mumbai: Weather literally stops trains instantly!")
        
        # Calculate monsoon impact
        disrupted_services = sum(count for combo, count in weather_train_map.items() 
                               if any(status in combo for status in ['Delayed', 'Cancelled', 'Flooded']))
        disruption_rate = (disrupted_services / 1000) * 100
        print(f"- Monsoon disruption rate: {disruption_rate:.1f}%")
        
        print(f"\nQuantum Circuit:")
        print(qc.draw())
        
        return qc, counts, weather_train_map
    
    def mumbai_rush_hour_multiverse(self):
        """
        Rush hour multiverse: Multiple possible commute routes simultaneously
        Rush hour में multiple routes की quantum possibility
        """
        print("\n🌐 Mumbai Rush Hour Multiverse - Quantum Commute Routes")
        print("-" * 60)
        
        print("Multiverse Commute Scenario:")
        print("🏠 Home: Andheri")
        print("🏢 Office: Nariman Point")
        print("⚡ Quantum commuter explores ALL possible routes simultaneously!")
        
        # 3 qubits for route options
        qc = QuantumCircuit(3, 3)
        
        # Possible route combinations
        route_options = {
            '000': 'Direct Western Line 🚆',
            '001': 'Western + Taxi 🚆🚕',
            '010': 'Bus to Bandra + Western 🚌🚆',
            '011': 'Metro + Western 🚇🚆',
            '100': 'Taxi to Dadar + Central 🚕🚂',
            '101': 'Western + Central + Taxi 🚆🚂🚕',
            '110': 'Bus + Metro + Western 🚌🚇🚆',
            '111': 'Full Mumbai experience (All modes) 🚌🚇🚆🚕'
        }
        
        print(f"\nPossible commute routes:")
        for binary, route in route_options.items():
            print(f"  {binary}: {route}")
        
        # Create multiverse superposition
        print("\nStep 1: 8:00 AM - Commute begins, all routes possible")
        qc.h(0)  # Route choice dimension 1
        qc.h(1)  # Route choice dimension 2
        qc.h(2)  # Route choice dimension 3
        
        print("Step 2: Quantum commuter exists in ALL routes simultaneously!")
        print("Superposition: |ψ⟩ = (1/√8) Σ|route_i⟩")
        
        # Add Mumbai-specific route correlations
        print("Step 3: Route choices become correlated (Mumbai chaos)")
        # If Western line is delayed, other options become more likely
        qc.cx(0, 1)  # Correlation between route choices
        
        # Add peak hour uncertainty
        print("Step 4: Peak hour adds extra randomness")
        qc.ry(np.pi/4, 2)  # Rotation for variable route preference
        
        # Measure final route choice
        print("Step 5: 8:30 AM - Commuter makes final route decision")
        qc.measure_all()
        
        # Execute
        transpiled_qc = transpile(qc, self.simulator)
        job = self.simulator.run(transpiled_qc, shots=1000)
        result = job.result()
        counts = result.get_counts()
        
        print(f"\nMumbai Multiverse Commute Results (1000 commuters):")
        
        total_time_saved = 0
        for binary_state, count in sorted(counts.items()):
            route = route_options.get(binary_state, f"Unknown route {binary_state}")
            percentage = (count / 1000) * 100
            
            # Estimate time saved by quantum superposition
            route_complexity = binary_state.count('1')
            time_saved = route_complexity * 5  # 5 minutes per route component
            total_time_saved += time_saved * count
            
            print(f"  {route}: {count} commuters ({percentage:.1f}%)")
            print(f"    Time saved by quantum exploration: {time_saved} minutes")
        
        avg_time_saved = total_time_saved / 1000
        print(f"\n⏱️ Quantum Commute Benefits:")
        print(f"- Average time saved per commuter: {avg_time_saved:.1f} minutes")
        print(f"- Total time saved: {total_time_saved:.0f} minutes per 1000 commuters")
        print(f"- Quantum advantage: Explore all routes simultaneously")
        print(f"- Mumbai reality: Commuters do mentally compute all options!")
        
        # Calculate route efficiency
        complex_routes = sum(count for binary, count in counts.items() 
                           if binary.count('1') >= 2)
        efficiency = (complex_routes / 1000) * 100
        print(f"- Multi-modal route usage: {efficiency:.1f}%")
        
        print(f"\n🎯 Quantum vs Classical Commuting:")
        print(f"Classical: Try one route, get stuck in traffic")
        print(f"Quantum: Exist in all routes, collapse to optimal one")
        print(f"Mumbai: Quantum tunneling through train doors! 😄")
        
        print(f"\nQuantum Circuit:")
        print(qc.draw())
        
        return qc, counts, route_options
    
    def visualize_superposition_results(self, 
                                      all_results: Dict[str, Any],
                                      save_path: str = "mumbai_superposition_analysis.png"):
        """
        Create comprehensive visualization of all superposition demos
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Mumbai Train Quantum Superposition Analysis', fontsize=16, fontweight='bold')
        
        # Demo 1: Single passenger results
        if 'single_passenger' in all_results:
            counts = all_results['single_passenger']['counts']
            stations = list(counts.keys())[:8]  # Top 8 for visibility
            values = [counts.get(station, 0) for station in stations]
            
            axes[0, 0].bar(range(len(stations)), values, color='skyblue')
            axes[0, 0].set_title('Single Passenger Location Distribution')
            axes[0, 0].set_xlabel('Station Binary Code')
            axes[0, 0].set_ylabel('Frequency')
            axes[0, 0].set_xticks(range(len(stations)))
            axes[0, 0].set_xticklabels(stations, rotation=45)
        
        # Demo 2: Peak hour analysis
        if 'peak_hour' in all_results:
            combinations = all_results['peak_hour']['combinations']
            combo_names = list(combinations.keys())[:6]  # Top 6
            combo_values = [combinations[name] for name in combo_names]
            
            colors = plt.cm.Set3(np.linspace(0, 1, len(combo_names)))
            axes[0, 1].pie(combo_values, labels=combo_names, colors=colors, autopct='%1.1f%%')
            axes[0, 1].set_title('Peak Hour Train Line Usage')
        
        # Demo 3: Weather-train correlation heatmap
        if 'weather' in all_results:
            weather_data = all_results['weather']['weather_train_map']
            
            # Create matrix for heatmap
            weather_conditions = ['Sunny', 'Light Rain', 'Heavy Rain', 'Flooding']
            train_states = ['Running', 'Delayed', 'Cancelled', 'Flooded']
            
            heatmap_data = np.zeros((4, 4))
            for combo, count in weather_data.items():
                for i, weather in enumerate(weather_conditions):
                    for j, train_state in enumerate(train_states):
                        if weather in combo and train_state in combo:
                            heatmap_data[i, j] = count
            
            sns.heatmap(heatmap_data, 
                       xticklabels=train_states, 
                       yticklabels=weather_conditions,
                       annot=True, fmt='.0f', cmap='YlOrRd', ax=axes[1, 0])
            axes[1, 0].set_title('Weather-Train State Correlation')
            axes[1, 0].set_xlabel('Train State')
            axes[1, 0].set_ylabel('Weather Condition')
        
        # Demo 4: Route complexity analysis
        if 'multiverse' in all_results:
            route_counts = all_results['multiverse']['counts']
            
            # Analyze route complexity
            complexity_dist = {}
            for binary_state, count in route_counts.items():
                complexity = binary_state.count('1')
                complexity_dist[complexity] = complexity_dist.get(complexity, 0) + count
            
            complexities = sorted(complexity_dist.keys())
            frequencies = [complexity_dist[c] for c in complexities]
            
            axes[1, 1].bar(complexities, frequencies, color='lightcoral')
            axes[1, 1].set_title('Commute Route Complexity Distribution')
            axes[1, 1].set_xlabel('Route Complexity (Number of Transport Modes)')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].set_xticks(complexities)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"Superposition analysis visualization saved to {save_path}")
    
    def run_all_superposition_demos(self):
        """
        Run complete Mumbai superposition demonstration suite
        """
        print("🎪 Complete Mumbai Train Superposition Showcase")
        print("=" * 60)
        
        demos = [
            ("single_passenger", "Single Passenger Superposition", self.single_passenger_superposition),
            ("peak_hour", "Peak Hour Multi-Train Superposition", self.peak_hour_superposition),
            ("weather", "Monsoon Weather-Train Superposition", self.mumbai_weather_superposition),
            ("multiverse", "Rush Hour Multiverse Routes", self.mumbai_rush_hour_multiverse)
        ]
        
        all_results = {}
        
        for demo_key, demo_name, demo_func in demos:
            print(f"\n" + "="*70)
            try:
                circuit, counts, extra_data = demo_func()
                all_results[demo_key] = {
                    "circuit": circuit,
                    "counts": counts,
                    "extra_data": extra_data,
                    "success": True
                }
                print(f"✅ {demo_name} completed successfully")
            except Exception as e:
                print(f"❌ {demo_name} failed: {str(e)}")
                all_results[demo_key] = {
                    "error": str(e),
                    "success": False
                }
        
        # Create comprehensive visualization
        successful_results = {k: v for k, v in all_results.items() if v.get("success", False)}
        if successful_results:
            self.visualize_superposition_results(successful_results)
        
        # Generate comprehensive report
        print(f"\n📊 MUMBAI SUPERPOSITION SHOWCASE SUMMARY")
        print("=" * 50)
        
        successful_demos = sum(1 for result in all_results.values() if result.get("success", False))
        total_demos = len(demos)
        
        print(f"Completed Demos: {successful_demos}/{total_demos}")
        print(f"Success Rate: {(successful_demos/total_demos)*100:.1f}%")
        
        print(f"\n🌟 Advanced Superposition Concepts Demonstrated:")
        print("1. 🎭 Multi-qubit superposition (parallel train existence)")
        print("2. 🔗 Quantum correlations (weather-train dependencies)")
        print("3. 🌐 Multiverse exploration (all route possibilities)")
        print("4. ⚡ Quantum interference in transportation")
        print("5. 📊 Probability amplitude analysis")
        
        print(f"\n🚆 Mumbai Train System Quantum Analogies:")
        print("- Passengers = Qubits in superposition")
        print("- Train lines = Quantum state spaces")
        print("- Peak hours = Maximum superposition")
        print("- Weather = External quantum noise")
        print("- Route choices = Quantum measurement outcomes")
        
        print(f"\n🎯 Real-world Applications:")
        print("- Quantum route optimization algorithms")
        print("- Traffic flow superposition modeling")
        print("- Weather prediction with quantum uncertainty")
        print("- Multi-modal transport quantum planning")
        
        print(f"\n💡 Key Insights for Quantum Computing:")
        print("- Superposition enables massive parallelism")
        print("- Measurement collapses infinite possibilities to one")
        print("- Quantum correlations model real-world dependencies")
        print("- Mumbai chaos = Natural quantum system! 😄")
        
        return all_results

def main():
    """
    Main function for Mumbai superposition demonstration
    """
    # Initialize the system
    mumbai_quantum = MumbaiTrainSuperposition()
    
    # Run all demonstrations
    results = mumbai_quantum.run_all_superposition_demos()
    
    print(f"\n🎉 Mumbai Train Superposition Journey Complete!")
    print("From Classical Trains to Quantum Superposition - Mind = Blown! 🤯")
    
    return mumbai_quantum, results

if __name__ == "__main__":
    mumbai_system, demo_results = main()
    print("\n🚆 Ready to catch the quantum train to the future! ⚛️➡️🚀")