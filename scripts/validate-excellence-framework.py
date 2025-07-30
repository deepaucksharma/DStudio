#!/usr/bin/env python3
"""
Excellence Framework Validation Script

Validates that all patterns have proper excellence tier metadata and 
tier-specific content requirements are met.

Usage:
    python3 scripts/validate-excellence-framework.py [options]
"""

import os
import sys
import yaml
import re
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass

PROJECT_ROOT = Path(__file__).parent.parent

@dataclass
class ValidationResult:
    success: bool
    errors: List[str]
    warnings: List[str]
    
class ExcellenceValidator:
    """Validate excellence framework requirements"""
    
    REQUIRED_TIERS = {'gold', 'silver', 'bronze'}
    VALID_STATUS = {
        'recommended', 'stable', 'use-with-expertise', 
        'use-with-caution', 'legacy', 'deprecated', 'experimental'
    }
    
    # Tier-specific content requirements
    GOLD_REQUIREMENTS = {
        'modern_examples': 'Modern examples with real companies',
        'production_checklist': 'Production readiness checklist'
    }
    
    SILVER_REQUIREMENTS = {
        'trade_offs': 'Trade-offs analysis (pros/cons)',
        'best_for': 'Usage guidelines (when to use)'
    }
    
    BRONZE_REQUIREMENTS = {
        'modern_alternatives': 'Modern alternatives section',
        'deprecation_reason': 'Deprecation context or legacy status'
    }
    
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.pattern_lib_path = project_root / "docs" / "pattern-library"
        
    def validate_all_patterns(self) -> ValidationResult:
        """Validate all patterns in the library"""
        errors = []
        warnings = []
        
        if not self.pattern_lib_path.exists():
            errors.append(f"Pattern library path not found: {self.pattern_lib_path}")
            return ValidationResult(False, errors, warnings)
        
        total_patterns = 0
        tier_counts = {'gold': 0, 'silver': 0, 'bronze': 0, 'missing': 0}
        
        for category_dir in self.pattern_lib_path.iterdir():
            if not category_dir.is_dir() or category_dir.name.startswith('.'):
                continue
                
            category = category_dir.name
            if self.verbose:
                print(f"📁 Validating category: {category}")
            
            for pattern_file in category_dir.glob("*.md"):
                if pattern_file.name == 'index.md':
                    continue
                    
                total_patterns += 1
                result = self._validate_pattern(pattern_file)
                
                errors.extend(result.errors)
                warnings.extend(result.warnings)
                
                # Count tiers
                tier = self._extract_tier(pattern_file)
                if tier in self.REQUIRED_TIERS:
                    tier_counts[tier] += 1
                else:
                    tier_counts['missing'] += 1
        
        # Summary validation
        self._validate_tier_distribution(tier_counts, total_patterns, errors, warnings)
        
        if self.verbose:
            print(f"\n📊 Pattern Summary:")
            print(f"   Total patterns: {total_patterns}")
            for tier, count in tier_counts.items():
                if count > 0:
                    percentage = (count / total_patterns) * 100 if total_patterns > 0 else 0
                    print(f"   {tier.title()}: {count} ({percentage:.1f}%)")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _validate_pattern(self, pattern_file: Path) -> ValidationResult:
        """Validate individual pattern file"""
        errors = []
        warnings = []
        
        relative_path = str(pattern_file.relative_to(self.project_root))
        
        try:
            with open(pattern_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract frontmatter
            frontmatter = self._extract_frontmatter(content)
            if not frontmatter:
                errors.append(f"{relative_path}: No YAML frontmatter found")
                return ValidationResult(False, errors, warnings)
            
            # Validate required fields
            tier = frontmatter.get('excellence_tier')
            status = frontmatter.get('pattern_status')
            
            if not tier:
                errors.append(f"{relative_path}: Missing 'excellence_tier' field")
            elif tier not in self.REQUIRED_TIERS:
                errors.append(f"{relative_path}: Invalid excellence_tier '{tier}'. Must be one of: {', '.join(self.REQUIRED_TIERS)}")
            
            if not status:
                errors.append(f"{relative_path}: Missing 'pattern_status' field")
            elif status not in self.VALID_STATUS:
                errors.append(f"{relative_path}: Invalid pattern_status '{status}'. Must be one of: {', '.join(self.VALID_STATUS)}")
            
            # Validate tier-specific requirements
            if tier in self.REQUIRED_TIERS:
                tier_errors, tier_warnings = self._validate_tier_requirements(
                    pattern_file, tier, frontmatter, content
                )
                errors.extend(tier_errors)
                warnings.extend(tier_warnings)
            
            # Validate consistency
            consistency_errors = self._validate_consistency(pattern_file, frontmatter, content)
            errors.extend(consistency_errors)
            
        except Exception as e:
            errors.append(f"{relative_path}: Failed to validate - {e}")
        
        return ValidationResult(len(errors) == 0, errors, warnings)
    
    def _validate_tier_requirements(self, pattern_file: Path, tier: str, 
                                  frontmatter: dict, content: str) -> tuple:
        """Validate tier-specific content requirements"""
        errors = []
        warnings = []
        relative_path = str(pattern_file.relative_to(self.project_root))
        
        if tier == 'gold':
            requirements = self.GOLD_REQUIREMENTS
            
            # Check for modern_examples in frontmatter
            if 'modern_examples' not in frontmatter or not frontmatter['modern_examples']:
                errors.append(f"{relative_path}: Gold pattern missing 'modern_examples' in frontmatter")
            
            # Check for production_checklist in frontmatter
            if 'production_checklist' not in frontmatter or not frontmatter['production_checklist']:
                errors.append(f"{relative_path}: Gold pattern missing 'production_checklist' in frontmatter")
            
            # Check content for production examples
            if 'production example' not in content.lower() and 'case study' not in content.lower():
                warnings.append(f"{relative_path}: Gold pattern should include production examples or case studies")
                
        elif tier == 'silver':
            # Check for trade_offs in frontmatter
            if 'trade_offs' not in frontmatter or not frontmatter['trade_offs']:
                errors.append(f"{relative_path}: Silver pattern missing 'trade_offs' in frontmatter")
            
            # Check for best_for in frontmatter
            if 'best_for' not in frontmatter or not frontmatter['best_for']:
                errors.append(f"{relative_path}: Silver pattern missing 'best_for' in frontmatter")
            
            # Check content for usage guidance
            usage_indicators = ['when to use', 'best for', 'ideal for', 'use cases']
            if not any(indicator in content.lower() for indicator in usage_indicators):
                warnings.append(f"{relative_path}: Silver pattern should include usage guidance")
                
        elif tier == 'bronze':
            # Check content for alternatives
            alt_indicators = ['alternative', 'modern approach', 'deprecated', 'legacy']
            if not any(indicator in content.lower() for indicator in alt_indicators):
                errors.append(f"{relative_path}: Bronze pattern should explain modern alternatives or deprecation reason")
            
            # Check for migration guidance
            migration_indicators = ['migration', 'upgrade', 'replace', 'modernize']
            if not any(indicator in content.lower() for indicator in migration_indicators):
                warnings.append(f"{relative_path}: Bronze pattern should include migration guidance")
        
        return errors, warnings
    
    def _validate_consistency(self, pattern_file: Path, frontmatter: dict, content: str) -> List[str]:
        """Validate consistency between frontmatter and content"""
        errors = []
        relative_path = str(pattern_file.relative_to(self.project_root))
        
        tier = frontmatter.get('excellence_tier')
        
        # Check for tier badge consistency
        if tier == 'gold' and '🏆 Gold Standard Pattern' not in content:
            errors.append(f"{relative_path}: Gold pattern missing gold badge in content")
        elif tier == 'silver' and '🥈 Silver' not in content:
            errors.append(f"{relative_path}: Silver pattern missing silver badge in content")
        elif tier == 'bronze' and '🥉 Bronze' not in content:
            errors.append(f"{relative_path}: Bronze pattern missing bronze badge in content")
        
        # Check category consistency
        category = frontmatter.get('category')
        expected_category = pattern_file.parent.name
        if category and category != expected_category:
            errors.append(f"{relative_path}: Category mismatch - frontmatter: '{category}', folder: '{expected_category}'")
        
        return errors
    
    def _validate_tier_distribution(self, tier_counts: dict, total_patterns: int, 
                                  errors: List[str], warnings: List[str]):
        """Validate overall tier distribution makes sense"""
        if total_patterns == 0:
            return
        
        gold_pct = (tier_counts['gold'] / total_patterns) * 100
        silver_pct = (tier_counts['silver'] / total_patterns) * 100
        bronze_pct = (tier_counts['bronze'] / total_patterns) * 100
        
        # Guidelines for tier distribution
        if gold_pct > 40:
            warnings.append(f"High percentage of Gold patterns ({gold_pct:.1f}%) - ensure quality standards are maintained")
        
        if bronze_pct > 30:
            warnings.append(f"High percentage of Bronze patterns ({bronze_pct:.1f}%) - consider migration guides")
        
        if tier_counts['missing'] > 0:
            errors.append(f"{tier_counts['missing']} patterns missing excellence tier metadata")
    
    def _extract_frontmatter(self, content: str) -> Optional[dict]:
        """Extract YAML frontmatter from markdown content"""
        if not content.startswith('---'):
            return None
        
        end_marker = content.find('---', 3)
        if end_marker == -1:
            return None
        
        frontmatter_yaml = content[3:end_marker].strip()
        try:
            return yaml.safe_load(frontmatter_yaml) or {}
        except yaml.YAMLError:
            return None
    
    def _extract_tier(self, pattern_file: Path) -> Optional[str]:
        """Extract tier from pattern file"""
        try:
            with open(pattern_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter = self._extract_frontmatter(content)
            return frontmatter.get('excellence_tier') if frontmatter else None
        except:
            return None

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Excellence Framework Validator')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--pattern', help='Validate specific pattern file')
    parser.add_argument('--category', help='Validate specific category only')
    parser.add_argument('--tier', choices=['gold', 'silver', 'bronze'], 
                       help='Validate specific tier only')
    
    args = parser.parse_args()
    
    validator = ExcellenceValidator(PROJECT_ROOT, verbose=args.verbose)
    
    try:
        if args.pattern:
            # Validate single pattern
            pattern_file = Path(args.pattern)
            if not pattern_file.is_absolute():
                pattern_file = PROJECT_ROOT / pattern_file
            
            result = validator._validate_pattern(pattern_file)
        else:
            # Validate all patterns
            result = validator.validate_all_patterns()
        
        # Output results
        if result.warnings:
            print("⚠️  Warnings:")
            for warning in result.warnings:
                print(f"  {warning}")
            print()
        
        if result.errors:
            print("❌ Errors:")
            for error in result.errors:
                print(f"  {error}")
            print()
            print(f"Found {len(result.errors)} errors and {len(result.warnings)} warnings")
            sys.exit(1)
        else:
            print("✅ Excellence framework validation passed!")
            if result.warnings:
                print(f"Found {len(result.warnings)} warnings")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()