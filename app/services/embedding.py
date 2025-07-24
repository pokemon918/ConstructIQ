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
        self.dimensions = 1536
        
        self.requests_per_minute = 3500
        self.tokens_per_minute = 350000
        self.last_request_time = 0
        self.min_request_interval = 60.0 / self.requests_per_minute
        
    def create_text_block(self, record: Dict[str, Any]) -> str:
        """Create a comprehensive text block optimized for semantic search performance."""
        sections = []
        
        # 1. PROJECT DESCRIPTION (highest priority for semantic search)
        project_desc = record.get('project', {}).get('description')
        if project_desc:
            sections.append(f"PROJECT: {project_desc}")
        
        # 2. PERMIT DETAILS
        permit_info = record.get('permit_info', {})
        permit_details = []
        
        if permit_info.get('permit_type_description'):
            permit_details.append(permit_info['permit_type_description'])
        if permit_info.get('permit_type'):
            permit_details.append(permit_info['permit_type'])
        if permit_info.get('work_class'):
            permit_details.append(permit_info['work_class'])
        if permit_info.get('permit_class'):
            permit_details.append(permit_info['permit_class'])
        if permit_info.get('status'):
            permit_details.append(permit_info['status'])
        
        if permit_details:
            sections.append(f"PERMIT TYPE: {' | '.join(permit_details)}")
        
        # 3. LOCATION INFORMATION
        location = record.get('location', {})
        location_parts = []
        
        if location.get('address'):
            location_parts.append(location['address'])
        if location.get('city'):
            location_parts.append(location['city'])
        if location.get('state'):
            location_parts.append(location['state'])
        if location.get('legal_description'):
            location_parts.append(location['legal_description'])
        
        if location_parts:
            sections.append(f"LOCATION: {' | '.join(location_parts)}")
        
        # 4. CONTRACTOR INFORMATION
        contractor = record.get('contractor', {})
        contractor_info = []
        
        if contractor.get('contractor_company_name'):
            contractor_info.append(contractor['contractor_company_name'])
        if contractor.get('contractor_trade'):
            contractor_info.append(contractor['contractor_trade'])
        if contractor.get('contractor_full_name'):
            contractor_info.append(contractor['contractor_full_name'])
        
        if contractor_info:
            sections.append(f"CONTRACTOR: {' | '.join(contractor_info)}")
        
        # 5. APPLICANT INFORMATION
        applicant = record.get('applicant', {})
        applicant_info = []
        
        if applicant.get('applicant_full_name'):
            applicant_info.append(applicant['applicant_full_name'])
        if applicant.get('applicant_organization'):
            applicant_info.append(applicant['applicant_organization'])
        
        if applicant_info:
            sections.append(f"APPLICANT: {' | '.join(applicant_info)}")
        
        # 6. VALUATION AND SCOPE
        valuation = record.get('valuation', {})
        valuation_info = []
        
        if valuation.get('total_job_valuation') and valuation['total_job_valuation'] > 0:
            valuation_info.append(f"Total Value: ${valuation['total_job_valuation']:,.0f}")
        if valuation.get('total_new_addition_sqft') and valuation['total_new_addition_sqft'] > 0:
            valuation_info.append(f"New Addition: {valuation['total_new_addition_sqft']} sqft")
        if valuation.get('total_existing_building_sqft') and valuation['total_existing_building_sqft'] > 0:
            valuation_info.append(f"Existing Building: {valuation['total_existing_building_sqft']} sqft")
        if valuation.get('remodel_repair_sqft') and valuation['remodel_repair_sqft'] > 0:
            valuation_info.append(f"Remodel/Repair: {valuation['remodel_repair_sqft']} sqft")
        if valuation.get('number_of_floors') and valuation['number_of_floors'] > 0:
            valuation_info.append(f"Floors: {valuation['number_of_floors']}")
        if valuation.get('housing_units') and valuation['housing_units'] > 0:
            valuation_info.append(f"Housing Units: {valuation['housing_units']}")
        
        # Add specific trade valuations
        trade_valuations = []
        for trade in ['building', 'electrical', 'mechanical', 'plumbing', 'medgas']:
            trade_val = valuation.get(f'{trade}_valuation')
            trade_remodel = valuation.get(f'{trade}_valuation_remodel')
            if trade_val and trade_val > 0:
                trade_valuations.append(f"{trade.title()}: ${trade_val:,.0f}")
            if trade_remodel and trade_remodel > 0:
                trade_valuations.append(f"{trade.title()} Remodel: ${trade_remodel:,.0f}")
        
        if trade_valuations:
            valuation_info.extend(trade_valuations)
        
        if valuation_info:
            sections.append(f"VALUATION: {' | '.join(valuation_info)}")
        
        # 7. DATES AND TIMELINE
        dates = record.get('dates', {})
        date_info = []
        
        if dates.get('applied_date'):
            date_info.append(f"Applied: {dates['applied_date'][:10]}")
        if dates.get('issue_date'):
            date_info.append(f"Issued: {dates['issue_date'][:10]}")
        if dates.get('calendar_year'):
            date_info.append(f"Year: {dates['calendar_year']}")
        if dates.get('day_issued'):
            date_info.append(f"Day: {dates['day_issued']}")
        
        if date_info:
            sections.append(f"DATES: {' | '.join(date_info)}")
        
        # 8. PROJECT RELATIONSHIPS
        project = record.get('project', {})
        project_info = []
        
        if project.get('project_id'):
            project_info.append(f"Project ID: {project['project_id']}")
        if project.get('master_permit_number'):
            project_info.append(f"Master Permit: {project['master_permit_number']}")
        
        if project_info:
            sections.append(f"PROJECT INFO: {' | '.join(project_info)}")
        
        # 9. ADDITIONAL CONTEXT
        additional_info = []
        
        if permit_info.get('condominium'):
            additional_info.append("Condominium")
        if permit_info.get('certificate_of_occupancy'):
            additional_info.append("Certificate of Occupancy")
        if permit_info.get('recently_issued'):
            additional_info.append("Recently Issued")
        if location.get('council_district'):
            additional_info.append(f"Council District {location['council_district']}")
        if location.get('jurisdiction'):
            additional_info.append(location['jurisdiction'])
        
        if additional_info:
            sections.append(f"CONTEXT: {' | '.join(additional_info)}")
        
        # Combine all sections with clear separators
        text_block = " || ".join(sections)
        
        # Ensure the text block is not empty and has meaningful content
        if not text_block.strip():
            permit_number = record.get('permit_info', {}).get('permit_number', 'Unknown')
            text_block = f"Permit {permit_number} - No detailed information available"
        
        # Truncate if too long (OpenAI has token limits)
        if len(text_block) > 4000:
            text_block = text_block[:4000] + "..."
            
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
