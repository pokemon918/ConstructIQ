import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services import PermitService

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_environment_variables():
    required_vars = ['OPENAI_API_KEY', 'PINECONE_API_KEY', 'PINECONE_ENVIRONMENT']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set these variables in your .env file or environment")
        return False
    
    return True

def run_complete_pipeline(processed_data_path: str, index_name: str, batch_size: int):
    logger.info("=" * 60)
    logger.info("STARTING AUSTIN PERMIT EMBEDDING PIPELINE")
    logger.info("=" * 60)
    
    # Initialize the permit service
    try:
        permit_service = PermitService()
        logger.info("Permit service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize permit service: {e}")
        return False
    
    # Check service status
    logger.info("Checking service status...")
    status = permit_service.get_service_status()
    logger.info(f"Service status: {json.dumps(status, indent=2)}")
    
    # Run the complete pipeline
    try:
        stats = permit_service.process_and_index_data(
            processed_data_path="data/processed/normalized_permits_20250723_132411.json",
            index_name=index_name,
            batch_size=batch_size
        )
        
        # Log final statistics
        logger.info("=" * 60)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info(f"Final statistics: {json.dumps(stats, indent=2)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return False


def main():
    """Main function to run the embedding pipeline."""
    parser = argparse.ArgumentParser(description='Process Austin permit data and create embeddings')
    parser.add_argument('--processed-data', 
                       default='data/processed/normalized_permits_20250723_132411.json',
                       help='Path to processed JSON data file')
    parser.add_argument('--index-name', 
                       default='austin-permits',
                       help='Name of the Pinecone index')
    parser.add_argument('--batch-size', 
                       type=int, 
                       default=100,
                       help='Batch size for processing')
    parser.add_argument('--skip-pipeline', 
                       action='store_true',
                       help='Skip the main pipeline and only run demonstrations')
    parser.add_argument('--demo-only', 
                       action='store_true',
                       help='Only run search demonstrations')
    
    args = parser.parse_args()
    
    # Check environment variables
    if not load_environment_variables():
        sys.exit(1)
    
    # Check if processed data file exists
    if not args.skip_pipeline and not os.path.exists(args.processed_data):
        logger.error(f"Processed data file not found: {args.processed_data}")
        logger.error("Please ensure the processed data file exists")
        sys.exit(1)
    
    # Run pipeline if not skipped
    if not args.skip_pipeline and not args.demo_only:
        success = run_complete_pipeline(
            processed_data_path=args.processed_data,
            index_name=args.index_name,
            batch_size=args.batch_size
        )
        
        if not success:
            logger.error("Pipeline failed. Exiting.")
            sys.exit(1)

if __name__ == "__main__":
    main()