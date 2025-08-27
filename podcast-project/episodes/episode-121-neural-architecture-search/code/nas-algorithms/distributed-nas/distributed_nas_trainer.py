"""
Distributed Neural Architecture Search Implementation
Multiple GPUs और cloud instances पर NAS algorithms को distribute करने के लिए
Indian companies जैसे Flipkart, Zomato के large-scale model training के लिए
"""

import torch
import torch.distributed as dist
import torch.multiprocessing as mp
from torch.nn.parallel import DistributedDataParallel as DDP
import torch.backends.cudnn as cudnn
import numpy as np
import logging
import time
import os
import json
import argparse
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime, timedelta
import psutil
import GPUtil
import threading
from dataclasses import dataclass
from pathlib import Path

# Import DARTS model from previous implementation
import sys
sys.path.append('../darts')
from darts_model import Network, DARTSTrainer

# Hindi comments के साथ logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(rank)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DistributedNASConfig:
    """Configuration for distributed NAS training"""
    # Training parameters
    epochs: int = 50
    batch_size: int = 32
    learning_rate_weights: float = 0.025
    learning_rate_arch: float = 3e-4
    momentum: float = 0.9
    weight_decay: float = 3e-4
    
    # Model parameters
    init_channels: int = 16
    layers: int = 8
    num_classes: int = 1000
    
    # Distributed parameters
    world_size: int = 4  # Number of GPUs/processes
    backend: str = 'nccl'  # Communication backend
    
    # Indian cloud provider settings
    cloud_provider: str = 'jio_cloud'  # jio_cloud, tata_cloud, airtel_cloud
    instance_type: str = 'gpu.2xlarge'
    cost_per_hour_inr: float = 150.0  # Cost in INR per hour
    
    # Monitoring
    log_interval: int = 10
    save_interval: int = 5
    
    # Data paths
    data_path: str = '/data/indian_ecommerce_images'
    checkpoint_path: str = '/checkpoints/distributed_nas'

class GPUMonitor:
    """
    GPU usage monitoring for Indian cloud providers
    Cost और performance monitoring के लिए
    """
    
    def __init__(self, config: DistributedNASConfig, rank: int):
        self.config = config
        self.rank = rank
        self.monitoring = True
        self.stats = {
            'gpu_utilization': [],
            'gpu_memory': [],
            'gpu_temperature': [],
            'cpu_usage': [],
            'memory_usage': [],
            'timestamps': []
        }
        
    def start_monitoring(self):
        """Start background monitoring thread"""
        self.monitoring_thread = threading.Thread(target=self._monitor_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        logger.info(f"🔍 GPU monitoring started on rank {self.rank}")
    
    def stop_monitoring(self):
        """Stop monitoring and return stats"""
        self.monitoring = False
        if hasattr(self, 'monitoring_thread'):
            self.monitoring_thread.join()
        logger.info(f"⏹️ GPU monitoring stopped on rank {self.rank}")
        return self.stats
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # GPU stats
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Primary GPU
                    self.stats['gpu_utilization'].append(gpu.load * 100)
                    self.stats['gpu_memory'].append(gpu.memoryUtil * 100)
                    self.stats['gpu_temperature'].append(gpu.temperature)
                
                # CPU और RAM stats
                self.stats['cpu_usage'].append(psutil.cpu_percent())
                self.stats['memory_usage'].append(psutil.virtual_memory().percent)
                self.stats['timestamps'].append(datetime.now().isoformat())
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.warning(f"⚠️ Monitoring error: {e}")
                time.sleep(10)

class CostCalculator:
    """
    Indian cloud provider cost calculation
    GPU hours और training cost का accurate calculation
    """
    
    def __init__(self, config: DistributedNASConfig):
        self.config = config
        self.start_time = None
        self.total_cost_inr = 0.0
        
        # Indian cloud provider pricing (sample rates)
        self.pricing = {
            'jio_cloud': {
                'gpu.xlarge': 120.0,   # ₹120/hour
                'gpu.2xlarge': 150.0,  # ₹150/hour
                'gpu.4xlarge': 280.0,  # ₹280/hour
            },
            'tata_cloud': {
                'gpu.xlarge': 115.0,
                'gpu.2xlarge': 145.0,
                'gpu.4xlarge': 270.0,
            },
            'airtel_cloud': {
                'gpu.xlarge': 125.0,
                'gpu.2xlarge': 155.0,
                'gpu.4xlarge': 290.0,
            }
        }
    
    def start_training(self):
        """Training शुरू करते समय cost tracking start करें"""
        self.start_time = datetime.now()
        cost_per_hour = self.pricing[self.config.cloud_provider][self.config.instance_type]
        logger.info(f"💰 Cost tracking started - Provider: {self.config.cloud_provider}")
        logger.info(f"💸 Rate: ₹{cost_per_hour}/hour for {self.config.instance_type}")
        logger.info(f"🌐 World size: {self.config.world_size} instances")
    
    def calculate_current_cost(self) -> Tuple[float, float]:
        """Current training cost calculate करें"""
        if not self.start_time:
            return 0.0, 0.0
        
        elapsed_time = datetime.now() - self.start_time
        hours_elapsed = elapsed_time.total_seconds() / 3600
        
        cost_per_hour = self.pricing[self.config.cloud_provider][self.config.instance_type]
        total_cost = cost_per_hour * hours_elapsed * self.config.world_size
        
        return hours_elapsed, total_cost
    
    def estimate_total_cost(self, current_epoch: int, total_epochs: int) -> Dict:
        """Total training cost का estimate निकालें"""
        if not self.start_time or current_epoch == 0:
            return {}
        
        elapsed_time = datetime.now() - self.start_time
        time_per_epoch = elapsed_time.total_seconds() / current_epoch
        
        remaining_epochs = total_epochs - current_epoch
        estimated_remaining_time = remaining_epochs * time_per_epoch / 3600  # hours
        
        hours_elapsed, current_cost = self.calculate_current_cost()
        cost_per_hour = self.pricing[self.config.cloud_provider][self.config.instance_type]
        estimated_total_cost = current_cost + (estimated_remaining_time * cost_per_hour * self.config.world_size)
        
        return {
            'current_epoch': current_epoch,
            'total_epochs': total_epochs,
            'hours_elapsed': hours_elapsed,
            'current_cost_inr': current_cost,
            'estimated_total_cost_inr': estimated_total_cost,
            'estimated_remaining_hours': estimated_remaining_time,
            'cost_per_hour_per_instance': cost_per_hour,
            'total_instances': self.config.world_size
        }

class DistributedNASTrainer:
    """
    Multi-GPU distributed DARTS trainer
    Indian cloud infrastructure पर optimized
    """
    
    def __init__(self, config: DistributedNASConfig, rank: int, world_size: int):
        self.config = config
        self.rank = rank
        self.world_size = world_size
        self.device = torch.device(f'cuda:{rank}')
        
        # Cost और monitoring setup
        self.cost_calculator = CostCalculator(config) if rank == 0 else None
        self.gpu_monitor = GPUMonitor(config, rank)
        
        # Model initialization
        self.model = None
        self.criterion = torch.nn.CrossEntropyLoss()
        
        logger.info(f"🚀 Distributed NAS Trainer initialized - Rank: {rank}/{world_size}")
    
    def setup_distributed(self, master_addr: str = 'localhost', master_port: str = '12355'):
        """Distributed training setup"""
        os.environ['MASTER_ADDR'] = master_addr
        os.environ['MASTER_PORT'] = master_port
        
        # Initialize distributed process group
        dist.init_process_group(
            backend=self.config.backend,
            rank=self.rank,
            world_size=self.world_size
        )
        
        # Set device for this process
        torch.cuda.set_device(self.rank)
        
        logger.info(f"🌐 Distributed setup completed - Rank: {self.rank}")
    
    def create_model(self):
        """Create DARTS model with DDP wrapper"""
        # Create base model
        self.model = Network(
            C=self.config.init_channels,
            num_classes=self.config.num_classes,
            layers=self.config.layers,
            criterion=self.criterion
        ).to(self.device)
        
        # Wrap with DistributedDataParallel
        self.model = DDP(self.model, device_ids=[self.rank], find_unused_parameters=True)
        
        # Create optimizers
        self.w_optimizer = torch.optim.SGD(
            self.model.parameters(),
            lr=self.config.learning_rate_weights,
            momentum=self.config.momentum,
            weight_decay=self.config.weight_decay
        )
        
        self.arch_optimizer = torch.optim.Adam(
            self.model.module.arch_parameters(),
            lr=self.config.learning_rate_arch,
            betas=(0.5, 0.999),
            weight_decay=1e-3
        )
        
        # Learning rate scheduler
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.w_optimizer, T_max=self.config.epochs, eta_min=0.001
        )
        
        logger.info(f"🏗️ Model created and wrapped with DDP - Rank: {self.rank}")
        logger.info(f"📊 Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def create_dataloaders(self):
        """Create distributed data loaders"""
        # This is a placeholder - in real implementation, you would load actual data
        # For demonstration, we'll create synthetic data
        
        from torch.utils.data import Dataset, DataLoader, DistributedSampler
        
        class SyntheticDataset(Dataset):
            def __init__(self, size: int = 10000):
                self.size = size
                
            def __len__(self):
                return self.size
            
            def __getitem__(self, idx):
                # Generate synthetic Indian e-commerce product images
                image = torch.randn(3, 224, 224)  # RGB image
                label = torch.randint(0, self.config.num_classes, (1,)).item()
                return image, label
        
        # Create datasets
        train_dataset = SyntheticDataset(size=50000)
        val_dataset = SyntheticDataset(size=10000)
        
        # Create distributed samplers
        train_sampler = DistributedSampler(
            train_dataset, 
            num_replicas=self.world_size, 
            rank=self.rank,
            shuffle=True
        )
        
        val_sampler = DistributedSampler(
            val_dataset,
            num_replicas=self.world_size,
            rank=self.rank,
            shuffle=False
        )
        
        # Create data loaders
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            sampler=train_sampler,
            num_workers=4,
            pin_memory=True
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            sampler=val_sampler,
            num_workers=4,
            pin_memory=True
        )
        
        logger.info(f"📚 Data loaders created - Rank: {self.rank}")
        logger.info(f"🔢 Train batches: {len(self.train_loader)}, Val batches: {len(self.val_loader)}")
    
    def train_epoch(self, epoch: int) -> Dict[str, float]:
        """Train one epoch with distributed setup"""
        self.model.train()
        
        # Set epoch for distributed sampler
        if hasattr(self.train_loader.sampler, 'set_epoch'):
            self.train_loader.sampler.set_epoch(epoch)
        
        epoch_stats = {
            'train_loss': 0.0,
            'train_acc': 0.0,
            'arch_loss': 0.0,
            'gpu_memory_mb': 0.0
        }
        
        num_batches = len(self.train_loader)
        
        # Get validation iterator for architecture optimization
        val_iter = iter(self.val_loader)
        
        for batch_idx, (train_data, train_target) in enumerate(self.train_loader):
            train_data, train_target = train_data.to(self.device), train_target.to(self.device)
            
            # Get validation batch for architecture update
            try:
                val_data, val_target = next(val_iter)
            except StopIteration:
                val_iter = iter(self.val_loader)
                val_data, val_target = next(val_iter)
            
            val_data, val_target = val_data.to(self.device), val_target.to(self.device)
            
            # Update architecture parameters
            self.arch_optimizer.zero_grad()
            logits = self.model(val_data)
            arch_loss = self.criterion(logits, val_target)
            arch_loss.backward()
            self.arch_optimizer.step()
            
            # Update network weights
            self.w_optimizer.zero_grad()
            logits = self.model(train_data)
            train_loss = self.criterion(logits, train_target)
            train_loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), 5.0)
            self.w_optimizer.step()
            
            # Calculate accuracy
            pred = logits.argmax(dim=1)
            acc = (pred == train_target).float().mean()
            
            # Update statistics
            epoch_stats['train_loss'] += train_loss.item()
            epoch_stats['train_acc'] += acc.item()
            epoch_stats['arch_loss'] += arch_loss.item()
            epoch_stats['gpu_memory_mb'] = torch.cuda.max_memory_allocated(self.device) / 1024 / 1024
            
            # Log progress
            if batch_idx % self.config.log_interval == 0 and self.rank == 0:
                logger.info(f"Epoch {epoch}, Batch {batch_idx}/{num_batches}: "
                           f"Train Loss={train_loss.item():.4f}, "
                           f"Arch Loss={arch_loss.item():.4f}, "
                           f"Acc={acc.item():.4f}")
                
                # Cost update
                if self.cost_calculator:
                    hours, cost = self.cost_calculator.calculate_current_cost()
                    logger.info(f"💰 Training cost so far: ₹{cost:.2f} ({hours:.2f} hours)")
        
        # Average statistics across all batches
        for key in epoch_stats:
            if key != 'gpu_memory_mb':
                epoch_stats[key] /= num_batches
        
        # Update learning rate
        self.scheduler.step()
        
        # Synchronize across all processes
        if dist.is_initialized():
            for key in ['train_loss', 'train_acc', 'arch_loss']:
                tensor = torch.tensor(epoch_stats[key]).to(self.device)
                dist.all_reduce(tensor, op=dist.ReduceOp.SUM)
                epoch_stats[key] = tensor.item() / self.world_size
        
        return epoch_stats
    
    def validate(self) -> float:
        """Validate current model"""
        self.model.eval()
        val_loss = 0.0
        val_acc = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for val_data, val_target in self.val_loader:
                val_data, val_target = val_data.to(self.device), val_target.to(self.device)
                
                logits = self.model(val_data)
                loss = self.criterion(logits, val_target)
                
                pred = logits.argmax(dim=1)
                acc = (pred == val_target).float().mean()
                
                val_loss += loss.item()
                val_acc += acc.item()
                num_batches += 1
        
        val_loss /= num_batches
        val_acc /= num_batches
        
        # Synchronize validation metrics
        if dist.is_initialized():
            loss_tensor = torch.tensor(val_loss).to(self.device)
            acc_tensor = torch.tensor(val_acc).to(self.device)
            
            dist.all_reduce(loss_tensor, op=dist.ReduceOp.SUM)
            dist.all_reduce(acc_tensor, op=dist.ReduceOp.SUM)
            
            val_loss = loss_tensor.item() / self.world_size
            val_acc = acc_tensor.item() / self.world_size
        
        return val_loss, val_acc
    
    def save_checkpoint(self, epoch: int, is_best: bool = False):
        """Save training checkpoint"""
        if self.rank == 0:  # Only save from rank 0
            checkpoint = {
                'epoch': epoch,
                'model_state_dict': self.model.module.state_dict(),
                'w_optimizer_state_dict': self.w_optimizer.state_dict(),
                'arch_optimizer_state_dict': self.arch_optimizer.state_dict(),
                'scheduler_state_dict': self.scheduler.state_dict(),
                'config': self.config,
                'genotype': self.model.module.genotype(),
            }
            
            # Create checkpoint directory
            checkpoint_dir = Path(self.config.checkpoint_path)
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            
            # Save checkpoint
            checkpoint_path = checkpoint_dir / f'checkpoint_epoch_{epoch}.pth'
            torch.save(checkpoint, checkpoint_path)
            
            if is_best:
                best_path = checkpoint_dir / 'best_model.pth'
                torch.save(checkpoint, best_path)
                logger.info(f"🏆 Best model saved at epoch {epoch}")
            
            logger.info(f"💾 Checkpoint saved: {checkpoint_path}")
    
    def train(self):
        """Main training loop"""
        if self.rank == 0 and self.cost_calculator:
            self.cost_calculator.start_training()
        
        # Start monitoring
        self.gpu_monitor.start_monitoring()
        
        best_val_loss = float('inf')
        training_stats = []
        
        logger.info(f"🏃‍♂️ Starting distributed NAS training for {self.config.epochs} epochs")
        
        for epoch in range(self.config.epochs):
            epoch_start_time = time.time()
            
            # Train one epoch
            train_stats = self.train_epoch(epoch)
            
            # Validate
            val_loss, val_acc = self.validate()
            
            epoch_time = time.time() - epoch_start_time
            
            # Log epoch results (only rank 0)
            if self.rank == 0:
                logger.info(f"📊 Epoch {epoch} completed in {epoch_time:.2f}s")
                logger.info(f"🎯 Train Loss: {train_stats['train_loss']:.4f}, "
                           f"Train Acc: {train_stats['train_acc']:.4f}")
                logger.info(f"✅ Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
                logger.info(f"🧠 GPU Memory: {train_stats['gpu_memory_mb']:.1f} MB")
                
                # Cost estimation
                if self.cost_calculator:
                    cost_info = self.cost_calculator.estimate_total_cost(epoch + 1, self.config.epochs)
                    if cost_info:
                        logger.info(f"💰 Current cost: ₹{cost_info['current_cost_inr']:.2f}")
                        logger.info(f"📈 Estimated total cost: ₹{cost_info['estimated_total_cost_inr']:.2f}")
                
                # Save current architecture
                current_genotype = self.model.module.genotype()
                logger.info(f"🧬 Current architecture: {current_genotype}")
                
                # Track training stats
                training_stats.append({
                    'epoch': epoch,
                    'train_loss': train_stats['train_loss'],
                    'train_acc': train_stats['train_acc'],
                    'val_loss': val_loss,
                    'val_acc': val_acc,
                    'epoch_time': epoch_time,
                    'genotype': str(current_genotype)
                })
            
            # Save checkpoint
            is_best = val_loss < best_val_loss
            if is_best:
                best_val_loss = val_loss
            
            if epoch % self.config.save_interval == 0 or is_best:
                self.save_checkpoint(epoch, is_best)
        
        # Stop monitoring
        monitoring_stats = self.gpu_monitor.stop_monitoring()
        
        # Final results (only rank 0)
        if self.rank == 0:
            logger.info("🎉 Distributed NAS training completed!")
            
            # Final cost calculation
            if self.cost_calculator:
                hours, total_cost = self.cost_calculator.calculate_current_cost()
                logger.info(f"💸 Total training cost: ₹{total_cost:.2f} ({hours:.2f} hours)")
                logger.info(f"🌐 Total instances used: {self.config.world_size}")
                logger.info(f"☁️ Cloud provider: {self.config.cloud_provider}")
            
            # Best architecture
            best_genotype = self.model.module.genotype()
            logger.info(f"🏆 Final best architecture: {best_genotype}")
            
            # Save final training report
            self._save_training_report(training_stats, monitoring_stats, total_cost if self.cost_calculator else 0)
    
    def _save_training_report(self, training_stats: List[Dict], 
                            monitoring_stats: Dict, total_cost: float):
        """Save comprehensive training report"""
        report = {
            'config': {
                'epochs': self.config.epochs,
                'world_size': self.config.world_size,
                'cloud_provider': self.config.cloud_provider,
                'instance_type': self.config.instance_type,
            },
            'final_results': {
                'best_val_loss': min(stats['val_loss'] for stats in training_stats),
                'best_val_acc': max(stats['val_acc'] for stats in training_stats),
                'total_cost_inr': total_cost,
                'training_time_hours': sum(stats['epoch_time'] for stats in training_stats) / 3600,
            },
            'training_history': training_stats,
            'monitoring': monitoring_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        report_path = Path(self.config.checkpoint_path) / 'training_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Training report saved: {report_path}")
    
    def cleanup(self):
        """Cleanup distributed training"""
        if dist.is_initialized():
            dist.destroy_process_group()
        logger.info(f"🧹 Cleanup completed - Rank: {self.rank}")

def run_distributed_nas(rank: int, world_size: int, config: DistributedNASConfig, 
                       master_addr: str = 'localhost', master_port: str = '12355'):
    """
    Run distributed NAS training process
    
    Args:
        rank: Process rank
        world_size: Total number of processes
        config: Training configuration
        master_addr: Master node address
        master_port: Master node port
    """
    try:
        # Create trainer
        trainer = DistributedNASTrainer(config, rank, world_size)
        
        # Setup distributed training
        trainer.setup_distributed(master_addr, master_port)
        
        # Create model and data loaders
        trainer.create_model()
        trainer.create_dataloaders()
        
        # Start training
        trainer.train()
        
        # Cleanup
        trainer.cleanup()
        
    except Exception as e:
        logger.error(f"❌ Training failed on rank {rank}: {e}")
        raise

def main():
    """Main function for distributed NAS training"""
    parser = argparse.ArgumentParser(description='Distributed Neural Architecture Search')
    parser.add_argument('--epochs', type=int, default=50, help='Number of training epochs')
    parser.add_argument('--batch-size', type=int, default=32, help='Batch size per GPU')
    parser.add_argument('--world-size', type=int, default=4, help='Number of GPUs/processes')
    parser.add_argument('--cloud-provider', type=str, default='jio_cloud', 
                       choices=['jio_cloud', 'tata_cloud', 'airtel_cloud'],
                       help='Indian cloud provider')
    parser.add_argument('--instance-type', type=str, default='gpu.2xlarge',
                       help='Instance type')
    parser.add_argument('--master-addr', type=str, default='localhost',
                       help='Master node address')
    parser.add_argument('--master-port', type=str, default='12355',
                       help='Master node port')
    
    args = parser.parse_args()
    
    # Create configuration
    config = DistributedNASConfig(
        epochs=args.epochs,
        batch_size=args.batch_size,
        world_size=args.world_size,
        cloud_provider=args.cloud_provider,
        instance_type=args.instance_type
    )
    
    logger.info("🇮🇳 Starting Distributed Neural Architecture Search")
    logger.info(f"🌐 World size: {config.world_size}")
    logger.info(f"☁️ Cloud provider: {config.cloud_provider}")
    logger.info(f"💻 Instance type: {config.instance_type}")
    
    # Launch distributed training
    if torch.cuda.is_available() and torch.cuda.device_count() >= config.world_size:
        # Multi-GPU single machine
        mp.spawn(
            run_distributed_nas,
            args=(config.world_size, config, args.master_addr, args.master_port),
            nprocs=config.world_size,
            join=True
        )
    else:
        logger.error("❌ Insufficient GPUs available for distributed training")
        logger.info(f"Available GPUs: {torch.cuda.device_count()}")
        logger.info(f"Required GPUs: {config.world_size}")

if __name__ == "__main__":
    main()