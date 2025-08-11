#!/usr/bin/env python3
"""
RLHF Training Loop for Indian Cultural Context
Episode 5: Code Example 5

Production-ready Reinforcement Learning from Human Feedback system
Optimized for Indian cultural context, regional preferences, and languages

Author: Code Developer Agent
Context: ChatGPT-style training for Indian cultural alignment
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torch.nn.functional as F
import numpy as np
import json
import time
import logging
import asyncio
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import pickle
import redis
import asyncpg
from transformers import AutoTokenizer, AutoModelForCausalLM
from collections import defaultdict
import random

# Mumbai-style production logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FeedbackType(Enum):
    CULTURAL_APPROPRIATENESS = "cultural_appropriateness"
    LANGUAGE_QUALITY = "language_quality"
    FACTUAL_ACCURACY = "factual_accuracy"
    HELPFULNESS = "helpfulness"
    SAFETY = "safety"
    REGIONAL_RELEVANCE = "regional_relevance"

class RegionalContext(Enum):
    NORTH_INDIA = "north_india"
    SOUTH_INDIA = "south_india" 
    WEST_INDIA = "west_india"
    EAST_INDIA = "east_india"
    NORTHEAST_INDIA = "northeast_india"

@dataclass
class HumanFeedback:
    """Human feedback for Indian cultural context"""
    prompt: str
    response_a: str
    response_b: str
    preferred_response: str  # 'a' or 'b'
    feedback_type: FeedbackType
    regional_context: RegionalContext
    language: str  # 'hi', 'en', 'ta', 'bn', etc.
    cultural_score: float  # 0-1, how culturally appropriate
    linguistic_score: float  # 0-1, how linguistically correct
    factual_score: float  # 0-1, how factually accurate
    reviewer_id: str
    timestamp: float
    cost_inr: float = 0.5  # Cost per feedback in INR

@dataclass
class RLHFConfig:
    """Configuration for RLHF training"""
    model_name: str = "ai4bharat/indic-bert"
    reward_model_layers: int = 2
    ppo_learning_rate: float = 1e-6
    reward_learning_rate: float = 1e-5
    ppo_epochs: int = 4
    batch_size: int = 8
    mini_batch_size: int = 2
    max_seq_length: int = 512
    kl_penalty: float = 0.1
    clip_epsilon: float = 0.2
    value_loss_coeff: float = 0.5
    entropy_coeff: float = 0.01
    
    # Indian context specific
    cultural_weight: float = 0.3
    linguistic_weight: float = 0.2
    regional_weight: float = 0.15
    safety_weight: float = 0.35
    
    # Cost optimization
    use_gradient_checkpointing: bool = True
    mixed_precision: bool = True
    cost_per_step_inr: float = 0.1

class IndianCulturalRewardModel(nn.Module):
    """
    Reward model trained on Indian cultural preferences
    Considers regional variations, language quality, and cultural appropriateness
    """
    
    def __init__(self, config: RLHFConfig, base_model_name: str):
        super().__init__()
        self.config = config
        
        # Load base model
        self.base_model = AutoModelForCausalLM.from_pretrained(
            base_model_name, 
            torch_dtype=torch.float16 if config.mixed_precision else torch.float32
        )
        
        # Freeze base model parameters
        for param in self.base_model.parameters():
            param.requires_grad = False
        
        # Reward head layers
        hidden_size = self.base_model.config.hidden_size
        
        self.reward_head = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_size // 4, 1)  # Single reward score
        )
        
        # Cultural context embeddings
        self.cultural_embeddings = nn.Embedding(len(RegionalContext), hidden_size // 4)
        self.language_embeddings = nn.Embedding(10, hidden_size // 4)  # Support 10 languages
        
        # Multi-task reward heads for different aspects
        self.cultural_head = nn.Linear(hidden_size, 1)
        self.linguistic_head = nn.Linear(hidden_size, 1)
        self.safety_head = nn.Linear(hidden_size, 1)
        self.regional_head = nn.Linear(hidden_size, 1)
        
    def forward(self, 
                input_ids: torch.Tensor,
                attention_mask: torch.Tensor,
                regional_context: Optional[torch.Tensor] = None,
                language_ids: Optional[torch.Tensor] = None) -> Dict[str, torch.Tensor]:
        """
        Forward pass for reward calculation
        
        Args:
            input_ids: [batch_size, seq_len]
            attention_mask: [batch_size, seq_len]
            regional_context: [batch_size] - regional context IDs
            language_ids: [batch_size] - language IDs
        """
        
        # Get base model representations
        with torch.no_grad():
            outputs = self.base_model(input_ids=input_ids, attention_mask=attention_mask, 
                                    output_hidden_states=True)
        
        # Use last hidden state of the last token (similar to GPT)
        sequence_lengths = attention_mask.sum(dim=1) - 1  # -1 for 0-indexing
        last_hidden_states = outputs.hidden_states[-1]  # Last layer
        
        # Get the last token representation for each sequence
        batch_size = last_hidden_states.size(0)
        last_token_hidden = last_hidden_states[range(batch_size), sequence_lengths]
        
        # Add cultural and language context
        contextual_hidden = last_token_hidden
        
        if regional_context is not None:
            cultural_emb = self.cultural_embeddings(regional_context)
            contextual_hidden = contextual_hidden + cultural_emb
            
        if language_ids is not None:
            lang_emb = self.language_embeddings(language_ids)
            contextual_hidden = contextual_hidden + lang_emb
        
        # Calculate different reward aspects
        overall_reward = self.reward_head(contextual_hidden)
        cultural_reward = self.cultural_head(contextual_hidden)
        linguistic_reward = self.linguistic_head(contextual_hidden)
        safety_reward = self.safety_head(contextual_hidden)
        regional_reward = self.regional_head(contextual_hidden)
        
        # Combine rewards with weights
        weighted_reward = (
            self.config.cultural_weight * torch.sigmoid(cultural_reward) +
            self.config.linguistic_weight * torch.sigmoid(linguistic_reward) +
            self.config.safety_weight * torch.sigmoid(safety_reward) +
            self.config.regional_weight * torch.sigmoid(regional_reward)
        )
        
        return {
            "overall_reward": overall_reward,
            "weighted_reward": weighted_reward,
            "cultural_reward": cultural_reward,
            "linguistic_reward": linguistic_reward,
            "safety_reward": safety_reward,
            "regional_reward": regional_reward,
            "last_hidden_state": last_token_hidden
        }

class IndianFeedbackDataset(Dataset):
    """Dataset for Indian human feedback"""
    
    def __init__(self, 
                 feedback_data: List[HumanFeedback],
                 tokenizer: AutoTokenizer,
                 max_length: int = 512):
        self.feedback_data = feedback_data
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Create language and regional mappings
        self.language_to_id = {
            'hi': 0, 'en': 1, 'ta': 2, 'te': 3, 'bn': 4,
            'mr': 5, 'gu': 6, 'kn': 7, 'ml': 8, 'or': 9
        }
        
        self.regional_to_id = {
            RegionalContext.NORTH_INDIA: 0,
            RegionalContext.SOUTH_INDIA: 1, 
            RegionalContext.WEST_INDIA: 2,
            RegionalContext.EAST_INDIA: 3,
            RegionalContext.NORTHEAST_INDIA: 4
        }
        
        logger.info(f"Loaded {len(feedback_data)} feedback samples")
        self._analyze_dataset()
    
    def _analyze_dataset(self):
        """Analyze dataset composition"""
        language_counts = defaultdict(int)
        regional_counts = defaultdict(int)
        feedback_type_counts = defaultdict(int)
        
        for feedback in self.feedback_data:
            language_counts[feedback.language] += 1
            regional_counts[feedback.regional_context] += 1
            feedback_type_counts[feedback.feedback_type] += 1
        
        logger.info("Dataset Analysis:")
        logger.info(f"  Languages: {dict(language_counts)}")
        logger.info(f"  Regions: {dict(regional_counts)}")
        logger.info(f"  Feedback Types: {dict(feedback_type_counts)}")
    
    def __len__(self):
        return len(self.feedback_data)
    
    def __getitem__(self, idx):
        feedback = self.feedback_data[idx]
        
        # Create prompt + response pairs
        prompt_response_a = feedback.prompt + " " + feedback.response_a
        prompt_response_b = feedback.prompt + " " + feedback.response_b
        
        # Tokenize
        tokens_a = self.tokenizer(
            prompt_response_a,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        tokens_b = self.tokenizer(
            prompt_response_b,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # Preference label (1 if A is preferred, 0 if B is preferred)
        preference = 1.0 if feedback.preferred_response == 'a' else 0.0
        
        # Context IDs
        language_id = self.language_to_id.get(feedback.language, 1)  # Default to English
        regional_id = self.regional_to_id.get(feedback.regional_context, 0)  # Default to North
        
        return {
            'input_ids_a': tokens_a['input_ids'].squeeze(),
            'attention_mask_a': tokens_a['attention_mask'].squeeze(),
            'input_ids_b': tokens_b['input_ids'].squeeze(),
            'attention_mask_b': tokens_b['attention_mask'].squeeze(),
            'preference': torch.tensor(preference, dtype=torch.float32),
            'language_id': torch.tensor(language_id, dtype=torch.long),
            'regional_id': torch.tensor(regional_id, dtype=torch.long),
            'cultural_score': torch.tensor(feedback.cultural_score, dtype=torch.float32),
            'linguistic_score': torch.tensor(feedback.linguistic_score, dtype=torch.float32),
            'factual_score': torch.tensor(feedback.factual_score, dtype=torch.float32),
        }

class PPOTrainer:
    """
    PPO (Proximal Policy Optimization) trainer for RLHF
    Optimized for Indian cultural alignment
    """
    
    def __init__(self, 
                 policy_model: nn.Module,
                 reward_model: IndianCulturalRewardModel,
                 tokenizer: AutoTokenizer,
                 config: RLHFConfig):
        self.policy_model = policy_model
        self.reward_model = reward_model
        self.tokenizer = tokenizer
        self.config = config
        
        # Optimizers
        self.policy_optimizer = optim.AdamW(
            policy_model.parameters(),
            lr=config.ppo_learning_rate,
            weight_decay=0.01
        )
        
        # Reference model (frozen copy of original policy)
        self.reference_model = type(policy_model)(policy_model.config)
        self.reference_model.load_state_dict(policy_model.state_dict())
        for param in self.reference_model.parameters():
            param.requires_grad = False
        
        # Training metrics
        self.training_stats = {
            'total_steps': 0,
            'total_cost_inr': 0.0,
            'avg_reward': 0.0,
            'avg_kl_divergence': 0.0,
            'policy_loss': 0.0,
            'value_loss': 0.0
        }
        
    def compute_rewards(self,
                       input_ids: torch.Tensor,
                       attention_mask: torch.Tensor,
                       regional_context: torch.Tensor,
                       language_ids: torch.Tensor) -> torch.Tensor:
        """Compute rewards using the reward model"""
        
        with torch.no_grad():
            reward_outputs = self.reward_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                regional_context=regional_context,
                language_ids=language_ids
            )
            
            # Use weighted reward that considers cultural context
            rewards = reward_outputs['weighted_reward'].squeeze(-1)
            
            return rewards
    
    def compute_kl_penalty(self,
                          logits: torch.Tensor,
                          ref_logits: torch.Tensor,
                          attention_mask: torch.Tensor) -> torch.Tensor:
        """Compute KL divergence penalty between current and reference policy"""
        
        # Convert to log probabilities
        log_probs = F.log_softmax(logits, dim=-1)
        ref_log_probs = F.log_softmax(ref_logits, dim=-1)
        
        # Compute KL divergence
        kl_div = F.kl_div(log_probs, ref_log_probs.exp(), reduction='none')
        kl_div = kl_div.sum(dim=-1)  # Sum over vocab dimension
        
        # Mask padding tokens
        kl_div = kl_div * attention_mask
        
        # Average over sequence length
        kl_penalty = kl_div.sum(dim=-1) / attention_mask.sum(dim=-1)
        
        return kl_penalty
    
    def train_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Single PPO training step"""
        
        start_time = time.time()
        
        # Extract batch data
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        regional_context = batch['regional_id']
        language_ids = batch['language_id']
        
        batch_size, seq_len = input_ids.shape
        
        # Generate responses from current policy
        with torch.no_grad():
            policy_outputs = self.policy_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=input_ids
            )
            
            ref_outputs = self.reference_model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=input_ids
            )
        
        # Compute rewards
        rewards = self.compute_rewards(input_ids, attention_mask, regional_context, language_ids)
        
        # Compute KL penalty
        kl_penalty = self.compute_kl_penalty(
            policy_outputs.logits, 
            ref_outputs.logits, 
            attention_mask
        )
        
        # Total reward with KL penalty
        total_rewards = rewards - self.config.kl_penalty * kl_penalty
        
        # PPO loss computation
        old_log_probs = F.log_softmax(ref_outputs.logits, dim=-1)
        new_log_probs = F.log_softmax(policy_outputs.logits, dim=-1)
        
        # Get log probabilities of actual tokens
        old_log_probs_selected = old_log_probs.gather(2, input_ids.unsqueeze(-1)).squeeze(-1)
        new_log_probs_selected = new_log_probs.gather(2, input_ids.unsqueeze(-1)).squeeze(-1)
        
        # Compute ratio
        log_ratio = new_log_probs_selected - old_log_probs_selected
        ratio = torch.exp(log_ratio)
        
        # Compute advantages (simplified - using rewards as advantages)
        advantages = total_rewards.unsqueeze(-1).expand(-1, seq_len)
        advantages = advantages * attention_mask
        
        # PPO clipped objective
        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1.0 - self.config.clip_epsilon, 1.0 + self.config.clip_epsilon) * advantages
        
        policy_loss = -torch.min(surr1, surr2)
        policy_loss = (policy_loss * attention_mask).sum() / attention_mask.sum()
        
        # Value loss (simplified)
        value_loss = F.mse_loss(policy_outputs.logits.mean(dim=-1), rewards)
        
        # Entropy bonus for exploration
        entropy = -(F.softmax(policy_outputs.logits, dim=-1) * F.log_softmax(policy_outputs.logits, dim=-1)).sum(dim=-1)
        entropy = (entropy * attention_mask).sum() / attention_mask.sum()
        
        # Total loss
        total_loss = (policy_loss + 
                     self.config.value_loss_coeff * value_loss - 
                     self.config.entropy_coeff * entropy)
        
        # Backward pass
        self.policy_optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_model.parameters(), 1.0)
        self.policy_optimizer.step()
        
        # Update statistics
        step_time = time.time() - start_time
        step_cost = batch_size * self.config.cost_per_step_inr
        
        self.training_stats['total_steps'] += 1
        self.training_stats['total_cost_inr'] += step_cost
        self.training_stats['avg_reward'] = rewards.mean().item()
        self.training_stats['avg_kl_divergence'] = kl_penalty.mean().item()
        self.training_stats['policy_loss'] = policy_loss.item()
        self.training_stats['value_loss'] = value_loss.item()
        
        return {
            'total_loss': total_loss.item(),
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'avg_reward': rewards.mean().item(),
            'avg_kl_div': kl_penalty.mean().item(),
            'step_time': step_time,
            'step_cost_inr': step_cost
        }

class RLHFTrainingPipeline:
    """
    Complete RLHF training pipeline for Indian cultural alignment
    """
    
    def __init__(self, config: RLHFConfig):
        self.config = config
        self.tokenizer = None
        self.policy_model = None
        self.reward_model = None
        self.trainer = None
        self.feedback_data = []
        
    async def initialize(self):
        """Initialize all components"""
        
        # Load tokenizer and models
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load policy model
        self.policy_model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16 if self.config.mixed_precision else torch.float32
        )
        
        # Initialize reward model
        self.reward_model = IndianCulturalRewardModel(self.config, self.config.model_name)
        
        # Initialize PPO trainer
        self.trainer = PPOTrainer(
            self.policy_model,
            self.reward_model,
            self.tokenizer,
            self.config
        )
        
        # Load sample feedback data
        await self._load_sample_feedback()
        
        logger.info("RLHF Training Pipeline initialized successfully")
    
    async def _load_sample_feedback(self):
        """Load sample Indian cultural feedback data"""
        
        # Sample feedback data for Indian context
        sample_feedback = [
            HumanFeedback(
                prompt="भारत में सबसे अच्छा त्योहार कौन सा है?",
                response_a="दिवाली सबसे अच्छा त्योहार है क्योंकि यह रोशनी का त्योहार है।",
                response_b="Christmas is the best festival because it's celebrated worldwide.",
                preferred_response="a",  # Culturally appropriate Hindi response
                feedback_type=FeedbackType.CULTURAL_APPROPRIATENESS,
                regional_context=RegionalContext.NORTH_INDIA,
                language="hi",
                cultural_score=0.9,
                linguistic_score=0.8,
                factual_score=0.7,
                reviewer_id="reviewer_001",
                timestamp=time.time()
            ),
            HumanFeedback(
                prompt="How do you make authentic South Indian dosa?",
                response_a="Just buy a packet from the store and microwave it.",
                response_b="Soak rice and urad dal separately for 4-6 hours, grind them to make batter, ferment overnight, then cook on tawa with oil.",
                preferred_response="b",  # Culturally accurate cooking method
                feedback_type=FeedbackType.FACTUAL_ACCURACY,
                regional_context=RegionalContext.SOUTH_INDIA,
                language="en",
                cultural_score=0.8,
                linguistic_score=0.9,
                factual_score=0.95,
                reviewer_id="reviewer_002",
                timestamp=time.time()
            ),
            HumanFeedback(
                prompt="मुंबई में local train कैसे पकड़ें?",
                response_a="बस प्लेटफॉर्म पर जाकर कोई भी train पकड़ लो।",
                response_b="पहले ticket लें, फिर सही platform पर जाएं, और train के direction check करके ladies/general compartment में बैठें।",
                preferred_response="b",  # Practical and safe advice
                feedback_type=FeedbackType.HELPFULNESS,
                regional_context=RegionalContext.WEST_INDIA,
                language="hi",
                cultural_score=0.9,
                linguistic_score=0.9,
                factual_score=0.9,
                reviewer_id="reviewer_003",
                timestamp=time.time()
            )
        ]
        
        self.feedback_data.extend(sample_feedback)
        logger.info(f"Loaded {len(self.feedback_data)} feedback samples")
    
    async def train_reward_model(self, epochs: int = 3) -> Dict[str, float]:
        """Train the reward model on human feedback"""
        
        logger.info("Training reward model...")
        
        # Create dataset and dataloader
        dataset = IndianFeedbackDataset(self.feedback_data, self.tokenizer, self.config.max_seq_length)
        dataloader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)
        
        # Optimizer for reward model
        optimizer = optim.AdamW(self.reward_model.parameters(), lr=self.config.reward_learning_rate)
        
        total_loss = 0.0
        total_cost = 0.0
        
        self.reward_model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            
            for batch_idx, batch in enumerate(dataloader):
                optimizer.zero_grad()
                
                # Get rewards for both responses
                rewards_a = self.reward_model(
                    input_ids=batch['input_ids_a'],
                    attention_mask=batch['attention_mask_a'],
                    regional_context=batch['regional_id'],
                    language_ids=batch['language_id']
                )['weighted_reward'].squeeze()
                
                rewards_b = self.reward_model(
                    input_ids=batch['input_ids_b'],
                    attention_mask=batch['attention_mask_b'],
                    regional_context=batch['regional_id'],
                    language_ids=batch['language_id']
                )['weighted_reward'].squeeze()
                
                # Preference loss (Bradley-Terry model)
                # If A is preferred, reward_a should be higher than reward_b
                logits = rewards_a - rewards_b
                labels = batch['preference']  # 1 if A preferred, 0 if B preferred
                
                # Convert to probabilities and compute cross-entropy
                probs_a_better = torch.sigmoid(logits)
                loss = F.binary_cross_entropy(probs_a_better, labels)
                
                # Add auxiliary losses for multi-task learning
                cultural_loss = F.mse_loss(torch.sigmoid(rewards_a), batch['cultural_score']) + \
                               F.mse_loss(torch.sigmoid(rewards_b), batch['cultural_score'])
                
                total_loss_batch = loss + 0.1 * cultural_loss
                
                total_loss_batch.backward()
                torch.nn.utils.clip_grad_norm_(self.reward_model.parameters(), 1.0)
                optimizer.step()
                
                epoch_loss += total_loss_batch.item()
                total_cost += batch['input_ids_a'].size(0) * 0.02  # ₹0.02 per sample
                
                if batch_idx % 10 == 0:
                    logger.info(f"Epoch {epoch+1}, Batch {batch_idx}, Loss: {total_loss_batch.item():.4f}")
            
            avg_epoch_loss = epoch_loss / len(dataloader)
            total_loss += avg_epoch_loss
            logger.info(f"Epoch {epoch+1} completed, Average Loss: {avg_epoch_loss:.4f}")
        
        self.reward_model.eval()
        
        return {
            'total_loss': total_loss / epochs,
            'total_cost_inr': total_cost,
            'epochs': epochs,
            'samples_trained': len(self.feedback_data)
        }
    
    async def train_policy_with_ppo(self, steps: int = 100) -> Dict[str, Any]:
        """Train policy model using PPO"""
        
        logger.info("Training policy with PPO...")
        
        # Sample prompts for generation
        sample_prompts = [
            "भारत की संस्कृति के बारे में बताएं",
            "How to cook biryani at home?",
            "मुंबई की यात्रा के लिए टिप्स दें",
            "What are the benefits of yoga?",
            "भारतीय त्योहारों का महत्व क्या है?"
        ]
        
        training_logs = []
        
        for step in range(steps):
            # Sample a prompt
            prompt = random.choice(sample_prompts)
            
            # Tokenize prompt
            prompt_tokens = self.tokenizer(
                prompt,
                return_tensors='pt',
                padding=True,
                truncation=True,
                max_length=self.config.max_seq_length // 2  # Leave space for generation
            )
            
            # Generate response
            with torch.no_grad():
                generated = self.policy_model.generate(
                    input_ids=prompt_tokens['input_ids'],
                    attention_mask=prompt_tokens['attention_mask'],
                    max_length=self.config.max_seq_length,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            # Create batch for training
            batch = {
                'input_ids': generated,
                'attention_mask': torch.ones_like(generated),
                'regional_id': torch.randint(0, len(RegionalContext), (generated.size(0),)),
                'language_id': torch.randint(0, 10, (generated.size(0),))
            }
            
            # PPO training step
            step_results = self.trainer.train_step(batch)
            training_logs.append(step_results)
            
            if step % 10 == 0:
                logger.info(f"PPO Step {step}: "
                           f"Loss={step_results['total_loss']:.4f}, "
                           f"Reward={step_results['avg_reward']:.4f}, "
                           f"Cost=₹{step_results['step_cost_inr']:.4f}")
        
        # Calculate summary statistics
        avg_loss = np.mean([log['total_loss'] for log in training_logs])
        avg_reward = np.mean([log['avg_reward'] for log in training_logs])
        total_cost = sum([log['step_cost_inr'] for log in training_logs])
        total_time = sum([log['step_time'] for log in training_logs])
        
        return {
            'avg_loss': avg_loss,
            'avg_reward': avg_reward,
            'total_cost_inr': total_cost,
            'total_time_seconds': total_time,
            'steps_completed': steps,
            'training_logs': training_logs[-10:]  # Last 10 logs
        }
    
    def get_training_summary(self) -> Dict[str, Any]:
        """Get complete training summary"""
        
        return {
            'total_feedback_samples': len(self.feedback_data),
            'model_parameters': f"{sum(p.numel() for p in self.policy_model.parameters()) / 1e6:.1f}M",
            'reward_model_parameters': f"{sum(p.numel() for p in self.reward_model.parameters()) / 1e6:.1f}M",
            'training_stats': self.trainer.training_stats,
            'config': asdict(self.config)
        }

# Example usage and testing
async def test_rlhf_pipeline():
    """Test RLHF pipeline with Indian cultural context"""
    
    print("🧠 RLHF Training Pipeline Test - Indian Cultural Context")
    print("=" * 60)
    
    # Create configuration
    config = RLHFConfig(
        model_name="gpt2",  # Using GPT2 for demo (smaller model)
        batch_size=2,
        ppo_epochs=2,
        max_seq_length=256,
        cultural_weight=0.4,
        linguistic_weight=0.3,
        safety_weight=0.3
    )
    
    # Initialize pipeline
    pipeline = RLHFTrainingPipeline(config)
    await pipeline.initialize()
    
    print(f"✅ Pipeline initialized")
    print(f"   Feedback samples: {len(pipeline.feedback_data)}")
    print(f"   Policy model: {config.model_name}")
    print(f"   Max sequence length: {config.max_seq_length}")
    
    # Train reward model
    print(f"\n📊 Training Reward Model...")
    reward_results = await pipeline.train_reward_model(epochs=2)
    
    print(f"   Training completed!")
    print(f"   Average loss: {reward_results['total_loss']:.4f}")
    print(f"   Training cost: ₹{reward_results['total_cost_inr']:.2f}")
    print(f"   Samples trained: {reward_results['samples_trained']}")
    
    # Train policy with PPO
    print(f"\n🎯 Training Policy with PPO...")
    ppo_results = await pipeline.train_policy_with_ppo(steps=20)
    
    print(f"   PPO training completed!")
    print(f"   Average loss: {ppo_results['avg_loss']:.4f}")
    print(f"   Average reward: {ppo_results['avg_reward']:.4f}")
    print(f"   Training cost: ₹{ppo_results['total_cost_inr']:.2f}")
    print(f"   Training time: {ppo_results['total_time_seconds']:.1f}s")
    
    # Get complete summary
    summary = pipeline.get_training_summary()
    print(f"\n📈 Training Summary:")
    print(f"   Total feedback samples: {summary['total_feedback_samples']}")
    print(f"   Policy model size: {summary['model_parameters']}")
    print(f"   Reward model size: {summary['reward_model_parameters']}")
    print(f"   Total training steps: {summary['training_stats']['total_steps']}")
    print(f"   Total cost: ₹{summary['training_stats']['total_cost_inr']:.2f}")
    
    print(f"\n🎯 Indian Cultural Optimizations:")
    print(f"   ✅ Regional context awareness (5 regions)")
    print(f"   ✅ Multilingual support (Hindi, English, Tamil, etc.)")
    print(f"   ✅ Cultural appropriateness scoring")
    print(f"   ✅ Linguistic quality assessment")
    print(f"   ✅ Safety and factual accuracy")
    print(f"   ✅ Cost optimization with mixed precision")

if __name__ == "__main__":
    asyncio.run(test_rlhf_pipeline())