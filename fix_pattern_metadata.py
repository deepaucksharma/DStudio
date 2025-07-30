#!/usr/bin/env python3
'''
Auto-generated script to fix pattern metadata issues
'''

import yaml
import re
from pathlib import Path

def update_field(file_path: str, field: str, new_value: str):
    '''Update a field value in the frontmatter.'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            print(f"No frontmatter found in {file_path}")
            return
        
        end_marker = content.find('\n---\n', 3)
        if end_marker == -1:
            end_marker = content.find('\n---', 3)
            if end_marker == -1:
                print(f"Could not find end of frontmatter in {file_path}")
                return
        
        frontmatter = content[3:end_marker].strip()
        body = content[end_marker + 4:]
        
        # Parse and update
        data = yaml.safe_load(frontmatter) or {}
        data[field] = new_value
        
        # Write back
        new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_frontmatter}---\n{body}"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Updated {field} in {file_path}")
    
    except Exception as e:
        print(f"Error updating {file_path}: {e}")

def rename_field(file_path: str, old_field: str, new_field: str):
    '''Rename a field in the frontmatter.'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            print(f"No frontmatter found in {file_path}")
            return
        
        end_marker = content.find('\n---\n', 3)
        if end_marker == -1:
            end_marker = content.find('\n---', 3)
            if end_marker == -1:
                print(f"Could not find end of frontmatter in {file_path}")
                return
        
        frontmatter = content[3:end_marker].strip()
        body = content[end_marker + 4:]
        
        # Parse, rename, and update
        data = yaml.safe_load(frontmatter) or {}
        if old_field in data:
            data[new_field] = data.pop(old_field)
            
            # Write back
            new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{new_frontmatter}---\n{body}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Renamed {old_field} to {new_field} in {file_path}")
    
    except Exception as e:
        print(f"Error renaming field in {file_path}: {e}")

def add_missing_field(file_path: str, field: str, value: str):
    '''Add a missing field to the frontmatter.'''
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            # Add frontmatter if missing
            new_content = f"---\n{field}: {value}\n---\n{content}"
        else:
            end_marker = content.find('\n---\n', 3)
            if end_marker == -1:
                end_marker = content.find('\n---', 3)
                if end_marker == -1:
                    print(f"Could not find end of frontmatter in {file_path}")
                    return
            
            frontmatter = content[3:end_marker].strip()
            body = content[end_marker + 4:]
            
            # Parse and add field
            data = yaml.safe_load(frontmatter) or {}
            if field not in data:
                data[field] = value
                
                # Write back
                new_frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False)
                new_content = f"---\n{new_frontmatter}---\n{body}"
            else:
                print(f"Field {field} already exists in {file_path}")
                return
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Added {field} to {file_path}")
    
    except Exception as e:
        print(f"Error adding field to {file_path}: {e}")

if __name__ == "__main__":
    print("Starting pattern metadata fixes...")
    
    # Fixes for docs/pattern-library/architecture/anti-corruption-layer.md
    update_field('docs/pattern-library/architecture/anti-corruption-layer.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/architecture/anti-corruption-layer.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/anti-corruption-layer.md', 'pattern_type', 'pattern-type')
    rename_field('docs/pattern-library/architecture/anti-corruption-layer.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/anti-corruption-layer.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/architecture/anti-corruption-layer.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/architecture/shared-nothing.md
    update_field('docs/pattern-library/architecture/shared-nothing.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/architecture/shared-nothing.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/shared-nothing.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/architecture/shared-nothing.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/architecture/shared-nothing.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/shared-nothing.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/shared-nothing.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/architecture/graphql-federation.md
    rename_field('docs/pattern-library/architecture/graphql-federation.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/graphql-federation.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/graphql-federation.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/graphql-federation.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/graphql-federation.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/architecture/graphql-federation.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/architecture/choreography.md
    rename_field('docs/pattern-library/architecture/choreography.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/choreography.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/architecture/choreography.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/architecture/choreography.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/choreography.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/choreography.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/choreography.md', 'deprecation_reason', 'deprecation-reason')
    rename_field('docs/pattern-library/architecture/choreography.md', 'modern_alternatives', 'modern-alternatives')
    rename_field('docs/pattern-library/architecture/choreography.md', 'migration_guide', 'migration-guide')
    # Fixes for docs/pattern-library/architecture/kappa-architecture.md
    rename_field('docs/pattern-library/architecture/kappa-architecture.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/kappa-architecture.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/kappa-architecture.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/kappa-architecture.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/kappa-architecture.md', 'modern_alternatives', 'modern-alternatives')
    rename_field('docs/pattern-library/architecture/kappa-architecture.md', 'deprecation_reason', 'deprecation-reason')
    # Fixes for docs/pattern-library/architecture/cell-based.md
    update_field('docs/pattern-library/architecture/cell-based.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/architecture/cap-theorem.md
    update_field('docs/pattern-library/architecture/cap-theorem.md', 'pattern_status', 'use-with-caution')
    rename_field('docs/pattern-library/architecture/cap-theorem.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/cap-theorem.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/cap-theorem.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/cap-theorem.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/cap-theorem.md', 'modern_context', 'modern-context')
    rename_field('docs/pattern-library/architecture/cap-theorem.md', 'educational_value', 'educational-value')
    # Fixes for docs/pattern-library/architecture/event-driven.md
    update_field('docs/pattern-library/architecture/event-driven.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/architecture/ambassador.md
    update_field('docs/pattern-library/architecture/ambassador.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/architecture/ambassador.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/ambassador.md', 'pattern_type', 'pattern-type')
    rename_field('docs/pattern-library/architecture/ambassador.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/ambassador.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/architecture/ambassador.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/architecture/strangler-fig.md
    update_field('docs/pattern-library/architecture/strangler-fig.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/architecture/strangler-fig.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/strangler-fig.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/strangler-fig.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/strangler-fig.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/architecture/event-streaming.md
    rename_field('docs/pattern-library/architecture/event-streaming.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/event-streaming.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/event-streaming.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/event-streaming.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/event-streaming.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/architecture/event-streaming.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/architecture/sidecar.md
    rename_field('docs/pattern-library/architecture/sidecar.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/sidecar.md', 'pattern_type', 'pattern-type')
    rename_field('docs/pattern-library/architecture/sidecar.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/sidecar.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/architecture/sidecar.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/architecture/lambda-architecture.md
    rename_field('docs/pattern-library/architecture/lambda-architecture.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/lambda-architecture.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/lambda-architecture.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/lambda-architecture.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/lambda-architecture.md', 'modern_alternatives', 'modern-alternatives')
    rename_field('docs/pattern-library/architecture/lambda-architecture.md', 'deprecation_reason', 'deprecation-reason')
    # Fixes for docs/pattern-library/architecture/backends-for-frontends.md
    update_field('docs/pattern-library/architecture/backends-for-frontends.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/architecture/backends-for-frontends.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/backends-for-frontends.md', 'pattern_type', 'pattern-type')
    rename_field('docs/pattern-library/architecture/backends-for-frontends.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/backends-for-frontends.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/architecture/backends-for-frontends.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/architecture/valet-key.md
    update_field('docs/pattern-library/architecture/valet-key.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/architecture/valet-key.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/valet-key.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/valet-key.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/valet-key.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/architecture/serverless-faas.md
    update_field('docs/pattern-library/architecture/serverless-faas.md', 'pattern_status', 'use-with-expertise')
    rename_field('docs/pattern-library/architecture/serverless-faas.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/architecture/serverless-faas.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/architecture/serverless-faas.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/architecture/serverless-faas.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/architecture/serverless-faas.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/architecture/serverless-faas.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/coordination/hlc.md
    rename_field('docs/pattern-library/coordination/hlc.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/hlc.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/hlc.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/hlc.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/coordination/hlc.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/coordination/hlc.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/coordination/emergent-leader.md
    update_field('docs/pattern-library/coordination/emergent-leader.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/coordination/emergent-leader.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/emergent-leader.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/emergent-leader.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/emergent-leader.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/coordination/distributed-queue.md
    rename_field('docs/pattern-library/coordination/distributed-queue.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/distributed-queue.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/distributed-queue.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/distributed-queue.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/coordination/distributed-queue.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/coordination/distributed-queue.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/coordination/leader-follower.md
    update_field('docs/pattern-library/coordination/leader-follower.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/coordination/leader-follower.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/leader-follower.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/leader-follower.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/leader-follower.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/coordination/consensus.md
    rename_field('docs/pattern-library/coordination/consensus.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/consensus.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/consensus.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/consensus.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/coordination/consensus.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/coordination/consensus.md', 'production_checklist', 'production-checklist')
    rename_field('docs/pattern-library/coordination/consensus.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/coordination/consensus.md', 'related_pillars', 'related-pillars')
    # Fixes for docs/pattern-library/coordination/generation-clock.md
    update_field('docs/pattern-library/coordination/generation-clock.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/coordination/generation-clock.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/generation-clock.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/generation-clock.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/generation-clock.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/coordination/cas.md
    rename_field('docs/pattern-library/coordination/cas.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/cas.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/cas.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/cas.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/coordination/cas.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/coordination/cas.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/coordination/logical-clocks.md
    update_field('docs/pattern-library/coordination/logical-clocks.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/coordination/logical-clocks.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/logical-clocks.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/logical-clocks.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/logical-clocks.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/coordination/distributed-lock.md
    update_field('docs/pattern-library/coordination/distributed-lock.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/coordination/lease.md
    update_field('docs/pattern-library/coordination/lease.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/coordination/lease.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/lease.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/lease.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/lease.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/coordination/state-watch.md
    update_field('docs/pattern-library/coordination/state-watch.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/coordination/state-watch.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/state-watch.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/state-watch.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/state-watch.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/coordination/leader-election.md
    rename_field('docs/pattern-library/coordination/leader-election.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/leader-election.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/leader-election.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/leader-election.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/coordination/leader-election.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/coordination/leader-election.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/coordination/actor-model.md
    rename_field('docs/pattern-library/coordination/actor-model.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/actor-model.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/actor-model.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/actor-model.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/coordination/actor-model.md', 'modern_alternatives', 'modern-alternatives')
    rename_field('docs/pattern-library/coordination/actor-model.md', 'still_valid_for', 'still-valid-for')
    rename_field('docs/pattern-library/coordination/actor-model.md', 'migration_guide', 'migration-guide')
    rename_field('docs/pattern-library/coordination/actor-model.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/coordination/actor-model.md', 'related_pillars', 'related-pillars')
    # Fixes for docs/pattern-library/coordination/clock-sync.md
    update_field('docs/pattern-library/coordination/clock-sync.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/coordination/clock-sync.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/clock-sync.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/clock-sync.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/clock-sync.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/coordination/low-high-water-marks.md
    update_field('docs/pattern-library/coordination/low-high-water-marks.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/coordination/low-high-water-marks.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/coordination/low-high-water-marks.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/coordination/low-high-water-marks.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/coordination/low-high-water-marks.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/data-management/shared-database.md
    rename_field('docs/pattern-library/data-management/shared-database.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/shared-database.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/shared-database.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/shared-database.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/shared-database.md', 'modern_alternatives', 'modern-alternatives')
    rename_field('docs/pattern-library/data-management/shared-database.md', 'deprecation_reason', 'deprecation-reason')
    rename_field('docs/pattern-library/data-management/shared-database.md', 'migration_guide', 'migration-guide')
    # Fixes for docs/pattern-library/data-management/polyglot-persistence.md
    update_field('docs/pattern-library/data-management/polyglot-persistence.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/data-management/polyglot-persistence.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/polyglot-persistence.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/polyglot-persistence.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/polyglot-persistence.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/data-management/distributed-storage.md
    rename_field('docs/pattern-library/data-management/distributed-storage.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/distributed-storage.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/distributed-storage.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/distributed-storage.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/distributed-storage.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/data-management/distributed-storage.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/data-management/eventual-consistency.md
    update_field('docs/pattern-library/data-management/eventual-consistency.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/data-management/eventual-consistency.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/eventual-consistency.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/eventual-consistency.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/eventual-consistency.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/data-management/outbox.md
    update_field('docs/pattern-library/data-management/outbox.md', 'pattern_status', 'use-with-expertise')
    rename_field('docs/pattern-library/data-management/outbox.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/outbox.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/outbox.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/outbox.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/outbox.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/data-management/outbox.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/data-management/cdc.md
    update_field('docs/pattern-library/data-management/cdc.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/data-management/saga.md
    rename_field('docs/pattern-library/data-management/saga.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/saga.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/saga.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/saga.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/data-management/saga.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/data-management/saga.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/saga.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/data-management/saga.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/data-management/event-sourcing.md
    update_field('docs/pattern-library/data-management/event-sourcing.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/data-management/segmented-log.md
    update_field('docs/pattern-library/data-management/segmented-log.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/data-management/segmented-log.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/segmented-log.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/segmented-log.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/segmented-log.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/data-management/read-repair.md
    rename_field('docs/pattern-library/data-management/read-repair.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/read-repair.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/read-repair.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/read-repair.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/read-repair.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/data-management/read-repair.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/data-management/data-lake.md
    update_field('docs/pattern-library/data-management/data-lake.md', 'pattern_status', 'use-with-expertise')
    rename_field('docs/pattern-library/data-management/data-lake.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/data-lake.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/data-lake.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/data-lake.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/data-lake.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/data-management/data-lake.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/data-management/data-lake.md', 'related_pillars', 'related-pillars')
    # Fixes for docs/pattern-library/data-management/bloom-filter.md
    rename_field('docs/pattern-library/data-management/bloom-filter.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/bloom-filter.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/bloom-filter.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/bloom-filter.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/bloom-filter.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/data-management/bloom-filter.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/data-management/tunable-consistency.md
    update_field('docs/pattern-library/data-management/tunable-consistency.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/data-management/tunable-consistency.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/tunable-consistency.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/tunable-consistency.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/tunable-consistency.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/data-management/materialized-view.md
    rename_field('docs/pattern-library/data-management/materialized-view.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/materialized-view.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/materialized-view.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/materialized-view.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/materialized-view.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/data-management/materialized-view.md', 'production_checklist', 'production-checklist')
    rename_field('docs/pattern-library/data-management/materialized-view.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/data-management/materialized-view.md', 'related_pillars', 'related-pillars')
    # Fixes for docs/pattern-library/data-management/deduplication.md
    rename_field('docs/pattern-library/data-management/deduplication.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/deduplication.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/deduplication.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/deduplication.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/deduplication.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/data-management/deduplication.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/data-management/lsm-tree.md
    update_field('docs/pattern-library/data-management/lsm-tree.md', 'pattern_status', 'use-with-expertise')
    rename_field('docs/pattern-library/data-management/lsm-tree.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/lsm-tree.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/lsm-tree.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/lsm-tree.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/lsm-tree.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/data-management/lsm-tree.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/data-management/merkle-trees.md
    rename_field('docs/pattern-library/data-management/merkle-trees.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/merkle-trees.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/merkle-trees.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/merkle-trees.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/merkle-trees.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/data-management/merkle-trees.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/data-management/cqrs.md
    update_field('docs/pattern-library/data-management/cqrs.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/data-management/write-ahead-log.md
    update_field('docs/pattern-library/data-management/write-ahead-log.md', 'pattern_status', 'use-with-expertise')
    rename_field('docs/pattern-library/data-management/write-ahead-log.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/write-ahead-log.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/write-ahead-log.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/write-ahead-log.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/write-ahead-log.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/data-management/write-ahead-log.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/data-management/consistent-hashing.md
    update_field('docs/pattern-library/data-management/consistent-hashing.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/data-management/crdt.md
    rename_field('docs/pattern-library/data-management/crdt.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/crdt.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/crdt.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/crdt.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/crdt.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/data-management/crdt.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/data-management/delta-sync.md
    update_field('docs/pattern-library/data-management/delta-sync.md', 'pattern_status', 'use-with-expertise')
    rename_field('docs/pattern-library/data-management/delta-sync.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/data-management/delta-sync.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/data-management/delta-sync.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/data-management/delta-sync.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/data-management/delta-sync.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/data-management/delta-sync.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/data-management/delta-sync.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/data-management/delta-sync.md', 'related_pillars', 'related-pillars')
    # Fixes for docs/pattern-library/scaling/caching-strategies.md
    rename_field('docs/pattern-library/scaling/caching-strategies.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/caching-strategies.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/caching-strategies.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/caching-strategies.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/caching-strategies.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/scaling/caching-strategies.md', 'production_checklist', 'production-checklist')
    rename_field('docs/pattern-library/scaling/caching-strategies.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/scaling/caching-strategies.md', 'related_pillars', 'related-pillars')
    # Fixes for docs/pattern-library/scaling/geo-distribution.md
    update_field('docs/pattern-library/scaling/geo-distribution.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/scaling/multi-region.md
    update_field('docs/pattern-library/scaling/multi-region.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/scaling/sharding.md
    update_field('docs/pattern-library/scaling/sharding.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/scaling/tile-caching.md
    update_field('docs/pattern-library/scaling/tile-caching.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/scaling/tile-caching.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/tile-caching.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/tile-caching.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/tile-caching.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/scaling/backpressure.md
    update_field('docs/pattern-library/scaling/backpressure.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/scaling/queues-streaming.md
    rename_field('docs/pattern-library/scaling/queues-streaming.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/queues-streaming.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/queues-streaming.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/queues-streaming.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/queues-streaming.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/scaling/queues-streaming.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/scaling/analytics-scale.md
    update_field('docs/pattern-library/scaling/analytics-scale.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/scaling/analytics-scale.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/analytics-scale.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/analytics-scale.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/analytics-scale.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/analytics-scale.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/scaling/analytics-scale.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/scaling/geo-replication.md
    rename_field('docs/pattern-library/scaling/geo-replication.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/geo-replication.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/geo-replication.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/geo-replication.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/geo-replication.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/scaling/geo-replication.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/scaling/auto-scaling.md
    update_field('docs/pattern-library/scaling/auto-scaling.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/scaling/id-generation-scale.md
    rename_field('docs/pattern-library/scaling/id-generation-scale.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/id-generation-scale.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/id-generation-scale.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/id-generation-scale.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/id-generation-scale.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/scaling/id-generation-scale.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/scaling/edge-computing.md
    rename_field('docs/pattern-library/scaling/edge-computing.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/edge-computing.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/edge-computing.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/edge-computing.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/edge-computing.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/scaling/edge-computing.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/scaling/request-batching.md
    rename_field('docs/pattern-library/scaling/request-batching.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/request-batching.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/request-batching.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/request-batching.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/request-batching.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/scaling/request-batching.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/scaling/chunking.md
    update_field('docs/pattern-library/scaling/chunking.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/scaling/chunking.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/chunking.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/chunking.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/chunking.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/chunking.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/scaling/chunking.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/scaling/priority-queue.md
    rename_field('docs/pattern-library/scaling/priority-queue.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/priority-queue.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/priority-queue.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/priority-queue.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/priority-queue.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/scaling/priority-queue.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/scaling/rate-limiting.md
    rename_field('docs/pattern-library/scaling/rate-limiting.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/rate-limiting.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/rate-limiting.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/rate-limiting.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/scaling/rate-limiting.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/scaling/rate-limiting.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/rate-limiting.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/scaling/rate-limiting.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/scaling/load-balancing.md
    update_field('docs/pattern-library/scaling/load-balancing.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/scaling/scatter-gather.md
    rename_field('docs/pattern-library/scaling/scatter-gather.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/scatter-gather.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/scatter-gather.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/scatter-gather.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/scaling/scatter-gather.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/scaling/scatter-gather.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/scaling/url-normalization.md
    update_field('docs/pattern-library/scaling/url-normalization.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/scaling/url-normalization.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/scaling/url-normalization.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/scaling/url-normalization.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/scaling/url-normalization.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/communication/publish-subscribe.md
    rename_field('docs/pattern-library/communication/publish-subscribe.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/communication/publish-subscribe.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/communication/publish-subscribe.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/communication/publish-subscribe.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/communication/publish-subscribe.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/communication/publish-subscribe.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/communication/api-gateway.md
    rename_field('docs/pattern-library/communication/api-gateway.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/communication/api-gateway.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/communication/api-gateway.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/communication/api-gateway.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/communication/api-gateway.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/communication/api-gateway.md', 'production_checklist', 'production-checklist')
    rename_field('docs/pattern-library/communication/api-gateway.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/communication/api-gateway.md', 'related_pillars', 'related-pillars')
    # Fixes for docs/pattern-library/communication/request-reply.md
    rename_field('docs/pattern-library/communication/request-reply.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/communication/request-reply.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/communication/request-reply.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/communication/request-reply.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/communication/request-reply.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/communication/request-reply.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/communication/service-registry.md
    rename_field('docs/pattern-library/communication/service-registry.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/communication/service-registry.md', 'pattern_type', 'pattern-type')
    rename_field('docs/pattern-library/communication/service-registry.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/communication/service-registry.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/communication/service-registry.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/communication/service-mesh.md
    update_field('docs/pattern-library/communication/service-mesh.md', 'pattern_status', 'recommended')
    # Fixes for docs/pattern-library/communication/websocket.md
    rename_field('docs/pattern-library/communication/websocket.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/communication/websocket.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/communication/websocket.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/communication/websocket.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/communication/websocket.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/communication/websocket.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/communication/grpc.md
    rename_field('docs/pattern-library/communication/grpc.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/communication/grpc.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/communication/grpc.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/communication/grpc.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/communication/grpc.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/communication/grpc.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/communication/service-discovery.md
    update_field('docs/pattern-library/communication/service-discovery.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/communication/service-discovery.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/communication/service-discovery.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/communication/service-discovery.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/communication/service-discovery.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/resilience/load-shedding.md
    update_field('docs/pattern-library/resilience/load-shedding.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/resilience/load-shedding.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/load-shedding.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/load-shedding.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/load-shedding.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/resilience/load-shedding.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/resilience/load-shedding.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/resilience/timeout.md
    rename_field('docs/pattern-library/resilience/timeout.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/timeout.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/timeout.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/timeout.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/resilience/timeout.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/resilience/timeout.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/resilience/fault-tolerance.md
    update_field('docs/pattern-library/resilience/fault-tolerance.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/resilience/fault-tolerance.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/fault-tolerance.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/fault-tolerance.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/fault-tolerance.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/resilience/retry-backoff.md
    rename_field('docs/pattern-library/resilience/retry-backoff.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/retry-backoff.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/retry-backoff.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/retry-backoff.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/resilience/retry-backoff.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/resilience/retry-backoff.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/resilience/retry-backoff.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/resilience/retry-backoff.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/resilience/heartbeat.md
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'best_for', 'best-for')
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/resilience/heartbeat.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/resilience/circuit-breaker.md
    rename_field('docs/pattern-library/resilience/circuit-breaker.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/circuit-breaker.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/circuit-breaker.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/circuit-breaker.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/resilience/circuit-breaker.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/resilience/circuit-breaker.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/resilience/circuit-breaker.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/resilience/circuit-breaker.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/resilience/split-brain.md
    update_field('docs/pattern-library/resilience/split-brain.md', 'pattern_status', 'recommended')
    rename_field('docs/pattern-library/resilience/split-brain.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/split-brain.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/resilience/split-brain.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/resilience/split-brain.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/split-brain.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/split-brain.md', 'last_updated', 'last-updated')
    # Fixes for docs/pattern-library/resilience/health-check.md
    rename_field('docs/pattern-library/resilience/health-check.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/health-check.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/health-check.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/health-check.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/resilience/health-check.md', 'modern_examples', 'modern-examples')
    # Fixes for docs/pattern-library/resilience/graceful-degradation.md
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'best_for', 'best-for')
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'modern_examples', 'modern-examples')
    rename_field('docs/pattern-library/resilience/graceful-degradation.md', 'production_checklist', 'production-checklist')
    # Fixes for docs/pattern-library/resilience/bulkhead.md
    rename_field('docs/pattern-library/resilience/bulkhead.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/bulkhead.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/bulkhead.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/bulkhead.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/resilience/bulkhead.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/resilience/bulkhead.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/resilience/bulkhead.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/resilience/bulkhead.md', 'best_for', 'best-for')
    # Fixes for docs/pattern-library/resilience/failover.md
    update_field('docs/pattern-library/resilience/failover.md', 'pattern_status', 'use-with-expertise')
    rename_field('docs/pattern-library/resilience/failover.md', 'reading_time', 'reading-time')
    rename_field('docs/pattern-library/resilience/failover.md', 'when_to_use', 'when-to-use')
    rename_field('docs/pattern-library/resilience/failover.md', 'when_not_to_use', 'when-not-to-use')
    rename_field('docs/pattern-library/resilience/failover.md', 'related_laws', 'related-laws')
    rename_field('docs/pattern-library/resilience/failover.md', 'related_pillars', 'related-pillars')
    rename_field('docs/pattern-library/resilience/failover.md', 'last_updated', 'last-updated')
    rename_field('docs/pattern-library/resilience/failover.md', 'trade_offs', 'trade-offs')
    rename_field('docs/pattern-library/resilience/failover.md', 'best_for', 'best-for')
    rename_field('docs/pattern-library/resilience/failover.md', 'modern_alternatives', 'modern-alternatives')
    
    print("Pattern metadata fixes completed!")
