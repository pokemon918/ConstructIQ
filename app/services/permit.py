import os
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from .embedding import EmbeddingService
from .vector_db import VectorDatabaseService

logger = logging.getLogger(__name__)

class PermitService:
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 pinecone_api_key: Optional[str] = None,
                 pinecone_environment: Optional[str] = None):
        self.embedding_service = EmbeddingService(api_key=openai_api_key)
        self.vector_db_service = VectorDatabaseService(
            api_key=pinecone_api_key,
            environment=pinecone_environment
        )
    
    def process_and_index_data(self, 
                              processed_data_path: str = "data/processed/normalized_permits_20250723_132411.json",
                              index_name: Optional[str] = None,
                              batch_size: int = 100) -> Dict[str, Any]:
        logger.info("Starting data indexing pipeline using processed data")
        
        # Step 1: Load processed data
        logger.info(f"Loading processed data from {processed_data_path}")
        processed_data = self._load_processed_data(processed_data_path)
        
        if not processed_data:
            raise ValueError(f"No processed data found in {processed_data_path}")
        
        logger.info(f"Loaded {len(processed_data)} processed records")
        
        # Step 2: Generate embeddings
        logger.info("Generating embeddings for processed records")
        processed_records = self.embedding_service.process_records_for_embedding(processed_data)
        
        # Step 3: Get embedding statistics
        embedding_stats = self.embedding_service.get_embedding_stats(processed_records)
        logger.info(f"Embedding statistics: {embedding_stats}")
        
        # Step 4: Index into vector database
        logger.info("Indexing records into vector database")
        indexing_stats = self.vector_db_service.index_records(
            processed_records=processed_records,
            index_name=index_name,
            batch_size=batch_size
        )
        
        # Step 5: Get index statistics
        index_stats = self.vector_db_service.get_index_stats(index_name)
        logger.info(f"Index statistics: {index_stats}")
        
        # Compile final statistics
        final_stats = {
            'pipeline_summary': {
                'processed_records': len(processed_data),
                'processed_records_with_embeddings': len(processed_records),
                'processed_data_path': processed_data_path
            },
            'embedding_stats': embedding_stats,
            'indexing_stats': indexing_stats,
            'index_stats': index_stats
        }
        
        logger.info("Pipeline completed successfully")
        return final_stats
    
    def search_permits(self, 
                      query_text: str,
                      top_k: int = 10,
                      index_name: Optional[str] = None,
                      filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:

        logger.info(f"Searching for permits with query: '{query_text}'")
        
        results = self.vector_db_service.search_by_text(
            query_text=query_text,
            embedding_service=self.embedding_service,
            top_k=top_k,
            index_name=index_name,
            filter_dict=filter_dict
        )
        
        logger.info(f"Found {len(results)} results")
        return results
    
    def search_permits_by_vector(self, 
                                query_vector: List[float],
                                top_k: int = 10,
                                index_name: Optional[str] = None,
                                filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:

        logger.info(f"Searching for permits with vector similarity")
        
        results = self.vector_db_service.search_similar(
            query_vector=query_vector,
            top_k=top_k,
            index_name=index_name,
            filter_dict=filter_dict
        )
        
        logger.info(f"Found {len(results)} results")
        return results
    
    def _load_processed_data(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'records' in data:
                return data['records']
            else:
                logger.warning(f"Unexpected data format in {file_path}")
                return []
                
        except Exception as e:
            logger.error(f"Error loading processed data from {file_path}: {e}")
            return []
    
    def get_service_status(self) -> Dict[str, Any]:
        status = {
            'embedding_service': 'initialized',
            'vector_db_service': 'initialized'
        }
        
        # Check OpenAI API
        try:
            test_embedding = self.embedding_service.generate_embedding("test")
            status['openai_api'] = 'connected' if test_embedding else 'error'
        except Exception as e:
            status['openai_api'] = f'error: {str(e)}'
        
        # Check Pinecone
        try:
            index_stats = self.vector_db_service.get_index_stats()
            status['pinecone'] = 'connected' if index_stats else 'error'
            status['index_stats'] = index_stats
        except Exception as e:
            status['pinecone'] = f'error: {str(e)}'
        
        return status 