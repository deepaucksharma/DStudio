# Design Bigtable

## Overview

This page is under construction. Bigtable is Google's distributed storage system for structured data that scales to petabytes of data across thousands of machines.

## Key Design Challenges

- **Scalability**: Petabyte-scale storage
- **Performance**: Low-latency reads and writes
- **Consistency**: Strong consistency within rows
- **Availability**: High availability with automatic failover
- **Data Model**: Sparse, distributed, multi-dimensional sorted map
- **Integration**: Foundation for many Google services

## Core Components

1. **Tablet Servers**: Store and serve data tablets
2. **Master Server**: Tablet assignment and load balancing
3. **Chubby**: Distributed lock service
4. **GFS/Colossus**: Underlying distributed file system
5. **SSTable**: Immutable sorted string table files

## Coming Soon

Detailed system design covering:
- Tablet splitting and merging
- Compaction strategies
- Row-level transactions
- Locality groups
- Bloom filters for optimization

[Return to Google Interview Guide](./index.md)