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
    
    # Check service status
    print("\nChecking service status...")
    status = permit_service.get_service_status()

    print(status)
    
    print("\n" + "="*50)
    print("EXAMPLE SEARCHES")
    print("="*50)
    
    search_queries = [
        "residential construction"
    ]
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        try:
            results = permit_service.search_permits(
                query_text=query,
                top_k=5,
                index_name="austin-permits"
            )
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                metadata = result.metadata
                print(f"  {i}. Score: {result.score:.3f}")
                print(f"     Permit: {metadata.get('permit_number', 'N/A')}")
                print(f"     Type: {metadata.get('permit_type', 'N/A')}")
                print(f"     Address: {metadata.get('city', 'N/A')}")
                print()
                
        except Exception as e:
            print(f"Search failed: {e}")

if __name__ == "__main__":
    main() 