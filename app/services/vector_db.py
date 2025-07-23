import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pinecone import Pinecone, ServerlessSpec
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class VectorDatabaseService:
    def __init__(self, api_key: Optional[str] = None, environment: Optional[str] = None):
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.environment = environment or os.getenv('PINECONE_ENVIRONMENT')
        
        if not self.api_key:
            raise ValueError("Pinecone API key is required. Set PINECONE_API_KEY environment variable or pass api_key parameter.")
        
        if not self.environment:
            raise ValueError("Pinecone environment is required. Set PINECONE_ENVIRONMENT environment variable or pass environment parameter.")
        
        # Initialize Pinecone with new API
        self.pc = Pinecone(api_key=self.api_key)
        
        # Default index configuration
        self.index_name = "austin-permits"
        self.dimension = 1536  # text-embedding-3-small dimensions
        self.metric = "cosine"
        
    def create_index(self, index_name: Optional[str] = None, dimension: Optional[int] = None) -> bool:
        index_name = index_name or self.index_name
        dimension = dimension or self.dimension
        
        try:
            # Check if index already exists
            if index_name in self.pc.list_indexes().names():
                logger.info(f"Index '{index_name}' already exists")
                return True
            
            # Create index
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=self.metric,
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            
            logger.info(f"Successfully created index '{index_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error creating index '{index_name}': {e}")
            return False
    
    def get_index(self, index_name: Optional[str] = None):
        index_name = index_name or self.index_name
        
        if index_name not in self.pc.list_indexes().names():
            raise ValueError(f"Index '{index_name}' does not exist")
        
        return self.pc.Index(index_name)
    
    def delete_index(self, index_name: Optional[str] = None) -> bool:
        index_name = index_name or self.index_name
        
        try:
            if index_name in self.pc.list_indexes().names():
                self.pc.delete_index(index_name)
                logger.info(f"Successfully deleted index '{index_name}'")
                return True
            else:
                logger.warning(f"Index '{index_name}' does not exist")
                return True
                
        except Exception as e:
            logger.error(f"Error deleting index '{index_name}': {e}")
            return False
    
    def index_records(self, processed_records: List[Dict[str, Any]], 
                     index_name: Optional[str] = None, 
                     batch_size: int = 100) -> Dict[str, Any]:
        index_name = index_name or self.index_name
        
        # Ensure index exists
        if not self.create_index(index_name):
            raise RuntimeError(f"Failed to create or access index '{index_name}'")
        
        index = self.get_index(index_name)
        
        # Filter out records without embeddings
        valid_records = [record for record in processed_records if record['embedding'] is not None]
        
        if not valid_records:
            logger.warning("No valid records with embeddings to index")
            return {
                'total_records': 0,
                'indexed_records': 0,
                'failed_records': 0,
                'success_rate': 0.0
            }
        
        logger.info(f"Indexing {len(valid_records)} records with embeddings")
        
        indexed_count = 0
        failed_count = 0
        
        # Process in batches
        for i in range(0, len(valid_records), batch_size):
            batch = valid_records[i:i + batch_size]
            batch_vectors = []
            
            for record in batch:
                try:
                    # Prepare metadata for filtering and retrieval
                    metadata = self._prepare_metadata(record)
                    
                    vector_data = {
                        'id': record['record_id'],
                        'values': record['embedding'],
                        'metadata': metadata
                    }
                    print(vector_data)
                    batch_vectors.append(vector_data)
                    
                except Exception as e:
                    logger.error(f"Error preparing record {record.get('record_id', 'unknown')}: {e}")
                    failed_count += 1
            
            # Upsert batch
            if batch_vectors:
                try:
                    index.upsert(vectors=batch_vectors)
                    indexed_count += len(batch_vectors)
                    logger.info(f"Indexed batch {i//batch_size + 1}/{(len(valid_records) + batch_size - 1)//batch_size}")
                    
                except Exception as e:
                    logger.error(f"Error indexing batch: {e}")
                    failed_count += len(batch_vectors)
            
            # Small delay between batches
            if i + batch_size < len(valid_records):
                time.sleep(0.1)
        
        success_rate = indexed_count / len(valid_records) if valid_records else 0
        
        stats = {
            'total_records': len(processed_records),
            'valid_records': len(valid_records),
            'indexed_records': indexed_count,
            'failed_records': failed_count,
            'success_rate': success_rate
        }
        
        logger.info(f"Indexing completed: {stats}")
        return stats
    
    def _prepare_metadata(self, record: Dict[str, Any]) -> Dict[str, Any]:
        permit_info = record['record'].get('permit_info', {})
        location = record['record'].get('location', {})
        dates = record['record'].get('dates', {})
        valuation = record['record'].get('valuation', {})
        contractor = record['record'].get('contractor', {})
        applicant = record['record'].get('applicant', {})
        
        metadata = {
            # Core identifiers
            'record_id': record['record_id'],
            'permit_number': permit_info.get('permit_number'),
            'project_id': record['record'].get('project', {}).get('project_id'),
            
            # Permit classification
            'permit_type': permit_info.get('permit_type'),
            'permit_class': permit_info.get('permit_class'),
            'work_class': permit_info.get('work_class'),
            'status': permit_info.get('status'),
            
            # Location
            'city': location.get('city'),
            'state': location.get('state'),
            'zip_code': location.get('zip_code'),
            'council_district': location.get('council_district'),
            
            # Dates (as strings for filtering)
            'applied_date': dates.get('applied_date'),
            'issue_date': dates.get('issue_date'),
            'calendar_year': dates.get('calendar_year'),
            
            # Valuation (as numbers for range queries)
            'total_job_valuation': valuation.get('total_job_valuation'),
            'total_new_addition_sqft': valuation.get('total_new_addition_sqft'),
            'total_existing_building_sqft': valuation.get('total_existing_building_sqft'),
            
            # Contractor
            'contractor_company': contractor.get('contractor_company_name'),
            'contractor_trade': contractor.get('contractor_trade'),
            
            # Applicant
            'applicant_name': applicant.get('applicant_full_name'),
            'applicant_organization': applicant.get('applicant_organization'),
            
            # Text for search
            'text_block': record['text_block'][:1000],  # Truncate to avoid metadata size limits
            
            # Indexing metadata
            'indexed_at': datetime.now().isoformat(),
            'embedding_model': 'text-embedding-3-small'
        }
        
        metadata = {k: v for k, v in metadata.items() if v is not None}
        
        return metadata
    
    def search_similar(self, query_vector: List[float], 
                      top_k: int = 5,
                      index_name: Optional[str] = None,
                      filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        index_name = index_name or self.index_name
        index = self.get_index(index_name)
        
        try:
            results = index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict
            )
            
            return results.matches
            
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            return []
    
    def search_by_text(self, query_text: str,
                      embedding_service,
                      top_k: int = 5,
                      index_name: Optional[str] = None,
                      filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        # Generate embedding for query text
        query_embedding = embedding_service.generate_embedding(query_text)
        
        if query_embedding is None:
            logger.error("Failed to generate embedding for query text")
            return []
        
        return self.search_similar(
            query_vector=query_embedding,
            top_k=top_k,
            index_name=index_name,
            filter_dict=filter_dict
        )
    
    def get_index_stats(self, index_name: Optional[str] = None) -> Dict[str, Any]:
        index_name = index_name or self.index_name
        
        try:
            index = self.get_index(index_name)
            stats = index.describe_index_stats()
            
            return {
                'index_name': index_name,
                'total_vector_count': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': stats.namespaces
            }
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
