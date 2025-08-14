#!/usr/bin/env python3
"""
GitOps Feature Flag Management System
=====================================

Indian market के लिए intelligent feature flag management with GitOps integration।
Regional rollouts, A/B testing, और festival season features के साथ।

Features:
- GitOps-driven feature flag management
- Regional rollout strategies (Mumbai → Delhi → Bangalore)
- Indian business hours और festival season awareness
- A/B testing with business metrics integration
- Circuit breaker integration for safe rollouts
- Compliance controls for regulated features

Author: Hindi Tech Podcast - Episode 19
Context: Feature Management for Indian E-commerce
"""

import asyncio
import logging
import json
import yaml
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import kubernetes
from kubernetes import client, config
import aiohttp
import asyncpg
import redis.asyncio as redis
import pytz
from pathlib import Path
import math
import random
import statistics

# Indian timezone
IST = pytz.timezone('Asia/Kolkata')

# Enhanced logging for feature flag operations
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('feature_flag_gitops.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FeatureFlagStatus(Enum):
    """Feature flag status"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    TESTING = "testing"
    ROLLING_OUT = "rolling_out"
    FULLY_DEPLOYED = "fully_deployed"
    DISABLED = "disabled"
    ARCHIVED = "archived"

class RolloutStrategy(Enum):
    """Feature rollout strategies"""
    IMMEDIATE = "immediate"
    GRADUAL = "gradual"
    REGIONAL = "regional"
    USER_SEGMENT = "user_segment"
    BUSINESS_HOURS_ONLY = "business_hours_only"
    FESTIVAL_AWARE = "festival_aware"

class UserSegment(Enum):
    """User segments for targeted rollouts"""
    ALL_USERS = "all_users"
    PREMIUM_USERS = "premium_users"
    NEW_USERS = "new_users"
    BETA_TESTERS = "beta_testers"
    MUMBAI_USERS = "mumbai_users"
    DELHI_USERS = "delhi_users"
    BANGALORE_USERS = "bangalore_users"
    TIER1_CITIES = "tier1_cities"
    TIER2_CITIES = "tier2_cities"

@dataclass
class FeatureFlag:
    """Feature flag definition"""
    flag_id: str
    name: str
    description: str
    status: FeatureFlagStatus = FeatureFlagStatus.INACTIVE
    
    # Targeting
    rollout_percentage: float = 0.0  # 0-100%
    user_segments: List[UserSegment] = field(default_factory=lambda: [UserSegment.ALL_USERS])
    regions: List[str] = field(default_factory=lambda: ['mumbai', 'delhi', 'bangalore'])
    
    # Business rules
    business_hours_only: bool = False
    exclude_festival_season: bool = False
    requires_premium: bool = False
    
    # A/B testing
    is_experiment: bool = False
    control_percentage: float = 50.0  # For A/B tests
    treatment_percentage: float = 50.0
    
    # Rollout strategy
    strategy: RolloutStrategy = RolloutStrategy.GRADUAL
    rollout_start_date: Optional[datetime] = None
    rollout_end_date: Optional[datetime] = None
    
    # Safety
    circuit_breaker_enabled: bool = True
    error_rate_threshold: float = 5.0  # %
    latency_threshold_ms: int = 2000
    rollback_on_failure: bool = True
    
    # Compliance
    requires_compliance_approval: bool = False
    compliance_notes: str = ""
    
    # Metadata
    owner: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(IST))
    updated_at: datetime = field(default_factory=lambda: datetime.now(IST))
    
    # Configuration
    config_values: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserContext:
    """User context for feature flag evaluation"""
    user_id: str
    region: str = "mumbai"
    city: str = ""
    user_segment: UserSegment = UserSegment.ALL_USERS
    is_premium: bool = False
    registration_date: Optional[datetime] = None
    
    # Session info
    ip_address: str = ""
    device_type: str = "mobile"  # mobile, desktop, tablet
    platform: str = "android"   # android, ios, web
    
    # Business context
    is_business_hours: bool = True
    is_festival_season: bool = False
    
    # A/B testing
    experiment_bucket: Optional[str] = None

@dataclass
class FeatureEvaluation:
    """Result of feature flag evaluation"""
    flag_id: str
    user_id: str
    enabled: bool
    variation: str = "default"  # For A/B tests: "control", "treatment", etc.
    
    # Context
    user_context: UserContext = None
    evaluation_time: datetime = field(default_factory=lambda: datetime.now(IST))
    
    # Reason
    evaluation_reason: str = ""
    rule_matched: str = ""
    
    # Config
    config_values: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FeatureFlagConfig:
    """GitOps feature flag configuration"""
    # Storage
    redis_url: str = "redis://redis:6379"
    postgres_url: str = "postgresql://user:pass@postgres:5432/features"
    
    # GitOps
    git_repo: str = ""
    git_branch: str = "main"
    config_path: str = "feature-flags/"
    
    # Kubernetes
    namespace: str = "feature-flags"
    config_map_name: str = "feature-flags-config"
    
    # Monitoring
    prometheus_url: str = "http://prometheus:9090"
    
    # Business settings
    default_regions: List[str] = field(default_factory=lambda: ['mumbai', 'delhi', 'bangalore'])
    business_hours: Dict[str, str] = field(default_factory=lambda: {"start": "09:00", "end": "21:00"})
    
    # Safety
    max_rollout_speed: float = 10.0  # Max 10% per hour
    circuit_breaker_enabled: bool = True
    
    # Notifications
    slack_webhook: str = ""
    feature_team_email: str = "features@company.com"

class IndianBusinessRules:
    """Indian business context for feature flags"""
    
    @staticmethod
    def is_business_hours(timestamp: datetime = None) -> bool:
        """Check if current time is business hours in India"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        return 9 <= timestamp.hour <= 21
    
    @staticmethod
    def is_festival_season(timestamp: datetime = None) -> bool:
        """Check if current time is during festival season"""
        if timestamp is None:
            timestamp = datetime.now(IST)
        
        # Major Indian festival periods
        festival_periods = [
            # Diwali season (Oct-Nov)
            (datetime(timestamp.year, 10, 15, tzinfo=IST), 
             datetime(timestamp.year, 11, 15, tzinfo=IST)),
             
            # Independence Day sales (Aug)
            (datetime(timestamp.year, 8, 10, tzinfo=IST),
             datetime(timestamp.year, 8, 20, tzinfo=IST)),
             
            # New Year shopping (Dec-Jan)
            (datetime(timestamp.year, 12, 25, tzinfo=IST),
             datetime(timestamp.year + 1, 1, 5, tzinfo=IST))
        ]
        
        return any(start <= timestamp <= end for start, end in festival_periods)
    
    @staticmethod
    def get_user_segment(user_context: UserContext) -> UserSegment:
        """Determine user segment based on context"""
        # Premium users
        if user_context.is_premium:
            return UserSegment.PREMIUM_USERS
        
        # Regional segments
        if user_context.region == 'mumbai':
            return UserSegment.MUMBAI_USERS
        elif user_context.region == 'delhi':
            return UserSegment.DELHI_USERS
        elif user_context.region == 'bangalore':
            return UserSegment.BANGALORE_USERS
        
        # New users (registered in last 30 days)
        if (user_context.registration_date and 
            user_context.registration_date > datetime.now(IST) - timedelta(days=30)):
            return UserSegment.NEW_USERS
        
        # City tier-based segments
        tier1_cities = ['mumbai', 'delhi', 'bangalore', 'chennai', 'kolkata', 'hyderabad']
        if user_context.city.lower() in tier1_cities:
            return UserSegment.TIER1_CITIES
        else:
            return UserSegment.TIER2_CITIES
    
    @staticmethod
    def should_enable_for_festival_season(flag: FeatureFlag, timestamp: datetime = None) -> bool:
        """Check if feature should be enabled during festival season"""
        if timestamp is None:
            timestamp = datetime.now(IST)
            
        is_festival = IndianBusinessRules.is_festival_season(timestamp)
        
        # If flag excludes festival season and it's festival time, disable
        if flag.exclude_festival_season and is_festival:
            return False
        
        # If flag is festival-aware, enable only during festivals
        if flag.strategy == RolloutStrategy.FESTIVAL_AWARE and not is_festival:
            return False
        
        return True

class FeatureFlagEvaluator:
    """
    Feature flag evaluation engine।
    
    Regional rollouts, business rules, और A/B testing के साथ intelligent
    feature flag evaluation for Indian market।
    """
    
    def __init__(self, config: FeatureFlagConfig):
        self.config = config
        self.redis_client = None
        self.feature_flags_cache = {}  # In-memory cache
        
    async def initialize(self) -> bool:
        """Initialize feature flag evaluator"""
        try:
            logger.info("🚀 Initializing Feature Flag Evaluator")
            
            # Setup Redis connection
            self.redis_client = redis.from_url(self.config.redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Load feature flags into cache
            await self._load_feature_flags()
            
            logger.info("✅ Feature Flag Evaluator initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Feature Flag Evaluator initialization failed: {e}")
            return False
    
    async def _load_feature_flags(self) -> None:
        """Load feature flags from Redis cache"""
        try:
            # Get all feature flag keys
            flag_keys = await self.redis_client.keys("feature_flag:*")
            
            for flag_key in flag_keys:
                flag_data = await self.redis_client.hgetall(flag_key)
                if flag_data:
                    flag_id = flag_key.replace("feature_flag:", "")
                    
                    # Parse flag data
                    feature_flag = FeatureFlag(
                        flag_id=flag_id,
                        name=flag_data.get('name', ''),
                        description=flag_data.get('description', ''),
                        status=FeatureFlagStatus(flag_data.get('status', 'inactive')),
                        rollout_percentage=float(flag_data.get('rollout_percentage', 0)),
                        user_segments=[UserSegment(s) for s in json.loads(flag_data.get('user_segments', '["all_users"]'))],
                        regions=json.loads(flag_data.get('regions', '["mumbai"]')),
                        business_hours_only=json.loads(flag_data.get('business_hours_only', 'false')),
                        exclude_festival_season=json.loads(flag_data.get('exclude_festival_season', 'false')),
                        is_experiment=json.loads(flag_data.get('is_experiment', 'false')),
                        control_percentage=float(flag_data.get('control_percentage', 50)),
                        treatment_percentage=float(flag_data.get('treatment_percentage', 50)),
                        strategy=RolloutStrategy(flag_data.get('strategy', 'gradual')),
                        circuit_breaker_enabled=json.loads(flag_data.get('circuit_breaker_enabled', 'true')),
                        error_rate_threshold=float(flag_data.get('error_rate_threshold', 5.0)),
                        config_values=json.loads(flag_data.get('config_values', '{}'))
                    )
                    
                    self.feature_flags_cache[flag_id] = feature_flag
                    
            logger.info(f"📊 Loaded {len(self.feature_flags_cache)} feature flags")
            
        except Exception as e:
            logger.error(f"❌ Failed to load feature flags: {e}")
    
    async def evaluate_flag(self, flag_id: str, user_context: UserContext) -> FeatureEvaluation:
        """Evaluate feature flag for user"""
        try:
            # Get feature flag
            feature_flag = self.feature_flags_cache.get(flag_id)
            if not feature_flag:
                return FeatureEvaluation(
                    flag_id=flag_id,
                    user_id=user_context.user_id,
                    enabled=False,
                    evaluation_reason="Flag not found"
                )
            
            # Check if flag is active
            if feature_flag.status == FeatureFlagStatus.INACTIVE:
                return FeatureEvaluation(
                    flag_id=flag_id,
                    user_id=user_context.user_id,
                    enabled=False,
                    evaluation_reason="Flag inactive"
                )
            
            # Update user context with business rules
            current_time = datetime.now(IST)
            user_context.is_business_hours = IndianBusinessRules.is_business_hours(current_time)
            user_context.is_festival_season = IndianBusinessRules.is_festival_season(current_time)
            user_context.user_segment = IndianBusinessRules.get_user_segment(user_context)
            
            # Check circuit breaker
            if feature_flag.circuit_breaker_enabled:
                circuit_open = await self._check_circuit_breaker(flag_id)
                if circuit_open:
                    return FeatureEvaluation(
                        flag_id=flag_id,
                        user_id=user_context.user_id,
                        enabled=False,
                        evaluation_reason="Circuit breaker open"
                    )
            
            # Apply business rules
            business_rules_passed, reason = self._evaluate_business_rules(feature_flag, user_context)
            if not business_rules_passed:
                return FeatureEvaluation(
                    flag_id=flag_id,
                    user_id=user_context.user_id,
                    enabled=False,
                    evaluation_reason=reason
                )
            
            # Check rollout percentage
            rollout_enabled = self._check_rollout_percentage(feature_flag, user_context)
            if not rollout_enabled:
                return FeatureEvaluation(
                    flag_id=flag_id,
                    user_id=user_context.user_id,
                    enabled=False,
                    evaluation_reason="Not in rollout percentage"
                )
            
            # Determine variation (for A/B tests)
            variation = self._determine_variation(feature_flag, user_context)
            
            # Feature is enabled
            evaluation = FeatureEvaluation(
                flag_id=flag_id,
                user_id=user_context.user_id,
                enabled=True,
                variation=variation,
                user_context=user_context,
                evaluation_reason="All conditions met",
                config_values=feature_flag.config_values
            )
            
            # Record evaluation for analytics
            await self._record_evaluation(evaluation)
            
            return evaluation
            
        except Exception as e:
            logger.error(f"❌ Failed to evaluate flag {flag_id}: {e}")
            return FeatureEvaluation(
                flag_id=flag_id,
                user_id=user_context.user_id,
                enabled=False,
                evaluation_reason=f"Evaluation error: {str(e)}"
            )
    
    def _evaluate_business_rules(self, flag: FeatureFlag, user_context: UserContext) -> Tuple[bool, str]:
        """Evaluate business rules for feature flag"""
        
        # Business hours check
        if flag.business_hours_only and not user_context.is_business_hours:
            return False, "Outside business hours"
        
        # Festival season check
        if not IndianBusinessRules.should_enable_for_festival_season(flag):
            return False, "Festival season rule not met"
        
        # Premium user requirement
        if flag.requires_premium and not user_context.is_premium:
            return False, "Premium user required"
        
        # Region targeting
        if flag.regions and user_context.region not in flag.regions:
            return False, f"Region {user_context.region} not targeted"
        
        # User segment targeting
        if (flag.user_segments and 
            UserSegment.ALL_USERS not in flag.user_segments and
            user_context.user_segment not in flag.user_segments):
            return False, f"User segment {user_context.user_segment.value} not targeted"
        
        return True, "Business rules passed"
    
    def _check_rollout_percentage(self, flag: FeatureFlag, user_context: UserContext) -> bool:
        """Check if user is within rollout percentage"""
        
        # If fully deployed, always enable
        if flag.status == FeatureFlagStatus.FULLY_DEPLOYED:
            return True
        
        # If testing or rolling out, check percentage
        if flag.status in [FeatureFlagStatus.TESTING, FeatureFlagStatus.ROLLING_OUT]:
            # Use consistent hash for user to ensure stable assignment
            hash_input = f"{flag.flag_id}:{user_context.user_id}"
            user_hash = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
            user_percentage = (user_hash % 100) + 1
            
            return user_percentage <= flag.rollout_percentage
        
        return False
    
    def _determine_variation(self, flag: FeatureFlag, user_context: UserContext) -> str:
        """Determine variation for A/B tests"""
        
        if not flag.is_experiment:
            return "default"
        
        # Use consistent hash for experiment assignment
        hash_input = f"{flag.flag_id}:experiment:{user_context.user_id}"
        experiment_hash = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        experiment_percentage = (experiment_hash % 100) + 1
        
        if experiment_percentage <= flag.control_percentage:
            return "control"
        elif experiment_percentage <= (flag.control_percentage + flag.treatment_percentage):
            return "treatment"
        else:
            return "control"  # Default to control if percentages don't add to 100
    
    async def _check_circuit_breaker(self, flag_id: str) -> bool:
        """Check if circuit breaker is open for flag"""
        try:
            circuit_key = f"circuit_breaker:{flag_id}"
            circuit_status = await self.redis_client.get(circuit_key)
            
            return circuit_status == "open"
            
        except Exception as e:
            logger.error(f"❌ Circuit breaker check failed: {e}")
            return False  # Fail safe - assume circuit is closed
    
    async def _record_evaluation(self, evaluation: FeatureEvaluation) -> None:
        """Record feature flag evaluation for analytics"""
        try:
            # Store in Redis for real-time analytics
            evaluation_key = f"evaluation:{evaluation.flag_id}:{datetime.now(IST).strftime('%Y%m%d%H')}"
            evaluation_data = {
                'user_id': evaluation.user_id,
                'enabled': str(evaluation.enabled),
                'variation': evaluation.variation,
                'timestamp': evaluation.evaluation_time.isoformat(),
                'region': evaluation.user_context.region if evaluation.user_context else 'unknown'
            }
            
            await self.redis_client.hset(evaluation_key, mapping=evaluation_data)
            await self.redis_client.expire(evaluation_key, 86400 * 7)  # Keep for 7 days
            
            # Increment counters
            counter_key = f"counter:{evaluation.flag_id}:{evaluation.variation}:{datetime.now(IST).strftime('%Y%m%d%H')}"
            await self.redis_client.incr(counter_key)
            await self.redis_client.expire(counter_key, 86400 * 7)
            
        except Exception as e:
            logger.error(f"❌ Failed to record evaluation: {e}")

class FeatureFlagManager:
    """
    GitOps Feature Flag Management।
    
    Git-based configuration management के साथ feature flags की complete
    lifecycle management और monitoring।
    """
    
    def __init__(self, config: FeatureFlagConfig):
        self.config = config
        self.evaluator = FeatureFlagEvaluator(config)
        self.redis_client = None
        self.pg_pool = None
        self.k8s_client = None
        
    async def initialize(self) -> bool:
        """Initialize feature flag manager"""
        try:
            logger.info("🚀 Initializing Feature Flag Manager")
            
            # Initialize evaluator
            if not await self.evaluator.initialize():
                return False
            
            # Setup Redis connection
            self.redis_client = redis.from_url(self.config.redis_url, decode_responses=True)
            await self.redis_client.ping()
            
            # Setup PostgreSQL for long-term storage
            self.pg_pool = await asyncpg.create_pool(
                self.config.postgres_url,
                min_size=5,
                max_size=20
            )
            
            # Initialize database schema
            await self._initialize_database()
            
            # Setup Kubernetes client
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            self.k8s_client = client.ApiClient()
            
            logger.info("✅ Feature Flag Manager initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Feature Flag Manager initialization failed: {e}")
            return False
    
    async def _initialize_database(self) -> None:
        """Initialize feature flag database schema"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS feature_flags (
            id SERIAL PRIMARY KEY,
            flag_id VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(500) NOT NULL,
            description TEXT,
            status VARCHAR(50) NOT NULL,
            rollout_percentage FLOAT DEFAULT 0,
            config_data JSONB DEFAULT '{}'::jsonb,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            owner VARCHAR(255),
            
            INDEX idx_flag_status (status),
            INDEX idx_flag_updated (updated_at)
        );
        
        CREATE TABLE IF NOT EXISTS flag_evaluations (
            id SERIAL PRIMARY KEY,
            flag_id VARCHAR(255) NOT NULL,
            user_id VARCHAR(255) NOT NULL,
            enabled BOOLEAN NOT NULL,
            variation VARCHAR(50) DEFAULT 'default',
            user_context JSONB DEFAULT '{}'::jsonb,
            evaluation_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            region VARCHAR(100),
            
            INDEX idx_eval_flag (flag_id),
            INDEX idx_eval_time (evaluation_time),
            INDEX idx_eval_region (region)
        );
        
        CREATE TABLE IF NOT EXISTS experiment_results (
            id SERIAL PRIMARY KEY,
            flag_id VARCHAR(255) NOT NULL,
            experiment_date DATE NOT NULL,
            variation VARCHAR(50) NOT NULL,
            users_count INTEGER DEFAULT 0,
            conversion_count INTEGER DEFAULT 0,
            conversion_rate FLOAT DEFAULT 0,
            revenue_total FLOAT DEFAULT 0,
            statistical_significance FLOAT DEFAULT 0,
            
            INDEX idx_experiment_flag_date (flag_id, experiment_date),
            INDEX idx_experiment_variation (variation)
        );
        """
        
        async with self.pg_pool.acquire() as conn:
            await conn.execute(schema_sql)
        
        logger.info("✅ Feature flag database schema initialized")
    
    async def create_feature_flag(self, flag: FeatureFlag) -> bool:
        """Create new feature flag"""
        try:
            logger.info(f"📝 Creating feature flag: {flag.flag_id}")
            
            # Save to Redis for fast access
            flag_key = f"feature_flag:{flag.flag_id}"
            flag_data = {
                'name': flag.name,
                'description': flag.description,
                'status': flag.status.value,
                'rollout_percentage': flag.rollout_percentage,
                'user_segments': json.dumps([s.value for s in flag.user_segments]),
                'regions': json.dumps(flag.regions),
                'business_hours_only': json.dumps(flag.business_hours_only),
                'exclude_festival_season': json.dumps(flag.exclude_festival_season),
                'is_experiment': json.dumps(flag.is_experiment),
                'control_percentage': flag.control_percentage,
                'treatment_percentage': flag.treatment_percentage,
                'strategy': flag.strategy.value,
                'circuit_breaker_enabled': json.dumps(flag.circuit_breaker_enabled),
                'error_rate_threshold': flag.error_rate_threshold,
                'config_values': json.dumps(flag.config_values),
                'owner': flag.owner,
                'created_at': flag.created_at.isoformat()
            }
            
            await self.redis_client.hset(flag_key, mapping=flag_data)
            
            # Save to PostgreSQL for long-term storage
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO feature_flags 
                    (flag_id, name, description, status, rollout_percentage, config_data, owner)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, flag.flag_id, flag.name, flag.description, flag.status.value,
                flag.rollout_percentage, json.dumps(asdict(flag), default=str), flag.owner)
            
            # Update local cache
            self.evaluator.feature_flags_cache[flag.flag_id] = flag
            
            # Sync to Kubernetes ConfigMap
            await self._sync_to_kubernetes()
            
            logger.info(f"✅ Feature flag created: {flag.flag_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create feature flag {flag.flag_id}: {e}")
            return False
    
    async def update_rollout_percentage(self, flag_id: str, new_percentage: float, 
                                      updated_by: str) -> bool:
        """Update feature flag rollout percentage"""
        try:
            logger.info(f"📊 Updating rollout for {flag_id}: {new_percentage}%")
            
            # Get current flag
            if flag_id not in self.evaluator.feature_flags_cache:
                logger.error(f"Flag not found: {flag_id}")
                return False
            
            flag = self.evaluator.feature_flags_cache[flag_id]
            
            # Validate rollout speed (safety check)
            if self.config.max_rollout_speed > 0:
                time_since_last_update = datetime.now(IST) - flag.updated_at
                hours_since_update = time_since_last_update.total_seconds() / 3600
                
                if hours_since_update < 1:  # Less than 1 hour
                    max_increase = self.config.max_rollout_speed
                    if new_percentage - flag.rollout_percentage > max_increase:
                        logger.warning(f"Rollout speed exceeded: {new_percentage - flag.rollout_percentage}% > {max_increase}%")
                        return False
            
            # Update flag
            flag.rollout_percentage = new_percentage
            flag.updated_at = datetime.now(IST)
            
            # Update status based on percentage
            if new_percentage == 0:
                flag.status = FeatureFlagStatus.INACTIVE
            elif new_percentage < 100:
                flag.status = FeatureFlagStatus.ROLLING_OUT
            else:
                flag.status = FeatureFlagStatus.FULLY_DEPLOYED
            
            # Save updates
            flag_key = f"feature_flag:{flag_id}"
            await self.redis_client.hset(flag_key, 'rollout_percentage', new_percentage)
            await self.redis_client.hset(flag_key, 'status', flag.status.value)
            await self.redis_client.hset(flag_key, 'updated_at', flag.updated_at.isoformat())
            
            # Update database
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE feature_flags 
                    SET rollout_percentage = $1, status = $2, updated_at = $3
                    WHERE flag_id = $4
                """, new_percentage, flag.status.value, flag.updated_at, flag_id)
            
            # Log audit event
            await self._log_flag_change(flag_id, 'rollout_update', {
                'old_percentage': flag.rollout_percentage,
                'new_percentage': new_percentage,
                'updated_by': updated_by
            })
            
            # Send notifications for significant changes
            if new_percentage >= 50 and flag.rollout_percentage < 50:
                await self._send_rollout_notification(flag_id, "50% rollout milestone reached")
            elif new_percentage == 100:
                await self._send_rollout_notification(flag_id, "Full deployment completed")
            
            logger.info(f"✅ Rollout updated: {flag_id} → {new_percentage}%")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update rollout for {flag_id}: {e}")
            return False
    
    async def run_circuit_breaker_checks(self) -> None:
        """Run circuit breaker checks for all active flags"""
        try:
            active_flags = [flag for flag in self.evaluator.feature_flags_cache.values()
                          if flag.status in [FeatureFlagStatus.ROLLING_OUT, FeatureFlagStatus.FULLY_DEPLOYED]
                          and flag.circuit_breaker_enabled]
            
            for flag in active_flags:
                try:
                    should_open = await self._should_open_circuit_breaker(flag)
                    
                    if should_open:
                        await self._open_circuit_breaker(flag.flag_id, "Error rate threshold exceeded")
                        logger.warning(f"🔴 Circuit breaker opened for flag: {flag.flag_id}")
                        
                except Exception as e:
                    logger.error(f"❌ Circuit breaker check failed for {flag.flag_id}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Circuit breaker checks failed: {e}")
    
    async def _should_open_circuit_breaker(self, flag: FeatureFlag) -> bool:
        """Check if circuit breaker should be opened"""
        try:
            # Get recent evaluation counts and errors
            current_hour = datetime.now(IST).strftime('%Y%m%d%H')
            
            # Count total evaluations
            total_key = f"counter:{flag.flag_id}:*:{current_hour}"
            total_evaluations = 0
            
            counter_keys = await self.redis_client.keys(total_key)
            for key in counter_keys:
                count = await self.redis_client.get(key)
                total_evaluations += int(count) if count else 0
            
            if total_evaluations < 100:  # Need minimum sample size
                return False
            
            # Check error rate from application metrics (mock implementation)
            error_rate = await self._get_flag_error_rate(flag.flag_id)
            
            if error_rate > flag.error_rate_threshold:
                logger.warning(f"Error rate exceeded threshold: {error_rate}% > {flag.error_rate_threshold}%")
                return True
            
            # Check latency (mock implementation)
            latency_p95 = await self._get_flag_latency_p95(flag.flag_id)
            
            if latency_p95 > flag.latency_threshold_ms:
                logger.warning(f"Latency exceeded threshold: {latency_p95}ms > {flag.latency_threshold_ms}ms")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Circuit breaker evaluation failed: {e}")
            return False
    
    async def _get_flag_error_rate(self, flag_id: str) -> float:
        """Get error rate for feature flag (mock implementation)"""
        # In real implementation, query Prometheus for error rates
        # For demo, simulate some error rates
        import random
        return random.uniform(0.1, 10.0)
    
    async def _get_flag_latency_p95(self, flag_id: str) -> float:
        """Get 95th percentile latency for feature flag (mock implementation)"""
        # In real implementation, query Prometheus for latency metrics
        # For demo, simulate latency values
        import random
        return random.uniform(100, 3000)
    
    async def _open_circuit_breaker(self, flag_id: str, reason: str) -> None:
        """Open circuit breaker for flag"""
        try:
            circuit_key = f"circuit_breaker:{flag_id}"
            await self.redis_client.setex(circuit_key, 3600, "open")  # Open for 1 hour
            
            # Log event
            await self._log_flag_change(flag_id, 'circuit_breaker_opened', {
                'reason': reason,
                'opened_at': datetime.now(IST).isoformat()
            })
            
            # Send alert
            await self._send_circuit_breaker_alert(flag_id, reason)
            
        except Exception as e:
            logger.error(f"❌ Failed to open circuit breaker: {e}")
    
    async def get_experiment_results(self, flag_id: str, days: int = 7) -> Dict[str, Any]:
        """Get A/B experiment results"""
        try:
            logger.info(f"📊 Getting experiment results for {flag_id}")
            
            start_date = datetime.now(IST).date() - timedelta(days=days)
            end_date = datetime.now(IST).date()
            
            async with self.pg_pool.acquire() as conn:
                results = await conn.fetch("""
                    SELECT variation, 
                           SUM(users_count) as total_users,
                           SUM(conversion_count) as total_conversions,
                           AVG(conversion_rate) as avg_conversion_rate,
                           SUM(revenue_total) as total_revenue
                    FROM experiment_results 
                    WHERE flag_id = $1 AND experiment_date BETWEEN $2 AND $3
                    GROUP BY variation
                    ORDER BY variation
                """, flag_id, start_date, end_date)
                
                experiment_data = {}
                for row in results:
                    experiment_data[row['variation']] = {
                        'users': row['total_users'],
                        'conversions': row['total_conversions'],
                        'conversion_rate': row['avg_conversion_rate'],
                        'revenue': row['total_revenue']
                    }
                
                # Calculate statistical significance (simplified)
                statistical_significance = 0.0
                if 'control' in experiment_data and 'treatment' in experiment_data:
                    control = experiment_data['control']
                    treatment = experiment_data['treatment']
                    
                    if control['users'] > 100 and treatment['users'] > 100:
                        # Simplified statistical significance calculation
                        control_rate = control['conversion_rate']
                        treatment_rate = treatment['conversion_rate']
                        
                        if control_rate > 0 and treatment_rate > 0:
                            improvement = abs(treatment_rate - control_rate) / control_rate
                            statistical_significance = min(improvement * 100, 99.9)
                
                return {
                    'flag_id': flag_id,
                    'experiment_period': f"{start_date} to {end_date}",
                    'variations': experiment_data,
                    'statistical_significance': statistical_significance,
                    'recommendation': self._get_experiment_recommendation(experiment_data, statistical_significance)
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to get experiment results: {e}")
            return {}
    
    def _get_experiment_recommendation(self, experiment_data: Dict[str, Any], 
                                     significance: float) -> str:
        """Get experiment recommendation"""
        if significance < 95:
            return "Continue experiment - not statistically significant yet"
        
        if 'control' not in experiment_data or 'treatment' not in experiment_data:
            return "Insufficient data for recommendation"
        
        control_rate = experiment_data['control']['conversion_rate']
        treatment_rate = experiment_data['treatment']['conversion_rate']
        
        if treatment_rate > control_rate * 1.05:  # 5% improvement
            return "Launch treatment variation - statistically significant improvement"
        elif treatment_rate < control_rate * 0.95:  # 5% degradation
            return "Stop experiment - treatment shows degradation"
        else:
            return "No significant difference - consider other variations"
    
    async def _sync_to_kubernetes(self) -> None:
        """Sync feature flags to Kubernetes ConfigMap"""
        try:
            # Create ConfigMap data
            config_data = {}
            
            for flag_id, flag in self.evaluator.feature_flags_cache.items():
                config_data[f"{flag_id}.yaml"] = yaml.dump(asdict(flag), default_flow_style=False)
            
            # Update ConfigMap
            v1 = client.CoreV1Api()
            config_map = client.V1ConfigMap(
                metadata=client.V1ObjectMeta(
                    name=self.config.config_map_name,
                    namespace=self.config.namespace
                ),
                data=config_data
            )
            
            try:
                v1.patch_namespaced_config_map(
                    name=self.config.config_map_name,
                    namespace=self.config.namespace,
                    body=config_map
                )
                logger.info("✅ Feature flags synced to Kubernetes")
            except client.ApiException as e:
                if e.status == 404:
                    v1.create_namespaced_config_map(
                        namespace=self.config.namespace,
                        body=config_map
                    )
                    logger.info("✅ Feature flags ConfigMap created")
                else:
                    raise e
                    
        except Exception as e:
            logger.error(f"❌ Failed to sync to Kubernetes: {e}")
    
    async def _log_flag_change(self, flag_id: str, change_type: str, change_data: Dict[str, Any]) -> None:
        """Log feature flag changes for audit"""
        try:
            log_entry = {
                'flag_id': flag_id,
                'change_type': change_type,
                'change_data': change_data,
                'timestamp': datetime.now(IST).isoformat()
            }
            
            log_key = f"flag_audit:{flag_id}:{datetime.now(IST).strftime('%Y%m%d')}"
            await self.redis_client.rpush(log_key, json.dumps(log_entry))
            await self.redis_client.expire(log_key, 86400 * 30)  # Keep for 30 days
            
        except Exception as e:
            logger.error(f"❌ Failed to log flag change: {e}")
    
    async def _send_rollout_notification(self, flag_id: str, message: str) -> None:
        """Send rollout milestone notifications"""
        logger.info(f"📢 Rollout notification: {flag_id} - {message}")
        # Implementation would send to Slack, email, etc.
    
    async def _send_circuit_breaker_alert(self, flag_id: str, reason: str) -> None:
        """Send circuit breaker alert"""
        logger.warning(f"🚨 Circuit breaker alert: {flag_id} - {reason}")
        # Implementation would send urgent alerts to on-call team
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()
        
        if self.pg_pool:
            await self.pg_pool.close()
        
        logger.info("🧹 Feature Flag Manager cleaned up")


async def main():
    """Main function for feature flag GitOps"""
    print("🎯 GitOps Feature Flag Management System")
    print("=" * 50)
    
    # Configuration
    config = FeatureFlagConfig(
        redis_url=os.getenv("REDIS_URL", "redis://redis:6379"),
        postgres_url=os.getenv("DATABASE_URL", "postgresql://user:pass@postgres:5432/features"),
        git_repo="https://github.com/company/feature-flags",
        namespace="feature-flags",
        prometheus_url=os.getenv("PROMETHEUS_URL", "http://prometheus:9090"),
        slack_webhook=os.getenv("SLACK_WEBHOOK", ""),
        feature_team_email="features@company.com",
        max_rollout_speed=10.0,
        circuit_breaker_enabled=True
    )
    
    # Initialize manager
    manager = FeatureFlagManager(config)
    
    try:
        if await manager.initialize():
            print("✅ Feature Flag Manager initialized successfully")
            
            # Example: Create a new feature flag
            new_flag = FeatureFlag(
                flag_id="payment_upi_qr_v2",
                name="UPI QR Code v2",
                description="New UPI QR code generation with enhanced security",
                status=FeatureFlagStatus.TESTING,
                rollout_percentage=10.0,
                user_segments=[UserSegment.BETA_TESTERS, UserSegment.MUMBAI_USERS],
                regions=['mumbai'],
                business_hours_only=True,
                is_experiment=True,
                control_percentage=50.0,
                treatment_percentage=50.0,
                strategy=RolloutStrategy.GRADUAL,
                circuit_breaker_enabled=True,
                error_rate_threshold=3.0,
                owner="payments-team",
                config_values={
                    "qr_version": "2.0",
                    "security_level": "enhanced",
                    "timeout_ms": 30000
                }
            )
            
            success = await manager.create_feature_flag(new_flag)
            if success:
                print(f"✅ Created feature flag: {new_flag.flag_id}")
                
                # Example: Evaluate flag for a user
                user_context = UserContext(
                    user_id="user_12345",
                    region="mumbai",
                    city="mumbai",
                    user_segment=UserSegment.BETA_TESTERS,
                    is_premium=False,
                    device_type="mobile",
                    platform="android"
                )
                
                evaluation = await manager.evaluator.evaluate_flag(new_flag.flag_id, user_context)
                
                print(f"🎯 Flag Evaluation Results:")
                print(f"   Flag ID: {evaluation.flag_id}")
                print(f"   User ID: {evaluation.user_id}")
                print(f"   Enabled: {evaluation.enabled}")
                print(f"   Variation: {evaluation.variation}")
                print(f"   Reason: {evaluation.evaluation_reason}")
                
                # Example: Update rollout percentage
                rollout_success = await manager.update_rollout_percentage(
                    new_flag.flag_id, 25.0, "feature-team"
                )
                
                if rollout_success:
                    print(f"✅ Updated rollout to 25%")
                
            else:
                print(f"❌ Failed to create feature flag")
                
        else:
            print("❌ Failed to initialize Feature Flag Manager")
            
    except Exception as e:
        print(f"❌ Feature Flag Manager error: {e}")
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())