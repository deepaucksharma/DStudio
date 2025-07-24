# Design Spanner

## Overview

This page is under construction. Spanner is Google's globally distributed, strongly consistent database that provides ACID transactions across continents.

## Key Design Challenges

- **Global Consistency**: Linearizability across the globe
- **TrueTime**: Synchronized global timestamps
- **Multi-Version**: MVCC for lock-free reads
- **Transactions**: ACID across continents
- **SQL Support**: Full SQL with strong consistency
- **Auto-Sharding**: Transparent data distribution

## Core Components

1. **TrueTime API**: Global clock synchronization
2. **Paxos Groups**: Replicated state machines
3. **Transaction Manager**: 2PC with Paxos
4. **Directory Service**: Data placement and migration
5. **Timestamp Oracle**: Transaction ordering

## Coming Soon

Detailed system design covering:
- TrueTime implementation
- Externally consistent transactions
- Read-only transactions
- Schema changes without downtime
- Geographic data placement

[Return to Google Interview Guide](./index.md)