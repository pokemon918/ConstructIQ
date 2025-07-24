from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SearchFilters(BaseModel):
    permit_type: Optional[str] = Field(None, description="Type of permit")
    permit_class: Optional[str] = Field(None, description="Class of permit (Residential, Commercial, etc.)")
    work_class: Optional[str] = Field(None, description="Type of work (New, Remodel, Addition, etc.)")
    status: Optional[str] = Field(None, description="Permit status")
    calendar_year_issued: Optional[int] = Field(None, description="Year permit was issued")
    fiscal_year_issued: Optional[int] = Field(None, description="Fiscal year permit was issued")
    total_job_valuation: Optional[Dict[str, Any]] = Field(None, description="Total job valuation with operators")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State name")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    council_district: Optional[Dict[str, Any]] = Field(None, description="Council district with operators")
    contractor_company: Optional[str] = Field(None, description="Contractor company name")
    contractor_trade: Optional[str] = Field(None, description="Contractor trade type")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text", example="commercial remodel downtown")
    filters: Optional[SearchFilters] = Field(None, description="Optional filters to apply")
    top_k: Optional[int] = Field(5, description="Number of results to return", ge=1, le=50)


class SearchResult(BaseModel):
    record_id: str = Field(..., description="Unique record identifier")
    similarity_score: float = Field(..., description="Similarity score from vector search")
    permit_number: Optional[str] = Field(None, description="Permit number")
    permit_type: Optional[str] = Field(None, description="Type of permit")
    permit_class: Optional[str] = Field(None, description="Class of permit")
    work_class: Optional[str] = Field(None, description="Type of work")
    status: Optional[str] = Field(None, description="Permit status")
    address: Optional[str] = Field(None, description="Property address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State name")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    calendar_year_issued: Optional[int] = Field(None, description="Year permit was issued")
    total_job_valuation: Optional[float] = Field(None, description="Total job valuation")
    contractor_company: Optional[str] = Field(None, description="Contractor company name")
    contractor_trade: Optional[str] = Field(None, description="Contractor trade type")
    project_description: Optional[str] = Field(None, description="Project description")
    text_block: Optional[str] = Field(None, description="Text block used for embedding")


class SearchResponse(BaseModel):
    query: str = Field(..., description="Original search query")
    filters: Optional[SearchFilters] = Field(None, description="Applied filters")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    search_time_ms: float = Field(..., description="Search execution time in milliseconds") 