# Episode 143: MLOps and AI Infrastructure - AI & ML Systems in Distributed Computing

## Abstract

MLOps represents the convergence of machine learning, DevOps practices, and distributed systems engineering. As ML models transition from research prototypes to production systems serving millions of users, robust infrastructure, automated pipelines, and sophisticated orchestration become critical. This episode explores the distributed systems principles underlying modern MLOps platforms, examining how companies like Uber, Airbnb, and Netflix have built scalable ML infrastructure.

We'll dive deep into ML pipeline orchestration, model versioning and deployment strategies, A/B testing frameworks for ML systems, and the distributed architectures that enable continuous integration and delivery of machine learning models at scale. Through detailed analysis of production systems like Uber's Michelangelo, Airbnb's Bighead, and Netflix's Metaflow, we'll understand how distributed systems principles enable reliable, scalable ML operations.

## Table of Contents

1. Foundations of MLOps and Distributed ML Infrastructure
2. ML Pipeline Orchestration and Workflow Management
3. Distributed Model Training and Experiment Management
4. Model Versioning, Registry, and Artifact Management
5. Continuous Integration and Deployment for ML
6. A/B Testing and Experimentation Platforms
7. Model Serving and Inference Infrastructure
8. Monitoring, Observability, and ML System Health
9. Production MLOps Platforms Analysis
10. Distributed Resource Management for ML Workloads
11. Future Directions in ML Infrastructure

## 1. Foundations of MLOps and Distributed ML Infrastructure

MLOps extends traditional DevOps practices to accommodate the unique challenges of machine learning systems: data dependencies, model drift, experimental nature of ML development, and the need for continuous retraining and deployment.

### Core MLOps Principles in Distributed Systems

**Scalability**: ML workloads span from data preprocessing (terabytes of data) to model training (distributed across hundreds of GPUs) to inference (millions of requests per second).

**Reproducibility**: Exact reproduction of ML experiments requires versioning of code, data, models, and infrastructure state across distributed systems.

**Automation**: End-to-end automation of ML pipelines from data ingestion to model deployment, including distributed training orchestration and multi-region deployment.

**Monitoring**: Comprehensive observability across the ML lifecycle, including data quality, model performance, and system health in distributed environments.

### Distributed ML Infrastructure Architecture

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
import asyncio
import uuid
import json
import logging
from datetime import datetime, timedelta
import numpy as np
import torch
import kubernetes
from kubernetes import client, config

@dataclass
class MLWorkflowSpec:
    """Specification for ML workflow execution"""
    workflow_id: str
    name: str
    steps: List['MLStep']
    dependencies: Dict[str, List[str]]
    resource_requirements: Dict[str, Any]
    scheduling_constraints: Dict[str, Any]
    retry_policy: Dict[str, Any]
    
    def validate(self) -> bool:
        """Validate workflow specification"""
        # Check for circular dependencies
        if self._has_circular_dependencies():
            raise ValueError("Circular dependencies detected in workflow")
        
        # Validate resource requirements
        for step in self.steps:
            if not self._validate_resources(step.resource_requirements):
                raise ValueError(f"Invalid resource requirements for step {step.name}")
        
        return True
    
    def _has_circular_dependencies(self) -> bool:
        """Check for circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in self.dependencies.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_name in self.dependencies:
            if step_name not in visited:
                if dfs(step_name):
                    return True
        
        return False

@dataclass
class MLStep:
    """Individual step in ML workflow"""
    step_id: str
    name: str
    step_type: str  # 'data_preprocessing', 'training', 'evaluation', 'deployment'
    docker_image: str
    command: List[str]
    environment_variables: Dict[str, str]
    resource_requirements: Dict[str, Any]
    input_artifacts: List[str]
    output_artifacts: List[str]
    parameters: Dict[str, Any]
    
    def to_kubernetes_job(self) -> client.V1Job:
        """Convert ML step to Kubernetes Job specification"""
        
        # Container specification
        container = client.V1Container(
            name=self.name,
            image=self.docker_image,
            command=self.command,
            env=[client.V1EnvVar(name=k, value=str(v)) 
                 for k, v in self.environment_variables.items()],
            resources=client.V1ResourceRequirements(
                requests=self.resource_requirements.get('requests', {}),
                limits=self.resource_requirements.get('limits', {})
            ),
            volume_mounts=[
                client.V1VolumeMount(
                    name='shared-storage',
                    mount_path='/shared'
                )
            ]
        )
        
        # Pod template
        pod_template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                labels={'step': self.name, 'workflow': 'ml-pipeline'}
            ),
            spec=client.V1PodSpec(
                containers=[container],
                restart_policy='Never',
                volumes=[
                    client.V1Volume(
                        name='shared-storage',
                        persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                            claim_name='ml-shared-storage'
                        )
                    )
                ]
            )
        )
        
        # Job specification
        job_spec = client.V1JobSpec(
            template=pod_template,
            backoff_limit=self.resource_requirements.get('retry_limit', 3),
            ttl_seconds_after_finished=86400  # 24 hours
        )
        
        # Job object
        job = client.V1Job(
            api_version='batch/v1',
            kind='Job',
            metadata=client.V1ObjectMeta(
                name=f"{self.name}-{uuid.uuid4().hex[:8]}",
                labels={'step': self.name}
            ),
            spec=job_spec
        )
        
        return job

class MLOrchestrator:
    """
    Distributed ML workflow orchestrator built on Kubernetes
    """
    
    def __init__(self, namespace: str = 'mlops', 
                 storage_class: str = 'fast-ssd'):
        self.namespace = namespace
        self.storage_class = storage_class
        
        # Initialize Kubernetes client
        try:
            config.load_incluster_config()  # Running inside cluster
        except:
            config.load_kube_config()  # Running outside cluster
        
        self.k8s_batch = client.BatchV1Api()
        self.k8s_core = client.CoreV1Api()
        self.k8s_apps = client.AppsV1Api()
        
        # Workflow state management
        self.active_workflows: Dict[str, 'WorkflowExecution'] = {}
        self.step_status: Dict[str, str] = {}  # step_id -> status
        
        # Resource pool management
        self.resource_pool = ResourcePool()
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def execute_workflow(self, workflow_spec: MLWorkflowSpec) -> str:
        """
        Execute ML workflow with distributed orchestration
        
        Returns:
            Workflow execution ID
        """
        
        # Validate workflow
        workflow_spec.validate()
        
        # Create workflow execution
        execution = WorkflowExecution(
            execution_id=str(uuid.uuid4()),
            workflow_spec=workflow_spec,
            start_time=datetime.now(),
            status='running'
        )
        
        self.active_workflows[execution.execution_id] = execution
        
        try:
            # Setup shared storage for workflow
            await self._setup_workflow_storage(execution)
            
            # Execute workflow steps according to dependency graph
            await self._execute_workflow_graph(execution)
            
            execution.status = 'completed'
            execution.end_time = datetime.now()
            
        except Exception as e:
            execution.status = 'failed'
            execution.error = str(e)
            execution.end_time = datetime.now()
            self.logger.error(f"Workflow {execution.execution_id} failed: {e}")
            raise
        
        return execution.execution_id
    
    async def _execute_workflow_graph(self, execution: 'WorkflowExecution'):
        """Execute workflow steps respecting dependency constraints"""
        
        workflow = execution.workflow_spec
        completed_steps = set()
        running_steps = {}
        
        while len(completed_steps) < len(workflow.steps):
            # Find ready steps (all dependencies completed)
            ready_steps = []
            for step in workflow.steps:
                if step.step_id not in completed_steps and step.step_id not in running_steps:
                    dependencies = workflow.dependencies.get(step.step_id, [])
                    if all(dep in completed_steps for dep in dependencies):
                        ready_steps.append(step)
            
            # Launch ready steps
            for step in ready_steps:
                job_future = asyncio.create_task(self._execute_step(step))
                running_steps[step.step_id] = job_future
                self.logger.info(f"Started step {step.name}")
            
            # Check for completed steps
            completed_in_iteration = []
            for step_id, job_future in running_steps.items():
                if job_future.done():
                    try:
                        await job_future  # Get result and handle exceptions
                        completed_steps.add(step_id)
                        completed_in_iteration.append(step_id)
                        self.logger.info(f"Completed step {step_id}")
                    except Exception as e:
                        self.logger.error(f"Step {step_id} failed: {e}")
                        raise
            
            # Remove completed steps from running
            for step_id in completed_in_iteration:
                del running_steps[step_id]
            
            # Wait before next iteration
            if running_steps:
                await asyncio.sleep(5)
            elif not ready_steps:
                # Deadlock detection
                remaining_steps = [s.step_id for s in workflow.steps 
                                 if s.step_id not in completed_steps]
                raise RuntimeError(f"Workflow deadlock: remaining steps {remaining_steps}")
    
    async def _execute_step(self, step: MLStep) -> Dict[str, Any]:
        """Execute individual ML step as Kubernetes job"""
        
        # Check resource availability
        if not await self.resource_pool.reserve_resources(step.resource_requirements):
            raise ResourceUnavailableException(
                f"Insufficient resources for step {step.name}"
            )
        
        try:
            # Create Kubernetes job
            job = step.to_kubernetes_job()
            
            # Submit job
            created_job = self.k8s_batch.create_namespaced_job(
                namespace=self.namespace,
                body=job
            )
            
            job_name = created_job.metadata.name
            
            # Wait for job completion
            result = await self._wait_for_job_completion(job_name)
            
            # Collect outputs and logs
            outputs = await self._collect_step_outputs(step, job_name)
            
            return {
                'step_id': step.step_id,
                'status': 'completed',
                'outputs': outputs,
                'job_name': job_name
            }
            
        finally:
            # Release reserved resources
            await self.resource_pool.release_resources(step.resource_requirements)
    
    async def _wait_for_job_completion(self, job_name: str, 
                                     timeout: int = 3600) -> Dict[str, Any]:
        """Wait for Kubernetes job to complete"""
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            # Check job status
            job = self.k8s_batch.read_namespaced_job(
                name=job_name,
                namespace=self.namespace
            )
            
            if job.status.succeeded:
                return {'status': 'succeeded', 'job': job}
            elif job.status.failed:
                # Get failure details
                pods = self.k8s_core.list_namespaced_pod(
                    namespace=self.namespace,
                    label_selector=f'job-name={job_name}'
                )
                
                failure_reason = "Unknown failure"
                if pods.items:
                    pod = pods.items[0]
                    if pod.status.container_statuses:
                        container_status = pod.status.container_statuses[0]
                        if container_status.state.terminated:
                            failure_reason = container_status.state.terminated.reason
                
                raise JobExecutionException(f"Job {job_name} failed: {failure_reason}")
            
            await asyncio.sleep(10)  # Poll every 10 seconds
        
        raise TimeoutException(f"Job {job_name} timed out after {timeout} seconds")
    
    async def _setup_workflow_storage(self, execution: 'WorkflowExecution'):
        """Setup persistent storage for workflow execution"""
        
        # Create PVC for workflow data
        pvc_name = f"ml-workflow-{execution.execution_id[:8]}"
        
        pvc = client.V1PersistentVolumeClaim(
            api_version='v1',
            kind='PersistentVolumeClaim',
            metadata=client.V1ObjectMeta(name=pvc_name),
            spec=client.V1PersistentVolumeClaimSpec(
                access_modes=['ReadWriteMany'],
                resources=client.V1ResourceRequirements(
                    requests={'storage': '100Gi'}
                ),
                storage_class=self.storage_class
            )
        )
        
        self.k8s_core.create_namespaced_persistent_volume_claim(
            namespace=self.namespace,
            body=pvc
        )
        
        execution.storage_claim = pvc_name

@dataclass
class WorkflowExecution:
    """Represents an executing ML workflow"""
    execution_id: str
    workflow_spec: MLWorkflowSpec
    start_time: datetime
    status: str
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    storage_claim: Optional[str] = None
    step_results: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.step_results is None:
            self.step_results = {}

class ResourcePool:
    """Manages distributed compute resources for ML workloads"""
    
    def __init__(self):
        self.available_resources = {
            'cpu': 1000,  # CPU cores
            'memory': 4000,  # GB
            'gpu': 100,   # GPU units
            'storage': 10000  # GB
        }
        self.reserved_resources = {
            'cpu': 0,
            'memory': 0,
            'gpu': 0,
            'storage': 0
        }
        self.resource_lock = asyncio.Lock()
    
    async def reserve_resources(self, requirements: Dict[str, Any]) -> bool:
        """Reserve resources for step execution"""
        async with self.resource_lock:
            # Check availability
            for resource, amount in requirements.items():
                if resource in self.available_resources:
                    available = (self.available_resources[resource] - 
                               self.reserved_resources[resource])
                    if available < amount:
                        return False
            
            # Reserve resources
            for resource, amount in requirements.items():
                if resource in self.reserved_resources:
                    self.reserved_resources[resource] += amount
            
            return True
    
    async def release_resources(self, requirements: Dict[str, Any]):
        """Release reserved resources"""
        async with self.resource_lock:
            for resource, amount in requirements.items():
                if resource in self.reserved_resources:
                    self.reserved_resources[resource] -= amount
                    self.reserved_resources[resource] = max(
                        0, self.reserved_resources[resource]
                    )

# Custom exceptions
class ResourceUnavailableException(Exception):
    pass

class JobExecutionException(Exception):
    pass

class TimeoutException(Exception):
    pass
```

### ML Pipeline Definition and DAG Management

Modern ML pipelines are complex directed acyclic graphs (DAGs) with sophisticated dependency management:

```python
from typing import Callable, Any
import networkx as nx
import matplotlib.pyplot as plt

class MLPipelineDAG:
    """
    ML Pipeline represented as Directed Acyclic Graph
    with advanced scheduling and optimization capabilities
    """
    
    def __init__(self, pipeline_name: str):
        self.pipeline_name = pipeline_name
        self.graph = nx.DiGraph()
        self.step_definitions = {}
        self.execution_history = []
        
        # Pipeline metadata
        self.created_at = datetime.now()
        self.version = "1.0.0"
        self.tags = set()
    
    def add_step(self, step: MLStep, dependencies: List[str] = None):
        """Add step to pipeline DAG"""
        
        # Add node to graph
        self.graph.add_node(
            step.step_id,
            name=step.name,
            step_type=step.step_type,
            resource_requirements=step.resource_requirements,
            estimated_duration=self._estimate_step_duration(step),
            retry_count=0
        )
        
        # Add dependencies as edges
        if dependencies:
            for dep in dependencies:
                if dep not in self.graph:
                    raise ValueError(f"Dependency {dep} not found in pipeline")
                self.graph.add_edge(dep, step.step_id)
        
        self.step_definitions[step.step_id] = step
    
    def optimize_execution_plan(self) -> List[List[str]]:
        """
        Optimize pipeline execution plan using topological sorting
        and resource-aware scheduling
        
        Returns:
            List of execution phases, each containing parallelizable steps
        """
        
        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Pipeline contains cycles")
        
        # Generate topological ordering
        topo_order = list(nx.topological_sort(self.graph))
        
        # Create execution phases
        execution_phases = []
        remaining_steps = set(topo_order)
        
        while remaining_steps:
            # Find steps with no remaining dependencies
            ready_steps = []
            for step in remaining_steps:
                dependencies = set(self.graph.predecessors(step))
                if not dependencies.intersection(remaining_steps):
                    ready_steps.append(step)
            
            if not ready_steps:
                raise RuntimeError("No ready steps found - possible cycle")
            
            # Apply resource-based grouping
            resource_groups = self._group_by_resources(ready_steps)
            
            for group in resource_groups:
                execution_phases.append(group)
                remaining_steps.difference_update(group)
        
        return execution_phases
    
    def _group_by_resources(self, steps: List[str]) -> List[List[str]]:
        """Group steps by resource compatibility for parallel execution"""
        
        groups = []
        remaining_steps = steps.copy()
        
        while remaining_steps:
            # Start new group with first remaining step
            current_group = [remaining_steps[0]]
            current_resources = self.graph.nodes[remaining_steps[0]]['resource_requirements']
            remaining_steps.remove(remaining_steps[0])
            
            # Add compatible steps to current group
            compatible_steps = []
            for step in remaining_steps:
                step_resources = self.graph.nodes[step]['resource_requirements']
                if self._are_resources_compatible(current_resources, step_resources):
                    compatible_steps.append(step)
            
            current_group.extend(compatible_steps)
            for step in compatible_steps:
                remaining_steps.remove(step)
            
            groups.append(current_group)
        
        return groups
    
    def _are_resources_compatible(self, resources1: Dict, resources2: Dict) -> bool:
        """Check if two resource requirements can be satisfied simultaneously"""
        
        # Simple heuristic: check if combined requirements don't exceed limits
        combined_cpu = resources1.get('cpu', 0) + resources2.get('cpu', 0)
        combined_memory = resources1.get('memory', 0) + resources2.get('memory', 0)
        combined_gpu = resources1.get('gpu', 0) + resources2.get('gpu', 0)
        
        # Assume cluster limits (in practice, get from resource manager)
        cpu_limit = 64
        memory_limit = 256  # GB
        gpu_limit = 8
        
        return (combined_cpu <= cpu_limit and 
                combined_memory <= memory_limit and 
                combined_gpu <= gpu_limit)
    
    def estimate_total_duration(self, execution_plan: List[List[str]] = None) -> float:
        """Estimate total pipeline execution time"""
        
        if execution_plan is None:
            execution_plan = self.optimize_execution_plan()
        
        total_duration = 0.0
        
        for phase in execution_plan:
            # Phase duration is maximum of all steps in phase (parallel execution)
            phase_duration = max(
                self.graph.nodes[step]['estimated_duration'] for step in phase
            )
            total_duration += phase_duration
        
        return total_duration
    
    def _estimate_step_duration(self, step: MLStep) -> float:
        """Estimate step execution duration based on historical data"""
        
        # In practice, this would use historical execution data
        # For now, use heuristics based on step type and resources
        
        base_durations = {
            'data_preprocessing': 300,  # 5 minutes
            'training': 3600,          # 1 hour
            'evaluation': 600,         # 10 minutes
            'deployment': 300          # 5 minutes
        }
        
        base_duration = base_durations.get(step.step_type, 600)
        
        # Scale based on resource requirements
        cpu_factor = step.resource_requirements.get('cpu', 1) / 4  # Baseline: 4 CPUs
        memory_factor = step.resource_requirements.get('memory', 8) / 8  # Baseline: 8GB
        
        scaling_factor = max(cpu_factor, memory_factor)
        
        return base_duration / scaling_factor
    
    def visualize_pipeline(self, save_path: str = None):
        """Visualize pipeline DAG"""
        
        plt.figure(figsize=(12, 8))
        
        # Create layout
        pos = nx.spring_layout(self.graph, k=2, iterations=50)
        
        # Color nodes by step type
        color_map = {
            'data_preprocessing': 'lightblue',
            'training': 'lightgreen',
            'evaluation': 'lightyellow',
            'deployment': 'lightcoral'
        }
        
        node_colors = [color_map.get(
            self.graph.nodes[node].get('step_type', 'unknown'), 'lightgray'
        ) for node in self.graph.nodes()]
        
        # Draw graph
        nx.draw(self.graph, pos, 
                node_color=node_colors,
                with_labels=True,
                node_size=2000,
                font_size=8,
                font_weight='bold',
                arrows=True,
                arrowsize=20)
        
        plt.title(f"ML Pipeline: {self.pipeline_name}")
        plt.axis('off')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.show()
    
    def validate_pipeline(self) -> List[str]:
        """Validate pipeline and return list of issues"""
        
        issues = []
        
        # Check for cycles
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            issues.append(f"Cycles detected: {cycles}")
        
        # Check for disconnected components
        if not nx.is_weakly_connected(self.graph):
            issues.append("Pipeline contains disconnected components")
        
        # Check resource requirements
        for step_id in self.graph.nodes():
            step = self.step_definitions[step_id]
            if not self._validate_step_resources(step):
                issues.append(f"Invalid resource requirements for step {step_id}")
        
        # Check for missing dependencies
        for step_id, step in self.step_definitions.items():
            for input_artifact in step.input_artifacts:
                if not self._has_producer(input_artifact, step_id):
                    issues.append(f"No producer found for artifact {input_artifact} in step {step_id}")
        
        return issues
    
    def _validate_step_resources(self, step: MLStep) -> bool:
        """Validate step resource requirements"""
        resources = step.resource_requirements
        
        # Check for required fields
        if 'cpu' not in resources or 'memory' not in resources:
            return False
        
        # Check for reasonable values
        if resources['cpu'] <= 0 or resources['memory'] <= 0:
            return False
        
        if resources.get('gpu', 0) < 0:
            return False
        
        return True
    
    def _has_producer(self, artifact: str, consumer_step: str) -> bool:
        """Check if artifact has a producer step"""
        
        for step_id, step in self.step_definitions.items():
            if step_id != consumer_step and artifact in step.output_artifacts:
                # Check if this producer runs before consumer
                if nx.has_path(self.graph, step_id, consumer_step):
                    return True
        
        return False
```

## 2. ML Pipeline Orchestration and Workflow Management

Distributed ML workflow orchestration requires sophisticated scheduling, resource management, and fault tolerance mechanisms.

### Advanced Workflow Scheduling

```python
import heapq
from enum import Enum
from dataclasses import dataclass, field
from typing import Set

class SchedulingPolicy(Enum):
    FIFO = "fifo"
    SHORTEST_JOB_FIRST = "sjf"
    PRIORITY = "priority"
    FAIR_SHARE = "fair_share"
    RESOURCE_AWARE = "resource_aware"

@dataclass
class WorkflowSchedulingRequest:
    """Request for workflow scheduling"""
    workflow_id: str
    priority: int
    estimated_duration: float
    resource_requirements: Dict[str, float]
    submission_time: datetime
    user_id: str
    team_id: str
    scheduling_constraints: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """Comparison for priority queue"""
        return self.priority > other.priority  # Higher priority first

class DistributedWorkflowScheduler:
    """
    Advanced distributed scheduler for ML workflows
    with multiple scheduling policies and resource awareness
    """
    
    def __init__(self, cluster_resources: Dict[str, float],
                 scheduling_policy: SchedulingPolicy = SchedulingPolicy.RESOURCE_AWARE):
        self.cluster_resources = cluster_resources
        self.available_resources = cluster_resources.copy()
        self.scheduling_policy = scheduling_policy
        
        # Scheduling queues
        self.pending_workflows: List[WorkflowSchedulingRequest] = []
        self.running_workflows: Dict[str, WorkflowSchedulingRequest] = {}
        self.completed_workflows: List[str] = []
        
        # Fair share tracking
        self.user_resource_usage: Dict[str, Dict[str, float]] = {}
        self.team_resource_quotas: Dict[str, Dict[str, float]] = {}
        
        # Performance metrics
        self.scheduling_metrics = {
            'total_workflows': 0,
            'average_wait_time': 0.0,
            'average_execution_time': 0.0,
            'resource_utilization': {},
            'fairness_index': 0.0
        }
        
        # Preemption support
        self.preemptable_workflows: Set[str] = set()
        
    async def schedule_workflow(self, request: WorkflowSchedulingRequest) -> bool:
        """
        Schedule workflow for execution
        
        Returns:
            True if scheduled immediately, False if queued
        """
        
        self.scheduling_metrics['total_workflows'] += 1
        
        # Check immediate scheduling possibility
        if self._can_schedule_immediately(request):
            await self._start_workflow(request)
            return True
        
        # Queue workflow based on scheduling policy
        if self.scheduling_policy == SchedulingPolicy.FIFO:
            self.pending_workflows.append(request)
        
        elif self.scheduling_policy == SchedulingPolicy.PRIORITY:
            heapq.heappush(self.pending_workflows, request)
        
        elif self.scheduling_policy == SchedulingPolicy.SHORTEST_JOB_FIRST:
            # Insert based on estimated duration
            insertion_point = 0
            for i, pending in enumerate(self.pending_workflows):
                if request.estimated_duration < pending.estimated_duration:
                    insertion_point = i
                    break
            else:
                insertion_point = len(self.pending_workflows)
            
            self.pending_workflows.insert(insertion_point, request)
        
        elif self.scheduling_policy == SchedulingPolicy.FAIR_SHARE:
            # Queue with fair share consideration
            fair_share_priority = self._calculate_fair_share_priority(request)
            request.priority = fair_share_priority
            heapq.heappush(self.pending_workflows, request)
        
        elif self.scheduling_policy == SchedulingPolicy.RESOURCE_AWARE:
            # Advanced resource-aware queuing
            await self._resource_aware_scheduling(request)
        
        return False
    
    def _can_schedule_immediately(self, request: WorkflowSchedulingRequest) -> bool:
        """Check if workflow can be scheduled immediately"""
        
        for resource, required in request.resource_requirements.items():
            if resource in self.available_resources:
                if self.available_resources[resource] < required:
                    return False
        
        # Check scheduling constraints
        constraints = request.scheduling_constraints
        
        if 'node_selector' in constraints:
            # Check node availability (simplified)
            required_nodes = constraints['node_selector']
            if not self._check_node_availability(required_nodes):
                return False
        
        if 'anti_affinity' in constraints:
            # Check anti-affinity constraints
            conflicting_workflows = constraints['anti_affinity']
            for workflow_id in self.running_workflows:
                if workflow_id in conflicting_workflows:
                    return False
        
        return True
    
    async def _resource_aware_scheduling(self, request: WorkflowSchedulingRequest):
        """Advanced resource-aware scheduling with preemption support"""
        
        # Try to find space by preempting lower priority workflows
        if await self._try_preemption(request):
            await self._start_workflow(request)
            return
        
        # Try resource fragmentation optimization
        if self._can_optimize_fragmentation(request):
            await self._optimize_and_schedule(request)
            return
        
        # Queue with smart positioning based on resource fit
        insertion_point = self._find_optimal_queue_position(request)
        self.pending_workflows.insert(insertion_point, request)
    
    async def _try_preemption(self, request: WorkflowSchedulingRequest) -> bool:
        """Try to preempt lower priority workflows to make space"""
        
        if request.priority < 5:  # Only high priority workflows can preempt
            return False
        
        # Find preemptable workflows
        candidates = []
        for workflow_id, running_workflow in self.running_workflows.items():
            if (workflow_id in self.preemptable_workflows and 
                running_workflow.priority < request.priority):
                candidates.append((workflow_id, running_workflow))
        
        # Sort by priority (lowest first)
        candidates.sort(key=lambda x: x[1].priority)
        
        # Calculate resources needed
        needed_resources = {}
        for resource, required in request.resource_requirements.items():
            if resource in self.available_resources:
                deficit = required - self.available_resources[resource]
                if deficit > 0:
                    needed_resources[resource] = deficit
        
        # Try to preempt enough workflows
        resources_freed = {r: 0.0 for r in needed_resources}
        workflows_to_preempt = []
        
        for workflow_id, workflow in candidates:
            workflows_to_preempt.append(workflow_id)
            
            for resource, usage in workflow.resource_requirements.items():
                if resource in resources_freed:
                    resources_freed[resource] += usage
            
            # Check if we have enough resources
            if all(resources_freed[r] >= needed_resources[r] 
                   for r in needed_resources):
                break
        
        if all(resources_freed[r] >= needed_resources[r] 
               for r in needed_resources):
            # Preempt selected workflows
            for workflow_id in workflows_to_preempt:
                await self._preempt_workflow(workflow_id)
            return True
        
        return False
    
    async def _preempt_workflow(self, workflow_id: str):
        """Preempt a running workflow"""
        
        if workflow_id not in self.running_workflows:
            return
        
        workflow = self.running_workflows[workflow_id]
        
        # Save checkpoint for later resumption
        await self._checkpoint_workflow(workflow_id)
        
        # Stop workflow execution
        await self._stop_workflow(workflow_id)
        
        # Free resources
        for resource, usage in workflow.resource_requirements.items():
            if resource in self.available_resources:
                self.available_resources[resource] += usage
        
        # Move back to queue with higher priority
        workflow.priority += 1  # Boost priority after preemption
        heapq.heappush(self.pending_workflows, workflow)
        
        del self.running_workflows[workflow_id]
        self.preemptable_workflows.discard(workflow_id)
    
    def _calculate_fair_share_priority(self, request: WorkflowSchedulingRequest) -> int:
        """Calculate priority based on fair share usage"""
        
        user_id = request.user_id
        team_id = request.team_id
        
        # Get current usage
        user_usage = self.user_resource_usage.get(user_id, {})
        team_quota = self.team_resource_quotas.get(team_id, {})
        
        # Calculate usage ratios
        usage_ratios = []
        for resource in ['cpu', 'memory', 'gpu']:
            current_usage = user_usage.get(resource, 0)
            quota = team_quota.get(resource, 100)  # Default quota
            if quota > 0:
                usage_ratios.append(current_usage / quota)
        
        # Lower average usage ratio = higher priority
        avg_usage_ratio = sum(usage_ratios) / len(usage_ratios) if usage_ratios else 0
        priority = max(1, int(10 * (1 - avg_usage_ratio)))
        
        return priority
    
    async def workflow_completed(self, workflow_id: str):
        """Handle workflow completion"""
        
        if workflow_id not in self.running_workflows:
            return
        
        completed_workflow = self.running_workflows[workflow_id]
        
        # Free resources
        for resource, usage in completed_workflow.resource_requirements.items():
            if resource in self.available_resources:
                self.available_resources[resource] += usage
        
        # Update usage tracking
        self._update_usage_tracking(completed_workflow, completed=True)
        
        # Remove from running
        del self.running_workflows[workflow_id]
        self.preemptable_workflows.discard(workflow_id)
        self.completed_workflows.append(workflow_id)
        
        # Update metrics
        execution_time = (datetime.now() - completed_workflow.submission_time).total_seconds()
        self._update_metrics(execution_time)
        
        # Try to schedule pending workflows
        await self._schedule_pending_workflows()
    
    async def _schedule_pending_workflows(self):
        """Try to schedule pending workflows"""
        
        scheduled_workflows = []
        
        for i, request in enumerate(self.pending_workflows):
            if self._can_schedule_immediately(request):
                scheduled_workflows.append(i)
                await self._start_workflow(request)
        
        # Remove scheduled workflows from queue (in reverse order)
        for i in reversed(scheduled_workflows):
            self.pending_workflows.pop(i)
    
    async def _start_workflow(self, request: WorkflowSchedulingRequest):
        """Start workflow execution"""
        
        # Reserve resources
        for resource, required in request.resource_requirements.items():
            if resource in self.available_resources:
                self.available_resources[resource] -= required
        
        # Add to running workflows
        self.running_workflows[request.workflow_id] = request
        
        # Update usage tracking
        self._update_usage_tracking(request, completed=False)
        
        # Mark as preemptable if priority allows
        if request.priority < 8:  # Lower priority workflows are preemptable
            self.preemptable_workflows.add(request.workflow_id)
    
    def _update_usage_tracking(self, request: WorkflowSchedulingRequest, 
                              completed: bool):
        """Update resource usage tracking for fair share"""
        
        user_id = request.user_id
        multiplier = -1 if completed else 1
        
        if user_id not in self.user_resource_usage:
            self.user_resource_usage[user_id] = {}
        
        for resource, usage in request.resource_requirements.items():
            if resource not in self.user_resource_usage[user_id]:
                self.user_resource_usage[user_id][resource] = 0
            
            self.user_resource_usage[user_id][resource] += multiplier * usage
            self.user_resource_usage[user_id][resource] = max(
                0, self.user_resource_usage[user_id][resource]
            )
    
    def get_scheduling_metrics(self) -> Dict[str, Any]:
        """Get comprehensive scheduling metrics"""
        
        # Calculate resource utilization
        resource_utilization = {}
        for resource, total in self.cluster_resources.items():
            used = total - self.available_resources[resource]
            utilization = (used / total) * 100 if total > 0 else 0
            resource_utilization[resource] = utilization
        
        # Calculate fairness index (Jain's fairness index)
        fairness_index = self._calculate_fairness_index()
        
        self.scheduling_metrics.update({
            'pending_workflows': len(self.pending_workflows),
            'running_workflows': len(self.running_workflows),
            'completed_workflows': len(self.completed_workflows),
            'resource_utilization': resource_utilization,
            'fairness_index': fairness_index
        })
        
        return self.scheduling_metrics
    
    def _calculate_fairness_index(self) -> float:
        """Calculate Jain's fairness index for resource allocation"""
        
        usage_values = []
        for user_usage in self.user_resource_usage.values():
            total_usage = sum(usage_values.values() for usage_values in [user_usage])
            usage_values.append(total_usage)
        
        if not usage_values:
            return 1.0
        
        n = len(usage_values)
        sum_usage = sum(usage_values)
        sum_squares = sum(x**2 for x in usage_values)
        
        if sum_squares == 0:
            return 1.0
        
        fairness_index = (sum_usage**2) / (n * sum_squares)
        return fairness_index
```

This implementation provides a comprehensive foundation for MLOps infrastructure with distributed workflow orchestration, advanced scheduling policies, resource management, and fairness mechanisms. The system handles complex ML pipelines with sophisticated dependency management, preemption support, and comprehensive monitoring.

The episode would continue with sections on model versioning, CI/CD for ML, A/B testing platforms, model serving infrastructure, monitoring and observability, analysis of production platforms like Uber's Michelangelo and Netflix's Metaflow, and future directions in ML infrastructure.

Would you like me to continue with the remaining sections of Episode 143 or proceed to create Episodes 144 and 145?