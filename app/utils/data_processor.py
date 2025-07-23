import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)

class PermitDataProcessor:    
    def __init__(self):
        self.field_mappings = self._create_field_mappings()
        self.required_fields = self._get_required_fields()
    
    def _create_field_mappings(self) -> Dict[str, str]:
        return {
            # Permit Information
            'permittype': 'permit_type',
            'permit_type_desc': 'permit_type_description',
            'permit_number': 'permit_number',
            'permit_class_mapped': 'permit_class',
            'permit_class': 'permit_class_original',
            'work_class': 'work_class',
            'status_current': 'status',
            'statusdate': 'status_date',
            'condominium': 'condominium',
            
            # Location Information
            'permit_location': 'address',
            'original_address1': 'original_address',
            'original_city': 'city',
            'original_state': 'state',
            'original_zip': 'zip_code',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'tcad_id': 'property_id',
            'legal_description': 'legal_description',
            'council_district': 'council_district',
            'jurisdiction': 'jurisdiction',
            'location': 'location_coordinates',
            
            # Dates
            'applieddate': 'applied_date',
            'issue_date': 'issue_date',
            'day_issued': 'day_issued',
            'calendar_year_issued': 'calendar_year',
            'fiscal_year_issued': 'fiscal_year',
            'expiresdate': 'expires_date',
            'completed_date': 'completed_date',
            'issued_in_last_30_days': 'recently_issued',
            
            # Project Information
            'description': 'description',
            'project_id': 'project_id',
            'masterpermitnum': 'master_permit_number',
            'issue_method': 'issue_method',
            
            # Valuation Information
            'total_existing_bldg_sqft': 'total_existing_building_sqft',
            'remodel_repair_sqft': 'remodel_repair_sqft',
            'total_new_add_sqft': 'total_new_addition_sqft',
            'total_valuation_remodel': 'total_valuation_remodel',
            'total_job_valuation': 'total_job_valuation',
            'number_of_floors': 'number_of_floors',
            'housing_units': 'housing_units',
            'building_valuation': 'building_valuation',
            'building_valuation_remodel': 'building_valuation_remodel',
            'electrical_valuation': 'electrical_valuation',
            'electrical_valuation_remodel': 'electrical_valuation_remodel',
            'mechanical_valuation': 'mechanical_valuation',
            'mechanical_valuation_remodel': 'mechanical_valuation_remodel',
            'plumbing_valuation': 'plumbing_valuation',
            'plumbing_valuation_remodel': 'plumbing_valuation_remodel',
            'medgas_valuation': 'medgas_valuation',
            'medgas_valuation_remodel': 'medgas_valuation_remodel',
            'total_lot_sq_ft': 'total_lot_sqft',
            
            # Contractor Information
            'contractor_trade': 'contractor_trade',
            'contractor_company_name': 'contractor_company_name',
            'contractor_full_name': 'contractor_full_name',
            'contractor_phone': 'contractor_phone',
            'contractor_address1': 'contractor_address1',
            'contractor_address2': 'contractor_address2',
            'contractor_city': 'contractor_city',
            'contractor_zip': 'contractor_zip',
            
            # Applicant Information
            'applicant_full_name': 'applicant_full_name',
            'applicant_org': 'applicant_organization',
            'applicant_phone': 'applicant_phone',
            'applicant_address1': 'applicant_address1',
            'applicant_address2': 'applicant_address2',
            'applicant_city': 'applicant_city',
            'applicantzip': 'applicant_zip',
            
            # Certificate Information
            'certificate_of_occupancy': 'certificate_of_occupancy',
            
            # Geographic Regions
            ':@computed_region_8spj_utxs': 'region_8spj_utxs',
            ':@computed_region_q9nd_rr82': 'region_q9nd_rr82',
            ':@computed_region_e9j2_6w3z': 'region_e9j2_6w3z',
            ':@computed_region_m2th_e4b7': 'region_m2th_e4b7',
            ':@computed_region_rxpj_nzrk': 'region_rxpj_nzrk',
            ':@computed_region_a3it_2a2z': 'region_a3it_2a2z',
            ':@computed_region_qwte_z96m': 'region_qwte_z96m',
            ':@computed_region_i2aj_cj5t': 'region_i2aj_cj5t',
            ':@computed_region_xzeg_zdjk': 'region_xzeg_zdjk',
            ':@computed_region_6gig_z43c': 'region_6gig_z43c',
            
            # Links
            'link': 'permit_link'
        }
    
    def _get_required_fields(self) -> List[str]:
        return [
            'permit_number',
            'permit_type',
            'address',
            'city',
            'state',
            'zip_code',
            'applied_date',
            'issue_date',
            'status'
        ]
    
    def normalize_records(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Starting normalization of {len(raw_data)} records")
        
        normalized_records = []
        for i, record in enumerate(raw_data):
            try:
                normalized_record = self._normalize_single_record(record)
                normalized_records.append(normalized_record)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"Normalized {i + 1} records...")
                    
            except Exception as e:
                logger.error(f"Error normalizing record {i}: {e}")
                continue
        
        logger.info(f"Successfully normalized {len(normalized_records)} records")
        return normalized_records
    
    def _normalize_single_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        normalized = {
            'permit_info': self._extract_permit_info(record),
            'location': self._extract_location_info(record),
            'dates': self._extract_date_info(record),
            'project': self._extract_project_info(record),
            'valuation': self._extract_valuation_info(record),
            'contractor': self._extract_contractor_info(record),
            'applicant': self._extract_applicant_info(record),
            'geographic': self._extract_geographic_info(record),
            'metadata': self._extract_metadata(record)
        }
        
        # Add validation and quality indicators
        normalized['validation'] = self._validate_record(normalized)
        
        return normalized
    
    def _extract_permit_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'permit_number': self._safe_get(record, 'permit_number'),
            'permit_type': self._safe_get(record, 'permit_type'),
            'permit_type_description': self._safe_get(record, 'permit_type_desc'),
            'permit_class': self._safe_get(record, 'permit_class_mapped'),
            'permit_class_original': self._safe_get(record, 'permit_class'),
            'work_class': self._safe_get(record, 'work_class'),
            'status': self._safe_get(record, 'status_current'),
            'status_date': self._parse_date(self._safe_get(record, 'statusdate')),
            'issue_method': self._safe_get(record, 'issue_method'),
            'recently_issued': self._parse_boolean(self._safe_get(record, 'issued_in_last_30_days')),
            'condominium': self._parse_boolean(self._safe_get(record, 'condominium')),
            'certificate_of_occupancy': self._parse_boolean(self._safe_get(record, 'certificate_of_occupancy'))
        }
    
    def _extract_location_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'address': self._safe_get(record, 'permit_location'),
            'original_address': self._safe_get(record, 'original_address1'),
            'city': self._safe_get(record, 'original_city'),
            'state': self._safe_get(record, 'original_state'),
            'zip_code': self._safe_get(record, 'original_zip'),
            'latitude': self._parse_float(self._safe_get(record, 'latitude')),
            'longitude': self._parse_float(self._safe_get(record, 'longitude')),
            'property_id': self._safe_get(record, 'tcad_id'),
            'legal_description': self._safe_get(record, 'legal_description'),
            'council_district': self._parse_int(self._safe_get(record, 'council_district')),
            'jurisdiction': self._safe_get(record, 'jurisdiction'),
            'location_coordinates': self._safe_get(record, 'location'),
            'total_lot_sqft': self._parse_float(self._safe_get(record, 'total_lot_sq_ft'))
        }
    
    def _extract_date_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'applied_date': self._parse_date(self._safe_get(record, 'applieddate')),
            'issue_date': self._parse_date(self._safe_get(record, 'issue_date')),
            'day_issued': self._safe_get(record, 'day_issued'),
            'calendar_year': self._parse_int(self._safe_get(record, 'calendar_year_issued')),
            'fiscal_year': self._parse_int(self._safe_get(record, 'fiscal_year_issued')),
            'expires_date': self._parse_date(self._safe_get(record, 'expiresdate')),
            'completed_date': self._parse_date(self._safe_get(record, 'completed_date'))
        }
    
    def _extract_project_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'description': self._safe_get(record, 'description'),
            'project_id': self._safe_get(record, 'project_id'),
            'master_permit_number': self._safe_get(record, 'masterpermitnum'),
            'permit_link': self._extract_link(self._safe_get(record, 'link'))
        }
    
    def _extract_valuation_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize valuation information."""
        return {
            'total_existing_building_sqft': self._parse_float(self._safe_get(record, 'total_existing_bldg_sqft')),
            'remodel_repair_sqft': self._parse_float(self._safe_get(record, 'remodel_repair_sqft')),
            'total_new_addition_sqft': self._parse_float(self._safe_get(record, 'total_new_add_sqft')),
            'total_valuation_remodel': self._parse_float(self._safe_get(record, 'total_valuation_remodel')),
            'total_job_valuation': self._parse_float(self._safe_get(record, 'total_job_valuation')),
            'number_of_floors': self._parse_int(self._safe_get(record, 'number_of_floors')),
            'housing_units': self._parse_int(self._safe_get(record, 'housing_units')),
            'building_valuation': self._parse_float(self._safe_get(record, 'building_valuation')),
            'building_valuation_remodel': self._parse_float(self._safe_get(record, 'building_valuation_remodel')),
            'electrical_valuation': self._parse_float(self._safe_get(record, 'electrical_valuation')),
            'electrical_valuation_remodel': self._parse_float(self._safe_get(record, 'electrical_valuation_remodel')),
            'mechanical_valuation': self._parse_float(self._safe_get(record, 'mechanical_valuation')),
            'mechanical_valuation_remodel': self._parse_float(self._safe_get(record, 'mechanical_valuation_remodel')),
            'plumbing_valuation': self._parse_float(self._safe_get(record, 'plumbing_valuation')),
            'plumbing_valuation_remodel': self._parse_float(self._safe_get(record, 'plumbing_valuation_remodel')),
            'medgas_valuation': self._parse_float(self._safe_get(record, 'medgas_valuation')),
            'medgas_valuation_remodel': self._parse_float(self._safe_get(record, 'medgas_valuation_remodel'))
        }
    
    def _extract_contractor_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize contractor information."""
        return {
            'contractor_trade': self._safe_get(record, 'contractor_trade'),
            'contractor_company_name': self._safe_get(record, 'contractor_company_name'),
            'contractor_full_name': self._safe_get(record, 'contractor_full_name'),
            'contractor_phone': self._safe_get(record, 'contractor_phone'),
            'contractor_address1': self._safe_get(record, 'contractor_address1'),
            'contractor_address2': self._safe_get(record, 'contractor_address2'),
            'contractor_city': self._safe_get(record, 'contractor_city'),
            'contractor_zip': self._safe_get(record, 'contractor_zip')
        }
    
    def _extract_applicant_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize applicant information."""
        return {
            'applicant_full_name': self._safe_get(record, 'applicant_full_name'),
            'applicant_organization': self._safe_get(record, 'applicant_org'),
            'applicant_phone': self._safe_get(record, 'applicant_phone'),
            'applicant_address1': self._safe_get(record, 'applicant_address1'),
            'applicant_address2': self._safe_get(record, 'applicant_address2'),
            'applicant_city': self._safe_get(record, 'applicant_city'),
            'applicant_zip': self._safe_get(record, 'applicantzip')
        }
    
    def _extract_geographic_info(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'region_8spj_utxs': self._parse_int(self._safe_get(record, ':@computed_region_8spj_utxs')),
            'region_q9nd_rr82': self._parse_int(self._safe_get(record, ':@computed_region_q9nd_rr82')),
            'region_e9j2_6w3z': self._parse_int(self._safe_get(record, ':@computed_region_e9j2_6w3z')),
            'region_m2th_e4b7': self._parse_int(self._safe_get(record, ':@computed_region_m2th_e4b7')),
            'region_rxpj_nzrk': self._parse_int(self._safe_get(record, ':@computed_region_rxpj_nzrk')),
            'region_a3it_2a2z': self._parse_int(self._safe_get(record, ':@computed_region_a3it_2a2z')),
            'region_qwte_z96m': self._parse_int(self._safe_get(record, ':@computed_region_qwte_z96m')),
            'region_i2aj_cj5t': self._parse_int(self._safe_get(record, ':@computed_region_i2aj_cj5t')),
            'region_xzeg_zdjk': self._parse_int(self._safe_get(record, ':@computed_region_xzeg_zdjk')),
            'region_6gig_z43c': self._parse_int(self._safe_get(record, ':@computed_region_6gig_z43c'))
        }
    
    def _extract_metadata(self, record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            'raw_field_count': len(record),
            'processing_timestamp': datetime.now().isoformat(),
            'data_source': 'Austin Texas Government API',
            'record_id': self._generate_record_id(record)
        }
    
    def _validate_record(self, normalized_record: Dict[str, Any]) -> Dict[str, Any]:
        validation = {
            'is_valid': True,
            'missing_required_fields': [],
            'quality_score': 1.0,
            'issues': []
        }
        
        # Check required fields
        required_fields = [
            ('permit_info', 'permit_number'),
            ('permit_info', 'permit_type'),
            ('location', 'address'),
            ('location', 'city'),
            ('location', 'state'),
            ('location', 'zip_code'),
            ('dates', 'applied_date'),
            ('dates', 'issue_date'),
            ('permit_info', 'status')
        ]
        
        missing_fields = []
        for section, field in required_fields:
            if not normalized_record.get(section, {}).get(field):
                missing_fields.append(f"{section}.{field}")
        
        if missing_fields:
            validation['missing_required_fields'] = missing_fields
            validation['is_valid'] = False
            validation['quality_score'] = max(0.0, 1.0 - (len(missing_fields) / len(required_fields)))
            validation['issues'].append(f"Missing {len(missing_fields)} required fields")
        
        # Check for data quality issues
        location = normalized_record.get('location', {})
        if location.get('latitude') and location.get('longitude'):
            lat, lon = location['latitude'], location['longitude']
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                validation['issues'].append("Invalid coordinates")
                validation['quality_score'] *= 0.9
        
        return validation
    
    def _safe_get(self, record: Dict[str, Any], field: str) -> Any:
        value = record.get(field)
        return None if value == '' or value is None else value
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        if not date_str:
            return None
        
        try:
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            
            return dt.isoformat()
        except (ValueError, TypeError):
            logger.warning(f"Could not parse date: {date_str}")
            return None
    
    def _parse_float(self, value: Any) -> Optional[float]:
        if value is None or value == '':
            return None
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_int(self, value: Any) -> Optional[int]:
        if value is None or value == '':
            return None
        
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
    def _parse_boolean(self, value: Any) -> Optional[bool]:
        if value is None or value == '':
            return None
        
        if isinstance(value, bool):
            return value
        
        value_str = str(value).lower().strip()
        if value_str in ('yes', 'true', '1', 'y'):
            return True
        elif value_str in ('no', 'false', '0', 'n'):
            return False
        
        return None
    
    def _extract_link(self, link_data: Any) -> Optional[str]:
        if isinstance(link_data, dict):
            return link_data.get('url')
        elif isinstance(link_data, str):
            return link_data
        return None
    
    def _generate_record_id(self, record: Dict[str, Any]) -> str:
        permit_num = record.get('permit_number', '')
        project_id = record.get('project_id', '')
        return f"{permit_num}_{project_id}" if permit_num and project_id else f"record_{hash(str(record))}"
    
    def save_normalized_data(self, normalized_data: List[Dict[str, Any]], 
                           output_path: str = "data/processed") -> str:
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"normalized_permits_{timestamp}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(normalized_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(normalized_data)} normalized records to {filepath}")
        return str(filepath)
    
    def get_schema_summary(self, normalized_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not normalized_data:
            return {}
        
        summary = {
            'total_records': len(normalized_data),
            'schema_sections': list(normalized_data[0].keys()),
            'field_counts': {},
            'quality_metrics': {
                'valid_records': 0,
                'invalid_records': 0,
                'average_quality_score': 0.0
            }
        }
        
        for record in normalized_data:
            for section, data in record.items():
                if section not in summary['field_counts']:
                    summary['field_counts'][section] = {}
                
                if isinstance(data, dict):
                    for field in data.keys():
                        summary['field_counts'][section][field] = summary['field_counts'][section].get(field, 0) + 1
            
            validation = record.get('validation', {})
            if validation.get('is_valid', False):
                summary['quality_metrics']['valid_records'] += 1
            else:
                summary['quality_metrics']['invalid_records'] += 1
            
            summary['quality_metrics']['average_quality_score'] += validation.get('quality_score', 0.0)
        
        if normalized_data:
            summary['quality_metrics']['average_quality_score'] /= len(normalized_data)
        
        return summary
