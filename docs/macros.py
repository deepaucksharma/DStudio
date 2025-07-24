"""
MkDocs Macros Module for DStudio Documentation

This module provides custom macros and variables for the MkDocs macros plugin.
"""

import datetime


def define_env(env):
    """
    This is the hook for defining variables, macros and filters
    
    - variables: the dictionary that contains the variables
    - macro: a decorator function, to declare a macro.
    - filter: a decorator function, to declare a filter.
    """
    
    # Add variables
    env.variables['current_year'] = datetime.datetime.now().year
    env.variables['project_name'] = 'The Compendium of Distributed Systems'
    env.variables['github_repo'] = 'https://github.com/deepaucksharma/DStudio'
    
    # Add macros
    @env.macro
    def law_ref(number, name):
        """Create a reference to a law"""
        return f'[Law {number}: {name}](../part1-axioms/axiom{number}-{name.lower().replace(" ", "-")}/)'
    
    @env.macro
    def pillar_ref(number, name):
        """Create a reference to a pillar"""
        return f'[Pillar {number}: {name}](../part2-pillars/{name.lower()}/)'
    
    @env.macro
    def pattern_ref(name):
        """Create a reference to a pattern"""
        slug = name.lower().replace(' ', '-')
        return f'[{name}](../patterns/{slug}.md)'
    
    @env.macro
    def case_study_ref(name):
        """Create a reference to a case study"""
        slug = name.lower().replace(' ', '-')
        return f'[{name}](../case-studies/{slug}.md)'
    
    @env.macro
    def latency_calc(distance_km, speed_fraction=0.67):
        """Calculate network latency based on distance and speed of light"""
        speed_of_light_km_ms = 300  # km/ms in vacuum
        effective_speed = speed_of_light_km_ms * speed_fraction
        return round(distance_km / effective_speed, 2)
    
    @env.macro
    def availability_nines(nines):
        """Convert availability nines to downtime per year"""
        availability = float('0.' + '9' * nines)
        downtime_minutes = (1 - availability) * 365 * 24 * 60
        
        if downtime_minutes < 60:
            return f"{downtime_minutes:.1f} minutes/year"
        elif downtime_minutes < 1440:  # Less than a day
            hours = downtime_minutes / 60
            return f"{hours:.1f} hours/year"
        else:
            days = downtime_minutes / 1440
            return f"{days:.1f} days/year"
    
    # Add filters
    @env.filter
    def format_bytes(bytes_value):
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"