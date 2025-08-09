"""
MkDocs Macros Module for DStudio Documentation

This module provides custom macros and variables for the MkDocs macros plugin.
"""

import datetime
from pathlib import Path



def get_law_slug(number, name):
    """Get the correct slug for a law."""
    law_slugs = {
        1: "correlated-failure",
        2: "asynchronous-reality",
        3: "emergent-chaos",
        4: "multidimensional-optimization",
        5: "distributed-knowledge",
        6: "cognitive-load",
        7: "economic-reality"
    }
    return law_slugs.get(number, name.lower().replace(" ", "-"))


def define_env(env):
    """
    This is the hook for defining variables, macros and filters

    - variables: the dictionary that contains the variables
    - macro: a decorator function, to declare a macro.
    - filter: a decorator function, to declare a filter.
    """

    # Add variables
    env.variables["current_year"] = datetime.datetime.now().year
    env.variables["project_name"] = "Distributed Systems Studio"
    env.variables["github_repo"] = "https://github.com/deepaucksharma/DStudio"

    # Build a lookup of pattern slugs to their category paths
    pattern_dir = Path(__file__).parent / "pattern-library"
    pattern_lookup = {}
    for md_file in pattern_dir.glob("**/*.md"):
        if md_file.name == "index.md":
            continue
        rel_parts = md_file.relative_to(pattern_dir).parts
        slug = md_file.stem
        category_path = "/".join(rel_parts[:-1])
        pattern_lookup[slug] = category_path if category_path else None

    # Add macros
    @env.macro
    def law_ref(number, name):
        """Create a reference to a law"""
        return f'[Law {number}: {name}](../core-principles/laws/{get_law_slug(number, name)}/)'

    @env.macro
    def pillar_ref(number, name):
        """Create a reference to a pillar"""
        return f'[Pillar {number}: {name}](../core-principles/pillars/{name.lower().replace(" ", "-")}/)'

    @env.macro
    def pattern_ref(name, category=None):
        """Create a reference to a pattern.

        If a category is provided, it will be used to build the path. If not,
        the function attempts to look up the category from the pattern library
        directory structure. When no category is found, the pattern is assumed
        to live at the root of the pattern library.
        """
        slug = name.lower().replace(" ", "-")
        cat = category.lower().replace(" ", "-") if category else pattern_lookup.get(slug)
        if cat:
            return f"[{name}](../pattern-library/{cat}/{slug}.md)"
        return f"[{name}](../pattern-library/{slug}.md)"

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
