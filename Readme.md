# ConstructIQ - Semantic API Prototype

A FastAPI-based semantic search API for construction permit data from the City of Austin.

## 🎯 Project Overview

This project implements a semantic search system for construction permit data that:
- Normalizes raw permit records into a clean schema
- Embeds permit data using OpenAI's text-embedding-3-small
- Indexes data in a vector database for semantic search
- Exposes a RESTful API with filtering and query logging capabilities

## 🏗️ Project Structure

```
ConstructIQ/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration management
│   ├── models/            # Data models and schemas
│   │   ├── __init__.py
│   │   ├── permit.py      # Permit data models
│   │   └── api.py         # API request/response models
│   ├── services/          # Business logic
│   │   ├── __init__.py
│   │   ├── embedding.py   # OpenAI embedding service
│   │   ├── vector_db.py   # Vector database operations
│   │   └── permit.py      # Permit data processing
│   ├── api/               # API routes
│   │   ├── __init__.py
│   │   ├── search.py      # Search endpoint
│   │   └── health.py      # Health check endpoint
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── logger.py      # Logging configuration
│       └── data_processor.py # Data normalization utilities
├── data/                  # Data files
│   ├── raw/              # Raw permit data
│   └── processed/        # Normalized permit data
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_services.py
│   └── test_utils.py
├── scripts/              # Utility scripts
│   ├── load_data.py      # Data loading script
│   ├── process_data.py   # Data processing script
│   ├── create_embeddings.py # Embedding and indexing pipeline
│   └── example_usage.py  # Example usage demonstration
├── docs/                 # Documentation
│   └── api.md           # API documentation
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Local development setup
└── README.md           # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key
- Pinecone API key and environment

### Installation

1. **Clone and setup environment:**
```bash
git clone <repository-url>
cd ConstructIQ
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Load and process data:**
```bash
# Load raw data from Austin API
python scripts/load_data.py

# Process and normalize data
python scripts/process_data.py

# Create embeddings and index in Pinecone
python scripts/create_embeddings.py
```

4. **Run the application:**
```bash
uvicorn app.main:app --reload
```

5. **Access the API:**
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/healthz
- Search Endpoint: POST http://localhost:8000/search

## 📊 Data Schema

The normalized permit schema groups fields logically:

```json
{
  "metadata": {
    "record_id": "string",
    "validation_status": "string"
  },
  "permit_info": {
    "permit_number": "string",
    "permit_type": "string",
    "permit_type_description": "string",
    "permit_class": "string",
    "work_class": "string",
    "status": "string",
    "description": "string"
  },
  "location": {
    "address": "string",
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "latitude": "float",
    "longitude": "float",
    "council_district": "string"
  },
  "dates": {
    "applied_date": "string",
    "issue_date": "string",
    "calendar_year": "string",
    "expires_date": "string"
  },
  "project": {
    "project_id": "string",
    "master_permit_number": "string"
  },
  "valuation": {
    "total_job_valuation": "float",
    "total_new_addition_sqft": "float",
    "total_existing_building_sqft": "float"
  },
  "contractor": {
    "contractor_company_name": "string",
    "contractor_trade": "string",
    "contractor_full_name": "string"
  },
  "applicant": {
    "applicant_full_name": "string",
    "applicant_organization": "string"
  }
}
```

## 🔍 Embedding and Vector Search

The system uses OpenAI's `text-embedding-3-small` model to create semantic embeddings from permit records. Text blocks are constructed from relevant fields:

- **Description**: Permit description and work details
- **Permit Type**: Type and classification information
- **Work Class**: Specific work category
- **Location**: Address and geographic information
- **Contractor**: Contractor company and trade information
- **Applicant**: Applicant name and organization
- **Valuation**: Project value and square footage

### Search Capabilities

- **Semantic Search**: Find permits by natural language queries
- **Filtered Search**: Combine semantic search with metadata filters
- **Vector Similarity**: Direct vector similarity search
- **Metadata Filtering**: Filter by permit type, location, dates, valuation, etc.

## 🔍 API Endpoints

### POST /search
Semantic search for permits with filtering capabilities.

**Request:**
```json
{
  "query": "commercial remodel downtown",
  "filters": {
    "permit_type": "Commercial",
    "calendar_year_issued": 2023
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "permit_id": "string",
      "similarity_score": 0.95,
      "permit_data": { ... }
    }
  ],
  "total_results": 5,
  "query_time_ms": 150
}
```

### GET /healthz
Health check endpoint.

### GET /docs
Interactive API documentation (Swagger UI).

## 🛠️ Development

### Running the Embedding Pipeline

1. **Load raw data:**
```bash
python scripts/load_data.py
```

2. **Process and normalize data:**
```bash
python scripts/process_data.py
```

3. **Create embeddings and index:**
```bash
python scripts/create_embeddings.py --raw-data data/raw/austin_permits.json --index-name austin-permits-v1
```

4. **Test search functionality:**
```bash
python scripts/example_usage.py
```

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/ tests/
isort app/ tests/
```

### Type Checking
```bash
mypy app/
```

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t constructiq-api .
docker run -p 8000:8000 constructiq-api
```

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENVIRONMENT`: Your Pinecone environment (e.g., "us-east-1-aws")
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## 📝 Logging

The application logs:
- Search queries with timestamps
- Applied filters
- Top result IDs
- Performance metrics

Logs are written to both console and file for analytics support.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is part of the ConstructIQ technical challenge.
