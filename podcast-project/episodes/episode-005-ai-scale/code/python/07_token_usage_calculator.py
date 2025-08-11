#!/usr/bin/env python3
"""
Token Usage Calculator with INR Pricing
Episode 5: Code Example 7

Production-ready token usage calculator for AI applications
Optimized for Indian pricing, multiple providers, and cost optimization

Author: Code Developer Agent
Context: Cost management for Indian AI/ML applications at scale
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re
import tiktoken
import asyncio
from datetime import datetime, timedelta
import numpy as np

# Production logging for cost management
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    OPENAI_GPT3_5 = "openai_gpt3.5"
    OPENAI_GPT4 = "openai_gpt4"
    ANTHROPIC_CLAUDE = "anthropic_claude"
    GOOGLE_BARD = "google_bard"
    COHERE = "cohere"
    HUGGINGFACE = "huggingface"
    LOCAL_MODEL = "local_model"
    
    # Indian providers
    AI4BHARAT = "ai4bharat"
    SARVAM_AI = "sarvam_ai"
    KRUTRIM = "krutrim"

class TokenType(Enum):
    INPUT = "input"
    OUTPUT = "output"
    CACHED = "cached"
    FINE_TUNING = "fine_tuning"

@dataclass
class PricingTier:
    """Pricing tier for different usage volumes"""
    name: str
    min_tokens: int
    max_tokens: int
    discount_percentage: float
    description: str

@dataclass
class ProviderPricing:
    """Pricing structure for AI providers in INR"""
    provider: AIProvider
    model_name: str
    input_price_per_1k_tokens: float  # INR per 1000 input tokens
    output_price_per_1k_tokens: float  # INR per 1000 output tokens
    cached_price_per_1k_tokens: float  # INR per 1000 cached tokens
    fine_tuning_price_per_1k_tokens: float  # INR per 1000 fine-tuning tokens
    
    # Indian specific pricing
    currency: str = "INR"
    includes_gst: bool = True
    pricing_tiers: List[PricingTier] = None
    
    # Rate limits (tokens per minute)
    rate_limit_tpm: int = 60000
    rate_limit_rpm: int = 3000  # requests per minute
    
    def __post_init__(self):
        if self.pricing_tiers is None:
            self.pricing_tiers = []

class TokenCounter:
    """
    Accurate token counting for different models and languages
    Optimized for Indian languages with special handling for Devanagari
    """
    
    def __init__(self):
        self.encoders = {}
        self._initialize_encoders()
    
    def _initialize_encoders(self):
        """Initialize token encoders for different models"""
        
        try:
            # OpenAI encoders
            self.encoders["gpt-3.5-turbo"] = tiktoken.get_encoding("cl100k_base")
            self.encoders["gpt-4"] = tiktoken.get_encoding("cl100k_base")
            self.encoders["text-davinci-003"] = tiktoken.get_encoding("p50k_base")
            
            logger.info("Initialized OpenAI token encoders")
        except Exception as e:
            logger.warning(f"Failed to initialize tiktoken encoders: {e}")
    
    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """
        Count tokens in text for specific model
        
        Args:
            text: Input text to count
            model: Model name for accurate counting
            
        Returns:
            Number of tokens
        """
        
        if model in self.encoders:
            return len(self.encoders[model].encode(text))
        else:
            # Fallback to heuristic counting
            return self._heuristic_token_count(text)
    
    def _heuristic_token_count(self, text: str) -> int:
        """
        Heuristic token counting for models without encoders
        Handles Indian languages specifically
        """
        
        # Count different script types
        devanagari_chars = len([c for c in text if 0x0900 <= ord(c) <= 0x097F])  # Hindi
        tamil_chars = len([c for c in text if 0x0B80 <= ord(c) <= 0x0BFF])      # Tamil
        bengali_chars = len([c for c in text if 0x0980 <= ord(c) <= 0x09FF])    # Bengali
        
        # English and other latin characters
        english_chars = len([c for c in text if c.isalpha() and ord(c) < 256])
        
        # Whitespace and punctuation
        spaces = text.count(' ')
        
        # Different token rates for different scripts
        # Devanagari: ~2.5 chars per token (complex script)
        # Tamil/Bengali: ~3 chars per token
        # English: ~4 chars per token
        # Spaces: ~4 spaces per token
        
        estimated_tokens = (
            devanagari_chars / 2.5 +
            tamil_chars / 3.0 +
            bengali_chars / 3.0 +
            english_chars / 4.0 +
            spaces / 4.0
        )
        
        return max(1, int(estimated_tokens))
    
    def analyze_text_composition(self, text: str) -> Dict[str, Any]:
        """Analyze text composition for better token estimation"""
        
        total_chars = len(text)
        if total_chars == 0:
            return {"total_chars": 0, "composition": {}, "estimated_tokens": 0}
        
        # Count different script types
        script_counts = {
            "devanagari": len([c for c in text if 0x0900 <= ord(c) <= 0x097F]),
            "tamil": len([c for c in text if 0x0B80 <= ord(c) <= 0x0BFF]),
            "bengali": len([c for c in text if 0x0980 <= ord(c) <= 0x09FF]),
            "english": len([c for c in text if c.isalpha() and ord(c) < 256]),
            "numbers": len([c for c in text if c.isdigit()]),
            "punctuation": len([c for c in text if not c.isalnum() and not c.isspace()]),
            "whitespace": len([c for c in text if c.isspace()])
        }
        
        # Calculate percentages
        composition = {
            script: (count / total_chars) * 100 
            for script, count in script_counts.items()
        }
        
        return {
            "total_chars": total_chars,
            "script_counts": script_counts,
            "composition": composition,
            "estimated_tokens": self._heuristic_token_count(text),
            "is_code_mixed": composition["devanagari"] > 10 and composition["english"] > 10
        }

class CostCalculator:
    """
    Calculate costs for different AI providers and usage patterns
    Optimized for Indian market with GST, tier pricing, and bulk discounts
    """
    
    def __init__(self):
        self.pricing_data = {}
        self.token_counter = TokenCounter()
        self._initialize_pricing()
    
    def _initialize_pricing(self):
        """Initialize pricing for all supported providers (in INR)"""
        
        # OpenAI pricing converted to INR (approximate rates)
        self.pricing_data[AIProvider.OPENAI_GPT3_5] = ProviderPricing(
            provider=AIProvider.OPENAI_GPT3_5,
            model_name="gpt-3.5-turbo",
            input_price_per_1k_tokens=0.15,   # ~₹0.15 per 1k tokens
            output_price_per_1k_tokens=0.30,  # ~₹0.30 per 1k tokens
            cached_price_per_1k_tokens=0.075, # 50% discount for cached
            fine_tuning_price_per_1k_tokens=2.50,
            pricing_tiers=[
                PricingTier("Starter", 0, 100000, 0, "Up to 100K tokens/month"),
                PricingTier("Growth", 100001, 1000000, 10, "100K-1M tokens/month"),
                PricingTier("Enterprise", 1000001, float('inf'), 25, "1M+ tokens/month")
            ]
        )
        
        self.pricing_data[AIProvider.OPENAI_GPT4] = ProviderPricing(
            provider=AIProvider.OPENAI_GPT4,
            model_name="gpt-4",
            input_price_per_1k_tokens=2.50,   # ~₹2.50 per 1k tokens
            output_price_per_1k_tokens=5.00,  # ~₹5.00 per 1k tokens
            cached_price_per_1k_tokens=1.25,  # 50% discount for cached
            fine_tuning_price_per_1k_tokens=25.00,
            rate_limit_tpm=10000,  # Lower limits for GPT-4
            rate_limit_rpm=500
        )
        
        # Indian provider pricing (competitive rates)
        self.pricing_data[AIProvider.AI4BHARAT] = ProviderPricing(
            provider=AIProvider.AI4BHARAT,
            model_name="IndicBERT",
            input_price_per_1k_tokens=0.05,   # ₹0.05 per 1k tokens
            output_price_per_1k_tokens=0.10,  # ₹0.10 per 1k tokens
            cached_price_per_1k_tokens=0.025,
            fine_tuning_price_per_1k_tokens=1.00,
            pricing_tiers=[
                PricingTier("Student", 0, 50000, 50, "Educational discount"),
                PricingTier("Startup", 50001, 500000, 30, "Startup discount"),
                PricingTier("Enterprise", 500001, float('inf'), 20, "Volume discount")
            ]
        )
        
        self.pricing_data[AIProvider.LOCAL_MODEL] = ProviderPricing(
            provider=AIProvider.LOCAL_MODEL,
            model_name="local-llama",
            input_price_per_1k_tokens=0.01,   # Only infrastructure costs
            output_price_per_1k_tokens=0.01,
            cached_price_per_1k_tokens=0.005,
            fine_tuning_price_per_1k_tokens=0.50,
            rate_limit_tpm=120000,  # Higher limits for local models
            rate_limit_rpm=6000
        )
        
        logger.info(f"Initialized pricing for {len(self.pricing_data)} providers")
    
    def calculate_cost(self, 
                      input_text: str,
                      output_text: str,
                      provider: AIProvider,
                      cached_tokens: int = 0,
                      monthly_volume: int = 0) -> Dict[str, Any]:
        """
        Calculate total cost for a request
        
        Args:
            input_text: Input prompt text
            output_text: Generated output text
            provider: AI provider to use
            cached_tokens: Number of cached tokens (if applicable)
            monthly_volume: Monthly token volume for tier pricing
        """
        
        if provider not in self.pricing_data:
            raise ValueError(f"Pricing not available for provider: {provider}")
        
        pricing = self.pricing_data[provider]
        
        # Count tokens
        input_tokens = self.token_counter.count_tokens(input_text, pricing.model_name)
        output_tokens = self.token_counter.count_tokens(output_text, pricing.model_name)
        total_tokens = input_tokens + output_tokens + cached_tokens
        
        # Base costs
        input_cost = (input_tokens / 1000) * pricing.input_price_per_1k_tokens
        output_cost = (output_tokens / 1000) * pricing.output_price_per_1k_tokens
        cached_cost = (cached_tokens / 1000) * pricing.cached_price_per_1k_tokens
        
        base_cost = input_cost + output_cost + cached_cost
        
        # Apply tier pricing discount
        discount_percentage = 0
        applicable_tier = None
        
        if pricing.pricing_tiers and monthly_volume > 0:
            for tier in pricing.pricing_tiers:
                if tier.min_tokens <= monthly_volume <= tier.max_tokens:
                    discount_percentage = tier.discount_percentage
                    applicable_tier = tier.name
                    break
        
        discounted_cost = base_cost * (1 - discount_percentage / 100)
        
        # Add GST if applicable (18% in India)
        final_cost = discounted_cost * 1.18 if pricing.includes_gst else discounted_cost
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cached_tokens": cached_tokens,
            "total_tokens": total_tokens,
            "base_cost_inr": base_cost,
            "discount_percentage": discount_percentage,
            "applicable_tier": applicable_tier,
            "discounted_cost_inr": discounted_cost,
            "gst_amount_inr": discounted_cost * 0.18 if pricing.includes_gst else 0,
            "final_cost_inr": final_cost,
            "cost_per_token_inr": final_cost / total_tokens if total_tokens > 0 else 0,
            "provider": provider.value,
            "model": pricing.model_name
        }
    
    def compare_providers(self, 
                         input_text: str,
                         output_text: str,
                         providers: List[AIProvider] = None,
                         monthly_volume: int = 100000) -> Dict[str, Any]:
        """Compare costs across different providers"""
        
        if providers is None:
            providers = list(self.pricing_data.keys())
        
        comparison = {}
        
        for provider in providers:
            try:
                cost_data = self.calculate_cost(
                    input_text, output_text, provider, 0, monthly_volume
                )
                comparison[provider.value] = cost_data
            except Exception as e:
                logger.warning(f"Failed to calculate cost for {provider}: {e}")
        
        # Find cheapest option
        cheapest = min(comparison.items(), key=lambda x: x[1]["final_cost_inr"])
        
        return {
            "comparisons": comparison,
            "cheapest_provider": cheapest[0],
            "cheapest_cost_inr": cheapest[1]["final_cost_inr"],
            "monthly_volume": monthly_volume
        }

class UsageTracker:
    """
    Track token usage and costs over time
    Provides insights for cost optimization
    """
    
    def __init__(self):
        self.usage_history = []
        self.daily_usage = {}
        self.monthly_totals = {}
        self.cost_calculator = CostCalculator()
    
    def track_usage(self, 
                   input_text: str,
                   output_text: str,
                   provider: AIProvider,
                   user_id: str = "default",
                   project_id: str = "default") -> Dict[str, Any]:
        """Track a single usage event"""
        
        cost_data = self.cost_calculator.calculate_cost(input_text, output_text, provider)
        
        usage_event = {
            "timestamp": time.time(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "hour": datetime.now().hour,
            "user_id": user_id,
            "project_id": project_id,
            "provider": provider.value,
            "input_length": len(input_text),
            "output_length": len(output_text),
            **cost_data
        }
        
        self.usage_history.append(usage_event)
        self._update_aggregates(usage_event)
        
        return usage_event
    
    def _update_aggregates(self, usage_event: Dict[str, Any]):
        """Update daily and monthly aggregates"""
        
        date = usage_event["date"]
        month = date[:7]  # YYYY-MM
        
        # Daily aggregates
        if date not in self.daily_usage:
            self.daily_usage[date] = {
                "total_tokens": 0,
                "total_cost_inr": 0,
                "request_count": 0,
                "providers": set()
            }
        
        daily = self.daily_usage[date]
        daily["total_tokens"] += usage_event["total_tokens"]
        daily["total_cost_inr"] += usage_event["final_cost_inr"]
        daily["request_count"] += 1
        daily["providers"].add(usage_event["provider"])
        
        # Monthly aggregates
        if month not in self.monthly_totals:
            self.monthly_totals[month] = {
                "total_tokens": 0,
                "total_cost_inr": 0,
                "request_count": 0,
                "unique_users": set(),
                "unique_projects": set()
            }
        
        monthly = self.monthly_totals[month]
        monthly["total_tokens"] += usage_event["total_tokens"]
        monthly["total_cost_inr"] += usage_event["final_cost_inr"]
        monthly["request_count"] += 1
        monthly["unique_users"].add(usage_event["user_id"])
        monthly["unique_projects"].add(usage_event["project_id"])
    
    def get_usage_summary(self, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get usage summary for date range"""
        
        if not start_date:
            start_date = min(self.daily_usage.keys()) if self.daily_usage else datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = max(self.daily_usage.keys()) if self.daily_usage else datetime.now().strftime("%Y-%m-%d")
        
        # Filter usage events
        filtered_events = [
            event for event in self.usage_history
            if start_date <= event["date"] <= end_date
        ]
        
        if not filtered_events:
            return {"message": "No usage data for specified date range"}
        
        # Aggregate statistics
        total_tokens = sum(event["total_tokens"] for event in filtered_events)
        total_cost = sum(event["final_cost_inr"] for event in filtered_events)
        request_count = len(filtered_events)
        
        # Provider breakdown
        provider_stats = {}
        for event in filtered_events:
            provider = event["provider"]
            if provider not in provider_stats:
                provider_stats[provider] = {
                    "tokens": 0,
                    "cost_inr": 0,
                    "requests": 0
                }
            
            provider_stats[provider]["tokens"] += event["total_tokens"]
            provider_stats[provider]["cost_inr"] += event["final_cost_inr"]
            provider_stats[provider]["requests"] += 1
        
        # Time-based analysis
        hourly_usage = {}
        for event in filtered_events:
            hour = event["hour"]
            if hour not in hourly_usage:
                hourly_usage[hour] = 0
            hourly_usage[hour] += event["total_tokens"]
        
        # Peak usage hour
        peak_hour = max(hourly_usage.items(), key=lambda x: x[1]) if hourly_usage else (0, 0)
        
        return {
            "date_range": f"{start_date} to {end_date}",
            "total_tokens": total_tokens,
            "total_cost_inr": f"₹{total_cost:.2f}",
            "request_count": request_count,
            "avg_tokens_per_request": total_tokens / request_count if request_count > 0 else 0,
            "avg_cost_per_request": f"₹{total_cost / request_count:.4f}" if request_count > 0 else "₹0",
            "provider_breakdown": provider_stats,
            "peak_usage_hour": peak_hour[0],
            "peak_usage_tokens": peak_hour[1],
            "daily_average_cost": f"₹{total_cost / max(1, len(set(event['date'] for event in filtered_events))):.2f}"
        }
    
    def predict_monthly_cost(self) -> Dict[str, Any]:
        """Predict monthly cost based on recent usage"""
        
        if not self.usage_history:
            return {"prediction": "No usage data available"}
        
        # Get last 7 days of usage
        recent_events = [
            event for event in self.usage_history
            if event["timestamp"] > time.time() - (7 * 24 * 3600)  # Last 7 days
        ]
        
        if not recent_events:
            return {"prediction": "Insufficient recent data"}
        
        # Calculate daily average
        daily_costs = {}
        for event in recent_events:
            date = event["date"]
            if date not in daily_costs:
                daily_costs[date] = 0
            daily_costs[date] += event["final_cost_inr"]
        
        avg_daily_cost = np.mean(list(daily_costs.values()))
        predicted_monthly_cost = avg_daily_cost * 30
        
        # Calculate with different usage patterns
        predictions = {
            "steady_usage": avg_daily_cost * 30,
            "20_percent_growth": avg_daily_cost * 30 * 1.2,
            "50_percent_growth": avg_daily_cost * 30 * 1.5,
            "conservative_estimate": avg_daily_cost * 25  # Assuming some days with lower usage
        }
        
        return {
            "current_avg_daily_cost": f"₹{avg_daily_cost:.2f}",
            "predictions": {k: f"₹{v:.2f}" for k, v in predictions.items()},
            "based_on_days": len(daily_costs),
            "recommendation": self._get_cost_recommendation(predicted_monthly_cost)
        }
    
    def _get_cost_recommendation(self, predicted_cost: float) -> str:
        """Get cost optimization recommendation"""
        
        if predicted_cost < 500:  # ₹500/month
            return "Low usage. Consider using free tiers or local models for development."
        elif predicted_cost < 5000:  # ₹5000/month
            return "Moderate usage. Look for volume discounts and optimize prompt efficiency."
        elif predicted_cost < 50000:  # ₹50k/month
            return "High usage. Consider enterprise pricing, caching, and hybrid local/cloud approach."
        else:
            return "Very high usage. Strongly recommend local model deployment and selective cloud usage."

# Example usage and testing
async def test_token_usage_calculator():
    """Test token usage calculator with Indian context"""
    
    print("💰 Token Usage Calculator Test - Indian Pricing")
    print("=" * 60)
    
    # Initialize components
    calculator = CostCalculator()
    tracker = UsageTracker()
    
    # Test different Indian language scenarios
    test_scenarios = [
        {
            "name": "Hindi E-commerce Query",
            "input": "मुझे एक अच्छा smartphone चाहिए जो ₹20,000 के under हो",
            "output": "आपके budget में ये options हैं: 1) Redmi Note 12 Pro (₹18,999) - 108MP camera, 5000mAh battery 2) Realme 10 Pro (₹19,499) - Curved display, 5000mAh battery 3) Samsung Galaxy M34 (₹19,999) - Super AMOLED display, 6000mAh battery। सभी में 5G support है और अच्छी performance है।",
            "monthly_volume": 50000
        },
        {
            "name": "English Technical Documentation",
            "input": "Explain microservices architecture patterns for Indian fintech applications",
            "output": "Microservices architecture for Indian fintech requires specific considerations: 1) Regulatory Compliance - Each service must handle RBI guidelines 2) Multi-language Support - Services should support Hindi, English, and regional languages 3) Payment Gateway Integration - UPI, wallet, and banking APIs 4) Scalability for Festival Loads - Handle Diwali/festival transaction spikes 5) Data Residency - Ensure data stays within India as per regulations",
            "monthly_volume": 200000
        },
        {
            "name": "Code Generation",
            "input": "Generate Python code for Indian mobile number validation",
            "output": "```python\nimport re\n\ndef validate_indian_mobile(mobile):\n    \"\"\"\n    Validate Indian mobile number\n    Format: +91XXXXXXXXXX or 0XXXXXXXXXX or XXXXXXXXXX\n    \"\"\"\n    # Remove spaces and special characters\n    mobile = re.sub(r'[\\s\\-\\(\\)]', '', str(mobile))\n    \n    # Pattern for Indian mobile numbers\n    patterns = [\n        r'^(\\+91)?[6-9]\\d{9}$',  # +91XXXXXXXXXX or XXXXXXXXXX\n        r'^0[6-9]\\d{9}$'  # 0XXXXXXXXXX\n    ]\n    \n    return any(re.match(pattern, mobile) for pattern in patterns)\n\n# Test cases\ntest_numbers = ['+91 9876543210', '9876543210', '0987654321', '1234567890']\nfor num in test_numbers:\n    print(f\"{num}: {validate_indian_mobile(num)}\")\n```",
            "monthly_volume": 100000
        }
    ]
    
    print(f"✅ Calculator initialized with {len(calculator.pricing_data)} providers")
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🧪 Scenario {i}: {scenario['name']}")
        print(f"   Input length: {len(scenario['input'])} chars")
        print(f"   Output length: {len(scenario['output'])} chars")
        print(f"   Monthly volume: {scenario['monthly_volume']:,} tokens")
        
        # Compare across providers
        comparison = calculator.compare_providers(
            scenario["input"],
            scenario["output"],
            monthly_volume=scenario["monthly_volume"]
        )
        
        print(f"\n   💸 Cost Comparison:")
        for provider, cost_data in comparison["comparisons"].items():
            print(f"      {provider}:")
            print(f"         Tokens: {cost_data['total_tokens']:,}")
            print(f"         Base Cost: ₹{cost_data['base_cost_inr']:.4f}")
            print(f"         Final Cost: ₹{cost_data['final_cost_inr']:.4f}")
            print(f"         Per Token: ₹{cost_data['cost_per_token_inr']:.6f}")
            if cost_data['applicable_tier']:
                print(f"         Tier: {cost_data['applicable_tier']} ({cost_data['discount_percentage']}% discount)")
        
        print(f"\n   🏆 Cheapest: {comparison['cheapest_provider']} - ₹{comparison['cheapest_cost_inr']:.4f}")
        
        # Track usage for different providers
        for provider_name in ["openai_gpt3.5", "ai4bharat", "local_model"]:
            provider = AIProvider(provider_name)
            if provider in calculator.pricing_data:
                tracker.track_usage(
                    scenario["input"],
                    scenario["output"],
                    provider,
                    f"user_{i}",
                    f"project_{scenario['name'].lower().replace(' ', '_')}"
                )
    
    # Usage analytics
    print(f"\n📊 Usage Analytics:")
    summary = tracker.get_usage_summary()
    
    for key, value in summary.items():
        if key != "provider_breakdown":
            print(f"   {key}: {value}")
    
    print(f"\n   Provider Breakdown:")
    for provider, stats in summary["provider_breakdown"].items():
        print(f"      {provider}: {stats['requests']} requests, "
              f"{stats['tokens']:,} tokens, ₹{stats['cost_inr']:.4f}")
    
    # Monthly prediction
    print(f"\n🔮 Monthly Cost Prediction:")
    prediction = tracker.predict_monthly_cost()
    
    for key, value in prediction.items():
        if key == "predictions":
            print(f"   Predictions:")
            for scenario, cost in value.items():
                print(f"      {scenario}: {cost}")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n💡 Indian Market Optimizations:")
    print(f"   ✅ INR pricing with GST calculations")
    print(f"   ✅ Tier-based volume discounts")
    print(f"   ✅ Indian language token counting")
    print(f"   ✅ Local provider comparisons")
    print(f"   ✅ Educational/startup discounts")
    print(f"   ✅ Cost prediction and recommendations")

if __name__ == "__main__":
    asyncio.run(test_token_usage_calculator())