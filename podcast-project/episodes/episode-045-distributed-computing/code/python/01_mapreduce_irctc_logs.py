#!/usr/bin/env python3
"""
MapReduce Implementation for IRCTC Log Analysis
IRCTC लॉग्स का word count - Distributed computing ka पहला कदम

यह example दिखाता है कि कैसे IRCTC के massive logs को process करते हैं
using MapReduce pattern. जब crores of users book tickets, तो logs का size
बहुत ज्यादा हो जाता है - इसलिए distributed processing जरूरी है।

Production में: IRCTC processes 1 million+ transactions daily
Cost impact: Single node processing would take 24+ hours for daily logs
"""

import json
import multiprocessing
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import time
import logging
from concurrent.futures import ProcessPoolExecutor
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IRCTCLogMapper:
    """
    Mapper class for IRCTC log processing
    हर log entry को छोटे pieces में break करता है
    """
    
    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        logger.info(f"Worker {worker_id} initialized - IRCTC log mapper ready")
    
    def map_log_entry(self, log_entry: str) -> List[Tuple[str, int]]:
        """
        Single log entry को process करके word counts return करता है
        
        Args:
            log_entry: Raw log line from IRCTC servers
            
        Returns:
            List of (word, count) tuples
        """
        try:
            # Parse JSON log entry
            log_data = json.loads(log_entry.strip())
            
            # Extract relevant fields for word counting
            text_fields = []
            if 'message' in log_data:
                text_fields.append(log_data['message'])
            if 'user_action' in log_data:
                text_fields.append(log_data['user_action'])
            if 'error_description' in log_data:
                text_fields.append(log_data['error_description'])
            
            word_pairs = []
            for text in text_fields:
                # Basic word extraction and cleaning
                words = text.lower().split()
                for word in words:
                    # Remove special characters
                    clean_word = ''.join(c for c in word if c.isalnum())
                    if len(clean_word) > 2:  # Filter short words
                        word_pairs.append((clean_word, 1))
            
            return word_pairs
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Worker {self.worker_id}: Failed to parse log entry: {e}")
            return []
    
    def map_batch(self, log_batch: List[str]) -> List[Tuple[str, int]]:
        """
        Process a batch of log entries
        """
        all_words = []
        start_time = time.time()
        
        for log_entry in log_batch:
            words = self.map_log_entry(log_entry)
            all_words.extend(words)
        
        processing_time = time.time() - start_time
        logger.info(f"Worker {self.worker_id}: Processed {len(log_batch)} entries "
                   f"in {processing_time:.2f}s, extracted {len(all_words)} words")
        
        return all_words

class IRCTCLogReducer:
    """
    Reducer class for aggregating word counts
    सभी mappers से आए results को combine करता है
    """
    
    def __init__(self):
        self.final_counts = defaultdict(int)
        logger.info("IRCTC log reducer initialized")
    
    def reduce(self, mapped_results: List[List[Tuple[str, int]]]) -> Dict[str, int]:
        """
        Combine all mapped results into final word counts
        
        Args:
            mapped_results: List of mapper outputs
            
        Returns:
            Dictionary with final word counts
        """
        start_time = time.time()
        
        # Combine all results
        for mapper_result in mapped_results:
            for word, count in mapper_result:
                self.final_counts[word] += count
        
        processing_time = time.time() - start_time
        logger.info(f"Reduced {len(mapped_results)} mapper results in {processing_time:.2f}s")
        logger.info(f"Total unique words: {len(self.final_counts)}")
        
        return dict(self.final_counts)

class IRCTCMapReduceProcessor:
    """
    Main MapReduce orchestrator for IRCTC log analysis
    पूरा distributed processing pipeline manage करता है
    """
    
    def __init__(self, num_workers: int = None):
        self.num_workers = num_workers or multiprocessing.cpu_count()
        logger.info(f"IRCTC MapReduce processor initialized with {self.num_workers} workers")
    
    def generate_sample_logs(self, num_logs: int = 10000) -> List[str]:
        """
        Generate sample IRCTC log entries for testing
        Production में यह actual log files से आएगा
        """
        import random
        
        actions = [
            "user_login", "ticket_search", "seat_availability_check",
            "payment_initiation", "payment_success", "payment_failure",
            "booking_confirmation", "ticket_cancellation", "refund_request",
            "pnr_status_check", "seat_selection", "food_ordering"
        ]
        
        stations = [
            "NEW_DELHI", "MUMBAI_CENTRAL", "KOLKATA", "CHENNAI_CENTRAL",
            "BANGALORE", "HYDERABAD", "AHMEDABAD", "PUNE", "SURAT", "KANPUR"
        ]
        
        errors = [
            "payment_gateway_timeout", "seat_allocation_failed", 
            "database_connection_error", "authentication_failed",
            "booking_limit_exceeded", "server_overload"
        ]
        
        sample_logs = []
        for i in range(num_logs):
            log_entry = {
                "timestamp": f"2024-01-{random.randint(1, 31):02d}T{random.randint(0, 23):02d}:{random.randint(0, 59):02d}:00Z",
                "user_id": f"USER_{random.randint(100000, 999999)}",
                "session_id": hashlib.md5(f"session_{i}".encode()).hexdigest()[:16],
                "user_action": random.choice(actions),
                "source_station": random.choice(stations),
                "destination_station": random.choice(stations),
                "message": f"Processing {random.choice(actions)} for journey from {random.choice(stations)} to {random.choice(stations)}",
            }
            
            # Add errors randomly
            if random.random() < 0.1:  # 10% error rate
                log_entry["error_description"] = f"Error occurred: {random.choice(errors)}"
                log_entry["error_code"] = random.randint(1000, 9999)
            
            sample_logs.append(json.dumps(log_entry))
        
        logger.info(f"Generated {len(sample_logs)} sample IRCTC log entries")
        return sample_logs
    
    def partition_logs(self, logs: List[str]) -> List[List[str]]:
        """
        Partition logs across workers
        हर worker को equal load मिले इसके लिए logs को distribute करते हैं
        """
        chunk_size = len(logs) // self.num_workers
        partitions = []
        
        for i in range(self.num_workers):
            start_idx = i * chunk_size
            if i == self.num_workers - 1:  # Last partition gets remaining logs
                end_idx = len(logs)
            else:
                end_idx = (i + 1) * chunk_size
            
            partition = logs[start_idx:end_idx]
            partitions.append(partition)
            logger.info(f"Partition {i}: {len(partition)} log entries")
        
        return partitions
    
    def run_mapreduce(self, logs: List[str]) -> Dict[str, int]:
        """
        Execute the complete MapReduce pipeline
        
        Args:
            logs: List of log entries to process
            
        Returns:
            Final word count results
        """
        start_time = time.time()
        logger.info(f"Starting MapReduce processing for {len(logs)} log entries")
        
        # Step 1: Partition logs
        partitions = self.partition_logs(logs)
        
        # Step 2: Map phase - parallel processing
        logger.info("Starting MAP phase...")
        map_start = time.time()
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # Create mapper instances and submit tasks
            futures = []
            for worker_id, partition in enumerate(partitions):
                mapper = IRCTCLogMapper(worker_id)
                future = executor.submit(mapper.map_batch, partition)
                futures.append(future)
            
            # Collect results
            mapped_results = []
            for i, future in enumerate(futures):
                result = future.result()
                mapped_results.append(result)
                logger.info(f"Mapper {i} completed with {len(result)} word pairs")
        
        map_time = time.time() - map_start
        logger.info(f"MAP phase completed in {map_time:.2f}s")
        
        # Step 3: Reduce phase
        logger.info("Starting REDUCE phase...")
        reduce_start = time.time()
        
        reducer = IRCTCLogReducer()
        final_results = reducer.reduce(mapped_results)
        
        reduce_time = time.time() - reduce_start
        logger.info(f"REDUCE phase completed in {reduce_time:.2f}s")
        
        total_time = time.time() - start_time
        logger.info(f"Total MapReduce processing time: {total_time:.2f}s")
        
        return final_results
    
    def analyze_results(self, word_counts: Dict[str, int], top_k: int = 20) -> Dict[str, Any]:
        """
        Analyze and summarize the word count results
        """
        # Get top words
        top_words = Counter(word_counts).most_common(top_k)
        
        # Calculate statistics
        total_words = sum(word_counts.values())
        unique_words = len(word_counts)
        avg_frequency = total_words / unique_words if unique_words > 0 else 0
        
        analysis = {
            "total_words_processed": total_words,
            "unique_words_found": unique_words,
            "average_word_frequency": round(avg_frequency, 2),
            "top_words": top_words,
            "processing_efficiency": {
                "words_per_second": total_words / max(1, time.time() - self.start_time),
                "workers_used": self.num_workers
            }
        }
        
        logger.info(f"Analysis complete: {total_words} total words, {unique_words} unique")
        return analysis

def demonstrate_irctc_mapreduce():
    """
    Demonstrate MapReduce with IRCTC log processing
    """
    print("\n🚂 IRCTC MapReduce Log Analysis Demo")
    print("=" * 50)
    
    # Initialize processor
    processor = IRCTCMapReduceProcessor(num_workers=4)
    processor.start_time = time.time()
    
    # Generate sample data
    print("\n📊 Generating sample IRCTC logs...")
    logs = processor.generate_sample_logs(50000)  # 50K log entries
    
    print(f"Sample log entry:")
    print(json.dumps(json.loads(logs[0]), indent=2))
    
    # Run MapReduce
    print("\n🔄 Running MapReduce processing...")
    word_counts = processor.run_mapreduce(logs)
    
    # Analyze results
    print("\n📈 Analyzing results...")
    analysis = processor.analyze_results(word_counts)
    
    # Display results
    print(f"\n📋 IRCTC Log Analysis Results:")
    print(f"Total words processed: {analysis['total_words_processed']:,}")
    print(f"Unique words found: {analysis['unique_words_found']:,}")
    print(f"Average word frequency: {analysis['average_word_frequency']}")
    print(f"Processing speed: {analysis['processing_efficiency']['words_per_second']:.0f} words/second")
    
    print(f"\n🔝 Top 10 most frequent words in IRCTC logs:")
    for i, (word, count) in enumerate(analysis['top_words'][:10], 1):
        print(f"{i:2d}. {word}: {count:,} occurrences")
    
    # Production insights
    print(f"\n💡 Production Insights:")
    print(f"- Processing 1M daily IRCTC logs would take ~{50000/analysis['processing_efficiency']['words_per_second']*20:.1f} seconds")
    print(f"- Memory usage scales linearly with unique vocabulary size")
    print(f"- Network overhead minimal due to embarrassingly parallel nature")
    print(f"- Can horizontally scale to 100+ nodes for real-time processing")

if __name__ == "__main__":
    demonstrate_irctc_mapreduce()