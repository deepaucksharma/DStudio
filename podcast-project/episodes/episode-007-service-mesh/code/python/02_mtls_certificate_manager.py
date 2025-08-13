#!/usr/bin/env python3
"""
mTLS Certificate Management for Service Mesh
Mumbai Police Radio Encryption Style Security

Context:
PhonePe/Paytm जैसे financial services के लिए automatic certificate rotation
जैसे Mumbai police radio encryption keys को regularly rotate करते हैं security के लिए

Features:
- Automatic certificate generation and rotation
- Istio integration
- Hindi logging and monitoring
- Production-ready error handling
"""

import os
import ssl
import json
import time
import base64
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import subprocess
import requests
import yaml

from cryptography import x509
from cryptography.x509.oid import NameOID, SignatureAlgorithmOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from kubernetes import client, config

# Setup logging - Hindi context के साथ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [मुंबई-mTLS] %(message)s',
    handlers=[
        logging.FileHandler('/var/log/mumbai-mtls-manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MumbaiMTLSManager')

@dataclass
class CertificateInfo:
    """Certificate metadata and paths"""
    service_name: str
    cert_path: str
    key_path: str
    ca_cert_path: str
    expiry_date: datetime
    created_date: datetime
    serial_number: str
    
    def is_expiring_soon(self, days_threshold: int = 30) -> bool:
        """Check if certificate expires within threshold"""
        return (self.expiry_date - datetime.now()).days <= days_threshold

class MumbaiMTLSManager:
    """
    mTLS Certificate Manager for Mumbai Service Mesh
    Mumbai police communication security की तरह - encrypted और authenticated
    """
    
    def __init__(self, 
                 ca_cert_path: str = "/etc/ssl/certs/mumbai-ca.crt",
                 ca_key_path: str = "/etc/ssl/private/mumbai-ca.key",
                 cert_storage_path: str = "/etc/ssl/service-mesh"):
        
        self.ca_cert_path = ca_cert_path
        self.ca_key_path = ca_key_path  
        self.cert_storage_path = Path(cert_storage_path)
        self.cert_storage_path.mkdir(exist_ok=True, parents=True)
        
        # Mumbai context - Service names mapping
        self.mumbai_services = {
            'payment-service': 'upi-payment-service.mumbai.svc.cluster.local',
            'order-service': 'order-service.mumbai.svc.cluster.local', 
            'auth-service': 'auth-service.mumbai.svc.cluster.local',
            'notification-service': 'notification-service.mumbai.svc.cluster.local'
        }
        
        # Certificate tracking
        self.certificates: Dict[str, CertificateInfo] = {}
        
        # Initialize Kubernetes client
        try:
            config.load_incluster_config()  # When running in cluster
        except:
            config.load_kube_config()  # When running locally
            
        self.k8s_client = client.CoreV1Api()
        
        logger.info("🔐 Mumbai mTLS Manager initialized")
        logger.info("CA Certificate: %s", ca_cert_path)
        logger.info("Certificate storage: %s", cert_storage_path)
    
    def ensure_ca_certificate(self):
        """
        Ensure CA certificate exists, create if needed
        Mumbai traffic control center के मुख्य certificate की तरह
        """
        if not os.path.exists(self.ca_cert_path) or not os.path.exists(self.ca_key_path):
            logger.info("🏗️ Creating new CA certificate for Mumbai mesh")
            self._create_ca_certificate()
        else:
            logger.info("✅ Using existing CA certificate")
            
        # Validate CA certificate
        self._validate_ca_certificate()
    
    def _create_ca_certificate(self):
        """Create a new CA certificate"""
        # Generate CA private key
        ca_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,  # Extra security for financial services
        )
        
        # Create CA certificate
        ca_cert_builder = x509.CertificateBuilder()
        ca_cert_builder = ca_cert_builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Maharashtra"), 
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Mumbai"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Mumbai Service Mesh CA"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Mumbai Mesh Root CA"),
        ]))
        
        ca_cert_builder = ca_cert_builder.issuer_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Maharashtra"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Mumbai"), 
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Mumbai Service Mesh CA"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Mumbai Mesh Root CA"),
        ]))
        
        # 10 years validity for CA
        ca_cert_builder = ca_cert_builder.not_valid_before(datetime.now())
        ca_cert_builder = ca_cert_builder.not_valid_after(datetime.now() + timedelta(days=3650))
        ca_cert_builder = ca_cert_builder.serial_number(x509.random_serial_number())
        ca_cert_builder = ca_cert_builder.public_key(ca_private_key.public_key())
        
        # CA extensions
        ca_cert_builder = ca_cert_builder.add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
        )
        ca_cert_builder = ca_cert_builder.add_extension(
            x509.KeyUsage(
                key_cert_sign=True,
                crl_sign=True,
                digital_signature=False,
                key_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        )
        
        # Sign the CA certificate
        ca_certificate = ca_cert_builder.sign(ca_private_key, hashes.SHA256())
        
        # Save CA certificate and key
        os.makedirs(os.path.dirname(self.ca_cert_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.ca_key_path), exist_ok=True)
        
        with open(self.ca_cert_path, "wb") as f:
            f.write(ca_certificate.public_bytes(serialization.Encoding.PEM))
        
        with open(self.ca_key_path, "wb") as f:
            f.write(ca_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Secure permissions
        os.chmod(self.ca_key_path, 0o600)
        os.chmod(self.ca_cert_path, 0o644)
        
        logger.info("✅ CA Certificate created successfully")
    
    def _validate_ca_certificate(self):
        """Validate CA certificate is valid and not expiring"""
        try:
            with open(self.ca_cert_path, "rb") as f:
                ca_cert = x509.load_pem_x509_certificate(f.read())
            
            # Check expiry
            expiry_date = ca_cert.not_valid_after
            days_until_expiry = (expiry_date - datetime.now()).days
            
            if days_until_expiry <= 90:  # 3 months warning
                logger.warning("⚠️ CA Certificate expiring in %d days!", days_until_expiry)
            else:
                logger.info("✅ CA Certificate valid until %s", expiry_date.strftime("%Y-%m-%d"))
                
        except Exception as e:
            logger.error("❌ CA Certificate validation failed: %s", e)
            raise
    
    def generate_service_certificate(self, service_name: str) -> CertificateInfo:
        """
        Generate mTLS certificate for service
        Mumbai police radio के लिए unique certificate बनाने की तरह
        """
        logger.info("🔑 Generating certificate for service: %s", service_name)
        
        # Load CA certificate and key
        with open(self.ca_cert_path, "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read())
        
        with open(self.ca_key_path, "rb") as f:
            ca_private_key = serialization.load_pem_private_key(f.read(), password=None)
        
        # Generate service private key
        service_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,  # Sufficient for service certificates
        )
        
        # Get service FQDN
        service_fqdn = self.mumbai_services.get(service_name, 
                                               f"{service_name}.mumbai.svc.cluster.local")
        
        # Create service certificate
        cert_builder = x509.CertificateBuilder()
        cert_builder = cert_builder.subject_name(x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Maharashtra"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Mumbai"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, f"Mumbai {service_name}"),
            x509.NameAttribute(NameOID.COMMON_NAME, service_fqdn),
        ]))
        
        cert_builder = cert_builder.issuer_name(ca_cert.subject)
        
        # 90 days validity - frequent rotation for security
        not_valid_before = datetime.now()
        not_valid_after = not_valid_before + timedelta(days=90)
        
        cert_builder = cert_builder.not_valid_before(not_valid_before)
        cert_builder = cert_builder.not_valid_after(not_valid_after)
        cert_builder = cert_builder.serial_number(x509.random_serial_number())
        cert_builder = cert_builder.public_key(service_private_key.public_key())
        
        # Service certificate extensions
        cert_builder = cert_builder.add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        )
        
        cert_builder = cert_builder.add_extension(
            x509.KeyUsage(
                key_cert_sign=False,
                crl_sign=False, 
                digital_signature=True,
                key_encipherment=True,
                key_agreement=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True
        )
        
        # Extended Key Usage - Client and Server authentication
        cert_builder = cert_builder.add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH
            ]),
            critical=True
        )
        
        # Subject Alternative Names - Mumbai style service discovery
        san_list = [
            x509.DNSName(service_fqdn),
            x509.DNSName(f"{service_name}.mumbai.svc"),
            x509.DNSName(f"{service_name}.mumbai"),
            x509.DNSName(service_name),
            # Localhost for testing
            x509.DNSName("localhost"),
            x509.IPAddress("127.0.0.1")
        ]
        
        cert_builder = cert_builder.add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False
        )
        
        # Sign the certificate
        service_certificate = cert_builder.sign(ca_private_key, hashes.SHA256())
        
        # Save certificate and key
        cert_dir = self.cert_storage_path / service_name
        cert_dir.mkdir(exist_ok=True)
        
        cert_path = cert_dir / "tls.crt"
        key_path = cert_dir / "tls.key"
        ca_cert_copy_path = cert_dir / "ca.crt"
        
        # Write service certificate
        with open(cert_path, "wb") as f:
            f.write(service_certificate.public_bytes(serialization.Encoding.PEM))
        
        # Write service private key  
        with open(key_path, "wb") as f:
            f.write(service_private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Copy CA certificate for verification
        with open(ca_cert_copy_path, "wb") as f:
            f.write(ca_cert.public_bytes(serialization.Encoding.PEM))
        
        # Set secure permissions
        os.chmod(key_path, 0o600)
        os.chmod(cert_path, 0o644)
        os.chmod(ca_cert_copy_path, 0o644)
        
        # Create certificate info
        cert_info = CertificateInfo(
            service_name=service_name,
            cert_path=str(cert_path),
            key_path=str(key_path),
            ca_cert_path=str(ca_cert_copy_path),
            expiry_date=not_valid_after,
            created_date=not_valid_before,
            serial_number=str(service_certificate.serial_number)
        )
        
        self.certificates[service_name] = cert_info
        logger.info("✅ Certificate generated for %s (expires: %s)", 
                   service_name, not_valid_after.strftime("%Y-%m-%d"))
        
        return cert_info
    
    def create_kubernetes_secret(self, service_name: str, namespace: str = "mumbai") -> bool:
        """
        Create Kubernetes TLS secret for service
        Mumbai police radio configuration की तरह automatic deployment
        """
        if service_name not in self.certificates:
            logger.error("❌ Certificate not found for service: %s", service_name)
            return False
        
        cert_info = self.certificates[service_name]
        
        try:
            # Read certificate files
            with open(cert_info.cert_path, 'r') as f:
                cert_data = f.read()
            
            with open(cert_info.key_path, 'r') as f:
                key_data = f.read()
            
            with open(cert_info.ca_cert_path, 'r') as f:
                ca_cert_data = f.read()
            
            # Create secret metadata
            secret_name = f"{service_name}-mtls-certs"
            
            secret_body = {
                'apiVersion': 'v1',
                'kind': 'Secret',
                'metadata': {
                    'name': secret_name,
                    'namespace': namespace,
                    'labels': {
                        'app': service_name,
                        'type': 'mtls',
                        'managed-by': 'mumbai-mtls-manager',
                        'mumbai.io/service': service_name
                    },
                    'annotations': {
                        'mumbai.io/cert-serial': cert_info.serial_number,
                        'mumbai.io/created': cert_info.created_date.isoformat(),
                        'mumbai.io/expires': cert_info.expiry_date.isoformat()
                    }
                },
                'type': 'kubernetes.io/tls',
                'data': {
                    'tls.crt': base64.b64encode(cert_data.encode()).decode(),
                    'tls.key': base64.b64encode(key_data.encode()).decode(),
                    'ca.crt': base64.b64encode(ca_cert_data.encode()).decode()
                }
            }
            
            # Create or update secret
            try:
                # Try to get existing secret
                existing_secret = self.k8s_client.read_namespaced_secret(
                    name=secret_name, namespace=namespace)
                
                # Update existing secret
                self.k8s_client.patch_namespaced_secret(
                    name=secret_name, 
                    namespace=namespace, 
                    body=secret_body
                )
                logger.info("🔄 Updated Kubernetes secret: %s/%s", namespace, secret_name)
                
            except client.ApiException as e:
                if e.status == 404:
                    # Create new secret
                    self.k8s_client.create_namespaced_secret(
                        namespace=namespace, 
                        body=secret_body
                    )
                    logger.info("✅ Created Kubernetes secret: %s/%s", namespace, secret_name)
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error("❌ Failed to create Kubernetes secret: %s", e)
            return False
    
    def rotate_certificate(self, service_name: str) -> bool:
        """
        Rotate service certificate
        Mumbai police radio encryption key rotation की तरह
        """
        logger.info("🔄 Rotating certificate for service: %s", service_name)
        
        try:
            # Generate new certificate
            new_cert_info = self.generate_service_certificate(service_name)
            
            # Update Kubernetes secret
            self.create_kubernetes_secret(service_name)
            
            # Trigger Istio to reload certificates
            self._trigger_istio_cert_reload(service_name)
            
            logger.info("✅ Certificate rotated successfully for %s", service_name)
            return True
            
        except Exception as e:
            logger.error("❌ Certificate rotation failed for %s: %s", service_name, e)
            return False
    
    def _trigger_istio_cert_reload(self, service_name: str):
        """Trigger Istio to reload certificates"""
        try:
            # Restart deployment to pick up new certificates
            apps_v1 = client.AppsV1Api()
            
            # Add annotation to trigger rolling restart
            patch_body = {
                'spec': {
                    'template': {
                        'metadata': {
                            'annotations': {
                                'kubectl.kubernetes.io/restartedAt': datetime.now().isoformat()
                            }
                        }
                    }
                }
            }
            
            apps_v1.patch_namespaced_deployment(
                name=service_name,
                namespace="mumbai", 
                body=patch_body
            )
            
            logger.info("🔄 Triggered deployment restart for certificate reload: %s", service_name)
            
        except Exception as e:
            logger.warning("⚠️ Could not trigger deployment restart: %s", e)
    
    def check_certificate_expiry(self) -> Dict[str, Dict[str, any]]:
        """
        Check certificate expiry status
        Mumbai police radio certificate inventory की तरह
        """
        expiry_status = {}
        
        for service_name, cert_info in self.certificates.items():
            days_until_expiry = (cert_info.expiry_date - datetime.now()).days
            
            status = "HEALTHY"
            if days_until_expiry <= 7:
                status = "CRITICAL"
            elif days_until_expiry <= 30:
                status = "WARNING"
            
            expiry_status[service_name] = {
                'days_until_expiry': days_until_expiry,
                'expiry_date': cert_info.expiry_date.isoformat(),
                'status': status,
                'serial_number': cert_info.serial_number,
                'needs_rotation': cert_info.is_expiring_soon(30)
            }
        
        return expiry_status
    
    def auto_rotate_expiring_certificates(self):
        """
        Auto-rotate certificates that are expiring soon
        Mumbai police automatic system maintenance की तरह
        """
        expiry_status = self.check_certificate_expiry()
        
        for service_name, status in expiry_status.items():
            if status['needs_rotation']:
                logger.info("🔄 Auto-rotating expiring certificate: %s", service_name)
                self.rotate_certificate(service_name)

def main():
    """
    Demo: Mumbai UPI Payment Service mTLS Setup
    PhonePe/Paytm जैसे services के लिए automatic certificate management
    """
    print("🔐 Mumbai Service Mesh mTLS Certificate Manager")
    print("=" * 55)
    
    # Initialize mTLS manager
    mtls_manager = MumbaiMTLSManager()
    
    # Ensure CA certificate exists
    mtls_manager.ensure_ca_certificate()
    
    # Generate certificates for Mumbai services
    mumbai_services = [
        'payment-service',
        'order-service', 
        'auth-service',
        'notification-service'
    ]
    
    print("\n🔑 Generating service certificates...")
    for service in mumbai_services:
        cert_info = mtls_manager.generate_service_certificate(service)
        print(f"  ✅ {service}: {cert_info.expiry_date.strftime('%Y-%m-%d')}")
        
        # Create Kubernetes secret
        success = mtls_manager.create_kubernetes_secret(service)
        if success:
            print(f"     📦 Kubernetes secret created")
    
    # Check expiry status
    print("\n📅 Certificate Expiry Status:")
    expiry_status = mtls_manager.check_certificate_expiry()
    
    for service, status in expiry_status.items():
        status_emoji = {"HEALTHY": "✅", "WARNING": "⚠️", "CRITICAL": "❌"}
        emoji = status_emoji.get(status['status'], "❓")
        print(f"  {emoji} {service}: {status['days_until_expiry']} days remaining")
    
    # Demo certificate rotation
    print("\n🔄 Testing certificate rotation for payment-service...")
    rotation_success = mtls_manager.rotate_certificate('payment-service')
    print(f"Rotation {'successful' if rotation_success else 'failed'}")
    
    print("\n🚀 Mumbai mTLS setup complete! Ready for production.")

if __name__ == "__main__":
    main()