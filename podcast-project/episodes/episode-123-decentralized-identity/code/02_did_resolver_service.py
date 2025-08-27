#!/usr/bin/env python3
"""
Episode 123: DID Resolver Service
Mumbai Local Train Information System Style

Bhai, jaise station pe announce hota hai "Next station Andheri",
waise hi ye service batayegi ki koi DID ka matlab kya hai.
DID resolver = Train information system for digital identity

Author: Hindi Podcast Team
Cost: ₹500-2000/month for production deployment
"""

import json
import asyncio
import hashlib
import aiohttp
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import redis
import logging
from contextlib import asynccontextmanager

# Mumbai style logging
logging.basicConfig(level=logging.INFO, format='🚂 %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Models for API
class DIDResolutionRequest(BaseModel):
    did: str = Field(..., description="DID to resolve")
    accept: Optional[str] = Field("application/did+json", description="Accept header")

class DIDResolutionResult(BaseModel):
    didDocument: Dict
    didDocumentMetadata: Dict
    didResolutionMetadata: Dict

class MumbaiDIDResolver:
    """
    Mumbai Local Train Style DID Resolver
    Sabko batata hai ki kis DID ka kya matlab hai
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.supported_methods = ["mumbai", "web", "key", "ethr"]
        self.cache_ttl = 3600  # 1 hour cache
        
        # Mumbai train lines to method mapping
        self.method_endpoints = {
            "mumbai": "https://mumbai-identity.gov.in/api/v1/",
            "web": "https://web-did-resolver.herokuapp.com/",
            "key": "local",  # Local resolution
            "ethr": "https://ethr-did-resolver.herokuapp.com/"
        }
    
    async def resolve_did(self, did: str) -> Dict:
        """
        DID resolve karo - jaise train ka current status check karna
        """
        logger.info(f"🔍 Resolving DID: {did}")
        
        # DID format validate karo
        if not self._validate_did_format(did):
            raise ValueError(f"Invalid DID format: {did}")
        
        # Extract method from DID
        method = self._extract_method(did)
        
        if method not in self.supported_methods:
            raise ValueError(f"Unsupported DID method: {method}")
        
        # Check cache first (jaise last announcement)
        cached_result = await self._get_from_cache(did)
        if cached_result:
            logger.info(f"📦 Cache hit for DID: {did}")
            return cached_result
        
        # Method-specific resolution
        if method == "mumbai":
            result = await self._resolve_mumbai_did(did)
        elif method == "web":
            result = await self._resolve_web_did(did)
        elif method == "key":
            result = await self._resolve_key_did(did)
        elif method == "ethr":
            result = await self._resolve_ethereum_did(did)
        else:
            raise ValueError(f"Method {method} not implemented")
        
        # Cache the result
        await self._cache_result(did, result)
        
        logger.info(f"✅ Successfully resolved DID: {did}")
        return result
    
    def _validate_did_format(self, did: str) -> bool:
        """
        DID format check karo - proper syntax hai ya nahi
        Format: did:method:specific-id
        """
        parts = did.split(":")
        return len(parts) >= 3 and parts[0] == "did"
    
    def _extract_method(self, did: str) -> str:
        """DID method extract karo"""
        parts = did.split(":")
        return parts[1] if len(parts) >= 3 else ""
    
    async def _resolve_mumbai_did(self, did: str) -> Dict:
        """
        Mumbai method DID resolve karo
        Ye humara custom method hai - local government style
        """
        logger.info(f"🚇 Resolving Mumbai DID: {did}")
        
        # Extract specific ID
        specific_id = ":".join(did.split(":")[2:])
        
        # Mumbai DIDs are stored locally or in government database
        # For demo, we'll create a standard response
        did_document = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed25519-2020/v1"
            ],
            "id": did,
            "verificationMethod": [{
                "id": f"{did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyJwk": {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": specific_id  # Simplified for demo
                }
            }],
            "authentication": [f"{did}#key-1"],
            "service": [{
                "id": f"{did}#mumbai-service",
                "type": "MumbaiIdentityService",
                "serviceEndpoint": f"https://mumbai-identity.gov.in/services/{specific_id}"
            }],
            "created": "2024-01-01T00:00:00Z",
            "updated": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "didDocument": did_document,
            "didDocumentMetadata": {
                "method": {
                    "published": True,
                    "recoveryCommitment": None,
                    "updateCommitment": None
                },
                "created": "2024-01-01T00:00:00Z",
                "updated": datetime.now(timezone.utc).isoformat()
            },
            "didResolutionMetadata": {
                "contentType": "application/did+json",
                "retrieved": datetime.now(timezone.utc).isoformat(),
                "duration": 150  # milliseconds
            }
        }
    
    async def _resolve_web_did(self, did: str) -> Dict:
        """
        Web method DID resolve karo via HTTP
        """
        logger.info(f"🌐 Resolving Web DID: {did}")
        
        # Extract URL from DID
        # Format: did:web:example.com:user:alice
        parts = did.split(":")
        domain = parts[2]
        path_parts = parts[3:] if len(parts) > 3 else []
        
        # Construct URL
        if path_parts:
            url = f"https://{domain}/.well-known/did/{'/'.join(path_parts)}/did.json"
        else:
            url = f"https://{domain}/.well-known/did.json"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        did_document = await response.json()
                        return {
                            "didDocument": did_document,
                            "didDocumentMetadata": {
                                "method": {"published": True},
                                "retrieved": datetime.now(timezone.utc).isoformat()
                            },
                            "didResolutionMetadata": {
                                "contentType": "application/did+json",
                                "retrieved": datetime.now(timezone.utc).isoformat()
                            }
                        }
                    else:
                        raise HTTPException(status_code=404, detail=f"DID not found at {url}")
        except Exception as e:
            logger.error(f"Error resolving web DID: {e}")
            raise HTTPException(status_code=500, detail=f"Resolution failed: {str(e)}")
    
    async def _resolve_key_did(self, did: str) -> Dict:
        """
        Key method DID resolve karo - self-contained public key
        """
        logger.info(f"🔑 Resolving Key DID: {did}")
        
        # Key DIDs contain the public key in the identifier
        # Format: did:key:z6Mkfriq1MqLBoPWecGoDLjguo1sB9brj6wT3qZ5BxkKpuP6
        
        specific_id = did.split(":")[2]
        
        # For demo, create a standard response
        did_document = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed25519-2020/v1"
            ],
            "id": did,
            "verificationMethod": [{
                "id": f"{did}#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyMultibase": specific_id
            }],
            "authentication": [f"{did}#key-1"],
            "assertionMethod": [f"{did}#key-1"],
            "capabilityDelegation": [f"{did}#key-1"],
            "capabilityInvocation": [f"{did}#key-1"]
        }
        
        return {
            "didDocument": did_document,
            "didDocumentMetadata": {
                "method": {"published": True}
            },
            "didResolutionMetadata": {
                "contentType": "application/did+json",
                "retrieved": datetime.now(timezone.utc).isoformat()
            }
        }
    
    async def _resolve_ethereum_did(self, did: str) -> Dict:
        """
        Ethereum method DID resolve karo via blockchain
        """
        logger.info(f"⛓️ Resolving Ethereum DID: {did}")
        
        # Ethereum DIDs are resolved via smart contract
        # For demo, simulate blockchain call
        await asyncio.sleep(0.5)  # Simulate blockchain delay
        
        address = did.split(":")[2]
        
        did_document = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed25519-2020/v1"
            ],
            "id": did,
            "verificationMethod": [{
                "id": f"{did}#owner",
                "type": "EcdsaSecp256k1RecoveryMethod2020",
                "controller": did,
                "blockchainAccountId": f"eip155:1:{address}"
            }],
            "authentication": [f"{did}#owner"],
            "assertionMethod": [f"{did}#owner"]
        }
        
        return {
            "didDocument": did_document,
            "didDocumentMetadata": {
                "method": {
                    "published": True,
                    "network": "mainnet",
                    "blockNumber": 18500000  # Current block
                }
            },
            "didResolutionMetadata": {
                "contentType": "application/did+json",
                "retrieved": datetime.now(timezone.utc).isoformat(),
                "blockchainCost": "₹50"  # Gas cost in INR
            }
        }
    
    async def _get_from_cache(self, did: str) -> Optional[Dict]:
        """Redis cache se result nikalo"""
        if not self.redis_client:
            return None
        
        try:
            cached = self.redis_client.get(f"did_resolution:{did}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache error: {e}")
        return None
    
    async def _cache_result(self, did: str, result: Dict):
        """Result ko cache mein store karo"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.setex(
                f"did_resolution:{did}",
                self.cache_ttl,
                json.dumps(result)
            )
        except Exception as e:
            logger.warning(f"Cache store error: {e}")

# FastAPI Application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚂 Starting Mumbai DID Resolver Service")
    
    # Initialize Redis (optional)
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        redis_client.ping()
        app.state.redis = redis_client
        logger.info("📦 Connected to Redis cache")
    except:
        app.state.redis = None
        logger.warning("⚠️ Redis not available, running without cache")
    
    # Initialize DID resolver
    app.state.resolver = MumbaiDIDResolver(app.state.redis)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Mumbai DID Resolver Service")

app = FastAPI(
    title="Mumbai DID Resolver Service",
    description="Decentralized Identity Resolution - Mumbai Local Train Style",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mumbai-did-resolver", "timestamp": datetime.now()}

@app.get("/1.0/identifiers/{did:path}", response_model=DIDResolutionResult)
async def resolve_did(did: str, accept: str = "application/did+json"):
    """
    DID Resolution endpoint - Universal resolver compatible
    
    Mumbai style DID resolution:
    - did:mumbai:xyz -> Mumbai government database
    - did:web:example.com -> HTTPS resolution
    - did:key:z6Mk... -> Self-contained key
    - did:ethr:0x123... -> Ethereum blockchain
    """
    try:
        resolver = app.state.resolver
        result = await resolver.resolve_did(did)
        
        # Add response headers
        headers = {
            "Content-Type": accept,
            "Cache-Control": "max-age=3600"  # 1 hour cache
        }
        
        return JSONResponse(content=result, headers=headers)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Resolution error for {did}: {e}")
        raise HTTPException(status_code=500, detail="Internal resolution error")

@app.post("/resolve", response_model=DIDResolutionResult)
async def resolve_did_post(request: DIDResolutionRequest):
    """
    POST endpoint for DID resolution with options
    """
    try:
        resolver = app.state.resolver
        result = await resolver.resolve_did(request.did)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Resolution error for {request.did}: {e}")
        raise HTTPException(status_code=500, detail="Internal resolution error")

@app.get("/methods")
async def supported_methods():
    """List supported DID methods"""
    resolver = app.state.resolver
    return {
        "supportedMethods": resolver.supported_methods,
        "endpoints": resolver.method_endpoints,
        "cacheEnabled": resolver.redis_client is not None
    }

@app.get("/stats")
async def resolution_stats():
    """
    Resolution statistics - Mumbai train status style
    """
    # Mock stats for demo
    return {
        "totalResolutions": 45623,
        "successRate": 98.5,
        "averageResponseTime": "150ms",
        "cacheHitRate": 75.2,
        "methodDistribution": {
            "mumbai": 40,
            "web": 30,
            "key": 20,
            "ethr": 10
        },
        "dailyResolutions": {
            "today": 1247,
            "yesterday": 1189,
            "peakHour": "10:00-11:00 AM"
        },
        "costAnalysis": {
            "totalCostToday": "₹125",
            "averageCostPerResolution": "₹0.10",
            "cacheSwings": "₹45"
        }
    }

def demo_did_resolution():
    """
    Standalone demo function
    """
    print("🚂 === Mumbai DID Resolver Demo === 🚂")
    
    # Test DIDs
    test_dids = [
        "did:mumbai:abc123",
        "did:key:z6MkfriqRMqLBoPWecGoDLjguo1sB9brj6wT3qZ5BxkKpuP6",
        "did:web:example.com:user:alice",
        "did:ethr:0x1234567890123456789012345678901234567890"
    ]
    
    resolver = MumbaiDIDResolver()
    
    async def resolve_all():
        for did in test_dids:
            try:
                print(f"\
🔍 Resolving: {did}")
                result = await resolver.resolve_did(did)
                print(f"✅ Method: {did.split(':')[1]}")
                print(f"📄 Document ID: {result['didDocument']['id']}")
                print(f"🔑 Verification methods: {len(result['didDocument'].get('verificationMethod', []))}")
                print(f"⏱️ Retrieved: {result['didResolutionMetadata']['retrieved'][:19]}")
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Run demo
    asyncio.run(resolve_all())
    
    print("\
💰 === Cost Analysis ===")
    costs = {
        "mumbai": "₹0 (government service)",
        "web": "₹0.10 (HTTP request)",
        "key": "₹0 (local computation)",
        "ethr": "₹50 (blockchain query)"
    }
    
    for method, cost in costs.items():
        print(f"   {method}: {cost}")

if __name__ == "__main__":
    # Run demo
    demo_did_resolution()
    
    print("\
🚀 To start the web service:")
    print("   uvicorn 02_did_resolver_service:app --reload --port 8001")
    print("\
📚 API Documentation:")
    print("   http://localhost:8001/docs")
    print("\
🔍 Test resolution:")
    print("   curl http://localhost:8001/1.0/identifiers/did:mumbai:abc123")