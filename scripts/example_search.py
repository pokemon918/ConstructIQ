import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.services import PermitService

load_dotenv()

def main():    
    # Check environment variables
    required_vars = ['OPENAI_API_KEY', 'PINECONE_API_KEY', 'PINECONE_ENVIRONMENT']
    for var in required_vars:
        if not os.getenv(var):
            print(f"Error: {var} environment variable is required")
            return
    
    # Initialize the permit service
    print("Initializing permit service...")
    permit_service = PermitService()
    
    print("\n" + "="*60)
    print("EXAMPLE SEARCHES WITH FILTERS")
    print("="*60)
    
    # Define search examples with filters
    search_examples = [
        {
            "query": "commercial remodel downtown",
            "filters": {
                "permit_class": "Commercial",
                "calendar_year_issued":2011
            }
        }
    ]
    
    for example in search_examples:
        print(f"\n{'='*50}")
        print(f"{'='*50}")
        print(f"Query: '{example['query']}'")
        print(f"Filters: {json.dumps(example['filters'], indent=2)}")
        
        try:
            results = permit_service.search_permits(
                query_text=example['query'],
                top_k=5,
                index_name="austin-permits",
                filter_dict=example['filters']
            )
            
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                metadata = result.metadata
                print(f"\n  {i}. Score: {result.score:.3f}")
                print(f"     metadata: {metadata}")
                
        except Exception as e:
            print(f"Search failed: {e}")
    
    print(f"\n{'='*60}")
    print("SAMPLE FILTERS AVAILABLE")
    print("="*60)
    
    # Show available sample filters
    # sample_filters = permit_service.create_sample_filters()
    # for filter_name, filter_dict in sample_filters.items():
    #     print(f"\n{filter_name}:")
    #     print(f"  {json.dumps(filter_dict, indent=2)}")

if __name__ == "__main__":
    main() 