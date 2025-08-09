# Episode 142: Federated Learning Systems - AI & ML Systems in Distributed Computing

## Abstract

Federated learning represents a paradigm shift in distributed machine learning, enabling collaborative model training across decentralized data sources while preserving privacy. This approach addresses critical challenges in modern AI deployment: data privacy regulations, bandwidth constraints, and the need to leverage data distributed across edge devices, institutions, and organizations without centralizing sensitive information.

This episode explores the theoretical foundations of federated learning, from secure aggregation protocols to differential privacy mechanisms. We examine production systems including Google's Gboard keyboard predictions, Apple's Siri improvements, and healthcare applications where patient privacy is paramount. Through mathematical analysis and practical implementations, we'll understand how federated learning balances model performance with privacy preservation in real-world distributed systems.

## Table of Contents

1. Foundations of Federated Learning
2. Privacy-Preserving Distributed Learning Theory
3. Secure Aggregation Protocols
4. Differential Privacy in Federated Settings
5. Communication-Efficient Federated Learning
6. Non-IID Data Challenges and Solutions
7. Federated Learning Algorithms and Convergence
8. Production Systems and Applications
9. Cross-Silo vs Cross-Device Federated Learning
10. Security Threats and Defenses
11. Future Directions and Research Frontiers

## 1. Foundations of Federated Learning

Federated learning (FL) was formally introduced by Google in 2016 to address the challenge of training machine learning models on distributed data without centralizing the data itself. The fundamental principle is "bring the code to the data, not the data to the code."

### Mathematical Framework

Consider K participating clients, each with local dataset Dₖ of size nₖ. The global objective is to minimize:

```
F(w) = Σₖ₌₁ᴷ (nₖ/n) Fₖ(w)
```

where:
- w are the global model parameters
- n = Σₖ nₖ is the total number of samples
- Fₖ(w) = (1/nₖ) Σᵢ∈Dₖ ℓ(xᵢ, yᵢ; w) is the local objective function

This differs from traditional distributed learning in several key aspects:
1. **Heterogeneous data**: Each client's data follows different distributions
2. **Intermittent participation**: Clients may not always be available
3. **Privacy constraints**: Raw data never leaves client devices
4. **Resource constraints**: Clients have limited computation and communication capabilities

### Federated Averaging (FedAvg) Algorithm

The foundational federated learning algorithm is FedAvg:

```python
import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Tuple
import copy

class FederatedAveraging:
    """
    Federated Averaging (FedAvg) implementation with comprehensive optimizations
    """
    
    def __init__(self, global_model: nn.Module, learning_rate: float = 0.01,
                 client_fraction: float = 1.0, local_epochs: int = 1):
        self.global_model = global_model
        self.learning_rate = learning_rate
        self.client_fraction = client_fraction
        self.local_epochs = local_epochs
        
        # Track convergence metrics
        self.global_loss_history = []
        self.client_participation_history = []
        self.communication_costs = []
        
    def federated_averaging(self, clients: List['FederatedClient'], 
                          communication_rounds: int) -> Dict:
        """
        Main federated averaging algorithm
        
        Args:
            clients: List of federated learning clients
            communication_rounds: Number of global communication rounds
            
        Returns:
            Dictionary with training metrics and final model
        """
        
        for round_idx in range(communication_rounds):
            print(f"Communication Round {round_idx + 1}/{communication_rounds}")
            
            # Client selection
            selected_clients = self._select_clients(clients)
            self.client_participation_history.append(len(selected_clients))
            
            # Broadcast global model to selected clients
            client_updates = []
            total_samples = 0
            
            for client in selected_clients:
                # Send current global model to client
                client_model = copy.deepcopy(self.global_model)
                
                # Client performs local training
                local_update, num_samples = client.local_training(
                    client_model, self.local_epochs, self.learning_rate
                )
                
                client_updates.append({
                    'model_update': local_update,
                    'num_samples': num_samples
                })
                total_samples += num_samples
            
            # Aggregate client updates
            self._aggregate_updates(client_updates, total_samples)
            
            # Evaluate global model
            global_loss = self._evaluate_global_model(clients)
            self.global_loss_history.append(global_loss)
            
            # Communication cost tracking
            model_size = sum(p.numel() for p in self.global_model.parameters())
            round_comm_cost = len(selected_clients) * model_size * 2  # Upload + download
            self.communication_costs.append(round_comm_cost)
            
            if round_idx % 10 == 0:
                print(f"Round {round_idx}, Global Loss: {global_loss:.4f}")
        
        return {
            'final_model': self.global_model,
            'loss_history': self.global_loss_history,
            'communication_costs': self.communication_costs,
            'participation_history': self.client_participation_history
        }
    
    def _select_clients(self, clients: List['FederatedClient']) -> List['FederatedClient']:
        """Select subset of clients for this round"""
        num_selected = max(1, int(len(clients) * self.client_fraction))
        return np.random.choice(clients, num_selected, replace=False).tolist()
    
    def _aggregate_updates(self, client_updates: List[Dict], total_samples: int):
        """Perform weighted averaging of client model updates"""
        
        # Initialize aggregated parameters
        aggregated_state = {}
        for name, param in self.global_model.named_parameters():
            aggregated_state[name] = torch.zeros_like(param)
        
        # Weighted averaging based on number of samples
        for update in client_updates:
            weight = update['num_samples'] / total_samples
            client_state = update['model_update']
            
            for name in aggregated_state:
                aggregated_state[name] += weight * client_state[name]
        
        # Update global model
        global_state = self.global_model.state_dict()
        for name in aggregated_state:
            global_state[name] = aggregated_state[name]
        
        self.global_model.load_state_dict(global_state)
    
    def _evaluate_global_model(self, clients: List['FederatedClient']) -> float:
        """Evaluate global model on all client data"""
        total_loss = 0.0
        total_samples = 0
        
        self.global_model.eval()
        with torch.no_grad():
            for client in clients:
                client_loss, num_samples = client.evaluate_model(self.global_model)
                total_loss += client_loss * num_samples
                total_samples += num_samples
        
        return total_loss / total_samples if total_samples > 0 else float('inf')

class FederatedClient:
    """
    Federated learning client with local training and evaluation capabilities
    """
    
    def __init__(self, client_id: str, local_data: torch.utils.data.DataLoader,
                 test_data: torch.utils.data.DataLoader = None):
        self.client_id = client_id
        self.local_data = local_data
        self.test_data = test_data
        
        # Client-specific hyperparameters
        self.local_learning_rate = 0.01
        self.batch_size = 32
        
        # Privacy and security settings
        self.privacy_budget = 1.0  # For differential privacy
        self.add_noise = False
        
    def local_training(self, model: nn.Module, epochs: int, 
                      learning_rate: float) -> Tuple[Dict, int]:
        """
        Perform local training on client data
        
        Returns:
            Tuple of (model state dict, number of training samples)
        """
        model.train()
        optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()
        
        num_samples = 0
        
        for epoch in range(epochs):
            for batch_idx, (data, target) in enumerate(self.local_data):
                optimizer.zero_grad()
                output = model(data)
                loss = criterion(output, target)
                loss.backward()
                
                # Optional: Add differential privacy noise
                if self.add_noise:
                    self._add_dp_noise(model, self.privacy_budget)
                
                optimizer.step()
                num_samples += len(data)
        
        return model.state_dict(), num_samples
    
    def evaluate_model(self, model: nn.Module) -> Tuple[float, int]:
        """Evaluate model on client's test data"""
        model.eval()
        criterion = nn.CrossEntropyLoss()
        
        total_loss = 0.0
        num_samples = 0
        
        with torch.no_grad():
            data_loader = self.test_data if self.test_data else self.local_data
            for data, target in data_loader:
                output = model(data)
                loss = criterion(output, target)
                total_loss += loss.item() * len(data)
                num_samples += len(data)
        
        return total_loss / num_samples if num_samples > 0 else 0.0, num_samples
    
    def _add_dp_noise(self, model: nn.Module, privacy_budget: float):
        """Add differential privacy noise to gradients"""
        with torch.no_grad():
            for param in model.parameters():
                if param.grad is not None:
                    # Gaussian mechanism for differential privacy
                    sensitivity = 2.0  # L2 sensitivity
                    noise_scale = sensitivity / privacy_budget
                    noise = torch.normal(0, noise_scale, size=param.grad.shape)
                    param.grad += noise
```

### Convergence Analysis of FedAvg

The convergence properties of FedAvg depend on data heterogeneity and system parameters. Under certain assumptions, we can establish convergence rates:

**Assumption 1 (L-Smoothness)**: Each local function Fₖ is L-smooth:
```
||∇Fₖ(x) - ∇Fₖ(y)|| ≤ L||x - y||
```

**Assumption 2 (Bounded Divergence)**: The divergence between local and global optima is bounded:
```
||∇Fₖ(w*)|| ≤ σₖ for all k
```

**Theorem**: Under L-smoothness and bounded divergence, FedAvg with E local epochs and learning rate η satisfies:

```
𝔼[||∇F(wₜ)||²] ≤ O(1/T) + O(E²η²σ²) + O(E²η²γ²)
```

where T is the number of communication rounds, σ² measures data heterogeneity, and γ² measures client sampling variance.

This shows that:
1. More local epochs (E) can hurt convergence due to client drift
2. Data heterogeneity (σ²) directly impacts convergence
3. Client sampling introduces additional variance

## 2. Privacy-Preserving Distributed Learning Theory

Privacy preservation in federated learning involves multiple layers of protection, from cryptographic techniques to algorithmic privacy guarantees.

### Formal Privacy Models

#### Local Differential Privacy (LDP)

Each client satisfies ε-local differential privacy if for any two datasets D and D' differing in one record:

```
Pr[M(D) = o] ≤ e^ε · Pr[M(D') = o]
```

for all possible outputs o, where M is the randomization mechanism.

```python
class LocalDifferentialPrivacy:
    """
    Local differential privacy mechanisms for federated learning
    """
    
    def __init__(self, epsilon: float, sensitivity: float = 1.0):
        self.epsilon = epsilon
        self.sensitivity = sensitivity
        
    def laplace_mechanism(self, true_value: torch.Tensor) -> torch.Tensor:
        """
        Add Laplace noise for differential privacy
        
        Noise scale: Δf/ε where Δf is global sensitivity
        """
        noise_scale = self.sensitivity / self.epsilon
        noise = torch.from_numpy(
            np.random.laplace(0, noise_scale, true_value.shape)
        ).float()
        
        return true_value + noise
    
    def gaussian_mechanism(self, true_value: torch.Tensor, 
                          delta: float = 1e-5) -> torch.Tensor:
        """
        Add Gaussian noise for (ε, δ)-differential privacy
        
        Noise scale: √(2 ln(1.25/δ)) * Δf/ε
        """
        noise_scale = np.sqrt(2 * np.log(1.25 / delta)) * self.sensitivity / self.epsilon
        noise = torch.normal(0, noise_scale, size=true_value.shape)
        
        return true_value + noise
    
    def exponential_mechanism(self, candidates: List[torch.Tensor], 
                            scores: List[float]) -> torch.Tensor:
        """
        Select candidate based on exponential mechanism
        
        Probability ∝ exp(ε * score / 2Δf)
        """
        scaled_scores = [self.epsilon * score / (2 * self.sensitivity) 
                        for score in scores]
        
        # Numerical stability: subtract max
        max_score = max(scaled_scores)
        exp_scores = [np.exp(score - max_score) for score in scaled_scores]
        
        # Sample according to probabilities
        probabilities = exp_scores / np.sum(exp_scores)
        selected_idx = np.random.choice(len(candidates), p=probabilities)
        
        return candidates[selected_idx]

class DifferentiallyPrivateFedAvg:
    """
    Federated Averaging with differential privacy guarantees
    """
    
    def __init__(self, epsilon: float, delta: float = 1e-5, 
                 clipping_threshold: float = 1.0):
        self.epsilon = epsilon
        self.delta = delta
        self.clipping_threshold = clipping_threshold
        self.ldp = LocalDifferentialPrivacy(epsilon)
        
        # Privacy accounting
        self.privacy_spent = 0.0
        self.rounds_completed = 0
    
    def private_gradient_aggregation(self, client_gradients: List[torch.Tensor],
                                   client_weights: List[float]) -> torch.Tensor:
        """
        Aggregate gradients with differential privacy
        
        Steps:
        1. Clip individual gradients
        2. Add calibrated noise
        3. Perform weighted aggregation
        """
        
        # Step 1: Clip gradients to bound sensitivity
        clipped_gradients = []
        for grad in client_gradients:
            grad_norm = torch.norm(grad)
            if grad_norm > self.clipping_threshold:
                clipped_grad = grad * (self.clipping_threshold / grad_norm)
            else:
                clipped_grad = grad
            clipped_gradients.append(clipped_grad)
        
        # Step 2: Weighted aggregation
        total_weight = sum(client_weights)
        aggregated_grad = torch.zeros_like(clipped_gradients[0])
        
        for grad, weight in zip(clipped_gradients, client_weights):
            aggregated_grad += (weight / total_weight) * grad
        
        # Step 3: Add noise for differential privacy
        # Sensitivity is clipping_threshold / total_weight
        sensitivity = self.clipping_threshold
        noisy_grad = self.ldp.gaussian_mechanism(aggregated_grad, self.delta)
        
        # Update privacy accounting
        self._update_privacy_spent()
        
        return noisy_grad
    
    def _update_privacy_spent(self):
        """Update cumulative privacy expenditure"""
        # Simple composition: privacy cost accumulates linearly
        # In practice, use advanced composition theorems for tighter bounds
        self.privacy_spent += self.epsilon
        self.rounds_completed += 1
        
        if self.privacy_spent > 10.0:  # Example threshold
            raise PrivacyBudgetExhaustedException(
                f"Privacy budget exhausted: {self.privacy_spent}"
            )
    
    def get_privacy_metrics(self) -> Dict:
        """Get current privacy metrics"""
        return {
            'epsilon_spent': self.privacy_spent,
            'delta': self.delta,
            'rounds_completed': self.rounds_completed,
            'privacy_remaining': max(0, 10.0 - self.privacy_spent)
        }

class PrivacyBudgetExhaustedException(Exception):
    """Raised when privacy budget is exhausted"""
    pass
```

#### Rényi Differential Privacy (RDP)

RDP provides tighter composition bounds for iterative algorithms like SGD:

```python
class RenyiDifferentialPrivacy:
    """
    Rényi differential privacy for better composition bounds
    """
    
    def __init__(self, alpha: float = 2.0):
        self.alpha = alpha
        self.rdp_orders = [1 + x / 10.0 for x in range(1, 100)] + list(range(11, 64))
    
    def compute_rdp(self, q: float, noise_multiplier: float, steps: int) -> List[float]:
        """
        Compute RDP for Gaussian mechanism
        
        Args:
            q: Sampling probability
            noise_multiplier: Noise scale / sensitivity
            steps: Number of iterations
            
        Returns:
            List of RDP values for different orders
        """
        rdp = []
        
        for alpha in self.rdp_orders:
            if alpha == 1:
                rdp_alpha = float('inf')
            elif alpha == float('inf'):
                rdp_alpha = 0
            else:
                # RDP for Gaussian mechanism
                rdp_alpha = (q * alpha * (alpha - 1)) / (2 * noise_multiplier**2)
            
            rdp.append(steps * rdp_alpha)
        
        return rdp
    
    def rdp_to_dp(self, rdp: List[float], delta: float) -> float:
        """
        Convert RDP to (ε, δ)-DP using optimal conversion
        """
        eps = float('inf')
        
        for alpha, rdp_alpha in zip(self.rdp_orders, rdp):
            if alpha > 1 and rdp_alpha < float('inf'):
                eps = min(eps, rdp_alpha + np.log(delta) / (alpha - 1))
        
        return max(0, eps)

class PrivateAggregator:
    """
    Advanced private aggregation with multiple privacy mechanisms
    """
    
    def __init__(self, privacy_config: Dict):
        self.config = privacy_config
        self.rdp = RenyiDifferentialPrivacy()
        
        # Multiple aggregation strategies
        self.strategies = {
            'gaussian': self._gaussian_aggregation,
            'laplace': self._laplace_aggregation,
            'sparse': self._sparse_vector_aggregation
        }
    
    def aggregate(self, client_updates: List[torch.Tensor], 
                 strategy: str = 'gaussian') -> torch.Tensor:
        """
        Perform private aggregation using specified strategy
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return self.strategies[strategy](client_updates)
    
    def _gaussian_aggregation(self, updates: List[torch.Tensor]) -> torch.Tensor:
        """Gaussian mechanism for private aggregation"""
        # Clip updates
        clipped_updates = []
        for update in updates:
            norm = torch.norm(update)
            if norm > self.config['clipping_threshold']:
                clipped_updates.append(
                    update * self.config['clipping_threshold'] / norm
                )
            else:
                clipped_updates.append(update)
        
        # Average updates
        avg_update = torch.stack(clipped_updates).mean(dim=0)
        
        # Add Gaussian noise
        noise_scale = (self.config['clipping_threshold'] * 
                      np.sqrt(2 * np.log(1.25 / self.config['delta'])) / 
                      self.config['epsilon'])
        
        noise = torch.normal(0, noise_scale, size=avg_update.shape)
        
        return avg_update + noise
    
    def _sparse_vector_aggregation(self, updates: List[torch.Tensor]) -> torch.Tensor:
        """Sparse vector technique for private aggregation"""
        # Identify top-k coordinates across all updates
        k = self.config.get('sparsity_k', 100)
        threshold = self.config.get('sparse_threshold', 0.1)
        
        # Concatenate all updates to find global top-k
        all_updates = torch.cat([u.flatten() for u in updates])
        top_k_indices = torch.topk(torch.abs(all_updates), k).indices
        
        # Create sparse representation
        sparse_updates = []
        for update in updates:
            flat_update = update.flatten()
            sparse_update = torch.zeros_like(flat_update)
            
            # Keep only top-k coordinates above threshold
            for idx in top_k_indices:
                if torch.abs(flat_update[idx]) > threshold:
                    sparse_update[idx] = flat_update[idx]
            
            sparse_updates.append(sparse_update.reshape(update.shape))
        
        # Apply Gaussian mechanism to sparse updates
        return self._gaussian_aggregation(sparse_updates)
```

## 3. Secure Aggregation Protocols

Secure aggregation allows the server to compute aggregate statistics (like average model updates) without learning individual client contributions.

### Cryptographic Foundations

#### Shamir's Secret Sharing

```python
import random
from typing import List, Tuple
import numpy as np

class ShamirSecretSharing:
    """
    Shamir's Secret Sharing for secure aggregation
    """
    
    def __init__(self, threshold: int, num_parties: int, prime: int = 2**31 - 1):
        self.threshold = threshold
        self.num_parties = num_parties
        self.prime = prime
    
    def share_secret(self, secret: int) -> List[Tuple[int, int]]:
        """
        Share a secret among parties using polynomial interpolation
        
        Returns list of (party_id, share_value) tuples
        """
        # Generate random polynomial coefficients
        coefficients = [secret] + [random.randint(0, self.prime - 1) 
                                  for _ in range(self.threshold - 1)]
        
        # Evaluate polynomial at different points
        shares = []
        for party_id in range(1, self.num_parties + 1):
            share_value = self._evaluate_polynomial(coefficients, party_id)
            shares.append((party_id, share_value % self.prime))
        
        return shares
    
    def reconstruct_secret(self, shares: List[Tuple[int, int]]) -> int:
        """
        Reconstruct secret from threshold number of shares
        """
        if len(shares) < self.threshold:
            raise ValueError("Insufficient shares for reconstruction")
        
        # Use first 'threshold' shares
        shares = shares[:self.threshold]
        
        secret = 0
        for i, (xi, yi) in enumerate(shares):
            # Lagrange interpolation
            li = 1
            for j, (xj, _) in enumerate(shares):
                if i != j:
                    li = (li * (-xj) * pow(xi - xj, -1, self.prime)) % self.prime
            
            secret = (secret + yi * li) % self.prime
        
        return secret
    
    def _evaluate_polynomial(self, coefficients: List[int], x: int) -> int:
        """Evaluate polynomial at point x"""
        result = 0
        x_power = 1
        
        for coeff in coefficients:
            result = (result + coeff * x_power) % self.prime
            x_power = (x_power * x) % self.prime
        
        return result

class SecureAggregationProtocol:
    """
    Secure aggregation protocol for federated learning
    """
    
    def __init__(self, num_clients: int, threshold: int, 
                 dropout_resilience: int = None):
        self.num_clients = num_clients
        self.threshold = threshold
        self.dropout_resilience = dropout_resilience or (num_clients // 3)
        
        # Cryptographic components
        self.secret_sharing = ShamirSecretSharing(threshold, num_clients)
        self.client_keys = {}  # Store client public keys
        self.session_keys = {}  # Store session keys for each pair
        
        # Protocol state
        self.round_number = 0
        self.client_masks = {}
        self.aggregation_buffer = None
    
    def initialize_round(self, participating_clients: List[int]) -> Dict:
        """
        Initialize a new secure aggregation round
        
        Returns:
            Dictionary with round parameters for clients
        """
        self.round_number += 1
        self.participating_clients = participating_clients
        
        # Generate session parameters
        round_params = {
            'round_id': self.round_number,
            'participants': participating_clients,
            'threshold': self.threshold,
            'dropout_threshold': len(participating_clients) - self.dropout_resilience
        }
        
        return round_params
    
    def generate_client_masks(self, client_id: int, 
                            other_clients: List[int]) -> torch.Tensor:
        """
        Generate pairwise masks for secure aggregation
        
        Each client generates a mask for every other client using
        a pseudorandom function with shared keys
        """
        total_mask = torch.zeros(self.model_size)
        
        for other_client in other_clients:
            if other_client != client_id:
                # Generate pairwise mask using shared key
                shared_key = self._get_shared_key(client_id, other_client)
                pairwise_mask = self._generate_mask(shared_key, self.round_number)
                
                if other_client > client_id:
                    total_mask += pairwise_mask
                else:
                    total_mask -= pairwise_mask
        
        return total_mask
    
    def secure_aggregate(self, masked_updates: Dict[int, torch.Tensor],
                        dropout_clients: List[int] = None) -> torch.Tensor:
        """
        Perform secure aggregation of masked client updates
        
        Args:
            masked_updates: Dictionary of {client_id: masked_update}
            dropout_clients: List of clients that dropped out
            
        Returns:
            Aggregated model update without individual contributions
        """
        dropout_clients = dropout_clients or []
        
        # Check if we have enough participants
        active_clients = [c for c in self.participating_clients 
                         if c not in dropout_clients]
        
        if len(active_clients) < self.threshold:
            raise InsufficientParticipantsError(
                f"Only {len(active_clients)} participants, need {self.threshold}"
            )
        
        # Sum all masked updates
        aggregated_masked = torch.zeros_like(next(iter(masked_updates.values())))
        for client_id, masked_update in masked_updates.items():
            if client_id not in dropout_clients:
                aggregated_masked += masked_update
        
        # Reconstruct and subtract dropout masks
        dropout_mask_compensation = torch.zeros_like(aggregated_masked)
        
        for dropout_client in dropout_clients:
            # Reconstruct this client's mask using secret sharing
            client_mask = self._reconstruct_dropout_mask(
                dropout_client, active_clients
            )
            dropout_mask_compensation += client_mask
        
        # Final aggregated result (masks cancel out for active clients)
        final_aggregate = aggregated_masked - dropout_mask_compensation
        
        return final_aggregate / len(active_clients)
    
    def _get_shared_key(self, client1: int, client2: int) -> bytes:
        """Get shared key between two clients using key agreement"""
        # In practice, this would use Diffie-Hellman or similar
        # For simulation, we use a deterministic function
        key_material = f"{min(client1, client2)}:{max(client1, client2)}:{self.round_number}"
        return key_material.encode()
    
    def _generate_mask(self, key: bytes, round_id: int) -> torch.Tensor:
        """Generate pseudorandom mask using key and round ID"""
        # Use key and round_id as seed for reproducible randomness
        seed = hash(key + str(round_id).encode()) % (2**32)
        generator = torch.Generator()
        generator.manual_seed(seed)
        
        return torch.normal(0, 1, size=(self.model_size,), generator=generator)
    
    def _reconstruct_dropout_mask(self, dropout_client: int, 
                                 active_clients: List[int]) -> torch.Tensor:
        """
        Reconstruct the mask of a dropout client using secret shares
        from active clients
        """
        # This requires that each client secret-shares their mask components
        # Implementation would involve collecting shares from active clients
        # and reconstructing using Shamir's secret sharing
        
        # Placeholder implementation
        return torch.zeros(self.model_size)

class InsufficientParticipantsError(Exception):
    """Raised when not enough clients participate for secure aggregation"""
    pass
```

### Practical Secure Aggregation Implementation

```python
class PracticalSecureAggregation:
    """
    Practical secure aggregation protocol optimized for federated learning
    """
    
    def __init__(self, num_clients: int, security_parameter: int = 128):
        self.num_clients = num_clients
        self.security_parameter = security_parameter
        
        # Protocol phases
        self.phase = "initialization"
        self.client_states = {}
        
        # Cryptographic setup
        self._setup_cryptography()
    
    def _setup_cryptography(self):
        """Setup cryptographic primitives"""
        # Initialize public key infrastructure
        self.pki = PublicKeyInfrastructure(self.security_parameter)
        
        # Setup threshold encryption
        self.threshold_crypto = ThresholdEncryption(
            threshold=self.num_clients // 2 + 1,
            num_parties=self.num_clients
        )
    
    def run_secure_aggregation_round(self, client_updates: Dict[int, torch.Tensor],
                                   surviving_clients: List[int]) -> torch.Tensor:
        """
        Run complete secure aggregation round with four phases:
        1. Setup and key generation
        2. Masking and commitment
        3. Unmasking (if no dropouts) or reconstruction
        4. Final aggregation
        """
        
        # Phase 1: Setup
        self._phase_1_setup(surviving_clients)
        
        # Phase 2: Masked input collection
        masked_inputs = self._phase_2_masking(client_updates, surviving_clients)
        
        # Phase 3: Dropout handling and unmasking
        if len(surviving_clients) == self.num_clients:
            # No dropouts - direct unmasking
            result = self._phase_3_direct_unmasking(masked_inputs)
        else:
            # Handle dropouts with secret reconstruction
            result = self._phase_3_dropout_reconstruction(
                masked_inputs, surviving_clients
            )
        
        return result
    
    def _phase_1_setup(self, clients: List[int]):
        """Phase 1: Setup and key agreement"""
        self.phase = "setup"
        
        # Generate pairwise keys for all client pairs
        for i in clients:
            for j in clients:
                if i < j:  # Avoid duplicate pairs
                    shared_key = self.pki.generate_shared_key(i, j)
                    self.client_states[(i, j)] = shared_key
        
        # Setup threshold encryption keys
        public_key, key_shares = self.threshold_crypto.setup()
        self.threshold_public_key = public_key
        
        for client_id in clients:
            self.client_states[client_id] = {
                'threshold_key_share': key_shares[client_id],
                'pairwise_keys': {}
            }
    
    def _phase_2_masking(self, client_updates: Dict[int, torch.Tensor],
                        clients: List[int]) -> Dict[int, torch.Tensor]:
        """Phase 2: Collect masked inputs from clients"""
        self.phase = "masking"
        masked_inputs = {}
        
        for client_id in clients:
            if client_id in client_updates:
                # Generate client's total mask
                client_mask = self._generate_client_mask(client_id, clients)
                
                # Mask the client's update
                masked_update = client_updates[client_id] + client_mask
                masked_inputs[client_id] = masked_update
        
        return masked_inputs
    
    def _phase_3_direct_unmasking(self, masked_inputs: Dict[int, torch.Tensor]) -> torch.Tensor:
        """Phase 3: Direct unmasking when no dropouts occur"""
        self.phase = "unmasking"
        
        # Sum all masked inputs - masks cancel out due to pairwise construction
        total = torch.zeros_like(next(iter(masked_inputs.values())))
        
        for masked_input in masked_inputs.values():
            total += masked_input
        
        # Average across clients
        return total / len(masked_inputs)
    
    def _phase_3_dropout_reconstruction(self, masked_inputs: Dict[int, torch.Tensor],
                                      surviving_clients: List[int]) -> torch.Tensor:
        """Phase 3: Handle dropouts with secret reconstruction"""
        self.phase = "reconstruction"
        
        # Sum surviving client inputs
        surviving_sum = torch.zeros_like(next(iter(masked_inputs.values())))
        for client_id in surviving_clients:
            if client_id in masked_inputs:
                surviving_sum += masked_inputs[client_id]
        
        # Reconstruct dropout contributions using threshold cryptography
        all_clients = set(range(self.num_clients))
        dropout_clients = all_clients - set(surviving_clients)
        
        dropout_compensation = torch.zeros_like(surviving_sum)
        
        for dropout_client in dropout_clients:
            # Reconstruct this client's mask contribution
            mask_shares = []
            for surviving_client in surviving_clients:
                if surviving_client in self.client_states:
                    share = self._get_mask_share(dropout_client, surviving_client)
                    mask_shares.append(share)
            
            # Use threshold decryption to reconstruct mask
            reconstructed_mask = self.threshold_crypto.decrypt_shares(mask_shares)
            dropout_compensation += reconstructed_mask
        
        # Final result: surviving inputs minus reconstructed dropout masks
        result = surviving_sum - dropout_compensation
        return result / len(surviving_clients)
    
    def _generate_client_mask(self, client_id: int, all_clients: List[int]) -> torch.Tensor:
        """Generate the total mask for a client"""
        total_mask = torch.zeros(self.model_size)
        
        for other_client in all_clients:
            if other_client != client_id:
                # Get shared key
                pair_key = self.client_states.get((min(client_id, other_client), 
                                                  max(client_id, other_client)))
                
                if pair_key:
                    # Generate pairwise mask
                    pairwise_mask = self._prg(pair_key, self.model_size)
                    
                    # Add or subtract based on client ID ordering
                    if client_id < other_client:
                        total_mask += pairwise_mask
                    else:
                        total_mask -= pairwise_mask
        
        return total_mask
    
    def _prg(self, seed: bytes, length: int) -> torch.Tensor:
        """Pseudorandom generator for mask generation"""
        # Use seed to generate deterministic random tensor
        generator = torch.Generator()
        generator.manual_seed(int.from_bytes(seed[:4], 'big'))
        
        return torch.normal(0, 1, size=(length,), generator=generator)
    
    def _get_mask_share(self, dropout_client: int, surviving_client: int) -> bytes:
        """Get mask share from surviving client for dropout reconstruction"""
        # This would involve the surviving client computing and returning
        # a share of the dropout client's mask for reconstruction
        # Placeholder implementation
        return b"mock_share"

class PublicKeyInfrastructure:
    """Mock PKI for secure aggregation"""
    
    def __init__(self, security_parameter: int):
        self.security_parameter = security_parameter
        self.client_keys = {}
    
    def generate_shared_key(self, client1: int, client2: int) -> bytes:
        """Generate shared key between two clients"""
        # Mock implementation - in practice, use ECDH or similar
        key_material = f"shared_key_{min(client1, client2)}_{max(client1, client2)}"
        return key_material.encode()

class ThresholdEncryption:
    """Threshold encryption for secure aggregation"""
    
    def __init__(self, threshold: int, num_parties: int):
        self.threshold = threshold
        self.num_parties = num_parties
    
    def setup(self) -> Tuple[bytes, Dict[int, bytes]]:
        """Setup threshold encryption scheme"""
        public_key = b"mock_public_key"
        key_shares = {i: f"key_share_{i}".encode() 
                     for i in range(self.num_parties)}
        
        return public_key, key_shares
    
    def decrypt_shares(self, shares: List[bytes]) -> torch.Tensor:
        """Decrypt using threshold number of shares"""
        # Mock implementation
        return torch.zeros(1000)  # Placeholder tensor
```

## 4. Differential Privacy in Federated Settings

Differential privacy in federated learning operates at multiple levels: local privacy at each client and global privacy for the aggregated model.

### Multi-Level Privacy Framework

```python
class FederatedDifferentialPrivacy:
    """
    Multi-level differential privacy for federated learning
    
    Provides privacy guarantees at:
    1. Local level (each client's contribution)
    2. Global level (aggregated model)
    3. Central level (server-side operations)
    """
    
    def __init__(self, local_epsilon: float, global_epsilon: float,
                 delta: float = 1e-5, clipping_threshold: float = 1.0):
        
        self.local_epsilon = local_epsilon
        self.global_epsilon = global_epsilon
        self.delta = delta
        self.clipping_threshold = clipping_threshold
        
        # Privacy accountants
        self.local_accountant = PrivacyAccountant(local_epsilon, delta)
        self.global_accountant = PrivacyAccountant(global_epsilon, delta)
        
        # Advanced composition tracking
        self.rdp_orders = [1 + x / 10.0 for x in range(1, 100)] + list(range(11, 64))
        self.local_rdp_budget = {order: [] for order in self.rdp_orders}
        self.global_rdp_budget = {order: [] for order in self.rdp_orders}
    
    def local_privacy_mechanism(self, client_gradient: torch.Tensor,
                               mechanism: str = 'gaussian') -> torch.Tensor:
        """
        Apply local differential privacy to client gradient
        
        Args:
            client_gradient: Client's computed gradient
            mechanism: Privacy mechanism ('gaussian', 'laplace', 'sparse')
            
        Returns:
            Privatized gradient
        """
        
        # Step 1: Gradient clipping for bounded sensitivity
        clipped_gradient = self._clip_gradient(client_gradient)
        
        # Step 2: Apply privacy mechanism
        if mechanism == 'gaussian':
            private_gradient = self._gaussian_mechanism(clipped_gradient, 
                                                      self.local_epsilon, 
                                                      self.delta)
        elif mechanism == 'laplace':
            private_gradient = self._laplace_mechanism(clipped_gradient, 
                                                     self.local_epsilon)
        elif mechanism == 'sparse':
            private_gradient = self._sparse_mechanism(clipped_gradient, 
                                                    self.local_epsilon)
        else:
            raise ValueError(f"Unknown mechanism: {mechanism}")
        
        # Step 3: Update privacy accounting
        self.local_accountant.step(self.local_epsilon)
        
        return private_gradient
    
    def global_privacy_mechanism(self, aggregated_gradient: torch.Tensor,
                                num_participants: int) -> torch.Tensor:
        """
        Apply global differential privacy to aggregated gradient
        
        This provides additional privacy protection at the server level
        """
        
        # Scale noise based on number of participants
        effective_sensitivity = self.clipping_threshold / num_participants
        
        # Apply global privacy mechanism
        noise_scale = effective_sensitivity * np.sqrt(2 * np.log(1.25 / self.delta)) / self.global_epsilon
        noise = torch.normal(0, noise_scale, size=aggregated_gradient.shape)
        
        private_aggregated = aggregated_gradient + noise
        
        # Update global privacy accounting
        self.global_accountant.step(self.global_epsilon)
        
        return private_aggregated
    
    def adaptive_privacy_allocation(self, round_number: int, 
                                  total_rounds: int, 
                                  importance_weights: torch.Tensor = None) -> Tuple[float, float]:
        """
        Adaptively allocate privacy budget across training rounds
        
        Uses different strategies:
        1. Uniform allocation
        2. Decreasing allocation (more privacy early)
        3. Importance-weighted allocation
        """
        
        remaining_rounds = total_rounds - round_number
        
        if importance_weights is not None:
            # Importance-weighted allocation
            current_weight = importance_weights[round_number]
            remaining_weights = importance_weights[round_number:].sum()
            
            local_epsilon_round = self.local_epsilon * (current_weight / remaining_weights)
            global_epsilon_round = self.global_epsilon * (current_weight / remaining_weights)
        
        else:
            # Uniform allocation
            local_epsilon_round = self.local_epsilon / total_rounds
            global_epsilon_round = self.global_epsilon / total_rounds
        
        return local_epsilon_round, global_epsilon_round
    
    def _clip_gradient(self, gradient: torch.Tensor) -> torch.Tensor:
        """Clip gradient to bound L2 sensitivity"""
        gradient_norm = torch.norm(gradient)
        if gradient_norm > self.clipping_threshold:
            return gradient * (self.clipping_threshold / gradient_norm)
        return gradient
    
    def _gaussian_mechanism(self, value: torch.Tensor, epsilon: float, 
                          delta: float) -> torch.Tensor:
        """Gaussian mechanism for (ε, δ)-differential privacy"""
        sensitivity = self.clipping_threshold
        noise_scale = sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / epsilon
        noise = torch.normal(0, noise_scale, size=value.shape)
        return value + noise
    
    def _laplace_mechanism(self, value: torch.Tensor, epsilon: float) -> torch.Tensor:
        """Laplace mechanism for ε-differential privacy"""
        sensitivity = self.clipping_threshold
        noise_scale = sensitivity / epsilon
        noise = torch.from_numpy(
            np.random.laplace(0, noise_scale, value.shape)
        ).float()
        return value + noise
    
    def _sparse_mechanism(self, gradient: torch.Tensor, epsilon: float) -> torch.Tensor:
        """Sparse vector technique for high-dimensional gradients"""
        
        # Parameters for sparse vector technique
        k = min(100, gradient.numel() // 10)  # Top-k elements
        threshold = 0.1  # Threshold for selection
        
        # Flatten gradient for processing
        flat_gradient = gradient.flatten()
        
        # Find top-k coordinates
        top_k_values, top_k_indices = torch.topk(torch.abs(flat_gradient), k)
        
        # Apply exponential mechanism to select coordinates above threshold
        selected_indices = []
        remaining_budget = epsilon
        
        for i, (value, idx) in enumerate(zip(top_k_values, top_k_indices)):
            if value > threshold and remaining_budget > 0:
                # Use exponential mechanism
                score = value.item()
                prob = np.exp(remaining_budget * score / (2 * self.clipping_threshold))
                
                if np.random.random() < prob / (1 + prob):
                    selected_indices.append(idx)
                    remaining_budget -= epsilon / k
        
        # Create sparse gradient
        sparse_gradient = torch.zeros_like(flat_gradient)
        for idx in selected_indices:
            # Add noise to selected coordinates
            noise = np.random.laplace(0, 2 * self.clipping_threshold / remaining_budget) if remaining_budget > 0 else 0
            sparse_gradient[idx] = flat_gradient[idx] + noise
        
        return sparse_gradient.reshape(gradient.shape)

class PrivacyAccountant:
    """
    Privacy accountant for tracking cumulative privacy loss
    """
    
    def __init__(self, total_epsilon: float, delta: float):
        self.total_epsilon = total_epsilon
        self.delta = delta
        self.spent_epsilon = 0.0
        self.step_count = 0
        
        # Advanced composition bounds
        self.rdp_orders = [1 + x / 10.0 for x in range(1, 100)] + list(range(11, 64))
        self.rdp_budget = [0.0] * len(self.rdp_orders)
    
    def step(self, epsilon_step: float, mechanism: str = 'gaussian') -> bool:
        """
        Account for one step of privacy expenditure
        
        Returns:
            True if privacy budget allows this step, False otherwise
        """
        
        if mechanism == 'gaussian':
            # Use RDP accounting for better composition
            self._update_rdp_budget(epsilon_step)
            current_epsilon = self._rdp_to_dp()
        else:
            # Basic composition
            current_epsilon = self.spent_epsilon + epsilon_step
        
        if current_epsilon <= self.total_epsilon:
            self.spent_epsilon = current_epsilon
            self.step_count += 1
            return True
        else:
            return False
    
    def _update_rdp_budget(self, epsilon_step: float):
        """Update RDP budget for Gaussian mechanism"""
        # Convert epsilon to noise multiplier
        noise_multiplier = np.sqrt(2 * np.log(1.25 / self.delta)) / epsilon_step
        
        # Update RDP for each order
        for i, alpha in enumerate(self.rdp_orders):
            if alpha > 1:
                rdp_alpha = 1 / (2 * noise_multiplier**2) if alpha == 2 else (alpha * (alpha - 1)) / (2 * noise_multiplier**2)
                self.rdp_budget[i] += rdp_alpha
    
    def _rdp_to_dp(self) -> float:
        """Convert RDP to (ε, δ)-DP"""
        epsilon = float('inf')
        
        for alpha, rdp_alpha in zip(self.rdp_orders, self.rdp_budget):
            if alpha > 1 and rdp_alpha < float('inf'):
                eps_alpha = rdp_alpha + np.log(self.delta) / (alpha - 1)
                epsilon = min(epsilon, eps_alpha)
        
        return max(0, epsilon)
    
    def get_privacy_metrics(self) -> Dict:
        """Get current privacy metrics"""
        return {
            'spent_epsilon': self.spent_epsilon,
            'remaining_epsilon': max(0, self.total_epsilon - self.spent_epsilon),
            'delta': self.delta,
            'steps_taken': self.step_count,
            'rdp_budget': dict(zip(self.rdp_orders, self.rdp_budget))
        }

class AdaptiveNoiseScheduler:
    """
    Adaptive noise scheduler for federated learning with differential privacy
    """
    
    def __init__(self, initial_noise: float, decay_rate: float = 0.95,
                 min_noise: float = 0.01):
        self.initial_noise = initial_noise
        self.decay_rate = decay_rate
        self.min_noise = min_noise
        
        # Adaptation parameters
        self.loss_history = []
        self.noise_history = []
        self.performance_threshold = 0.1  # 10% performance drop threshold
    
    def get_noise_multiplier(self, round_number: int, current_loss: float,
                           baseline_loss: float = None) -> float:
        """
        Compute adaptive noise multiplier based on training progress
        
        Args:
            round_number: Current training round
            current_loss: Current model loss
            baseline_loss: Baseline loss (without privacy)
            
        Returns:
            Noise multiplier for this round
        """
        
        # Base noise with exponential decay
        base_noise = max(
            self.min_noise,
            self.initial_noise * (self.decay_rate ** round_number)
        )
        
        # Performance-based adaptation
        if baseline_loss is not None and len(self.loss_history) > 5:
            # Check if performance is degrading significantly
            recent_avg_loss = np.mean(self.loss_history[-5:])
            performance_ratio = recent_avg_loss / baseline_loss
            
            if performance_ratio > (1 + self.performance_threshold):
                # Performance is degrading, reduce noise
                adaptation_factor = 0.8
            elif performance_ratio < (1 + self.performance_threshold / 2):
                # Performance is good, can afford more noise
                adaptation_factor = 1.1
            else:
                adaptation_factor = 1.0
            
            adaptive_noise = base_noise * adaptation_factor
        else:
            adaptive_noise = base_noise
        
        # Record history
        self.loss_history.append(current_loss)
        self.noise_history.append(adaptive_noise)
        
        # Keep only recent history
        if len(self.loss_history) > 100:
            self.loss_history = self.loss_history[-50:]
            self.noise_history = self.noise_history[-50:]
        
        return adaptive_noise
    
    def analyze_privacy_utility_tradeoff(self) -> Dict:
        """
        Analyze the privacy-utility tradeoff over training rounds
        """
        if len(self.loss_history) < 10:
            return {"error": "Insufficient history for analysis"}
        
        # Compute correlation between noise and loss
        correlation = np.corrcoef(self.noise_history, self.loss_history)[0, 1]
        
        # Compute privacy cost (cumulative noise)
        cumulative_privacy_cost = np.cumsum(self.noise_history)
        
        # Find optimal noise level (minimize loss while preserving privacy)
        loss_improvement = np.diff(self.loss_history)
        noise_increase = np.diff(self.noise_history)
        
        efficiency_ratios = []
        for i in range(len(loss_improvement)):
            if noise_increase[i] != 0:
                efficiency_ratios.append(abs(loss_improvement[i]) / abs(noise_increase[i]))
        
        return {
            'noise_loss_correlation': correlation,
            'cumulative_privacy_cost': cumulative_privacy_cost[-1],
            'average_efficiency_ratio': np.mean(efficiency_ratios) if efficiency_ratios else 0,
            'recommended_noise': np.median(self.noise_history),
            'privacy_regret': sum(max(0, n - self.min_noise) for n in self.noise_history)
        }
```

This covers the foundations, privacy-preserving theory, secure aggregation protocols, and differential privacy mechanisms in federated learning. The episode would continue with sections on communication efficiency, non-IID data challenges, federated learning algorithms, production systems, security threats, and future directions, maintaining the same level of mathematical rigor and practical implementation detail.

Would you like me to continue with the remaining sections of Episode 142 or proceed to create the other episodes?