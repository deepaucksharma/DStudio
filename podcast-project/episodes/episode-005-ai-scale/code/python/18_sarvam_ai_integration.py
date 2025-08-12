#!/usr/bin/env python3
"""
Sarvam AI Integration for Indian Language Technologies
Episode 5: Code Example 18

Production-ready integration with Sarvam AI's Indian language models
Supporting speech, text, and multimodal AI capabilities

Author: Code Developer Agent
Context: Sarvam AI platform for Indian language technologies and cultural AI
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from datetime import datetime, timedelta
import hashlib
import base64
import io
from pathlib import Path

# Sarvam AI के लिए production logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SarvamModel(Enum):
    """Sarvam AI models for different Indian language tasks"""
    SARVAM_2B = "sarvam-2b"
    SARVAM_7B = "sarvam-7b" 
    SARVAM_MULTILINGUAL = "sarvam-multilingual"
    SARVAM_VISION = "sarvam-vision"
    SARVAM_SPEECH = "sarvam-speech"
    SARVAM_EMBEDDING = "sarvam-embedding"

class SarvamService(Enum):
    """Available Sarvam AI services"""
    TEXT_GENERATION = "text-generation"
    TRANSLATION = "translation"
    TRANSCRIPTION = "transcription"
    TEXT_TO_SPEECH = "text-to-speech"
    SPEECH_TO_SPEECH = "speech-to-speech"
    EMBEDDING_GENERATION = "embedding-generation"
    VISION_UNDERSTANDING = "vision-understanding"
    MULTIMODAL_CHAT = "multimodal-chat"

@dataclass
class SarvamConfig:
    """Configuration for Sarvam AI API integration"""
    api_key: str
    base_url: str = "https://api.sarvam.ai/v1"
    timeout: int = 60  # Longer timeout for speech processing
    max_retries: int = 3
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour cache
    
    # Cost tracking (competitive Indian pricing)
    text_cost_per_token_inr: float = 0.00015  # ₹0.00015 per token
    speech_cost_per_second_inr: float = 0.02   # ₹0.02 per second of audio
    vision_cost_per_image_inr: float = 0.50    # ₹0.50 per image
    
    # Rate limiting
    requests_per_minute: int = 100
    tokens_per_day: int = 2000000  # 2M tokens per day
    audio_minutes_per_day: int = 1440  # 24 hours of audio per day
    
    # Indian language preferences
    default_source_language: str = "hi"  # Hindi
    default_target_language: str = "en"  # English
    enable_indic_numerals: bool = True
    cultural_adaptation: bool = True

@dataclass
class TextGenerationRequest:
    """Request for Sarvam text generation"""
    prompt: str
    model: SarvamModel = SarvamModel.SARVAM_2B
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    language: str = "hi"  # Hindi by default
    cultural_context: bool = True
    stop_sequences: Optional[List[str]] = None

@dataclass 
class TranslationRequest:
    """Request for Sarvam translation services"""
    text: str
    source_language: str
    target_language: str
    model: SarvamModel = SarvamModel.SARVAM_MULTILINGUAL
    domain: str = "general"  # general, technical, literary
    preserve_formatting: bool = True
    enable_transliteration: bool = False

@dataclass
class TranscriptionRequest:
    """Request for Sarvam speech-to-text"""
    audio_data: bytes
    source_language: str = "hi"
    model: SarvamModel = SarvamModel.SARVAM_SPEECH
    enable_punctuation: bool = True
    enable_timestamps: bool = False
    audio_format: str = "wav"
    sample_rate: int = 16000

@dataclass
class TTSRequest:
    """Request for Sarvam text-to-speech"""
    text: str
    target_language: str = "hi"
    voice_id: Optional[str] = None  # Will use default voice
    speaking_rate: float = 1.0
    pitch: float = 0.0
    audio_format: str = "wav"
    sample_rate: int = 22050

@dataclass
class EmbeddingRequest:
    """Request for Sarvam text embeddings"""
    texts: List[str]
    model: SarvamModel = SarvamModel.SARVAM_EMBEDDING
    language: str = "hi"
    normalize_embeddings: bool = True
    
@dataclass
class VisionRequest:
    """Request for Sarvam vision understanding"""
    image_data: bytes
    prompt: str
    model: SarvamModel = SarvamModel.SARVAM_VISION
    language: str = "hi"
    detail_level: str = "medium"  # low, medium, high

@dataclass
class SarvamResponse:
    """Standard response from Sarvam AI services"""
    content: Union[str, List[float], bytes]
    model: str
    language: str
    processing_time_ms: int
    cost_inr: float
    request_id: str
    metadata: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    
class SarvamClient:
    """
    Production-ready client for Sarvam AI platform
    सर्वम AI - भारतीय भाषाओं के लिए comprehensive AI platform
    """
    
    def __init__(self, config: SarvamConfig):
        self.config = config
        self.session = None
        self.usage_tracker = SarvamUsageTracker()
        self.cache = {}
        
        # Rate limiting state
        self.request_timestamps = []
        self.daily_token_count = 0
        self.daily_audio_minutes = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info("🇮🇳 Sarvam AI Client initialized - Indian Language AI Platform")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "SarvamAI-Python-Client/1.0"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_cache_key(self, service: str, **kwargs) -> str:
        """Generate cache key for requests"""
        cache_data = {"service": service, **kwargs}
        cache_string = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(cache_string.encode('utf-8')).hexdigest()
    
    async def check_rate_limits(self, tokens: int = 0, audio_seconds: float = 0):
        """Check and enforce rate limits"""
        
        now = datetime.now()
        
        # Reset daily counters if new day
        if now >= self.daily_reset_time + timedelta(days=1):
            self.daily_token_count = 0
            self.daily_audio_minutes = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check daily limits
        if self.daily_token_count + tokens > self.config.tokens_per_day:
            raise Exception(f"Daily token limit exceeded: {self.config.tokens_per_day}")
        
        if self.daily_audio_minutes + (audio_seconds / 60) > self.config.audio_minutes_per_day:
            raise Exception(f"Daily audio limit exceeded: {self.config.audio_minutes_per_day} minutes")
        
        # Check per-minute rate limit
        one_minute_ago = now - timedelta(minutes=1)
        recent_requests = [ts for ts in self.request_timestamps if ts > one_minute_ago]
        
        if len(recent_requests) >= self.config.requests_per_minute:
            wait_time = 60 - (now - recent_requests[0]).total_seconds()
            logger.warning(f"⏱️ Rate limit reached, waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)
        
        # Update counters
        self.request_timestamps.append(now)
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > one_minute_ago]
        self.daily_token_count += tokens
        self.daily_audio_minutes += audio_seconds / 60
    
    async def generate_text(self, request: TextGenerationRequest) -> SarvamResponse:
        """
        Generate text using Sarvam AI models
        सर्वम AI के साथ text generation - Indian languages में optimized
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Enhance prompt with cultural context if enabled
        enhanced_prompt = request.prompt
        if request.cultural_context:
            cultural_prefix = self._get_cultural_context_prefix(request.language)
            enhanced_prompt = f"{cultural_prefix}\n{request.prompt}"
        
        # Check cache
        cache_key = self.get_cache_key(
            "text_generation",
            prompt=enhanced_prompt,
            model=request.model.value,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            language=request.language
        )
        
        if self.config.enable_caching and cache_key in self.cache:
            cached_response, cached_at = self.cache[cache_key]
            if datetime.now() - cached_at < timedelta(seconds=self.config.cache_ttl):
                logger.info("📦 Using cached response")
                return cached_response
        
        # Check rate limits
        await self.check_rate_limits(tokens=request.max_tokens)
        
        # Prepare API request
        api_payload = {
            "model": request.model.value,
            "prompt": enhanced_prompt,
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "language": request.language,
            "stop": request.stop_sequences
        }
        
        try:
            url = f"{self.config.base_url}/text/generate"
            
            async with self.session.post(url, json=api_payload) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    generated_text = data.get("text", "")
                    tokens_used = data.get("usage", {}).get("total_tokens", 0)
                    
                    # Post-process for Indian languages
                    if request.language in ["hi", "bn", "ta", "te", "gu", "mr"]:
                        generated_text = self._post_process_indic_text(generated_text, request.language)
                    
                    # Calculate cost
                    cost_inr = tokens_used * self.config.text_cost_per_token_inr
                    
                    sarvam_response = SarvamResponse(
                        content=generated_text,
                        model=request.model.value,
                        language=request.language,
                        processing_time_ms=processing_time,
                        cost_inr=cost_inr,
                        request_id=request_id,
                        confidence_score=data.get("confidence", 0.9),
                        metadata={"tokens_used": tokens_used}
                    )
                    
                    # Cache and track usage
                    if self.config.enable_caching:
                        self.cache[cache_key] = (sarvam_response, datetime.now())
                    
                    self.usage_tracker.record_text_usage(tokens_used, cost_inr, processing_time)
                    
                    logger.info(f"✅ Text generated successfully in {request.language}")
                    return sarvam_response
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Text generation failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Sarvam text generation failed: {e}")
            raise
    
    async def translate_text(self, request: TranslationRequest) -> SarvamResponse:
        """
        Translate text using Sarvam multilingual models
        सर्वम AI के साथ translation - भारतीय भाषाओं के बीच translate करना
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Check cache
        cache_key = self.get_cache_key(
            "translation",
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
            domain=request.domain
        )
        
        if self.config.enable_caching and cache_key in self.cache:
            cached_response, cached_at = self.cache[cache_key]
            if datetime.now() - cached_at < timedelta(seconds=self.config.cache_ttl):
                logger.info("📦 Using cached translation")
                return cached_response
        
        # Estimate tokens and check limits
        estimated_tokens = len(request.text.split()) * 2
        await self.check_rate_limits(tokens=estimated_tokens)
        
        # Prepare translation request
        api_payload = {
            "model": request.model.value,
            "text": request.text,
            "source_language": request.source_language,
            "target_language": request.target_language,
            "domain": request.domain,
            "preserve_formatting": request.preserve_formatting,
            "enable_transliteration": request.enable_transliteration
        }
        
        try:
            url = f"{self.config.base_url}/translate"
            
            async with self.session.post(url, json=api_payload) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    translated_text = data.get("translated_text", "")
                    tokens_used = data.get("usage", {}).get("total_tokens", estimated_tokens)
                    
                    # Apply Indic script formatting if needed
                    if request.target_language in ["hi", "bn", "ta", "te", "gu", "mr"]:
                        translated_text = self._apply_indic_formatting(
                            translated_text, request.target_language
                        )
                    
                    cost_inr = tokens_used * self.config.text_cost_per_token_inr
                    
                    sarvam_response = SarvamResponse(
                        content=translated_text,
                        model=request.model.value,
                        language=request.target_language,
                        processing_time_ms=processing_time,
                        cost_inr=cost_inr,
                        request_id=request_id,
                        confidence_score=data.get("confidence", 0.92),
                        metadata={
                            "source_language": request.source_language,
                            "target_language": request.target_language,
                            "tokens_used": tokens_used,
                            "domain": request.domain
                        }
                    )
                    
                    # Cache and track
                    if self.config.enable_caching:
                        self.cache[cache_key] = (sarvam_response, datetime.now())
                    
                    self.usage_tracker.record_text_usage(tokens_used, cost_inr, processing_time)
                    
                    logger.info(f"✅ Translation completed: {request.source_language} → {request.target_language}")
                    return sarvam_response
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Translation failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Sarvam translation failed: {e}")
            raise
    
    async def transcribe_audio(self, request: TranscriptionRequest) -> SarvamResponse:
        """
        Transcribe audio using Sarvam speech recognition
        सर्वम AI के साथ audio को text में convert करना
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Estimate audio duration for rate limiting
        audio_duration = len(request.audio_data) / (request.sample_rate * 2)  # Rough estimate
        await self.check_rate_limits(audio_seconds=audio_duration)
        
        # Encode audio to base64
        audio_base64 = base64.b64encode(request.audio_data).decode('utf-8')
        
        # Prepare transcription request
        api_payload = {
            "model": request.model.value,
            "audio_data": audio_base64,
            "source_language": request.source_language,
            "audio_format": request.audio_format,
            "sample_rate": request.sample_rate,
            "enable_punctuation": request.enable_punctuation,
            "enable_timestamps": request.enable_timestamps
        }
        
        try:
            url = f"{self.config.base_url}/speech/transcribe"
            
            async with self.session.post(url, json=api_payload) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    transcript = data.get("transcript", "")
                    confidence = data.get("confidence", 0.9)
                    
                    # Post-process transcript for Indic languages
                    if request.source_language in ["hi", "bn", "ta", "te", "gu", "mr"]:
                        transcript = self._post_process_indic_transcript(
                            transcript, request.source_language
                        )
                    
                    cost_inr = audio_duration * self.config.speech_cost_per_second_inr
                    
                    sarvam_response = SarvamResponse(
                        content=transcript,
                        model=request.model.value,
                        language=request.source_language,
                        processing_time_ms=processing_time,
                        cost_inr=cost_inr,
                        request_id=request_id,
                        confidence_score=confidence,
                        metadata={
                            "audio_duration_seconds": audio_duration,
                            "timestamps": data.get("timestamps", []) if request.enable_timestamps else None,
                            "audio_format": request.audio_format
                        }
                    )
                    
                    self.usage_tracker.record_speech_usage(audio_duration, cost_inr, processing_time)
                    
                    logger.info(f"✅ Audio transcribed successfully in {request.source_language}")
                    return sarvam_response
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Transcription failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Sarvam transcription failed: {e}")
            raise
    
    async def synthesize_speech(self, request: TTSRequest) -> SarvamResponse:
        """
        Generate speech from text using Sarvam TTS
        सर्वम AI के साथ text को audio में convert करना
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Estimate audio duration for rate limiting
        estimated_duration = len(request.text) * 0.1  # Rough estimate: 10 chars per second
        await self.check_rate_limits(audio_seconds=estimated_duration)
        
        # Prepare TTS request
        api_payload = {
            "model": request.model or SarvamModel.SARVAM_SPEECH.value,
            "text": request.text,
            "target_language": request.target_language,
            "voice_id": request.voice_id,
            "speaking_rate": request.speaking_rate,
            "pitch": request.pitch,
            "audio_format": request.audio_format,
            "sample_rate": request.sample_rate
        }
        
        try:
            url = f"{self.config.base_url}/speech/synthesize"
            
            async with self.session.post(url, json=api_payload) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Get audio data
                    audio_base64 = data.get("audio_data", "")
                    audio_bytes = base64.b64decode(audio_base64)
                    actual_duration = data.get("duration_seconds", estimated_duration)
                    
                    cost_inr = actual_duration * self.config.speech_cost_per_second_inr
                    
                    sarvam_response = SarvamResponse(
                        content=audio_bytes,
                        model=api_payload["model"],
                        language=request.target_language,
                        processing_time_ms=processing_time,
                        cost_inr=cost_inr,
                        request_id=request_id,
                        metadata={
                            "audio_duration_seconds": actual_duration,
                            "audio_format": request.audio_format,
                            "sample_rate": request.sample_rate,
                            "text_length": len(request.text)
                        }
                    )
                    
                    self.usage_tracker.record_speech_usage(actual_duration, cost_inr, processing_time)
                    
                    logger.info(f"✅ Speech synthesized successfully in {request.target_language}")
                    return sarvam_response
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Speech synthesis failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Sarvam TTS failed: {e}")
            raise
    
    async def generate_embeddings(self, request: EmbeddingRequest) -> SarvamResponse:
        """
        Generate text embeddings using Sarvam models
        सर्वम AI के साथ text embeddings generate करना
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Calculate token usage
        total_tokens = sum(len(text.split()) for text in request.texts)
        await self.check_rate_limits(tokens=total_tokens)
        
        # Prepare embedding request
        api_payload = {
            "model": request.model.value,
            "texts": request.texts,
            "language": request.language,
            "normalize_embeddings": request.normalize_embeddings
        }
        
        try:
            url = f"{self.config.base_url}/embeddings"
            
            async with self.session.post(url, json=api_payload) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    embeddings = data.get("embeddings", [])
                    tokens_used = data.get("usage", {}).get("total_tokens", total_tokens)
                    
                    cost_inr = tokens_used * self.config.text_cost_per_token_inr
                    
                    sarvam_response = SarvamResponse(
                        content=embeddings,
                        model=request.model.value,
                        language=request.language,
                        processing_time_ms=processing_time,
                        cost_inr=cost_inr,
                        request_id=request_id,
                        metadata={
                            "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                            "num_texts": len(request.texts),
                            "tokens_used": tokens_used,
                            "normalized": request.normalize_embeddings
                        }
                    )
                    
                    self.usage_tracker.record_text_usage(tokens_used, cost_inr, processing_time)
                    
                    logger.info(f"✅ Generated embeddings for {len(request.texts)} texts")
                    return sarvam_response
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Embedding generation failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Sarvam embedding generation failed: {e}")
            raise
    
    async def understand_image(self, request: VisionRequest) -> SarvamResponse:
        """
        Understand image content using Sarvam vision models
        सर्वम AI के साथ image understanding - भारतीय context के साथ
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Check rate limits (images count as high token usage)
        estimated_tokens = 500  # Images typically use many tokens
        await self.check_rate_limits(tokens=estimated_tokens)
        
        # Encode image to base64
        image_base64 = base64.b64encode(request.image_data).decode('utf-8')
        
        # Prepare vision request
        api_payload = {
            "model": request.model.value,
            "image_data": image_base64,
            "prompt": request.prompt,
            "language": request.language,
            "detail_level": request.detail_level
        }
        
        try:
            url = f"{self.config.base_url}/vision/understand"
            
            async with self.session.post(url, json=api_payload) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    description = data.get("description", "")
                    tokens_used = data.get("usage", {}).get("total_tokens", estimated_tokens)
                    
                    # Post-process for Indian languages
                    if request.language in ["hi", "bn", "ta", "te", "gu", "mr"]:
                        description = self._post_process_indic_text(description, request.language)
                    
                    cost_inr = self.config.vision_cost_per_image_inr + (tokens_used * self.config.text_cost_per_token_inr)
                    
                    sarvam_response = SarvamResponse(
                        content=description,
                        model=request.model.value,
                        language=request.language,
                        processing_time_ms=processing_time,
                        cost_inr=cost_inr,
                        request_id=request_id,
                        confidence_score=data.get("confidence", 0.88),
                        metadata={
                            "image_size_bytes": len(request.image_data),
                            "detail_level": request.detail_level,
                            "tokens_used": tokens_used,
                            "objects_detected": data.get("objects", []),
                            "scenes_detected": data.get("scenes", [])
                        }
                    )
                    
                    self.usage_tracker.record_vision_usage(1, cost_inr, processing_time)
                    
                    logger.info(f"✅ Image understood successfully in {request.language}")
                    return sarvam_response
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Vision understanding failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Sarvam vision understanding failed: {e}")
            raise
    
    def _get_cultural_context_prefix(self, language: str) -> str:
        """Get cultural context prefix for different Indian languages"""
        
        cultural_contexts = {
            "hi": "भारतीय संस्कृति और परंपराओं को ध्यान में रखते हुए",
            "bn": "ভারতীয় সংস্কৃতি এবং ঐতিহ্য বিবেচনা করে",
            "ta": "இந்திய கலாசாரம் மற்றும் பாரம்பரியத்தைக் கருத்தில் கொண்டு",
            "te": "భారతీయ సంస్కృతి మరియు సంప్రదాయాలను పరిగణనలోకి తీసుకుని",
            "gu": "ભારતીય સંસ્કૃતિ અને પરંપરાઓને ધ્યાનમાં રાખીને",
            "mr": "भारतीय संस्कृती आणि परंपरा लक्षात घेऊन",
            "en": "Keeping in mind Indian culture and traditions"
        }
        
        return cultural_contexts.get(language, "")
    
    def _post_process_indic_text(self, text: str, language: str) -> str:
        """Post-process text for better Indic language formatting"""
        
        if language == "hi":
            # Fix common Hindi formatting issues
            text = text.replace(".", "।")  # Use Devanagari period
            text = text.replace("?", "?")   # Keep question mark
            text = text.replace("!", "!")   # Keep exclamation
            
            # Add proper spacing around punctuation
            text = text.replace("।", "। ")
            text = text.replace("  ", " ")  # Remove double spaces
        
        # Apply Indic numeral formatting if enabled
        if self.config.enable_indic_numerals and language in ["hi", "bn", "gu", "mr"]:
            text = self._convert_to_indic_numerals(text, language)
        
        return text.strip()
    
    def _apply_indic_formatting(self, text: str, language: str) -> str:
        """Apply proper formatting for Indic languages"""
        
        # Common formatting for all Indic languages
        text = text.strip()
        
        # Language-specific formatting
        if language == "hi":
            # Ensure proper sentence endings
            if not text.endswith(("।", "!", "?")):
                text += "।"
        
        return text
    
    def _post_process_indic_transcript(self, transcript: str, language: str) -> str:
        """Post-process transcript for better readability"""
        
        # Remove extra spaces and format properly
        transcript = " ".join(transcript.split())
        
        # Add punctuation if missing
        if language == "hi" and not transcript.endswith(("।", "!", "?")):
            transcript += "।"
        
        return transcript
    
    def _convert_to_indic_numerals(self, text: str, language: str) -> str:
        """Convert Arabic numerals to Indic numerals"""
        
        # Devanagari numerals for Hindi, Marathi
        if language in ["hi", "mr"]:
            devanagari_numerals = "०१२३४५६७८९"
            for i, numeral in enumerate(devanagari_numerals):
                text = text.replace(str(i), numeral)
        
        # Bengali numerals
        elif language == "bn":
            bengali_numerals = "০১২৩৪৫৬৭৮৯"
            for i, numeral in enumerate(bengali_numerals):
                text = text.replace(str(i), numeral)
        
        # Gujarati numerals
        elif language == "gu":
            gujarati_numerals = "૦૧૨૩૪૫૬૭૮૯"
            for i, numeral in enumerate(gujarati_numerals):
                text = text.replace(str(i), numeral)
        
        return text

class SarvamUsageTracker:
    """
    Track usage and costs for Sarvam AI services
    सर्वम AI के usage tracking और cost optimization
    """
    
    def __init__(self):
        self.text_usage = {"requests": 0, "tokens": 0, "cost_inr": 0.0}
        self.speech_usage = {"requests": 0, "audio_minutes": 0.0, "cost_inr": 0.0}
        self.vision_usage = {"requests": 0, "images": 0, "cost_inr": 0.0}
        
        self.daily_usage = {}
        self.service_performance = {}
        
    def record_text_usage(self, tokens: int, cost_inr: float, processing_time_ms: int):
        """Record text-based service usage"""
        
        self.text_usage["requests"] += 1
        self.text_usage["tokens"] += tokens
        self.text_usage["cost_inr"] += cost_inr
        
        self._record_daily_usage("text", cost_inr, tokens)
        self._record_performance("text", processing_time_ms)
    
    def record_speech_usage(self, audio_duration_seconds: float, cost_inr: float, processing_time_ms: int):
        """Record speech service usage"""
        
        self.speech_usage["requests"] += 1
        self.speech_usage["audio_minutes"] += audio_duration_seconds / 60
        self.speech_usage["cost_inr"] += cost_inr
        
        self._record_daily_usage("speech", cost_inr, audio_duration_seconds)
        self._record_performance("speech", processing_time_ms)
    
    def record_vision_usage(self, image_count: int, cost_inr: float, processing_time_ms: int):
        """Record vision service usage"""
        
        self.vision_usage["requests"] += 1
        self.vision_usage["images"] += image_count
        self.vision_usage["cost_inr"] += cost_inr
        
        self._record_daily_usage("vision", cost_inr, image_count)
        self._record_performance("vision", processing_time_ms)
    
    def _record_daily_usage(self, service: str, cost: float, units: Union[int, float]):
        """Record daily usage statistics"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.daily_usage:
            self.daily_usage[today] = {}
        
        if service not in self.daily_usage[today]:
            self.daily_usage[today][service] = {"cost": 0.0, "units": 0.0, "requests": 0}
        
        self.daily_usage[today][service]["cost"] += cost
        self.daily_usage[today][service]["units"] += units
        self.daily_usage[today][service]["requests"] += 1
    
    def _record_performance(self, service: str, processing_time_ms: int):
        """Record service performance metrics"""
        
        if service not in self.service_performance:
            self.service_performance[service] = {"total_time": 0, "request_count": 0}
        
        perf = self.service_performance[service]
        perf["total_time"] += processing_time_ms
        perf["request_count"] += 1
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Generate comprehensive usage report"""
        
        total_cost = (self.text_usage["cost_inr"] + 
                     self.speech_usage["cost_inr"] + 
                     self.vision_usage["cost_inr"])
        
        total_requests = (self.text_usage["requests"] + 
                         self.speech_usage["requests"] + 
                         self.vision_usage["requests"])
        
        # Calculate average performance
        avg_performance = {}
        for service, perf in self.service_performance.items():
            if perf["request_count"] > 0:
                avg_performance[service] = perf["total_time"] / perf["request_count"]
        
        return {
            "summary": {
                "total_cost_inr": total_cost,
                "total_requests": total_requests,
                "avg_cost_per_request": total_cost / max(1, total_requests)
            },
            "service_breakdown": {
                "text": self.text_usage,
                "speech": self.speech_usage,
                "vision": self.vision_usage
            },
            "daily_usage": self.daily_usage,
            "performance": avg_performance,
            "optimization_tips": self._get_optimization_tips()
        }
    
    def _get_optimization_tips(self) -> List[str]:
        """Generate cost optimization tips"""
        
        tips = []
        
        if self.text_usage["cost_inr"] > 10:  # ₹10
            tips.append("Consider caching frequent text requests to reduce costs")
        
        if self.speech_usage["cost_inr"] > 20:  # ₹20
            tips.append("Optimize audio quality settings to balance cost and quality")
        
        if self.vision_usage["cost_inr"] > 50:  # ₹50
            tips.append("Batch image processing requests for better efficiency")
        
        if not tips:
            tips.append("Your usage is well optimized! Keep up the good work")
        
        return tips

# Demo and testing functions
async def demo_sarvam_ai_integration():
    """
    Comprehensive demo of Sarvam AI integration
    सर्वम AI integration का comprehensive demo
    """
    
    print("🚀 Sarvam AI Integration Demo - Indian Language AI Platform")
    print("=" * 70)
    
    # Configuration (use environment variables in production)
    config = SarvamConfig(
        api_key="your_sarvam_api_key_here",
        enable_caching=True,
        cultural_adaptation=True,
        enable_indic_numerals=True
    )
    
    try:
        async with SarvamClient(config) as client:
            
            # Text Generation Demo
            print("\n🎯 Text Generation Examples:")
            
            generation_examples = [
                {
                    "prompt": "भारत में आर्टिफिशियल इंटेलिजेंस का भविष्य क्या है?",
                    "language": "hi",
                    "description": "Future of AI in India (Hindi)"
                },
                {
                    "prompt": "Explain how AI can help farmers in rural India",
                    "language": "en",
                    "description": "AI for Indian farmers (English)"
                },
                {
                    "prompt": "तमिल भाषा में तकनीक कैसे बढ़ रही है?",
                    "language": "ta",
                    "description": "Technology growth in Tamil (Hindi prompt, Tamil response)"
                }
            ]
            
            for i, example in enumerate(generation_examples, 1):
                print(f"\n{i}. {example['description']}:")
                print(f"   Prompt: {example['prompt']}")
                
                try:
                    request = TextGenerationRequest(
                        prompt=example['prompt'],
                        model=SarvamModel.SARVAM_2B,
                        max_tokens=150,
                        language=example['language'],
                        cultural_context=True
                    )
                    
                    # Simulate Sarvam API call
                    response = await simulate_sarvam_text_generation(request)
                    
                    print(f"   Generated: {response.content}")
                    print(f"   Cost: ₹{response.cost_inr:.4f}")
                    print(f"   Processing Time: {response.processing_time_ms}ms")
                    if response.confidence_score:
                        print(f"   Confidence: {response.confidence_score:.2f}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
            
            # Translation Demo
            print("\n🔄 Translation Examples:")
            
            translation_examples = [
                {
                    "text": "India is becoming a leader in artificial intelligence research and development.",
                    "source": "en",
                    "target": "hi",
                    "domain": "technical"
                },
                {
                    "text": "आज का मौसम बहुत अच्छा है। सूरज चमक रहा है।",
                    "source": "hi",
                    "target": "en",
                    "domain": "general"
                },
                {
                    "text": "தமிழ்நாட்டில் தொழில்நுட்பம் வேகமாக வளர்ந்து வருகிறது।",
                    "source": "ta",
                    "target": "hi",
                    "domain": "general"
                }
            ]
            
            for i, example in enumerate(translation_examples, 1):
                print(f"\n   Translation {i} ({example['source']} → {example['target']}):")
                print(f"   Original: {example['text']}")
                
                try:
                    request = TranslationRequest(
                        text=example['text'],
                        source_language=example['source'],
                        target_language=example['target'],
                        domain=example['domain'],
                        preserve_formatting=True
                    )
                    
                    response = await simulate_sarvam_translation(request)
                    
                    print(f"   Translated: {response.content}")
                    print(f"   Cost: ₹{response.cost_inr:.4f}")
                    print(f"   Confidence: {response.confidence_score:.2f}")
                    
                except Exception as e:
                    print(f"   ❌ Translation error: {e}")
            
            # Speech Processing Demo
            print("\n🎤 Speech Processing Examples:")
            
            # Mock audio transcription
            print("   Speech-to-Text (Hindi):")
            mock_audio_data = b"mock_hindi_audio_data"
            
            try:
                transcription_request = TranscriptionRequest(
                    audio_data=mock_audio_data,
                    source_language="hi",
                    enable_punctuation=True
                )
                
                transcription_response = await simulate_sarvam_transcription(transcription_request)
                
                print(f"   Transcript: {transcription_response.content}")
                print(f"   Language: {transcription_response.language}")
                print(f"   Cost: ₹{transcription_response.cost_inr:.4f}")
                print(f"   Confidence: {transcription_response.confidence_score:.2f}")
                
            except Exception as e:
                print(f"   ❌ Transcription error: {e}")
            
            # Text-to-Speech Demo
            print("\n   Text-to-Speech (Hindi):")
            
            try:
                tts_request = TTSRequest(
                    text="सर्वम AI भारतीय भाषाओं के लिए एक उत्कृष्ट platform है।",
                    target_language="hi",
                    speaking_rate=1.0
                )
                
                tts_response = await simulate_sarvam_tts(tts_request)
                
                print(f"   Text: {tts_request.text}")
                print(f"   Audio generated: {len(tts_response.content)} bytes")
                print(f"   Duration: {tts_response.metadata['audio_duration_seconds']:.1f}s")
                print(f"   Cost: ₹{tts_response.cost_inr:.4f}")
                
            except Exception as e:
                print(f"   ❌ TTS error: {e}")
            
            # Embeddings Demo
            print("\n🔢 Text Embeddings Example:")
            
            try:
                embedding_texts = [
                    "भारत एक महान देश है।",
                    "India is a great country.",
                    "तकनीक से जीवन आसान हो गया है।"
                ]
                
                embedding_request = EmbeddingRequest(
                    texts=embedding_texts,
                    language="hi",
                    normalize_embeddings=True
                )
                
                embedding_response = await simulate_sarvam_embeddings(embedding_request)
                
                embeddings = embedding_response.content
                print(f"   Generated embeddings for {len(embedding_texts)} texts")
                print(f"   Embedding dimension: {len(embeddings[0])}")
                print(f"   Cost: ₹{embedding_response.cost_inr:.4f}")
                
                # Show similarity between embeddings
                if len(embeddings) >= 2:
                    import numpy as np
                    similarity = np.dot(embeddings[0], embeddings[1])
                    print(f"   Similarity (Hindi-English): {similarity:.3f}")
                
            except Exception as e:
                print(f"   ❌ Embeddings error: {e}")
            
            # Vision Understanding Demo
            print("\n👁️ Vision Understanding Example:")
            
            try:
                # Mock image data
                mock_image_data = b"mock_image_data_representing_indian_scene"
                
                vision_request = VisionRequest(
                    image_data=mock_image_data,
                    prompt="इस तस्वीर में क्या है? विस्तार से बताइए।",
                    language="hi",
                    detail_level="medium"
                )
                
                vision_response = await simulate_sarvam_vision(vision_request)
                
                print(f"   Prompt: {vision_request.prompt}")
                print(f"   Description: {vision_response.content}")
                print(f"   Cost: ₹{vision_response.cost_inr:.4f}")
                print(f"   Confidence: {vision_response.confidence_score:.2f}")
                
            except Exception as e:
                print(f"   ❌ Vision understanding error: {e}")
            
            # Usage Analytics
            print("\n📊 Usage Analytics:")
            usage_report = client.usage_tracker.get_usage_report()
            
            print(f"   Total Cost: ₹{usage_report['summary']['total_cost_inr']:.4f}")
            print(f"   Total Requests: {usage_report['summary']['total_requests']}")
            print(f"   Avg Cost per Request: ₹{usage_report['summary']['avg_cost_per_request']:.4f}")
            
            print("\n   Service Breakdown:")
            for service, usage in usage_report['service_breakdown'].items():
                print(f"      {service.title()}: {usage['requests']} requests, ₹{usage['cost_inr']:.4f}")
            
            if usage_report['optimization_tips']:
                print("\n   💡 Optimization Tips:")
                for tip in usage_report['optimization_tips']:
                    print(f"      • {tip}")
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    print("\n🎯 Sarvam AI Integration Features:")
    print("   ✅ Comprehensive Indian language AI platform")
    print("   ✅ Text generation with cultural context")
    print("   ✅ High-quality translation between Indian languages")
    print("   ✅ Speech-to-text and text-to-speech in Indian languages")
    print("   ✅ Multilingual embeddings and similarity")
    print("   ✅ Vision understanding with Indian context")
    print("   ✅ Competitive Indian pricing structure")
    print("   ✅ Indic script formatting and numeral support")
    print("   ✅ Advanced caching and rate limiting")
    print("   ✅ Comprehensive usage tracking and analytics")
    print("   ✅ Cultural adaptation and context awareness")

# Mock functions for demo (replace with actual API calls in production)
async def simulate_sarvam_text_generation(request: TextGenerationRequest) -> SarvamResponse:
    """Simulate Sarvam text generation for demo"""
    
    await asyncio.sleep(0.9)
    
    # Mock responses based on language
    mock_responses = {
        "hi": "भारत में आर्टिफिशियल इंटेलिजेंस का भविष्य अत्यधिक उज्ज्वल है। हमारे देश में युवा प्रतिभाओं की कमी नहीं है और government भी AI research को बढ़ावा दे रही है। आने वाले समय में भारत इस क्षेत्र में विश्व अग्रणी बनेगा।",
        "en": "Artificial Intelligence can revolutionize Indian agriculture by providing farmers with real-time weather predictions, soil analysis, crop monitoring, and market price information. Smart irrigation systems and drone-based crop surveillance can increase yields while reducing water usage and costs.",
        "ta": "तमिल नाडु में प्रौद्योगिकी का विकास तेज़ी से हो रहा है। चेन्नई एक प्रमुख IT hub बन गया है और यहाँ कई multinational companies के offices हैं। Tamil भाषा में भी digital content बढ़ रहा है।"
    }
    
    generated_text = mock_responses.get(request.language, f"[Sarvam AI response in {request.language}]: {request.prompt[:100]}...")
    
    return SarvamResponse(
        content=generated_text,
        model=request.model.value,
        language=request.language,
        processing_time_ms=900,
        cost_inr=0.030,
        request_id=str(uuid.uuid4()),
        confidence_score=0.91,
        metadata={"tokens_used": len(generated_text.split()) + len(request.prompt.split())}
    )

async def simulate_sarvam_translation(request: TranslationRequest) -> SarvamResponse:
    """Simulate Sarvam translation for demo"""
    
    await asyncio.sleep(0.7)
    
    mock_translations = {
        ("India is becoming a leader in artificial intelligence research and development.", "en", "hi"): "भारत कृत्रिम बुद्धिमत्ता अनुसंधान और विकास में अग्रणी बन रहा है।",
        ("आज का मौसम बहुत अच्छा है। सूरज चमक रहा है।", "hi", "en"): "Today's weather is very nice. The sun is shining.",
        ("தமிழ்நாட்டில் தொழில்நுட்பம் வேகமாக வளர்ந்து வருகிறது।", "ta", "hi"): "तमिल नाडु में प्रौद्योगिकी तेज़ी से बढ़ रही है।"
    }
    
    key = (request.text, request.source_language, request.target_language)
    translated_text = mock_translations.get(key, f"[Translated from {request.source_language} to {request.target_language}]: {request.text}")
    
    return SarvamResponse(
        content=translated_text,
        model=request.model.value,
        language=request.target_language,
        processing_time_ms=700,
        cost_inr=0.022,
        request_id=str(uuid.uuid4()),
        confidence_score=0.94,
        metadata={
            "source_language": request.source_language,
            "target_language": request.target_language,
            "tokens_used": len(request.text.split()) * 2
        }
    )

async def simulate_sarvam_transcription(request: TranscriptionRequest) -> SarvamResponse:
    """Simulate Sarvam speech transcription for demo"""
    
    await asyncio.sleep(1.5)
    
    mock_transcript = "नमस्ते, मैं सर्वम AI का उपयोग करके speech को text में convert कर रहा हूं। यह technology बहुत उपयोगी है।"
    
    return SarvamResponse(
        content=mock_transcript,
        model=request.model.value,
        language=request.source_language,
        processing_time_ms=1500,
        cost_inr=0.15,  # Based on audio duration
        request_id=str(uuid.uuid4()),
        confidence_score=0.89,
        metadata={
            "audio_duration_seconds": 7.5,
            "audio_format": request.audio_format,
            "enable_punctuation": request.enable_punctuation
        }
    )

async def simulate_sarvam_tts(request: TTSRequest) -> SarvamResponse:
    """Simulate Sarvam text-to-speech for demo"""
    
    await asyncio.sleep(1.2)
    
    # Mock audio data
    mock_audio = b"mock_audio_content_representing_hindi_tts"
    estimated_duration = len(request.text) * 0.08  # 8 chars per second
    
    return SarvamResponse(
        content=mock_audio,
        model="sarvam-speech",
        language=request.target_language,
        processing_time_ms=1200,
        cost_inr=estimated_duration * 0.02,  # ₹0.02 per second
        request_id=str(uuid.uuid4()),
        metadata={
            "audio_duration_seconds": estimated_duration,
            "audio_format": request.audio_format,
            "sample_rate": request.sample_rate,
            "text_length": len(request.text)
        }
    )

async def simulate_sarvam_embeddings(request: EmbeddingRequest) -> SarvamResponse:
    """Simulate Sarvam embeddings generation for demo"""
    
    await asyncio.sleep(0.6)
    
    # Generate mock embeddings (384-dimensional for demo)
    import numpy as np
    np.random.seed(42)  # For consistent demo results
    
    embeddings = []
    for text in request.texts:
        # Generate deterministic embedding based on text hash
        text_hash = hash(text)
        np.random.seed(text_hash % (2**31))
        embedding = np.random.normal(0, 1, 384).tolist()
        
        # Normalize if requested
        if request.normalize_embeddings:
            norm = np.linalg.norm(embedding)
            embedding = (np.array(embedding) / norm).tolist()
        
        embeddings.append(embedding)
    
    total_tokens = sum(len(text.split()) for text in request.texts)
    
    return SarvamResponse(
        content=embeddings,
        model=request.model.value,
        language=request.language,
        processing_time_ms=600,
        cost_inr=total_tokens * 0.00015,
        request_id=str(uuid.uuid4()),
        metadata={
            "embedding_dimension": 384,
            "num_texts": len(request.texts),
            "tokens_used": total_tokens,
            "normalized": request.normalize_embeddings
        }
    )

async def simulate_sarvam_vision(request: VisionRequest) -> SarvamResponse:
    """Simulate Sarvam vision understanding for demo"""
    
    await asyncio.sleep(2.0)
    
    mock_description = """इस तस्वीर में एक भारतीय गाँव का दृश्य दिखाया गया है। यहाँ हरे-भरे खेत नज़र आ रहे हैं और कुछ किसान अपने काम में व्यस्त हैं। पीछे की ओर पारंपरिक भारतीय घर दिखाई दे रहे हैं। आसमान साफ़ है और मौसम अच्छा लग रहा है। यह एक शांत और सुंदर ग्रामीण परिवेश है।"""
    
    return SarvamResponse(
        content=mock_description,
        model=request.model.value,
        language=request.language,
        processing_time_ms=2000,
        cost_inr=0.65,  # ₹0.50 for image + text tokens
        request_id=str(uuid.uuid4()),
        confidence_score=0.87,
        metadata={
            "image_size_bytes": len(request.image_data),
            "detail_level": request.detail_level,
            "tokens_used": 85,
            "objects_detected": ["किसान", "खेत", "घर", "आसमान"],
            "scenes_detected": ["ग्रामीण क्षेत्र", "कृषि भूमि"]
        }
    )

if __name__ == "__main__":
    asyncio.run(demo_sarvam_ai_integration())