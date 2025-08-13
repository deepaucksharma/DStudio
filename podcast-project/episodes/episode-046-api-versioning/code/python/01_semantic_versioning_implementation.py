#!/usr/bin/env python3
"""
Semantic Versioning Implementation for API Evolution
Inspired by UPI API evolution (1.0 -> 2.0 -> 3.0)

Example: UPI API ne kaise evolve kiya - from simple payment to multi-bank support
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

class VersionType(Enum):
    """Version types according to semantic versioning"""
    MAJOR = "major"  # Breaking changes - जैसे UPI 1.0 se 2.0
    MINOR = "minor"  # New features - नई functionality add करना
    PATCH = "patch"  # Bug fixes - bug fixes और security patches

@dataclass
class APIVersion:
    """API version representation with Indian context"""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, APIVersion):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __lt__(self, other) -> bool:
        if not isinstance(other, APIVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

class SemanticVersionManager:
    """
    Semantic version manager for API evolution
    Example: UPI payments ki tarah version management
    """
    
    def __init__(self, initial_version: str = "1.0.0"):
        self.current_version = self.parse_version(initial_version)
        self.version_history: List[Tuple[APIVersion, str, datetime]] = []
        self.deprecated_versions: Dict[APIVersion, datetime] = {}
        
        # Track version like UPI API evolution
        self.add_to_history("Initial release - Basic UPI functionality")
    
    def parse_version(self, version_string: str) -> APIVersion:
        """Parse semantic version string"""
        pattern = r'^(\d+)\.(\d+)\.(\d+)$'
        match = re.match(pattern, version_string)
        
        if not match:
            raise ValueError(f"Invalid semantic version: {version_string}")
        
        major, minor, patch = match.groups()
        return APIVersion(int(major), int(minor), int(patch))
    
    def bump_version(self, version_type: VersionType, description: str) -> APIVersion:
        """
        Bump version based on type of change
        Example: UPI API evolution scenarios
        """
        old_version = self.current_version
        
        if version_type == VersionType.MAJOR:
            # Breaking changes - जैसे payment format change
            self.current_version = APIVersion(
                old_version.major + 1, 0, 0
            )
        elif version_type == VersionType.MINOR:
            # New features - जैसे multi-bank support add करना
            self.current_version = APIVersion(
                old_version.major, old_version.minor + 1, 0
            )
        else:  # PATCH
            # Bug fixes - जैसे security patches
            self.current_version = APIVersion(
                old_version.major, old_version.minor, old_version.patch + 1
            )
        
        self.add_to_history(description)
        print(f"Version bumped: {old_version} -> {self.current_version}")
        print(f"Change: {description}")
        
        return self.current_version
    
    def add_to_history(self, description: str):
        """Add version to history"""
        self.version_history.append((
            self.current_version, description, datetime.now()
        ))
    
    def deprecate_version(self, version_string: str, sunset_date: datetime = None):
        """
        Deprecate a version like UPI 1.0 deprecation
        """
        version = self.parse_version(version_string)
        if sunset_date is None:
            sunset_date = datetime.now() + timedelta(days=365)  # 1 year notice
        
        self.deprecated_versions[version] = sunset_date
        print(f"Version {version} deprecated. Sunset date: {sunset_date.strftime('%Y-%m-%d')}")
    
    def is_compatible(self, requested_version: str, current_version: str = None) -> bool:
        """
        Check version compatibility using semantic versioning rules
        Major version changes are breaking
        """
        if current_version is None:
            current = self.current_version
        else:
            current = self.parse_version(current_version)
        
        requested = self.parse_version(requested_version)
        
        # Same major version = backward compatible
        if requested.major == current.major:
            return requested <= current
        
        # Different major version = potentially breaking
        return False
    
    def get_supported_versions(self) -> List[APIVersion]:
        """Get list of currently supported versions"""
        now = datetime.now()
        supported = []
        
        for version, sunset_date in self.deprecated_versions.items():
            if now <= sunset_date:
                supported.append(version)
        
        # Current version is always supported
        if self.current_version not in supported:
            supported.append(self.current_version)
        
        return sorted(supported)
    
    def get_migration_path(self, from_version: str, to_version: str) -> List[str]:
        """
        Generate migration path between versions
        Example: UPI 1.0 se 3.0 tak ka path
        """
        from_ver = self.parse_version(from_version)
        to_ver = self.parse_version(to_version)
        
        if from_ver == to_ver:
            return ["No migration needed - same version"]
        
        migration_steps = []
        
        # Major version changes need special handling
        if from_ver.major != to_ver.major:
            migration_steps.append(
                f"BREAKING CHANGE: Major version change {from_ver.major} -> {to_ver.major}"
            )
            migration_steps.append("Review API contract changes")
            migration_steps.append("Update client code for new endpoints")
            migration_steps.append("Test with new request/response formats")
        
        # Minor version changes
        if from_ver.minor < to_ver.minor:
            migration_steps.append(
                f"Feature updates: Minor version {from_ver.minor} -> {to_ver.minor}"
            )
            migration_steps.append("Review new optional parameters")
            migration_steps.append("Test new functionality")
        
        # Patch version changes
        if from_ver.patch < to_ver.patch:
            migration_steps.append(
                f"Bug fixes: Patch version {from_ver.patch} -> {to_ver.patch}"
            )
            migration_steps.append("Update to latest security fixes")
        
        return migration_steps
    
    def generate_changelog(self) -> Dict:
        """Generate changelog like major APIs do"""
        changelog = {
            "api_name": "UPI Payment API",
            "current_version": str(self.current_version),
            "versions": [],
            "deprecated_versions": {}
        }
        
        for version, description, date in reversed(self.version_history):
            changelog["versions"].append({
                "version": str(version),
                "description": description,
                "release_date": date.strftime("%Y-%m-%d %H:%M:%S"),
                "type": self._classify_change(description)
            })
        
        for version, sunset_date in self.deprecated_versions.items():
            changelog["deprecated_versions"][str(version)] = sunset_date.strftime("%Y-%m-%d")
        
        return changelog
    
    def _classify_change(self, description: str) -> str:
        """Classify change type from description"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['breaking', 'removed', 'incompatible']):
            return "breaking"
        elif any(word in description_lower for word in ['added', 'new', 'feature']):
            return "feature"
        elif any(word in description_lower for word in ['fixed', 'bug', 'security']):
            return "fix"
        else:
            return "other"

def demonstrate_upi_api_evolution():
    """
    Demonstrate UPI API evolution using semantic versioning
    Real-world example of how UPI evolved over time
    """
    print("🔥 UPI API Evolution - Semantic Versioning Example")
    print("=" * 60)
    
    # Initialize with UPI 1.0
    upi_api = SemanticVersionManager("1.0.0")
    
    # UPI 1.1 - Minor feature additions
    upi_api.bump_version(
        VersionType.MINOR,
        "Added QR code payment support - QR code se payment functionality"
    )
    
    # UPI 1.1.1 - Bug fix
    upi_api.bump_version(
        VersionType.PATCH,
        "Fixed transaction timeout issues - timeout ka bug fix"
    )
    
    # UPI 1.2 - More features
    upi_api.bump_version(
        VersionType.MINOR,
        "Added multi-bank support - multiple banks ke saath integration"
    )
    
    # UPI 2.0 - Major breaking change
    upi_api.bump_version(
        VersionType.MAJOR,
        "New authentication system - OAuth 2.0 migration (BREAKING CHANGE)"
    )
    
    # UPI 2.1 - New features on v2
    upi_api.bump_version(
        VersionType.MINOR,
        "Added international payments - विदेशी payment support"
    )
    
    print("\n📊 Current API Status:")
    print(f"Current Version: {upi_api.current_version}")
    
    # Test version compatibility
    print("\n🔍 Version Compatibility Check:")
    test_versions = ["1.0.0", "1.1.0", "2.0.0", "2.1.0", "3.0.0"]
    
    for version in test_versions:
        try:
            compatible = upi_api.is_compatible(version)
            print(f"Version {version}: {'✅ Compatible' if compatible else '❌ Not Compatible'}")
        except ValueError as e:
            print(f"Version {version}: ❌ Invalid version")
    
    # Deprecate old version
    print("\n⚠️  Deprecating Old Version:")
    upi_api.deprecate_version("1.0.0")
    
    # Show migration path
    print("\n🛣️  Migration Path (1.0.0 -> 2.1.0):")
    migration_steps = upi_api.get_migration_path("1.0.0", "2.1.0")
    for i, step in enumerate(migration_steps, 1):
        print(f"{i}. {step}")
    
    # Generate changelog
    print("\n📝 API Changelog:")
    changelog = upi_api.generate_changelog()
    print(json.dumps(changelog, indent=2))
    
    print("\n🎯 Key Takeaways:")
    print("1. Major version changes indicate breaking changes")
    print("2. Minor versions add features without breaking existing functionality")
    print("3. Patch versions are for bug fixes and security updates")
    print("4. Always provide migration paths for version upgrades")
    print("5. Give adequate notice before deprecating versions")

if __name__ == "__main__":
    demonstrate_upi_api_evolution()