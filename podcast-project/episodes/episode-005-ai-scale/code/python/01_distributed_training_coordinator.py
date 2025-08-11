#!/usr/bin/env python3
"""
Distributed Training Coordinator for AI at Scale
Episode 5: Code Example 1

Production-ready distributed training system for Indian multilingual models
Supporting Hindi, Tamil, Bengali, and English training at scale

Author: Code Developer Agent
Context: Indian AI/ML production systems
"""

import torch
import torch.distributed as dist
import torch.multiprocessing as mp
import torch.nn as nn
import torch.optim as optim
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.utils.data import DataLoader, DistributedSampler
import os
import json
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from transformers import AutoTokenizer, AutoModel
import psutil
import GPUtil

# हिंदी में logging setup - Production में ये सब clear होना चाहिए
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('distributed_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """
    Training configuration for Indian multilingual models
    Optimized for Indian cloud infrastructure costs
    """
    model_name: str = "ai4bharat/indic-bert"  # Indian multilingual model
    batch_size: int = 32  # Per GPU batch size
    learning_rate: float = 2e-5
    num_epochs: int = 3
    max_seq_length: int = 512
    gradient_accumulation_steps: int = 4
    warmup_steps: int = 1000
    save_steps: int = 500
    eval_steps: int = 250
    languages: List[str] = None  # Hindi, Tamil, Bengali, English
    output_dir: str = "./models/indic_multilingual"
    
    def __post_init__(self):
        if self.languages is None:
            self.languages = ["hi", "ta", "bn", "en"]  # Indian languages

class IndianMultilingualDataset(torch.utils.data.Dataset):
    """
    Dataset class for Indian multilingual training
    Supports code-mixing common in Indian languages
    """
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Indian language specific preprocessing
        logger.info(f"Dataset initialized with {len(texts)} samples")
        logger.info(f"Languages detected: {self._detect_languages()}")
    
    def _detect_languages(self) -> Dict[str, int]:
        """Detect language distribution in dataset"""
        lang_counts = {"hindi": 0, "english": 0, "code_mixed": 0}
        
        for text in self.texts[:100]:  # Sample detection
            if any(ord(char) > 2304 and ord(char) < 2431 for char in text):  # Devanagari
                if any(ord(char) < 128 for char in text):  # Mixed with English
                    lang_counts["code_mixed"] += 1
                else:
                    lang_counts["hindi"] += 1
            else:
                lang_counts["english"] += 1
        
        return lang_counts
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenize with special handling for Indian languages
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

class ResourceMonitor:
    """
    Monitor GPU and system resources during distributed training
    Critical for cost optimization in Indian cloud providers
    """
    
    def __init__(self, rank: int):
        self.rank = rank
        self.start_time = time.time()
        self.metrics = []
    
    def log_resources(self, step: int):
        """Log current resource usage"""
        try:
            # GPU metrics
            gpus = GPUtil.getGPUs()
            gpu_usage = gpus[self.rank] if self.rank < len(gpus) else None
            
            # System metrics
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            metrics = {
                'step': step,
                'rank': self.rank,
                'timestamp': time.time(),
                'gpu_usage': gpu_usage.load * 100 if gpu_usage else 0,
                'gpu_memory': gpu_usage.memoryUsed if gpu_usage else 0,
                'cpu_usage': cpu_usage,
                'ram_usage': memory.percent,
                'elapsed_time': time.time() - self.start_time
            }
            
            self.metrics.append(metrics)
            
            if step % 100 == 0:  # Log every 100 steps
                logger.info(f"Rank {self.rank} - GPU: {metrics['gpu_usage']:.1f}%, "
                          f"RAM: {metrics['ram_usage']:.1f}%, "
                          f"Time: {metrics['elapsed_time']:.1f}s")
                
        except Exception as e:
            logger.warning(f"Resource monitoring failed: {e}")
    
    def estimate_cost(self, hourly_rate_inr: float = 50.0) -> float:
        """
        Estimate training cost in INR
        Based on average Indian cloud provider rates
        """
        elapsed_hours = (time.time() - self.start_time) / 3600
        total_cost = elapsed_hours * hourly_rate_inr
        
        logger.info(f"Training cost estimate: ₹{total_cost:.2f} "
                   f"({elapsed_hours:.2f} hours @ ₹{hourly_rate_inr}/hour)")
        
        return total_cost

class DistributedTrainingCoordinator:
    """
    Main coordinator for distributed training
    Optimized for Indian infrastructure and cost constraints
    """
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.train_loader = None
        self.val_loader = None
        self.optimizer = None
        self.scheduler = None
        self.resource_monitor = None
        
    def setup_process_group(self, rank: int, world_size: int):
        """Initialize distributed process group"""
        os.environ['MASTER_ADDR'] = '127.0.0.1'
        os.environ['MASTER_PORT'] = '12355'
        
        # Initialize process group for distributed training
        dist.init_process_group("nccl", rank=rank, world_size=world_size)
        torch.cuda.set_device(rank)
        
        logger.info(f"Process group initialized - Rank: {rank}, World size: {world_size}")
    
    def cleanup(self):
        """Clean up distributed training"""
        dist.destroy_process_group()
    
    def load_model_and_tokenizer(self):
        """Load Indian multilingual model and tokenizer"""
        logger.info(f"Loading model: {self.config.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModel.from_pretrained(self.config.model_name)
        
        # Add classification head for downstream task
        self.model.classifier = nn.Linear(self.model.config.hidden_size, 3)  # 3-class sentiment
        
        logger.info(f"Model loaded with {sum(p.numel() for p in self.model.parameters())} parameters")
    
    def create_dataloaders(self, train_texts: List[str], train_labels: List[int],
                          val_texts: List[str], val_labels: List[int], 
                          rank: int, world_size: int):
        """Create distributed data loaders"""
        
        # Create datasets
        train_dataset = IndianMultilingualDataset(
            train_texts, train_labels, self.tokenizer, self.config.max_seq_length
        )
        val_dataset = IndianMultilingualDataset(
            val_texts, val_labels, self.tokenizer, self.config.max_seq_length
        )
        
        # Create distributed samplers
        train_sampler = DistributedSampler(
            train_dataset, num_replicas=world_size, rank=rank, shuffle=True
        )
        val_sampler = DistributedSampler(
            val_dataset, num_replicas=world_size, rank=rank, shuffle=False
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
        
        logger.info(f"Data loaders created - Train: {len(self.train_loader)}, "
                   f"Val: {len(self.val_loader)} batches")
    
    def setup_model_and_optimizer(self, rank: int):
        """Setup model and optimizer for distributed training"""
        
        # Move model to GPU and wrap with DDP
        device = torch.device(f"cuda:{rank}")
        self.model.to(device)
        self.model = DDP(self.model, device_ids=[rank])
        
        # Setup optimizer
        self.optimizer = optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=0.01
        )
        
        # Setup learning rate scheduler
        total_steps = len(self.train_loader) * self.config.num_epochs
        self.scheduler = optim.lr_scheduler.LinearLR(
            self.optimizer,
            start_factor=0.1,
            total_iters=self.config.warmup_steps
        )
        
        logger.info(f"Model and optimizer setup completed on device: {device}")
    
    def train_epoch(self, epoch: int, rank: int):
        """Train one epoch with distributed coordination"""
        self.model.train()
        total_loss = 0
        num_batches = len(self.train_loader)
        
        self.train_loader.sampler.set_epoch(epoch)  # For proper shuffling
        
        for step, batch in enumerate(self.train_loader):
            # Move batch to device
            device = torch.device(f"cuda:{rank}")
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            # Forward pass
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            logits = self.model.module.classifier(outputs.last_hidden_state[:, 0, :])
            
            # Calculate loss
            loss_fn = nn.CrossEntropyLoss()
            loss = loss_fn(logits, labels)
            
            # Backward pass
            loss.backward()
            
            # Gradient accumulation
            if (step + 1) % self.config.gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                self.scheduler.step()
                self.optimizer.zero_grad()
            
            total_loss += loss.item()
            
            # Resource monitoring
            if self.resource_monitor and step % 50 == 0:
                self.resource_monitor.log_resources(step)
            
            # Progress logging
            if rank == 0 and step % 100 == 0:
                avg_loss = total_loss / (step + 1)
                lr = self.scheduler.get_last_lr()[0]
                logger.info(f"Epoch {epoch}, Step {step}/{num_batches}, "
                          f"Loss: {avg_loss:.4f}, LR: {lr:.2e}")
        
        return total_loss / num_batches
    
    def validate(self, rank: int) -> float:
        """Validate model performance"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        device = torch.device(f"cuda:{rank}")
        
        with torch.no_grad():
            for batch in self.val_loader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                logits = self.model.module.classifier(outputs.last_hidden_state[:, 0, :])
                
                loss_fn = nn.CrossEntropyLoss()
                loss = loss_fn(logits, labels)
                total_loss += loss.item()
                
                # Calculate accuracy
                predictions = torch.argmax(logits, dim=1)
                correct += (predictions == labels).sum().item()
                total += labels.size(0)
        
        accuracy = correct / total
        avg_loss = total_loss / len(self.val_loader)
        
        if rank == 0:
            logger.info(f"Validation - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}")
        
        return accuracy
    
    def save_model(self, epoch: int, rank: int):
        """Save model checkpoint"""
        if rank == 0:  # Only save from rank 0
            checkpoint_path = f"{self.config.output_dir}/checkpoint-epoch-{epoch}"
            os.makedirs(checkpoint_path, exist_ok=True)
            
            # Save model state
            torch.save({
                'epoch': epoch,
                'model_state_dict': self.model.module.state_dict(),
                'optimizer_state_dict': self.optimizer.state_dict(),
                'scheduler_state_dict': self.scheduler.state_dict(),
            }, f"{checkpoint_path}/model.pt")
            
            # Save tokenizer
            self.tokenizer.save_pretrained(checkpoint_path)
            
            logger.info(f"Model saved to {checkpoint_path}")
    
    def train(self, rank: int, world_size: int, train_data: Tuple, val_data: Tuple):
        """Main training function for distributed setup"""
        
        # Setup distributed training
        self.setup_process_group(rank, world_size)
        
        # Initialize resource monitor
        self.resource_monitor = ResourceMonitor(rank)
        
        try:
            # Load model and create data loaders
            self.load_model_and_tokenizer()
            self.create_dataloaders(*train_data, *val_data, rank, world_size)
            self.setup_model_and_optimizer(rank)
            
            # Training loop
            best_accuracy = 0
            for epoch in range(self.config.num_epochs):
                if rank == 0:
                    logger.info(f"Starting epoch {epoch + 1}/{self.config.num_epochs}")
                
                # Train one epoch
                train_loss = self.train_epoch(epoch, rank)
                
                # Validate
                val_accuracy = self.validate(rank)
                
                # Save best model
                if rank == 0 and val_accuracy > best_accuracy:
                    best_accuracy = val_accuracy
                    self.save_model(epoch, rank)
                
                # Synchronize all processes
                dist.barrier()
            
            # Final cost estimation
            if rank == 0:
                final_cost = self.resource_monitor.estimate_cost()
                logger.info(f"Training completed! Best accuracy: {best_accuracy:.4f}")
                logger.info(f"Total cost: ₹{final_cost:.2f}")
                
        except Exception as e:
            logger.error(f"Training failed on rank {rank}: {e}")
            raise
        finally:
            self.cleanup()

def run_distributed_training(rank, world_size, config, train_data, val_data):
    """Entry point for distributed training process"""
    coordinator = DistributedTrainingCoordinator(config)
    coordinator.train(rank, world_size, train_data, val_data)

def main():
    """
    Main function to demonstrate distributed training
    Production example with Indian multilingual data
    """
    
    # Sample Indian multilingual data (normally loaded from database/files)
    train_texts = [
        "यह फिल्म बहुत अच्छी है। I loved it!",  # Hindi + English code-mixing
        "This movie is fantastic and entertaining",
        "इस सिनेमा का story बहुत boring था",
        "The acting was superb but story was weak",
        "मुझे यह movie पसंद नहीं आई क्योंकि it was too long"
    ] * 1000  # Replicate for demo
    
    train_labels = [2, 2, 0, 1, 0] * 1000  # 0: negative, 1: neutral, 2: positive
    
    val_texts = train_texts[:100]
    val_labels = train_labels[:100]
    
    # Training configuration
    config = TrainingConfig(
        model_name="ai4bharat/indic-bert",
        batch_size=16,  # Smaller for demo
        num_epochs=2,
        learning_rate=2e-5,
        output_dir="./models/indic_sentiment"
    )
    
    # Setup for distributed training
    world_size = torch.cuda.device_count()
    if world_size < 2:
        logger.warning("Distributed training requires multiple GPUs. Running on single GPU.")
        world_size = 1
    
    logger.info(f"Starting distributed training on {world_size} GPUs")
    logger.info(f"Model: {config.model_name}")
    logger.info(f"Languages: {config.languages}")
    logger.info(f"Estimated cost: ₹{50 * config.num_epochs * 2:.2f} (₹50/hour GPU)")
    
    # Launch distributed training
    if world_size > 1:
        mp.spawn(
            run_distributed_training,
            args=(world_size, config, (train_texts, train_labels), (val_texts, val_labels)),
            nprocs=world_size,
            join=True
        )
    else:
        # Single GPU training
        run_distributed_training(0, 1, config, (train_texts, train_labels), (val_texts, val_labels))

if __name__ == "__main__":
    main()