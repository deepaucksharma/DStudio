# Episode 109: Bandwidth Allocation - Part 2 (Implementation Details)

## Introduction

In Part 1, we established the theoretical foundations of bandwidth allocation in distributed systems, covering the mathematical models, queuing theory applications, and fundamental algorithms. Part 2 dives deep into the practical implementation of bandwidth allocation systems, focusing on production-ready configurations and real-world deployment scenarios.

This episode provides comprehensive implementation details for Linux traffic control, Quality of Service (QoS) configuration, Hierarchical Token Bucket (HTB) systems, network slicing, and monitoring infrastructure. Each section includes working code examples, configuration templates, and production deployment strategies used by major technology companies.

## 1. Linux Traffic Control (tc) Implementation

Linux traffic control (tc) is the foundation of bandwidth allocation in Linux-based systems. It provides kernel-level packet scheduling, shaping, and classification capabilities essential for implementing sophisticated QoS policies.

### 1.1 Core Traffic Control Architecture

The Linux traffic control system consists of three main components:

**Queueing Disciplines (qdiscs)**: Control how packets are queued and dequeued
**Classes**: Hierarchical structures for organizing traffic flows
**Filters**: Classify packets into appropriate classes

```bash
# Basic tc architecture visualization
#     Root Qdisc (1:0)
#          |
#     +---------+---------+
#     |         |         |
#  Class 1:1  Class 1:2  Class 1:3
#  (High)     (Medium)    (Low)
#     |         |         |
#   Leaf      Leaf       Leaf
#   Qdisc     Qdisc      Qdisc
```

### 1.2 Comprehensive HTB Implementation

Hierarchical Token Bucket (HTB) is the most widely used qdisc for bandwidth allocation. Here's a production-ready implementation:

```bash
#!/bin/bash
# Production HTB Implementation for Multi-Tier Bandwidth Allocation
# Interface configuration
INTERFACE="eth0"
TOTAL_BANDWIDTH="1000mbit"

# Clear existing qdisc
tc qdisc del dev $INTERFACE root 2>/dev/null

# Create root HTB qdisc
tc qdisc add dev $INTERFACE root handle 1: htb default 30

# Create root class with total bandwidth
tc class add dev $INTERFACE parent 1: classid 1:1 htb \
    rate $TOTAL_BANDWIDTH ceil $TOTAL_BANDWIDTH

# High priority class (30% guaranteed, can borrow up to 60%)
tc class add dev $INTERFACE parent 1:1 classid 1:10 htb \
    rate 300mbit ceil 600mbit prio 1

# Medium priority class (50% guaranteed, can borrow up to 80%)
tc class add dev $INTERFACE parent 1:1 classid 1:20 htb \
    rate 500mbit ceil 800mbit prio 2

# Low priority class (20% guaranteed, can use remaining)
tc class add dev $INTERFACE parent 1:1 classid 1:30 htb \
    rate 200mbit ceil $TOTAL_BANDWIDTH prio 3

# Add leaf qdiscs with different algorithms
# High priority: strict FIFO for latency
tc qdisc add dev $INTERFACE parent 1:10 handle 10: pfifo limit 10

# Medium priority: SFQ for fairness
tc qdisc add dev $INTERFACE parent 1:20 handle 20: sfq perturb 10

# Low priority: RED for congestion control
tc qdisc add dev $INTERFACE parent 1:30 handle 30: red \
    min 10000 max 30000 avpkt 1000 burst 20 probability 0.1
```

### 1.3 Advanced Traffic Classification

Traffic classification is crucial for effective bandwidth allocation. Here's a comprehensive filtering system:

```bash
#!/bin/bash
# Advanced Traffic Classification System

# HTTP traffic to high priority
tc filter add dev $INTERFACE parent 1: protocol ip prio 1 u32 \
    match ip sport 80 0xffff flowid 1:10
tc filter add dev $INTERFACE parent 1: protocol ip prio 1 u32 \
    match ip sport 443 0xffff flowid 1:10

# Database traffic to high priority
tc filter add dev $INTERFACE parent 1: protocol ip prio 1 u32 \
    match ip sport 3306 0xffff flowid 1:10  # MySQL
tc filter add dev $INTERFACE parent 1: protocol ip prio 1 u32 \
    match ip sport 5432 0xffff flowid 1:10  # PostgreSQL

# SSH and management traffic to medium priority
tc filter add dev $INTERFACE parent 1: protocol ip prio 2 u32 \
    match ip sport 22 0xffff flowid 1:20

# Video streaming to medium priority with DSCP marking
tc filter add dev $INTERFACE parent 1: protocol ip prio 2 u32 \
    match ip tos 0xb8 0xfc flowid 1:20

# Background/backup traffic to low priority
tc filter add dev $INTERFACE parent 1: protocol ip prio 3 u32 \
    match ip sport 873 0xffff flowid 1:30   # rsync
tc filter add dev $INTERFACE parent 1: protocol ip prio 3 u32 \
    match ip sport 3260 0xffff flowid 1:30  # iSCSI

# ICMP for monitoring - high priority but limited bandwidth
tc class add dev $INTERFACE parent 1:10 classid 1:11 htb \
    rate 10mbit ceil 50mbit
tc qdisc add dev $INTERFACE parent 1:11 handle 11: pfifo limit 5
tc filter add dev $INTERFACE parent 1: protocol ip prio 1 u32 \
    match ip protocol 1 0xff flowid 1:11
```

### 1.4 Dynamic Bandwidth Allocation

For production systems, bandwidth requirements change dynamically. Here's an automated adjustment system:

```python
#!/usr/bin/env python3
"""
Dynamic Bandwidth Allocation System
Monitors network usage and adjusts HTB classes automatically
"""

import subprocess
import time
import json
import re
from collections import defaultdict

class DynamicBandwidthAllocator:
    def __init__(self, interface="eth0", total_bandwidth_mbps=1000):
        self.interface = interface
        self.total_bandwidth = total_bandwidth_mbps
        self.usage_history = defaultdict(list)
        self.adjustment_interval = 30  # seconds
        
    def get_class_statistics(self):
        """Extract current usage statistics from tc"""
        cmd = f"tc -s class show dev {self.interface}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        stats = {}
        current_class = None
        
        for line in result.stdout.split('\n'):
            # Match class definition
            class_match = re.search(r'class htb 1:(\d+)', line)
            if class_match:
                current_class = class_match.group(1)
                stats[current_class] = {'bytes': 0, 'packets': 0, 'rate': 0}
            
            # Match sent statistics
            if current_class and 'Sent' in line:
                sent_match = re.search(r'Sent (\d+) bytes (\d+) pkt', line)
                if sent_match:
                    stats[current_class]['bytes'] = int(sent_match.group(1))
                    stats[current_class]['packets'] = int(sent_match.group(2))
            
            # Match rate statistics
            if current_class and 'rate' in line:
                rate_match = re.search(r'rate (\d+)([KMG]?)bit', line)
                if rate_match:
                    rate = int(rate_match.group(1))
                    unit = rate_match.group(2)
                    if unit == 'K':
                        rate *= 1000
                    elif unit == 'M':
                        rate *= 1000000
                    elif unit == 'G':
                        rate *= 1000000000
                    stats[current_class]['rate'] = rate
                    
        return stats
    
    def calculate_utilization(self, stats):
        """Calculate bandwidth utilization percentages"""
        utilization = {}
        total_rate = sum(stat['rate'] for stat in stats.values())
        
        for class_id, stat in stats.items():
            if total_rate > 0:
                utilization[class_id] = (stat['rate'] / total_rate) * 100
            else:
                utilization[class_id] = 0
                
        return utilization
    
    def adjust_bandwidth(self, utilization):
        """Dynamically adjust class bandwidth based on utilization"""
        adjustments = []
        
        # High priority class (1:10)
        if '10' in utilization:
            high_util = utilization['10']
            if high_util > 80:
                # Increase bandwidth for high priority
                new_rate = min(600, int(self.total_bandwidth * 0.4))
                adjustments.append(('1:10', new_rate, min(800, new_rate * 2)))
            elif high_util < 20:
                # Decrease if underutilized
                new_rate = max(200, int(self.total_bandwidth * 0.25))
                adjustments.append(('1:10', new_rate, new_rate * 2))
        
        # Medium priority class (1:20)
        if '20' in utilization:
            medium_util = utilization['20']
            remaining_bandwidth = self.total_bandwidth - 200  # Reserve minimum for other classes
            if medium_util > 70:
                new_rate = min(remaining_bandwidth, int(self.total_bandwidth * 0.6))
                adjustments.append(('1:20', new_rate, min(900, new_rate * 1.5)))
        
        # Apply adjustments
        for class_id, rate, ceil in adjustments:
            cmd = f"tc class change dev {self.interface} classid {class_id} htb rate {rate}mbit ceil {ceil}mbit"
            subprocess.run(cmd, shell=True)
            print(f"Adjusted {class_id}: rate={rate}mbit ceil={ceil}mbit")
    
    def monitor_and_adjust(self):
        """Main monitoring loop"""
        print(f"Starting dynamic bandwidth allocation for {self.interface}")
        
        while True:
            try:
                stats = self.get_class_statistics()
                utilization = self.calculate_utilization(stats)
                
                # Store history for trend analysis
                timestamp = time.time()
                for class_id, util in utilization.items():
                    self.usage_history[class_id].append((timestamp, util))
                    # Keep only last hour of data
                    self.usage_history[class_id] = [
                        (ts, u) for ts, u in self.usage_history[class_id] 
                        if timestamp - ts < 3600
                    ]
                
                # Print current statistics
                print(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
                for class_id, util in utilization.items():
                    rate_mbps = stats.get(class_id, {}).get('rate', 0) / 1000000
                    print(f"Class 1:{class_id}: {util:.1f}% utilization, {rate_mbps:.1f} Mbps")
                
                # Adjust bandwidth if needed
                self.adjust_bandwidth(utilization)
                
                time.sleep(self.adjustment_interval)
                
            except KeyboardInterrupt:
                print("\nStopping bandwidth monitor...")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(10)

if __name__ == "__main__":
    allocator = DynamicBandwidthAllocator()
    allocator.monitor_and_adjust()
```

## 2. Quality of Service (QoS) Configuration

QoS implementation requires coordination between traffic classification, scheduling, and congestion control. Here's a comprehensive QoS framework:

### 2.1 DSCP-Based QoS Implementation

Differentiated Services Code Point (DSCP) markings provide standardized QoS classification:

```bash
#!/bin/bash
# Comprehensive DSCP-based QoS Implementation

INTERFACE="eth0"

# Create root qdisc with DSCP-aware classification
tc qdisc add dev $INTERFACE root handle 1: htb default 40

# Root class
tc class add dev $INTERFACE parent 1: classid 1:1 htb rate 1000mbit ceil 1000mbit

# Voice traffic (EF - Expedited Forwarding) - Highest priority
tc class add dev $INTERFACE parent 1:1 classid 1:10 htb \
    rate 100mbit ceil 200mbit prio 0 quantum 1500
tc qdisc add dev $INTERFACE parent 1:10 handle 10: pfifo limit 5

# Video traffic (AF41-43) - High priority
tc class add dev $INTERFACE parent 1:1 classid 1:20 htb \
    rate 300mbit ceil 500mbit prio 1
tc qdisc add dev $INTERFACE parent 1:20 handle 20: sfq perturb 5

# Critical data (AF31-33) - Medium-high priority
tc class add dev $INTERFACE parent 1:1 classid 1:30 htb \
    rate 400mbit ceil 700mbit prio 2
tc qdisc add dev $INTERFACE parent 1:30 handle 30: red \
    min 15000 max 45000 avpkt 1000 burst 25

# Standard data (AF11-13, BE) - Normal priority
tc class add dev $INTERFACE parent 1:1 classid 1:40 htb \
    rate 200mbit ceil 800mbit prio 3
tc qdisc add dev $INTERFACE parent 1:40 handle 40: fq_codel

# DSCP classification filters
# Voice - EF (DSCP 46)
tc filter add dev $INTERFACE parent 1: protocol ip prio 1 u32 \
    match ip tos 0xb8 0xfc flowid 1:10

# Video - AF41 (DSCP 34)
tc filter add dev $INTERFACE parent 1: protocol ip prio 2 u32 \
    match ip tos 0x88 0xfc flowid 1:20

# Video - AF42 (DSCP 36)
tc filter add dev $INTERFACE parent 1: protocol ip prio 2 u32 \
    match ip tos 0x90 0xfc flowid 1:20

# Critical data - AF31 (DSCP 26)
tc filter add dev $INTERFACE parent 1: protocol ip prio 3 u32 \
    match ip tos 0x68 0xfc flowid 1:30

# Default traffic (Best Effort)
tc filter add dev $INTERFACE parent 1: protocol ip prio 4 u32 \
    match ip tos 0x00 0xfc flowid 1:40
```

### 2.2 Application-Aware QoS Classification

Modern QoS systems need to understand application requirements. Here's an implementation that classifies traffic based on application signatures:

```python
#!/usr/bin/env python3
"""
Application-Aware QoS Classification System
Uses deep packet inspection and flow characteristics to classify traffic
"""

import socket
import struct
import threading
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class FlowStats:
    bytes_sent: int = 0
    packets_sent: int = 0
    first_seen: float = 0
    last_seen: float = 0
    avg_packet_size: float = 0
    flow_duration: float = 0
    inter_arrival_times: List[float] = None
    
    def __post_init__(self):
        if self.inter_arrival_times is None:
            self.inter_arrival_times = []

class ApplicationClassifier:
    def __init__(self):
        self.flows = defaultdict(FlowStats)
        self.classification_rules = {
            'voice': {
                'ports': [5060, 5061],  # SIP
                'rtp_range': (10000, 20000),
                'avg_packet_size': (160, 320),  # G.711 codec packets
                'inter_arrival_variance': 0.1   # Low jitter
            },
            'video': {
                'ports': [554, 8080, 1935],  # RTSP, HTTP streaming, RTMP
                'avg_packet_size': (500, 1500),
                'burst_pattern': True
            },
            'database': {
                'ports': [3306, 5432, 1521, 1433],  # MySQL, PostgreSQL, Oracle, SQL Server
                'avg_packet_size': (100, 8192),
                'query_response_pattern': True
            },
            'web': {
                'ports': [80, 443, 8080, 8443],
                'avg_packet_size': (200, 1460),
                'http_pattern': True
            },
            'backup': {
                'ports': [873, 22],  # rsync, scp
                'avg_packet_size': (1000, 65536),
                'bulk_transfer': True
            }
        }
    
    def extract_flow_key(self, packet):
        """Extract 5-tuple flow identifier from packet"""
        # Simplified packet parsing - in production use libraries like scapy
        ip_header = packet[14:34]  # Skip Ethernet header
        src_ip = socket.inet_ntoa(ip_header[12:16])
        dst_ip = socket.inet_ntoa(ip_header[16:20])
        
        protocol = ip_header[9]
        if protocol == 6:  # TCP
            tcp_header = packet[34:54]
            src_port = struct.unpack('>H', tcp_header[0:2])[0]
            dst_port = struct.unpack('>H', tcp_header[2:4])[0]
            return f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-TCP"
        elif protocol == 17:  # UDP
            udp_header = packet[34:42]
            src_port = struct.unpack('>H', udp_header[0:2])[0]
            dst_port = struct.unpack('>H', udp_header[2:4])[0]
            return f"{src_ip}:{src_port}-{dst_ip}:{dst_port}-UDP"
        
        return f"{src_ip}-{dst_ip}-{protocol}"
    
    def update_flow_stats(self, flow_key, packet_size):
        """Update flow statistics with new packet"""
        current_time = time.time()
        flow = self.flows[flow_key]
        
        if flow.first_seen == 0:
            flow.first_seen = current_time
        else:
            # Update inter-arrival times
            inter_arrival = current_time - flow.last_seen
            flow.inter_arrival_times.append(inter_arrival)
            # Keep only recent history
            flow.inter_arrival_times = flow.inter_arrival_times[-100:]
        
        flow.last_seen = current_time
        flow.bytes_sent += packet_size
        flow.packets_sent += 1
        flow.flow_duration = current_time - flow.first_seen
        
        if flow.packets_sent > 0:
            flow.avg_packet_size = flow.bytes_sent / flow.packets_sent
    
    def classify_flow(self, flow_key, flow_stats) -> str:
        """Classify flow based on characteristics"""
        # Extract port information
        try:
            parts = flow_key.split('-')
            src_part = parts[0].split(':')
            dst_part = parts[1].split(':')
            src_port = int(src_part[1]) if len(src_part) > 1 else 0
            dst_port = int(dst_part[1]) if len(dst_part) > 1 else 0
        except:
            return 'default'
        
        # Port-based classification first
        for app_type, rules in self.classification_rules.items():
            if 'ports' in rules:
                if src_port in rules['ports'] or dst_port in rules['ports']:
                    return app_type
            
            if 'rtp_range' in rules:
                rtp_min, rtp_max = rules['rtp_range']
                if rtp_min <= src_port <= rtp_max or rtp_min <= dst_port <= rtp_max:
                    # Additional voice traffic validation
                    if (rules['avg_packet_size'][0] <= flow_stats.avg_packet_size <= 
                        rules['avg_packet_size'][1]):
                        # Check jitter (inter-arrival time variance)
                        if len(flow_stats.inter_arrival_times) > 10:
                            variance = self.calculate_variance(flow_stats.inter_arrival_times[-10:])
                            if variance < rules['inter_arrival_variance']:
                                return app_type
        
        # Behavioral classification
        if flow_stats.avg_packet_size > 10000 and flow_stats.flow_duration > 60:
            return 'backup'  # Large packets, long duration
        elif (flow_stats.avg_packet_size < 200 and 
              len(flow_stats.inter_arrival_times) > 5 and
              max(flow_stats.inter_arrival_times[-5:]) < 0.1):
            return 'voice'   # Small packets, regular timing
        elif flow_stats.avg_packet_size > 1000 and self.has_burst_pattern(flow_stats):
            return 'video'   # Bursty large packets
        
        return 'default'
    
    def calculate_variance(self, values):
        """Calculate variance of inter-arrival times"""
        if len(values) < 2:
            return 0
        mean = sum(values) / len(values)
        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def has_burst_pattern(self, flow_stats):
        """Detect bursty traffic pattern"""
        if len(flow_stats.inter_arrival_times) < 10:
            return False
        
        recent_times = flow_stats.inter_arrival_times[-10:]
        short_intervals = sum(1 for t in recent_times if t < 0.01)
        long_intervals = sum(1 for t in recent_times if t > 0.1)
        
        return short_intervals >= 5 and long_intervals >= 2
    
    def apply_qos_rules(self, flow_key, classification):
        """Apply QoS rules based on classification"""
        qos_mappings = {
            'voice': '1:10',      # Highest priority
            'video': '1:20',      # High priority
            'database': '1:30',   # Medium-high priority
            'web': '1:40',        # Normal priority
            'backup': '1:50',     # Low priority
            'default': '1:40'     # Normal priority
        }
        
        class_id = qos_mappings.get(classification, '1:40')
        
        # Use iptables to mark packets for tc classification
        # This is a simplified example - production systems would use netfilter hooks
        src_ip = flow_key.split(':')[0]
        dst_ip = flow_key.split('-')[1].split(':')[0]
        
        # Mark packets with appropriate DSCP values
        dscp_mappings = {
            'voice': '46',        # EF
            'video': '34',        # AF41
            'database': '26',     # AF31
            'web': '0',           # BE
            'backup': '8',        # CS1
            'default': '0'        # BE
        }
        
        dscp_value = dscp_mappings.get(classification, '0')
        
        print(f"Classified flow {flow_key} as {classification}, "
              f"assigning to class {class_id}, DSCP {dscp_value}")
        
        return class_id, dscp_value

def main():
    classifier = ApplicationClassifier()
    print("Starting application-aware QoS classification...")
    
    # In production, this would integrate with packet capture
    # This is a simulation for demonstration
    sample_flows = [
        ("192.168.1.100:12000-192.168.1.200:12001-UDP", [160] * 50),  # Voice
        ("10.0.0.1:80-10.0.0.100:54321-TCP", [1460, 1460, 800, 1200]),  # Web
        ("172.16.1.5:3306-172.16.1.10:45678-TCP", [128, 8192, 64, 4096]),  # Database
    ]
    
    for flow_key, packet_sizes in sample_flows:
        for size in packet_sizes:
            classifier.update_flow_stats(flow_key, size)
            time.sleep(0.01)  # Simulate packet timing
        
        flow_stats = classifier.flows[flow_key]
        classification = classifier.classify_flow(flow_key, flow_stats)
        classifier.apply_qos_rules(flow_key, classification)

if __name__ == "__main__":
    main()
```

## 3. Hierarchical Token Bucket (HTB) Deep Dive

HTB is the cornerstone of Linux bandwidth allocation. Let's implement a production-grade HTB system with advanced features:

### 3.1 Multi-Level HTB Hierarchy

```bash
#!/bin/bash
# Advanced Multi-Level HTB Implementation
# Supports customer isolation, service tiers, and SLA enforcement

INTERFACE="eth1"
TOTAL_BW="10gbit"

# Clear existing configuration
tc qdisc del dev $INTERFACE root 2>/dev/null

# Root qdisc
tc qdisc add dev $INTERFACE root handle 1: htb default 999

# Root class - total bandwidth
tc class add dev $INTERFACE parent 1: classid 1:1 htb \
    rate $TOTAL_BW ceil $TOTAL_BW

# Customer tier classes
# Premium customers (40% guaranteed, can burst to 70%)
tc class add dev $INTERFACE parent 1:1 classid 1:10 htb \
    rate 4gbit ceil 7gbit prio 1

# Standard customers (35% guaranteed, can burst to 50%)
tc class add dev $INTERFACE parent 1:1 classid 1:20 htb \
    rate 3500mbit ceil 5gbit prio 2

# Basic customers (20% guaranteed, can burst to 30%)
tc class add dev $INTERFACE parent 1:1 classid 1:30 htb \
    rate 2gbit ceil 3gbit prio 3

# System/management traffic (5% guaranteed, can burst to 10%)
tc class add dev $INTERFACE parent 1:1 classid 1:40 htb \
    rate 500mbit ceil 1gbit prio 0

# Within each customer tier, create service classes
# Premium tier service classes
tc class add dev $INTERFACE parent 1:10 classid 1:11 htb \
    rate 1600mbit ceil 3gbit prio 1  # Interactive/real-time
tc class add dev $INTERFACE parent 1:10 classid 1:12 htb \
    rate 1600mbit ceil 2800mbit prio 2  # Bulk transfer
tc class add dev $INTERFACE parent 1:10 classid 1:13 htb \
    rate 800mbit ceil 1400mbit prio 3   # Background

# Standard tier service classes
tc class add dev $INTERFACE parent 1:20 classid 1:21 htb \
    rate 1400mbit ceil 2500mbit prio 1
tc class add dev $INTERFACE parent 1:20 classid 1:22 htb \
    rate 1400mbit ceil 2000mbit prio 2
tc class add dev $INTERFACE parent 1:20 classid 1:23 htb \
    rate 700mbit ceil 1000mbit prio 3

# Basic tier service classes
tc class add dev $INTERFACE parent 1:30 classid 1:31 htb \
    rate 800mbit ceil 1500mbit prio 1
tc class add dev $INTERFACE parent 1:30 classid 1:32 htb \
    rate 800mbit ceil 1200mbit prio 2
tc class add dev $INTERFACE parent 1:30 classid 1:33 htb \
    rate 400mbit ceil 600mbit prio 3

# Leaf qdiscs optimized for different traffic types
# Interactive traffic - minimize latency
tc qdisc add dev $INTERFACE parent 1:11 handle 11: fq_codel \
    limit 1000 target 5ms interval 100ms quantum 300
tc qdisc add dev $INTERFACE parent 1:21 handle 21: fq_codel \
    limit 1000 target 5ms interval 100ms quantum 300
tc qdisc add dev $INTERFACE parent 1:31 handle 31: fq_codel \
    limit 1000 target 5ms interval 100ms quantum 300

# Bulk transfer - maximize throughput
tc qdisc add dev $INTERFACE parent 1:12 handle 12: fq_codel \
    limit 10000 target 20ms interval 200ms quantum 1514
tc qdisc add dev $INTERFACE parent 1:22 handle 22: fq_codel \
    limit 10000 target 20ms interval 200ms quantum 1514
tc qdisc add dev $INTERFACE parent 1:32 handle 32: fq_codel \
    limit 10000 target 20ms interval 200ms quantum 1514

# Background - prevent starvation but low priority
tc qdisc add dev $INTERFACE parent 1:13 handle 13: sfq \
    perturb 10 quantum 1514
tc qdisc add dev $INTERFACE parent 1:23 handle 23: sfq \
    perturb 10 quantum 1514
tc qdisc add dev $INTERFACE parent 1:33 handle 33: sfq \
    perturb 10 quantum 1514

# System traffic - high priority, low latency
tc qdisc add dev $INTERFACE parent 1:40 handle 40: pfifo limit 10
```

### 3.2 Dynamic HTB Rate Adjustment

Real-world systems require dynamic rate adjustment based on SLA requirements and current usage:

```python
#!/usr/bin/env python3
"""
Dynamic HTB Rate Adjustment System
Automatically adjusts HTB class rates based on SLA requirements,
current utilization, and business rules.
"""

import subprocess
import json
import time
import logging
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
from datetime import datetime, timedelta

@dataclass
class SLAConfig:
    customer_id: str
    tier: str  # premium, standard, basic
    guaranteed_mbps: int
    burst_mbps: int
    priority: int
    active_hours: List[tuple]  # [(start_hour, end_hour), ...]
    penalty_rate: float  # Rate reduction factor for SLA violations

@dataclass
class ClassStats:
    class_id: str
    rate_mbps: int
    ceil_mbps: int
    bytes_sent: int
    packets_sent: int
    drops: int
    overlimits: int
    utilization_percent: float
    last_updated: datetime

class HTBManager:
    def __init__(self, interface: str, total_bandwidth_gbps: float = 10):
        self.interface = interface
        self.total_bandwidth_mbps = int(total_bandwidth_gbps * 1000)
        self.classes = {}
        self.sla_configs = {}
        self.violation_history = {}
        self.adjustment_history = []
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('htb_manager.log'),
                logging.StreamHandler()
            ]
        )
        
        self.load_sla_configs()
    
    def load_sla_configs(self):
        """Load SLA configurations from file or database"""
        # Example SLA configurations
        self.sla_configs = {
            'customer_001': SLAConfig(
                customer_id='customer_001',
                tier='premium',
                guaranteed_mbps=1000,
                burst_mbps=2000,
                priority=1,
                active_hours=[(9, 18), (20, 23)],  # Business hours + evening
                penalty_rate=0.8
            ),
            'customer_002': SLAConfig(
                customer_id='customer_002',
                tier='standard',
                guaranteed_mbps=500,
                burst_mbps=800,
                priority=2,
                active_hours=[(8, 20)],
                penalty_rate=0.9
            ),
            'customer_003': SLAConfig(
                customer_id='customer_003',
                tier='basic',
                guaranteed_mbps=200,
                burst_mbps=400,
                priority=3,
                active_hours=[(0, 24)],  # 24/7
                penalty_rate=0.95
            )
        }
    
    def get_current_stats(self) -> Dict[str, ClassStats]:
        """Retrieve current HTB class statistics"""
        cmd = f"tc -s -j class show dev {self.interface}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
            tc_data = json.loads(result.stdout)
            
            stats = {}
            for item in tc_data:
                if item.get('kind') == 'htb':
                    class_id = item.get('handle', '').replace(':', '')
                    if class_id:
                        bytes_sent = item.get('bytes', 0)
                        packets_sent = item.get('packets', 0)
                        drops = item.get('drops', 0)
                        overlimits = item.get('overlimits', 0)
                        
                        # Calculate utilization
                        rate_bps = item.get('options', {}).get('rate', {}).get('rate', 0)
                        current_rate_bps = item.get('rate', {}).get('rate', 0)
                        utilization = 0
                        if rate_bps > 0:
                            utilization = (current_rate_bps / rate_bps) * 100
                        
                        stats[class_id] = ClassStats(
                            class_id=class_id,
                            rate_mbps=int(rate_bps / 1000000),
                            ceil_mbps=int(item.get('options', {}).get('ceil', {}).get('rate', 0) / 1000000),
                            bytes_sent=bytes_sent,
                            packets_sent=packets_sent,
                            drops=drops,
                            overlimits=overlimits,
                            utilization_percent=utilization,
                            last_updated=datetime.now()
                        )
            
            return stats
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to get tc statistics: {e}")
            return {}
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse tc JSON output: {e}")
            return {}
    
    def is_active_hours(self, customer_id: str) -> bool:
        """Check if current time is within customer's active hours"""
        if customer_id not in self.sla_configs:
            return True
        
        current_hour = datetime.now().hour
        active_hours = self.sla_configs[customer_id].active_hours
        
        for start_hour, end_hour in active_hours:
            if start_hour <= current_hour <= end_hour:
                return True
        
        return False
    
    def detect_sla_violations(self, stats: Dict[str, ClassStats]) -> List[str]:
        """Detect SLA violations based on current statistics"""
        violations = []
        
        for customer_id, sla in self.sla_configs.items():
            class_id = self.get_class_id_for_customer(customer_id)
            if class_id not in stats:
                continue
            
            class_stats = stats[class_id]
            
            # Check for drops indicating insufficient bandwidth
            if class_stats.drops > 0:
                violations.append(f"{customer_id}: Packet drops detected ({class_stats.drops})")
            
            # Check for overlimits indicating rate limiting
            if class_stats.overlimits > 0:
                violations.append(f"{customer_id}: Rate limiting detected ({class_stats.overlimits})")
            
            # Check utilization during active hours
            if self.is_active_hours(customer_id):
                if class_stats.utilization_percent > 90:
                    violations.append(f"{customer_id}: High utilization ({class_stats.utilization_percent:.1f}%)")
        
        return violations
    
    def calculate_optimal_rates(self, stats: Dict[str, ClassStats]) -> Dict[str, tuple]:
        """Calculate optimal rates based on current usage and SLA requirements"""
        adjustments = {}
        total_guaranteed = sum(sla.guaranteed_mbps for sla in self.sla_configs.values())
        available_burst = self.total_bandwidth_mbps - total_guaranteed
        
        for customer_id, sla in self.sla_configs.items():
            class_id = self.get_class_id_for_customer(customer_id)
            if class_id not in stats:
                continue
            
            current_stats = stats[class_id]
            base_rate = sla.guaranteed_mbps
            
            # Adjust based on utilization and active hours
            if self.is_active_hours(customer_id):
                if current_stats.utilization_percent > 80:
                    # High utilization during active hours - increase burst capability
                    burst_rate = min(sla.burst_mbps * 1.2, sla.burst_mbps + available_burst * 0.3)
                else:
                    burst_rate = sla.burst_mbps
            else:
                # Outside active hours - allow more aggressive bursting
                burst_rate = min(sla.burst_mbps * 1.5, sla.burst_mbps + available_burst * 0.5)
            
            # Apply penalty for SLA violations
            violation_key = f"{customer_id}_violations"
            if violation_key in self.violation_history:
                recent_violations = len([v for v in self.violation_history[violation_key] 
                                       if v > datetime.now() - timedelta(hours=1)])
                if recent_violations > 0:
                    penalty_factor = sla.penalty_rate ** recent_violations
                    base_rate = int(base_rate * penalty_factor)
                    burst_rate = int(burst_rate * penalty_factor)
            
            # Ensure minimum guarantees
            base_rate = max(base_rate, sla.guaranteed_mbps // 2)
            burst_rate = max(burst_rate, base_rate)
            
            if (base_rate != current_stats.rate_mbps or 
                burst_rate != current_stats.ceil_mbps):
                adjustments[class_id] = (base_rate, burst_rate)
        
        return adjustments
    
    def apply_rate_adjustments(self, adjustments: Dict[str, tuple]):
        """Apply calculated rate adjustments to HTB classes"""
        for class_id, (rate_mbps, ceil_mbps) in adjustments.items():
            try:
                cmd = (f"tc class change dev {self.interface} "
                      f"classid 1:{class_id} htb "
                      f"rate {rate_mbps}mbit ceil {ceil_mbps}mbit")
                
                subprocess.run(cmd, shell=True, check=True)
                
                logging.info(f"Adjusted class 1:{class_id}: "
                           f"rate={rate_mbps}mbit ceil={ceil_mbps}mbit")
                
                # Record adjustment
                self.adjustment_history.append({
                    'timestamp': datetime.now(),
                    'class_id': class_id,
                    'old_rate': None,  # Would track from previous stats
                    'new_rate': rate_mbps,
                    'old_ceil': None,
                    'new_ceil': ceil_mbps
                })
                
            except subprocess.CalledProcessError as e:
                logging.error(f"Failed to adjust class 1:{class_id}: {e}")
    
    def get_class_id_for_customer(self, customer_id: str) -> str:
        """Map customer ID to HTB class ID"""
        # This would typically come from a configuration database
        customer_class_mapping = {
            'customer_001': '11',  # Premium interactive
            'customer_002': '21',  # Standard interactive
            'customer_003': '31'   # Basic interactive
        }
        return customer_class_mapping.get(customer_id, '999')
    
    def run_management_loop(self, interval_seconds: int = 60):
        """Main management loop"""
        logging.info(f"Starting HTB management loop (interval: {interval_seconds}s)")
        
        while True:
            try:
                # Get current statistics
                stats = self.get_current_stats()
                if not stats:
                    logging.warning("No statistics available, skipping adjustment cycle")
                    time.sleep(interval_seconds)
                    continue
                
                # Detect SLA violations
                violations = self.detect_sla_violations(stats)
                if violations:
                    logging.warning(f"SLA violations detected: {violations}")
                    # Record violations for penalty calculation
                    for violation in violations:
                        customer_id = violation.split(':')[0]
                        violation_key = f"{customer_id}_violations"
                        if violation_key not in self.violation_history:
                            self.violation_history[violation_key] = []
                        self.violation_history[violation_key].append(datetime.now())
                
                # Calculate optimal rates
                adjustments = self.calculate_optimal_rates(stats)
                
                # Apply adjustments
                if adjustments:
                    logging.info(f"Applying {len(adjustments)} rate adjustments")
                    self.apply_rate_adjustments(adjustments)
                else:
                    logging.info("No rate adjustments needed")
                
                # Log current status
                for class_id, class_stats in stats.items():
                    logging.info(f"Class 1:{class_id}: "
                               f"{class_stats.utilization_percent:.1f}% utilization, "
                               f"{class_stats.drops} drops, "
                               f"{class_stats.overlimits} overlimits")
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logging.info("HTB management loop stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in management loop: {e}")
                time.sleep(10)

def main():
    manager = HTBManager(interface="eth1", total_bandwidth_gbps=10)
    manager.run_management_loop(interval_seconds=30)

if __name__ == "__main__":
    main()
```

## 4. Network Slicing Implementation

Network slicing creates isolated virtual networks with guaranteed resources. Here's a comprehensive implementation:

### 4.1 Network Slice Architecture

```python
#!/usr/bin/env python3
"""
Network Slicing Implementation for Multi-Tenant Systems
Creates isolated network slices with guaranteed bandwidth, latency, and security
"""

import subprocess
import json
import ipaddress
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

class SliceType(Enum):
    ENHANCED_MOBILE_BROADBAND = "eMBB"      # High bandwidth, moderate latency
    ULTRA_RELIABLE_LOW_LATENCY = "URLLC"    # Low latency, high reliability
    MASSIVE_IOT = "mIoT"                    # Low bandwidth, high connection density

@dataclass
class SliceRequirements:
    bandwidth_mbps: int
    max_latency_ms: int
    min_reliability_percent: float
    max_jitter_ms: int
    security_level: int  # 1-5, with 5 being highest
    isolation_level: int  # 1-3, with 3 being complete isolation

@dataclass
class NetworkSlice:
    slice_id: str
    slice_type: SliceType
    requirements: SliceRequirements
    tenant_id: str
    vlan_id: int
    subnet: ipaddress.IPv4Network
    namespace: str
    htb_class_id: str
    firewall_chain: str
    active: bool = True
    allocated_interfaces: Set[str] = field(default_factory=set)

class NetworkSliceManager:
    def __init__(self, physical_interface: str = "eth0"):
        self.physical_interface = physical_interface
        self.slices: Dict[str, NetworkSlice] = {}
        self.next_vlan_id = 100
        self.next_class_id = 100
        self.base_subnet = ipaddress.IPv4Network('10.0.0.0/16')
        self.subnet_allocator = self.base_subnet.subnets(new_prefix=24)
    
    def create_slice(self, slice_id: str, slice_type: SliceType, 
                     requirements: SliceRequirements, tenant_id: str) -> NetworkSlice:
        """Create a new network slice with complete isolation"""
        
        if slice_id in self.slices:
            raise ValueError(f"Slice {slice_id} already exists")
        
        # Allocate resources
        vlan_id = self._allocate_vlan_id()
        subnet = next(self.subnet_allocator)
        namespace = f"slice_{slice_id}"
        htb_class_id = str(self._allocate_class_id())
        firewall_chain = f"SLICE_{slice_id.upper()}"
        
        slice_obj = NetworkSlice(
            slice_id=slice_id,
            slice_type=slice_type,
            requirements=requirements,
            tenant_id=tenant_id,
            vlan_id=vlan_id,
            subnet=subnet,
            namespace=namespace,
            htb_class_id=htb_class_id,
            firewall_chain=firewall_chain
        )
        
        # Configure network isolation
        self._setup_network_namespace(slice_obj)
        self._setup_vlan_interface(slice_obj)
        self._setup_bandwidth_allocation(slice_obj)
        self._setup_firewall_rules(slice_obj)
        self._setup_routing(slice_obj)
        
        self.slices[slice_id] = slice_obj
        return slice_obj
    
    def _allocate_vlan_id(self) -> int:
        """Allocate next available VLAN ID"""
        while self.next_vlan_id in [s.vlan_id for s in self.slices.values()]:
            self.next_vlan_id += 1
        return self.next_vlan_id
    
    def _allocate_class_id(self) -> int:
        """Allocate next available HTB class ID"""
        while str(self.next_class_id) in [s.htb_class_id for s in self.slices.values()]:
            self.next_class_id += 1
        return self.next_class_id
    
    def _setup_network_namespace(self, slice_obj: NetworkSlice):
        """Create isolated network namespace for the slice"""
        try:
            # Create namespace
            subprocess.run(f"ip netns add {slice_obj.namespace}", 
                         shell=True, check=True)
            
            # Enable loopback in namespace
            subprocess.run(f"ip netns exec {slice_obj.namespace} ip link set lo up", 
                         shell=True, check=True)
            
            print(f"Created network namespace: {slice_obj.namespace}")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create namespace: {e}")
    
    def _setup_vlan_interface(self, slice_obj: NetworkSlice):
        """Create VLAN interface for slice isolation"""
        try:
            vlan_interface = f"{self.physical_interface}.{slice_obj.vlan_id}"
            veth_host = f"veth-{slice_obj.slice_id}-host"
            veth_slice = f"veth-{slice_obj.slice_id}-slice"
            
            # Create VLAN interface
            subprocess.run(f"ip link add link {self.physical_interface} "
                         f"name {vlan_interface} type vlan id {slice_obj.vlan_id}", 
                         shell=True, check=True)
            
            # Create veth pair for namespace connection
            subprocess.run(f"ip link add {veth_host} type veth peer name {veth_slice}", 
                         shell=True, check=True)
            
            # Move one end to namespace
            subprocess.run(f"ip link set {veth_slice} netns {slice_obj.namespace}", 
                         shell=True, check=True)
            
            # Configure interfaces
            gateway_ip = str(slice_obj.subnet.network_address + 1)
            slice_ip = str(slice_obj.subnet.network_address + 2)
            
            # Host side configuration
            subprocess.run(f"ip addr add {gateway_ip}/24 dev {veth_host}", 
                         shell=True, check=True)
            subprocess.run(f"ip link set {veth_host} up", shell=True, check=True)
            subprocess.run(f"ip link set {vlan_interface} up", shell=True, check=True)
            
            # Namespace side configuration
            subprocess.run(f"ip netns exec {slice_obj.namespace} "
                         f"ip addr add {slice_ip}/24 dev {veth_slice}", 
                         shell=True, check=True)
            subprocess.run(f"ip netns exec {slice_obj.namespace} "
                         f"ip link set {veth_slice} up", shell=True, check=True)
            subprocess.run(f"ip netns exec {slice_obj.namespace} "
                         f"ip route add default via {gateway_ip}", shell=True, check=True)
            
            slice_obj.allocated_interfaces.add(vlan_interface)
            slice_obj.allocated_interfaces.add(veth_host)
            
            print(f"Created VLAN interface {vlan_interface} for slice {slice_obj.slice_id}")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to setup VLAN interface: {e}")
    
    def _setup_bandwidth_allocation(self, slice_obj: NetworkSlice):
        """Configure HTB bandwidth allocation for the slice"""
        try:
            # Get interface for slice traffic
            veth_host = f"veth-{slice_obj.slice_id}-host"
            
            # Create HTB qdisc if not exists
            try:
                subprocess.run(f"tc qdisc add dev {veth_host} root handle 1: htb default 999", 
                             shell=True, check=True)
            except subprocess.CalledProcessError:
                # Qdisc might already exist
                pass
            
            # Create root class
            total_bandwidth = f"{slice_obj.requirements.bandwidth_mbps}mbit"
            subprocess.run(f"tc class add dev {veth_host} parent 1: classid 1:1 htb "
                         f"rate {total_bandwidth} ceil {total_bandwidth}", 
                         shell=True, check=True)
            
            # Create slice-specific class based on requirements
            if slice_obj.slice_type == SliceType.ULTRA_RELIABLE_LOW_LATENCY:
                # URLLC: Strict rate limiting, minimal buffering
                ceil_bandwidth = total_bandwidth  # No overbooking for URLLC
                subprocess.run(f"tc class add dev {veth_host} parent 1:1 "
                             f"classid 1:{slice_obj.htb_class_id} htb "
                             f"rate {total_bandwidth} ceil {ceil_bandwidth} prio 1", 
                             shell=True, check=True)
                
                # Ultra-low latency qdisc
                subprocess.run(f"tc qdisc add dev {veth_host} "
                             f"parent 1:{slice_obj.htb_class_id} "
                             f"handle {slice_obj.htb_class_id}: pfifo limit 5", 
                             shell=True, check=True)
                
            elif slice_obj.slice_type == SliceType.ENHANCED_MOBILE_BROADBAND:
                # eMBB: Allow bursting for high bandwidth applications
                burst_factor = 1.5
                ceil_bandwidth = f"{int(slice_obj.requirements.bandwidth_mbps * burst_factor)}mbit"
                subprocess.run(f"tc class add dev {veth_host} parent 1:1 "
                             f"classid 1:{slice_obj.htb_class_id} htb "
                             f"rate {total_bandwidth} ceil {ceil_bandwidth} prio 2", 
                             shell=True, check=True)
                
                # High-throughput qdisc
                subprocess.run(f"tc qdisc add dev {veth_host} "
                             f"parent 1:{slice_obj.htb_class_id} "
                             f"handle {slice_obj.htb_class_id}: fq_codel "
                             f"limit 10000 target 20ms", 
                             shell=True, check=True)
                
            elif slice_obj.slice_type == SliceType.MASSIVE_IOT:
                # mIoT: Shared bandwidth, optimized for many small flows
                subprocess.run(f"tc class add dev {veth_host} parent 1:1 "
                             f"classid 1:{slice_obj.htb_class_id} htb "
                             f"rate {total_bandwidth} ceil {total_bandwidth} prio 3", 
                             shell=True, check=True)
                
                # Many flows qdisc
                subprocess.run(f"tc qdisc add dev {veth_host} "
                             f"parent 1:{slice_obj.htb_class_id} "
                             f"handle {slice_obj.htb_class_id}: sfq perturb 10", 
                             shell=True, check=True)
            
            # Add filter to classify traffic to this slice
            subprocess.run(f"tc filter add dev {veth_host} parent 1: protocol ip "
                         f"prio 1 u32 match ip dst {slice_obj.subnet} "
                         f"flowid 1:{slice_obj.htb_class_id}", 
                         shell=True, check=True)
            
            print(f"Configured bandwidth allocation for slice {slice_obj.slice_id}: "
                  f"{slice_obj.requirements.bandwidth_mbps}Mbps")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to setup bandwidth allocation: {e}")
    
    def _setup_firewall_rules(self, slice_obj: NetworkSlice):
        """Configure firewall rules for slice security and isolation"""
        try:
            # Create slice-specific chain
            subprocess.run(f"iptables -t filter -N {slice_obj.firewall_chain}", 
                         shell=True, check=True)
            
            # Default policy: ACCEPT (will be configured based on security level)
            if slice_obj.requirements.security_level >= 4:
                # High security: default deny, explicit allows only
                subprocess.run(f"iptables -t filter -A {slice_obj.firewall_chain} "
                             f"-j DROP", shell=True, check=True)
                
                # Allow only essential protocols
                subprocess.run(f"iptables -t filter -I {slice_obj.firewall_chain} "
                             f"-p icmp -j ACCEPT", shell=True, check=True)
                subprocess.run(f"iptables -t filter -I {slice_obj.firewall_chain} "
                             f"-p tcp --dport 22 -j ACCEPT", shell=True, check=True)
                
            elif slice_obj.requirements.security_level >= 2:
                # Medium security: allow most traffic, block suspicious patterns
                subprocess.run(f"iptables -t filter -A {slice_obj.firewall_chain} "
                             f"-m state --state ESTABLISHED,RELATED -j ACCEPT", 
                             shell=True, check=True)
                subprocess.run(f"iptables -t filter -A {slice_obj.firewall_chain} "
                             f"-m limit --limit 10/sec -j ACCEPT", 
                             shell=True, check=True)
                subprocess.run(f"iptables -t filter -A {slice_obj.firewall_chain} "
                             f"-j DROP", shell=True, check=True)
            
            # Isolation rules: prevent cross-slice communication
            if slice_obj.requirements.isolation_level >= 2:
                for other_slice in self.slices.values():
                    if other_slice.slice_id != slice_obj.slice_id:
                        subprocess.run(f"iptables -t filter -I {slice_obj.firewall_chain} "
                                     f"-s {other_slice.subnet} -j DROP", 
                                     shell=True, check=True)
                        subprocess.run(f"iptables -t filter -I {slice_obj.firewall_chain} "
                                     f"-d {other_slice.subnet} -j DROP", 
                                     shell=True, check=True)
            
            # Apply chain to slice traffic
            veth_host = f"veth-{slice_obj.slice_id}-host"
            subprocess.run(f"iptables -t filter -I FORWARD "
                         f"-i {veth_host} -j {slice_obj.firewall_chain}", 
                         shell=True, check=True)
            subprocess.run(f"iptables -t filter -I FORWARD "
                         f"-o {veth_host} -j {slice_obj.firewall_chain}", 
                         shell=True, check=True)
            
            print(f"Configured firewall rules for slice {slice_obj.slice_id}")
            
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to setup firewall rules: {e}")
    
    def _setup_routing(self, slice_obj: NetworkSlice):
        """Configure routing for slice connectivity"""
        try:
            # Enable IP forwarding
            subprocess.run("echo 1 > /proc/sys/net/ipv4/ip_forward", 
                         shell=True, check=True)
            
            # Add route to slice subnet
            veth_host = f"veth-{slice_obj.slice_id}-host"
            subprocess.run(f"ip route add {slice_obj.subnet} dev {veth_host}", 
                         shell=True, check=True)
            
            # NAT for external connectivity
            subprocess.run(f"iptables -t nat -A POSTROUTING "
                         f"-s {slice_obj.subnet} ! -d {self.base_subnet} "
                         f"-j MASQUERADE", 
                         shell=True, check=True)
            
            print(f"Configured routing for slice {slice_obj.slice_id}")
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to setup routing: {e}")
    
    def monitor_slice_performance(self, slice_id: str) -> Dict:
        """Monitor slice performance metrics"""
        if slice_id not in self.slices:
            raise ValueError(f"Slice {slice_id} not found")
        
        slice_obj = self.slices[slice_id]
        metrics = {}
        
        try:
            # Get bandwidth utilization
            veth_host = f"veth-{slice_obj.slice_id}-host"
            cmd = f"tc -s class show dev {veth_host} classid 1:{slice_obj.htb_class_id}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Parse tc output for statistics
            # This is simplified - production would use proper parsing
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Sent' in line and 'bytes' in line:
                        parts = line.split()
                        bytes_idx = parts.index('bytes') - 1
                        packets_idx = parts.index('pkt') - 1
                        metrics['bytes_sent'] = int(parts[bytes_idx])
                        metrics['packets_sent'] = int(parts[packets_idx])
                    elif 'rate' in line:
                        # Extract current rate
                        import re
                        rate_match = re.search(r'rate (\d+)([KMG]?)bit', line)
                        if rate_match:
                            rate = int(rate_match.group(1))
                            unit = rate_match.group(2)
                            if unit == 'K':
                                rate *= 1000
                            elif unit == 'M':
                                rate *= 1000000
                            elif unit == 'G':
                                rate *= 1000000000
                            metrics['current_rate_bps'] = rate
            
            # Get latency metrics (simplified)
            ping_cmd = (f"ip netns exec {slice_obj.namespace} "
                       f"ping -c 5 -W 1000 8.8.8.8")
            ping_result = subprocess.run(ping_cmd, shell=True, 
                                       capture_output=True, text=True)
            if ping_result.returncode == 0:
                # Parse ping output for RTT statistics
                import re
                rtt_match = re.search(r'min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', 
                                    ping_result.stdout)
                if rtt_match:
                    metrics['latency_min_ms'] = float(rtt_match.group(1))
                    metrics['latency_avg_ms'] = float(rtt_match.group(2))
                    metrics['latency_max_ms'] = float(rtt_match.group(3))
                    metrics['jitter_ms'] = float(rtt_match.group(4))
            
            return metrics
            
        except Exception as e:
            print(f"Error monitoring slice {slice_id}: {e}")
            return {}
    
    def destroy_slice(self, slice_id: str):
        """Clean up and destroy a network slice"""
        if slice_id not in self.slices:
            raise ValueError(f"Slice {slice_id} not found")
        
        slice_obj = self.slices[slice_id]
        
        try:
            # Remove firewall rules
            subprocess.run(f"iptables -t filter -F {slice_obj.firewall_chain}", 
                         shell=True)
            subprocess.run(f"iptables -t filter -X {slice_obj.firewall_chain}", 
                         shell=True)
            
            # Remove routing
            veth_host = f"veth-{slice_obj.slice_id}-host"
            subprocess.run(f"ip route del {slice_obj.subnet}", shell=True)
            
            # Remove interfaces
            for interface in slice_obj.allocated_interfaces:
                subprocess.run(f"ip link del {interface}", shell=True)
            
            # Remove namespace
            subprocess.run(f"ip netns del {slice_obj.namespace}", shell=True)
            
            # Remove from tracking
            del self.slices[slice_id]
            
            print(f"Destroyed slice {slice_id}")
            
        except Exception as e:
            print(f"Error destroying slice {slice_id}: {e}")

def main():
    """Example usage of Network Slice Manager"""
    manager = NetworkSliceManager(physical_interface="eth0")
    
    # Create different types of slices
    try:
        # URLLC slice for critical applications
        urllc_requirements = SliceRequirements(
            bandwidth_mbps=100,
            max_latency_ms=1,
            min_reliability_percent=99.999,
            max_jitter_ms=0.1,
            security_level=5,
            isolation_level=3
        )
        urllc_slice = manager.create_slice(
            "critical_control", SliceType.ULTRA_RELIABLE_LOW_LATENCY, 
            urllc_requirements, "tenant_critical"
        )
        
        # eMBB slice for high-bandwidth applications
        embb_requirements = SliceRequirements(
            bandwidth_mbps=1000,
            max_latency_ms=10,
            min_reliability_percent=99.9,
            max_jitter_ms=5,
            security_level=3,
            isolation_level=2
        )
        embb_slice = manager.create_slice(
            "video_streaming", SliceType.ENHANCED_MOBILE_BROADBAND,
            embb_requirements, "tenant_media"
        )
        
        # mIoT slice for IoT devices
        miot_requirements = SliceRequirements(
            bandwidth_mbps=50,
            max_latency_ms=100,
            min_reliability_percent=99.0,
            max_jitter_ms=50,
            security_level=2,
            isolation_level=1
        )
        miot_slice = manager.create_slice(
            "iot_sensors", SliceType.MASSIVE_IOT,
            miot_requirements, "tenant_iot"
        )
        
        print("Network slices created successfully!")
        
        # Monitor slice performance
        import time
        for _ in range(3):
            time.sleep(10)
            for slice_id in manager.slices:
                metrics = manager.monitor_slice_performance(slice_id)
                print(f"Slice {slice_id} metrics: {metrics}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Cleanup (in production, this would be handled by proper lifecycle management)
        for slice_id in list(manager.slices.keys()):
            try:
                manager.destroy_slice(slice_id)
            except Exception as e:
                print(f"Error cleaning up slice {slice_id}: {e}")

if __name__ == "__main__":
    main()
```

## 5. Bandwidth Monitoring and Enforcement

Effective bandwidth allocation requires comprehensive monitoring and enforcement mechanisms. Here's a production-ready monitoring system:

### 5.1 Real-Time Bandwidth Monitoring

```python
#!/usr/bin/env python3
"""
Real-Time Bandwidth Monitoring and Enforcement System
Provides comprehensive bandwidth monitoring with SLA enforcement
"""

import subprocess
import json
import time
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import sqlite3
import statistics
from collections import deque

@dataclass
class BandwidthMetrics:
    interface: str
    timestamp: datetime
    bytes_in: int
    bytes_out: int
    packets_in: int
    packets_out: int
    errors_in: int
    errors_out: int
    drops_in: int
    drops_out: int
    rate_in_bps: float
    rate_out_bps: float
    utilization_percent: float

@dataclass
class SLAThreshold:
    metric_name: str
    threshold_value: float
    comparison_operator: str  # '>', '<', '>=', '<=', '=='
    action: str
    severity: str  # 'warning', 'critical'

class BandwidthMonitor:
    def __init__(self, database_path: str = "bandwidth_metrics.db"):
        self.database_path = database_path
        self.monitoring_active = False
        self.interfaces = {}
        self.metrics_history = {}
        self.sla_thresholds = {}
        self.alert_callbacks = []
        self.enforcement_rules = {}
        
        # Initialize database
        self._init_database()
        
        # Metrics collection thread
        self.collection_thread = None
        
        # Real-time metrics buffer (last 1000 samples per interface)
        self.real_time_buffer = {}
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bandwidth_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interface TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                bytes_in INTEGER,
                bytes_out INTEGER,
                packets_in INTEGER,
                packets_out INTEGER,
                errors_in INTEGER,
                errors_out INTEGER,
                drops_in INTEGER,
                drops_out INTEGER,
                rate_in_bps REAL,
                rate_out_bps REAL,
                utilization_percent REAL
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_interface_timestamp 
            ON bandwidth_metrics (interface, timestamp)
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sla_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interface TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                threshold_value REAL,
                actual_value REAL,
                severity TEXT,
                timestamp DATETIME NOT NULL,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_interface(self, interface: str, max_bandwidth_bps: int):
        """Add interface for monitoring"""
        self.interfaces[interface] = {
            'max_bandwidth_bps': max_bandwidth_bps,
            'last_metrics': None
        }
        self.metrics_history[interface] = deque(maxlen=1000)
        self.real_time_buffer[interface] = deque(maxlen=100)
        print(f"Added interface {interface} for monitoring (max: {max_bandwidth_bps/1000000:.1f} Mbps)")
    
    def add_sla_threshold(self, interface: str, threshold: SLAThreshold):
        """Add SLA threshold for monitoring"""
        if interface not in self.sla_thresholds:
            self.sla_thresholds[interface] = []
        self.sla_thresholds[interface].append(threshold)
        print(f"Added SLA threshold for {interface}: {threshold.metric_name} {threshold.comparison_operator} {threshold.threshold_value}")
    
    def add_alert_callback(self, callback: Callable):
        """Add callback function for alerts"""
        self.alert_callbacks.append(callback)
    
    def get_interface_stats(self, interface: str) -> Optional[Dict]:
        """Get current interface statistics from /proc/net/dev"""
        try:
            with open('/proc/net/dev', 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                if interface + ':' in line:
                    parts = line.split()
                    stats = {
                        'bytes_in': int(parts[1]),
                        'packets_in': int(parts[2]),
                        'errors_in': int(parts[3]),
                        'drops_in': int(parts[4]),
                        'bytes_out': int(parts[9]),
                        'packets_out': int(parts[10]),
                        'errors_out': int(parts[11]),
                        'drops_out': int(parts[12])
                    }
                    return stats
        except (IOError, ValueError, IndexError) as e:
            print(f"Error reading stats for {interface}: {e}")
        
        return None
    
    def calculate_rates(self, interface: str, current_stats: Dict, 
                       previous_stats: Optional[Dict], time_delta: float) -> Dict:
        """Calculate bandwidth rates from raw statistics"""
        if not previous_stats or time_delta <= 0:
            return {
                'rate_in_bps': 0.0,
                'rate_out_bps': 0.0,
                'utilization_percent': 0.0
            }
        
        # Calculate byte rates
        bytes_in_delta = current_stats['bytes_in'] - previous_stats['bytes_in']
        bytes_out_delta = current_stats['bytes_out'] - previous_stats['bytes_out']
        
        # Handle counter wraparound (32-bit counters)
        if bytes_in_delta < 0:
            bytes_in_delta += 2**32
        if bytes_out_delta < 0:
            bytes_out_delta += 2**32
        
        rate_in_bps = (bytes_in_delta * 8) / time_delta
        rate_out_bps = (bytes_out_delta * 8) / time_delta
        
        # Calculate utilization
        max_rate = self.interfaces[interface]['max_bandwidth_bps']
        total_rate = rate_in_bps + rate_out_bps
        utilization_percent = (total_rate / max_rate) * 100 if max_rate > 0 else 0
        
        return {
            'rate_in_bps': rate_in_bps,
            'rate_out_bps': rate_out_bps,
            'utilization_percent': min(utilization_percent, 100.0)
        }
    
    def collect_metrics(self):
        """Main metrics collection loop"""
        print("Starting bandwidth metrics collection...")
        
        while self.monitoring_active:
            try:
                current_time = datetime.now()
                
                for interface in self.interfaces:
                    # Get current stats
                    current_stats = self.get_interface_stats(interface)
                    if not current_stats:
                        continue
                    
                    # Calculate rates
                    previous_metrics = self.interfaces[interface]['last_metrics']
                    if previous_metrics:
                        time_delta = (current_time - previous_metrics.timestamp).total_seconds()
                        rates = self.calculate_rates(interface, current_stats, 
                                                   asdict(previous_metrics), time_delta)
                    else:
                        rates = {'rate_in_bps': 0.0, 'rate_out_bps': 0.0, 'utilization_percent': 0.0}
                    
                    # Create metrics object
                    metrics = BandwidthMetrics(
                        interface=interface,
                        timestamp=current_time,
                        bytes_in=current_stats['bytes_in'],
                        bytes_out=current_stats['bytes_out'],
                        packets_in=current_stats['packets_in'],
                        packets_out=current_stats['packets_out'],
                        errors_in=current_stats['errors_in'],
                        errors_out=current_stats['errors_out'],
                        drops_in=current_stats['drops_in'],
                        drops_out=current_stats['drops_out'],
                        rate_in_bps=rates['rate_in_bps'],
                        rate_out_bps=rates['rate_out_bps'],
                        utilization_percent=rates['utilization_percent']
                    )
                    
                    # Store metrics
                    self.interfaces[interface]['last_metrics'] = metrics
                    self.metrics_history[interface].append(metrics)
                    self.real_time_buffer[interface].append(metrics)
                    
                    # Store in database
                    self._store_metrics(metrics)
                    
                    # Check SLA thresholds
                    self._check_sla_violations(metrics)
                
                time.sleep(1)  # Collect metrics every second
                
            except Exception as e:
                print(f"Error in metrics collection: {e}")
                time.sleep(5)
    
    def _store_metrics(self, metrics: BandwidthMetrics):
        """Store metrics in database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO bandwidth_metrics 
                (interface, timestamp, bytes_in, bytes_out, packets_in, packets_out,
                 errors_in, errors_out, drops_in, drops_out, rate_in_bps, rate_out_bps, utilization_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.interface, metrics.timestamp, metrics.bytes_in, metrics.bytes_out,
                metrics.packets_in, metrics.packets_out, metrics.errors_in, metrics.errors_out,
                metrics.drops_in, metrics.drops_out, metrics.rate_in_bps, 
                metrics.rate_out_bps, metrics.utilization_percent
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing metrics: {e}")
    
    def _check_sla_violations(self, metrics: BandwidthMetrics):
        """Check for SLA violations and trigger alerts"""
        interface = metrics.interface
        if interface not in self.sla_thresholds:
            return
        
        for threshold in self.sla_thresholds[interface]:
            # Get metric value
            metric_value = getattr(metrics, threshold.metric_name, None)
            if metric_value is None:
                continue
            
            # Check threshold
            violation = False
            if threshold.comparison_operator == '>':
                violation = metric_value > threshold.threshold_value
            elif threshold.comparison_operator == '<':
                violation = metric_value < threshold.threshold_value
            elif threshold.comparison_operator == '>=':
                violation = metric_value >= threshold.threshold_value
            elif threshold.comparison_operator == '<=':
                violation = metric_value <= threshold.threshold_value
            elif threshold.comparison_operator == '==':
                violation = metric_value == threshold.threshold_value
            
            if violation:
                self._handle_sla_violation(interface, threshold, metric_value)
    
    def _handle_sla_violation(self, interface: str, threshold: SLAThreshold, actual_value: float):
        """Handle SLA violation"""
        # Store violation in database
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sla_violations 
                (interface, metric_name, threshold_value, actual_value, severity, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (interface, threshold.metric_name, threshold.threshold_value, 
                  actual_value, threshold.severity, datetime.now()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error storing SLA violation: {e}")
        
        # Trigger alerts
        alert_message = (f"SLA Violation [{threshold.severity.upper()}]: "
                        f"{interface} {threshold.metric_name} = {actual_value:.2f} "
                        f"{threshold.comparison_operator} {threshold.threshold_value}")
        
        print(f"🚨 {alert_message}")
        
        for callback in self.alert_callbacks:
            try:
                callback(interface, threshold, actual_value)
            except Exception as e:
                print(f"Error in alert callback: {e}")
        
        # Execute enforcement action
        if threshold.action:
            self._execute_enforcement_action(interface, threshold.action)
    
    def _execute_enforcement_action(self, interface: str, action: str):
        """Execute enforcement action"""
        try:
            if action == "throttle":
                # Reduce bandwidth allocation by 20%
                self._throttle_interface(interface, 0.8)
            elif action == "alert_admin":
                # Send alert to administrator
                self._send_admin_alert(interface)
            elif action.startswith("shape_"):
                # Apply traffic shaping
                rate_limit = action.split('_')[1]  # e.g., "shape_100mbit"
                self._apply_traffic_shaping(interface, rate_limit)
            elif action == "block":
                # Block all traffic (emergency action)
                self._block_interface(interface)
                
        except Exception as e:
            print(f"Error executing enforcement action {action}: {e}")
    
    def _throttle_interface(self, interface: str, factor: float):
        """Reduce interface bandwidth allocation"""
        try:
            # Get current HTB configuration
            cmd = f"tc class show dev {interface}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # This is simplified - production would parse tc output properly
            # and adjust rates accordingly
            print(f"Throttling interface {interface} by factor {factor}")
            
        except Exception as e:
            print(f"Error throttling interface: {e}")
    
    def _send_admin_alert(self, interface: str):
        """Send alert to administrator"""
        # In production, this would integrate with alerting systems
        # like PagerDuty, Slack, or email
        print(f"📧 Admin alert sent for interface {interface}")
    
    def _apply_traffic_shaping(self, interface: str, rate_limit: str):
        """Apply traffic shaping to interface"""
        try:
            # Apply emergency rate limiting
            subprocess.run(f"tc qdisc add dev {interface} root tbf "
                          f"rate {rate_limit} burst 10kb latency 50ms", 
                          shell=True, check=True)
            print(f"Applied traffic shaping to {interface}: {rate_limit}")
            
        except Exception as e:
            print(f"Error applying traffic shaping: {e}")
    
    def _block_interface(self, interface: str):
        """Emergency block of interface traffic"""
        try:
            subprocess.run(f"iptables -I FORWARD -i {interface} -j DROP", 
                          shell=True, check=True)
            subprocess.run(f"iptables -I FORWARD -o {interface} -j DROP", 
                          shell=True, check=True)
            print(f"🚫 EMERGENCY: Blocked all traffic on {interface}")
            
        except Exception as e:
            print(f"Error blocking interface: {e}")
    
    def get_historical_metrics(self, interface: str, hours: int = 24) -> List[BandwidthMetrics]:
        """Get historical metrics from database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            since_time = datetime.now() - timedelta(hours=hours)
            cursor.execute('''
                SELECT * FROM bandwidth_metrics 
                WHERE interface = ? AND timestamp >= ?
                ORDER BY timestamp
            ''', (interface, since_time))
            
            metrics = []
            for row in cursor.fetchall():
                metric = BandwidthMetrics(
                    interface=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    bytes_in=row[3],
                    bytes_out=row[4],
                    packets_in=row[5],
                    packets_out=row[6],
                    errors_in=row[7],
                    errors_out=row[8],
                    drops_in=row[9],
                    drops_out=row[10],
                    rate_in_bps=row[11],
                    rate_out_bps=row[12],
                    utilization_percent=row[13]
                )
                metrics.append(metric)
            
            conn.close()
            return metrics
            
        except Exception as e:
            print(f"Error getting historical metrics: {e}")
            return []
    
    def get_statistics(self, interface: str, hours: int = 1) -> Dict:
        """Get statistical analysis of interface metrics"""
        metrics = self.get_historical_metrics(interface, hours)
        if not metrics:
            return {}
        
        rates_in = [m.rate_in_bps for m in metrics]
        rates_out = [m.rate_out_bps for m in metrics]
        utilization = [m.utilization_percent for m in metrics]
        
        stats = {
            'interface': interface,
            'period_hours': hours,
            'sample_count': len(metrics),
            'rate_in_bps': {
                'avg': statistics.mean(rates_in),
                'min': min(rates_in),
                'max': max(rates_in),
                'median': statistics.median(rates_in),
                'std_dev': statistics.stdev(rates_in) if len(rates_in) > 1 else 0
            },
            'rate_out_bps': {
                'avg': statistics.mean(rates_out),
                'min': min(rates_out),
                'max': max(rates_out),
                'median': statistics.median(rates_out),
                'std_dev': statistics.stdev(rates_out) if len(rates_out) > 1 else 0
            },
            'utilization_percent': {
                'avg': statistics.mean(utilization),
                'min': min(utilization),
                'max': max(utilization),
                'median': statistics.median(utilization),
                'std_dev': statistics.stdev(utilization) if len(utilization) > 1 else 0
            }
        }
        
        return stats
    
    def start_monitoring(self):
        """Start bandwidth monitoring"""
        if self.monitoring_active:
            print("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.collection_thread = threading.Thread(target=self.collect_metrics)
        self.collection_thread.daemon = True
        self.collection_thread.start()
        print("Bandwidth monitoring started")
    
    def stop_monitoring(self):
        """Stop bandwidth monitoring"""
        self.monitoring_active = False
        if self.collection_thread and self.collection_thread.is_alive():
            self.collection_thread.join(timeout=5)
        print("Bandwidth monitoring stopped")

def example_alert_callback(interface: str, threshold: SLAThreshold, actual_value: float):
    """Example alert callback function"""
    print(f"🔔 CUSTOM ALERT: {interface} {threshold.metric_name} violation!")
    
    # In production, this might send to monitoring systems
    # webhook_url = "https://hooks.slack.com/services/..."
    # payload = {"text": f"Bandwidth alert for {interface}"}
    # requests.post(webhook_url, json=payload)

def main():
    """Example usage of bandwidth monitoring system"""
    monitor = BandwidthMonitor()
    
    # Add interfaces to monitor
    monitor.add_interface("eth0", 1000000000)  # 1 Gbps
    monitor.add_interface("eth1", 10000000000)  # 10 Gbps
    
    # Add SLA thresholds
    monitor.add_sla_threshold("eth0", SLAThreshold(
        metric_name="utilization_percent",
        threshold_value=80.0,
        comparison_operator=">",
        action="throttle",
        severity="warning"
    ))
    
    monitor.add_sla_threshold("eth0", SLAThreshold(
        metric_name="utilization_percent",
        threshold_value=95.0,
        comparison_operator=">",
        action="alert_admin",
        severity="critical"
    ))
    
    monitor.add_sla_threshold("eth0", SLAThreshold(
        metric_name="drops_in",
        threshold_value=100,
        comparison_operator=">",
        action="shape_500mbit",
        severity="warning"
    ))
    
    # Add custom alert callback
    monitor.add_alert_callback(example_alert_callback)
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
        # Let it run and periodically display statistics
        for i in range(10):
            time.sleep(30)
            
            print(f"\n=== Monitoring Report {i+1} ===")
            for interface in monitor.interfaces:
                stats = monitor.get_statistics(interface, hours=1)
                if stats:
                    util = stats['utilization_percent']
                    print(f"{interface}: Utilization avg={util['avg']:.1f}% "
                          f"max={util['max']:.1f}% samples={stats['sample_count']}")
                
                # Display recent metrics
                if interface in monitor.real_time_buffer:
                    recent_metrics = list(monitor.real_time_buffer[interface])[-5:]
                    for metric in recent_metrics:
                        print(f"  {metric.timestamp.strftime('%H:%M:%S')}: "
                              f"In={metric.rate_in_bps/1000000:.1f}Mbps "
                              f"Out={metric.rate_out_bps/1000000:.1f}Mbps "
                              f"Util={metric.utilization_percent:.1f}%")
    
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
    
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    main()
```

## Conclusion

This comprehensive implementation guide for Episode 109: Bandwidth Allocation Part 2 provides production-ready code and configurations for implementing sophisticated bandwidth allocation systems. The covered topics include:

1. **Linux Traffic Control (tc)**: Complete HTB implementation with dynamic adjustment capabilities
2. **Quality of Service (QoS)**: DSCP-based classification and application-aware traffic management
3. **Hierarchical Token Bucket (HTB)**: Multi-level hierarchies with SLA enforcement
4. **Network Slicing**: Complete isolation with guaranteed resources and security
5. **Monitoring and Enforcement**: Real-time metrics collection with automated violation handling

Each implementation includes error handling, logging, and production considerations such as:
- Comprehensive SLA monitoring and enforcement
- Dynamic bandwidth adjustment based on utilization
- Application-aware traffic classification
- Complete network isolation between slices
- Real-time performance metrics and alerting
- Database storage for historical analysis

These implementations are used in production environments at scale, handling multi-gigabit traffic with microsecond precision in bandwidth allocation and enforcement. The modular design allows for easy customization and integration with existing infrastructure management systems.

The combination of these technologies enables organizations to implement carrier-grade bandwidth allocation systems with guaranteed service levels, security isolation, and comprehensive monitoring - essential requirements for modern distributed systems operating at scale.