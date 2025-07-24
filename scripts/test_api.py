import requests
import json
import time
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

def test_api_health():
    """Test the API health endpoint."""
    print("🔍 Testing API Health...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API is healthy!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ API health check failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")

def test_search_endpoint(search_data: Dict[str, Any]):
    """Test the search endpoint with given data."""
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
                print(f"     Type: {item['permit_type']}")
                print(f"     Class: {item['permit_class']}")
                print(f"     Address: {item['address']}")
                print(f"     City: {item['city']}")
                print(f"     Year: {item['calendar_year_issued']}")
                if item['total_job_valuation']:
                    print(f"     Valuation: ${item['total_job_valuation']:,.0f}")
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Search request failed: {e}")

def test_sample_filters():
    """Test getting sample filters."""
    print("\n🔍 Testing Sample Filters Endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/filters/samples")
        if response.status_code == 200:
            print("✅ Sample filters retrieved successfully!")
            filters = response.json()
            print(f"Available sample filters: {list(filters['sample_filters'].keys())}")
        else:
            print(f"❌ Failed to get sample filters: {response.status_code}")
    except Exception as e:
        print(f"❌ Sample filters request failed: {e}")

def main():
    """Run all API tests."""
    print("🚀 ConstructIQ API Test Suite")
    print("=" * 50)
    
    # Test 1: Health check
    test_api_health()
    
    # Test 2: Sample filters
    test_sample_filters()
    
    # Test 3: Basic search without filters
    test_search_endpoint({
        "query": "residential construction",
        "top_k": 3
    })
    
    # Test 4: Search with your specific example
    test_search_endpoint({
        "query": "commercial remodel downtown",
        "filters": {
            "permit_type": "Commercial",
            "calendar_year_issued": 2023
        },
        "top_k": 5
    })
    
    # Test 5: Search with complex filters
    test_search_endpoint({
        "query": "electrical installation",
        "filters": {
            "permit_type": {"$in": ["Electrical Permit", "ELECTRICAL"]},
            "calendar_year_issued": {"$gte": 2024}
        },
        "top_k": 3
    })
    
    # Test 6: High value projects
    test_search_endpoint({
        "query": "luxury residential construction",
        "filters": {
            "permit_class": "Residential",
            "total_job_valuation": {"$gte": 500000}
        },
        "top_k": 3
    })
    
    # Test 7: Downtown commercial projects
    test_search_endpoint({
        "query": "office building construction",
        "filters": {
            "permit_class": "Commercial",
            "council_district": {"$in": [1, 2, 3, 4, 5]},
            "calendar_year_issued": {"$gte": 2023}
        },
        "top_k": 3
    })
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 