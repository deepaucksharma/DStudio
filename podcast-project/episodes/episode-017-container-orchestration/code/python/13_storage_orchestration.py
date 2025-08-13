#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Storage Orchestration with Persistent Volumes for Container Orchestration
Episode 17: Container Orchestration

यह example दिखाता है कि कैसे MakeMyTrip जैसी travel companies
production में container storage को efficiently manage करती हैं।

Real-world scenario: MakeMyTrip का storage orchestration for travel data
"""

import yaml
import json
import os
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from loguru import logger

class StorageClass(Enum):
    """Storage class enumeration"""
    FAST_SSD = "fast-ssd"           # High IOPS, low latency
    STANDARD_SSD = "standard-ssd"   # Balanced performance
    STANDARD_HDD = "standard-hdd"   # Cost-effective storage
    COLD_STORAGE = "cold-storage"   # Archive storage
    BACKUP_STORAGE = "backup"       # Backup and disaster recovery

class AccessMode(Enum):
    """Persistent Volume access modes"""
    READ_WRITE_ONCE = "ReadWriteOnce"      # Single node, read-write
    READ_ONLY_MANY = "ReadOnlyMany"        # Multiple nodes, read-only
    READ_WRITE_MANY = "ReadWriteMany"      # Multiple nodes, read-write

class VolumeType(Enum):
    """Volume type enumeration"""
    DATABASE = "database"
    LOGS = "logs"
    CACHE = "cache"
    MEDIA = "media"
    BACKUP = "backup"
    TEMP = "temp"

@dataclass
class StorageRequirement:
    """Storage requirement specification"""
    service_name: str
    volume_type: VolumeType
    storage_class: StorageClass
    access_mode: AccessMode
    size_gb: int
    backup_required: bool
    retention_days: int
    performance_tier: str
    encryption_required: bool

class MakeMyTripStorageOrchestrator:
    """
    MakeMyTrip-style Storage Orchestrator for Container Orchestration
    Production-ready storage management for Indian travel industry
    """
    
    def __init__(self):
        # MakeMyTrip service storage requirements
        self.service_storage_requirements = {
            "flight-search": {
                "cache_storage": StorageRequirement(
                    service_name="flight-search",
                    volume_type=VolumeType.CACHE,
                    storage_class=StorageClass.FAST_SSD,
                    access_mode=AccessMode.READ_WRITE_ONCE,
                    size_gb=100,
                    backup_required=False,
                    retention_days=1,
                    performance_tier="high_iops",
                    encryption_required=True
                ),
                "search_logs": StorageRequirement(
                    service_name="flight-search",
                    volume_type=VolumeType.LOGS,
                    storage_class=StorageClass.STANDARD_SSD,
                    access_mode=AccessMode.READ_WRITE_ONCE,
                    size_gb=50,
                    backup_required=True,
                    retention_days=90,
                    performance_tier="standard",
                    encryption_required=True
                )
            },
            
            "hotel-booking": {
                "booking_database": StorageRequirement(
                    service_name="hotel-booking",
                    volume_type=VolumeType.DATABASE,
                    storage_class=StorageClass.FAST_SSD,
                    access_mode=AccessMode.READ_WRITE_ONCE,
                    size_gb=500,
                    backup_required=True,
                    retention_days=2555,  # 7 years for financial records
                    performance_tier="high_performance",
                    encryption_required=True
                ),
                "booking_media": StorageRequirement(
                    service_name="hotel-booking",
                    volume_type=VolumeType.MEDIA,
                    storage_class=StorageClass.STANDARD_HDD,
                    access_mode=AccessMode.READ_ONLY_MANY,
                    size_gb=2000,
                    backup_required=True,
                    retention_days=1095,  # 3 years
                    performance_tier="standard",
                    encryption_required=False
                )
            },
            
            "payment-service": {
                "transaction_database": StorageRequirement(
                    service_name="payment-service",
                    volume_type=VolumeType.DATABASE,
                    storage_class=StorageClass.FAST_SSD,
                    access_mode=AccessMode.READ_WRITE_ONCE,
                    size_gb=1000,
                    backup_required=True,
                    retention_days=3650,  # 10 years for financial compliance
                    performance_tier="ultra_high_performance",
                    encryption_required=True
                ),
                "payment_logs": StorageRequirement(
                    service_name="payment-service",
                    volume_type=VolumeType.LOGS,
                    storage_class=StorageClass.STANDARD_SSD,
                    access_mode=AccessMode.READ_WRITE_ONCE,
                    size_gb=200,
                    backup_required=True,
                    retention_days=2555,  # 7 years for audit
                    performance_tier="high_iops",
                    encryption_required=True
                )
            },
            
            "user-service": {
                "user_database": StorageRequirement(
                    service_name="user-service",
                    volume_type=VolumeType.DATABASE,
                    storage_class=StorageClass.STANDARD_SSD,
                    access_mode=AccessMode.READ_WRITE_ONCE,
                    size_gb=300,
                    backup_required=True,
                    retention_days=1825,  # 5 years
                    performance_tier="standard",
                    encryption_required=True
                ),
                "user_media": StorageRequirement(
                    service_name="user-service",
                    volume_type=VolumeType.MEDIA,
                    storage_class=StorageClass.STANDARD_HDD,
                    access_mode=AccessMode.READ_WRITE_MANY,
                    size_gb=1000,
                    backup_required=True,
                    retention_days=1095,  # 3 years
                    performance_tier="standard",
                    encryption_required=False
                )
            },
            
            "analytics-service": {
                "analytics_database": StorageRequirement(
                    service_name="analytics-service",
                    volume_type=VolumeType.DATABASE,
                    storage_class=StorageClass.STANDARD_SSD,
                    access_mode=AccessMode.READ_WRITE_ONCE,
                    size_gb=2000,
                    backup_required=True,
                    retention_days=1095,  # 3 years
                    performance_tier="high_throughput",
                    encryption_required=True
                ),
                "analytics_logs": StorageRequirement(
                    service_name="analytics-service",
                    volume_type=VolumeType.LOGS,
                    storage_class=StorageClass.COLD_STORAGE,
                    access_mode=AccessMode.READ_WRITE_ONCE,
                    size_gb=5000,
                    backup_required=True,
                    retention_days=365,  # 1 year
                    performance_tier="archive",
                    encryption_required=True
                )
            }
        }
        
        # Indian cloud storage options and pricing
        self.storage_providers = {
            "aws": {
                "regions": ["ap-south-1", "ap-southeast-1"],
                "storage_classes": {
                    StorageClass.FAST_SSD: {
                        "type": "gp3",
                        "iops": 3000,
                        "throughput": 125,
                        "cost_per_gb_month": 0.08  # USD
                    },
                    StorageClass.STANDARD_SSD: {
                        "type": "gp2",
                        "iops": 100,
                        "throughput": 250,
                        "cost_per_gb_month": 0.05
                    },
                    StorageClass.STANDARD_HDD: {
                        "type": "sc1",
                        "iops": 12,
                        "throughput": 250,
                        "cost_per_gb_month": 0.025
                    },
                    StorageClass.COLD_STORAGE: {
                        "type": "st1",
                        "iops": 12,
                        "throughput": 500,
                        "cost_per_gb_month": 0.015
                    }
                }
            },
            
            "azure": {
                "regions": ["Central India", "South India"],
                "storage_classes": {
                    StorageClass.FAST_SSD: {
                        "type": "Premium_LRS",
                        "iops": 5000,
                        "throughput": 200,
                        "cost_per_gb_month": 0.09
                    },
                    StorageClass.STANDARD_SSD: {
                        "type": "StandardSSD_LRS",
                        "iops": 500,
                        "throughput": 60,
                        "cost_per_gb_month": 0.06
                    }
                }
            },
            
            "gcp": {
                "regions": ["asia-south1", "asia-southeast1"],
                "storage_classes": {
                    StorageClass.FAST_SSD: {
                        "type": "pd-ssd",
                        "iops": 3000,
                        "throughput": 240,
                        "cost_per_gb_month": 0.085
                    },
                    StorageClass.STANDARD_HDD: {
                        "type": "pd-standard",
                        "iops": 75,
                        "throughput": 120,
                        "cost_per_gb_month": 0.04
                    }
                }
            }
        }
        
        # Backup and disaster recovery configurations
        self.backup_strategies = {
            VolumeType.DATABASE: {
                "frequency": "hourly",
                "retention_daily": 7,
                "retention_weekly": 4,
                "retention_monthly": 12,
                "cross_region": True,
                "point_in_time_recovery": True
            },
            VolumeType.LOGS: {
                "frequency": "daily",
                "retention_daily": 30,
                "retention_weekly": 12,
                "retention_monthly": 24,
                "cross_region": True,
                "point_in_time_recovery": False
            },
            VolumeType.MEDIA: {
                "frequency": "weekly",
                "retention_daily": 0,
                "retention_weekly": 8,
                "retention_monthly": 12,
                "cross_region": True,
                "point_in_time_recovery": False
            },
            VolumeType.CACHE: {
                "frequency": "none",
                "retention_daily": 0,
                "retention_weekly": 0,
                "retention_monthly": 0,
                "cross_region": False,
                "point_in_time_recovery": False
            }
        }
        
        logger.info("✈️ MakeMyTrip Storage Orchestrator initialized!")
        logger.info("Production-ready storage management for travel industry!")
    
    def generate_storage_class(self, storage_class: StorageClass, provider: str = "aws") -> str:
        """Generate Kubernetes StorageClass manifest"""
        
        provider_config = self.storage_providers.get(provider, {})
        storage_config = provider_config.get("storage_classes", {}).get(storage_class, {})
        
        if provider == "aws":
            provisioner = "ebs.csi.aws.com"
            parameters = {
                "type": storage_config.get("type", "gp2"),
                "iops": str(storage_config.get("iops", 100)),
                "throughput": str(storage_config.get("throughput", 125)),
                "encrypted": "true"
            }
        elif provider == "azure":
            provisioner = "disk.csi.azure.com"
            parameters = {
                "storageaccounttype": storage_config.get("type", "StandardSSD_LRS"),
                "kind": "Managed"
            }
        elif provider == "gcp":
            provisioner = "pd.csi.storage.gke.io"
            parameters = {
                "type": storage_config.get("type", "pd-standard"),
                "replication-type": "regional-pd"
            }
        else:
            # Default local storage
            provisioner = "kubernetes.io/no-provisioner"
            parameters = {}
        
        storage_class_manifest = {
            "apiVersion": "storage.k8s.io/v1",
            "kind": "StorageClass",
            "metadata": {
                "name": f"makemytrip-{storage_class.value}",
                "labels": {
                    "company": "makemytrip",
                    "storage-tier": storage_class.value,
                    "provider": provider
                },
                "annotations": {
                    "storageclass.kubernetes.io/is-default-class": "false",
                    "storage.makemytrip.com/cost-per-gb": str(storage_config.get("cost_per_gb_month", 0)),
                    "storage.makemytrip.com/iops": str(storage_config.get("iops", 100)),
                    "storage.makemytrip.com/throughput": str(storage_config.get("throughput", 125))
                }
            },
            "provisioner": provisioner,
            "parameters": parameters,
            "reclaimPolicy": "Retain",  # Don't delete data automatically
            "allowVolumeExpansion": True,
            "volumeBindingMode": "WaitForFirstConsumer"
        }
        
        return yaml.dump(storage_class_manifest, default_flow_style=False)
    
    def generate_persistent_volume_claim(self, requirement: StorageRequirement, 
                                       namespace: str = "makemytrip-prod") -> str:
        """Generate PersistentVolumeClaim for service storage requirement"""
        
        pvc_name = f"{requirement.service_name}-{requirement.volume_type.value}-pvc"
        
        pvc_manifest = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": pvc_name,
                "namespace": namespace,
                "labels": {
                    "app": requirement.service_name,
                    "volume-type": requirement.volume_type.value,
                    "storage-class": requirement.storage_class.value,
                    "company": "makemytrip"
                },
                "annotations": {
                    "volume.beta.kubernetes.io/storage-class": f"makemytrip-{requirement.storage_class.value}",
                    "storage.makemytrip.com/backup-required": str(requirement.backup_required),
                    "storage.makemytrip.com/retention-days": str(requirement.retention_days),
                    "storage.makemytrip.com/encryption-required": str(requirement.encryption_required),
                    "storage.makemytrip.com/performance-tier": requirement.performance_tier
                }
            },
            "spec": {
                "accessModes": [requirement.access_mode.value],
                "resources": {
                    "requests": {
                        "storage": f"{requirement.size_gb}Gi"
                    }
                },
                "storageClassName": f"makemytrip-{requirement.storage_class.value}"
            }
        }
        
        return yaml.dump(pvc_manifest, default_flow_style=False)
    
    def generate_deployment_with_storage(self, service_name: str, namespace: str = "makemytrip-prod") -> str:
        """Generate Deployment with attached storage volumes"""
        
        if service_name not in self.service_storage_requirements:
            logger.error(f"No storage requirements found for service: {service_name}")
            return ""
        
        storage_reqs = self.service_storage_requirements[service_name]
        
        # Prepare volume mounts and volumes
        volume_mounts = []
        volumes = []
        
        for volume_name, requirement in storage_reqs.items():
            pvc_name = f"{requirement.service_name}-{requirement.volume_type.value}-pvc"
            
            # Volume mount configuration
            mount_path = self.get_mount_path(requirement.volume_type)
            volume_mounts.append({
                "name": volume_name,
                "mountPath": mount_path,
                "readOnly": requirement.volume_type == VolumeType.MEDIA and requirement.access_mode == AccessMode.READ_ONLY_MANY
            })
            
            # Volume configuration
            volumes.append({
                "name": volume_name,
                "persistentVolumeClaim": {
                    "claimName": pvc_name
                }
            })
        
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": service_name,
                "namespace": namespace,
                "labels": {
                    "app": service_name,
                    "company": "makemytrip",
                    "tier": "production"
                }
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_name,
                            "company": "makemytrip"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": service_name,
                            "image": f"makemytrip/{service_name}:latest",
                            "ports": [{"containerPort": 8080}],
                            "volumeMounts": volume_mounts,
                            "env": [
                                {"name": "SERVICE_NAME", "value": service_name},
                                {"name": "STORAGE_ROOT", "value": "/data"}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "250m",
                                    "memory": "512Mi"
                                },
                                "limits": {
                                    "cpu": "1000m",
                                    "memory": "2Gi"
                                }
                            }
                        }],
                        "volumes": volumes,
                        "securityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 1000,
                            "fsGroup": 2000
                        }
                    }
                }
            }
        }
        
        return yaml.dump(deployment_manifest, default_flow_style=False)
    
    def get_mount_path(self, volume_type: VolumeType) -> str:
        """Get mount path for different volume types"""
        
        mount_paths = {
            VolumeType.DATABASE: "/data/db",
            VolumeType.LOGS: "/data/logs",
            VolumeType.CACHE: "/data/cache",
            VolumeType.MEDIA: "/data/media",
            VolumeType.BACKUP: "/data/backup",
            VolumeType.TEMP: "/tmp/data"
        }
        
        return mount_paths.get(volume_type, "/data")
    
    def generate_backup_cronjob(self, requirement: StorageRequirement, namespace: str = "makemytrip-prod") -> str:
        """Generate CronJob for automated backups"""
        
        if not requirement.backup_required:
            return ""
        
        backup_strategy = self.backup_strategies.get(requirement.volume_type, {})
        frequency = backup_strategy.get("frequency", "daily")
        
        # Determine cron schedule
        if frequency == "hourly":
            schedule = "0 * * * *"
        elif frequency == "daily":
            schedule = "0 2 * * *"  # 2 AM IST
        elif frequency == "weekly":
            schedule = "0 2 * * 0"  # Sunday 2 AM
        else:
            return ""  # No backup needed
        
        backup_job_name = f"{requirement.service_name}-{requirement.volume_type.value}-backup"
        pvc_name = f"{requirement.service_name}-{requirement.volume_type.value}-pvc"
        
        cronjob_manifest = {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": backup_job_name,
                "namespace": namespace,
                "labels": {
                    "app": requirement.service_name,
                    "backup-type": requirement.volume_type.value,
                    "company": "makemytrip"
                }
            },
            "spec": {
                "schedule": schedule,
                "timeZone": "Asia/Kolkata",
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [{
                                    "name": "backup-container",
                                    "image": "makemytrip/backup-tool:latest",
                                    "command": ["/bin/sh"],
                                    "args": [
                                        "-c",
                                        f"""
                                        echo "Starting backup for {requirement.service_name}-{requirement.volume_type.value}"
                                        BACKUP_FILE="/backup/{requirement.service_name}-{requirement.volume_type.value}-$(date +%Y%m%d_%H%M%S).tar.gz"
                                        tar -czf $BACKUP_FILE -C /data .
                                        echo "Backup completed: $BACKUP_FILE"
                                        
                                        # Upload to cloud storage (AWS S3)
                                        aws s3 cp $BACKUP_FILE s3://makemytrip-backups/{requirement.service_name}/{requirement.volume_type.value}/
                                        
                                        # Cleanup local backup file
                                        rm $BACKUP_FILE
                                        
                                        echo "Backup uploaded and local file cleaned"
                                        """
                                    ],
                                    "volumeMounts": [
                                        {
                                            "name": "data-volume",
                                            "mountPath": "/data",
                                            "readOnly": True
                                        },
                                        {
                                            "name": "backup-volume",
                                            "mountPath": "/backup"
                                        }
                                    ],
                                    "env": [
                                        {"name": "AWS_DEFAULT_REGION", "value": "ap-south-1"},
                                        {"name": "BACKUP_RETENTION_DAYS", "value": str(requirement.retention_days)}
                                    ]
                                }],
                                "volumes": [
                                    {
                                        "name": "data-volume",
                                        "persistentVolumeClaim": {
                                            "claimName": pvc_name
                                        }
                                    },
                                    {
                                        "name": "backup-volume",
                                        "emptyDir": {}
                                    }
                                ],
                                "restartPolicy": "OnFailure"
                            }
                        }
                    }
                },
                "successfulJobsHistoryLimit": 3,
                "failedJobsHistoryLimit": 1
            }
        }
        
        return yaml.dump(cronjob_manifest, default_flow_style=False)
    
    def generate_volume_snapshot_class(self, provider: str = "aws") -> str:
        """Generate VolumeSnapshotClass for point-in-time snapshots"""
        
        if provider == "aws":
            driver = "ebs.csi.aws.com"
        elif provider == "azure":
            driver = "disk.csi.azure.com"
        elif provider == "gcp":
            driver = "pd.csi.storage.gke.io"
        else:
            driver = "hostpath.csi.k8s.io"
        
        snapshot_class_manifest = {
            "apiVersion": "snapshot.storage.k8s.io/v1",
            "kind": "VolumeSnapshotClass",
            "metadata": {
                "name": f"makemytrip-snapshot-class-{provider}",
                "labels": {
                    "company": "makemytrip",
                    "provider": provider
                },
                "annotations": {
                    "snapshot.storage.kubernetes.io/is-default-class": "true"
                }
            },
            "driver": driver,
            "deletionPolicy": "Retain"
        }
        
        return yaml.dump(snapshot_class_manifest, default_flow_style=False)
    
    def calculate_storage_costs(self, provider: str = "aws") -> Dict[str, float]:
        """Calculate monthly storage costs for all services"""
        
        provider_config = self.storage_providers.get(provider, {})
        storage_classes = provider_config.get("storage_classes", {})
        
        total_costs = {}
        overall_cost = 0.0
        
        for service_name, storage_reqs in self.service_storage_requirements.items():
            service_cost = 0.0
            
            for volume_name, requirement in storage_reqs.items():
                storage_config = storage_classes.get(requirement.storage_class, {})
                cost_per_gb = storage_config.get("cost_per_gb_month", 0.05)
                
                volume_cost = requirement.size_gb * cost_per_gb
                service_cost += volume_cost
                
                logger.info(f"   {service_name}-{volume_name}: {requirement.size_gb}GB × ${cost_per_gb:.3f} = ${volume_cost:.2f}/month")
            
            total_costs[service_name] = service_cost
            overall_cost += service_cost
        
        total_costs["total"] = overall_cost
        total_costs["total_inr"] = overall_cost * 83  # USD to INR conversion
        
        return total_costs
    
    def generate_storage_monitoring_dashboard(self) -> Dict[str, Any]:
        """Generate storage monitoring configuration"""
        
        dashboard_config = {
            "dashboard": {
                "title": "MakeMyTrip Storage Orchestration",
                "tags": ["makemytrip", "storage", "kubernetes"],
                "timezone": "Asia/Kolkata",
                "panels": [
                    {
                        "title": "Storage Usage by Service",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "sum by (persistentvolumeclaim) (kubelet_volume_stats_used_bytes / kubelet_volume_stats_capacity_bytes * 100)",
                                "legendFormat": "{{persistentvolumeclaim}}"
                            }
                        ]
                    },
                    {
                        "title": "Storage IOPS",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(container_fs_reads_total[5m]) + rate(container_fs_writes_total[5m])",
                                "legendFormat": "{{container}}"
                            }
                        ]
                    },
                    {
                        "title": "Backup Status",
                        "type": "table",
                        "targets": [
                            {
                                "expr": "kube_cronjob_status_last_successful_time",
                                "legendFormat": "{{cronjob}}"
                            }
                        ]
                    },
                    {
                        "title": "Storage Costs (Monthly)",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": "sum(storage_cost_per_gb * storage_usage_gb)",
                                "legendFormat": "Total Cost USD"
                            }
                        ]
                    }
                ]
            }
        }
        
        return dashboard_config
    
    def create_complete_storage_stack(self, output_dir: str, provider: str = "aws"):
        """Create complete storage orchestration configuration"""
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate StorageClasses
        storage_classes_dir = os.path.join(output_dir, "storage-classes")
        os.makedirs(storage_classes_dir, exist_ok=True)
        
        for storage_class in StorageClass:
            if storage_class in self.storage_providers[provider]["storage_classes"]:
                sc_yaml = self.generate_storage_class(storage_class, provider)
                with open(os.path.join(storage_classes_dir, f"{storage_class.value}-storageclass.yaml"), "w") as f:
                    f.write(sc_yaml)
        
        # Generate PVCs and Deployments
        pvcs_dir = os.path.join(output_dir, "persistent-volume-claims")
        deployments_dir = os.path.join(output_dir, "deployments")
        backups_dir = os.path.join(output_dir, "backup-jobs")
        
        os.makedirs(pvcs_dir, exist_ok=True)
        os.makedirs(deployments_dir, exist_ok=True)
        os.makedirs(backups_dir, exist_ok=True)
        
        for service_name, storage_reqs in self.service_storage_requirements.items():
            # Generate PVCs
            for volume_name, requirement in storage_reqs.items():
                pvc_yaml = self.generate_persistent_volume_claim(requirement)
                with open(os.path.join(pvcs_dir, f"{service_name}-{requirement.volume_type.value}-pvc.yaml"), "w") as f:
                    f.write(pvc_yaml)
                
                # Generate backup jobs
                backup_yaml = self.generate_backup_cronjob(requirement)
                if backup_yaml:
                    with open(os.path.join(backups_dir, f"{service_name}-{requirement.volume_type.value}-backup.yaml"), "w") as f:
                        f.write(backup_yaml)
            
            # Generate deployment
            deployment_yaml = self.generate_deployment_with_storage(service_name)
            with open(os.path.join(deployments_dir, f"{service_name}-deployment.yaml"), "w") as f:
                f.write(deployment_yaml)
        
        # Generate VolumeSnapshotClass
        snapshot_class_yaml = self.generate_volume_snapshot_class(provider)
        with open(os.path.join(output_dir, "volume-snapshot-class.yaml"), "w") as f:
            f.write(snapshot_class_yaml)
        
        # Generate cost analysis
        costs = self.calculate_storage_costs(provider)
        with open(os.path.join(output_dir, "storage-costs.json"), "w") as f:
            json.dump(costs, f, indent=2)
        
        # Generate monitoring dashboard
        dashboard = self.generate_storage_monitoring_dashboard()
        with open(os.path.join(output_dir, "grafana-dashboard.json"), "w") as f:
            json.dump(dashboard, f, indent=2)
        
        logger.info(f"✅ Complete storage stack created in {output_dir}")

def main():
    """Demonstration of MakeMyTrip storage orchestration"""
    
    print("✈️ MakeMyTrip Storage Orchestration Demo")
    print("Production-ready storage management for Indian travel industry")
    print("=" * 60)
    
    # Initialize storage orchestrator
    storage_orchestrator = MakeMyTripStorageOrchestrator()
    
    print("💾 Service Storage Requirements:")
    for service_name, storage_reqs in storage_orchestrator.service_storage_requirements.items():
        print(f"\\n📦 {service_name.upper()}:")
        total_storage = 0
        for volume_name, requirement in storage_reqs.items():
            print(f"   {volume_name}:")
            print(f"     Type: {requirement.volume_type.value}")
            print(f"     Class: {requirement.storage_class.value}")
            print(f"     Size: {requirement.size_gb}GB")
            print(f"     Backup: {'Yes' if requirement.backup_required else 'No'}")
            print(f"     Retention: {requirement.retention_days} days")
            total_storage += requirement.size_gb
        print(f"   Total Storage: {total_storage}GB")
    
    print("\\n💰 Storage Cost Analysis:")
    costs = storage_orchestrator.calculate_storage_costs("aws")
    
    for service_name, cost in costs.items():
        if service_name not in ["total", "total_inr"]:
            print(f"   {service_name}: ${cost:.2f}/month")
    
    print(f"\\n   TOTAL: ${costs['total']:.2f}/month (₹{costs['total_inr']:.2f}/month)")
    
    print("\\n📋 Generating Storage Configuration...")
    
    output_dir = "/tmp/makemytrip_storage_orchestration"
    storage_orchestrator.create_complete_storage_stack(output_dir, "aws")
    
    print(f"\\n📂 Storage files created in: {output_dir}")
    print("\\n📁 Generated Components:")
    
    for root, dirs, files in os.walk(output_dir):
        level = root.replace(output_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    print("\\n✅ Storage orchestration demonstration completed!")

if __name__ == "__main__":
    main()

# Production Deployment Guide:
"""
# 1. Deploy storage classes:
kubectl apply -f /tmp/makemytrip_storage_orchestration/storage-classes/

# 2. Create persistent volume claims:
kubectl apply -f /tmp/makemytrip_storage_orchestration/persistent-volume-claims/

# 3. Deploy applications with storage:
kubectl apply -f /tmp/makemytrip_storage_orchestration/deployments/

# 4. Set up backup jobs:
kubectl apply -f /tmp/makemytrip_storage_orchestration/backup-jobs/

# 5. Configure volume snapshots:
kubectl apply -f /tmp/makemytrip_storage_orchestration/volume-snapshot-class.yaml

# 6. Monitor storage usage:
kubectl get pv,pvc -A
kubectl top pods --containers

# 7. Create volume snapshot:
kubectl apply -f - <<EOF
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: flight-search-cache-snapshot
spec:
  volumeSnapshotClassName: makemytrip-snapshot-class-aws
  source:
    persistentVolumeClaimName: flight-search-cache-pvc
EOF

# 8. Check backup job status:
kubectl get cronjobs -A
kubectl get jobs -A

# 9. Restore from backup:
# Create new PVC from snapshot
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: flight-search-cache-restored
spec:
  dataSource:
    name: flight-search-cache-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
  storageClassName: makemytrip-fast-ssd
EOF

# 10. Storage cost monitoring:
# Set up alerts for storage usage and costs
# Regular storage cleanup and optimization
"""