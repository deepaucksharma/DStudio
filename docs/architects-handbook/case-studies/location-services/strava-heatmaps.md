---
title: Strava Heatmaps Case Study
description: "Analysis of Strava's global activity heatmap and privacy implications"
excellence_tier: bronze
architecture_status: use-with-caution
current_scale: global
key_patterns: ["gps-aggregation", "differential-privacy", "heatmap-generation"]
privacy_concerns: "Exposed sensitive military locations in 2018"
---

# Strava Heatmaps Case Study

> 🚧 This case study is planned for future development.

## Overview
This case study would examine Strava's architecture for aggregating billions of GPS activities into global heatmaps, including the privacy challenges that led to exposing sensitive military locations.

## Key Challenges
- Processing billions of GPS tracks efficiently
- Aggregating activities while preserving privacy
- Differential privacy for sensitive locations
- Real-time heatmap generation and updates
- Privacy zones and activity obfuscation
- Balancing data utility with user privacy

## Related Case Studies
- [Google Maps](google-maps.md.md) - Traffic data aggregation
- [Location Privacy](../pattern-library/location-privacy) - Privacy patterns
- ML Pipeline (Coming Soon.md) - Activity pattern analysis

## External Resources
- [Strava Metro](https://metro.strava.com/) - Anonymized activity data
- [Strava Privacy Controls](https://support.strava.com/hc/en-us/articles/115000173384)
- [Military Base Exposure Incident](https://www.bbc.com/news/technology-42853072)