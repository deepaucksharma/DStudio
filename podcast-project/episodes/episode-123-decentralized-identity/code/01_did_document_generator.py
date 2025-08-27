#!/usr/bin/env python3
"""
Episode 123: DID Document Generator
Mumbai Style Identity Document Creator

Bhai, ye script banayega tumhara unique DID document.
Jaise har Mumbai local train passenger ka unique ID hota hai,
waise hi har digital identity ka unique DID hota hai.

Author: Hindi Podcast Team
Cost: Free for generation, ₹5-50 for blockchain registration
"""

import json
import time
import hashlib
import base64
from datetime import datetime, timezone
from typing import Dict, List, Optional
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import logging

# Mumbai style logging
logging.basicConfig(level=logging.INFO, format='🚂 %(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class MumbaiDIDGenerator:
    """
    Mumbai Local Train Style DID Generator
    Har passenger ka unique pass, har user ka unique DID
    """
    
    def __init__(self, network: str = "mumbai"):
        self.network = network
        self.method = "mumbai"  # Our custom DID method
        
    def generate_keypair(self) -> tuple:
        """
        Key pair banao - jaise train pass ke liye signature
        Returns: (private_key, public_key)
        """
        logger.info("🔑 Generating Ed25519 key pair - Mumbai style crypto")
        
        # Ed25519 sabse secure aur fast hai
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        return private_key, public_key
    
    def create_did_identifier(self, public_key) -> str:
        """
        DID identifier banao - unique ID jaise PNR number
        Mumbai method: did:mumbai:z{base58-multibase-encoded-key}
        """
        # Public key ko bytes mein convert karo
        pub_key_bytes = public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw
        )
        
        # SHA256 hash banao
        hash_obj = hashlib.sha256()
        hash_obj.update(pub_key_bytes)
        key_hash = hash_obj.digest()
        
        # Base64 encoding karo (Mumbai local ticket style)
        encoded_key = base64.urlsafe_b64encode(key_hash[:16]).decode().rstrip('=')
        
        did = f"did:{self.method}:{encoded_key}"
        logger.info(f"🎫 Generated DID: {did}")
        
        return did
    
    def create_verification_method(self, did: str, public_key, key_id: str = "key-1") -> Dict:
        """
        Verification method banao - signature verify karne ke liye
        """
        pub_key_jwk = self._public_key_to_jwk(public_key)
        
        return {
            "id": f"{did}#{key_id}",
            "type": "Ed25519VerificationKey2020",
            "controller": did,
            "publicKeyJwk": pub_key_jwk
        }
    
    def _public_key_to_jwk(self, public_key) -> Dict:
        """
        Public key ko JWK format mein convert karo
        """
        pub_key_bytes = public_key.public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw
        )
        
        return {
            "kty": "OKP",
            "crv": "Ed25519",
            "x": base64.urlsafe_b64encode(pub_key_bytes).decode().rstrip('=')
        }
    
    def create_did_document(self, 
                          name: str,
                          role: str = "mumbaikar",
                          services: Optional[List[Dict]] = None) -> Dict:
        """
        Complete DID document banao - digital identity card
        
        Args:
            name: User ka naam (Mumbai style)
            role: Kya kaam karta hai (developer, trader, etc.)
            services: Kya services provide karta hai
        """
        logger.info(f"📄 Creating DID document for {name} ({role})")
        
        # Key pair generate karo
        private_key, public_key = self.generate_keypair()
        
        # DID identifier banao
        did = self.create_did_identifier(public_key)
        
        # Verification method banao
        verification_method = self.create_verification_method(did, public_key)
        
        # Default services add karo agar nahi diye
        if services is None:
            services = []
        
        # Mumbai specific service endpoints
        services.extend([
            {
                "id": f"{did}#mumbai-local-service",
                "type": "MumbaiLocalIdentityService",
                "serviceEndpoint": {
                    "uri": f"https://mumbai-identity.gov.in/services/{did.split(':')[-1]}",
                    "accept": ["didcomm/v2", "didcomm/aip2;env=rfc587"]
                }
            },
            {
                "id": f"{did}#messaging",
                "type": "MessagingService", 
                "serviceEndpoint": f"https://mumbai-didcomm.herokuapp.com/api/v1/{did.split(':')[-1]}"
            }
        ])
        
        # Complete DID document
        did_document = {
            "@context": [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed25519-2020/v1"
            ],
            "id": did,
            "verificationMethod": [verification_method],
            "authentication": [verification_method["id"]],
            "assertionMethod": [verification_method["id"]],
            "keyAgreement": [verification_method["id"]],
            "capabilityInvocation": [verification_method["id"]],
            "capabilityDelegation": [verification_method["id"]],
            "service": services,
            "created": datetime.now(timezone.utc).isoformat(),
            "updated": datetime.now(timezone.utc).isoformat(),
            # Mumbai specific metadata
            "mumbaiMetadata": {
                "name": name,
                "role": role,
                "network": self.network,
                "trainLine": self._get_random_train_line(),
                "station": self._get_random_station(),
                "issueDate": datetime.now(timezone.utc).isoformat(),
                "validityPeriod": "P1Y"  # 1 year validity
            }
        }
        
        logger.info("✅ DID document created successfully!")
        return {
            "didDocument": did_document,
            "privateKey": self._serialize_private_key(private_key),
            "publicKey": self._serialize_public_key(public_key)
        }
    
    def _serialize_private_key(self, private_key) -> str:
        """Private key ko string format mein serialize karo"""
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        return private_bytes.decode()
    
    def _serialize_public_key(self, public_key) -> str:
        """Public key ko string format mein serialize karo"""
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return public_bytes.decode()
    
    def _get_random_train_line(self) -> str:
        """Random Mumbai train line assign karo"""
        import random
        lines = ["Western", "Central", "Harbour", "Trans-Harbour", "Mono-Rail"]
        return random.choice(lines)
    
    def _get_random_station(self) -> str:
        """Random Mumbai station assign karo"""
        import random
        stations = ["Andheri", "Bandra", "Dadar", "CST", "Kurla", "Thane", 
                   "Borivali", "Virar", "Kalyan", "Dombivli", "Ghatkopar"]
        return random.choice(stations)

def demo_mumbai_did_generation():
    """
    Demo: Mumbai style DID generation
    """
    print("🚂 === Mumbai DID Generator Demo === 🚂")
    
    generator = MumbaiDIDGenerator()
    
    # Mumbai ke kuch typical users
    mumbai_users = [
        {"name": "Rajesh Sharma", "role": "software_developer"},
        {"name": "Priya Patel", "role": "trader"}, 
        {"name": "Vikram Singh", "role": "dabba_wala"},
        {"name": "Anita Desai", "role": "financial_analyst"}
    ]
    
    for user in mumbai_users:
        print(f"\n🎫 Creating DID for {user['name']} ({user['role']})")
        
        # Custom services for different roles
        services = []
        if user['role'] == 'dabba_wala':
            services.append({
                "id": "#dabba-delivery",
                "type": "FoodDeliveryService",
                "serviceEndpoint": "https://mumbai-dabba.com/api/delivery"
            })
        elif user['role'] == 'trader':
            services.append({
                "id": "#trading-verification", 
                "type": "TradingVerificationService",
                "serviceEndpoint": "https://bse.com/api/trader-verification"
            })
        
        result = generator.create_did_document(
            name=user['name'],
            role=user['role'],
            services=services
        )
        
        # Display results
        did_doc = result['didDocument']
        print(f"✅ DID: {did_doc['id']}")
        print(f"🚉 Station: {did_doc['mumbaiMetadata']['station']}")
        print(f"🚇 Line: {did_doc['mumbaiMetadata']['trainLine']}")
        print(f"📅 Created: {did_doc['created'][:19]}")
        
        # Save to file
        filename = f"did_document_{user['name'].replace(' ', '_').lower()}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"💾 Saved to: {filename}")

def calculate_mumbai_did_costs():
    """
    Mumbai DID system ke costs calculate karo
    """
    print("\n💰 === Mumbai DID Cost Analysis === 💰")
    
    costs = {
        "did_generation": 0,  # Free
        "blockchain_registration": 50,  # INR per DID
        "verification_per_month": 100,  # INR per 1000 verifications
        "storage_per_gb": 5,  # INR per GB per month
        "api_calls_per_1000": 0.50  # INR
    }
    
    print("📊 Cost Breakdown (INR):")
    for service, cost in costs.items():
        print(f"   {service.replace('_', ' ').title()}: ₹{cost}")
    
    # Monthly cost for 10,000 users
    users = 10000
    monthly_cost = (
        users * costs["blockchain_registration"] / 12 +  # Annual registration
        users * 10 * costs["verification_per_month"] / 1000 +  # 10 verifications per user
        users * 0.1 * costs["storage_per_gb"] +  # 100MB per user
        users * 50 * costs["api_calls_per_1000"] / 1000  # 50 API calls per user
    )
    
    print(f"\n🏙️ Mumbai DID Network (10,000 users):")
    print(f"   Monthly Cost: ₹{monthly_cost:,.2f}")
    print(f"   Cost per user per month: ₹{monthly_cost/users:.2f}")
    print(f"   Annual Cost: ₹{monthly_cost*12:,.2f}")

if __name__ == "__main__":
    # Mumbai DID generation demo
    demo_mumbai_did_generation()
    
    # Cost analysis
    calculate_mumbai_did_costs()
    
    print("\n🎉 Mumbai DID Generator completed successfully!")
    print("💡 Next: Use did_resolver.py to resolve these DIDs")
    print("📚 Learn more: https://w3c.github.io/did-core/")