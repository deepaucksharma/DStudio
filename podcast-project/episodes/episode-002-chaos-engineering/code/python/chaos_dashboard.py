#!/usr/bin/env python3
"""
Chaos Engineering Dashboard - Episode 2
चाओस इंजीनियरिंग डैशबोर्ड

Real-time dashboard for chaos engineering experiments with Indian context
भारतीय संदर्भ के साथ chaos engineering प्रयोगों के लिए real-time dashboard

जैसे Mumbai traffic control room में सभी signals और traffic की monitoring होती है -
यह भी सभी chaos experiments की real-time monitoring करता है!

Author: Code Developer Agent A5-C-002
Indian Context: GameDay orchestration, Production chaos monitoring
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from enum import Enum
import random
import logging
from flask import Flask, render_template_string, jsonify
import plotly.graph_objs as go
import plotly.utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExperimentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"

class ChaosType(Enum):
    SERVICE_FAILURE = "service_failure"
    NETWORK_LATENCY = "network_latency"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATABASE_SLOWDOWN = "database_slowdown"
    DEPENDENCY_FAILURE = "dependency_failure"

@dataclass
class ChaosExperiment:
    experiment_id: str
    name: str
    description: str
    chaos_type: ChaosType
    target_service: str
    start_time: datetime
    duration_minutes: int
    status: ExperimentStatus = ExperimentStatus.PENDING
    
    # Metrics
    baseline_metrics: Dict[str, float] = field(default_factory=dict)
    current_metrics: Dict[str, float] = field(default_factory=dict)
    impact_score: float = 0.0
    
    # Indian context
    region: str = "mumbai"
    affected_users: int = 0
    business_impact: str = "low"
    recovery_time_minutes: Optional[float] = None
    
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None

class ChaosDashboard:
    def __init__(self):
        self.experiments: Dict[str, ChaosExperiment] = {}
        self.system_health = {
            'mumbai': {'cpu': 45, 'memory': 60, 'response_time': 150, 'error_rate': 0.5},
            'delhi': {'cpu': 40, 'memory': 55, 'response_time': 180, 'error_rate': 0.3},
            'bangalore': {'cpu': 50, 'memory': 65, 'response_time': 120, 'error_rate': 0.2}
        }
        
        self.app = Flask(__name__)
        self.setup_routes()
        self.monitor_thread = None
        self.is_monitoring = False
        
        # Indian services simulation
        self.indian_services = {
            'irctc_booking': {'region': 'delhi', 'critical': True, 'users': 50000},
            'paytm_payments': {'region': 'mumbai', 'critical': True, 'users': 100000},
            'zomato_orders': {'region': 'bangalore', 'critical': False, 'users': 30000},
            'flipkart_catalog': {'region': 'mumbai', 'critical': False, 'users': 80000}
        }
    
    def setup_routes(self):
        @self.app.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_HTML)
        
        @self.app.route('/api/experiments')
        def get_experiments():
            return jsonify([asdict(exp) for exp in self.experiments.values()])
        
        @self.app.route('/api/system_health')
        def get_system_health():
            return jsonify(self.system_health)
        
        @self.app.route('/api/start_experiment/<experiment_id>')
        def start_experiment(experiment_id):
            if experiment_id in self.experiments:
                exp = self.experiments[experiment_id]
                exp.status = ExperimentStatus.RUNNING
                exp.start_time = datetime.now()
                logger.info(f"Started experiment: {exp.name}")
                return jsonify({'status': 'started', 'experiment_id': experiment_id})
            return jsonify({'error': 'Experiment not found'}), 404
        
        @self.app.route('/api/metrics_data')
        def get_metrics_data():
            # Generate plotly chart data
            timestamps = []
            cpu_data = []
            memory_data = []
            response_time_data = []
            
            # Generate last 30 minutes of data
            for i in range(30):
                timestamps.append((datetime.now() - timedelta(minutes=30-i)).strftime('%H:%M'))
                cpu_data.append(random.randint(30, 90))
                memory_data.append(random.randint(40, 85))
                response_time_data.append(random.randint(100, 500))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=timestamps, y=cpu_data, mode='lines', name='CPU %'))
            fig.add_trace(go.Scatter(x=timestamps, y=memory_data, mode='lines', name='Memory %'))
            
            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            return graphJSON
    
    def add_experiment(self, experiment: ChaosExperiment):
        self.experiments[experiment.experiment_id] = experiment
        logger.info(f"Added experiment: {experiment.name} targeting {experiment.target_service}")
    
    def create_sample_experiments(self):
        # IRCTC booking failure experiment
        irctc_exp = ChaosExperiment(
            experiment_id="exp_001",
            name="IRCTC Booking Service Failure",
            description="Simulate booking service failure during peak hours",
            chaos_type=ChaosType.SERVICE_FAILURE,
            target_service="irctc_booking",
            start_time=datetime.now(),
            duration_minutes=15,
            region="delhi",
            affected_users=50000,
            business_impact="high"
        )
        self.add_experiment(irctc_exp)
        
        # Paytm payment latency
        paytm_exp = ChaosExperiment(
            experiment_id="exp_002", 
            name="Paytm Payment Gateway Latency",
            description="Inject 2s latency in payment processing",
            chaos_type=ChaosType.NETWORK_LATENCY,
            target_service="paytm_payments",
            start_time=datetime.now() + timedelta(minutes=5),
            duration_minutes=10,
            region="mumbai",
            affected_users=25000,
            business_impact="medium"
        )
        self.add_experiment(paytm_exp)
        
        # Zomato database slowdown
        zomato_exp = ChaosExperiment(
            experiment_id="exp_003",
            name="Zomato Restaurant DB Slowdown", 
            description="Slow down restaurant database queries by 5x",
            chaos_type=ChaosType.DATABASE_SLOWDOWN,
            target_service="zomato_orders",
            start_time=datetime.now() + timedelta(minutes=10),
            duration_minutes=20,
            region="bangalore",
            affected_users=15000,
            business_impact="low"
        )
        self.add_experiment(zomato_exp)
    
    def start_monitoring(self):
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Started chaos monitoring dashboard")
    
    def _monitoring_loop(self):
        while self.is_monitoring:
            # Update system health metrics
            self._update_system_health()
            
            # Update experiment statuses
            self._update_experiment_statuses()
            
            time.sleep(5)  # Update every 5 seconds
    
    def _update_system_health(self):
        for region in self.system_health:
            health = self.system_health[region]
            
            # Simulate metric variations
            health['cpu'] += random.randint(-5, 5)
            health['cpu'] = max(20, min(95, health['cpu']))
            
            health['memory'] += random.randint(-3, 3) 
            health['memory'] = max(30, min(90, health['memory']))
            
            health['response_time'] += random.randint(-20, 20)
            health['response_time'] = max(50, min(1000, health['response_time']))
            
            health['error_rate'] += random.uniform(-0.1, 0.1)
            health['error_rate'] = max(0, min(5, health['error_rate']))
    
    def _update_experiment_statuses(self):
        current_time = datetime.now()
        
        for exp in self.experiments.values():
            if exp.status == ExperimentStatus.PENDING and exp.start_time <= current_time:
                exp.status = ExperimentStatus.RUNNING
                logger.info(f"Experiment {exp.name} started automatically")
            
            elif exp.status == ExperimentStatus.RUNNING:
                elapsed = (current_time - exp.start_time).total_seconds() / 60
                
                if elapsed >= exp.duration_minutes:
                    exp.status = ExperimentStatus.COMPLETED
                    exp.end_time = current_time
                    exp.recovery_time_minutes = random.uniform(1, 5)
                    logger.info(f"Experiment {exp.name} completed")
                else:
                    # Update metrics during experiment
                    self._update_experiment_metrics(exp, elapsed)
    
    def _update_experiment_metrics(self, exp: ChaosExperiment, elapsed_minutes: float):
        # Simulate impact on system based on experiment type
        service_info = self.indian_services.get(exp.target_service, {})
        region = service_info.get('region', 'mumbai')
        
        if region in self.system_health:
            health = self.system_health[region]
            
            if exp.chaos_type == ChaosType.SERVICE_FAILURE:
                health['error_rate'] = min(5, health['error_rate'] + 0.5)
                exp.impact_score = min(10, elapsed_minutes * 2)
            
            elif exp.chaos_type == ChaosType.NETWORK_LATENCY:
                health['response_time'] = min(1000, health['response_time'] + 50)
                exp.impact_score = min(8, elapsed_minutes * 1.5)
            
            elif exp.chaos_type == ChaosType.DATABASE_SLOWDOWN:
                health['response_time'] = min(1000, health['response_time'] + 30)
                health['cpu'] = min(95, health['cpu'] + 5)
                exp.impact_score = min(6, elapsed_minutes * 1.2)
    
    def run_dashboard(self, host='0.0.0.0', port=5000, debug=False):
        self.start_monitoring()
        self.create_sample_experiments()
        
        logger.info(f"Starting Chaos Engineering Dashboard at http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)

# HTML Template for the dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Chaos Engineering Dashboard | चाओस इंजीनियरिंग डैशबोर्ड</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; text-align: center; }
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .metric { display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; border-radius: 8px; min-width: 120px; text-align: center; }
        .metric-value { font-size: 24px; font-weight: bold; }
        .metric-label { font-size: 12px; color: #666; }
        .experiment { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 8px; }
        .status-pending { border-left: 5px solid #ffc107; }
        .status-running { border-left: 5px solid #17a2b8; background-color: #f0f8ff; }
        .status-completed { border-left: 5px solid #28a745; }
        .status-failed { border-left: 5px solid #dc3545; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn-start { background: #28a745; color: white; }
        .btn-stop { background: #dc3545; color: white; }
        .region-mumbai { color: #ff6b35; }
        .region-delhi { color: #004e92; }
        .region-bangalore { color: #7209b7; }
        .chart-container { width: 100%; height: 400px; }
        .high-impact { color: #dc3545; font-weight: bold; }
        .medium-impact { color: #ffc107; font-weight: bold; }
        .low-impact { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛠️ Chaos Engineering Dashboard</h1>
        <h2>चाओस इंजीनियरिंग डैशबोर्ड</h2>
        <p>Real-time monitoring of chaos experiments across Indian services</p>
        <p>भारतीय सेवाओं में chaos प्रयोगों की real-time निगरानी</p>
    </div>

    <div class="dashboard-grid">
        <div class="card">
            <h3>🏥 System Health | सिस्टम स्वास्थ्य</h3>
            <div id="system-health">
                <!-- System health metrics will be loaded here -->
            </div>
        </div>

        <div class="card">
            <h3>📊 Live Metrics | लाइव मेट्रिक्स</h3>
            <div id="metrics-chart" class="chart-container"></div>
        </div>
    </div>

    <div class="card">
        <h3>🧪 Active Experiments | सक्रिय प्रयोग</h3>
        <div id="experiments-list">
            <!-- Experiments will be loaded here -->
        </div>
    </div>

    <script>
        function updateSystemHealth() {
            $.get('/api/system_health', function(data) {
                let html = '';
                Object.keys(data).forEach(region => {
                    const health = data[region];
                    html += `
                        <div style="border: 1px solid #ddd; margin: 10px; padding: 15px; border-radius: 8px;">
                            <h4 class="region-${region}">🌍 ${region.charAt(0).toUpperCase() + region.slice(1)} Region</h4>
                            <div class="metric">
                                <div class="metric-value">${health.cpu}%</div>
                                <div class="metric-label">CPU Usage</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${health.memory}%</div>
                                <div class="metric-label">Memory</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${health.response_time}ms</div>
                                <div class="metric-label">Response Time</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${health.error_rate.toFixed(2)}%</div>
                                <div class="metric-label">Error Rate</div>
                            </div>
                        </div>
                    `;
                });
                $('#system-health').html(html);
            });
        }

        function updateExperiments() {
            $.get('/api/experiments', function(data) {
                let html = '';
                data.forEach(exp => {
                    const statusClass = `status-${exp.status}`;
                    const impactClass = exp.business_impact === 'high' ? 'high-impact' : 
                                      exp.business_impact === 'medium' ? 'medium-impact' : 'low-impact';
                    
                    html += `
                        <div class="experiment ${statusClass}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h4>🎯 ${exp.name}</h4>
                                    <p><strong>Service:</strong> ${exp.target_service} | 
                                       <strong>Region:</strong> ${exp.region} | 
                                       <strong>Type:</strong> ${exp.chaos_type}</p>
                                    <p>${exp.description}</p>
                                    <p><strong>Status:</strong> ${exp.status} | 
                                       <strong>Impact:</strong> <span class="${impactClass}">${exp.business_impact}</span> | 
                                       <strong>Affected Users:</strong> ${exp.affected_users.toLocaleString()}</p>
                                    ${exp.impact_score > 0 ? `<p><strong>Current Impact Score:</strong> ${exp.impact_score.toFixed(1)}/10</p>` : ''}
                                </div>
                                <div>
                                    ${exp.status === 'pending' ? `<button class="btn btn-start" onclick="startExperiment('${exp.experiment_id}')">Start</button>` : ''}
                                    ${exp.status === 'running' ? '<span style="color: #17a2b8; font-weight: bold;">🔄 RUNNING</span>' : ''}
                                    ${exp.status === 'completed' ? '<span style="color: #28a745; font-weight: bold;">✅ COMPLETED</span>' : ''}
                                </div>
                            </div>
                        </div>
                    `;
                });
                $('#experiments-list').html(html);
            });
        }

        function updateMetricsChart() {
            $.get('/api/metrics_data', function(data) {
                Plotly.newPlot('metrics-chart', JSON.parse(data), {
                    title: 'System Metrics Over Time | समय के साथ सिस्टम मेट्रिक्स',
                    xaxis: { title: 'Time | समय' },
                    yaxis: { title: 'Percentage | प्रतिशत' }
                });
            });
        }

        function startExperiment(experimentId) {
            $.get(`/api/start_experiment/${experimentId}`, function(response) {
                alert(`Experiment ${experimentId} started! | प्रयोग ${experimentId} शुरू हुआ!`);
                updateExperiments();
            });
        }

        // Update dashboard every 5 seconds
        setInterval(function() {
            updateSystemHealth();
            updateExperiments();
        }, 5000);

        // Update metrics chart every 10 seconds
        setInterval(updateMetricsChart, 10000);

        // Initial load
        $(document).ready(function() {
            updateSystemHealth();
            updateExperiments();
            updateMetricsChart();
        });
    </script>
</body>
</html>
"""

def main():
    """Main function to run chaos dashboard demo"""
    print("🛠️ Chaos Engineering Dashboard - Episode 2")
    print("चाओस इंजीनियरिंग डैशबोर्ड - एपिसोड 2\n")
    
    dashboard = ChaosDashboard()
    
    print("Dashboard features:")
    print("1. Real-time system health monitoring")
    print("2. Active chaos experiments tracking")
    print("3. Impact measurement and visualization")
    print("4. Indian service context (IRCTC, Paytm, Zomato)")
    print("5. Regional monitoring (Mumbai, Delhi, Bangalore)")
    
    print("\n" + "="*60)
    print("STARTING DASHBOARD SERVER")
    print("डैशबोर्ड सर्वर शुरू कर रहे हैं")
    print("="*60)
    
    try:
        dashboard.run_dashboard(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        print("उपयोगकर्ता द्वारा डैशबोर्ड बंद किया गया")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")
        print("Note: This demo requires Flask and Plotly packages")
        print("नोट: इस डेमो के लिए Flask और Plotly packages चाहिए")
        
        # Create static demo instead
        print("\nCreating static demo data...")
        dashboard.create_sample_experiments()
        
        print("\nSample experiments created:")
        for exp_id, exp in dashboard.experiments.items():
            print(f"  {exp_id}: {exp.name}")
            print(f"    Target: {exp.target_service} | Region: {exp.region}")
            print(f"    Impact: {exp.business_impact} | Users: {exp.affected_users:,}")
        
        print("\n💡 KEY FEATURES | मुख्य विशेषताएं:")
        print("1. Real-time monitoring of all chaos experiments")
        print("   सभी chaos प्रयोगों की real-time निगरानी")
        print("2. System health metrics across Indian regions")
        print("   भारतीय क्षेत्रों में system health metrics")
        print("3. Business impact assessment")
        print("   व्यापारिक प्रभाव का आकलन")
        print("4. User impact estimation")
        print("   उपयोगकर्ता प्रभाव का अनुमान")

if __name__ == "__main__":
    main()