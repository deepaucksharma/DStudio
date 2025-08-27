"""
DARTS (Differentiable Architecture Search) Implementation
Flipkart के product image classification के लिए neural architecture search
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import logging
from typing import List, Tuple, Dict, Optional
from collections import namedtuple

# Hindi comments के लिए logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Operation के types define करते हैं - ये basic building blocks हैं
PRIMITIVES = [
    'none',           # No operation - skip connection
    'max_pool_3x3',   # Max pooling 3x3
    'avg_pool_3x3',   # Average pooling 3x3
    'skip_connect',   # Identity/skip connection
    'sep_conv_3x3',   # Separable convolution 3x3 (mobile-friendly)
    'sep_conv_5x5',   # Separable convolution 5x5
    'dil_conv_3x3',   # Dilated convolution 3x3
    'dil_conv_5x5',   # Dilated convolution 5x5
]

# Genotype - discovered architecture का representation
Genotype = namedtuple('Genotype', 'normal normal_concat reduce reduce_concat')

class MixedOp(nn.Module):
    """
    Mixed Operation - सभी possible operations का weighted combination
    DARTS का core idea यही है - continuous relaxation of discrete search space
    """
    
    def __init__(self, C: int, stride: int):
        """
        Args:
            C: Number of input/output channels
            stride: Stride for convolution operations
        """
        super(MixedOp, self).__init__()
        self._ops = nn.ModuleList()
        
        # हर primitive operation के लिए actual layer बनाते हैं
        for primitive in PRIMITIVES:
            op = OPS[primitive](C, stride, False)  # No affine in BN for search
            self._ops.append(op)
    
    def forward(self, x: torch.Tensor, weights: torch.Tensor) -> torch.Tensor:
        """
        Forward pass - सभी operations का weighted sum
        
        Args:
            x: Input tensor
            weights: Architecture weights (alpha parameters)
        """
        # Gumbel softmax for better discrete approximation
        # यह training को stable बनाता है
        if self.training:
            # Hard Gumbel softmax during training
            weights = F.gumbel_softmax(weights, tau=1.0, hard=True, dim=0)
        else:
            # Simple softmax during evaluation
            weights = F.softmax(weights, dim=0)
        
        # Weighted combination of all operations
        result = sum(w * op(x) for w, op in zip(weights, self._ops) if w > 0)
        return result

class Cell(nn.Module):
    """
    DARTS Cell - normal cell या reduction cell
    Flipkart के image classification के लिए optimized
    """
    
    def __init__(self, steps: int, multiplier: int, C_prev_prev: int, 
                 C_prev: int, C: int, reduction: bool, reduction_prev: bool):
        """
        Args:
            steps: Number of intermediate nodes in cell
            multiplier: Channel multiplier for output
            C_prev_prev: Channels from cell s-2
            C_prev: Channels from cell s-1  
            C: Current cell channels
            reduction: Whether this is a reduction cell
            reduction_prev: Whether previous cell was reduction
        """
        super(Cell, self).__init__()
        self.reduction = reduction
        self.steps = steps
        self.multiplier = multiplier
        
        # Input processing layers
        if reduction_prev:
            self.preprocess0 = FactorizedReduce(C_prev_prev, C, affine=False)
        else:
            self.preprocess0 = ReLUConvBN(C_prev_prev, C, 1, 1, 0, affine=False)
        self.preprocess1 = ReLUConvBN(C_prev, C, 1, 1, 0, affine=False)
        
        # Mixed operations for each edge
        self._ops = nn.ModuleList()
        self._bns = nn.ModuleList()
        
        # Cell के अंदर connections बनाते हैं
        for i in range(self.steps):
            for j in range(2 + i):  # 2 input nodes + i intermediate nodes
                stride = 2 if reduction and j < 2 else 1
                op = MixedOp(C, stride)
                self._ops.append(op)
    
    def forward(self, s0: torch.Tensor, s1: torch.Tensor, 
                weights: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through cell
        
        Args:
            s0: Output from cell s-2
            s1: Output from cell s-1
            weights: Architecture weights for this cell
        """
        # Preprocess inputs
        s0 = self.preprocess0(s0)
        s1 = self.preprocess1(s1)
        
        states = [s0, s1]
        offset = 0
        
        # Process each intermediate node
        for i in range(self.steps):
            # Collect inputs from all previous nodes
            node_inputs = []
            for j in range(len(states)):
                node_input = self._ops[offset + j](states[j], weights[offset + j])
                node_inputs.append(node_input)
            
            # Sum all inputs to create new intermediate node
            s = sum(node_inputs)
            states.append(s)
            offset += len(states) - 1
        
        # Concatenate final intermediate nodes (skip input nodes)
        output = torch.cat(states[-self.multiplier:], dim=1)
        return output

class Network(nn.Module):
    """
    Main DARTS Network for Indian e-commerce image classification
    Flipkart, Amazon India के product images के लिए optimized
    """
    
    def __init__(self, C: int, num_classes: int, layers: int, criterion=None,
                 steps: int = 4, multiplier: int = 4, stem_multiplier: int = 3):
        """
        Args:
            C: Initial number of channels
            num_classes: Number of output classes (e.g., product categories)
            layers: Number of cells in the network
            criterion: Loss function
            steps: Number of intermediate nodes per cell
            multiplier: Channel multiplier
            stem_multiplier: Stem channel multiplier
        """
        super(Network, self).__init__()
        self._C = C
        self._num_classes = num_classes
        self._layers = layers
        self._criterion = criterion
        self._steps = steps
        self._multiplier = multiplier
        
        # Stem network - initial feature extraction
        # Indian product images के लिए optimized
        C_curr = stem_multiplier * C
        self.stem = nn.Sequential(
            nn.Conv2d(3, C_curr, 3, padding=1, bias=False),
            nn.BatchNorm2d(C_curr),
            nn.ReLU(inplace=True)
        )
        
        # Architecture parameters (alpha) - ये learnable हैं
        # Normal cell और reduction cell के लिए अलग weights
        self._initialize_alphas()
        
        # Build the network cells
        self.cells = nn.ModuleList()
        
        C_prev_prev, C_prev, C_curr = C_curr, C_curr, C
        reduction_prev = False
        
        for i in range(layers):
            # Reduction cells at 1/3 and 2/3 depth for downsampling
            if i in [layers // 3, 2 * layers // 3]:
                C_curr *= 2
                reduction = True
            else:
                reduction = False
                
            cell = Cell(steps, multiplier, C_prev_prev, C_prev, C_curr, 
                       reduction, reduction_prev)
            reduction_prev = reduction
            self.cells.append(cell)
            
            C_prev_prev, C_prev = C_prev, multiplier * C_curr
        
        # Final classification layer
        self.global_pooling = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(C_prev, num_classes)
        
        logger.info(f"🏗️ DARTS Network initialized - Layers: {layers}, Classes: {num_classes}")
    
    def _initialize_alphas(self):
        """Initialize architecture parameters"""
        k = sum(1 for i in range(self._steps) for n in range(2 + i))
        num_ops = len(PRIMITIVES)
        
        # Normal cell architecture parameters
        self.alphas_normal = nn.Parameter(torch.randn(k, num_ops) * 1e-3)
        
        # Reduction cell architecture parameters  
        self.alphas_reduce = nn.Parameter(torch.randn(k, num_ops) * 1e-3)
        
        # Register as parameters for optimization
        self._arch_parameters = [
            self.alphas_normal,
            self.alphas_reduce,
        ]
        
        logger.info(f"🎛️ Architecture parameters initialized - Normal: {self.alphas_normal.shape}, Reduce: {self.alphas_reduce.shape}")
    
    def forward(self, input: torch.Tensor) -> torch.Tensor:
        """
        Forward pass - Flipkart product image से classification probability तक
        """
        # Stem processing
        s0 = s1 = self.stem(input)
        
        # Pass through all cells
        for i, cell in enumerate(self.cells):
            # Use appropriate architecture weights
            if cell.reduction:
                weights = F.softmax(self.alphas_reduce, dim=-1)
            else:
                weights = F.softmax(self.alphas_normal, dim=-1)
            
            s0, s1 = s1, cell(s0, s1, weights)
        
        # Global average pooling and classification
        out = self.global_pooling(s1)
        out = out.view(out.size(0), -1)
        logits = self.classifier(out)
        
        return logits
    
    def arch_parameters(self):
        """Return architecture parameters for optimization"""
        return self._arch_parameters
    
    def genotype(self) -> Genotype:
        """
        Convert continuous architecture to discrete genotype
        Training के बाद final architecture निकालने के लिए
        """
        def _parse(weights):
            """Parse weights to get top-2 operations for each node"""
            gene = []
            n = 2  # Number of input nodes
            start = 0
            
            for i in range(self._steps):
                end = start + n
                W = weights[start:end].copy()
                
                # Get top-2 operations for current node
                edges = sorted(range(i + 2), 
                             key=lambda x: -max(W[x][k] for k in range(len(W[x])) 
                                               if k != PRIMITIVES.index('none')))[:2]
                
                for j in edges:
                    k_best = None
                    for k in range(len(W[j])):
                        if k != PRIMITIVES.index('none'):
                            if k_best is None or W[j][k] > W[j][k_best]:
                                k_best = k
                    gene.append((PRIMITIVES[k_best], j))
                
                start = end
                n += 1
            
            return gene
        
        # Parse normal and reduction cells
        gene_normal = _parse(F.softmax(self.alphas_normal, dim=-1).data.cpu().numpy())
        gene_reduce = _parse(F.softmax(self.alphas_reduce, dim=-1).data.cpu().numpy())
        
        concat = range(2 + self._steps - self._multiplier, self._steps + 2)
        genotype = Genotype(
            normal=gene_normal, normal_concat=concat,
            reduce=gene_reduce, reduce_concat=concat
        )
        
        logger.info(f"🧬 Genotype extracted: {genotype}")
        return genotype
    
    def loss(self, input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        """Calculate loss for current batch"""
        logits = self(input)
        return self._criterion(logits, target)

# Helper operations used in DARTS

class ReLUConvBN(nn.Module):
    """ReLU + Conv + BatchNorm operation"""
    
    def __init__(self, C_in: int, C_out: int, kernel_size: int, stride: int, 
                 padding: int, affine: bool = True):
        super(ReLUConvBN, self).__init__()
        self.op = nn.Sequential(
            nn.ReLU(inplace=False),
            nn.Conv2d(C_in, C_out, kernel_size, stride=stride, 
                     padding=padding, bias=False),
            nn.BatchNorm2d(C_out, affine=affine)
        )
    
    def forward(self, x):
        return self.op(x)

class DilConv(nn.Module):
    """Dilated Convolution - larger receptive field के लिए"""
    
    def __init__(self, C_in: int, C_out: int, kernel_size: int, stride: int, 
                 padding: int, dilation: int, affine: bool = True):
        super(DilConv, self).__init__()
        self.op = nn.Sequential(
            nn.ReLU(inplace=False),
            nn.Conv2d(C_in, C_out, kernel_size=kernel_size, stride=stride, 
                     padding=padding, dilation=dilation, groups=C_in, bias=False),
            nn.Conv2d(C_in, C_out, kernel_size=1, padding=0, bias=False),
            nn.BatchNorm2d(C_out, affine=affine),
        )
    
    def forward(self, x):
        return self.op(x)

class SepConv(nn.Module):
    """Separable Convolution - mobile-friendly operation"""
    
    def __init__(self, C_in: int, C_out: int, kernel_size: int, stride: int, 
                 padding: int, affine: bool = True):
        super(SepConv, self).__init__()
        self.op = nn.Sequential(
            nn.ReLU(inplace=False),
            nn.Conv2d(C_in, C_in, kernel_size=kernel_size, stride=stride, 
                     padding=padding, groups=C_in, bias=False),
            nn.Conv2d(C_in, C_out, kernel_size=1, padding=0, bias=False),
            nn.BatchNorm2d(C_out, affine=affine),
            nn.ReLU(inplace=False),
            nn.Conv2d(C_out, C_out, kernel_size=kernel_size, stride=1, 
                     padding=padding, groups=C_out, bias=False),
            nn.Conv2d(C_out, C_out, kernel_size=1, padding=0, bias=False),
            nn.BatchNorm2d(C_out, affine=affine),
        )
    
    def forward(self, x):
        return self.op(x)

class FactorizedReduce(nn.Module):
    """Factorized reduction for efficient downsampling"""
    
    def __init__(self, C_in: int, C_out: int, affine: bool = True):
        super(FactorizedReduce, self).__init__()
        assert C_out % 2 == 0
        self.relu = nn.ReLU(inplace=False)
        self.conv_1 = nn.Conv2d(C_in, C_out // 2, 1, stride=2, padding=0, bias=False)
        self.conv_2 = nn.Conv2d(C_in, C_out // 2, 1, stride=2, padding=0, bias=False)
        self.bn = nn.BatchNorm2d(C_out, affine=affine)
    
    def forward(self, x):
        x = self.relu(x)
        out = torch.cat([self.conv_1(x), self.conv_2(x[:, :, 1:, 1:])], dim=1)
        out = self.bn(out)
        return out

# Operations dictionary
OPS = {
    'none': lambda C, stride, affine: Zero(stride),
    'avg_pool_3x3': lambda C, stride, affine: nn.AvgPool2d(3, stride=stride, padding=1, count_include_pad=False),
    'max_pool_3x3': lambda C, stride, affine: nn.MaxPool2d(3, stride=stride, padding=1),
    'skip_connect': lambda C, stride, affine: Identity() if stride == 1 else FactorizedReduce(C, C, affine=affine),
    'sep_conv_3x3': lambda C, stride, affine: SepConv(C, C, 3, stride, 1, affine=affine),
    'sep_conv_5x5': lambda C, stride, affine: SepConv(C, C, 5, stride, 2, affine=affine),
    'dil_conv_3x3': lambda C, stride, affine: DilConv(C, C, 3, stride, 2, 2, affine=affine),
    'dil_conv_5x5': lambda C, stride, affine: DilConv(C, C, 5, stride, 4, 2, affine=affine),
}

class Identity(nn.Module):
    """Identity operation - input को as-is pass करता है"""
    
    def forward(self, x):
        return x

class Zero(nn.Module):
    """Zero operation - for 'none' primitive"""
    
    def __init__(self, stride):
        super(Zero, self).__init__()
        self.stride = stride
    
    def forward(self, x):
        if self.stride == 1:
            return x.mul(0.)
        return x[:, :, ::self.stride, ::self.stride].mul(0.)

class DARTSTrainer:
    """
    DARTS Training Loop for Indian E-commerce
    Flipkart के product categories के लिए optimized
    """
    
    def __init__(self, model: Network, train_loader, valid_loader, 
                 w_lr: float = 0.025, arch_lr: float = 3e-4, w_momentum: float = 0.9,
                 w_weight_decay: float = 3e-4, device: str = 'cuda'):
        """
        Args:
            model: DARTS network model
            train_loader: Training data loader
            valid_loader: Validation data loader
            w_lr: Learning rate for network weights
            arch_lr: Learning rate for architecture parameters
            w_momentum: Momentum for weight optimizer
            w_weight_decay: Weight decay for regularization
            device: Training device (cuda/cpu)
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.valid_loader = valid_loader
        self.device = device
        
        # Network weights optimizer (SGD with momentum)
        self.w_optimizer = torch.optim.SGD(
            model.parameters(),
            lr=w_lr,
            momentum=w_momentum,
            weight_decay=w_weight_decay
        )
        
        # Architecture parameters optimizer (Adam)
        self.arch_optimizer = torch.optim.Adam(
            model.arch_parameters(),
            lr=arch_lr,
            betas=(0.5, 0.999),
            weight_decay=1e-3
        )
        
        # Learning rate scheduler
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.w_optimizer, T_max=100, eta_min=0.001
        )
        
        logger.info(f"🏃‍♂️ DARTS Trainer initialized - Device: {device}")
    
    def train_epoch(self, epoch: int) -> Tuple[float, float, float]:
        """
        Train one epoch with bilevel optimization
        
        Returns:
            Tuple of (train_loss, train_acc, valid_loss)
        """
        self.model.train()
        train_loss = 0.0
        train_acc = 0.0
        total_samples = 0
        
        train_iter = iter(self.train_loader)
        valid_iter = iter(self.valid_loader)
        
        for step in range(len(self.train_loader)):
            # Get training batch
            try:
                train_X, train_y = next(train_iter)
            except StopIteration:
                train_iter = iter(self.train_loader)
                train_X, train_y = next(train_iter)
            
            # Get validation batch for architecture update
            try:
                valid_X, valid_y = next(valid_iter)
            except StopIteration:
                valid_iter = iter(self.valid_loader)
                valid_X, valid_y = next(valid_iter)
            
            train_X, train_y = train_X.to(self.device), train_y.to(self.device)
            valid_X, valid_y = valid_X.to(self.device), valid_y.to(self.device)
            
            # Update architecture parameters (alpha)
            self.arch_optimizer.zero_grad()
            logits = self.model(valid_X)
            arch_loss = F.cross_entropy(logits, valid_y)
            arch_loss.backward()
            self.arch_optimizer.step()
            
            # Update network weights
            self.w_optimizer.zero_grad()
            logits = self.model(train_X)
            loss = F.cross_entropy(logits, train_y)
            loss.backward()
            
            # Gradient clipping for stability
            nn.utils.clip_grad_norm_(self.model.parameters(), 5.0)
            self.w_optimizer.step()
            
            # Calculate accuracy
            pred = logits.argmax(dim=1)
            acc = (pred == train_y).float().mean()
            
            train_loss += loss.item()
            train_acc += acc.item()
            total_samples += 1
            
            if step % 50 == 0:
                logger.info(f"Epoch {epoch}, Step {step}: Loss={loss.item():.4f}, Acc={acc.item():.4f}")
        
        # Update learning rate
        self.scheduler.step()
        
        avg_train_loss = train_loss / total_samples
        avg_train_acc = train_acc / total_samples
        
        # Validate on validation set
        val_loss = self.validate()
        
        logger.info(f"🎯 Epoch {epoch} completed - Train Loss: {avg_train_loss:.4f}, "
                   f"Train Acc: {avg_train_acc:.4f}, Val Loss: {val_loss:.4f}")
        
        return avg_train_loss, avg_train_acc, val_loss
    
    def validate(self) -> float:
        """Validate current model"""
        self.model.eval()
        val_loss = 0.0
        total_samples = 0
        
        with torch.no_grad():
            for valid_X, valid_y in self.valid_loader:
                valid_X, valid_y = valid_X.to(self.device), valid_y.to(self.device)
                logits = self.model(valid_X)
                loss = F.cross_entropy(logits, valid_y)
                val_loss += loss.item()
                total_samples += 1
        
        return val_loss / total_samples
    
    def search(self, epochs: int = 50) -> Genotype:
        """
        Run complete DARTS search process
        
        Args:
            epochs: Number of training epochs
            
        Returns:
            Final discovered architecture genotype
        """
        logger.info(f"🔍 Starting DARTS search for {epochs} epochs...")
        
        best_val_loss = float('inf')
        best_genotype = None
        
        for epoch in range(epochs):
            train_loss, train_acc, val_loss = self.train_epoch(epoch)
            
            # Save best architecture based on validation loss
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_genotype = self.model.genotype()
                logger.info(f"🏆 New best architecture found at epoch {epoch}")
            
            # Print current architecture every 10 epochs
            if epoch % 10 == 0:
                current_genotype = self.model.genotype()
                logger.info(f"Current architecture: {current_genotype}")
        
        logger.info(f"✅ DARTS search completed!")
        logger.info(f"🥇 Best validation loss: {best_val_loss:.4f}")
        logger.info(f"🏗️ Best architecture: {best_genotype}")
        
        return best_genotype

if __name__ == "__main__":
    # Example usage for Flipkart product classification
    print("🛍️ DARTS example for Flipkart product classification")
    
    # Create model for Indian e-commerce (100 product categories)
    model = Network(C=16, num_classes=100, layers=8, 
                   criterion=nn.CrossEntropyLoss())
    
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"Architecture parameters: {sum(p.numel() for p in model.arch_parameters()):,}")
    
    # Mock input (224x224 product images)
    x = torch.randn(4, 3, 224, 224)
    logits = model(x)
    print(f"Output shape: {logits.shape}")
    
    # Show current genotype
    genotype = model.genotype()
    print(f"Initial genotype: {genotype}")