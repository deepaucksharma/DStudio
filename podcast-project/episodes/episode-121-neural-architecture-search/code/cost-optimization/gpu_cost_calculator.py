"""
GPU Cost Calculator for Neural Architecture Search
Indian cloud providers और global providers के लिए cost optimization
Flipkart, Zomato जैसी companies के लिए NAS training cost analysis
"""

import torch
import numpy as np
import pandas as pd
import logging
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Tuple, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import requests
import time
from enum import Enum

# Hindi comments के साथ logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudProvider(Enum):
    """Cloud provider options"""
    # Indian providers
    JIO_CLOUD = "jio_cloud"
    TATA_CLOUD = "tata_cloud"
    AIRTEL_CLOUD = "airtel_cloud"
    YOTTA_CLOUD = "yotta_cloud"
    
    # Global providers
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    OCI = "oci"  # Oracle Cloud (has presence in India)

@dataclass
class GPUInstance:
    """GPU instance specification"""
    name: str
    provider: CloudProvider
    gpu_type: str
    gpu_count: int
    gpu_memory_gb: int
    cpu_cores: int
    ram_gb: int
    storage_gb: int
    network_gbps: float
    
    # Pricing (INR per hour)
    cost_per_hour_inr: float
    cost_per_hour_usd: float
    
    # Performance characteristics
    fp32_tflops: float
    fp16_tflops: float
    tensor_tflops: float  # For AI workloads
    
    # Regional availability
    regions: List[str] = field(default_factory=list)
    availability_score: float = 1.0  # 0-1, where 1 is always available

@dataclass 
class NASTrainingConfig:
    """NAS training configuration for cost estimation"""
    # Architecture search parameters
    search_epochs: int = 50
    supernet_epochs: int = 300
    architecture_candidates: int = 1000
    final_training_epochs: int = 600
    
    # Dataset configuration
    dataset_size: int = 1000000  # Number of images
    image_resolution: int = 224
    num_classes: int = 1000
    
    # Training configuration
    batch_size: int = 256
    num_workers: int = 8
    mixed_precision: bool = True
    gradient_accumulation_steps: int = 1
    
    # Model configuration
    max_parameters: int = 50000000  # 50M parameters
    target_flops: int = 500000000   # 500M FLOPs
    
    # Cost optimization
    spot_instances: bool = True
    preemptible_discount: float = 0.7  # 30% savings
    reserved_instances: bool = False
    reserved_discount: float = 0.4     # 60% savings

class GPUCostDatabase:
    """
    Database of GPU instances from Indian and global cloud providers
    Real-time pricing और availability के साथ
    """
    
    def __init__(self):
        self.instances = self._load_gpu_instances()
        self.exchange_rate_usd_to_inr = 83.0  # Current rate (update regularly)
        self.last_price_update = datetime.now()
    
    def _load_gpu_instances(self) -> List[GPUInstance]:
        """Load GPU instance configurations"""
        instances = [
            # Indian Cloud Providers
            
            # Jio Cloud (Estimated pricing)
            GPUInstance(
                name="jio-gpu-v100-1x", provider=CloudProvider.JIO_CLOUD,
                gpu_type="NVIDIA V100", gpu_count=1, gpu_memory_gb=32,
                cpu_cores=8, ram_gb=64, storage_gb=500, network_gbps=10.0,
                cost_per_hour_inr=180.0, cost_per_hour_usd=2.17,
                fp32_tflops=15.7, fp16_tflops=31.4, tensor_tflops=125.0,
                regions=["mumbai", "delhi", "bangalore"], availability_score=0.85
            ),
            GPUInstance(
                name="jio-gpu-a100-1x", provider=CloudProvider.JIO_CLOUD,
                gpu_type="NVIDIA A100", gpu_count=1, gpu_memory_gb=80,
                cpu_cores=16, ram_gb=128, storage_gb=1000, network_gbps=25.0,
                cost_per_hour_inr=350.0, cost_per_hour_usd=4.22,
                fp32_tflops=19.5, fp16_tflops=78.0, tensor_tflops=312.0,
                regions=["mumbai", "pune"], availability_score=0.7
            ),
            
            # Tata Cloud
            GPUInstance(
                name="tata-gpu-t4-2x", provider=CloudProvider.TATA_CLOUD,
                gpu_type="NVIDIA T4", gpu_count=2, gpu_memory_gb=32,
                cpu_cores=16, ram_gb=64, storage_gb=500, network_gbps=10.0,
                cost_per_hour_inr=150.0, cost_per_hour_usd=1.81,
                fp32_tflops=16.8, fp16_tflops=33.6, tensor_tflops=130.0,
                regions=["mumbai", "delhi", "chennai"], availability_score=0.9
            ),
            GPUInstance(
                name="tata-gpu-v100-4x", provider=CloudProvider.TATA_CLOUD,
                gpu_type="NVIDIA V100", gpu_count=4, gpu_memory_gb=128,
                cpu_cores=32, ram_gb=256, storage_gb=2000, network_gbps=50.0,
                cost_per_hour_inr=650.0, cost_per_hour_usd=7.83,
                fp32_tflops=62.8, fp16_tflops=125.6, tensor_tflops=500.0,
                regions=["mumbai", "bangalore"], availability_score=0.75
            ),
            
            # Yotta Cloud (NTT Communications India)
            GPUInstance(
                name="yotta-gpu-a100-2x", provider=CloudProvider.YOTTA_CLOUD,
                gpu_type="NVIDIA A100", gpu_count=2, gpu_memory_gb=160,
                cpu_cores=32, ram_gb=256, storage_gb=2000, network_gbps=50.0,
                cost_per_hour_inr=600.0, cost_per_hour_usd=7.23,
                fp32_tflops=39.0, fp16_tflops=156.0, tensor_tflops=624.0,
                regions=["mumbai", "delhi"], availability_score=0.8
            ),
            
            # AWS India
            GPUInstance(
                name="p3.2xlarge", provider=CloudProvider.AWS,
                gpu_type="NVIDIA V100", gpu_count=1, gpu_memory_gb=16,
                cpu_cores=8, ram_gb=61, storage_gb=0, network_gbps=10.0,
                cost_per_hour_inr=275.0, cost_per_hour_usd=3.31,
                fp32_tflops=15.7, fp16_tflops=31.4, tensor_tflops=125.0,
                regions=["ap-south-1"], availability_score=0.95
            ),
            GPUInstance(
                name="p4d.24xlarge", provider=CloudProvider.AWS,
                gpu_type="NVIDIA A100", gpu_count=8, gpu_memory_gb=320,
                cpu_cores=96, ram_gb=1152, storage_gb=8000, network_gbps=400.0,
                cost_per_hour_inr=2740.0, cost_per_hour_usd=33.02,
                fp32_tflops=156.0, fp16_tflops=624.0, tensor_tflops=2496.0,
                regions=["ap-south-1"], availability_score=0.85
            ),
            
            # Google Cloud India
            GPUInstance(
                name="n1-highmem-8-v100", provider=CloudProvider.GCP,
                gpu_type="NVIDIA V100", gpu_count=1, gpu_memory_gb=16,
                cpu_cores=8, ram_gb=52, storage_gb=0, network_gbps=16.0,
                cost_per_hour_inr=245.0, cost_per_hour_usd=2.95,
                fp32_tflops=15.7, fp16_tflops=31.4, tensor_tflops=125.0,
                regions=["asia-south1"], availability_score=0.9
            ),
            GPUInstance(
                name="a2-highgpu-4g", provider=CloudProvider.GCP,
                gpu_type="NVIDIA A100", gpu_count=4, gpu_memory_gb=320,
                cpu_cores=48, ram_gb=340, storage_gb=0, network_gbps=100.0,
                cost_per_hour_inr=1680.0, cost_per_hour_usd=20.24,
                fp32_tflops=78.0, fp16_tflops=312.0, tensor_tflops=1248.0,
                regions=["asia-south1"], availability_score=0.8
            ),
            
            # Azure India
            GPUInstance(
                name="NC6s_v3", provider=CloudProvider.AZURE,
                gpu_type="NVIDIA V100", gpu_count=1, gpu_memory_gb=16,
                cpu_cores=6, ram_gb=112, storage_gb=0, network_gbps=12.0,
                cost_per_hour_inr=290.0, cost_per_hour_usd=3.49,
                fp32_tflops=15.7, fp16_tflops=31.4, tensor_tflops=125.0,
                regions=["centralindia", "southindia"], availability_score=0.9
            ),
            GPUInstance(
                name="ND96asr_v4", provider=CloudProvider.AZURE,
                gpu_type="NVIDIA A100", gpu_count=8, gpu_memory_gb=320,
                cpu_cores=96, ram_gb=900, storage_gb=6000, network_gbps=200.0,
                cost_per_hour_inr=2900.0, cost_per_hour_usd=34.94,
                fp32_tflops=156.0, fp16_tflops=624.0, tensor_tflops=2496.0,
                regions=["centralindia"], availability_score=0.75
            )
        ]
        
        return instances
    
    def get_instances_by_provider(self, provider: CloudProvider) -> List[GPUInstance]:
        """Get instances for specific cloud provider"""
        return [inst for inst in self.instances if inst.provider == provider]
    
    def get_instances_by_gpu_type(self, gpu_type: str) -> List[GPUInstance]:
        """Get instances with specific GPU type"""
        return [inst for inst in self.instances if gpu_type.lower() in inst.gpu_type.lower()]
    
    def get_instances_in_budget(self, max_cost_per_hour_inr: float) -> List[GPUInstance]:
        """Get instances within budget"""
        return [inst for inst in self.instances if inst.cost_per_hour_inr <= max_cost_per_hour_inr]
    
    def update_exchange_rate(self):
        """Update USD to INR exchange rate (placeholder for real API)"""
        try:
            # In real implementation, fetch from exchange rate API
            # For demo, using fixed rate
            self.exchange_rate_usd_to_inr = 83.0
            self.last_price_update = datetime.now()
            logger.info(f"💱 Exchange rate updated: 1 USD = ₹{self.exchange_rate_usd_to_inr}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to update exchange rate: {e}")

class NASCostEstimator:
    """
    Neural Architecture Search cost estimator
    Different phases की cost calculation के साथ
    """
    
    def __init__(self, gpu_database: GPUCostDatabase):
        self.gpu_db = gpu_database
        self.training_phases = {
            'supernet_training': 0.6,      # 60% of total time
            'architecture_search': 0.3,    # 30% of total time  
            'final_training': 0.1          # 10% of total time
        }
    
    def estimate_training_time(self, config: NASTrainingConfig, 
                             instance: GPUInstance) -> Dict[str, float]:
        """
        Estimate training time for each phase of NAS
        """
        # Base calculations (simplified model)
        samples_per_second = self._calculate_throughput(config, instance)
        
        # Supernet training time
        supernet_samples = config.search_epochs * config.dataset_size
        supernet_time_hours = supernet_samples / (samples_per_second * 3600)
        
        # Architecture search time (more efficient, parallel evaluation)
        search_time_hours = supernet_time_hours * 0.5  # 50% of supernet time
        
        # Final training time (single architecture, longer training)
        final_samples = config.final_training_epochs * config.dataset_size
        final_time_hours = final_samples / (samples_per_second * 3600)
        
        # Apply efficiency factors
        if config.mixed_precision:
            # Mixed precision speeds up training
            supernet_time_hours *= 0.7
            search_time_hours *= 0.7
            final_time_hours *= 0.7
        
        if instance.gpu_count > 1:
            # Multi-GPU scaling (not perfectly linear)
            scaling_efficiency = min(0.9, 0.6 + 0.1 * instance.gpu_count)
            supernet_time_hours /= (instance.gpu_count * scaling_efficiency)
            search_time_hours /= (instance.gpu_count * scaling_efficiency)
            final_time_hours /= (instance.gpu_count * scaling_efficiency)
        
        total_time_hours = supernet_time_hours + search_time_hours + final_time_hours
        
        return {
            'supernet_training_hours': supernet_time_hours,
            'architecture_search_hours': search_time_hours,
            'final_training_hours': final_time_hours,
            'total_training_hours': total_time_hours,
            'estimated_throughput_samples_per_second': samples_per_second
        }
    
    def _calculate_throughput(self, config: NASTrainingConfig, 
                            instance: GPUInstance) -> float:
        """Calculate training throughput (samples per second)"""
        # Base throughput calculation (simplified)
        base_throughput = 100  # samples/second for baseline
        
        # GPU performance factor
        gpu_factor = instance.tensor_tflops / 125.0  # Normalized to V100
        
        # Batch size factor
        batch_factor = config.batch_size / 256.0
        
        # Image resolution factor (quadratic impact)
        resolution_factor = (224 / config.image_resolution) ** 2
        
        # Memory constraint factor
        memory_per_sample = (config.image_resolution ** 2 * 3 * 4) / (1024 ** 3)  # GB
        max_batch_size = instance.gpu_memory_gb / (memory_per_sample * 4)  # 4x overhead
        memory_factor = min(1.0, max_batch_size / config.batch_size)
        
        throughput = (base_throughput * gpu_factor * batch_factor * 
                     resolution_factor * memory_factor)
        
        return max(10, throughput)  # Minimum 10 samples/second
    
    def calculate_cost_breakdown(self, config: NASTrainingConfig, 
                               instance: GPUInstance) -> Dict[str, Any]:
        """
        Calculate detailed cost breakdown for NAS training
        """
        # Get training time estimates
        time_estimates = self.estimate_training_time(config, instance)
        
        # Base hourly cost
        base_cost_per_hour = instance.cost_per_hour_inr
        
        # Apply discounts
        if config.spot_instances:
            effective_cost_per_hour = base_cost_per_hour * config.preemptible_discount
            discount_type = "Spot/Preemptible"
            discount_percentage = (1 - config.preemptible_discount) * 100
        elif config.reserved_instances:
            effective_cost_per_hour = base_cost_per_hour * config.reserved_discount
            discount_type = "Reserved Instance"
            discount_percentage = (1 - config.reserved_discount) * 100
        else:
            effective_cost_per_hour = base_cost_per_hour
            discount_type = "On-Demand"
            discount_percentage = 0
        
        # Calculate costs for each phase
        supernet_cost = (time_estimates['supernet_training_hours'] * 
                        effective_cost_per_hour)
        search_cost = (time_estimates['architecture_search_hours'] * 
                      effective_cost_per_hour)
        final_cost = (time_estimates['final_training_hours'] * 
                     effective_cost_per_hour)
        
        total_compute_cost = supernet_cost + search_cost + final_cost
        
        # Additional costs
        storage_cost = self._calculate_storage_cost(config, time_estimates['total_training_hours'])
        data_transfer_cost = self._calculate_data_transfer_cost(config)
        monitoring_cost = total_compute_cost * 0.02  # 2% of compute cost
        
        total_cost = total_compute_cost + storage_cost + data_transfer_cost + monitoring_cost
        
        # Cost per architecture candidate
        cost_per_candidate = total_cost / max(1, config.architecture_candidates)
        
        return {
            'instance_info': {
                'name': instance.name,
                'provider': instance.provider.value,
                'gpu_type': instance.gpu_type,
                'gpu_count': instance.gpu_count,
                'hourly_rate_inr': base_cost_per_hour,
                'effective_rate_inr': effective_cost_per_hour,
                'discount_type': discount_type,
                'discount_percentage': discount_percentage
            },
            'time_breakdown_hours': time_estimates,
            'cost_breakdown_inr': {
                'supernet_training': supernet_cost,
                'architecture_search': search_cost,
                'final_training': final_cost,
                'compute_total': total_compute_cost,
                'storage': storage_cost,
                'data_transfer': data_transfer_cost,
                'monitoring': monitoring_cost,
                'total_cost': total_cost
            },
            'efficiency_metrics': {
                'cost_per_hour_per_gpu': effective_cost_per_hour / instance.gpu_count,
                'cost_per_candidate': cost_per_candidate,
                'cost_per_tflop_hour': effective_cost_per_hour / instance.tensor_tflops,
                'total_training_days': time_estimates['total_training_hours'] / 24
            },
            'config_impact': {
                'mixed_precision_savings_inr': total_compute_cost * 0.3 if config.mixed_precision else 0,
                'multi_gpu_efficiency': min(0.9, 0.6 + 0.1 * instance.gpu_count) if instance.gpu_count > 1 else 1.0,
                'spot_instance_savings_inr': (base_cost_per_hour - effective_cost_per_hour) * time_estimates['total_training_hours']
            }
        }
    
    def _calculate_storage_cost(self, config: NASTrainingConfig, 
                              training_hours: float) -> float:
        """Calculate storage costs"""
        # Dataset storage
        dataset_size_gb = (config.dataset_size * config.image_resolution ** 2 * 3) / (1024 ** 3)
        
        # Model checkpoints and logs
        checkpoint_size_gb = config.max_parameters * 4 / (1024 ** 3)  # 4 bytes per parameter
        num_checkpoints = max(10, training_hours / 5)  # Checkpoint every 5 hours
        total_checkpoint_gb = checkpoint_size_gb * num_checkpoints
        
        # Intermediate results
        intermediate_gb = dataset_size_gb * 0.1  # 10% of dataset size
        
        total_storage_gb = dataset_size_gb + total_checkpoint_gb + intermediate_gb
        
        # Storage cost (₹2 per GB per month, prorated)
        storage_cost_per_gb_hour = 2.0 / (30 * 24)  # Monthly to hourly
        storage_cost = total_storage_gb * storage_cost_per_gb_hour * training_hours
        
        return storage_cost
    
    def _calculate_data_transfer_cost(self, config: NASTrainingConfig) -> float:
        """Calculate data transfer costs"""
        # Dataset download (one-time)
        dataset_size_gb = (config.dataset_size * config.image_resolution ** 2 * 3) / (1024 ** 3)
        
        # Model uploads/downloads
        model_transfer_gb = config.max_parameters * 4 / (1024 ** 3) * 5  # 5 model transfers
        
        total_transfer_gb = dataset_size_gb + model_transfer_gb
        
        # Data transfer cost (₹5 per GB)
        transfer_cost = total_transfer_gb * 5.0
        
        return transfer_cost
    
    def compare_providers(self, config: NASTrainingConfig, 
                         max_budget_inr: Optional[float] = None) -> pd.DataFrame:
        """
        Compare costs across different cloud providers
        """
        results = []
        
        for instance in self.gpu_db.instances:
            try:
                cost_breakdown = self.calculate_cost_breakdown(config, instance)
                
                # Skip if over budget
                if max_budget_inr and cost_breakdown['cost_breakdown_inr']['total_cost'] > max_budget_inr:
                    continue
                
                result = {
                    'Provider': instance.provider.value,
                    'Instance': instance.name,
                    'GPU_Type': instance.gpu_type,
                    'GPU_Count': instance.gpu_count,
                    'Total_Cost_INR': cost_breakdown['cost_breakdown_inr']['total_cost'],
                    'Training_Days': cost_breakdown['efficiency_metrics']['total_training_days'],
                    'Cost_Per_Candidate_INR': cost_breakdown['efficiency_metrics']['cost_per_candidate'],
                    'Hourly_Rate_INR': cost_breakdown['instance_info']['effective_rate_inr'],
                    'Availability_Score': instance.availability_score,
                    'Indian_Provider': instance.provider.value in ['jio_cloud', 'tata_cloud', 'airtel_cloud', 'yotta_cloud']
                }
                
                results.append(result)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to calculate cost for {instance.name}: {e}")
        
        df = pd.DataFrame(results)
        
        if not df.empty:
            # Sort by total cost
            df = df.sort_values('Total_Cost_INR')
            
            # Add cost efficiency ranking
            df['Cost_Efficiency_Rank'] = df['Total_Cost_INR'].rank()
            df['Speed_Rank'] = df['Training_Days'].rank()
            df['Overall_Score'] = (df['Cost_Efficiency_Rank'] + df['Speed_Rank']) / 2
        
        return df
    
    def optimize_configuration(self, config: NASTrainingConfig, 
                             target_budget_inr: float,
                             preferred_providers: List[CloudProvider] = None) -> Dict[str, Any]:
        """
        Optimize NAS configuration to fit within budget
        """
        if preferred_providers is None:
            # Default to Indian providers first
            preferred_providers = [
                CloudProvider.JIO_CLOUD, CloudProvider.TATA_CLOUD,
                CloudProvider.YOTTA_CLOUD, CloudProvider.AWS, CloudProvider.GCP
            ]
        
        best_config = None
        best_instance = None
        best_cost = float('inf')
        optimization_log = []
        
        for provider in preferred_providers:
            provider_instances = self.gpu_db.get_instances_by_provider(provider)
            
            for instance in provider_instances:
                for spot in [True, False]:
                    for mixed_precision in [True, False]:
                        # Create test configuration
                        test_config = NASTrainingConfig(
                            search_epochs=config.search_epochs,
                            supernet_epochs=config.supernet_epochs,
                            architecture_candidates=config.architecture_candidates,
                            final_training_epochs=config.final_training_epochs,
                            dataset_size=config.dataset_size,
                            image_resolution=config.image_resolution,
                            num_classes=config.num_classes,
                            batch_size=config.batch_size,
                            spot_instances=spot,
                            mixed_precision=mixed_precision
                        )
                        
                        try:
                            cost_breakdown = self.calculate_cost_breakdown(test_config, instance)
                            total_cost = cost_breakdown['cost_breakdown_inr']['total_cost']
                            
                            optimization_log.append({
                                'provider': provider.value,
                                'instance': instance.name,
                                'spot_instances': spot,
                                'mixed_precision': mixed_precision,
                                'total_cost_inr': total_cost,
                                'within_budget': total_cost <= target_budget_inr,
                                'training_days': cost_breakdown['efficiency_metrics']['total_training_days']
                            })
                            
                            if total_cost <= target_budget_inr and total_cost < best_cost:
                                best_cost = total_cost
                                best_config = test_config
                                best_instance = instance
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Optimization test failed: {e}")
        
        if best_config and best_instance:
            final_breakdown = self.calculate_cost_breakdown(best_config, best_instance)
            
            return {
                'optimized_config': best_config,
                'recommended_instance': best_instance,
                'cost_breakdown': final_breakdown,
                'budget_utilization': best_cost / target_budget_inr,
                'optimization_log': optimization_log,
                'savings_vs_baseline': (optimization_log[0]['total_cost_inr'] - best_cost) if optimization_log else 0
            }
        else:
            return {
                'optimized_config': None,
                'recommended_instance': None,
                'message': f"No configuration found within budget of ₹{target_budget_inr:,.2f}",
                'optimization_log': optimization_log,
                'minimum_budget_required': min([entry['total_cost_inr'] for entry in optimization_log]) if optimization_log else None
            }

# Visualization and reporting functions

def create_cost_comparison_chart(comparison_df: pd.DataFrame, save_path: Optional[str] = None):
    """Create cost comparison visualization"""
    plt.style.use('seaborn-v0_8')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Total cost comparison
    indian_mask = comparison_df['Indian_Provider']
    
    ax1.bar(comparison_df[indian_mask]['Instance'], 
           comparison_df[indian_mask]['Total_Cost_INR'], 
           alpha=0.7, color='orange', label='Indian Providers')
    ax1.bar(comparison_df[~indian_mask]['Instance'], 
           comparison_df[~indian_mask]['Total_Cost_INR'], 
           alpha=0.7, color='blue', label='Global Providers')
    ax1.set_xlabel('Instance Type')
    ax1.set_ylabel('Total Cost (₹)')
    ax1.set_title('Total Training Cost Comparison')
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    
    # 2. Cost per candidate
    ax2.scatter(comparison_df['Training_Days'], comparison_df['Cost_Per_Candidate_INR'],
               c=comparison_df['Indian_Provider'].map({True: 'orange', False: 'blue'}),
               alpha=0.7, s=100)
    ax2.set_xlabel('Training Days')
    ax2.set_ylabel('Cost per Architecture Candidate (₹)')
    ax2.set_title('Training Speed vs Cost Efficiency')
    
    # 3. Provider cost distribution
    provider_costs = comparison_df.groupby('Provider')['Total_Cost_INR'].mean()
    ax3.pie(provider_costs.values, labels=provider_costs.index, autopct='%1.1f%%')
    ax3.set_title('Average Cost Distribution by Provider')
    
    # 4. GPU type performance
    gpu_perf = comparison_df.groupby('GPU_Type').agg({
        'Total_Cost_INR': 'mean',
        'Training_Days': 'mean'
    }).reset_index()
    
    ax4.scatter(gpu_perf['Training_Days'], gpu_perf['Total_Cost_INR'], s=150, alpha=0.7)
    for i, gpu in enumerate(gpu_perf['GPU_Type']):
        ax4.annotate(gpu, (gpu_perf['Training_Days'].iloc[i], gpu_perf['Total_Cost_INR'].iloc[i]))
    ax4.set_xlabel('Average Training Days')
    ax4.set_ylabel('Average Total Cost (₹)')
    ax4.set_title('GPU Type Performance vs Cost')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"📊 Cost comparison chart saved: {save_path}")
    
    plt.show()

# Demonstration functions

def demo_cost_estimation():
    """Demonstrate cost estimation for different scenarios"""
    print("\n💰 === NAS Cost Estimation Demo ===")
    
    # Initialize database and estimator
    gpu_db = GPUCostDatabase()
    estimator = NASCostEstimator(gpu_db)
    
    # Create sample configuration
    config = NASTrainingConfig(
        search_epochs=30,
        supernet_epochs=200,
        architecture_candidates=500,
        final_training_epochs=300,
        dataset_size=500000,  # 500K images
        mixed_precision=True,
        spot_instances=True
    )
    
    print("🔍 Sample NAS Configuration:")
    print(f"  Search epochs: {config.search_epochs}")
    print(f"  Architecture candidates: {config.architecture_candidates}")
    print(f"  Dataset size: {config.dataset_size:,} images")
    print(f"  Mixed precision: {config.mixed_precision}")
    print(f"  Spot instances: {config.spot_instances}")
    
    # Test with Indian cloud provider
    jio_instances = gpu_db.get_instances_by_provider(CloudProvider.JIO_CLOUD)
    if jio_instances:
        instance = jio_instances[0]  # Use first Jio instance
        
        print(f"\n📊 Cost estimation for {instance.name}:")
        cost_breakdown = estimator.calculate_cost_breakdown(config, instance)
        
        print(f"  Total training time: {cost_breakdown['time_breakdown_hours']['total_training_hours']:.1f} hours")
        print(f"  Total cost: ₹{cost_breakdown['cost_breakdown_inr']['total_cost']:,.2f}")
        print(f"  Cost per candidate: ₹{cost_breakdown['efficiency_metrics']['cost_per_candidate']:,.2f}")
        print(f"  Training days: {cost_breakdown['efficiency_metrics']['total_training_days']:.1f}")

def demo_provider_comparison():
    """Demonstrate provider comparison"""
    print("\n🔄 === Provider Comparison Demo ===")
    
    gpu_db = GPUCostDatabase()
    estimator = NASCostEstimator(gpu_db)
    
    # Configuration for comparison
    config = NASTrainingConfig(
        search_epochs=25,
        architecture_candidates=300,
        mixed_precision=True,
        spot_instances=True
    )
    
    # Compare providers
    comparison_df = estimator.compare_providers(config, max_budget_inr=50000)
    
    if not comparison_df.empty:
        print("📊 Top 5 most cost-effective options:")
        top_5 = comparison_df.head()
        
        for idx, row in top_5.iterrows():
            print(f"\n{idx+1}. {row['Provider']} - {row['Instance']}")
            print(f"   Total Cost: ₹{row['Total_Cost_INR']:,.2f}")
            print(f"   Training Days: {row['Training_Days']:.1f}")
            print(f"   Indian Provider: {'✅' if row['Indian_Provider'] else '❌'}")
    else:
        print("❌ No instances found within budget")

def demo_budget_optimization():
    """Demonstrate budget optimization"""
    print("\n🎯 === Budget Optimization Demo ===")
    
    gpu_db = GPUCostDatabase()
    estimator = NASCostEstimator(gpu_db)
    
    # Base configuration
    config = NASTrainingConfig(
        search_epochs=40,
        architecture_candidates=800,
        dataset_size=1000000
    )
    
    # Optimize for different budgets
    budgets = [25000, 50000, 100000]  # ₹25k, ₹50k, ₹100k
    
    for budget in budgets:
        print(f"\n💸 Optimizing for budget: ₹{budget:,}")
        
        optimization_result = estimator.optimize_configuration(
            config, 
            target_budget_inr=budget,
            preferred_providers=[CloudProvider.JIO_CLOUD, CloudProvider.TATA_CLOUD, CloudProvider.AWS]
        )
        
        if optimization_result['optimized_config']:
            instance = optimization_result['recommended_instance']
            cost = optimization_result['cost_breakdown']['cost_breakdown_inr']['total_cost']
            days = optimization_result['cost_breakdown']['efficiency_metrics']['total_training_days']
            
            print(f"  ✅ Optimal solution found:")
            print(f"     Provider: {instance.provider.value}")
            print(f"     Instance: {instance.name}")
            print(f"     Cost: ₹{cost:,.2f} ({cost/budget*100:.1f}% of budget)")
            print(f"     Training time: {days:.1f} days")
            print(f"     Spot instances: {optimization_result['optimized_config'].spot_instances}")
        else:
            min_budget = optimization_result.get('minimum_budget_required')
            print(f"  ❌ No solution within budget")
            if min_budget:
                print(f"     Minimum budget required: ₹{min_budget:,.2f}")

def demo_indian_vs_global_providers():
    """Compare Indian vs Global cloud providers"""
    print("\n🇮🇳 === Indian vs Global Providers Demo ===")
    
    gpu_db = GPUCostDatabase()
    estimator = NASCostEstimator(gpu_db)
    
    config = NASTrainingConfig(
        search_epochs=30,
        architecture_candidates=500,
        spot_instances=True,
        mixed_precision=True
    )
    
    # Get comparison data
    comparison_df = estimator.compare_providers(config)
    
    if not comparison_df.empty:
        indian_providers = comparison_df[comparison_df['Indian_Provider']]
        global_providers = comparison_df[~comparison_df['Indian_Provider']]
        
        print("📊 Summary Comparison:")
        print(f"\nIndian Providers:")
        print(f"  Average cost: ₹{indian_providers['Total_Cost_INR'].mean():,.2f}")
        print(f"  Average training days: {indian_providers['Training_Days'].mean():.1f}")
        print(f"  Number of options: {len(indian_providers)}")
        
        print(f"\nGlobal Providers:")
        print(f"  Average cost: ₹{global_providers['Total_Cost_INR'].mean():,.2f}")
        print(f"  Average training days: {global_providers['Training_Days'].mean():.1f}")
        print(f"  Number of options: {len(global_providers)}")
        
        # Best option from each category
        if not indian_providers.empty:
            best_indian = indian_providers.loc[indian_providers['Total_Cost_INR'].idxmin()]
            print(f"\n🏆 Best Indian Option: {best_indian['Provider']} - {best_indian['Instance']}")
            print(f"   Cost: ₹{best_indian['Total_Cost_INR']:,.2f}")
        
        if not global_providers.empty:
            best_global = global_providers.loc[global_providers['Total_Cost_INR'].idxmin()]
            print(f"\n🌍 Best Global Option: {best_global['Provider']} - {best_global['Instance']}")
            print(f"   Cost: ₹{best_global['Total_Cost_INR']:,.2f}")

if __name__ == "__main__":
    print("🇮🇳 GPU Cost Calculator for Neural Architecture Search")
    print("Cost optimization for Indian and global cloud providers")
    
    # Run all demonstrations
    demo_cost_estimation()
    demo_provider_comparison()
    demo_budget_optimization()
    demo_indian_vs_global_providers()
    
    print("\n🎉 GPU cost calculation demonstrations completed!")
    print("💡 Use this tool to optimize NAS training costs across different cloud providers")