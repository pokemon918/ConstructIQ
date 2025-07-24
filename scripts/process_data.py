import json
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from utils.data_processor import PermitDataProcessor

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_raw_data(file_path: str) -> list:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} records from {file_path}")
        return data
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        raise

def main():
    try:
        # Initialize the data processor
        processor = PermitDataProcessor()
        
        # Find the most recent raw data file
        raw_data_dir = Path("data/raw")
        if not raw_data_dir.exists():
            logger.error("Raw data directory not found. Please run the data loading script first.")
            return 1
        
        # Get the most recent JSON file
        json_files = list(raw_data_dir.glob("*.json"))
        if not json_files:
            logger.error("No JSON files found in data/raw directory.")
            return 1
        
        # Sort by modification time and get the most recent
        latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
        logger.info(f"Processing file: {latest_file}")
        
        # Load raw data
        raw_data = load_raw_data(str(latest_file))
        
        # Normalize the records
        logger.info("Starting data normalization...")
        normalized_data = processor.normalize_records(raw_data)
        
        # Save normalized data
        output_path = processor.save_normalized_data(normalized_data)
        
        # Generate and display schema summary
        summary = processor.get_schema_summary(normalized_data)
        
        print("\n" + "="*60)
        print("📊 DATA NORMALIZATION SUMMARY")
        print("="*60)
        print(f"📁 Input file: {latest_file}")
        print(f"📁 Output file: {output_path}")
        print(f"📊 Total records processed: {summary['total_records']}")
        print(f"📋 Schema sections: {', '.join(summary['schema_sections'])}")
        
        print("\n🏗️  SCHEMA STRUCTURE:")
        for section in summary['schema_sections']:
            if section in summary['field_counts']:
                field_count = len(summary['field_counts'][section])
                print(f"  • {section}: {field_count} fields")
        
        print("\n✅ QUALITY METRICS:")
        quality = summary['quality_metrics']
        print(f"  • Valid records: {quality['valid_records']}")
        print(f"  • Invalid records: {quality['invalid_records']}")
        print(f"  • Average quality score: {quality['average_quality_score']:.2f}")
        
        # if normalized_data:
        #     print("\n📋 SAMPLE NORMALIZED RECORD STRUCTURE:")
        #     sample_record = normalized_data[0]
        #     for section, data in sample_record.items():
        #         if isinstance(data, dict):
        #             print(f"  • {section}:")
        #             for key, value in list(data.items())[:3]:  # Show first 3 fields
        #                 value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
        #                 print(f"    - {key}: {value_preview}")
        #             if len(data) > 3:
        #                 print(f"    ... and {len(data) - 3} more fields")
        #         else:
        #             print(f"  • {section}: {data}")
        
        print("\n✅ Data normalization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 