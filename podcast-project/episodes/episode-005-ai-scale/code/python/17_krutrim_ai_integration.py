#!/usr/bin/env python3
"""
Krutrim AI Integration for Indian Language Models
Episode 5: Code Example 17

Production-ready integration with Ola's Krutrim AI platform
Supporting Indian languages with advanced reasoning capabilities

Author: Code Developer Agent
Context: Ola's indigenous AI platform with multilingual Indian language support
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, AsyncIterator
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from datetime import datetime, timedelta
import hashlib
import base64

# Krutrim AI के लिए production logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KrutrimModel(Enum):
    """Krutrim AI models available for different use cases"""
    KRUTRIM_BASE = "krutrim-base"
    KRUTRIM_PRO = "krutrim-pro"
    KRUTRIM_MULTILINGUAL = "krutrim-multilingual"
    KRUTRIM_REASONING = "krutrim-reasoning"
    KRUTRIM_CODE = "krutrim-code"
    KRUTRIM_VISION = "krutrim-vision"

class KrutrimService(Enum):
    """Available Krutrim AI services"""
    TEXT_GENERATION = "text-generation"
    CHAT_COMPLETION = "chat-completion"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question-answering"
    CODE_GENERATION = "code-generation"
    SENTIMENT_ANALYSIS = "sentiment-analysis"
    ENTITY_EXTRACTION = "entity-extraction"

@dataclass
class KrutrimConfig:
    """Configuration for Krutrim AI API integration"""
    api_key: str
    organization_id: str
    base_url: str = "https://api.krutrim.ai/v1"
    timeout: int = 30
    max_retries: int = 3
    enable_caching: bool = True
    cache_ttl: int = 1800  # 30 minutes cache TTL
    
    # Cost and rate limiting for Krutrim
    cost_per_token_inr: float = 0.0002  # ₹0.0002 per token (competitive Indian pricing)
    rate_limit_per_minute: int = 60
    daily_token_limit: int = 1000000  # 1M tokens per day
    
    # Indian-specific settings
    default_language: str = "hindi"
    enable_hinglish_processing: bool = True  # Hindi + English mixed processing
    cultural_context: str = "indian"

@dataclass
class ChatMessage:
    """Chat message structure for Krutrim conversation"""
    role: str  # "system", "user", "assistant"
    content: str
    language: Optional[str] = None
    timestamp: Optional[datetime] = None

@dataclass
class TextGenerationRequest:
    """Request structure for Krutrim text generation"""
    prompt: str
    model: KrutrimModel = KrutrimModel.KRUTRIM_BASE
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    language: Optional[str] = None
    cultural_context: Optional[str] = "indian"
    use_case: Optional[str] = "general"
    stop_sequences: Optional[List[str]] = None

@dataclass
class ChatCompletionRequest:
    """Chat completion request for Krutrim conversational AI"""
    messages: List[ChatMessage]
    model: KrutrimModel = KrutrimModel.KRUTRIM_BASE
    max_tokens: int = 1024
    temperature: float = 0.7
    stream: bool = False
    language: Optional[str] = None
    cultural_context: str = "indian"
    conversation_id: Optional[str] = None

@dataclass
class KrutrimResponse:
    """Standard response structure from Krutrim AI"""
    content: str
    model: str
    language: str
    tokens_used: int
    cost_inr: float
    processing_time_ms: int
    request_id: str
    confidence_score: Optional[float] = None
    cultural_relevance: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TranslationRequest:
    """Translation request for Krutrim multilingual capabilities"""
    text: str
    source_language: str
    target_language: str
    domain: Optional[str] = "general"  # general, technical, literary, colloquial
    preserve_context: bool = True
    handle_code_mixing: bool = True  # For Hinglish and other mixed languages

class KrutrimClient:
    """
    Production-ready client for Ola's Krutrim AI platform
    कृत्रिम AI - Indian context और languages के लिए optimized
    """
    
    def __init__(self, config: KrutrimConfig):
        self.config = config
        self.session = None
        self.usage_tracker = KrutrimUsageTracker()
        self.context_manager = IndianContextManager()
        
        # Caching for repeated requests
        self.response_cache = {}
        
        # Rate limiting
        self.request_timestamps = []
        self.daily_token_count = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info("🚀 Krutrim AI Client initialized - Made in India AI platform")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Organization": self.config.organization_id,
                "Content-Type": "application/json",
                "User-Agent": "KrutrimClient-Python/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_cache_key(self, service: str, **kwargs) -> str:
        """Generate cache key for request"""
        cache_data = {"service": service, **kwargs}
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_from_cache(self, cache_key: str) -> Optional[KrutrimResponse]:
        """Get cached response if available"""
        if not self.config.enable_caching:
            return None
        
        if cache_key in self.response_cache:
            cached_response, cached_at = self.response_cache[cache_key]
            if datetime.now() - cached_at < timedelta(seconds=self.config.cache_ttl):
                logger.info("📦 Using cached Krutrim response")
                return cached_response
            else:
                del self.response_cache[cache_key]
        
        return None
    
    def save_to_cache(self, cache_key: str, response: KrutrimResponse):
        """Save response to cache"""
        if self.config.enable_caching:
            self.response_cache[cache_key] = (response, datetime.now())
    
    async def check_rate_limit(self, estimated_tokens: int = 100):
        """
        Check API rate limits for Krutrim
        Krutrim की rate limits और token limits check करना
        """
        
        now = datetime.now()
        
        # Reset daily counter if new day
        if now >= self.daily_reset_time + timedelta(days=1):
            self.daily_token_count = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check daily token limit
        if self.daily_token_count + estimated_tokens > self.config.daily_token_limit:
            raise Exception(f"Daily token limit exceeded: {self.config.daily_token_limit}")
        
        # Check per-minute rate limit
        one_minute_ago = now - timedelta(minutes=1)
        recent_requests = [ts for ts in self.request_timestamps if ts > one_minute_ago]
        
        if len(recent_requests) >= self.config.rate_limit_per_minute:
            wait_time = 60 - (now - recent_requests[0]).total_seconds()
            logger.warning(f"⏱️ Krutrim rate limit reached, waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)
        
        # Update counters
        self.request_timestamps.append(now)
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > one_minute_ago]
    
    async def generate_text(self, request: TextGenerationRequest) -> KrutrimResponse:
        """
        Generate text using Krutrim AI models
        कृत्रिम AI के साथ text generation - Indian context के साथ optimized
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Enhanced prompt with Indian cultural context
        enhanced_prompt = self.context_manager.enhance_prompt_with_context(
            request.prompt, 
            request.language, 
            request.cultural_context
        )
        
        # Check cache first
        cache_key = self.get_cache_key(
            "text_generation",
            prompt=enhanced_prompt,
            model=request.model.value,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        cached_response = self.get_from_cache(cache_key)
        if cached_response:
            return cached_response
        
        # Check rate limits
        await self.check_rate_limit(request.max_tokens)
        
        # Prepare API request
        api_payload = {
            "model": request.model.value,
            "prompt": enhanced_prompt,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
            "language": request.language or self.config.default_language,
            "cultural_context": request.cultural_context,
            "use_case": request.use_case
        }
        
        if request.stop_sequences:
            api_payload["stop"] = request.stop_sequences
        
        try:
            url = f"{self.config.base_url}/text/generate"
            
            async with self.session.post(url, json=api_payload) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    generated_text = data.get("choices", [{}])[0].get("text", "")
                    tokens_used = data.get("usage", {}).get("total_tokens", 0)
                    
                    # Calculate cost in INR
                    cost_inr = tokens_used * self.config.cost_per_token_inr
                    
                    # Update usage tracking
                    self.daily_token_count += tokens_used
                    
                    # Process response through Indian context filter
                    processed_text = self.context_manager.post_process_response(
                        generated_text, request.language
                    )
                    
                    krutrim_response = KrutrimResponse(
                        content=processed_text,
                        model=request.model.value,
                        language=request.language or self.config.default_language,
                        tokens_used=tokens_used,
                        cost_inr=cost_inr,
                        processing_time_ms=processing_time,
                        request_id=request_id,
                        confidence_score=data.get("confidence", 0.9),
                        cultural_relevance=data.get("cultural_relevance", 0.85),
                        metadata=data.get("metadata", {})
                    )
                    
                    # Cache and track usage
                    self.save_to_cache(cache_key, krutrim_response)
                    self.usage_tracker.record_usage("text_generation", tokens_used, cost_inr, processing_time)
                    
                    logger.info(f"✅ Text generated successfully with Krutrim {request.model.value}")
                    return krutrim_response
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Krutrim API error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Krutrim text generation failed: {e}")
            raise
    
    async def chat_completion(self, request: ChatCompletionRequest) -> KrutrimResponse:
        """
        Chat completion using Krutrim conversational AI
        कृत्रिम के साथ conversational AI - Indian languages में chat
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Enhance messages with cultural context
        enhanced_messages = []
        for message in request.messages:
            enhanced_content = self.context_manager.enhance_message_with_context(
                message.content, message.role, request.language
            )
            enhanced_messages.append({
                "role": message.role,
                "content": enhanced_content,
                "language": message.language or request.language
            })
        
        # Check cache for conversation
        cache_key = self.get_cache_key(
            "chat_completion",
            messages_hash=hashlib.md5(str(enhanced_messages).encode()).hexdigest(),
            model=request.model.value,
            temperature=request.temperature
        )
        
        cached_response = self.get_from_cache(cache_key)
        if cached_response:
            return cached_response
        
        # Check rate limits
        estimated_tokens = sum(len(msg["content"].split()) for msg in enhanced_messages) * 2
        await self.check_rate_limit(estimated_tokens)
        
        # Prepare API request
        api_payload = {
            "model": request.model.value,
            "messages": enhanced_messages,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "stream": request.stream,
            "language": request.language or self.config.default_language,
            "cultural_context": request.cultural_context,
            "conversation_id": request.conversation_id
        }
        
        try:
            url = f"{self.config.base_url}/chat/completions"
            
            if request.stream:
                return await self._handle_streaming_chat(url, api_payload, request_id, start_time)
            else:
                return await self._handle_non_streaming_chat(url, api_payload, request_id, start_time, cache_key)
        
        except Exception as e:
            logger.error(f"❌ Krutrim chat completion failed: {e}")
            raise
    
    async def _handle_non_streaming_chat(self, url: str, payload: dict, 
                                       request_id: str, start_time: float, 
                                       cache_key: str) -> KrutrimResponse:
        """Handle non-streaming chat completion"""
        
        async with self.session.post(url, json=payload) as response:
            processing_time = int((time.time() - start_time) * 1000)
            
            if response.status == 200:
                data = await response.json()
                
                assistant_message = data.get("choices", [{}])[0].get("message", {})
                content = assistant_message.get("content", "")
                tokens_used = data.get("usage", {}).get("total_tokens", 0)
                
                # Calculate cost
                cost_inr = tokens_used * self.config.cost_per_token_inr
                self.daily_token_count += tokens_used
                
                # Process response
                processed_content = self.context_manager.post_process_response(
                    content, payload.get("language")
                )
                
                krutrim_response = KrutrimResponse(
                    content=processed_content,
                    model=payload["model"],
                    language=payload["language"],
                    tokens_used=tokens_used,
                    cost_inr=cost_inr,
                    processing_time_ms=processing_time,
                    request_id=request_id,
                    confidence_score=data.get("confidence", 0.9),
                    cultural_relevance=data.get("cultural_relevance", 0.85)
                )
                
                # Cache and track
                self.save_to_cache(cache_key, krutrim_response)
                self.usage_tracker.record_usage("chat_completion", tokens_used, cost_inr, processing_time)
                
                return krutrim_response
            
            else:
                error_text = await response.text()
                raise Exception(f"Chat completion error: {response.status} - {error_text}")
    
    async def _handle_streaming_chat(self, url: str, payload: dict, 
                                   request_id: str, start_time: float) -> AsyncIterator[Dict[str, Any]]:
        """Handle streaming chat completion"""
        
        payload["stream"] = True
        
        async with self.session.post(url, json=payload) as response:
            if response.status == 200:
                async for line in response.content:
                    if line:
                        try:
                            if line.startswith(b'data: '):
                                json_str = line[6:].decode('utf-8').strip()
                                if json_str and json_str != '[DONE]':
                                    chunk_data = json.loads(json_str)
                                    yield chunk_data
                        except json.JSONDecodeError:
                            continue
            else:
                error_text = await response.text()
                raise Exception(f"Streaming chat error: {response.status} - {error_text}")
    
    async def translate_text(self, request: TranslationRequest) -> KrutrimResponse:
        """
        Translate text using Krutrim multilingual capabilities
        कृत्रिम के multilingual translation - Indian languages के साथ optimized
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Special handling for Hinglish and code-mixed content
        if request.handle_code_mixing:
            request.text = self.context_manager.preprocess_mixed_language_text(
                request.text, request.source_language, request.target_language
            )
        
        # Check cache
        cache_key = self.get_cache_key(
            "translation",
            text=request.text,
            source_lang=request.source_language,
            target_lang=request.target_language,
            domain=request.domain
        )
        
        cached_response = self.get_from_cache(cache_key)
        if cached_response:
            return cached_response
        
        # Estimate tokens and check limits
        estimated_tokens = len(request.text.split()) * 2  # Input + output
        await self.check_rate_limit(estimated_tokens)
        
        # Prepare translation request
        api_payload = {
            "model": KrutrimModel.KRUTRIM_MULTILINGUAL.value,
            "text": request.text,
            "source_language": request.source_language,
            "target_language": request.target_language,
            "domain": request.domain,
            "preserve_context": request.preserve_context,
            "handle_code_mixing": request.handle_code_mixing,
            "cultural_context": "indian"
        }
        
        try:
            url = f"{self.config.base_url}/translate"
            
            async with self.session.post(url, json=api_payload) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    translated_text = data.get("translated_text", "")
                    tokens_used = data.get("usage", {}).get("total_tokens", estimated_tokens)
                    
                    # Calculate cost
                    cost_inr = tokens_used * self.config.cost_per_token_inr
                    self.daily_token_count += tokens_used
                    
                    # Post-process translation
                    if request.handle_code_mixing and request.target_language == "hindi":
                        translated_text = self.context_manager.enhance_hindi_translation(translated_text)
                    
                    krutrim_response = KrutrimResponse(
                        content=translated_text,
                        model=KrutrimModel.KRUTRIM_MULTILINGUAL.value,
                        language=request.target_language,
                        tokens_used=tokens_used,
                        cost_inr=cost_inr,
                        processing_time_ms=processing_time,
                        request_id=request_id,
                        confidence_score=data.get("confidence", 0.92),
                        cultural_relevance=data.get("cultural_relevance", 0.88)
                    )
                    
                    # Cache and track
                    self.save_to_cache(cache_key, krutrim_response)
                    self.usage_tracker.record_usage("translation", tokens_used, cost_inr, processing_time)
                    
                    logger.info(f"✅ Translation completed: {request.source_language} → {request.target_language}")
                    return krutrim_response
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Translation error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Krutrim translation failed: {e}")
            raise
    
    async def analyze_sentiment(self, text: str, language: str = "hindi") -> KrutrimResponse:
        """
        Analyze sentiment with Indian cultural context
        भारतीय संदर्भ के साथ sentiment analysis
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Enhanced text for Indian sentiment patterns
        enhanced_text = self.context_manager.enhance_text_for_sentiment(text, language)
        
        api_payload = {
            "model": KrutrimModel.KRUTRIM_BASE.value,
            "text": enhanced_text,
            "language": language,
            "cultural_context": "indian",
            "task": "sentiment_analysis"
        }
        
        try:
            url = f"{self.config.base_url}/analyze/sentiment"
            
            async with self.session.post(url, json=api_payload) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    sentiment_result = {
                        "sentiment": data.get("sentiment", "neutral"),
                        "confidence": data.get("confidence", 0.8),
                        "emotions": data.get("emotions", {}),
                        "cultural_indicators": data.get("cultural_indicators", {}),
                        "intensity": data.get("intensity", 0.5)
                    }
                    
                    tokens_used = data.get("usage", {}).get("total_tokens", 50)
                    cost_inr = tokens_used * self.config.cost_per_token_inr
                    
                    return KrutrimResponse(
                        content=json.dumps(sentiment_result, ensure_ascii=False),
                        model=api_payload["model"],
                        language=language,
                        tokens_used=tokens_used,
                        cost_inr=cost_inr,
                        processing_time_ms=processing_time,
                        request_id=request_id,
                        confidence_score=sentiment_result["confidence"],
                        cultural_relevance=0.9
                    )
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Sentiment analysis error: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Sentiment analysis failed: {e}")
            raise

class KrutrimUsageTracker:
    """
    Track usage statistics for Krutrim API
    कृत्रिम API के usage tracking और cost optimization
    """
    
    def __init__(self):
        self.usage_history = []
        self.daily_stats = {}
        self.service_stats = {}
        self.cost_tracking = {
            "total_spent_inr": 0.0,
            "tokens_processed": 0,
            "requests_made": 0,
            "avg_cost_per_request": 0.0
        }
    
    def record_usage(self, service: str, tokens: int, cost_inr: float, processing_time_ms: int):
        """Record API usage for analytics"""
        
        usage_record = {
            "timestamp": datetime.now(),
            "service": service,
            "tokens": tokens,
            "cost_inr": cost_inr,
            "processing_time_ms": processing_time_ms
        }
        
        self.usage_history.append(usage_record)
        
        # Update aggregates
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_stats:
            self.daily_stats[today] = {"tokens": 0, "cost": 0.0, "requests": 0}
        
        self.daily_stats[today]["tokens"] += tokens
        self.daily_stats[today]["cost"] += cost_inr
        self.daily_stats[today]["requests"] += 1
        
        # Service-wise statistics
        if service not in self.service_stats:
            self.service_stats[service] = {"tokens": 0, "cost": 0.0, "requests": 0, "avg_time": 0}
        
        service_stat = self.service_stats[service]
        prev_requests = service_stat["requests"]
        service_stat["tokens"] += tokens
        service_stat["cost"] += cost_inr
        service_stat["requests"] += 1
        service_stat["avg_time"] = (
            (service_stat["avg_time"] * prev_requests + processing_time_ms) / service_stat["requests"]
        )
        
        # Overall cost tracking
        self.cost_tracking["total_spent_inr"] += cost_inr
        self.cost_tracking["tokens_processed"] += tokens
        self.cost_tracking["requests_made"] += 1
        self.cost_tracking["avg_cost_per_request"] = (
            self.cost_tracking["total_spent_inr"] / self.cost_tracking["requests_made"]
        )
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Generate comprehensive usage report"""
        
        # Recent usage (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_usage = [record for record in self.usage_history if record["timestamp"] > week_ago]
        
        recent_cost = sum(record["cost_inr"] for record in recent_usage)
        recent_tokens = sum(record["tokens"] for record in recent_usage)
        
        return {
            "overall": self.cost_tracking,
            "recent_7_days": {
                "total_cost_inr": recent_cost,
                "total_tokens": recent_tokens,
                "total_requests": len(recent_usage),
                "avg_cost_per_token": recent_cost / recent_tokens if recent_tokens > 0 else 0
            },
            "daily_breakdown": self.daily_stats,
            "service_breakdown": self.service_stats,
            "cost_optimization_suggestions": self._get_optimization_suggestions()
        }
    
    def _get_optimization_suggestions(self) -> List[str]:
        """Generate cost optimization suggestions"""
        
        suggestions = []
        
        # Check if caching could help
        total_requests = self.cost_tracking["requests_made"]
        if total_requests > 100:
            suggestions.append("Enable caching for repeated requests to reduce costs by up to 40%")
        
        # Check for high-cost services
        if "text_generation" in self.service_stats:
            gen_cost = self.service_stats["text_generation"]["cost"]
            if gen_cost > 100:  # ₹100
                suggestions.append("Consider using smaller models or reducing max_tokens for text generation")
        
        # Token usage optimization
        avg_tokens = self.cost_tracking["tokens_processed"] / max(1, self.cost_tracking["requests_made"])
        if avg_tokens > 500:
            suggestions.append("Average token usage is high - consider prompt optimization")
        
        # Time-based optimization
        if len(suggestions) == 0:
            suggestions.append("Your usage is optimized! Consider upgrading to higher tier for bulk discounts")
        
        return suggestions

class IndianContextManager:
    """
    Manage Indian cultural context and language nuances for Krutrim AI
    भारतीय संस्कृति और भाषा की बारीकियों को manage करना
    """
    
    def __init__(self):
        self.cultural_patterns = {
            "greetings": {
                "hindi": ["नमस्ते", "नमस्कार", "प्रणाम", "आदाब"],
                "formal_hindi": ["आपका स्वागत है", "धन्यवाद", "कृपया"],
                "english": ["Hello", "Good morning", "Good evening"]
            },
            "honorifics": {
                "hindi": ["जी", "साहब", "मैडम", "सर", "आंटी", "अंकल"],
                "respectful_terms": ["आप", "आपका", "आपकी", "आपके"]
            },
            "cultural_references": [
                "त्योहार", "दिवाली", "होली", "ईद", "गुरुपूर्णिमा",
                "भारत", "हिंदुस्तान", "देश", "राष्ट्र",
                "परिवार", "घर", "रिश्ते", "संस्कार"
            ]
        }
        
        self.hinglish_patterns = {
            "common_mixes": {
                "acha": "अच्छा", "bhai": "भाई", "yaar": "यार",
                "kya": "क्या", "hai": "है", "kar": "कर",
                "main": "मैं", "tu": "तू", "hum": "हम"
            },
            "english_in_hindi": ["ok", "please", "sorry", "thank you", "welcome"]
        }
    
    def enhance_prompt_with_context(self, prompt: str, language: Optional[str], 
                                  cultural_context: Optional[str]) -> str:
        """Enhance prompt with Indian cultural context"""
        
        if cultural_context == "indian" and language == "hindi":
            # Add respectful context for Hindi prompts
            if not any(honorific in prompt.lower() for honorific in self.cultural_patterns["honorifics"]["hindi"]):
                prompt = "कृपया " + prompt
        
        # Add cultural awareness instruction
        context_instruction = ""
        if cultural_context == "indian":
            context_instruction = "\n[Note: Please respond considering Indian cultural context and values]"
        
        return prompt + context_instruction
    
    def enhance_message_with_context(self, content: str, role: str, language: Optional[str]) -> str:
        """Enhance chat message with appropriate cultural context"""
        
        if role == "assistant" and language == "hindi":
            # Ensure polite and respectful responses
            if not content.endswith(("।", "!", "?")):
                content += "।"
            
            # Add respectful closing if appropriate
            if len(content) > 100 and not any(term in content for term in ["जी", "आप"]):
                content += " क्या और कोई सहायता चाहिए?"
        
        return content
    
    def post_process_response(self, response: str, language: Optional[str]) -> str:
        """Post-process response for better cultural relevance"""
        
        if language == "hindi":
            # Ensure proper Hindi punctuation
            response = response.replace(".", "।").replace(",", ",")
            
            # Fix common transliteration issues
            response = response.replace("aap", "आप").replace("hai", "है")
        
        return response.strip()
    
    def preprocess_mixed_language_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Preprocess Hinglish and code-mixed text"""
        
        if source_lang == "hinglish" or "english" in text.lower():
            # Convert common Hinglish words to proper Hindi
            for hinglish, hindi in self.hinglish_patterns["common_mixes"].items():
                text = text.replace(hinglish, hindi)
        
        return text
    
    def enhance_hindi_translation(self, translated_text: str) -> str:
        """Enhance Hindi translations for natural flow"""
        
        # Add appropriate sentence endings
        if not translated_text.endswith(("।", "!", "?")):
            translated_text += "।"
        
        # Ensure respectful language
        translated_text = translated_text.replace("तुम", "आप").replace("तेरा", "आपका")
        
        return translated_text
    
    def enhance_text_for_sentiment(self, text: str, language: str) -> str:
        """Enhance text for better sentiment analysis in Indian context"""
        
        # Add context markers for better sentiment understanding
        context_markers = {
            "hindi": "[Hindi text with Indian cultural context]",
            "english": "[English text in Indian context]",
            "hinglish": "[Mixed Hindi-English text]"
        }
        
        marker = context_markers.get(language, "[Indian context]")
        return f"{marker} {text}"

# Demo and testing functions
async def demo_krutrim_integration():
    """
    Comprehensive demo of Krutrim AI integration
    कृत्रिम AI integration का comprehensive demo
    """
    
    print("🚀 Krutrim AI Integration Demo - Made in India AI Platform")
    print("=" * 70)
    
    # Configuration (in production, use environment variables)
    config = KrutrimConfig(
        api_key="your_krutrim_api_key_here",
        organization_id="your_org_id_here",
        enable_caching=True,
        enable_hinglish_processing=True
    )
    
    try:
        async with KrutrimClient(config) as client:
            
            # Text Generation Demo
            print("\n🎯 Text Generation Examples:")
            
            generation_tests = [
                {
                    "prompt": "भारत में AI का भविष्य क्या है? कृपया विस्तार से बताइए।",
                    "language": "hindi",
                    "use_case": "educational",
                    "description": "Future of AI in India (Hindi)"
                },
                {
                    "prompt": "Write a short story about a farmer using AI technology in rural India",
                    "language": "english",
                    "use_case": "creative",
                    "description": "AI in Rural India Story (English)"
                },
                {
                    "prompt": "Ola cab service mein AI kaise help kar raha hai?",
                    "language": "hinglish", 
                    "use_case": "business",
                    "description": "AI in Ola Services (Hinglish)"
                }
            ]
            
            for i, test in enumerate(generation_tests, 1):
                print(f"\n{i}. {test['description']}:")
                print(f"   Prompt: {test['prompt']}")
                
                try:
                    request = TextGenerationRequest(
                        prompt=test['prompt'],
                        model=KrutrimModel.KRUTRIM_MULTILINGUAL,
                        max_tokens=200,
                        temperature=0.7,
                        language=test['language'],
                        use_case=test['use_case']
                    )
                    
                    # Simulate API call (in production, this would call actual Krutrim API)
                    response = await simulate_krutrim_text_generation(request)
                    
                    print(f"   Generated: {response.content}")
                    print(f"   Model: {response.model}")
                    print(f"   Tokens: {response.tokens_used}, Cost: ₹{response.cost_inr:.4f}")
                    print(f"   Cultural Relevance: {response.cultural_relevance:.2f}")
                    print(f"   Processing Time: {response.processing_time_ms}ms")
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            # Chat Completion Demo
            print("\n💬 Chat Completion Example:")
            
            chat_messages = [
                ChatMessage(role="system", content="You are a helpful AI assistant that understands Indian culture and languages."),
                ChatMessage(role="user", content="मुझे दिवाली के लिए कुछ traditional sweets के recipes बताइए"),
                ChatMessage(role="assistant", content="दिवाली के लिए यहाँ कुछ पारंपरिक मिठाइयों की recipes हैं: गुजिया, लड्डू, और खजूर।"),
                ChatMessage(role="user", content="गुजिया बनाने की detailed recipe बताइए")
            ]
            
            chat_request = ChatCompletionRequest(
                messages=chat_messages,
                model=KrutrimModel.KRUTRIM_BASE,
                max_tokens=300,
                language="hindi",
                cultural_context="indian"
            )
            
            try:
                chat_response = await simulate_krutrim_chat_completion(chat_request)
                
                print("   Conversation:")
                for msg in chat_messages[-2:]:
                    print(f"   {msg.role.title()}: {msg.content}")
                
                print(f"   Assistant: {chat_response.content}")
                print(f"   Cost: ₹{chat_response.cost_inr:.4f}, Time: {chat_response.processing_time_ms}ms")
                
            except Exception as e:
                print(f"   ❌ Chat completion error: {e}")
            
            # Translation Demo
            print("\n🔄 Translation Examples:")
            
            translation_tests = [
                {
                    "text": "India is becoming a global leader in artificial intelligence and machine learning technologies.",
                    "source": "english",
                    "target": "hindi",
                    "domain": "technical"
                },
                {
                    "text": "हमारे देश में technology का विकास बहुत तेजी से हो रहा है।",
                    "source": "hindi", 
                    "target": "english",
                    "domain": "general"
                },
                {
                    "text": "Bhai, main market jaa raha hun, kya chahiye?",
                    "source": "hinglish",
                    "target": "hindi",
                    "domain": "colloquial"
                }
            ]
            
            for i, test in enumerate(translation_tests, 1):
                print(f"\n   Translation {i} ({test['source']} → {test['target']}):")
                print(f"   Original: {test['text']}")
                
                try:
                    translation_request = TranslationRequest(
                        text=test['text'],
                        source_language=test['source'],
                        target_language=test['target'],
                        domain=test['domain'],
                        handle_code_mixing=True
                    )
                    
                    translation_response = await simulate_krutrim_translation(translation_request)
                    
                    print(f"   Translated: {translation_response.content}")
                    print(f"   Confidence: {translation_response.confidence_score:.2f}")
                    print(f"   Cost: ₹{translation_response.cost_inr:.4f}")
                    
                except Exception as e:
                    print(f"   ❌ Translation error: {e}")
            
            # Sentiment Analysis Demo
            print("\n😊 Sentiment Analysis Examples:")
            
            sentiment_texts = [
                "मुझे Krutrim AI बहुत पसंद है! यह वाकई amazing है।",
                "यह service थोड़ी slow है, improvement की जरूरत है।",
                "Ola की AI technology kamal ki hai, very impressive!"
            ]
            
            for i, text in enumerate(sentiment_texts, 1):
                print(f"\n   Text {i}: {text}")
                
                try:
                    sentiment_response = await simulate_krutrim_sentiment(text, "hinglish")
                    
                    sentiment_data = json.loads(sentiment_response.content)
                    print(f"   Sentiment: {sentiment_data['sentiment']} (confidence: {sentiment_data['confidence']:.2f})")
                    print(f"   Intensity: {sentiment_data['intensity']:.2f}")
                    print(f"   Cost: ₹{sentiment_response.cost_inr:.4f}")
                    
                except Exception as e:
                    print(f"   ❌ Sentiment analysis error: {e}")
            
            # Usage Analytics
            print("\n📊 Usage Analytics:")
            usage_report = client.usage_tracker.get_usage_report()
            
            print(f"   Total Requests: {usage_report['overall']['requests_made']}")
            print(f"   Total Cost: ₹{usage_report['overall']['total_spent_inr']:.4f}")
            print(f"   Avg Cost per Request: ₹{usage_report['overall']['avg_cost_per_request']:.4f}")
            print(f"   Tokens Processed: {usage_report['overall']['tokens_processed']:,}")
            
            if usage_report['cost_optimization_suggestions']:
                print("\n   💡 Cost Optimization Suggestions:")
                for suggestion in usage_report['cost_optimization_suggestions']:
                    print(f"      • {suggestion}")
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    print("\n🎯 Krutrim AI Integration Features:")
    print("   ✅ Made-in-India AI models with cultural understanding")
    print("   ✅ Multilingual support (Hindi, English, Hinglish)")
    print("   ✅ Advanced Indian context processing")
    print("   ✅ Competitive Indian pricing (₹0.0002/token)")
    print("   ✅ Code-mixing and Hinglish processing")
    print("   ✅ Cultural relevance scoring")
    print("   ✅ Comprehensive usage analytics")
    print("   ✅ Intelligent caching and optimization")
    print("   ✅ Production-ready rate limiting")
    print("   ✅ Support for Indian business use cases")

# Mock functions for demo (replace with actual API calls in production)
async def simulate_krutrim_text_generation(request: TextGenerationRequest) -> KrutrimResponse:
    """Simulate Krutrim text generation for demo"""
    
    await asyncio.sleep(0.8)  # Simulate processing time
    
    # Mock responses based on language and use case
    mock_responses = {
        ("hindi", "educational"): "भारत में AI का भविष्य बहुत उज्ज्वल है। हमारे देश में AI research और development में तेजी से प्रगति हो रही है। Startup ecosystem, government initiatives, और skilled workforce के कारण भारत AI के क्षेत्र में global leader बनने की दिशा में आगे बढ़ रहा है।",
        ("english", "creative"): "In the heart of rural Maharashtra, farmer Ramesh discovered how AI could transform his life. The smart irrigation system, powered by local AI models, helped him optimize water usage and increase crop yield by 40%. This technology, developed by Indian engineers, understood local weather patterns and soil conditions perfectly.",
        ("hinglish", "business"): "Ola cab service में AI बहुत important role play kar raha है। Route optimization, demand prediction, driver matching, और fare calculation सब में AI algorithms use होते हैं। यह customer experience को better बनाता है और efficiency भी बढ़ाता है।"
    }
    
    key = (request.language, request.use_case)
    generated_text = mock_responses.get(key, f"[Krutrim AI generated response for: {request.prompt[:50]}...]")
    
    return KrutrimResponse(
        content=generated_text,
        model=request.model.value,
        language=request.language or "hindi",
        tokens_used=len(generated_text.split()) + len(request.prompt.split()),
        cost_inr=0.025,  # Mock cost
        processing_time_ms=800,
        request_id=str(uuid.uuid4()),
        confidence_score=0.92,
        cultural_relevance=0.88
    )

async def simulate_krutrim_chat_completion(request: ChatCompletionRequest) -> KrutrimResponse:
    """Simulate Krutrim chat completion for demo"""
    
    await asyncio.sleep(1.2)
    
    # Mock response for Diwali sweets recipe
    response_content = """गुजिया बनाने की विस्तृत recipe:

सामग्री:
- मैदा: 2 कप
- घी: 4 बड़े चम्मच
- खोवा: 200 ग्राम
- सूखे मेवे: 1/2 कप (बादाम, किशमिश)
- चीनी: 1/2 कप
- इलायची पाउडर: 1/2 छोटा चम्मच

विधि:
1. मैदा में घी मिलाकर कड़क आटा गूंधें
2. खोवा को भून कर मेवे और चीनी मिलाएं
3. छोटी लोइयां बनाकर भरावन भरें
4. अर्धचंद्र आकार देकर तेल में तल लें

दिवाली की शुभकामनाएं! 🪔"""
    
    return KrutrimResponse(
        content=response_content,
        model=request.model.value,
        language=request.language or "hindi",
        tokens_used=180,
        cost_inr=0.036,
        processing_time_ms=1200,
        request_id=str(uuid.uuid4()),
        confidence_score=0.95,
        cultural_relevance=0.98
    )

async def simulate_krutrim_translation(request: TranslationRequest) -> KrutrimResponse:
    """Simulate Krutrim translation for demo"""
    
    await asyncio.sleep(0.6)
    
    mock_translations = {
        ("India is becoming a global leader in artificial intelligence and machine learning technologies.", "english", "hindi"): "भारत कृत्रिम बुद्धिमत्ता और मशीन लर्निंग प्रौद्योगिकी में विश्व अग्रणी बन रहा है।",
        ("हमारे देश में technology का विकास बहुत तेजी से हो रहा है।", "hindi", "english"): "Technology development is happening very rapidly in our country.",
        ("Bhai, main market jaa raha hun, kya chahiye?", "hinglish", "hindi"): "भाई, मैं बाजार जा रहा हूँ, क्या चाहिए?"
    }
    
    key = (request.text, request.source_language, request.target_language)
    translated_text = mock_translations.get(key, f"[Translated from {request.source_language} to {request.target_language}]: {request.text}")
    
    return KrutrimResponse(
        content=translated_text,
        model=KrutrimModel.KRUTRIM_MULTILINGUAL.value,
        language=request.target_language,
        tokens_used=len(request.text.split()) * 2,
        cost_inr=0.018,
        processing_time_ms=600,
        request_id=str(uuid.uuid4()),
        confidence_score=0.93,
        cultural_relevance=0.89
    )

async def simulate_krutrim_sentiment(text: str, language: str) -> KrutrimResponse:
    """Simulate Krutrim sentiment analysis for demo"""
    
    await asyncio.sleep(0.4)
    
    # Simple sentiment detection based on keywords
    positive_words = ["पसंद", "amazing", "kamal", "impressive", "great", "good", "excellent"]
    negative_words = ["slow", "bad", "problem", "issue", "धीमी", "खराब"]
    
    positive_count = sum(1 for word in positive_words if word.lower() in text.lower())
    negative_count = sum(1 for word in negative_words if word.lower() in text.lower())
    
    if positive_count > negative_count:
        sentiment = "positive"
        confidence = 0.85 + (positive_count * 0.05)
        intensity = 0.7 + (positive_count * 0.1)
    elif negative_count > positive_count:
        sentiment = "negative"
        confidence = 0.80 + (negative_count * 0.05)
        intensity = 0.6 + (negative_count * 0.1)
    else:
        sentiment = "neutral"
        confidence = 0.75
        intensity = 0.5
    
    sentiment_result = {
        "sentiment": sentiment,
        "confidence": min(confidence, 0.98),
        "emotions": {
            "joy": 0.8 if sentiment == "positive" else 0.2,
            "anger": 0.7 if sentiment == "negative" else 0.1,
            "neutral": 0.9 if sentiment == "neutral" else 0.3
        },
        "cultural_indicators": {
            "hinglish_usage": 0.9 if any(word in text.lower() for word in ["hai", "kar", "bhai"]) else 0.1,
            "respectful_tone": 0.8 if any(word in text for word in ["जी", "आप", "please"]) else 0.3
        },
        "intensity": min(intensity, 1.0)
    }
    
    return KrutrimResponse(
        content=json.dumps(sentiment_result, ensure_ascii=False),
        model=KrutrimModel.KRUTRIM_BASE.value,
        language=language,
        tokens_used=len(text.split()) + 20,  # Input + analysis tokens
        cost_inr=0.012,
        processing_time_ms=400,
        request_id=str(uuid.uuid4()),
        confidence_score=sentiment_result["confidence"],
        cultural_relevance=0.92
    )

if __name__ == "__main__":
    asyncio.run(demo_krutrim_integration())