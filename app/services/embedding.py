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
        """Create a comprehensive and descriptive text block with natural sentences optimized for semantic search performance."""
        sentences = []
        
        # 1. PROJECT DESCRIPTION (highest priority for semantic search)
        project_desc = record.get('project', {}).get('description')
        if project_desc:
            sentences.append(f"The project involves {project_desc.lower()}")
        
        # 2. PERMIT CLASSIFICATION AND TYPE
        permit_info = record.get('permit_info', {})
        
        # Create natural language permit description
        permit_parts = []
        if permit_info.get('permit_type_description'):
            permit_parts.append(permit_info['permit_type_description'].lower())
        if permit_info.get('permit_type'):
            permit_parts.append(permit_info['permit_type'].lower())
        if permit_info.get('work_class'):
            permit_parts.append(permit_info['work_class'].lower())
        if permit_info.get('permit_class'):
            permit_parts.append(permit_info['permit_class'].lower())
        
        if permit_parts:
            permit_desc = " ".join(permit_parts)
            sentences.append(f"This is a {permit_desc} permit")
        
        # Add status information
        if permit_info.get('status'):
            status = permit_info['status'].lower()
            sentences.append(f"The permit status is currently {status}")
        
        # Add issue method
        if permit_info.get('issue_method'):
            issue_method = permit_info['issue_method'].lower()
            sentences.append(f"The permit was issued through {issue_method} method")
        
        # 3. LOCATION AND PROPERTY INFORMATION
        location = record.get('location', {})
        
        # Create location sentence
        location_parts = []
        if location.get('address'):
            location_parts.append(f"located at {location['address']}")
        if location.get('city'):
            location_parts.append(f"in {location['city']}")
        if location.get('state'):
            location_parts.append(f"{location['state']}")
        if location.get('zip_code'):
            location_parts.append(f"ZIP code {location['zip_code']}")
        
        if location_parts:
            location_sentence = "The property is " + ", ".join(location_parts)
            sentences.append(location_sentence)
        
        # Add council district information
        if location.get('council_district'):
            sentences.append(f"The property is located in Council District {location['council_district']}")
        
        # Add jurisdiction
        if location.get('jurisdiction'):
            sentences.append(f"The project falls under {location['jurisdiction']} jurisdiction")
        
        # Add legal description if available
        if location.get('legal_description'):
            sentences.append(f"The legal description of the property is {location['legal_description']}")
        
        # 4. CONTRACTOR AND CONSTRUCTION TEAM
        contractor = record.get('contractor', {})
        
        if contractor.get('contractor_company_name'):
            company_name = contractor['contractor_company_name']
            sentences.append(f"The contractor for this project is {company_name}")
            
            if contractor.get('contractor_trade'):
                trade = contractor['contractor_trade'].lower()
                sentences.append(f"The contractor specializes in {trade} work")
            
            if contractor.get('contractor_full_name'):
                contact_name = contractor['contractor_full_name']
                sentences.append(f"The primary contact person is {contact_name}")
            
            if contractor.get('contractor_phone'):
                phone = contractor['contractor_phone']
                sentences.append(f"The contractor can be reached at {phone}")
        
        # 5. APPLICANT AND OWNER INFORMATION
        applicant = record.get('applicant', {})
        
        if applicant.get('applicant_full_name'):
            applicant_name = applicant['applicant_full_name']
            sentences.append(f"The permit applicant is {applicant_name}")
            
            if applicant.get('applicant_organization'):
                org = applicant['applicant_organization']
                sentences.append(f"The applicant represents {org}")
        
        # 6. PROJECT SCOPE AND VALUATION
        valuation = record.get('valuation', {})
        
        # Total project value
        if valuation.get('total_job_valuation') and valuation['total_job_valuation'] > 0:
            total_value = valuation['total_job_valuation']
            sentences.append(f"The total project value is ${total_value:,.0f}")
        
        # Square footage information
        sqft_info = []
        if valuation.get('total_new_addition_sqft') and valuation['total_new_addition_sqft'] > 0:
            sqft_info.append(f"{valuation['total_new_addition_sqft']} square feet of new addition")
        if valuation.get('total_existing_building_sqft') and valuation['total_existing_building_sqft'] > 0:
            sqft_info.append(f"{valuation['total_existing_building_sqft']} square feet of existing building")
        if valuation.get('remodel_repair_sqft') and valuation['remodel_repair_sqft'] > 0:
            sqft_info.append(f"{valuation['remodel_repair_sqft']} square feet of remodel and repair work")
        
        if sqft_info:
            sentences.append(f"The project includes " + ", ".join(sqft_info))
        
        # Building characteristics
        if valuation.get('number_of_floors') and valuation['number_of_floors'] > 0:
            floors = valuation['number_of_floors']
            sentences.append(f"The building has {floors} floor{'s' if floors > 1 else ''}")
        
        if valuation.get('housing_units') and valuation['housing_units'] > 0:
            units = valuation['housing_units']
            sentences.append(f"The project includes {units} housing unit{'s' if units > 1 else ''}")
        
        if valuation.get('total_lot_sqft') and valuation['total_lot_sqft'] > 0:
            lot_size = valuation['total_lot_sqft']
            sentences.append(f"The lot size is {lot_size} square feet")
        
        # Trade-specific valuations
        trade_valuations = []
        for trade in ['building', 'electrical', 'mechanical', 'plumbing', 'medgas']:
            trade_val = valuation.get(f'{trade}_valuation')
            trade_remodel = valuation.get(f'{trade}_valuation_remodel')
            if trade_val and trade_val > 0:
                trade_valuations.append(f"${trade_val:,.0f} for {trade} work")
            if trade_remodel and trade_remodel > 0:
                trade_valuations.append(f"${trade_remodel:,.0f} for {trade} remodel work")
        
        if trade_valuations:
            sentences.append(f"Trade-specific valuations include " + ", ".join(trade_valuations))
        
        # 7. TIMELINE AND DATES
        dates = record.get('dates', {})
        
        if dates.get('applied_date'):
            applied_date = dates['applied_date'][:10]
            sentences.append(f"The permit application was submitted on {applied_date}")
        
        if dates.get('issue_date'):
            issue_date = dates['issue_date'][:10]
            sentences.append(f"The permit was issued on {issue_date}")
        
        if dates.get('expires_date'):
            expires_date = dates['expires_date'][:10]
            sentences.append(f"The permit expires on {expires_date}")
        
        if dates.get('completed_date'):
            completed_date = dates['completed_date'][:10]
            sentences.append(f"The project was completed on {completed_date}")
        
        if dates.get('calendar_year'):
            year = dates['calendar_year']
            sentences.append(f"This permit was processed in {year}")
        
        if dates.get('day_issued'):
            day = dates['day_issued']
            sentences.append(f"The permit was issued on a {day}")
        
        # 8. PROJECT RELATIONSHIPS AND REFERENCES
        project = record.get('project', {})
        
        if project.get('project_id'):
            project_id = project['project_id']
            sentences.append(f"The project ID is {project_id}")
        
        if project.get('master_permit_number'):
            master_permit = project['master_permit_number']
            sentences.append(f"This permit is associated with master permit {master_permit}")
        
        # 9. SPECIAL CONDITIONS AND FLAGS
        special_conditions = []
        
        if permit_info.get('condominium'):
            special_conditions.append("This is a condominium project")
        if permit_info.get('certificate_of_occupancy'):
            special_conditions.append("A certificate of occupancy is required")
        if permit_info.get('recently_issued'):
            special_conditions.append("This permit was recently issued")
        
        if special_conditions:
            sentences.append("Special conditions include: " + ", ".join(special_conditions))
        
        # 10. COMPREHENSIVE PROJECT SUMMARY
        summary_elements = []
        
        # Basic project type
        permit_class = permit_info.get('permit_class', '')
        work_class = permit_info.get('work_class', '')
        city = location.get('city', '')
        year = dates.get('calendar_year', '')
        
        if permit_class and work_class and city and year:
            summary_elements.append(f"a {permit_class.lower()} {work_class.lower()} permit in {city} from {year}")
        
        # Add project description if available
        if project_desc:
            summary_elements.append(f"involving {project_desc.lower()}")
        
        # Add location details
        if location.get('address'):
            summary_elements.append(f"at {location['address']}")
        
        # Add valuation if available
        if valuation.get('total_job_valuation') and valuation['total_job_valuation'] > 0:
            total_value = valuation['total_job_valuation']
            summary_elements.append(f"with a total value of ${total_value:,.0f}")
        
        if summary_elements:
            summary_sentence = "This project represents " + " ".join(summary_elements)
            sentences.append(summary_sentence)
        
        # Combine all sentences with natural flow
        text_block = ". ".join(sentences) + "."
        
        # Ensure the text block is not empty and has meaningful content
        if not text_block.strip() or text_block.strip() == ".":
            permit_number = record.get('permit_info', {}).get('permit_number', 'Unknown')
            text_block = f"This is building permit {permit_number} with limited information available for this permit record."
        
        # Truncate if too long (OpenAI has token limits)
        if len(text_block) > 4000:
            # Try to keep complete sentences
            truncated = text_block[:4000]
            last_period = truncated.rfind('.')
            if last_period > 3500:  # Only truncate at sentence boundary if it's not too far back
                text_block = truncated[:last_period + 1]
            else:
                text_block = truncated + "..."
            
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
