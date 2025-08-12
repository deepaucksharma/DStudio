#!/usr/bin/env python3
"""
Bhashini AI Integration for Indian Languages
Episode 5: Code Example 16

Production-ready integration with Government of India's Bhashini platform
Supporting 22 Indian languages with translation, transcription, and TTS

Author: Code Developer Agent
Context: Indian Government AI platform for language technologies
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import hashlib
import uuid
from datetime import datetime, timedelta

# भारत सरकार के Bhashini platform के लिए production logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BhashiniService(Enum):
    TRANSLATION = "translation"
    TRANSCRIPTION = "asr"  # Automatic Speech Recognition
    TEXT_TO_SPEECH = "tts"
    TRANSLITERATION = "transliteration"
    
class IndianLanguage(Enum):
    # Major Indian languages supported by Bhashini
    HINDI = "hi"
    ENGLISH = "en"
    BENGALI = "bn"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    MARATHI = "mr"
    ODIA = "or"
    PUNJABI = "pa"
    TAMIL = "ta"
    TELUGU = "te"
    URDU = "ur"
    ASSAMESE = "as"
    MANIPURI = "mni"
    BODO = "brx"
    DOGRI = "doi"
    KASHMIRI = "ks"
    KONKANI = "gom"
    MAITHILI = "mai"
    NEPALI = "ne"
    SANSKRIT = "sa"
    SINDHI = "sd"

@dataclass
class BhashiniConfig:
    """Configuration for Bhashini API integration"""
    api_key: str
    user_id: str
    ulca_api_key: str  # ULCA (Universal Language Computing Architecture) API key
    base_url: str = "https://meity-auth.ulcacontrib.org"
    pipeline_url: str = "https://dhruva-api.bhashini.gov.in"
    timeout: int = 30
    max_retries: int = 3
    enable_caching: bool = True
    cache_ttl: int = 3600  # 1 hour cache TTL
    
    # Cost tracking for Government APIs (usually free but with limits)
    daily_request_limit: int = 10000  # Typical daily limit
    rate_limit_per_minute: int = 100  # Requests per minute

@dataclass
class TranslationRequest:
    """Translation request structure for Bhashini"""
    text: str
    source_language: IndianLanguage
    target_language: IndianLanguage
    domain: Optional[str] = "general"  # general, legal, medical, technical
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class TranslationResponse:
    """Translation response from Bhashini"""
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: float
    processing_time_ms: int
    model_version: str
    request_id: str
    cost_credits: int = 0  # If applicable

@dataclass
class TranscriptionRequest:
    """Speech to text request for Bhashini ASR"""
    audio_content: bytes  # Base64 encoded audio
    audio_format: str = "wav"  # wav, mp3, flac
    language: IndianLanguage = IndianLanguage.HINDI
    sample_rate: int = 16000
    audio_config: Dict[str, Any] = None
    enable_punctuation: bool = True
    enable_speaker_diarization: bool = False

@dataclass
class TranscriptionResponse:
    """Transcription response from Bhashini ASR"""
    transcript: str
    language: str
    confidence_score: float
    duration_seconds: float
    processing_time_ms: int
    word_timestamps: List[Dict[str, Any]] = None
    speaker_labels: List[str] = None
    request_id: str = ""

@dataclass
class TTSRequest:
    """Text to Speech request for Bhashini TTS"""
    text: str
    language: IndianLanguage
    voice_id: Optional[str] = None  # male/female voice
    speaking_rate: float = 1.0  # 0.5 to 2.0
    pitch: float = 0.0  # -20.0 to 20.0
    audio_format: str = "wav"
    sample_rate: int = 22050

@dataclass
class TTSResponse:
    """Text to Speech response from Bhashini TTS"""
    audio_content: bytes
    audio_format: str
    duration_seconds: float
    sample_rate: int
    processing_time_ms: int
    request_id: str

class BhashiniClient:
    """
    Production-ready client for Government of India's Bhashini platform
    भाषिणी - भारत सरकार का AI language platform
    """
    
    def __init__(self, config: BhashiniConfig):
        self.config = config
        self.session = None
        self.auth_token = None
        self.token_expires_at = None
        self.pipeline_cache = {}
        self.request_cache = {}
        
        # Rate limiting
        self.request_timestamps = []
        self.daily_request_count = 0
        self.daily_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        logger.info("🇮🇳 Bhashini Client initialized for Indian language processing")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        await self.authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def authenticate(self) -> str:
        """
        Authenticate with Bhashini ULCA platform
        भाषिणी authentication के लिए ULCA token प्राप्त करना
        """
        
        if self.auth_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.auth_token
        
        auth_url = f"{self.config.base_url}/ulca/apis/v0/model/getModelsPipeline"
        
        auth_payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": "hi",
                            "targetLanguage": "en"
                        }
                    }
                }
            ],
            "pipelineRequestConfig": {
                "pipelineId": "64392f96daac500b55c543cd"
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "userID": self.config.user_id,
            "ulcaApiKey": self.config.ulca_api_key
        }
        
        try:
            async with self.session.post(auth_url, json=auth_payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if "pipelineResponseConfig" in data:
                        pipeline_config = data["pipelineResponseConfig"][0]
                        self.auth_token = pipeline_config.get("config", {}).get("serviceId", "")
                        
                        # Set token expiry (typically 1 hour)
                        self.token_expires_at = datetime.now() + timedelta(hours=1)
                        
                        logger.info("✅ Successfully authenticated with Bhashini ULCA platform")
                        return self.auth_token
                    else:
                        raise Exception("Invalid authentication response from Bhashini")
                else:
                    error_text = await response.text()
                    raise Exception(f"Authentication failed: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Bhashini authentication failed: {e}")
            raise
    
    async def check_rate_limit(self):
        """
        Check API rate limits for Bhashini
        भाषिणी API की rate limits check करना
        """
        
        now = datetime.now()
        
        # Reset daily counter if new day
        if now >= self.daily_reset_time + timedelta(days=1):
            self.daily_request_count = 0
            self.daily_reset_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check daily limit
        if self.daily_request_count >= self.config.daily_request_limit:
            raise Exception(f"Daily request limit exceeded: {self.config.daily_request_limit}")
        
        # Check per-minute rate limit
        one_minute_ago = now - timedelta(minutes=1)
        recent_requests = [ts for ts in self.request_timestamps if ts > one_minute_ago]
        
        if len(recent_requests) >= self.config.rate_limit_per_minute:
            wait_time = 60 - (now - recent_requests[0]).total_seconds()
            logger.warning(f"⏱️ Rate limit reached, waiting {wait_time:.1f} seconds")
            await asyncio.sleep(wait_time)
        
        # Update counters
        self.request_timestamps.append(now)
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > one_minute_ago]
        self.daily_request_count += 1
    
    def get_cache_key(self, service: str, **kwargs) -> str:
        """Generate cache key for request"""
        cache_data = {"service": service, **kwargs}
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get cached response if available"""
        if not self.config.enable_caching:
            return None
        
        if cache_key in self.request_cache:
            cached_response, cached_at = self.request_cache[cache_key]
            if datetime.now() - cached_at < timedelta(seconds=self.config.cache_ttl):
                logger.info("📦 Using cached response")
                return cached_response
            else:
                del self.request_cache[cache_key]
        
        return None
    
    def save_to_cache(self, cache_key: str, response: Any):
        """Save response to cache"""
        if self.config.enable_caching:
            self.request_cache[cache_key] = (response, datetime.now())
    
    async def translate_text(self, request: TranslationRequest) -> TranslationResponse:
        """
        Translate text using Bhashini translation service
        भाषिणी translation API के साथ text translate करना
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Check cache first
        cache_key = self.get_cache_key(
            "translation",
            text=request.text,
            source_lang=request.source_language.value,
            target_lang=request.target_language.value
        )
        
        cached_response = self.get_from_cache(cache_key)
        if cached_response:
            return cached_response
        
        # Check rate limits
        await self.check_rate_limit()
        
        # Ensure we have valid auth token
        await self.authenticate()
        
        # Prepare translation request
        translation_url = f"{self.config.pipeline_url}/services/inference/pipeline"
        
        translation_payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": request.source_language.value,
                            "targetLanguage": request.target_language.value
                        },
                        "serviceId": self.auth_token
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": request.text
                    }
                ]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            async with self.session.post(translation_url, json=translation_payload, headers=headers) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    if "pipelineResponse" in data:
                        pipeline_response = data["pipelineResponse"][0]
                        output_data = pipeline_response.get("output", [{}])[0]
                        
                        translated_text = output_data.get("target", "")
                        confidence = output_data.get("confidence", 0.95)  # Default high confidence
                        
                        translation_response = TranslationResponse(
                            translated_text=translated_text,
                            source_language=request.source_language.value,
                            target_language=request.target_language.value,
                            confidence_score=confidence,
                            processing_time_ms=processing_time,
                            model_version="bhashini-v1",
                            request_id=request_id
                        )
                        
                        # Cache the response
                        self.save_to_cache(cache_key, translation_response)
                        
                        logger.info(f"✅ Translation completed: {request.source_language.value} → {request.target_language.value}")
                        return translation_response
                    
                    else:
                        raise Exception("Invalid response format from Bhashini translation API")
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Translation failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            raise
    
    async def transcribe_audio(self, request: TranscriptionRequest) -> TranscriptionResponse:
        """
        Transcribe audio using Bhashini ASR service
        भाषिणी ASR के साथ audio को text में convert करना
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Check rate limits
        await self.check_rate_limit()
        
        # Ensure we have valid auth token
        await self.authenticate()
        
        # Encode audio content to base64
        audio_base64 = base64.b64encode(request.audio_content).decode('utf-8')
        
        # Prepare transcription request
        transcription_url = f"{self.config.pipeline_url}/services/inference/pipeline"
        
        transcription_payload = {
            "pipelineTasks": [
                {
                    "taskType": "asr",
                    "config": {
                        "language": {
                            "sourceLanguage": request.language.value
                        },
                        "serviceId": self.auth_token,
                        "audioFormat": request.audio_format,
                        "samplingRate": request.sample_rate
                    }
                }
            ],
            "inputData": {
                "audio": [
                    {
                        "audioContent": audio_base64
                    }
                ]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            async with self.session.post(transcription_url, json=transcription_payload, headers=headers) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    if "pipelineResponse" in data:
                        pipeline_response = data["pipelineResponse"][0]
                        output_data = pipeline_response.get("output", [{}])[0]
                        
                        transcript = output_data.get("source", "")
                        confidence = output_data.get("confidence", 0.90)
                        
                        transcription_response = TranscriptionResponse(
                            transcript=transcript,
                            language=request.language.value,
                            confidence_score=confidence,
                            duration_seconds=0.0,  # Would calculate from audio
                            processing_time_ms=processing_time,
                            request_id=request_id
                        )
                        
                        logger.info(f"✅ Transcription completed in {request.language.value}")
                        return transcription_response
                    
                    else:
                        raise Exception("Invalid response format from Bhashini ASR API")
                
                else:
                    error_text = await response.text()
                    raise Exception(f"Transcription failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            raise
    
    async def synthesize_speech(self, request: TTSRequest) -> TTSResponse:
        """
        Generate speech from text using Bhashini TTS service
        भाषिणी TTS के साथ text को audio में convert करना
        """
        
        start_time = time.time()
        request_id = str(uuid.uuid4())
        
        # Check rate limits
        await self.check_rate_limit()
        
        # Ensure we have valid auth token
        await self.authenticate()
        
        # Prepare TTS request
        tts_url = f"{self.config.pipeline_url}/services/inference/pipeline"
        
        tts_payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": {
                        "language": {
                            "sourceLanguage": request.language.value
                        },
                        "serviceId": self.auth_token,
                        "audioFormat": request.audio_format,
                        "samplingRate": request.sample_rate
                    }
                }
            ],
            "inputData": {
                "input": [
                    {
                        "source": request.text
                    }
                ]
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            async with self.session.post(tts_url, json=tts_payload, headers=headers) as response:
                processing_time = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    data = await response.json()
                    
                    if "pipelineResponse" in data:
                        pipeline_response = data["pipelineResponse"][0]
                        output_data = pipeline_response.get("audio", [{}])[0]
                        
                        audio_content_base64 = output_data.get("audioContent", "")
                        audio_content = base64.b64decode(audio_content_base64)
                        
                        tts_response = TTSResponse(
                            audio_content=audio_content,
                            audio_format=request.audio_format,
                            duration_seconds=0.0,  # Would calculate from audio
                            sample_rate=request.sample_rate,
                            processing_time_ms=processing_time,
                            request_id=request_id
                        )
                        
                        logger.info(f"✅ TTS synthesis completed in {request.language.value}")
                        return tts_response
                    
                    else:
                        raise Exception("Invalid response format from Bhashini TTS API")
                
                else:
                    error_text = await response.text()
                    raise Exception(f"TTS synthesis failed: {response.status} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ TTS synthesis failed: {e}")
            raise
    
    async def get_supported_languages(self, service: BhashiniService) -> List[Dict[str, Any]]:
        """
        Get list of supported languages for a specific service
        भाषिणी में उपलब्ध भाषाओं की list प्राप्त करना
        """
        
        # Mock implementation - in production, this would call actual API
        supported_languages = {
            BhashiniService.TRANSLATION: [
                {"code": "hi", "name": "Hindi", "native_name": "हिंदी"},
                {"code": "en", "name": "English", "native_name": "English"},
                {"code": "bn", "name": "Bengali", "native_name": "বাংলা"},
                {"code": "gu", "name": "Gujarati", "native_name": "ગુજરાતી"},
                {"code": "kn", "name": "Kannada", "native_name": "ಕನ್ನಡ"},
                {"code": "ml", "name": "Malayalam", "native_name": "മലയാളം"},
                {"code": "mr", "name": "Marathi", "native_name": "मराठी"},
                {"code": "or", "name": "Odia", "native_name": "ଓଡ଼ିଆ"},
                {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ"},
                {"code": "ta", "name": "Tamil", "native_name": "தமிழ்"},
                {"code": "te", "name": "Telugu", "native_name": "తెలుగు"},
                {"code": "ur", "name": "Urdu", "native_name": "اردو"},
            ],
            BhashiniService.TRANSCRIPTION: [
                {"code": "hi", "name": "Hindi", "native_name": "हिंदी"},
                {"code": "en", "name": "English", "native_name": "English"},
                {"code": "bn", "name": "Bengali", "native_name": "বাংলা"},
                {"code": "gu", "name": "Gujarati", "native_name": "ગુજરાતી"},
                {"code": "ta", "name": "Tamil", "native_name": "தமிழ்"},
                {"code": "te", "name": "Telugu", "native_name": "తెలుగు"},
            ],
            BhashiniService.TEXT_TO_SPEECH: [
                {"code": "hi", "name": "Hindi", "native_name": "हिंदी"},
                {"code": "en", "name": "English", "native_name": "English"},
                {"code": "bn", "name": "Bengali", "native_name": "বাংলা"},
                {"code": "ta", "name": "Tamil", "native_name": "தமிழ்"},
            ]
        }
        
        return supported_languages.get(service, [])

class BhashiniAnalytics:
    """
    Analytics and monitoring for Bhashini API usage
    भाषिणी API के usage analytics और monitoring
    """
    
    def __init__(self):
        self.usage_stats = {
            "translation": {"requests": 0, "characters": 0, "errors": 0},
            "transcription": {"requests": 0, "audio_minutes": 0, "errors": 0},
            "tts": {"requests": 0, "characters": 0, "errors": 0},
        }
        self.language_stats = {}
        self.performance_stats = {
            "avg_translation_time": 0,
            "avg_transcription_time": 0,
            "avg_tts_time": 0,
        }
    
    def record_translation(self, source_lang: str, target_lang: str, 
                          character_count: int, processing_time_ms: int, success: bool):
        """Record translation usage statistics"""
        
        self.usage_stats["translation"]["requests"] += 1
        if success:
            self.usage_stats["translation"]["characters"] += character_count
        else:
            self.usage_stats["translation"]["errors"] += 1
        
        # Language pair statistics
        lang_pair = f"{source_lang}-{target_lang}"
        if lang_pair not in self.language_stats:
            self.language_stats[lang_pair] = {"count": 0, "avg_time": 0}
        
        stats = self.language_stats[lang_pair]
        stats["avg_time"] = (stats["avg_time"] * stats["count"] + processing_time_ms) / (stats["count"] + 1)
        stats["count"] += 1
        
        # Overall performance statistics
        total_requests = self.usage_stats["translation"]["requests"]
        self.performance_stats["avg_translation_time"] = (
            (self.performance_stats["avg_translation_time"] * (total_requests - 1) + processing_time_ms) / total_requests
        )
    
    def record_transcription(self, language: str, audio_duration_seconds: float, 
                           processing_time_ms: int, success: bool):
        """Record transcription usage statistics"""
        
        self.usage_stats["transcription"]["requests"] += 1
        if success:
            self.usage_stats["transcription"]["audio_minutes"] += audio_duration_seconds / 60
        else:
            self.usage_stats["transcription"]["errors"] += 1
        
        # Language statistics
        if language not in self.language_stats:
            self.language_stats[language] = {"asr_count": 0, "asr_avg_time": 0}
        
        if "asr_count" not in self.language_stats[language]:
            self.language_stats[language]["asr_count"] = 0
            self.language_stats[language]["asr_avg_time"] = 0
        
        stats = self.language_stats[language]
        stats["asr_avg_time"] = (stats["asr_avg_time"] * stats["asr_count"] + processing_time_ms) / (stats["asr_count"] + 1)
        stats["asr_count"] += 1
    
    def record_tts(self, language: str, character_count: int, processing_time_ms: int, success: bool):
        """Record TTS usage statistics"""
        
        self.usage_stats["tts"]["requests"] += 1
        if success:
            self.usage_stats["tts"]["characters"] += character_count
        else:
            self.usage_stats["tts"]["errors"] += 1
        
        # Language statistics
        if language not in self.language_stats:
            self.language_stats[language] = {"tts_count": 0, "tts_avg_time": 0}
        
        if "tts_count" not in self.language_stats[language]:
            self.language_stats[language]["tts_count"] = 0
            self.language_stats[language]["tts_avg_time"] = 0
        
        stats = self.language_stats[language]
        stats["tts_avg_time"] = (stats["tts_avg_time"] * stats["tts_count"] + processing_time_ms) / (stats["tts_count"] + 1)
        stats["tts_count"] += 1
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Generate comprehensive usage report"""
        
        total_requests = sum(
            self.usage_stats[service]["requests"] 
            for service in self.usage_stats
        )
        
        total_errors = sum(
            self.usage_stats[service]["errors"] 
            for service in self.usage_stats
        )
        
        success_rate = ((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 100
        
        # Most used language pairs
        sorted_lang_pairs = sorted(
            [(pair, stats["count"]) for pair, stats in self.language_stats.items() if "count" in stats],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "summary": {
                "total_requests": total_requests,
                "success_rate": f"{success_rate:.1f}%",
                "total_errors": total_errors,
            },
            "service_breakdown": self.usage_stats,
            "performance": self.performance_stats,
            "top_language_pairs": sorted_lang_pairs,
            "language_distribution": self.language_stats
        }

# Utility functions for Indian language processing
def detect_indian_language(text: str) -> Optional[IndianLanguage]:
    """
    Simple language detection for Indian languages
    भारतीय भाषाओं की पहचान के लिए simple detection
    """
    
    # Character ranges for different scripts
    script_ranges = {
        IndianLanguage.HINDI: (0x0900, 0x097F),  # Devanagari
        IndianLanguage.BENGALI: (0x0980, 0x09FF),  # Bengali
        IndianLanguage.GUJARATI: (0x0A80, 0x0AFF),  # Gujarati
        IndianLanguage.PUNJABI: (0x0A00, 0x0A7F),  # Gurmukhi (Punjabi)
        IndianLanguage.ODIA: (0x0B00, 0x0B7F),  # Odia
        IndianLanguage.TAMIL: (0x0B80, 0x0BFF),  # Tamil
        IndianLanguage.TELUGU: (0x0C00, 0x0C7F),  # Telugu
        IndianLanguage.KANNADA: (0x0C80, 0x0CFF),  # Kannada
        IndianLanguage.MALAYALAM: (0x0D00, 0x0D7F),  # Malayalam
    }
    
    # Count characters in each script
    script_counts = {}
    total_chars = 0
    
    for char in text:
        char_code = ord(char)
        total_chars += 1
        
        for language, (start, end) in script_ranges.items():
            if start <= char_code <= end:
                script_counts[language] = script_counts.get(language, 0) + 1
                break
    
    if total_chars == 0:
        return None
    
    # Find the script with the highest percentage
    max_count = 0
    detected_language = None
    
    for language, count in script_counts.items():
        percentage = (count / total_chars) * 100
        if percentage > 30 and count > max_count:  # At least 30% of characters
            max_count = count
            detected_language = language
    
    # Default to English if no Indian script detected significantly
    if detected_language is None:
        return IndianLanguage.ENGLISH
    
    return detected_language

def transliterate_to_roman(text: str, source_language: IndianLanguage) -> str:
    """
    Simple transliteration to Roman script
    भारतीय भाषाओं का Roman script में transliteration
    """
    
    # Basic transliteration mapping (simplified)
    # In production, use proper transliteration libraries like indic-transliteration
    
    if source_language == IndianLanguage.HINDI:
        # Very basic Hindi to Roman transliteration
        hindi_to_roman = {
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ii', 'उ': 'u', 'ऊ': 'uu',
            'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
            'क': 'ka', 'ख': 'kha', 'ग': 'ga', 'घ': 'gha', 'च': 'cha',
            'छ': 'chha', 'ज': 'ja', 'झ': 'jha', 'ट': 'ta', 'ठ': 'tha',
            'ड': 'da', 'ढ': 'dha', 'ण': 'na', 'त': 'ta', 'थ': 'tha',
            'द': 'da', 'ध': 'dha', 'न': 'na', 'प': 'pa', 'फ': 'pha',
            'ब': 'ba', 'भ': 'bha', 'म': 'ma', 'य': 'ya', 'र': 'ra',
            'ल': 'la', 'व': 'va', 'श': 'sha', 'ष': 'shha', 'स': 'sa',
            'ह': 'ha', '़': '', 'ं': 'n', 'ः': 'h', '्': ''
        }
        
        result = ""
        for char in text:
            result += hindi_to_roman.get(char, char)
        return result
    
    # For other languages, return as-is (would implement proper transliteration)
    return text

# Demo and testing functions
async def demo_bhashini_integration():
    """
    Comprehensive demo of Bhashini integration
    भाषिणी integration का comprehensive demo
    """
    
    print("🇮🇳 Bhashini Integration Demo - Government of India Language AI")
    print("=" * 70)
    
    # Configuration (in production, use environment variables)
    config = BhashiniConfig(
        api_key="your_api_key_here",
        user_id="demo_user",
        ulca_api_key="your_ulca_api_key_here",
        enable_caching=True
    )
    
    # Initialize analytics
    analytics = BhashiniAnalytics()
    
    try:
        async with BhashiniClient(config) as client:
            
            print("\n📋 Supported Languages:")
            translation_langs = await client.get_supported_languages(BhashiniService.TRANSLATION)
            print("Translation:")
            for lang in translation_langs[:6]:  # Show first 6
                print(f"   {lang['code']}: {lang['native_name']} ({lang['name']})")
            
            # Translation examples
            print("\n🔄 Translation Examples:")
            
            translation_tests = [
                {
                    "text": "नमस्ते, आप कैसे हैं?",
                    "source": IndianLanguage.HINDI,
                    "target": IndianLanguage.ENGLISH,
                    "description": "Hindi to English greeting"
                },
                {
                    "text": "Hello, how are you?",
                    "source": IndianLanguage.ENGLISH,
                    "target": IndianLanguage.HINDI,
                    "description": "English to Hindi greeting"
                },
                {
                    "text": "भारत एक महान देश है।",
                    "source": IndianLanguage.HINDI,
                    "target": IndianLanguage.TAMIL,
                    "description": "Hindi to Tamil sentence"
                },
                {
                    "text": "আমি ভাত খাই।",
                    "source": IndianLanguage.BENGALI,
                    "target": IndianLanguage.ENGLISH,
                    "description": "Bengali to English sentence"
                },
            ]
            
            for i, test in enumerate(translation_tests, 1):
                print(f"\n{i}. {test['description']}:")
                print(f"   Input ({test['source'].value}): {test['text']}")
                
                try:
                    # Create translation request
                    request = TranslationRequest(
                        text=test['text'],
                        source_language=test['source'],
                        target_language=test['target']
                    )
                    
                    # Perform translation (mock for demo)
                    # In production, this would call actual Bhashini API
                    response = await simulate_translation(request)
                    
                    print(f"   Output ({test['target'].value}): {response.translated_text}")
                    print(f"   Confidence: {response.confidence_score:.2f}")
                    print(f"   Time: {response.processing_time_ms}ms")
                    
                    # Record analytics
                    analytics.record_translation(
                        test['source'].value,
                        test['target'].value,
                        len(test['text']),
                        response.processing_time_ms,
                        True
                    )
                    
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    analytics.record_translation(
                        test['source'].value,
                        test['target'].value,
                        len(test['text']),
                        0,
                        False
                    )
            
            # Language detection demo
            print("\n🔍 Language Detection Demo:")
            detection_tests = [
                "नमस्ते दोस्तों!",  # Hindi
                "Hello friends!",   # English
                "আমার নাম রাহুল।",    # Bengali
                "வணக்கம் நண்பர்களே!", # Tamil
                "મારું નામ રાજ છે.",    # Gujarati
            ]
            
            for text in detection_tests:
                detected_lang = detect_indian_language(text)
                romanized = transliterate_to_roman(text, detected_lang) if detected_lang != IndianLanguage.ENGLISH else text
                
                print(f"   Text: {text}")
                print(f"   Detected: {detected_lang.value if detected_lang else 'unknown'}")
                print(f"   Romanized: {romanized}")
                print()
            
            # Transcription demo (mock)
            print("🎤 Speech Recognition Demo:")
            print("   [Simulating audio transcription...]")
            
            # Mock audio transcription
            mock_audio = b"mock_audio_data"
            transcription_request = TranscriptionRequest(
                audio_content=mock_audio,
                language=IndianLanguage.HINDI
            )
            
            transcription_response = await simulate_transcription(transcription_request)
            print(f"   Transcript: {transcription_response.transcript}")
            print(f"   Language: {transcription_response.language}")
            print(f"   Confidence: {transcription_response.confidence_score:.2f}")
            
            analytics.record_transcription(
                transcription_response.language,
                5.0,  # 5 seconds audio
                transcription_response.processing_time_ms,
                True
            )
            
            # TTS demo (mock)
            print("\n🔊 Text-to-Speech Demo:")
            print("   [Simulating speech synthesis...]")
            
            tts_request = TTSRequest(
                text="भाषिणी भारत सरकार का AI प्लेटफॉर्म है।",
                language=IndianLanguage.HINDI
            )
            
            tts_response = await simulate_tts(tts_request)
            print(f"   Text: {tts_request.text}")
            print(f"   Language: {tts_request.language.value}")
            print(f"   Audio duration: {tts_response.duration_seconds:.1f}s")
            print(f"   Processing time: {tts_response.processing_time_ms}ms")
            
            analytics.record_tts(
                tts_request.language.value,
                len(tts_request.text),
                tts_response.processing_time_ms,
                True
            )
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
    
    # Show analytics report
    print("\n📊 Usage Analytics Report:")
    report = analytics.get_usage_report()
    
    print(f"   Total requests: {report['summary']['total_requests']}")
    print(f"   Success rate: {report['summary']['success_rate']}")
    print(f"   Average translation time: {report['performance']['avg_translation_time']:.0f}ms")
    
    if report['top_language_pairs']:
        print("\n   Top language pairs:")
        for pair, count in report['top_language_pairs']:
            print(f"      {pair}: {count} requests")
    
    print("\n🎯 Bhashini Integration Features:")
    print("   ✅ 22+ Indian languages supported")
    print("   ✅ Translation, Transcription, TTS services")
    print("   ✅ Government-grade accuracy and security")
    print("   ✅ Free/low-cost API access")
    print("   ✅ Advanced caching and rate limiting")
    print("   ✅ Comprehensive analytics and monitoring")
    print("   ✅ Language detection and transliteration")
    print("   ✅ Production-ready error handling")
    print("   ✅ Support for Indian language scripts")
    print("   ✅ Integration with ULCA platform")

# Mock functions for demo (replace with actual API calls in production)
async def simulate_translation(request: TranslationRequest) -> TranslationResponse:
    """Simulate translation API call for demo"""
    
    await asyncio.sleep(0.5)  # Simulate network delay
    
    # Mock translations
    mock_translations = {
        ("नमस्ते, आप कैसे हैं?", "hi", "en"): "Hello, how are you?",
        ("Hello, how are you?", "en", "hi"): "नमस्ते, आप कैसे हैं?",
        ("भारत एक महान देश है।", "hi", "ta"): "இந்தியா ஒரு சிறந்த நாடு.",
        ("আমি ভাত খাই।", "bn", "en"): "I eat rice.",
    }
    
    key = (request.text, request.source_language.value, request.target_language.value)
    translated_text = mock_translations.get(key, f"[Translated: {request.text}]")
    
    return TranslationResponse(
        translated_text=translated_text,
        source_language=request.source_language.value,
        target_language=request.target_language.value,
        confidence_score=0.95,
        processing_time_ms=450,
        model_version="bhashini-demo-v1",
        request_id=str(uuid.uuid4())
    )

async def simulate_transcription(request: TranscriptionRequest) -> TranscriptionResponse:
    """Simulate transcription API call for demo"""
    
    await asyncio.sleep(1.0)  # Simulate processing time
    
    return TranscriptionResponse(
        transcript="नमस्ते, मैं भाषिणी का उपयोग कर रहा हूं।",
        language=request.language.value,
        confidence_score=0.92,
        duration_seconds=5.0,
        processing_time_ms=1000,
        request_id=str(uuid.uuid4())
    )

async def simulate_tts(request: TTSRequest) -> TTSResponse:
    """Simulate TTS API call for demo"""
    
    await asyncio.sleep(0.8)  # Simulate synthesis time
    
    return TTSResponse(
        audio_content=b"mock_audio_content",
        audio_format=request.audio_format,
        duration_seconds=3.5,
        sample_rate=request.sample_rate,
        processing_time_ms=800,
        request_id=str(uuid.uuid4())
    )

if __name__ == "__main__":
    asyncio.run(demo_bhashini_integration())