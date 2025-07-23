import os
import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
import time

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "text-embedding-3-small"
        self.dimensions = 1536  # text-embedding-3-small dimensions
        
        # Rate limiting settings
        self.requests_per_minute = 3500
        self.tokens_per_minute = 350000
        self.last_request_time = 0
        self.min_request_interval = 60.0 / self.requests_per_minute
        
    def create_text_block(self, record: Dict[str, Any]) -> str:
        # Extract relevant fields for embedding
        fields = []
        
        # Core permit information
        if record.get('permit_info', {}).get('description'):
            fields.append(f"Description: {record['permit_info']['description']}")
        
        if record.get('permit_info', {}).get('permit_type'):
            fields.append(f"Permit Type: {record['permit_info']['permit_type']}")
            
        if record.get('permit_info', {}).get('permit_type_description'):
            fields.append(f"Permit Type Description: {record['permit_info']['permit_type_description']}")
            
        if record.get('permit_info', {}).get('work_class'):
            fields.append(f"Work Class: {record['permit_info']['work_class']}")
            
        if record.get('permit_info', {}).get('permit_class'):
            fields.append(f"Permit Class: {record['permit_info']['permit_class']}")
            
        if record.get('permit_info', {}).get('status'):
            fields.append(f"Status: {record['permit_info']['status']}")
        
        # Location information
        if record.get('location', {}).get('address'):
            fields.append(f"Address: {record['location']['address']}")
            
        if record.get('location', {}).get('city'):
            fields.append(f"City: {record['location']['city']}")
            
        if record.get('location', {}).get('legal_description'):
            fields.append(f"Legal Description: {record['location']['legal_description']}")
        
        # Contractor information
        if record.get('contractor', {}).get('contractor_company_name'):
            fields.append(f"Contractor: {record['contractor']['contractor_company_name']}")
            
        if record.get('contractor', {}).get('contractor_trade'):
            fields.append(f"Contractor Trade: {record['contractor']['contractor_trade']}")
        
        # Applicant information
        if record.get('applicant', {}).get('applicant_full_name'):
            fields.append(f"Applicant: {record['applicant']['applicant_full_name']}")
            
        if record.get('applicant', {}).get('applicant_organization'):
            fields.append(f"Applicant Organization: {record['applicant']['applicant_organization']}")
        
        # Project information
        if record.get('project', {}).get('project_id'):
            fields.append(f"Project ID: {record['project']['project_id']}")
            
        if record.get('project', {}).get('master_permit_number'):
            fields.append(f"Master Permit: {record['project']['master_permit_number']}")
        
        # Valuation information (if significant)
        valuation = record.get('valuation', {})
        if valuation.get('total_job_valuation') and valuation['total_job_valuation'] > 0:
            fields.append(f"Job Valuation: ${valuation['total_job_valuation']:,.2f}")
            
        if valuation.get('total_new_addition_sqft') and valuation['total_new_addition_sqft'] > 0:
            fields.append(f"New Addition Sqft: {valuation['total_new_addition_sqft']}")
            
        if valuation.get('total_existing_building_sqft') and valuation['total_existing_building_sqft'] > 0:
            fields.append(f"Existing Building Sqft: {valuation['total_existing_building_sqft']}")
        
        # Join all fields into a single text block
        text_block = " | ".join(fields)
        
        # Ensure the text block is not empty
        if not text_block.strip():
            text_block = f"Permit {record.get('permit_info', {}).get('permit_number', 'Unknown')}"
            
        return text_block
    
    def _rate_limit(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        try:
            self._rate_limit()
            
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[Optional[List[float]]]:
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            batch_embeddings = []
            for text in batch:
                embedding = self.generate_embedding(text)
                batch_embeddings.append(embedding)
            
            embeddings.extend(batch_embeddings)
            
            # Small delay between batches to be respectful
            if i + batch_size < len(texts):
                time.sleep(0.1)
        
        return embeddings
    
    def process_records_for_embedding(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        processed_records = []
        
        for i, record in enumerate(records):
            # Create text block
            text_block = self.create_text_block(record)
            
            # Generate embedding
            embedding = self.generate_embedding(text_block)
            
            processed_record = {
                'record': record,
                'text_block': text_block,
                'embedding': embedding,
                'record_id': record.get('metadata', {}).get('record_id', f"record_{i}")
            }
            
            processed_records.append(processed_record)
            
            if (i + 1) % 100 == 0:
                logger.info(f"Processed {i + 1}/{len(records)} records")
        
        return processed_records
    
    def get_embedding_stats(self, processed_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        total_records = len(processed_records)
        successful_embeddings = sum(1 for record in processed_records if record['embedding'] is not None)
        failed_embeddings = total_records - successful_embeddings
        
        # Calculate average text block length
        text_lengths = [len(record['text_block']) for record in processed_records]
        avg_text_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
        
        return {
            'total_records': total_records,
            'successful_embeddings': successful_embeddings,
            'failed_embeddings': failed_embeddings,
            'success_rate': successful_embeddings / total_records if total_records > 0 else 0,
            'average_text_length': avg_text_length,
            'embedding_dimensions': self.dimensions
        }
