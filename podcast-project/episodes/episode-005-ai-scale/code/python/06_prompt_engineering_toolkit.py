#!/usr/bin/env python3
"""
Prompt Engineering Toolkit with Hindi/English Templates
Episode 5: Code Example 6

Production-ready prompt engineering system for Indian context
Supporting Hindi/English templates, chain-of-thought, few-shot learning

Author: Code Developer Agent
Context: Indian AI applications with multilingual prompt optimization
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import re
import hashlib
import asyncio
from abc import ABC, abstractmethod
import openai
import tiktoken

# Mumbai production logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptType(Enum):
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    TRANSLATION = "translation" 
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    CODE_GENERATION = "code_generation"
    CONVERSATIONAL = "conversational"

class Language(Enum):
    HINDI = "hi"
    ENGLISH = "en"
    MIXED = "hi_en"  # Code-mixed Hindi-English
    TAMIL = "ta"
    BENGALI = "bn"
    MARATHI = "mr"

@dataclass
class PromptTemplate:
    """Template for prompts with Indian context"""
    name: str
    type: PromptType
    language: Language
    template: str
    variables: List[str]
    few_shot_examples: List[Dict[str, str]]
    instructions: str
    constraints: List[str]
    cost_per_token_inr: float = 0.00002  # ₹0.00002 per token
    
    # Indian context specific
    cultural_context: Optional[str] = None
    regional_preference: Optional[str] = None
    formality_level: str = "neutral"  # formal, neutral, casual

@dataclass
class PromptExecutionResult:
    """Result of prompt execution"""
    prompt: str
    response: str
    token_count: int
    cost_inr: float
    execution_time_ms: float
    confidence: float
    language_detected: str
    quality_score: float
    
class PromptOptimizer:
    """
    Optimize prompts for better performance and cost efficiency
    Specialized for Indian languages and context
    """
    
    def __init__(self):
        self.optimization_history = []
        self.performance_cache = {}
        
    def optimize_for_hindi(self, prompt: str) -> str:
        """Optimize prompt for Hindi context"""
        
        optimizations = [
            # Add cultural context
            ("आप एक सहायक AI हैं जो भारतीय संस्कृति को समझते हैं।", "You are a helpful AI assistant."),
            
            # Use respectful language
            ("कृपया", "Please"),
            ("धन्यवाद", "Thank you"),
            
            # Add regional context markers
            ("भारतीय संदर्भ में", "in context"),
            ("हमारी परंपरा के अनुसार", "according to tradition"),
            
            # Use familiar examples
            ("जैसे कि Bollywood में", "like in movies"),
            ("भारत में आमतौर पर", "commonly in India"),
        ]
        
        optimized = prompt
        for hindi_phrase, english_phrase in optimizations:
            if english_phrase.lower() in prompt.lower():
                optimized = optimized.replace(english_phrase, f"{english_phrase} ({hindi_phrase})")
        
        return optimized
    
    def add_chain_of_thought(self, prompt: str, language: Language) -> str:
        """Add chain-of-thought reasoning to prompt"""
        
        if language == Language.HINDI or language == Language.MIXED:
            cot_instruction = """
कृपया step-by-step सोचें:
1. पहले problem को समझें
2. सभी options को देखें  
3. हर step को explain करें
4. Final answer दें

आपका जवाब:
"""
        else:
            cot_instruction = """
Please think step by step:
1. First understand the problem
2. Consider all options
3. Explain each reasoning step
4. Provide the final answer

Your response:
"""
        
        return prompt + "\n\n" + cot_instruction
    
    def optimize_token_usage(self, prompt: str) -> str:
        """Optimize prompt to reduce token usage while maintaining quality"""
        
        optimizations = [
            # Remove redundant words
            (r'\bvery very\b', 'extremely'),
            (r'\breally really\b', 'extremely'),
            (r'\bplease please\b', 'please'),
            
            # Compact common phrases
            (r'\bFor example\b', 'E.g.'),
            (r'\bThat is to say\b', 'I.e.'),
            (r'\bIn other words\b', 'I.e.'),
            
            # Remove excessive punctuation
            (r'[!]{2,}', '!'),
            (r'[?]{2,}', '?'),
            (r'[.]{3,}', '...'),
        ]
        
        optimized = prompt
        for pattern, replacement in optimizations:
            optimized = re.sub(pattern, replacement, optimized)
        
        # Remove extra whitespace
        optimized = ' '.join(optimized.split())
        
        return optimized

class IndianPromptTemplateLibrary:
    """
    Library of pre-built prompt templates for Indian context
    Covering common use cases in Indian applications
    """
    
    def __init__(self):
        self.templates = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize all prompt templates"""
        
        # Hindi Sentiment Analysis
        self.templates["hindi_sentiment"] = PromptTemplate(
            name="hindi_sentiment",
            type=PromptType.CLASSIFICATION,
            language=Language.HINDI,
            template="इस text का sentiment बताएं: '{text}'\n\nSentiment (positive/negative/neutral):",
            variables=["text"],
            few_shot_examples=[
                {
                    "input": "यह फिल्म बहुत अच्छी है!",
                    "output": "positive"
                },
                {
                    "input": "मुझे यह product पसंद नहीं आया",
                    "output": "negative" 
                },
                {
                    "input": "यह ठीक है",
                    "output": "neutral"
                }
            ],
            instructions="भारतीय भाषा और cultural context को ध्यान में रखकर sentiment analyze करें।",
            constraints=["Only return: positive, negative, or neutral", "Consider Hindi cultural expressions"],
            cultural_context="Indian emotional expressions",
            formality_level="neutral"
        )
        
        # Code-mixed Customer Support
        self.templates["customer_support_mixed"] = PromptTemplate(
            name="customer_support_mixed",
            type=PromptType.CONVERSATIONAL,
            language=Language.MIXED,
            template="""आप एक helpful customer support agent हैं। Customer की query का polite और helpful answer दें।

Customer: {query}

आपका response (Hindi और English mix में):""",
            variables=["query"],
            few_shot_examples=[
                {
                    "input": "Mera order abhi tak nahi aaya hai",
                    "output": "मुझे खुशी होगी आपकी help करने में। आपका order number क्या है? Main check करूंगा कि आपका order कहां है और delivery कब होगी।"
                }
            ],
            instructions="Mix Hindi और English naturally। Respectful और helpful रहें।",
            constraints=["Use respectful tone", "Mix languages naturally", "Provide actionable help"],
            cultural_context="Indian customer service expectations",
            formality_level="formal"
        )
        
        # Indian Recipe Generation
        self.templates["indian_recipe"] = PromptTemplate(
            name="indian_recipe",
            type=PromptType.GENERATION,
            language=Language.MIXED,
            template="""एक authentic {dish_name} recipe बनाएं जो {region} style में हो।

Include करें:
- Ingredients list (Hindi names के साथ)
- Step-by-step instructions
- Cooking time और servings
- Tips for best results

Recipe:""",
            variables=["dish_name", "region"],
            few_shot_examples=[
                {
                    "input": "dish_name: Biryani, region: Hyderabadi",
                    "output": "# Hyderabadi Biryani Recipe\n\n## Ingredients:\n- बासमती चावल (Basmati Rice) - 2 cups\n- मटन (Mutton) - 500g..."
                }
            ],
            instructions="Authentic Indian cooking methods use करें। Regional variations को highlight करें।",
            constraints=["Use authentic ingredients", "Include Hindi names", "Regional authenticity"],
            cultural_context="Indian cooking traditions",
            regional_preference="region-specific",
            formality_level="neutral"
        )
        
        # Financial Advice (Indian Context)
        self.templates["financial_advice"] = PromptTemplate(
            name="financial_advice",
            type=PromptType.QUESTION_ANSWERING,
            language=Language.MIXED,
            template="""आप एक financial advisor हैं जो Indian financial system को अच्छे से जानते हैं।

Question: {question}

कृपया इन points को cover करें:
1. Indian context में practical advice
2. Tax implications (if applicable)
3. Risk factors
4. Recommended actions

आपका detailed answer:""",
            variables=["question"],
            few_shot_examples=[
                {
                    "input": "Should I invest in mutual funds or FD?",
                    "output": "Indian market में यह एक common dilemma है। आपकी age, risk appetite, और financial goals के according choice करनी चाहिए..."
                }
            ],
            instructions="Indian financial regulations और tax laws के according advice दें।",
            constraints=["Consider Indian tax laws", "Mention regulatory bodies like SEBI", "Practical actionable advice"],
            cultural_context="Indian financial ecosystem",
            formality_level="formal"
        )
        
        # Programming Help (Indian Context)
        self.templates["programming_help"] = PromptTemplate(
            name="programming_help",
            type=PromptType.CODE_GENERATION,
            language=Language.MIXED,
            template="""आप एक senior software developer हैं जो Indian software industry में काम करते हैं।

Problem: {problem_description}

कृपया provide करें:
1. Working code solution
2. Explanation in Hindi-English mix
3. Best practices for Indian software companies
4. Performance considerations

आपका solution:""",
            variables=["problem_description"],
            few_shot_examples=[
                {
                    "input": "Create a function to validate Indian mobile numbers",
                    "output": "यहाँ है Indian mobile number validation का function:\n\n```python\ndef validate_indian_mobile(number):\n    import re\n    # Indian mobile pattern: +91 followed by 10 digits\n    pattern = r'^(\+91|91)?[6-9]\d{9}$'\n    return bool(re.match(pattern, str(number)))\n```"
                }
            ],
            instructions="Code comments Hindi में भी दें। Indian use cases consider करें।",
            constraints=["Working code only", "Include Hindi comments", "Consider Indian standards"],
            cultural_context="Indian software development practices",
            formality_level="neutral"
        )
        
        logger.info(f"Initialized {len(self.templates)} prompt templates")
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get template by name"""
        return self.templates.get(name)
    
    def list_templates(self, prompt_type: Optional[PromptType] = None, 
                      language: Optional[Language] = None) -> List[str]:
        """List available templates with optional filtering"""
        
        filtered = []
        for name, template in self.templates.items():
            if prompt_type and template.type != prompt_type:
                continue
            if language and template.language != language:
                continue
            filtered.append(name)
        
        return filtered

class PromptExecutor:
    """
    Execute prompts with cost tracking and performance monitoring
    Supports multiple AI providers optimized for Indian use cases
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.execution_history = []
        self.total_cost_inr = 0.0
        self.total_tokens = 0
        
        # Token encoder for cost calculation
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        except:
            self.encoder = None
            logger.warning("Tiktoken not available, using approximate token counting")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoder:
            return len(self.encoder.encode(text))
        else:
            # Approximate: 1 token ≈ 4 characters for English, 2-3 for Hindi
            hindi_chars = len([c for c in text if ord(c) > 0x0900 and ord(c) < 0x097F])
            english_chars = len(text) - hindi_chars
            return int(english_chars / 4 + hindi_chars / 2.5)
    
    async def execute_prompt(self, 
                           template: PromptTemplate,
                           variables: Dict[str, str],
                           model: str = "gpt-3.5-turbo") -> PromptExecutionResult:
        """
        Execute a prompt template with given variables
        Returns result with cost and performance metrics
        """
        
        start_time = time.time()
        
        # Build the final prompt
        final_prompt = self._build_prompt(template, variables)
        
        # Count tokens
        prompt_tokens = self.count_tokens(final_prompt)
        
        try:
            # Mock AI response (in production, use actual API)
            response = await self._mock_ai_response(final_prompt, template)
            response_tokens = self.count_tokens(response)
            
            # Calculate cost
            total_tokens = prompt_tokens + response_tokens
            cost_inr = total_tokens * template.cost_per_token_inr
            
            # Execution time
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Quality metrics
            quality_score = self._calculate_quality_score(response, template)
            confidence = self._calculate_confidence(response, template)
            
            # Language detection
            language_detected = self._detect_language(response)
            
            # Update totals
            self.total_cost_inr += cost_inr
            self.total_tokens += total_tokens
            
            result = PromptExecutionResult(
                prompt=final_prompt,
                response=response,
                token_count=total_tokens,
                cost_inr=cost_inr,
                execution_time_ms=execution_time_ms,
                confidence=confidence,
                language_detected=language_detected,
                quality_score=quality_score
            )
            
            # Store in history
            self.execution_history.append(result)
            
            logger.info(f"Prompt executed: {total_tokens} tokens, "
                       f"₹{cost_inr:.4f}, {execution_time_ms:.1f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Prompt execution failed: {e}")
            raise
    
    def _build_prompt(self, template: PromptTemplate, variables: Dict[str, str]) -> str:
        """Build final prompt from template and variables"""
        
        prompt = template.template
        
        # Replace variables
        for var, value in variables.items():
            prompt = prompt.replace(f"{{{var}}}", value)
        
        # Add few-shot examples if available
        if template.few_shot_examples:
            examples_text = "\n\nExamples:\n"
            for i, example in enumerate(template.few_shot_examples[:3], 1):  # Limit to 3 examples
                examples_text += f"\nExample {i}:\nInput: {example['input']}\nOutput: {example['output']}\n"
            
            # Insert examples before the main prompt
            prompt = examples_text + "\n" + prompt
        
        # Add instructions
        if template.instructions:
            instructions_text = f"\nInstructions: {template.instructions}\n"
            prompt = instructions_text + prompt
        
        return prompt
    
    async def _mock_ai_response(self, prompt: str, template: PromptTemplate) -> str:
        """
        Mock AI response for testing
        In production, replace with actual AI API calls
        """
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        # Generate mock response based on template type
        if template.type == PromptType.CLASSIFICATION:
            responses = ["positive", "negative", "neutral"]
            return f"{responses[hash(prompt) % len(responses)]}"
        
        elif template.type == PromptType.GENERATION:
            if "recipe" in template.name:
                return """# मटर पनीर Recipe

## Ingredients:
- पनीर (Paneer) - 200g
- मटर (Green Peas) - 1 cup
- प्याज (Onions) - 2 medium
- टमाटर (Tomatoes) - 3 medium

## Instructions:
1. पनीर को cubes में cut करें
2. Oil में onions को golden brown करें
3. Tomatoes add करके paste बनाएं
4. Spices डालें और पनीर add करें
5. 10 minutes cook करें

Cooking time: 30 minutes | Servings: 4"""
            
            else:
                return "यह एक sample response है जो actual AI model से generate होगा।"
        
        elif template.type == PromptType.CONVERSATIONAL:
            return "मैं आपकी help करने के लिए यहाँ हूँ। आपका query clear करने के लिए main try करूंगा।"
        
        elif template.type == PromptType.CODE_GENERATION:
            return """```python
def validate_indian_mobile(mobile):
    import re
    # Indian mobile number pattern
    pattern = r'^(\+91|91)?[6-9]\d{9}$'
    return bool(re.match(pattern, str(mobile)))

# Test करें
print(validate_indian_mobile("9876543210"))  # True
```"""
        
        else:
            return "Sample response based on prompt template."
    
    def _calculate_quality_score(self, response: str, template: PromptTemplate) -> float:
        """Calculate quality score for response"""
        
        quality = 0.5  # Base score
        
        # Check language appropriateness
        if template.language == Language.HINDI:
            hindi_chars = len([c for c in response if ord(c) > 0x0900 and ord(c) < 0x097F])
            if hindi_chars > len(response) * 0.3:  # 30% Hindi characters
                quality += 0.2
        
        # Check response length appropriateness
        if 50 <= len(response) <= 1000:
            quality += 0.1
        
        # Check for cultural context
        indian_words = ['भारत', 'India', 'हिंदी', 'रुपया', '₹', 'Mumbai', 'Delhi']
        if any(word in response for word in indian_words):
            quality += 0.1
        
        # Check for code blocks if code generation
        if template.type == PromptType.CODE_GENERATION and "```" in response:
            quality += 0.1
        
        return min(1.0, quality)
    
    def _calculate_confidence(self, response: str, template: PromptTemplate) -> float:
        """Calculate confidence in response"""
        
        confidence = 0.7  # Base confidence
        
        # Higher confidence for longer, structured responses
        if len(response) > 100:
            confidence += 0.1
        
        # Check for hedging language (reduces confidence)
        hedging_words = ['maybe', 'perhaps', 'might', 'possibly', 'शायद', 'हो सकता है']
        hedging_count = sum(1 for word in hedging_words if word in response.lower())
        confidence -= hedging_count * 0.05
        
        return max(0.1, min(1.0, confidence))
    
    def _detect_language(self, response: str) -> str:
        """Detect primary language in response"""
        
        hindi_chars = len([c for c in response if ord(c) > 0x0900 and ord(c) < 0x097F])
        english_chars = len([c for c in response if c.isalpha() and ord(c) < 0x0900])
        
        total_chars = hindi_chars + english_chars
        if total_chars == 0:
            return "unknown"
        
        hindi_ratio = hindi_chars / total_chars
        
        if hindi_ratio > 0.6:
            return "hindi"
        elif hindi_ratio > 0.2:
            return "mixed"
        else:
            return "english"
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage and cost summary"""
        
        return {
            "total_executions": len(self.execution_history),
            "total_tokens": self.total_tokens,
            "total_cost_inr": f"₹{self.total_cost_inr:.4f}",
            "avg_cost_per_execution": f"₹{self.total_cost_inr / max(1, len(self.execution_history)):.4f}",
            "avg_execution_time_ms": f"{np.mean([r.execution_time_ms for r in self.execution_history]):.1f}" if self.execution_history else "0",
            "avg_quality_score": f"{np.mean([r.quality_score for r in self.execution_history]):.3f}" if self.execution_history else "0"
        }

# Example usage and testing
async def test_prompt_engineering_toolkit():
    """Test prompt engineering toolkit with Indian examples"""
    
    print("🎯 Prompt Engineering Toolkit Test - Indian Context")
    print("=" * 60)
    
    # Initialize components
    library = IndianPromptTemplateLibrary()
    executor = PromptExecutor()
    optimizer = PromptOptimizer()
    
    print(f"✅ Library initialized with {len(library.templates)} templates")
    
    # Test different templates
    test_cases = [
        {
            "template_name": "hindi_sentiment",
            "variables": {"text": "यह फिल्म बहुत boring थी यार"}
        },
        {
            "template_name": "customer_support_mixed", 
            "variables": {"query": "Mera order cancel करना है"}
        },
        {
            "template_name": "indian_recipe",
            "variables": {"dish_name": "Chole Bhature", "region": "Punjabi"}
        },
        {
            "template_name": "financial_advice",
            "variables": {"question": "Should I invest in ELSS or PPF?"}
        }
    ]
    
    total_cost = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['template_name']}")
        
        # Get template
        template = library.get_template(test_case['template_name'])
        if not template:
            print(f"   ❌ Template not found")
            continue
        
        print(f"   Type: {template.type.value}")
        print(f"   Language: {template.language.value}")
        print(f"   Variables: {list(test_case['variables'].keys())}")
        
        # Execute prompt
        result = await executor.execute_prompt(template, test_case['variables'])
        
        print(f"   📊 Results:")
        print(f"      Tokens: {result.token_count}")
        print(f"      Cost: ₹{result.cost_inr:.4f}")
        print(f"      Time: {result.execution_time_ms:.1f}ms")
        print(f"      Quality: {result.quality_score:.3f}")
        print(f"      Confidence: {result.confidence:.3f}")
        print(f"      Language: {result.language_detected}")
        print(f"      Response: {result.response[:100]}...")
        
        total_cost += result.cost_inr
    
    # Test prompt optimization
    print(f"\n🔧 Testing Prompt Optimization:")
    
    test_prompt = "Please explain very very clearly how to make biryani in India."
    optimized = optimizer.optimize_token_usage(test_prompt)
    hindi_optimized = optimizer.optimize_for_hindi(optimized)
    cot_optimized = optimizer.add_chain_of_thought(hindi_optimized, Language.MIXED)
    
    print(f"   Original: {test_prompt}")
    print(f"   Optimized: {optimized}")
    print(f"   Hindi Context: {hindi_optimized}")
    print(f"   With CoT: {cot_optimized[:100]}...")
    
    # Usage summary
    print(f"\n📈 Usage Summary:")
    summary = executor.get_usage_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    print(f"\n🎯 Indian Context Features:")
    print(f"   ✅ Hindi/English mixed language support")
    print(f"   ✅ Cultural context awareness")
    print(f"   ✅ Regional preferences")
    print(f"   ✅ Indian use case templates (recipes, finance, etc.)")
    print(f"   ✅ Code-mixed conversation handling")
    print(f"   ✅ Cost optimization with token counting")
    print(f"   ✅ Chain-of-thought reasoning")
    print(f"   ✅ Few-shot learning examples")

if __name__ == "__main__":
    import numpy as np
    asyncio.run(test_prompt_engineering_toolkit())