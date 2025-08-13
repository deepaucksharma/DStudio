#!/usr/bin/env python3
"""
Automated API Documentation Generation for Versioning
Inspired by Postman's API documentation approach for Indian developer ecosystem

Example: Postman ne kaise automate kiya API documentation generation for versions
"""

import json
import yaml
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime
import re
import markdown
from jinja2 import Template
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentationType(Enum):
    """Types of documentation"""
    API_REFERENCE = "api_reference"
    MIGRATION_GUIDE = "migration_guide"
    QUICKSTART = "quickstart"
    CHANGELOG = "changelog"
    SDK_DOCS = "sdk_docs"

class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"

@dataclass
class APIParameter:
    """API parameter documentation"""
    name: str
    param_type: str  # query, path, header, body
    data_type: str
    required: bool = False
    description: str = ""
    example: Any = None
    constraints: Optional[Dict[str, Any]] = None

@dataclass
class APIResponse:
    """API response documentation"""
    status_code: int
    description: str
    schema: Dict[str, Any]
    example: Dict[str, Any]
    headers: Optional[Dict[str, str]] = None

@dataclass
class APIEndpoint:
    """API endpoint documentation"""
    path: str
    method: HTTPMethod
    summary: str
    description: str
    parameters: List[APIParameter] = field(default_factory=list)
    responses: List[APIResponse] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    deprecated: bool = False
    added_in_version: str = "1.0"
    deprecated_in_version: Optional[str] = None

@dataclass
class APIVersion:
    """API version documentation"""
    version: str
    release_date: str
    status: str  # active, deprecated, retired
    description: str
    endpoints: List[APIEndpoint] = field(default_factory=list)
    breaking_changes: List[str] = field(default_factory=list)
    migration_notes: List[str] = field(default_factory=list)

class APIDocumentationGenerator:
    """
    Generate comprehensive API documentation for multiple versions
    Postman style documentation with Indian developer context
    """
    
    def __init__(self, api_name: str, base_url: str):
        self.api_name = api_name
        self.base_url = base_url
        self.versions: Dict[str, APIVersion] = {}
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize documentation templates"""
        return {
            "api_reference": """
# {{api_name}} API Documentation

## Overview
{{api_name}} provides RESTful APIs for {{description}}.

**Base URL:** `{{base_url}}`
**Current Version:** {{current_version}}

## Authentication
All API requests require authentication using API key in header:
```
Authorization: Bearer YOUR_API_KEY
```

## Versions
{% for version in versions %}
### Version {{version.version}} {% if version.status == 'deprecated' %}(Deprecated){% endif %}
- **Release Date:** {{version.release_date}}
- **Status:** {{version.status}}
- **Description:** {{version.description}}
{% if version.breaking_changes %}
- **Breaking Changes:**
{% for change in version.breaking_changes %}
  - {{change}}
{% endfor %}
{% endif %}
{% endfor %}

## Endpoints

{% for endpoint in endpoints %}
### {{endpoint.method.value}} {{endpoint.path}}

{{endpoint.description}}

**Added in:** Version {{endpoint.added_in_version}}
{% if endpoint.deprecated %}
**⚠️  Deprecated:** Since version {{endpoint.deprecated_in_version}}
{% endif %}

#### Parameters
{% if endpoint.parameters %}
| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
{% for param in endpoint.parameters %}
| {{param.name}} | {{param.data_type}} | {{param.param_type}} | {{param.required}} | {{param.description}} |
{% endfor %}
{% else %}
No parameters required.
{% endif %}

#### Responses
{% for response in endpoint.responses %}
**{{response.status_code}}** - {{response.description}}
```json
{{response.example}}
```
{% endfor %}

#### Example Request
```bash
curl -X {{endpoint.method.value}} \\
  {{base_url}}{{endpoint.path}} \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"
```

---
{% endfor %}
            """,
            
            "migration_guide": """
# Migration Guide: {{from_version}} to {{to_version}}

## Overview
This guide helps you migrate from {{api_name}} API {{from_version}} to {{to_version}}.

## Timeline
- **{{from_version}} Deprecation Date:** {{deprecation_date}}
- **{{from_version}} Sunset Date:** {{sunset_date}}
- **Recommended Migration Window:** {{migration_window}}

## Breaking Changes
{% for change in breaking_changes %}
### {{change.title}}
{{change.description}}

**Impact:** {{change.impact}}
**Action Required:** {{change.action}}

**Before ({{from_version}}):**
```json
{{change.before_example}}
```

**After ({{to_version}}):**
```json
{{change.after_example}}
```
{% endfor %}

## Migration Checklist
{% for item in migration_checklist %}
- [ ] {{item}}
{% endfor %}

## Code Examples

### Python SDK Migration
```python
# Old code ({{from_version}})
import paytm_v1 as paytm
client = paytm.Client(api_key="your_key")
result = client.payments.create(amount=100, phone="9876543210")

# New code ({{to_version}})
import paytm_v2 as paytm
client = paytm.Client(api_key="your_key", version="v2")
result = client.payments.create(
    amount_in_paise=10000,  # Amount now in paise
    customer={"phone": "+919876543210"}  # Phone with country code
)
```

### Node.js SDK Migration
```javascript
// Old code ({{from_version}})
const PayTM = require('paytm-sdk-v1');
const client = new PayTM({apiKey: 'your_key'});
const result = await client.payments.create({
  amount: 100,
  phone: '9876543210'
});

// New code ({{to_version}})
const PayTM = require('paytm-sdk-v2');
const client = new PayTM({apiKey: 'your_key', version: 'v2'});
const result = await client.payments.create({
  amount_in_paise: 10000,
  customer: {phone: '+919876543210'}
});
```

## Support
- **Documentation:** https://docs.paytm.com/api/{{to_version}}
- **Developer Forum:** https://community.paytm.com
- **Support Email:** developers@paytm.com
- **Migration Assistance:** Schedule a call at https://calendly.com/paytm-dev-support
            """,
            
            "quickstart": """
# {{api_name}} API Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Get Your API Key
1. Sign up at [{{api_name}} Developer Portal](https://developers.{{domain}})
2. Create a new application
3. Copy your API key from the dashboard

### Step 2: Make Your First API Call

#### Using cURL
```bash
curl -X GET \\
  {{base_url}}/{{sample_endpoint}} \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json"
```

#### Using Python
```python
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
}

response = requests.get('{{base_url}}/{{sample_endpoint}}', headers=headers)
print(response.json())
```

#### Using Node.js
```javascript
const axios = require('axios');

const config = {
  method: 'get',
  url: '{{base_url}}/{{sample_endpoint}}',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  }
};

axios(config)
  .then(response => console.log(response.data))
  .catch(error => console.log(error));
```

### Step 3: Common Use Cases

#### {{use_case_1.title}}
{{use_case_1.description}}

```{{use_case_1.language}}
{{use_case_1.code}}
```

#### {{use_case_2.title}}
{{use_case_2.description}}

```{{use_case_2.language}}
{{use_case_2.code}}
```

## Next Steps
1. [Explore all API endpoints]({{docs_url}}/reference)
2. [Check out SDKs]({{docs_url}}/sdks)
3. [Join developer community]({{community_url}})

## Need Help?
- 📖 [Full Documentation]({{docs_url}})
- 💬 [Developer Community]({{community_url}})
- 📧 [Support Email](mailto:{{support_email}})
- 📞 [WhatsApp Support](https://wa.me/{{whatsapp_number}}) (India only)
            """
        }
    
    def add_api_version(self, version: APIVersion):
        """Add API version to documentation"""
        self.versions[version.version] = version
        logger.info(f"Added API version {version.version} to documentation")
    
    def generate_api_reference(self, version: str = None) -> str:
        """Generate complete API reference documentation"""
        template = Template(self.templates["api_reference"])
        
        if version:
            if version not in self.versions:
                raise ValueError(f"Version {version} not found")
            versions_to_document = [self.versions[version]]
            current_version = version
        else:
            # Document all versions
            versions_to_document = list(self.versions.values())
            current_version = self._get_latest_version()
        
        # Collect all endpoints from specified versions
        all_endpoints = []
        for v in versions_to_document:
            all_endpoints.extend(v.endpoints)
        
        return template.render(
            api_name=self.api_name,
            description="payment processing and digital wallet services",
            base_url=self.base_url,
            current_version=current_version,
            versions=versions_to_document,
            endpoints=all_endpoints
        )
    
    def generate_migration_guide(self, from_version: str, to_version: str) -> str:
        """Generate migration guide between versions"""
        if from_version not in self.versions or to_version not in self.versions:
            raise ValueError("Invalid version specified")
        
        from_ver = self.versions[from_version]
        to_ver = self.versions[to_version]
        
        # Generate breaking changes
        breaking_changes = self._identify_breaking_changes(from_ver, to_ver)
        
        template = Template(self.templates["migration_guide"])
        
        return template.render(
            api_name=self.api_name,
            from_version=from_version,
            to_version=to_version,
            deprecation_date="2024-06-01",
            sunset_date="2024-12-31",
            migration_window="6 months",
            breaking_changes=breaking_changes,
            migration_checklist=[
                "Review all breaking changes listed above",
                "Update API endpoints to new version",
                "Test payment flows in sandbox environment",
                "Update webhook handlers for new payload format",
                "Deploy changes to production",
                "Monitor for any issues post-migration"
            ]
        )
    
    def generate_quickstart_guide(self) -> str:
        """Generate quickstart guide"""
        template = Template(self.templates["quickstart"])
        
        latest_version = self._get_latest_version()
        
        return template.render(
            api_name=self.api_name,
            domain=self.api_name.lower() + ".com",
            base_url=self.base_url,
            sample_endpoint="payments",
            use_case_1={
                "title": "Create a Payment",
                "description": "Create a new payment request for ₹500",
                "language": "python",
                "code": '''
import paytm_sdk

client = paytm_sdk.Client(api_key="your_key")
payment = client.payments.create({
    "amount_in_paise": 50000,  # ₹500 in paise
    "currency": "INR",
    "customer": {
        "phone": "+919876543210",
        "email": "customer@example.com"
    },
    "callback_url": "https://yoursite.com/callback"
})

print(f"Payment ID: {payment['id']}")
print(f"Payment URL: {payment['checkout_url']}")
                '''
            },
            use_case_2={
                "title": "Check Payment Status",
                "description": "Check the status of a payment",
                "language": "python", 
                "code": '''
payment_id = "pay_12345"
status = client.payments.get(payment_id)

print(f"Status: {status['payment_status']}")
print(f"Amount: ₹{status['amount_in_paise'] / 100}")
                '''
            },
            docs_url=f"https://docs.{self.api_name.lower()}.com",
            community_url=f"https://community.{self.api_name.lower()}.com",
            support_email=f"developers@{self.api_name.lower()}.com",
            whatsapp_number="917042121212"
        )
    
    def generate_changelog(self) -> str:
        """Generate API changelog"""
        changelog = f"# {self.api_name} API Changelog\n\n"
        
        # Sort versions by release date (newest first)
        sorted_versions = sorted(
            self.versions.values(),
            key=lambda v: v.release_date,
            reverse=True
        )
        
        for version in sorted_versions:
            changelog += f"## Version {version.version} - {version.release_date}\n\n"
            changelog += f"{version.description}\n\n"
            
            if version.breaking_changes:
                changelog += "### 🚨 Breaking Changes\n"
                for change in version.breaking_changes:
                    changelog += f"- {change}\n"
                changelog += "\n"
            
            # List new endpoints
            new_endpoints = [ep for ep in version.endpoints if ep.added_in_version == version.version]
            if new_endpoints:
                changelog += "### ✨ New Endpoints\n"
                for endpoint in new_endpoints:
                    changelog += f"- `{endpoint.method.value} {endpoint.path}` - {endpoint.summary}\n"
                changelog += "\n"
            
            # List deprecated endpoints
            deprecated_endpoints = [ep for ep in version.endpoints if ep.deprecated and ep.deprecated_in_version == version.version]
            if deprecated_endpoints:
                changelog += "### ⚠️ Deprecated\n"
                for endpoint in deprecated_endpoints:
                    changelog += f"- `{endpoint.method.value} {endpoint.path}` - {endpoint.summary}\n"
                changelog += "\n"
            
            if version.migration_notes:
                changelog += "### 📝 Migration Notes\n"
                for note in version.migration_notes:
                    changelog += f"- {note}\n"
                changelog += "\n"
            
            changelog += "---\n\n"
        
        return changelog
    
    def _identify_breaking_changes(self, from_version: APIVersion, to_version: APIVersion) -> List[Dict[str, Any]]:
        """Identify breaking changes between versions"""
        breaking_changes = []
        
        # Example breaking changes for demo
        if from_version.version == "v1" and to_version.version == "v2":
            breaking_changes.extend([
                {
                    "title": "Amount Field Changed from Rupees to Paise",
                    "description": "The amount field now expects value in paise instead of rupees for better precision.",
                    "impact": "All payment creation calls will fail if not updated",
                    "action": "Multiply your rupee amounts by 100 to convert to paise",
                    "before_example": json.dumps({"amount": 100.50}, indent=2),
                    "after_example": json.dumps({"amount_in_paise": 10050}, indent=2)
                },
                {
                    "title": "Phone Number Format Requires Country Code",
                    "description": "Phone numbers must now include country code prefix.",
                    "impact": "Customer phone validation will fail",
                    "action": "Prefix all Indian phone numbers with +91",
                    "before_example": json.dumps({"phone": "9876543210"}, indent=2),
                    "after_example": json.dumps({"phone": "+919876543210"}, indent=2)
                }
            ])
        
        return breaking_changes
    
    def _get_latest_version(self) -> str:
        """Get the latest API version"""
        if not self.versions:
            return "1.0"
        
        # Simple version sorting (assumes semantic versioning)
        versions = list(self.versions.keys())
        versions.sort(key=lambda x: [int(n) for n in x.replace('v', '').split('.')])
        return versions[-1]
    
    def export_openapi_spec(self, version: str) -> Dict[str, Any]:
        """Export OpenAPI specification for a version"""
        if version not in self.versions:
            raise ValueError(f"Version {version} not found")
        
        api_version = self.versions[version]
        
        # Generate OpenAPI spec
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": f"{self.api_name} API",
                "version": version,
                "description": api_version.description,
                "contact": {
                    "name": f"{self.api_name} Developer Support",
                    "email": f"developers@{self.api_name.lower()}.com",
                    "url": f"https://docs.{self.api_name.lower()}.com"
                }
            },
            "servers": [
                {
                    "url": self.base_url,
                    "description": "Production server"
                },
                {
                    "url": self.base_url.replace("api", "api-sandbox"),
                    "description": "Sandbox server"
                }
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "ApiKeyAuth": {
                        "type": "apiKey",
                        "in": "header",
                        "name": "Authorization"
                    }
                }
            },
            "security": [
                {"ApiKeyAuth": []}
            ]
        }
        
        # Add endpoints to paths
        for endpoint in api_version.endpoints:
            path_key = endpoint.path
            method_key = endpoint.method.value.lower()
            
            if path_key not in spec["paths"]:
                spec["paths"][path_key] = {}
            
            # Build endpoint spec
            endpoint_spec = {
                "summary": endpoint.summary,
                "description": endpoint.description,
                "parameters": [],
                "responses": {}
            }
            
            # Add parameters
            for param in endpoint.parameters:
                param_spec = {
                    "name": param.name,
                    "in": param.param_type,
                    "required": param.required,
                    "description": param.description,
                    "schema": {"type": param.data_type}
                }
                if param.example:
                    param_spec["example"] = param.example
                
                endpoint_spec["parameters"].append(param_spec)
            
            # Add responses
            for response in endpoint.responses:
                endpoint_spec["responses"][str(response.status_code)] = {
                    "description": response.description,
                    "content": {
                        "application/json": {
                            "schema": response.schema,
                            "example": response.example
                        }
                    }
                }
            
            if endpoint.deprecated:
                endpoint_spec["deprecated"] = True
            
            spec["paths"][path_key][method_key] = endpoint_spec
        
        return spec

def create_sample_paytm_api_docs():
    """Create sample PayTM API documentation"""
    
    # Initialize documentation generator
    doc_gen = APIDocumentationGenerator("PayTM", "https://api.paytm.com")
    
    # Create V1 API version
    v1_endpoints = [
        APIEndpoint(
            path="/payments",
            method=HTTPMethod.POST,
            summary="Create Payment",
            description="Create a new payment request",
            parameters=[
                APIParameter("amount", "body", "number", True, "Amount in rupees", 100.50),
                APIParameter("phone", "body", "string", True, "Customer phone number", "9876543210"),
                APIParameter("email", "body", "string", False, "Customer email", "user@example.com")
            ],
            responses=[
                APIResponse(201, "Payment created successfully", 
                          {"type": "object", "properties": {"payment_id": {"type": "string"}}},
                          {"payment_id": "pay_123", "status": "created"})
            ],
            added_in_version="v1"
        ),
        APIEndpoint(
            path="/payments/{payment_id}",
            method=HTTPMethod.GET,
            summary="Get Payment Status",
            description="Retrieve payment status by ID",
            parameters=[
                APIParameter("payment_id", "path", "string", True, "Payment ID")
            ],
            responses=[
                APIResponse(200, "Payment details retrieved",
                          {"type": "object", "properties": {"status": {"type": "string"}}},
                          {"payment_id": "pay_123", "status": "completed", "amount": 100.50})
            ],
            added_in_version="v1"
        )
    ]
    
    v1 = APIVersion(
        version="v1",
        release_date="2023-01-15",
        status="deprecated",
        description="Initial PayTM API with basic payment functionality",
        endpoints=v1_endpoints,
        breaking_changes=[],
        migration_notes=["Basic payment processing", "Simple webhook notifications"]
    )
    
    # Create V2 API version
    v2_endpoints = [
        APIEndpoint(
            path="/payments",
            method=HTTPMethod.POST,
            summary="Create Payment",
            description="Create a new payment request with enhanced features",
            parameters=[
                APIParameter("amount_in_paise", "body", "integer", True, "Amount in paise (1 rupee = 100 paise)", 10050),
                APIParameter("customer", "body", "object", True, "Customer details"),
                APIParameter("callback_url", "body", "string", True, "Payment callback URL")
            ],
            responses=[
                APIResponse(201, "Payment created successfully",
                          {"type": "object", "properties": {"payment_id": {"type": "string"}, "checkout_url": {"type": "string"}}},
                          {"payment_id": "pay_456", "checkout_url": "https://checkout.paytm.com/pay_456", "status": "created"})
            ],
            added_in_version="v2"
        )
    ]
    
    v2 = APIVersion(
        version="v2", 
        release_date="2024-01-15",
        status="active",
        description="Enhanced PayTM API with UPI integration and better precision",
        endpoints=v2_endpoints,
        breaking_changes=[
            "Amount field changed from rupees to paise",
            "Customer phone number requires country code prefix",
            "New required callback_url parameter"
        ],
        migration_notes=[
            "Convert all amount values from rupees to paise (multiply by 100)",
            "Add +91 prefix to Indian phone numbers",
            "Implement callback URL handler for payment notifications"
        ]
    )
    
    # Add versions to documentation
    doc_gen.add_api_version(v1)
    doc_gen.add_api_version(v2)
    
    return doc_gen

def demonstrate_api_documentation_generation():
    """
    Demonstrate automated API documentation generation
    """
    print("🔥 API Documentation Generation - PayTM Style")
    print("=" * 60)
    
    # Create sample API documentation
    doc_gen = create_sample_paytm_api_docs()
    
    print("\n📚 Generating API Reference Documentation...")
    api_ref = doc_gen.generate_api_reference()
    print("✅ API Reference generated")
    
    print("\n🔄 Generating Migration Guide...")
    migration_guide = doc_gen.generate_migration_guide("v1", "v2")
    print("✅ Migration Guide generated")
    
    print("\n⚡ Generating Quick Start Guide...")
    quickstart = doc_gen.generate_quickstart_guide()
    print("✅ Quick Start Guide generated")
    
    print("\n📝 Generating Changelog...")
    changelog = doc_gen.generate_changelog()
    print("✅ Changelog generated")
    
    print("\n🔧 Generating OpenAPI Specification...")
    openapi_spec = doc_gen.export_openapi_spec("v2")
    print("✅ OpenAPI spec generated")
    
    # Show samples of generated documentation
    print("\n📖 Sample API Reference (First 1000 chars):")
    print("-" * 50)
    print(api_ref[:1000] + "..." if len(api_ref) > 1000 else api_ref)
    
    print("\n📖 Sample Migration Guide (First 800 chars):")
    print("-" * 50)
    print(migration_guide[:800] + "..." if len(migration_guide) > 800 else migration_guide)
    
    print("\n📊 OpenAPI Specification Summary:")
    print(f"  API Title: {openapi_spec['info']['title']}")
    print(f"  Version: {openapi_spec['info']['version']}")
    print(f"  Endpoints: {len(openapi_spec['paths'])}")
    print(f"  Security Schemes: {len(openapi_spec['components']['securitySchemes'])}")
    
    print("\n💡 Documentation Generation Benefits:")
    print("1. Consistent documentation across all versions")
    print("2. Automated migration guides reduce support burden")
    print("3. OpenAPI specs enable tool integration")
    print("4. Version-specific documentation prevents confusion")
    print("5. Code examples help developer adoption")
    
    print("\n🎯 PayTM Implementation Insights:")
    print("1. Multi-language code examples for Indian developers")
    print("2. WhatsApp support for quick developer assistance")
    print("3. Sandbox environment URLs for safe testing")
    print("4. Regional payment method examples (UPI, Cards)")
    print("5. Currency examples in INR with paise precision")
    
    # Export documentation files
    print("\n💾 Exporting Documentation Files...")
    
    # This would typically write to files
    documentation_files = {
        "api_reference_v2.md": api_ref,
        "migration_guide_v1_to_v2.md": migration_guide,
        "quickstart.md": quickstart,
        "changelog.md": changelog,
        "openapi_v2.json": json.dumps(openapi_spec, indent=2)
    }
    
    for filename, content in documentation_files.items():
        print(f"  ✅ {filename} ({len(content)} characters)")
    
    print(f"\nTotal documentation files generated: {len(documentation_files)}")

if __name__ == "__main__":
    demonstrate_api_documentation_generation()