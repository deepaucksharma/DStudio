"""
ENAS (Efficient Neural Architecture Search) Implementation
Paytm के fraud detection models के लिए reinforcement learning based NAS
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
from typing import List, Tuple, Dict, Optional
from collections import defaultdict
import random

# Hindi comments के साथ logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class ENASController(nn.Module):
    """
    ENAS Controller - RNN-based architecture generator
    Paytm के लिए fraud detection architectures generate करता है
    """
    
    def __init__(self, num_layers: int = 12, num_branches: int = 6, 
                 out_filters: int = 36, lstm_size: int = 32, 
                 lstm_num_layers: int = 2, lstm_keep_prob: float = 1.0,
                 tanh_constant: float = 1.5, temperature: float = None,
                 skip_target: float = 0.4, skip_weight: float = 0.8):
        """
        Args:
            num_layers: SuperNet में layers की संख्या
            num_branches: हर layer में possible operations
            out_filters: Output channels
            lstm_size: LSTM hidden size
            lstm_num_layers: LSTM layers
            lstm_keep_prob: Dropout probability
            tanh_constant: Tanh constant for attention
            temperature: Sampling temperature
            skip_target: Target skip connection ratio
            skip_weight: Skip connection weight
        """
        super(ENASController, self).__init__()
        
        self.num_layers = num_layers
        self.num_branches = num_branches
        self.out_filters = out_filters
        self.lstm_size = lstm_size
        self.lstm_num_layers = lstm_num_layers
        self.lstm_keep_prob = lstm_keep_prob
        self.tanh_constant = tanh_constant
        self.temperature = temperature
        self.skip_target = skip_target
        self.skip_weight = skip_weight
        
        # LSTM Controller for generating architectures
        self.lstm = nn.LSTM(
            input_size=self.lstm_size,
            hidden_size=self.lstm_size,
            num_layers=self.lstm_num_layers,
            batch_first=True,
            dropout=1.0 - self.lstm_keep_prob if self.lstm_num_layers > 1 else 0
        )
        
        # Embedding layers for different decision types
        self.g_emb = nn.Embedding(1, self.lstm_size)  # Go embedding
        
        # Operation selection embeddings
        self.op_emb = nn.Embedding(self.num_branches, self.lstm_size)
        
        # Skip connection embeddings
        self.skip_emb = nn.Embedding(1, self.lstm_size)
        
        # Output layers for different decisions
        self.op_linear = nn.Linear(self.lstm_size, self.num_branches)
        self.skip_linear = nn.Linear(self.lstm_size, 1)
        
        # Attention mechanism for skip connections
        self.attention_linear = nn.Linear(self.lstm_size, self.lstm_size)
        
        # Initialize parameters
        self.reset_parameters()
        
        logger.info(f"🧠 ENAS Controller initialized - Layers: {num_layers}, Branches: {num_branches}")
    
    def reset_parameters(self):
        """Initialize controller parameters"""
        init_range = 0.1
        for param in self.parameters():
            param.data.uniform_(-init_range, init_range)
        
        # Zero out skip connection bias to prefer no skip initially
        self.skip_linear.bias.data.fill_(-1.0)
    
    def forward(self, batch_size: int = 1) -> Tuple[torch.Tensor, torch.Tensor, List]:
        """
        Generate architectures using LSTM controller
        
        Args:
            batch_size: Number of architectures to generate
            
        Returns:
            log_probs: Log probabilities of generated architectures
            entropies: Entropy of decisions for regularization
            architectures: List of generated architecture specifications
        """
        # Initialize hidden state
        h_0 = torch.zeros(self.lstm_num_layers, batch_size, self.lstm_size, 
                         device=next(self.parameters()).device)
        c_0 = torch.zeros(self.lstm_num_layers, batch_size, self.lstm_size,
                         device=next(self.parameters()).device)
        
        # Go embedding to start generation
        inputs = self.g_emb.weight.unsqueeze(0).repeat(batch_size, 1, 1)
        
        log_probs = []
        entropies = []
        architectures = []
        
        # Hidden states for attention mechanism
        all_h = []
        
        for layer_id in range(self.num_layers):
            # LSTM forward pass
            output, (h_0, c_0) = self.lstm(inputs, (h_0, c_0))
            hidden = output.squeeze(1)  # [batch_size, lstm_size]
            all_h.append(hidden)
            
            # Operation selection
            op_logits = self.op_linear(hidden)
            if self.temperature is not None:
                op_logits /= self.temperature
            
            op_probs = F.softmax(op_logits, dim=-1)
            op_log_probs = F.log_softmax(op_logits, dim=-1)
            
            # Sample operation
            op_entropy = -(op_probs * op_log_probs).sum(1, keepdim=True)
            op_action = torch.multinomial(op_probs, 1).squeeze(1)
            selected_op_log_prob = op_log_probs.gather(1, op_action.unsqueeze(1))
            
            log_probs.append(selected_op_log_prob)
            entropies.append(op_entropy)
            
            # Skip connections (only after first layer)
            skip_targets = []
            if layer_id > 0:
                # Attention-based skip connection prediction
                skip_targets = self._get_skip_connections(
                    all_h, hidden, layer_id, batch_size
                )
            
            # Store architecture information
            if len(architectures) == 0:
                for _ in range(batch_size):
                    architectures.append({
                        'operations': [],
                        'skip_connections': []
                    })
            
            for i in range(batch_size):
                architectures[i]['operations'].append(op_action[i].item())
                architectures[i]['skip_connections'].append(skip_targets)
            
            # Prepare input for next step
            inputs = self.op_emb(op_action).unsqueeze(1)
        
        # Concatenate all log probabilities and entropies
        total_log_prob = torch.cat(log_probs, dim=1).sum(dim=1)
        total_entropy = torch.cat(entropies, dim=1).sum(dim=1)
        
        return total_log_prob, total_entropy, architectures
    
    def _get_skip_connections(self, all_h: List[torch.Tensor], 
                            current_h: torch.Tensor, layer_id: int, 
                            batch_size: int) -> List[int]:
        """
        Generate skip connections using attention mechanism
        
        Args:
            all_h: Previous hidden states
            current_h: Current hidden state
            layer_id: Current layer index
            batch_size: Batch size
            
        Returns:
            List of skip connection targets
        """
        skip_targets = []
        
        if layer_id == 0:
            return skip_targets
        
        # Attention over previous layers
        prev_h = torch.stack(all_h[:-1], dim=1)  # [batch_size, layer_id, lstm_size]
        
        # Compute attention weights
        query = self.attention_linear(current_h).unsqueeze(1)  # [batch_size, 1, lstm_size]
        key = prev_h  # [batch_size, layer_id, lstm_size]
        
        # Scaled dot-product attention
        attention_logits = torch.bmm(query, key.transpose(1, 2))  # [batch_size, 1, layer_id]
        attention_logits = attention_logits.squeeze(1)  # [batch_size, layer_id]
        
        if self.tanh_constant is not None:
            attention_logits = self.tanh_constant * torch.tanh(attention_logits)
        
        # Sample skip connections
        attention_probs = torch.sigmoid(attention_logits)
        
        for i in range(batch_size):
            batch_skip_targets = []
            for j in range(layer_id):
                # Probabilistic skip connection
                prob = attention_probs[i, j].item()
                if random.random() < prob:
                    batch_skip_targets.append(j)
            skip_targets.append(batch_skip_targets)
        
        return skip_targets
    
    def sample_arch(self) -> Dict:
        """
        Sample a single architecture
        
        Returns:
            Architecture specification dictionary
        """
        with torch.no_grad():
            log_prob, entropy, architectures = self.forward(batch_size=1)
            return architectures[0]

class ENASSupernet(nn.Module):
    """
    ENAS Supernet - सभी possible architectures का superset
    Paytm fraud detection के लिए optimized operations
    """
    
    def __init__(self, num_layers: int = 12, out_filters: int = 36, 
                 num_classes: int = 2, input_channels: int = 128):
        """
        Args:
            num_layers: Number of layers in supernet
            out_filters: Number of output filters
            num_classes: Number of output classes (fraud/not fraud)
            input_channels: Input feature dimensions
        """
        super(ENASSupernet, self).__init__()
        
        self.num_layers = num_layers
        self.out_filters = out_filters
        self.num_classes = num_classes
        
        # Define possible operations for fraud detection
        self.operations = nn.ModuleList([
            # Linear layers with different sizes
            nn.Linear(input_channels, out_filters),           # 0: small linear
            nn.Linear(input_channels, out_filters * 2),       # 1: medium linear  
            nn.Linear(input_channels, out_filters * 4),       # 2: large linear
            
            # Attention-based operations
            SelfAttentionLayer(input_channels, out_filters),   # 3: self attention
            CrossAttentionLayer(input_channels, out_filters),  # 4: cross attention
            
            # Skip connection
            IdentityLayer(),                                   # 5: identity/skip
        ])
        
        # Layer normalization for each layer
        self.layer_norms = nn.ModuleList([
            nn.LayerNorm(out_filters) for _ in range(num_layers)
        ])
        
        # Final classification head
        self.classifier = nn.Sequential(
            nn.Linear(out_filters, out_filters // 2),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(out_filters // 2, num_classes)
        )
        
        logger.info(f"🏗️ ENAS Supernet initialized - Layers: {num_layers}, Classes: {num_classes}")
    
    def forward(self, x: torch.Tensor, architecture: Dict) -> torch.Tensor:
        """
        Forward pass with specific architecture
        
        Args:
            x: Input features [batch_size, feature_dim]
            architecture: Architecture specification from controller
            
        Returns:
            Classification logits
        """
        batch_size = x.size(0)
        
        # Layer outputs for skip connections
        layer_outputs = [x]
        
        current_output = x
        
        for layer_id in range(self.num_layers):
            # Get operation for this layer
            op_id = architecture['operations'][layer_id]
            skip_connections = architecture['skip_connections'][layer_id]
            
            # Apply operation
            if op_id < len(self.operations):
                layer_input = current_output
                
                # Add skip connections if any
                if skip_connections and len(skip_connections) > 0:
                    skip_sum = sum(layer_outputs[i] for i in skip_connections 
                                 if i < len(layer_outputs))
                    if isinstance(skip_sum, torch.Tensor):
                        # Ensure compatible dimensions
                        if skip_sum.size(-1) == layer_input.size(-1):
                            layer_input = layer_input + skip_sum
                
                # Apply the selected operation
                operation = self.operations[op_id]
                layer_output = operation(layer_input)
                
                # Apply layer normalization
                if layer_output.size(-1) == self.out_filters:
                    layer_output = self.layer_norms[layer_id](layer_output)
                
                # Apply activation
                layer_output = F.relu(layer_output)
                
                layer_outputs.append(layer_output)
                current_output = layer_output
            else:
                # Invalid operation, use identity
                layer_outputs.append(current_output)
        
        # Final classification
        logits = self.classifier(current_output)
        return logits

class SelfAttentionLayer(nn.Module):
    """Self-attention layer for fraud detection features"""
    
    def __init__(self, input_dim: int, output_dim: int, num_heads: int = 8):
        super(SelfAttentionLayer, self).__init__()
        self.attention = nn.MultiheadAttention(
            embed_dim=input_dim,
            num_heads=num_heads,
            batch_first=True
        )
        self.projection = nn.Linear(input_dim, output_dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Add sequence dimension for attention
        x_seq = x.unsqueeze(1)  # [batch_size, 1, feature_dim]
        
        # Self-attention
        attended, _ = self.attention(x_seq, x_seq, x_seq)
        attended = attended.squeeze(1)  # [batch_size, feature_dim]
        
        # Project to output dimension
        output = self.projection(attended)
        return output

class CrossAttentionLayer(nn.Module):
    """Cross-attention layer for comparing transaction patterns"""
    
    def __init__(self, input_dim: int, output_dim: int, num_heads: int = 4):
        super(CrossAttentionLayer, self).__init__()
        self.attention = nn.MultiheadAttention(
            embed_dim=input_dim,
            num_heads=num_heads,
            batch_first=True
        )
        self.projection = nn.Linear(input_dim, output_dim)
        
        # Learnable reference patterns for fraud detection
        self.reference_patterns = nn.Parameter(
            torch.randn(10, input_dim) * 0.1  # 10 reference fraud patterns
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.size(0)
        
        # Expand reference patterns for batch
        references = self.reference_patterns.unsqueeze(0).expand(
            batch_size, -1, -1
        )  # [batch_size, 10, input_dim]
        
        # Query with input, key/value with reference patterns
        x_seq = x.unsqueeze(1)  # [batch_size, 1, input_dim]
        
        attended, _ = self.attention(x_seq, references, references)
        attended = attended.squeeze(1)  # [batch_size, input_dim]
        
        # Project to output dimension
        output = self.projection(attended)
        return output

class IdentityLayer(nn.Module):
    """Identity layer for skip connections"""
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x

class ENASTrainer:
    """
    ENAS Training Loop for Paytm Fraud Detection
    Controller और Supernet को jointly train करता है
    """
    
    def __init__(self, controller: ENASController, supernet: ENASSupernet,
                 train_loader, valid_loader, device: str = 'cuda',
                 controller_lr: float = 3.5e-4, child_lr: float = 0.05,
                 entropy_weight: float = 1e-4, baseline_decay: float = 0.999):
        """
        Args:
            controller: ENAS controller for architecture generation
            supernet: ENAS supernet for training
            train_loader: Training data loader
            valid_loader: Validation data loader
            device: Training device
            controller_lr: Controller learning rate
            child_lr: Child network learning rate
            entropy_weight: Entropy regularization weight
            baseline_decay: Baseline exponential moving average decay
        """
        self.controller = controller.to(device)
        self.supernet = supernet.to(device)
        self.train_loader = train_loader
        self.valid_loader = valid_loader
        self.device = device
        self.entropy_weight = entropy_weight
        self.baseline_decay = baseline_decay
        
        # Optimizers
        self.controller_optimizer = torch.optim.Adam(
            self.controller.parameters(), lr=controller_lr
        )
        
        self.supernet_optimizer = torch.optim.SGD(
            self.supernet.parameters(), lr=child_lr, momentum=0.9, weight_decay=1e-4
        )
        
        # Moving baseline for REINFORCE
        self.baseline = None
        
        # Loss function for fraud detection (binary classification)
        self.criterion = nn.CrossEntropyLoss()
        
        logger.info(f"🏃‍♂️ ENAS Trainer initialized - Device: {device}")
    
    def train_supernet(self, num_epochs: int = 100, architectures_per_epoch: int = 50):
        """
        Train supernet with random architectures
        
        Args:
            num_epochs: Number of training epochs
            architectures_per_epoch: Architectures to sample per epoch
        """
        logger.info(f"🏗️ Training supernet for {num_epochs} epochs...")
        
        for epoch in range(num_epochs):
            self.supernet.train()
            total_loss = 0.0
            total_acc = 0.0
            total_batches = 0
            
            for batch_idx, (data, target) in enumerate(self.train_loader):
                data, target = data.to(self.device), target.to(self.device)
                
                # Sample random architecture for this batch
                architecture = self.controller.sample_arch()
                
                # Forward pass with sampled architecture
                self.supernet_optimizer.zero_grad()
                logits = self.supernet(data, architecture)
                loss = self.criterion(logits, target)
                
                # Backward pass
                loss.backward()
                self.supernet_optimizer.step()
                
                # Calculate accuracy
                pred = logits.argmax(dim=1)
                acc = (pred == target).float().mean()
                
                total_loss += loss.item()
                total_acc += acc.item()
                total_batches += 1
                
                if batch_idx % 50 == 0:
                    logger.info(f"Epoch {epoch}, Batch {batch_idx}: "
                               f"Loss={loss.item():.4f}, Acc={acc.item():.4f}")
            
            avg_loss = total_loss / total_batches
            avg_acc = total_acc / total_batches
            
            logger.info(f"📊 Epoch {epoch} - Avg Loss: {avg_loss:.4f}, "
                       f"Avg Acc: {avg_acc:.4f}")
    
    def train_controller(self, num_epochs: int = 50, 
                        num_samples: int = 10, controller_steps: int = 5):
        """
        Train controller using REINFORCE
        
        Args:
            num_epochs: Number of controller training epochs
            num_samples: Architectures to sample for reward estimation
            controller_steps: Controller optimization steps per epoch
        """
        logger.info(f"🧠 Training controller for {num_epochs} epochs...")
        
        for epoch in range(num_epochs):
            self.controller.train()
            
            for step in range(controller_steps):
                # Sample architectures and get their rewards
                log_probs, entropies, architectures = self.controller(
                    batch_size=num_samples
                )
                
                # Evaluate architectures on validation set
                rewards = []
                for arch in architectures:
                    reward = self._evaluate_architecture(arch)
                    rewards.append(reward)
                
                rewards = torch.tensor(rewards, device=self.device)
                
                # Update moving baseline
                if self.baseline is None:
                    self.baseline = rewards.mean()
                else:
                    self.baseline = (self.baseline_decay * self.baseline + 
                                   (1 - self.baseline_decay) * rewards.mean())
                
                # REINFORCE loss
                advantages = rewards - self.baseline
                controller_loss = -(log_probs * advantages).mean()
                
                # Add entropy regularization
                entropy_loss = -entropies.mean()
                total_loss = controller_loss + self.entropy_weight * entropy_loss
                
                # Update controller
                self.controller_optimizer.zero_grad()
                total_loss.backward()
                self.controller_optimizer.step()
                
                if step % 5 == 0:
                    logger.info(f"Controller Epoch {epoch}, Step {step}: "
                               f"Loss={total_loss.item():.4f}, "
                               f"Reward={rewards.mean().item():.4f}")
        
        logger.info("✅ Controller training completed!")
    
    def _evaluate_architecture(self, architecture: Dict) -> float:
        """
        Evaluate architecture on validation set
        
        Args:
            architecture: Architecture specification
            
        Returns:
            Validation accuracy as reward
        """
        self.supernet.eval()
        total_correct = 0
        total_samples = 0
        
        with torch.no_grad():
            for data, target in self.valid_loader:
                if total_samples > 1000:  # Quick evaluation
                    break
                    
                data, target = data.to(self.device), target.to(self.device)
                logits = self.supernet(data, architecture)
                pred = logits.argmax(dim=1)
                total_correct += (pred == target).sum().item()
                total_samples += target.size(0)
        
        accuracy = total_correct / total_samples if total_samples > 0 else 0.0
        return accuracy
    
    def search(self, supernet_epochs: int = 100, controller_epochs: int = 50) -> Dict:
        """
        Complete ENAS search process
        
        Args:
            supernet_epochs: Epochs to train supernet
            controller_epochs: Epochs to train controller
            
        Returns:
            Best discovered architecture
        """
        logger.info("🔍 Starting ENAS search process...")
        
        # Phase 1: Train supernet with random architectures
        self.train_supernet(supernet_epochs)
        
        # Phase 2: Train controller to find good architectures
        self.train_controller(controller_epochs)
        
        # Phase 3: Find best architecture
        logger.info("🎯 Finding best architecture...")
        best_arch = None
        best_reward = -1.0
        
        for _ in range(100):  # Sample 100 architectures
            arch = self.controller.sample_arch()
            reward = self._evaluate_architecture(arch)
            
            if reward > best_reward:
                best_reward = reward
                best_arch = arch
        
        logger.info(f"🏆 Best architecture found with reward: {best_reward:.4f}")
        logger.info(f"🏗️ Architecture: {best_arch}")
        
        return best_arch

if __name__ == "__main__":
    # Example usage for Paytm fraud detection
    print("💳 ENAS example for Paytm fraud detection")
    
    # Create controller and supernet
    controller = ENASController(num_layers=8, num_branches=6)
    supernet = ENASSupernet(num_layers=8, out_filters=64, num_classes=2)
    
    print(f"Controller parameters: {sum(p.numel() for p in controller.parameters()):,}")
    print(f"Supernet parameters: {sum(p.numel() for p in supernet.parameters()):,}")
    
    # Sample architecture
    architecture = controller.sample_arch()
    print(f"Sample architecture: {architecture}")
    
    # Test forward pass
    x = torch.randn(32, 128)  # Batch of fraud detection features
    logits = supernet(x, architecture)
    print(f"Output shape: {logits.shape}")
    
    # Show probabilities
    probs = F.softmax(logits, dim=1)
    print(f"Sample predictions: {probs[:5]}")  # First 5 predictions