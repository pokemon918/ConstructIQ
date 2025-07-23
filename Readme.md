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
│   ├── setup_db.py       # Database setup
│   └── load_data.py      # Data loading script
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
- Vector database (Chroma, Pinecone, or pgvector)

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

3. **Setup database and load data:**
```bash
python scripts/setup_db.py
python scripts/load_data.py
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
  "permit_id": "string",
  "basic_info": {
    "permit_type": "string",
    "work_class": "string",
    "description": "string",
    "status": "string"
  },
  "location": {
    "address": "string",
    "city": "string",
    "state": "string",
    "zip_code": "string"
  },
  "timeline": {
    "date_issued": "date",
    "calendar_year_issued": "integer",
    "expiration_date": "date"
  },
  "valuation": {
    "total_value": "decimal",
    "fee": "decimal"
  },
  "contractor": {
    "contractor_name": "string",
    "contractor_license": "string"
  }
}
```

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
- `VECTOR_DB_URL`: Vector database connection string
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
