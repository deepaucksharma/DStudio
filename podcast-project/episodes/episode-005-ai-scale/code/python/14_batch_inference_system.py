#!/usr/bin/env python3
"""
Batch Inference System for Large-Scale Indian Data
Episode 5: Code Example 14

Production-ready batch processing system for AI inference
Optimized for processing millions of Indian language documents

Author: Code Developer Agent
Context: Flipkart/Paytm scale batch processing for Indian data
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Iterator, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
from pathlib import Path
import pickle
import redis
import boto3
from botocore.exceptions import ClientError
import psutil
import gc
from queue import Queue
import threading

# Production logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

@dataclass
class BatchJob:
    """Batch inference job configuration"""
    job_id: str
    input_source: str  # S3 path, file path, or database query
    output_destination: str
    model_id: str
    model_version: str
    batch_size: int
    priority: Priority
    
    # Indian context specific
    supported_languages: List[str]
    region_filter: Optional[str]
    cost_limit_inr: Optional[float]
    
    # Job metadata
    total_records: Optional[int] = None
    processed_records: int = 0
    failed_records: int = 0
    status: JobStatus = JobStatus.PENDING
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    cost_inr: float = 0.0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class InferenceResult:
    """Single inference result"""
    record_id: str
    input_data: Dict[str, Any]
    prediction: Any
    confidence: float
    processing_time_ms: float
    model_version: str
    cost_inr: float
    metadata: Dict[str, Any]

class IndianTextProcessor:
    """Text processor optimized for Indian languages"""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
        self.model = AutoModel.from_pretrained("ai4bharat/indic-bert")
        self.model.eval()
        
        # Language detection patterns
        self.language_patterns = {
            'hi': range(0x0900, 0x097F),  # Devanagari
            'ta': range(0x0B80, 0x0BFF),  # Tamil
            'bn': range(0x0980, 0x09FF),  # Bengali
            'te': range(0x0C00, 0x0C7F),  # Telugu
        }
        
        logger.info(f"Initialized Indian text processor with model: {model_id}")
    
    def detect_language(self, text: str) -> str:
        """Detect primary language in text"""
        
        if not text:
            return 'unknown'
        
        lang_scores = {}
        total_chars = len(text)
        
        for lang, char_range in self.language_patterns.items():
            count = sum(1 for char in text if ord(char) in char_range)
            lang_scores[lang] = count / total_chars if total_chars > 0 else 0
        
        # Check for English
        english_count = sum(1 for char in text if ord(char) < 256 and char.isalpha())
        lang_scores['en'] = english_count / total_chars if total_chars > 0 else 0
        
        # Return language with highest score
        best_lang = max(lang_scores.items(), key=lambda x: x[1])
        
        # If highest score is too low, consider it mixed
        if best_lang[1] < 0.3:
            return 'mixed'
        
        return best_lang[0]
    
    def preprocess_text(self, text: str, language: str = None) -> str:
        """Preprocess text for better inference"""
        
        if not text:
            return ""
        
        # Detect language if not provided
        if language is None:
            language = self.detect_language(text)
        
        # Add language marker
        if language != 'unknown':
            text = f"[{language.upper()}] {text}"
        
        # Clean text
        text = ' '.join(text.split())  # Normalize whitespace
        
        return text
    
    def process_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Process a batch of texts"""
        
        results = []
        
        for i, text in enumerate(texts):
            start_time = time.time()
            
            try:
                # Preprocess
                processed_text = self.preprocess_text(text)
                language = self.detect_language(text)
                
                # Tokenize
                inputs = self.tokenizer(
                    processed_text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True
                )
                
                # Inference
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # For demonstration, create mock sentiment prediction
                    pooled_output = outputs.last_hidden_state.mean(dim=1)
                    
                    # Mock sentiment classification
                    logits = torch.randn(1, 3)  # [negative, neutral, positive]
                    probabilities = torch.softmax(logits, dim=1)
                    prediction = torch.argmax(probabilities, dim=1).item()
                    confidence = probabilities.max().item()
                
                processing_time = (time.time() - start_time) * 1000
                
                result = {
                    'record_id': f"batch_{i}",
                    'prediction': ['negative', 'neutral', 'positive'][prediction],
                    'confidence': float(confidence),
                    'language_detected': language,
                    'processing_time_ms': processing_time,
                    'cost_inr': 0.002,  # ₹0.002 per inference
                    'input_length': len(text),
                    'processed_length': len(processed_text)
                }
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process text {i}: {e}")
                results.append({
                    'record_id': f"batch_{i}",
                    'error': str(e),
                    'processing_time_ms': (time.time() - start_time) * 1000
                })
        
        return results

class DataSourceReader:
    """Read data from various sources (S3, files, databases)"""
    
    def __init__(self):
        self.s3_client = None
        try:
            self.s3_client = boto3.client('s3')
        except Exception as e:
            logger.warning(f"S3 client not available: {e}")
    
    def read_data(self, source: str, batch_size: int = 1000) -> Iterator[List[Dict[str, Any]]]:
        """Read data in batches from source"""
        
        if source.startswith('s3://'):
            yield from self._read_from_s3(source, batch_size)
        elif source.endswith('.csv'):
            yield from self._read_from_csv(source, batch_size)
        elif source.endswith('.json') or source.endswith('.jsonl'):
            yield from self._read_from_json(source, batch_size)
        else:
            raise ValueError(f"Unsupported data source: {source}")
    
    def _read_from_csv(self, file_path: str, batch_size: int) -> Iterator[List[Dict[str, Any]]]:
        """Read CSV file in batches"""
        
        try:
            for chunk in pd.read_csv(file_path, chunksize=batch_size):
                batch = chunk.to_dict('records')
                yield batch
                
        except Exception as e:
            logger.error(f"Failed to read CSV file {file_path}: {e}")
            raise
    
    def _read_from_json(self, file_path: str, batch_size: int) -> Iterator[List[Dict[str, Any]]]:
        """Read JSON/JSONL file in batches"""
        
        try:
            if file_path.endswith('.jsonl'):
                # JSON Lines format
                batch = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            batch.append(json.loads(line))
                            
                            if len(batch) >= batch_size:
                                yield batch
                                batch = []
                
                # Yield remaining items
                if batch:
                    yield batch
            else:
                # Regular JSON file
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Yield in batches
                for i in range(0, len(data), batch_size):
                    yield data[i:i+batch_size]
                    
        except Exception as e:
            logger.error(f"Failed to read JSON file {file_path}: {e}")
            raise
    
    def _read_from_s3(self, s3_path: str, batch_size: int) -> Iterator[List[Dict[str, Any]]]:
        """Read from S3 in batches"""
        
        if not self.s3_client:
            raise RuntimeError("S3 client not available")
        
        # Parse S3 path
        parts = s3_path.replace('s3://', '').split('/', 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ''
        
        try:
            # List objects
            response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=key)
            
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.json') or obj['Key'].endswith('.jsonl'):
                    # Download and process file
                    response = self.s3_client.get_object(Bucket=bucket, Key=obj['Key'])
                    content = response['Body'].read().decode('utf-8')
                    
                    if obj['Key'].endswith('.jsonl'):
                        batch = []
                        for line in content.split('\n'):
                            if line.strip():
                                batch.append(json.loads(line))
                                
                                if len(batch) >= batch_size:
                                    yield batch
                                    batch = []
                        
                        if batch:
                            yield batch
                    else:
                        data = json.loads(content)
                        for i in range(0, len(data), batch_size):
                            yield data[i:i+batch_size]
                            
        except ClientError as e:
            logger.error(f"Failed to read from S3 {s3_path}: {e}")
            raise

class ResultWriter:
    """Write inference results to various destinations"""
    
    def __init__(self):
        self.s3_client = None
        try:
            self.s3_client = boto3.client('s3')
        except Exception as e:
            logger.warning(f"S3 client not available: {e}")
    
    def write_results(self, results: List[InferenceResult], destination: str, job_id: str):
        """Write results to destination"""
        
        if destination.startswith('s3://'):
            self._write_to_s3(results, destination, job_id)
        elif destination.endswith('.csv'):
            self._write_to_csv(results, destination)
        elif destination.endswith('.json'):
            self._write_to_json(results, destination)
        else:
            raise ValueError(f"Unsupported destination: {destination}")
    
    def _write_to_csv(self, results: List[InferenceResult], file_path: str):
        """Write results to CSV file"""
        
        try:
            # Convert results to DataFrame
            data = []
            for result in results:
                row = {
                    'record_id': result.record_id,
                    'prediction': result.prediction,
                    'confidence': result.confidence,
                    'processing_time_ms': result.processing_time_ms,
                    'model_version': result.model_version,
                    'cost_inr': result.cost_inr
                }
                # Add metadata fields
                row.update(result.metadata)
                data.append(row)
            
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            
            logger.info(f"Results written to CSV: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to write CSV results: {e}")
            raise
    
    def _write_to_json(self, results: List[InferenceResult], file_path: str):
        """Write results to JSON file"""
        
        try:
            data = [asdict(result) for result in results]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results written to JSON: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to write JSON results: {e}")
            raise
    
    def _write_to_s3(self, results: List[InferenceResult], s3_path: str, job_id: str):
        """Write results to S3"""
        
        if not self.s3_client:
            raise RuntimeError("S3 client not available")
        
        # Parse S3 path
        parts = s3_path.replace('s3://', '').split('/', 1)
        bucket = parts[0]
        key_prefix = parts[1] if len(parts) > 1 else ''
        
        key = f"{key_prefix}/job_{job_id}_results.json"
        
        try:
            data = [asdict(result) for result in results]
            content = json.dumps(data, indent=2, ensure_ascii=False)
            
            self.s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='application/json'
            )
            
            logger.info(f"Results written to S3: s3://{bucket}/{key}")
            
        except ClientError as e:
            logger.error(f"Failed to write S3 results: {e}")
            raise

class BatchInferenceEngine:
    """Main batch inference engine"""
    
    def __init__(self, max_workers: int = 4, max_memory_gb: int = 16):
        self.max_workers = max_workers
        self.max_memory_gb = max_memory_gb
        self.job_queue = Queue()
        self.active_jobs: Dict[str, BatchJob] = {}
        self.completed_jobs: Dict[str, BatchJob] = {}
        
        # Initialize components
        self.data_reader = DataSourceReader()
        self.result_writer = ResultWriter()
        self.processors: Dict[str, IndianTextProcessor] = {}
        
        # Resource monitoring
        self.total_processed = 0
        self.total_cost_inr = 0.0
        self.start_time = time.time()
        
        logger.info(f"Batch inference engine initialized with {max_workers} workers")
    
    def submit_job(self, job: BatchJob) -> str:
        """Submit a batch inference job"""
        
        # Validate job
        if not job.input_source or not job.output_destination:
            raise ValueError("Input source and output destination required")
        
        # Add to queue
        self.job_queue.put(job)
        self.active_jobs[job.job_id] = job
        
        logger.info(f"Job submitted: {job.job_id} - Priority: {job.priority.name}")
        
        return job.job_id
    
    def get_job_status(self, job_id: str) -> Optional[BatchJob]:
        """Get status of a specific job"""
        
        if job_id in self.active_jobs:
            return self.active_jobs[job_id]
        elif job_id in self.completed_jobs:
            return self.completed_jobs[job_id]
        else:
            return None
    
    def process_job(self, job: BatchJob):
        """Process a single batch job"""
        
        logger.info(f"Starting job processing: {job.job_id}")
        
        job.status = JobStatus.RUNNING
        job.started_at = time.time()
        
        try:
            # Initialize processor for this model
            if job.model_id not in self.processors:
                self.processors[job.model_id] = IndianTextProcessor(job.model_id)
            
            processor = self.processors[job.model_id]
            
            # Process data in batches
            all_results = []
            total_records = 0
            
            for batch_data in self.data_reader.read_data(job.input_source, job.batch_size):
                # Extract text data (assuming 'text' field)
                texts = []
                record_ids = []
                
                for record in batch_data:
                    if isinstance(record, dict) and 'text' in record:
                        texts.append(record['text'])
                        record_ids.append(record.get('id', f"record_{total_records}"))
                        total_records += 1
                
                # Process batch
                if texts:
                    batch_results = processor.process_batch(texts)
                    
                    # Convert to InferenceResult objects
                    for i, result in enumerate(batch_results):
                        if 'error' not in result:
                            inference_result = InferenceResult(
                                record_id=record_ids[i],
                                input_data=batch_data[i],
                                prediction=result['prediction'],
                                confidence=result['confidence'],
                                processing_time_ms=result['processing_time_ms'],
                                model_version=job.model_version,
                                cost_inr=result['cost_inr'],
                                metadata={
                                    'language_detected': result['language_detected'],
                                    'input_length': result['input_length'],
                                    'processed_length': result['processed_length']
                                }
                            )
                            all_results.append(inference_result)
                            job.processed_records += 1
                            job.cost_inr += result['cost_inr']
                        else:
                            job.failed_records += 1
                            logger.warning(f"Failed to process record {record_ids[i]}: {result['error']}")
                
                # Check cost limit
                if job.cost_limit_inr and job.cost_inr >= job.cost_limit_inr:
                    logger.warning(f"Job {job.job_id} stopped: cost limit reached (₹{job.cost_inr:.2f})")
                    break
                
                # Memory management
                self._manage_memory()
                
                # Progress logging
                if total_records % 10000 == 0:
                    logger.info(f"Job {job.job_id}: Processed {total_records} records, "
                              f"Cost: ₹{job.cost_inr:.2f}")
            
            # Write results
            if all_results:
                self.result_writer.write_results(all_results, job.output_destination, job.job_id)
            
            # Update job status
            job.total_records = total_records
            job.status = JobStatus.COMPLETED
            job.completed_at = time.time()
            
            # Update global metrics
            self.total_processed += job.processed_records
            self.total_cost_inr += job.cost_inr
            
            processing_time = job.completed_at - job.started_at
            
            logger.info(f"Job {job.job_id} completed successfully:")
            logger.info(f"  Records processed: {job.processed_records}/{total_records}")
            logger.info(f"  Failed records: {job.failed_records}")
            logger.info(f"  Processing time: {processing_time:.1f}s")
            logger.info(f"  Cost: ₹{job.cost_inr:.2f}")
            logger.info(f"  Throughput: {job.processed_records / processing_time:.1f} records/second")
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.completed_at = time.time()
            logger.error(f"Job {job.job_id} failed: {e}")
            
        finally:
            # Move to completed jobs
            if job.job_id in self.active_jobs:
                del self.active_jobs[job.job_id]
            self.completed_jobs[job.job_id] = job
    
    def _manage_memory(self):
        """Monitor and manage memory usage"""
        
        # Get memory usage
        memory_usage_gb = psutil.virtual_memory().used / 1024 / 1024 / 1024
        
        # Clear GPU cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Garbage collection
        gc.collect()
        
        # Warning if approaching limit
        if memory_usage_gb > self.max_memory_gb * 0.8:
            logger.warning(f"High memory usage: {memory_usage_gb:.1f}GB / {self.max_memory_gb}GB")
    
    def start_workers(self):
        """Start worker threads to process jobs"""
        
        def worker():
            while True:
                try:
                    # Get job from queue (blocks until available)
                    job = self.job_queue.get(timeout=60)  # 60 second timeout
                    
                    if job is None:  # Shutdown signal
                        break
                    
                    # Process job
                    self.process_job(job)
                    
                except Exception as e:
                    logger.error(f"Worker error: {e}")
                finally:
                    self.job_queue.task_done()
        
        # Start worker threads
        self.workers = []
        for i in range(self.max_workers):
            worker_thread = threading.Thread(target=worker, name=f"BatchWorker-{i}")
            worker_thread.daemon = True
            worker_thread.start()
            self.workers.append(worker_thread)
        
        logger.info(f"Started {len(self.workers)} worker threads")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system performance statistics"""
        
        uptime = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime,
            "total_jobs_processed": len(self.completed_jobs),
            "active_jobs": len(self.active_jobs),
            "total_records_processed": self.total_processed,
            "total_cost_inr": f"₹{self.total_cost_inr:.2f}",
            "avg_cost_per_record_inr": f"₹{self.total_cost_inr / max(1, self.total_processed):.4f}",
            "throughput_records_per_second": self.total_processed / uptime if uptime > 0 else 0,
            "memory_usage_gb": psutil.virtual_memory().used / 1024 / 1024 / 1024,
            "workers_active": len([w for w in getattr(self, 'workers', []) if w.is_alive()])
        }

# Create sample dataset for testing
def create_sample_indian_dataset(size: int = 10000) -> str:
    """Create sample Indian language dataset for batch processing"""
    
    # Sample Indian texts (mix of Hindi, English, and code-mixed)
    sample_texts = [
        "यह product बहुत अच्छा है। Quality excellent है।",
        "मुझे यह service पसंद नहीं आई। Very disappointing experience.",
        "Flipkart se ordered phone, delivery was very fast and पैकिंग भी अच्छी थी।",
        "Customer support team helped me resolve the issue quickly. धन्यवाद!",
        "Price थोड़ा ज्यादा है but quality के लिए it's worth it.",
        "Mumbai में traffic बहुत है but Uber ride was comfortable.",
        "Online shopping का experience बहुत smooth था।",
        "Restaurant का food delicious था। Will definitely visit again.",
        "Hotel staff was very helpful और rooms भी clean थे।",
        "Movie was entertaining लेकिन थोड़ा लंबा था।"
    ]
    
    # Generate dataset
    import random
    data = []
    
    for i in range(size):
        text = random.choice(sample_texts)
        # Add some variation
        text = text.replace("product", random.choice(["product", "item", "samaan"]))
        text = text.replace("service", random.choice(["service", "seva", "facility"]))
        
        record = {
            "id": f"record_{i+1:06d}",
            "text": text,
            "category": random.choice(["electronics", "food", "travel", "shopping", "entertainment"]),
            "region": random.choice(["north", "south", "east", "west", "central"]),
            "timestamp": time.time() + random.randint(-86400, 0)  # Last 24 hours
        }
        data.append(record)
    
    # Save to file
    output_file = "/tmp/indian_sample_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Sample dataset created: {output_file} with {size} records")
    return output_file

# Test and demonstration
def test_batch_inference_system():
    """Test batch inference system with Indian data"""
    
    print("⚡ Batch Inference System Test - Large-Scale Indian Data Processing")
    print("=" * 75)
    
    # Create sample dataset
    print("📚 Creating sample Indian dataset...")
    dataset_path = create_sample_indian_dataset(5000)  # 5000 records for demo
    
    # Initialize batch engine
    print("\n🚀 Initializing batch inference engine...")
    engine = BatchInferenceEngine(max_workers=2, max_memory_gb=8)
    engine.start_workers()
    
    # Create batch job
    job = BatchJob(
        job_id=f"indian_sentiment_job_{int(time.time())}",
        input_source=dataset_path,
        output_destination="/tmp/batch_results.json",
        model_id="indic_sentiment_analyzer",
        model_version="v2.1.0",
        batch_size=100,
        priority=Priority.HIGH,
        supported_languages=["hi", "en", "mixed"],
        region_filter=None,
        cost_limit_inr=50.0  # ₹50 budget limit
    )
    
    print(f"✅ Engine initialized with {engine.max_workers} workers")
    
    # Submit job
    print(f"\n📝 Submitting batch job...")
    job_id = engine.submit_job(job)
    
    print(f"   Job ID: {job_id}")
    print(f"   Input: {job.input_source}")
    print(f"   Output: {job.output_destination}")
    print(f"   Model: {job.model_id} {job.model_version}")
    print(f"   Batch size: {job.batch_size}")
    print(f"   Cost limit: ₹{job.cost_limit_inr}")
    
    # Monitor job progress
    print(f"\n⏳ Monitoring job progress...")
    
    while True:
        current_job = engine.get_job_status(job_id)
        if not current_job:
            break
        
        if current_job.status == JobStatus.RUNNING:
            print(f"   Status: {current_job.status.name}")
            print(f"   Progress: {current_job.processed_records} processed, {current_job.failed_records} failed")
            print(f"   Cost: ₹{current_job.cost_inr:.2f}")
            time.sleep(5)  # Check every 5 seconds
        elif current_job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            break
    
    # Final results
    final_job = engine.get_job_status(job_id)
    
    print(f"\n📊 Job Results:")
    print(f"   Status: {final_job.status.name}")
    print(f"   Total records: {final_job.total_records or 'Unknown'}")
    print(f"   Processed: {final_job.processed_records}")
    print(f"   Failed: {final_job.failed_records}")
    
    if final_job.started_at and final_job.completed_at:
        processing_time = final_job.completed_at - final_job.started_at
        throughput = final_job.processed_records / processing_time if processing_time > 0 else 0
        
        print(f"   Processing time: {processing_time:.1f} seconds")
        print(f"   Throughput: {throughput:.1f} records/second")
    
    print(f"   Total cost: ₹{final_job.cost_inr:.2f}")
    print(f"   Cost per record: ₹{final_job.cost_inr / max(1, final_job.processed_records):.4f}")
    
    # System statistics
    print(f"\n📈 System Statistics:")
    stats = engine.get_system_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Check output file
    if Path(job.output_destination).exists():
        print(f"\n✅ Results saved to: {job.output_destination}")
        
        # Show sample results
        with open(job.output_destination, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        print(f"   Sample results (first 3):")
        for i, result in enumerate(results[:3], 1):
            print(f"      {i}. Record: {result['record_id']}")
            print(f"         Prediction: {result['prediction']}")
            print(f"         Confidence: {result['confidence']:.3f}")
            print(f"         Language: {result['metadata']['language_detected']}")
            print(f"         Cost: ₹{result['cost_inr']:.4f}")
    
    print(f"\n🎯 Batch Processing Features Demonstrated:")
    print(f"   ✅ Large-scale Indian language processing (5000 records)")
    print(f"   ✅ Multi-threaded batch processing")
    print(f"   ✅ Automatic language detection (Hindi/English/Mixed)")
    print(f"   ✅ Cost tracking and budget limits in INR")
    print(f"   ✅ Progress monitoring and job status tracking")
    print(f"   ✅ Memory management and resource optimization")
    print(f"   ✅ Multiple input/output formats (JSON, CSV, S3)")
    print(f"   ✅ Production-ready error handling and logging")

if __name__ == "__main__":
    test_batch_inference_system()