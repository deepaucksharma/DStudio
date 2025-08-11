#!/usr/bin/env python3
"""
Embedding Search Engine for Indian Product Catalog
Episode 5: Code Example 11

Production-ready vector search system for Indian e-commerce
Supporting multilingual product search with semantic understanding

Author: Code Developer Agent
Context: Flipkart/Amazon India scale product search
"""

import numpy as np
import faiss
import torch
from transformers import AutoTokenizer, AutoModel
import json
import time
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pickle
import asyncio
import aioredis
from concurrent.futures import ThreadPoolExecutor
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProductInfo:
    """Product information for Indian e-commerce"""
    product_id: str
    title: str
    description: str
    category: str
    price_inr: float
    brand: str
    language: str
    region: str
    attributes: Dict[str, Any]
    embedding: Optional[np.ndarray] = None

@dataclass
class SearchResult:
    """Search result with relevance scoring"""
    product: ProductInfo
    similarity_score: float
    rank: int
    matched_features: List[str]

class IndianProductEmbedder:
    """Generate embeddings for Indian product catalog"""
    
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
        self.model = AutoModel.from_pretrained("ai4bharat/indic-bert")
        self.model.eval()
        
    def encode_product(self, product: ProductInfo) -> np.ndarray:
        """Generate embedding for a product"""
        
        # Combine title and description with Indian context
        text = f"{product.title} {product.description} {product.brand} {product.category}"
        
        # Add Hindi keywords for better search
        hindi_keywords = {
            "phone": "फ़ोन",
            "laptop": "लैपटॉप",
            "dress": "कपड़े",
            "food": "खाना",
            "book": "किताब"
        }
        
        for eng, hindi in hindi_keywords.items():
            if eng in text.lower():
                text += f" {hindi}"
        
        # Tokenize and encode
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        
        return embedding

class VectorSearchEngine:
    """Production vector search engine with FAISS"""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.products = []  # Store actual product data
        self.product_id_to_idx = {}
        self.embedder = IndianProductEmbedder()
        
        # Performance metrics
        self.search_count = 0
        self.total_search_time = 0.0
        
    def add_products(self, products: List[ProductInfo]):
        """Add products to search index"""
        logger.info(f"Adding {len(products)} products to index...")
        
        embeddings = []
        for i, product in enumerate(products):
            if product.embedding is None:
                product.embedding = self.embedder.encode_product(product)
            
            embeddings.append(product.embedding)
            self.products.append(product)
            self.product_id_to_idx[product.product_id] = len(self.products) - 1
            
            if (i + 1) % 1000 == 0:
                logger.info(f"Processed {i + 1} products...")
        
        # Normalize embeddings for cosine similarity
        embeddings = np.array(embeddings)
        faiss.normalize_L2(embeddings)
        
        # Add to FAISS index
        self.index.add(embeddings)
        
        logger.info(f"Index built with {self.index.ntotal} products")
    
    def search(self, query: str, top_k: int = 10, language: str = "hi", 
              filters: Optional[Dict] = None) -> List[SearchResult]:
        """Search for products using semantic similarity"""
        
        start_time = time.time()
        
        # Create dummy product for query encoding
        query_product = ProductInfo(
            product_id="query",
            title=query,
            description="",
            category="",
            price_inr=0,
            brand="",
            language=language,
            region="",
            attributes={}
        )
        
        # Get query embedding
        query_embedding = self.embedder.encode_product(query_product)
        query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Search in index
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Apply filters and create results
        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx >= len(self.products):
                continue
                
            product = self.products[idx]
            
            # Apply filters
            if filters and not self._matches_filters(product, filters):
                continue
            
            # Create search result
            result = SearchResult(
                product=product,
                similarity_score=float(score),
                rank=rank + 1,
                matched_features=self._get_matched_features(query, product)
            )
            results.append(result)
        
        # Update metrics
        search_time = time.time() - start_time
        self.search_count += 1
        self.total_search_time += search_time
        
        logger.info(f"Search completed in {search_time:.3f}s, found {len(results)} results")
        
        return results
    
    def _matches_filters(self, product: ProductInfo, filters: Dict) -> bool:
        """Check if product matches filters"""
        
        if "category" in filters and product.category not in filters["category"]:
            return False
        
        if "price_range" in filters:
            min_price, max_price = filters["price_range"]
            if not (min_price <= product.price_inr <= max_price):
                return False
        
        if "brand" in filters and product.brand not in filters["brand"]:
            return False
        
        if "region" in filters and product.region != filters["region"]:
            return False
        
        return True
    
    def _get_matched_features(self, query: str, product: ProductInfo) -> List[str]:
        """Identify which features matched the query"""
        
        query_words = set(query.lower().split())
        matched = []
        
        if any(word in product.title.lower() for word in query_words):
            matched.append("title")
        
        if any(word in product.description.lower() for word in query_words):
            matched.append("description")
        
        if any(word in product.brand.lower() for word in query_words):
            matched.append("brand")
        
        if any(word in product.category.lower() for word in query_words):
            matched.append("category")
        
        return matched

class CachedSearchEngine:
    """Search engine with Redis caching for production use"""
    
    def __init__(self, search_engine: VectorSearchEngine):
        self.search_engine = search_engine
        self.redis = None  # Will be initialized in production
        self.cache_ttl = 3600  # 1 hour cache
        self.cache_hits = 0
        self.cache_misses = 0
    
    async def initialize_cache(self):
        """Initialize Redis connection"""
        try:
            self.redis = await aioredis.from_url("redis://localhost:6379")
            logger.info("Redis cache initialized")
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
    
    async def search_cached(self, query: str, top_k: int = 10, 
                           language: str = "hi", filters: Optional[Dict] = None) -> List[SearchResult]:
        """Search with caching"""
        
        # Create cache key
        cache_key = self._generate_cache_key(query, top_k, language, filters)
        
        # Try cache first
        if self.redis:
            try:
                cached_result = await self.redis.get(cache_key)
                if cached_result:
                    self.cache_hits += 1
                    return pickle.loads(cached_result)
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")
        
        # Cache miss, perform actual search
        self.cache_misses += 1
        results = self.search_engine.search(query, top_k, language, filters)
        
        # Cache the results
        if self.redis:
            try:
                await self.redis.setex(cache_key, self.cache_ttl, pickle.dumps(results))
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")
        
        return results
    
    def _generate_cache_key(self, query: str, top_k: int, language: str, filters: Optional[Dict]) -> str:
        """Generate cache key for query"""
        key_data = {
            "query": query,
            "top_k": top_k,
            "language": language,
            "filters": filters or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"search:{hashlib.md5(key_string.encode()).hexdigest()}"
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate_percent": hit_rate,
            "total_requests": total_requests
        }

class IndianProductCatalog:
    """Complete product search system for Indian e-commerce"""
    
    def __init__(self):
        self.search_engine = VectorSearchEngine()
        self.cached_engine = CachedSearchEngine(self.search_engine)
        self.categories = [
            "Electronics", "Fashion", "Home & Kitchen", "Books",
            "Sports", "Beauty", "Automotive", "Grocery"
        ]
        self.regions = ["north", "south", "east", "west", "central"]
        
    async def initialize(self):
        """Initialize the catalog system"""
        await self.cached_engine.initialize_cache()
        
        # Load sample products
        products = self._generate_sample_products(5000)
        self.search_engine.add_products(products)
        
        logger.info("Indian Product Catalog initialized successfully")
    
    def _generate_sample_products(self, count: int) -> List[ProductInfo]:
        """Generate sample Indian e-commerce products"""
        
        products = []
        
        # Indian product examples
        sample_products = [
            {
                "title": "Samsung Galaxy S23 5G स्मार्टफोन",
                "description": "Latest Android smartphone with excellent camera और fast processor",
                "category": "Electronics",
                "brand": "Samsung",
                "price_range": (20000, 80000)
            },
            {
                "title": "Banarasi Silk Saree पारंपरिक साड़ी",
                "description": "Authentic handwoven Banarasi silk saree from Varanasi",
                "category": "Fashion",
                "brand": "Traditional",
                "price_range": (5000, 25000)
            },
            {
                "title": "Pressure Cooker प्रेशर कुकर",
                "description": "Stainless steel pressure cooker for Indian cooking",
                "category": "Home & Kitchen",
                "brand": "Hawkins",
                "price_range": (1500, 5000)
            },
            {
                "title": "The Mahabharata महाभारत Book",
                "description": "Complete Mahabharata in Hindi and English",
                "category": "Books",
                "brand": "Gita Press",
                "price_range": (200, 1000)
            },
            {
                "title": "Cricket Bat क्रिकेट बैट",
                "description": "Professional cricket bat made from English willow",
                "category": "Sports",
                "brand": "MRF",
                "price_range": (2000, 15000)
            }
        ]
        
        import random
        
        for i in range(count):
            template = random.choice(sample_products)
            
            product = ProductInfo(
                product_id=f"prod_{i+1:06d}",
                title=template["title"] + f" - Model {i%10+1}",
                description=template["description"] + f" Available in multiple colors.",
                category=template["category"],
                price_inr=random.uniform(*template["price_range"]),
                brand=template["brand"],
                language=random.choice(["hi", "en", "mixed"]),
                region=random.choice(self.regions),
                attributes={
                    "rating": random.uniform(3.0, 5.0),
                    "reviews": random.randint(10, 10000),
                    "availability": random.choice(["in_stock", "limited", "out_of_stock"]),
                    "delivery_days": random.randint(1, 7)
                }
            )
            
            products.append(product)
        
        return products
    
    async def smart_search(self, query: str, filters: Optional[Dict] = None,
                          top_k: int = 10, language: str = "hi") -> Dict[str, Any]:
        """Intelligent product search with analytics"""
        
        start_time = time.time()
        
        # Perform search
        results = await self.cached_engine.search_cached(query, top_k, language, filters)
        
        # Add search analytics
        search_time = time.time() - start_time
        
        # Format results for API response
        formatted_results = []
        for result in results:
            formatted_result = {
                "product_id": result.product.product_id,
                "title": result.product.title,
                "description": result.product.description[:200] + "..." if len(result.product.description) > 200 else result.product.description,
                "category": result.product.category,
                "price_inr": result.product.price_inr,
                "brand": result.product.brand,
                "similarity_score": round(result.similarity_score, 3),
                "rank": result.rank,
                "matched_features": result.matched_features,
                "attributes": result.product.attributes
            }
            formatted_results.append(formatted_result)
        
        # Get system statistics
        cache_stats = self.cached_engine.get_cache_stats()
        
        return {
            "query": query,
            "language": language,
            "filters_applied": filters or {},
            "results": formatted_results,
            "total_results": len(formatted_results),
            "search_time_ms": round(search_time * 1000, 2),
            "cache_stats": cache_stats,
            "system_stats": {
                "total_products": self.search_engine.index.ntotal,
                "total_searches": self.search_engine.search_count,
                "avg_search_time_ms": round(self.search_engine.total_search_time / max(1, self.search_engine.search_count) * 1000, 2)
            }
        }
    
    def get_recommendations(self, product_id: str, top_k: int = 5) -> List[SearchResult]:
        """Get product recommendations based on similarity"""
        
        if product_id not in self.search_engine.product_id_to_idx:
            return []
        
        # Get product
        product = self.search_engine.products[self.search_engine.product_id_to_idx[product_id]]
        
        # Use product title as query for recommendations
        return self.search_engine.search(
            query=f"{product.title} {product.category}",
            top_k=top_k + 1,  # +1 to exclude the product itself
            filters={"category": [product.category]}
        )[1:]  # Skip the first result (the product itself)

# Test and demonstration
async def test_embedding_search_engine():
    """Test the embedding search engine with Indian products"""
    
    print("🔍 Embedding Search Engine Test - Indian Product Catalog")
    print("=" * 70)
    
    # Initialize system
    catalog = IndianProductCatalog()
    await catalog.initialize()
    
    print(f"✅ Catalog initialized")
    print(f"   Products indexed: {catalog.search_engine.index.ntotal}")
    print(f"   Categories: {len(catalog.categories)}")
    print(f"   Regions: {len(catalog.regions)}")
    
    # Test searches in different languages
    test_queries = [
        {
            "query": "Samsung phone स्मार्टफोन",
            "language": "mixed",
            "filters": {"category": ["Electronics"], "price_range": (15000, 50000)},
            "description": "Mixed Hindi-English smartphone search"
        },
        {
            "query": "silk saree शादी के लिए",
            "language": "hi",
            "filters": {"category": ["Fashion"]},
            "description": "Hindi traditional wear search"
        },
        {
            "query": "pressure cooker kitchen",
            "language": "en",
            "filters": {"category": ["Home & Kitchen"], "price_range": (1000, 8000)},
            "description": "English kitchen appliance search"
        },
        {
            "query": "cricket bat खेल",
            "language": "mixed",
            "filters": {"category": ["Sports"]},
            "description": "Sports equipment search"
        }
    ]
    
    total_search_time = 0
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n🧪 Test {i}: {test['description']}")
        print(f"   Query: '{test['query']}'")
        print(f"   Language: {test['language']}")
        print(f"   Filters: {test['filters']}")
        
        # Perform search
        results = await catalog.smart_search(
            query=test["query"],
            filters=test["filters"],
            top_k=5,
            language=test["language"]
        )
        
        total_search_time += results["search_time_ms"]
        
        print(f"   📊 Results:")
        print(f"      Found: {results['total_results']} products")
        print(f"      Search time: {results['search_time_ms']}ms")
        print(f"      Cache hit rate: {results['cache_stats']['hit_rate_percent']:.1f}%")
        
        print(f"   🏆 Top Results:")
        for j, result in enumerate(results["results"][:3], 1):
            print(f"      {j}. {result['title']}")
            print(f"         Price: ₹{result['price_inr']:,.0f}")
            print(f"         Score: {result['similarity_score']:.3f}")
            print(f"         Matched: {', '.join(result['matched_features'])}")
    
    # Test recommendations
    print(f"\n🎯 Testing Recommendations:")
    sample_product_id = catalog.search_engine.products[0].product_id
    recommendations = catalog.get_recommendations(sample_product_id, top_k=3)
    
    print(f"   Product: {catalog.search_engine.products[0].title}")
    print(f"   Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"      {i}. {rec.product.title} (Score: {rec.similarity_score:.3f})")
    
    # Performance summary
    print(f"\n📈 Performance Summary:")
    system_stats = results["system_stats"]
    cache_stats = results["cache_stats"]
    
    print(f"   Total products: {system_stats['total_products']:,}")
    print(f"   Total searches: {system_stats['total_searches']}")
    print(f"   Average search time: {system_stats['avg_search_time_ms']:.2f}ms")
    print(f"   Cache efficiency: {cache_stats['hit_rate_percent']:.1f}% hit rate")
    print(f"   Cost per search: ₹{0.01:.3f} (estimated)")
    
    print(f"\n🎯 Indian E-commerce Features:")
    print(f"   ✅ Multilingual search (Hindi/English/Mixed)")
    print(f"   ✅ Semantic similarity with FAISS indexing")
    print(f"   ✅ Regional filtering and preferences")
    print(f"   ✅ Price range filtering in INR")
    print(f"   ✅ Redis caching for performance")
    print(f"   ✅ Product recommendations")
    print(f"   ✅ Indian brand and category support")

if __name__ == "__main__":
    asyncio.run(test_embedding_search_engine())