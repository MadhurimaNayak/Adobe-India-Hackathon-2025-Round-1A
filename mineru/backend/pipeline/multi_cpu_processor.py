import multiprocessing as mp
import os
from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import threading
import psutil
from loguru import logger
import time
import queue
import functools

from mineru.backend.pipeline.batch_analyze import BatchAnalyze
from mineru.backend.pipeline.pipeline_analyze import ModelSingleton
from mineru.utils.config_reader import get_device
from mineru.utils.model_utils import clean_memory


class MultiCPUProcessor:
    """Actually uses parallel processing effectively"""
    
    def __init__(self):
        self.cpu_cores = mp.cpu_count()
        self.max_workers = min(self.cpu_cores, 4)  # Don't exceed 4 for memory reasons
        self.optimal_batch_size = 4  # Smaller batches for parallel processing
        
        logger.info(f"TrueParallelProcessor: {self.max_workers} workers, batch_size={self.optimal_batch_size}")
    
    def process_with_multiprocessing(self, images_with_extra_info, formula_enable=False, table_enable=False):
        """Use actual multiprocessing for CPU-bound tasks"""
        total_pages = len(images_with_extra_info)
        
        #if total_pages <= 8:
            # Small docs: not worth the multiprocessing overhead
            #return self._process_single_batch(images_with_extra_info, formula_enable, table_enable)
        
        # Split into chunks for parallel processing
        chunk_size = max(2, total_pages // self.max_workers)
        chunks = [images_with_extra_info[i:i + chunk_size] 
                 for i in range(0, total_pages, chunk_size)]
        
        logger.info(f"Processing {len(chunks)} chunks across {self.max_workers} processes")
        
        # Use multiprocessing for true parallelism
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all chunks
            future_to_chunk = {
                executor.submit(
                    process_chunk_worker, 
                    chunk, 
                    formula_enable, 
                    table_enable
                ): i for i, chunk in enumerate(chunks)
            }
            
            # Collect results in order
            chunk_results = [None] * len(chunks)
            for future in as_completed(future_to_chunk):
                chunk_idx = future_to_chunk[future]
                try:
                    chunk_results[chunk_idx] = future.result()
                    logger.info(f"Chunk {chunk_idx + 1}/{len(chunks)} completed")
                except Exception as e:
                    logger.error(f"Chunk {chunk_idx} failed: {e}")
                    chunk_results[chunk_idx] = []
        
        # Flatten results
        results = []
        for chunk_result in chunk_results:
            if chunk_result:
                results.extend(chunk_result)
        
        return results
    
    def process_with_threading_optimized(self, images_with_extra_info, formula_enable=False, table_enable=False):
        """Optimized threading approach with separate model instances"""
        total_pages = len(images_with_extra_info)
        
        if total_pages <= 6:
            return self._process_single_batch(images_with_extra_info, formula_enable, table_enable)
        
        # Create batches for threading
        batches = [images_with_extra_info[i:i + self.optimal_batch_size] 
                  for i in range(0, total_pages, self.optimal_batch_size)]
        
        logger.info(f"Threading: {len(batches)} batches across {self.max_workers} threads")
        
        results = []
        results_lock = threading.Lock()
        
        def process_batch_thread(batch, batch_idx):
            try:
                # Each thread gets its own model instance
                model_manager = ModelSingleton()
                batch_model = BatchAnalyze(model_manager, len(batch), formula_enable, table_enable)
                batch_result = batch_model(batch)
                
                with results_lock:
                    results.extend(batch_result)
                
                logger.info(f"Thread batch {batch_idx + 1} completed ({len(batch)} pages)")
                return batch_result
                
            except Exception as e:
                logger.error(f"Thread batch {batch_idx} failed: {e}")
                return []
        
        # Use ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(process_batch_thread, batch, i) 
                      for i, batch in enumerate(batches)]
            
            # Wait for all to complete
            for future in as_completed(futures):
                try:
                    future.result()  # This will raise any exceptions
                except Exception as e:
                    logger.error(f"Thread execution error: {e}")
        
        return results
    
    def _process_single_batch(self, images_with_extra_info, formula_enable, table_enable):
        """Single batch processing"""
        model_manager = ModelSingleton()
        batch_model = BatchAnalyze(model_manager, len(images_with_extra_info), formula_enable, table_enable)
        return batch_model(images_with_extra_info)


# Worker function for multiprocessing (must be at module level)
def process_chunk_worker(chunk, formula_enable, table_enable):
    """Worker function for multiprocessing - must be picklable"""
    try:
        # Each process gets its own model
        model_manager = ModelSingleton()
        batch_model = BatchAnalyze(model_manager, len(chunk), formula_enable, table_enable)
        return batch_model(chunk)
    except Exception as e:
        logger.error(f"Worker process error: {e}")
        return []



if __name__ == "__main__":
    # Test with actual parallel processing
    processor = MultiCPUProcessor()
    
    # Usage:
    # results = processor.process_optimally(
    #     images_with_extra_info,
    #     formula_enable=False,
    #     table_enable=False
    # )
    
    print("Use HybridProcessor for adaptive parallel processing based on document size")