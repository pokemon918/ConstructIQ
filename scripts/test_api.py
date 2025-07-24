import requests
import json
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def test_api_health():
    """Test the API health endpoint."""
    print("🔍 Testing API Health...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is okay!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ API health check failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")

def test_search_endpoint(search_data: Dict[str, Any]):
    print(f"\n🔍 Testing Search: {search_data['query']}")
    if search_data.get('filters'):
        print(f"   Filters: {json.dumps(search_data['filters'], indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/search",
            json=search_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Search successful! Found {result['total_results']} results in {result['search_time_ms']}ms")
            
            for i, item in enumerate(result['results'], 1):
                print(f"\n  {i}. Score: {item['similarity_score']:.3f}")
                print(f"     Permit: {item['permit_number']}")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Search request failed: {e}")

def main():
    print("🚀 ConstructIQ API Test Suite")
    print("=" * 50)
    
    test_api_health()
    
    test_search_endpoint({
        "query": "residential construction",
        "top_k": 3
    })
    
    test_search_endpoint({
        "query": "commercial remodel downtown",
        "filters": {
            "permit_class": "Commercial",
            "calendar_year_issued": 2011
        },
        "top_k": 5
    })
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 