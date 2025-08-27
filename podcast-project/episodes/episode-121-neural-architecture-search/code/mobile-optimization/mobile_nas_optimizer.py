"""
Mobile-Optimized Neural Architecture Search
Indian mobile devices के लिए optimized NAS - efficient architectures
Jio Phone, budget Android phones पर चलने वाले models के लिए
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
import time
import json
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import psutil
from collections import OrderedDict

# Hindi comments के साथ logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MobileConstraints:
    """Mobile device constraints for Indian market"""
    # Hardware constraints
    max_params_mb: float = 5.0      # Maximum model size in MB
    max_flops_m: float = 100.0      # Maximum FLOPs in millions
    max_latency_ms: float = 50.0    # Maximum inference latency in ms
    max_memory_mb: float = 128.0    # Maximum runtime memory in MB
    
    # Target devices (Indian mobile market)
    target_devices: List[str] = None
    
    def __post_init__(self):
        if self.target_devices is None:
            self.target_devices = [
                'jio_phone_next',    # KaiOS based
                'samsung_m12',       # Budget Android
                'redmi_9a',         # Entry level
                'realme_c11',       # Low-end segment
                'oppo_a16k'         # Basic smartphone
            ]

class MobileOperations:
    """
    Mobile-friendly operations for NAS
    Low compute और memory efficient operations
    """
    
    @staticmethod
    def depthwise_conv(C_in: int, kernel_size: int, stride: int, padding: int):
        """Depthwise separable convolution - mobile friendly"""
        return nn.Sequential(
            # Depthwise convolution
            nn.Conv2d(C_in, C_in, kernel_size=kernel_size, stride=stride, 
                     padding=padding, groups=C_in, bias=False),
            nn.BatchNorm2d(C_in),
            nn.ReLU6(inplace=True),  # ReLU6 is mobile optimized
            
            # Pointwise convolution
            nn.Conv2d(C_in, C_in, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(C_in),
            nn.ReLU6(inplace=True)
        )
    
    @staticmethod
    def inverted_residual_block(C_in: int, C_out: int, stride: int, expand_ratio: int = 6):
        """MobileNetV2 style inverted residual block"""
        hidden_dim = int(round(C_in * expand_ratio))
        use_residual = stride == 1 and C_in == C_out
        
        layers = []
        
        # Expand phase
        if expand_ratio != 1:
            layers.extend([
                nn.Conv2d(C_in, hidden_dim, kernel_size=1, bias=False),
                nn.BatchNorm2d(hidden_dim),
                nn.ReLU6(inplace=True)
            ])
        
        # Depthwise phase
        layers.extend([
            nn.Conv2d(hidden_dim, hidden_dim, kernel_size=3, stride=stride,
                     padding=1, groups=hidden_dim, bias=False),
            nn.BatchNorm2d(hidden_dim),
            nn.ReLU6(inplace=True)
        ])
        
        # Project phase
        layers.extend([
            nn.Conv2d(hidden_dim, C_out, kernel_size=1, bias=False),
            nn.BatchNorm2d(C_out)
        ])
        
        conv = nn.Sequential(*layers)
        
        if use_residual:
            return ResidualBlock(conv)
        else:
            return conv
    
    @staticmethod
    def squeeze_excitation(C: int, reduction: int = 4):
        """Squeeze-and-Excitation block for mobile"""
        return nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(C, C // reduction, kernel_size=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(C // reduction, C, kernel_size=1),
            nn.Sigmoid()
        )
    
    @staticmethod
    def shuffle_channel(groups: int = 2):
        """Channel shuffle for ShuffleNet"""
        def shuffle(x):
            batch_size, num_channels, height, width = x.size()
            channels_per_group = num_channels // groups
            
            # Reshape and transpose
            x = x.view(batch_size, groups, channels_per_group, height, width)
            x = torch.transpose(x, 1, 2).contiguous()
            x = x.view(batch_size, -1, height, width)
            
            return x
        return shuffle

class ResidualBlock(nn.Module):
    """Simple residual connection for mobile architectures"""
    
    def __init__(self, conv_block):
        super(ResidualBlock, self).__init__()
        self.conv_block = conv_block
    
    def forward(self, x):
        return x + self.conv_block(x)

class MobileEfficiencyCalculator:
    """
    Mobile efficiency metrics calculator
    Indian smartphone hardware के लिए optimized
    """
    
    def __init__(self, constraints: MobileConstraints):
        self.constraints = constraints
        
        # Device specifications (Indian market devices)
        self.device_specs = {
            'jio_phone_next': {
                'cpu': 'Qualcomm QM215',
                'ram_mb': 512,
                'gpu': 'Adreno 308',
                'os': 'KaiOS 3.0',
                'inference_factor': 0.3  # Slower inference
            },
            'samsung_m12': {
                'cpu': 'Exynos 850',
                'ram_mb': 4096,
                'gpu': 'Mali-G52',
                'os': 'Android 11',
                'inference_factor': 0.8
            },
            'redmi_9a': {
                'cpu': 'Helio G25',
                'ram_mb': 2048,
                'gpu': 'PowerVR GE8320',
                'os': 'Android 10',
                'inference_factor': 0.6
            },
            'realme_c11': {
                'cpu': 'Helio G35',
                'ram_mb': 2048,
                'gpu': 'PowerVR GE8320',
                'os': 'Android 10',
                'inference_factor': 0.7
            },
            'oppo_a16k': {
                'cpu': 'Helio G35',
                'ram_mb': 3072,
                'gpu': 'PowerVR GE8320',
                'os': 'Android 11',
                'inference_factor': 0.75
            }
        }
    
    def calculate_model_size(self, model: nn.Module) -> float:
        """Calculate model size in MB"""
        param_size = 0
        buffer_size = 0
        
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        size_mb = (param_size + buffer_size) / (1024 ** 2)
        return size_mb
    
    def calculate_flops(self, model: nn.Module, input_shape: Tuple[int, int, int, int]) -> float:
        """
        Calculate FLOPs for the model
        Simplified calculation for mobile optimization
        """
        model.eval()
        flops = 0
        
        def flop_count_hook(module, input, output):
            nonlocal flops
            
            if isinstance(module, nn.Conv2d):
                # Conv2d FLOPs calculation
                kernel_dims = module.kernel_size[0] * module.kernel_size[1]
                in_channels = module.in_channels
                out_channels = module.out_channels
                output_dims = output.shape[2] * output.shape[3]
                
                # FLOPs = kernel_dims * in_channels * output_dims * out_channels
                conv_flops = kernel_dims * in_channels * output_dims * out_channels
                if module.groups > 1:
                    conv_flops = conv_flops / module.groups
                
                flops += conv_flops
            
            elif isinstance(module, nn.Linear):
                # Linear layer FLOPs
                flops += module.in_features * module.out_features
        
        # Register hooks
        hooks = []
        for module in model.modules():
            if isinstance(module, (nn.Conv2d, nn.Linear)):
                hooks.append(module.register_forward_hook(flop_count_hook))
        
        # Forward pass to calculate FLOPs
        with torch.no_grad():
            dummy_input = torch.randn(input_shape)
            model(dummy_input)
        
        # Remove hooks
        for hook in hooks:
            hook.remove()
        
        return flops / 1e6  # Return in millions
    
    def estimate_latency(self, model: nn.Module, device: str, 
                        input_shape: Tuple[int, int, int, int], 
                        num_runs: int = 100) -> Dict[str, float]:
        """
        Estimate inference latency on target mobile device
        """
        model.eval()
        
        # Get device specifications
        device_spec = self.device_specs.get(device, self.device_specs['redmi_9a'])
        inference_factor = device_spec['inference_factor']
        
        # Measure actual inference time (on current hardware)
        dummy_input = torch.randn(input_shape)
        
        # Warmup
        with torch.no_grad():
            for _ in range(10):
                _ = model(dummy_input)
        
        # Measure latency
        start_time = time.time()
        with torch.no_grad():
            for _ in range(num_runs):
                _ = model(dummy_input)
        end_time = time.time()
        
        avg_latency_ms = ((end_time - start_time) / num_runs) * 1000
        
        # Adjust for target device
        estimated_latency_ms = avg_latency_ms / inference_factor
        
        return {
            'measured_latency_ms': avg_latency_ms,
            'estimated_latency_ms': estimated_latency_ms,
            'target_device': device,
            'device_specs': device_spec
        }
    
    def calculate_memory_usage(self, model: nn.Module, 
                             input_shape: Tuple[int, int, int, int]) -> Dict[str, float]:
        """Calculate runtime memory usage"""
        model.eval()
        
        # Measure memory before
        process = psutil.Process()
        memory_before = process.memory_info().rss / (1024 ** 2)  # MB
        
        # Forward pass
        dummy_input = torch.randn(input_shape)
        with torch.no_grad():
            output = model(dummy_input)
        
        # Measure memory after
        memory_after = process.memory_info().rss / (1024 ** 2)  # MB
        
        # Calculate memory usage
        inference_memory = memory_after - memory_before
        
        # Estimate peak memory (including gradients for training)
        peak_memory = inference_memory * 2.5  # Rough estimate
        
        return {
            'inference_memory_mb': inference_memory,
            'peak_memory_mb': peak_memory,
            'model_size_mb': self.calculate_model_size(model)
        }
    
    def evaluate_mobile_efficiency(self, model: nn.Module, 
                                 input_shape: Tuple[int, int, int, int] = (1, 3, 224, 224),
                                 target_device: str = 'redmi_9a') -> Dict[str, Any]:
        """
        Comprehensive mobile efficiency evaluation
        """
        logger.info(f"📱 Evaluating mobile efficiency for {target_device}")
        
        # Calculate all metrics
        model_size_mb = self.calculate_model_size(model)
        flops_m = self.calculate_flops(model, input_shape)
        latency_info = self.estimate_latency(model, target_device, input_shape)
        memory_info = self.calculate_memory_usage(model, input_shape)
        
        # Check constraints
        constraints_met = {
            'size_constraint': model_size_mb <= self.constraints.max_params_mb,
            'flops_constraint': flops_m <= self.constraints.max_flops_m,
            'latency_constraint': latency_info['estimated_latency_ms'] <= self.constraints.max_latency_ms,
            'memory_constraint': memory_info['peak_memory_mb'] <= self.constraints.max_memory_mb
        }
        
        # Calculate efficiency score
        size_score = min(1.0, self.constraints.max_params_mb / max(model_size_mb, 0.1))
        flops_score = min(1.0, self.constraints.max_flops_m / max(flops_m, 0.1))
        latency_score = min(1.0, self.constraints.max_latency_ms / 
                           max(latency_info['estimated_latency_ms'], 1.0))
        memory_score = min(1.0, self.constraints.max_memory_mb / 
                          max(memory_info['peak_memory_mb'], 1.0))
        
        efficiency_score = (size_score + flops_score + latency_score + memory_score) / 4
        
        results = {
            'target_device': target_device,
            'metrics': {
                'model_size_mb': model_size_mb,
                'flops_millions': flops_m,
                'estimated_latency_ms': latency_info['estimated_latency_ms'],
                'peak_memory_mb': memory_info['peak_memory_mb']
            },
            'constraints': {
                'max_size_mb': self.constraints.max_params_mb,
                'max_flops_m': self.constraints.max_flops_m,
                'max_latency_ms': self.constraints.max_latency_ms,
                'max_memory_mb': self.constraints.max_memory_mb
            },
            'constraints_met': constraints_met,
            'scores': {
                'size_score': size_score,
                'flops_score': flops_score,
                'latency_score': latency_score,
                'memory_score': memory_score,
                'efficiency_score': efficiency_score
            },
            'device_specs': latency_info['device_specs']
        }
        
        # Log results
        logger.info(f"📊 Model size: {model_size_mb:.2f} MB (limit: {self.constraints.max_params_mb:.2f} MB)")
        logger.info(f"⚡ FLOPs: {flops_m:.2f} M (limit: {self.constraints.max_flops_m:.2f} M)")
        logger.info(f"⏱️ Latency: {latency_info['estimated_latency_ms']:.2f} ms (limit: {self.constraints.max_latency_ms:.2f} ms)")
        logger.info(f"🧠 Memory: {memory_info['peak_memory_mb']:.2f} MB (limit: {self.constraints.max_memory_mb:.2f} MB)")
        logger.info(f"🎯 Efficiency score: {efficiency_score:.3f}")
        
        all_constraints_met = all(constraints_met.values())
        if all_constraints_met:
            logger.info("✅ All mobile constraints satisfied!")
        else:
            failed_constraints = [k for k, v in constraints_met.items() if not v]
            logger.warning(f"❌ Failed constraints: {failed_constraints}")
        
        return results

class MobileNASSearchSpace:
    """
    Search space optimized for mobile devices
    Efficient operations और architectures के लिए
    """
    
    def __init__(self, constraints: MobileConstraints):
        self.constraints = constraints
        
        # Mobile-optimized operations
        self.operations = [
            'skip_connect',           # Identity connection
            'depthwise_3x3',         # Depthwise separable 3x3
            'depthwise_5x5',         # Depthwise separable 5x5
            'inverted_residual_3',   # Inverted residual, expand=3
            'inverted_residual_6',   # Inverted residual, expand=6
            'squeeze_excite',        # Squeeze-and-excitation
            'avg_pool_3x3',          # Average pooling
            'max_pool_3x3',          # Max pooling
        ]
        
        # Channel configurations (keeping low for mobile)
        self.channel_configs = [16, 24, 32, 48, 64, 96]
        
        # Depth configurations (shallow networks for mobile)
        self.depth_configs = [4, 6, 8, 10, 12]
    
    def create_mobile_operation(self, op_name: str, C: int, stride: int) -> nn.Module:
        """Create mobile-optimized operation"""
        if op_name == 'skip_connect':
            if stride == 1:
                return nn.Identity()
            else:
                return nn.Sequential(
                    nn.AvgPool2d(kernel_size=2, stride=stride),
                    nn.Conv2d(C, C, kernel_size=1, bias=False),
                    nn.BatchNorm2d(C)
                )
        
        elif op_name == 'depthwise_3x3':
            return MobileOperations.depthwise_conv(C, 3, stride, 1)
        
        elif op_name == 'depthwise_5x5':
            return MobileOperations.depthwise_conv(C, 5, stride, 2)
        
        elif op_name == 'inverted_residual_3':
            return MobileOperations.inverted_residual_block(C, C, stride, expand_ratio=3)
        
        elif op_name == 'inverted_residual_6':
            return MobileOperations.inverted_residual_block(C, C, stride, expand_ratio=6)
        
        elif op_name == 'squeeze_excite':
            se_block = MobileOperations.squeeze_excitation(C)
            if stride == 1:
                return nn.Sequential(
                    nn.Identity(),
                    se_block
                )
            else:
                return nn.Sequential(
                    nn.AvgPool2d(kernel_size=2, stride=stride),
                    se_block
                )
        
        elif op_name == 'avg_pool_3x3':
            return nn.AvgPool2d(kernel_size=3, stride=stride, padding=1)
        
        elif op_name == 'max_pool_3x3':
            return nn.MaxPool2d(kernel_size=3, stride=stride, padding=1)
        
        else:
            raise ValueError(f"Unknown operation: {op_name}")

class MobileNASModel(nn.Module):
    """
    Mobile-optimized NAS model
    Indian smartphone market के लिए designed
    """
    
    def __init__(self, num_classes: int = 1000, 
                 constraints: MobileConstraints = None):
        super(MobileNASModel, self).__init__()
        
        if constraints is None:
            constraints = MobileConstraints()
        
        self.constraints = constraints
        self.num_classes = num_classes
        
        # Lightweight stem
        self.stem = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU6(inplace=True)
        )
        
        # Mobile-optimized backbone
        self.features = self._make_mobile_layers()
        
        # Efficient classifier
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Dropout(0.2),
            nn.Conv2d(self.final_channels, num_classes, kernel_size=1),
            nn.Flatten()
        )
        
        # Initialize weights
        self._initialize_weights()
    
    def _make_mobile_layers(self) -> nn.Module:
        """Create mobile-optimized feature extraction layers"""
        layers = []
        
        # Configuration for mobile efficiency
        # (channels, num_blocks, stride)
        configs = [
            (48, 2, 1),   # Stage 1
            (64, 3, 2),   # Stage 2
            (96, 3, 2),   # Stage 3
            (128, 2, 1),  # Stage 4
        ]
        
        current_channels = 32  # From stem
        
        for channels, num_blocks, stride in configs:
            # Transition layer
            layers.append(nn.Sequential(
                nn.Conv2d(current_channels, channels, kernel_size=1, bias=False),
                nn.BatchNorm2d(channels),
                nn.ReLU6(inplace=True)
            ))
            
            # Mobile blocks
            for i in range(num_blocks):
                block_stride = stride if i == 0 else 1
                layers.append(
                    MobileOperations.inverted_residual_block(
                        channels, channels, block_stride, expand_ratio=6
                    )
                )
            
            current_channels = channels
        
        self.final_channels = current_channels
        return nn.Sequential(*layers)
    
    def _initialize_weights(self):
        """Initialize model weights"""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.ones_(m.weight)
                nn.init.zeros_(m.bias)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.zeros_(m.bias)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        x = self.stem(x)
        x = self.features(x)
        x = self.classifier(x)
        return x

# Demonstration functions

def demo_mobile_efficiency_evaluation():
    """Demonstrate mobile efficiency evaluation"""
    print("\n📱 === Mobile Efficiency Evaluation Demo ===")
    
    # Create mobile constraints for Indian devices
    constraints = MobileConstraints(
        max_params_mb=3.0,     # 3MB model size limit
        max_flops_m=80.0,      # 80M FLOPs limit  
        max_latency_ms=40.0,   # 40ms latency limit
        max_memory_mb=100.0    # 100MB memory limit
    )
    
    # Create efficiency calculator
    calculator = MobileEfficiencyCalculator(constraints)
    
    # Create sample model
    model = MobileNASModel(num_classes=100, constraints=constraints)  # 100 product categories
    
    # Evaluate efficiency for different Indian devices
    devices = ['jio_phone_next', 'redmi_9a', 'samsung_m12']
    
    for device in devices:
        print(f"\n📱 Evaluating for {device}:")
        results = calculator.evaluate_mobile_efficiency(model, target_device=device)
        
        print(f"✅ Efficiency Score: {results['scores']['efficiency_score']:.3f}")
        print(f"📊 All constraints met: {all(results['constraints_met'].values())}")

def demo_mobile_operations():
    """Demonstrate mobile-optimized operations"""
    print("\n⚡ === Mobile Operations Demo ===")
    
    # Test different mobile operations
    C = 64  # Number of channels
    input_tensor = torch.randn(1, C, 56, 56)
    
    operations = {
        'Depthwise Conv 3x3': MobileOperations.depthwise_conv(C, 3, 1, 1),
        'Inverted Residual (expand=6)': MobileOperations.inverted_residual_block(C, C, 1, 6),
        'Squeeze-Excitation': MobileOperations.squeeze_excitation(C),
    }
    
    for op_name, operation in operations.items():
        start_time = time.time()
        
        with torch.no_grad():
            output = operation(input_tensor)
        
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # Calculate parameters
        num_params = sum(p.numel() for p in operation.parameters())
        
        print(f"\n{op_name}:")
        print(f"  Parameters: {num_params:,}")
        print(f"  Output shape: {output.shape}")
        print(f"  Latency: {latency_ms:.2f} ms")

def demo_device_comparison():
    """Compare model performance across Indian mobile devices"""
    print("\n🔄 === Device Comparison Demo ===")
    
    # Create model
    model = MobileNASModel(num_classes=50)  # 50 categories for faster demo
    calculator = MobileEfficiencyCalculator(MobileConstraints())
    
    # Compare across different devices
    devices = list(calculator.device_specs.keys())
    comparison_results = {}
    
    for device in devices:
        results = calculator.evaluate_mobile_efficiency(model, target_device=device)
        comparison_results[device] = {
            'efficiency_score': results['scores']['efficiency_score'],
            'latency_ms': results['metrics']['estimated_latency_ms'],
            'constraints_met': all(results['constraints_met'].values())
        }
    
    # Print comparison table
    print("\n📊 Device Comparison Results:")
    print(f"{'Device':<20} {'Efficiency':<12} {'Latency (ms)':<15} {'Constraints Met'}")
    print("-" * 65)
    
    for device, metrics in comparison_results.items():
        print(f"{device:<20} {metrics['efficiency_score']:<12.3f} "
              f"{metrics['latency_ms']:<15.1f} {'✅' if metrics['constraints_met'] else '❌'}")

def demo_architecture_optimization():
    """Demonstrate architecture optimization for mobile constraints"""
    print("\n🏗️ === Architecture Optimization Demo ===")
    
    # Create different model configurations
    configs = [
        {'name': 'Tiny Model', 'channels': 16, 'depth': 4},
        {'name': 'Small Model', 'channels': 32, 'depth': 6},
        {'name': 'Medium Model', 'channels': 48, 'depth': 8},
    ]
    
    constraints = MobileConstraints(max_params_mb=2.0, max_latency_ms=30.0)
    calculator = MobileEfficiencyCalculator(constraints)
    
    print("📱 Testing different architecture configurations:")
    
    for config in configs:
        print(f"\n🔍 {config['name']}:")
        
        # Create model with specific configuration
        # (This is simplified - in practice you'd modify the architecture)
        model = MobileNASModel(num_classes=100)
        
        # Evaluate efficiency
        results = calculator.evaluate_mobile_efficiency(model, target_device='redmi_9a')
        
        print(f"  Size: {results['metrics']['model_size_mb']:.2f} MB")
        print(f"  Latency: {results['metrics']['estimated_latency_ms']:.1f} ms")
        print(f"  Efficiency: {results['scores']['efficiency_score']:.3f}")
        print(f"  Suitable for mobile: {'✅' if all(results['constraints_met'].values()) else '❌'}")

if __name__ == "__main__":
    print("🇮🇳 Mobile-Optimized Neural Architecture Search")
    print("Optimized for Indian smartphone market")
    
    # Run all demonstrations
    demo_mobile_efficiency_evaluation()
    demo_mobile_operations()
    demo_device_comparison()
    demo_architecture_optimization()
    
    print("\n🎉 Mobile NAS demonstrations completed!")
    print("💡 Models optimized for Indian mobile devices and network conditions")