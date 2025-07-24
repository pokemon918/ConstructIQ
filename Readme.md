# ConstructIQ - Austin Building Permits Search API

A semantic search API for Austin building permits using vector embeddings and Pinecone vector database.

## Features

- 🔍 **Semantic Search**: Find permits using natural language queries
- 🎯 **Advanced Filtering**: Filter by permit type, year, location, valuation, and more
- ⚡ **Fast Performance**: Vector similarity search with sub-second response times
- 📊 **Rich Metadata**: Comprehensive permit information with similarity scores
- 🚀 **RESTful API**: Easy-to-use FastAPI endpoints

## Quick Start

### 1. Environment Setup

Create a `.env` file in the root directory:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment_here

# Optional: Pinecone Index Name
PINECONE_INDEX_NAME=austin-permits
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Index Your Data

First, make sure you have processed permit data in `data/processed/` directory, then run:

```bash
python scripts/create_embeddings.py
```

### 4. Start the FastAPI Server

**Option 1: Using the startup script (Recommended)**
```bash
python run.py
```

**Option 2: Using uvicorn directly**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Option 3: From the app directory**
```bash
cd app
python main.py
```

### 5. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Search Endpoint**: POST http://localhost:8000/api/v1/search

## API Usage

### Search Permits

**Endpoint**: `POST /api/v1/search`

**Request Body**:
```json
{
  "query": "commercial remodel downtown",
  "filters": {
    "permit_class": "Commercial",
    "calendar_year_issued": 2011
  },
  "top_k": 5
}
```

### Available Filters

The API supports filtering on all metadata fields. Here are the main categories:

#### Core Identifiers
- `permit_number`, `project_id`, `master_permit_number`

#### Permit Classification
- `permit_type`, `permit_type_description`, `permit_class`, `permit_class_original`, `work_class`, `status`, `issue_method`

#### Location Data
- `address`, `original_address`, `city`, `state`, `zip_code`, `council_district`, `jurisdiction`, `property_id`, `legal_description`, `latitude`, `longitude`, `total_lot_sqft`

#### Dates
- `applied_date`, `issue_date`, `expires_date`, `completed_date`, `calendar_year_issued`, `fiscal_year_issued`, `day_issued`

#### Valuation (Numeric with operators)
- `total_job_valuation`, `total_new_addition_sqft`, `total_existing_building_sqft`, `remodel_repair_sqft`, `total_valuation_remodel`, `number_of_floors`, `housing_units`

#### Trade-Specific Valuations
- `building_valuation`, `building_valuation_remodel`, `electrical_valuation`, `electrical_valuation_remodel`, `mechanical_valuation`, `mechanical_valuation_remodel`, `plumbing_valuation`, `plumbing_valuation_remodel`, `medgas_valuation`, `medgas_valuation_remodel`

#### Contractor Information
- `contractor_company`, `contractor_trade`, `contractor_full_name`, `contractor_phone`, `contractor_address1`, `contractor_address2`, `contractor_city`, `contractor_zip`

#### Applicant Information
- `applicant_name`, `applicant_organization`, `applicant_phone`, `applicant_address1`, `applicant_address2`, `applicant_city`, `applicant_zip`

#### Project Details
- `project_description`, `permit_link`

#### Boolean Flags
- `condominium`, `certificate_of_occupancy`, `recently_issued`

## Testing the API

Run the test suite to verify everything is working:

```bash
python scripts/test_api.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed service status |
| `/api/v1/search` | POST | Search permits with filters |

## Development

### Project Structure

```
ConstructIQ/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Application configuration
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── search.py        # Search request/response models
│   │   └── common.py        # Common response models
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── search.py        # Search endpoints
│   │   └── health.py        # Health check endpoints
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── permit.py        # Main permit service
│   │   ├── embedding.py     # OpenAI embedding service
│   │   └── vector_db.py     # Pinecone vector database service
│   └── utils/               # Utilities
│       ├── __init__.py
│       └── data_processor.py # Data processing utilities
├── data/
│   ├── raw/                 # Raw permit data
│   └── processed/           # Processed permit data
├── scripts/
│   ├── create_embeddings.py # Data indexing script
│   ├── example_search.py    # Search examples
│   └── test_api.py          # API test suite
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Start with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Performance

- **Search Response Time**: < 500ms for most queries
- **Vector Index**: Pinecone serverless for scalability
- **Embedding Model**: OpenAI text-embedding-3-small (1536 dimensions)
- **Batch Processing**: Configurable batch sizes for indexing

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your `.env` file has valid API keys
2. **Index Not Found**: Run `python scripts/create_embeddings.py` first
3. **Connection Errors**: Check if the FastAPI server is running on port 8000

### Logs

Check the console output for detailed logs and error messages.

## License

This project is for educational and demonstration purposes.
