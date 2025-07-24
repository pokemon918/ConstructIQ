import requests
import json
import os
import csv
import io
from datetime import datetime
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AustinDataLoader:    
    def __init__(self, base_url=os.getenv("DATASET_API_URL")):
        self.base_url = base_url
        self.data_dir = Path("data/raw")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def fetch_data(self, limit=50, offset=0):
        try:
            # Construct the URL with query parameters
            url = f"{self.base_url}?$limit={limit}&$offset={offset}"
            logger.info(f"Fetching data from: {url}")
            
            # Make the request
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV response
            csv_text = response.text
            logger.info(f"Received CSV data: {len(csv_text)} characters")
            
            # Parse CSV data
            data = self._parse_csv_data(csv_text)
            logger.info(f"Successfully parsed {len(data)} records")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing CSV response: {e}")
            raise
    
    def _parse_csv_data(self, csv_text):
        try:
            csv_file = io.StringIO(csv_text)
            reader = csv.DictReader(csv_file)
            data = []
            for row in reader:
                processed_row = {}
                for key, value in row.items():
                    processed_row[key] = None if value == '' else value
                data.append(processed_row)
            
            logger.info(f"Parsed CSV with {len(data)} records and {len(data[0]) if data else 0} fields")
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing CSV data: {e}")
            raise
    
    def save_to_json(self, data, filename=None):
        try:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"austin_permits_{timestamp}.json"
            
            filepath = self.data_dir / filename
            
            # Save data with pretty formatting
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data saved to: {filepath}")
            logger.info(f"Total records saved: {len(data)}")
            
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving data to JSON: {e}")
            raise
    
    def load_and_save(self, limit=50, offset=0, filename=None):
        logger.info("Starting data loading process...")
        
        # Fetch data
        data = self.fetch_data(limit=limit, offset=offset)
        
        # Save to JSON
        filepath = self.save_to_json(data, filename=filename)
        
        logger.info("Data loading process completed successfully!")
        return filepath

def main():
    try:
        # Initialize the data loader
        loader = AustinDataLoader()
        
        # Get environment variables with defaults
        limit = int(os.getenv("LIMIT", "10"))
        offset = int(os.getenv("OFFSET", "0"))
        
        filepath = loader.load_and_save(limit=limit, offset=offset)
        
        print(f"\n✅ Data successfully loaded and saved to: {filepath}")
        print(f"📁 File location: {filepath.absolute()}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📊 Total records: {len(data)}")
        
        if data:
            print(f"📋 Total fields per record: {len(data[0])}")
        
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
