from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class SearchFilters(BaseModel):
    # ===== CORE IDENTIFIERS =====
    permit_number: Optional[str] = Field(None, description="Permit number")
    project_id: Optional[str] = Field(None, description="Project ID")
    master_permit_number: Optional[str] = Field(None, description="Master permit number")
    
    # ===== PERMIT CLASSIFICATION =====
    permit_type: Optional[str] = Field(None, description="Type of permit")
    permit_type_description: Optional[str] = Field(None, description="Permit type description")
    permit_class: Optional[str] = Field(None, description="Class of permit (Residential, Commercial, etc.)")
    permit_class_original: Optional[str] = Field(None, description="Original permit class")
    work_class: Optional[str] = Field(None, description="Type of work (New, Remodel, Addition, etc.)")
    status: Optional[str] = Field(None, description="Permit status")
    issue_method: Optional[str] = Field(None, description="Issue method")
    
    # ===== LOCATION DATA =====
    address: Optional[str] = Field(None, description="Property address")
    original_address: Optional[str] = Field(None, description="Original address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State name")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    council_district: Optional[Any] = Field(None, description="Council district (integer, string, or operators dict)")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction")
    property_id: Optional[str] = Field(None, description="Property ID")
    legal_description: Optional[str] = Field(None, description="Legal description")
    latitude: Optional[Dict[str, Any]] = Field(None, description="Latitude with operators")
    longitude: Optional[Dict[str, Any]] = Field(None, description="Longitude with operators")
    total_lot_sqft: Optional[Dict[str, Any]] = Field(None, description="Total lot square footage with operators")
    
    # ===== DATES =====
    applied_date: Optional[str] = Field(None, description="Applied date")
    issue_date: Optional[str] = Field(None, description="Issue date")
    expires_date: Optional[str] = Field(None, description="Expires date")
    completed_date: Optional[str] = Field(None, description="Completed date")
    calendar_year_issued: Optional[int] = Field(None, description="Year permit was issued")
    fiscal_year_issued: Optional[int] = Field(None, description="Fiscal year permit was issued")
    day_issued: Optional[str] = Field(None, description="Day issued")
    
    # ===== VALUATION =====
    total_job_valuation: Optional[Any] = Field(None, description="Total job valuation (number or operators dict)")
    total_new_addition_sqft: Optional[Dict[str, Any]] = Field(None, description="Total new addition square footage with operators")
    total_existing_building_sqft: Optional[Dict[str, Any]] = Field(None, description="Total existing building square footage with operators")
    remodel_repair_sqft: Optional[Dict[str, Any]] = Field(None, description="Remodel repair square footage with operators")
    total_valuation_remodel: Optional[Dict[str, Any]] = Field(None, description="Total valuation remodel with operators")
    number_of_floors: Optional[Dict[str, Any]] = Field(None, description="Number of floors with operators")
    housing_units: Optional[Dict[str, Any]] = Field(None, description="Housing units with operators")
    
    # ===== TRADE-SPECIFIC VALUATIONS =====
    building_valuation: Optional[Dict[str, Any]] = Field(None, description="Building valuation with operators")
    building_valuation_remodel: Optional[Dict[str, Any]] = Field(None, description="Building valuation remodel with operators")
    electrical_valuation: Optional[Dict[str, Any]] = Field(None, description="Electrical valuation with operators")
    electrical_valuation_remodel: Optional[Dict[str, Any]] = Field(None, description="Electrical valuation remodel with operators")
    mechanical_valuation: Optional[Dict[str, Any]] = Field(None, description="Mechanical valuation with operators")
    mechanical_valuation_remodel: Optional[Dict[str, Any]] = Field(None, description="Mechanical valuation remodel with operators")
    plumbing_valuation: Optional[Dict[str, Any]] = Field(None, description="Plumbing valuation with operators")
    plumbing_valuation_remodel: Optional[Dict[str, Any]] = Field(None, description="Plumbing valuation remodel with operators")
    medgas_valuation: Optional[Dict[str, Any]] = Field(None, description="Medical gas valuation with operators")
    medgas_valuation_remodel: Optional[Dict[str, Any]] = Field(None, description="Medical gas valuation remodel with operators")
    
    # ===== CONTRACTOR INFORMATION =====
    contractor_company: Optional[str] = Field(None, description="Contractor company name")
    contractor_trade: Optional[str] = Field(None, description="Contractor trade type")
    contractor_full_name: Optional[str] = Field(None, description="Contractor full name")
    contractor_phone: Optional[str] = Field(None, description="Contractor phone")
    contractor_address1: Optional[str] = Field(None, description="Contractor address line 1")
    contractor_address2: Optional[str] = Field(None, description="Contractor address line 2")
    contractor_city: Optional[str] = Field(None, description="Contractor city")
    contractor_zip: Optional[str] = Field(None, description="Contractor ZIP code")
    
    # ===== APPLICANT INFORMATION =====
    applicant_name: Optional[str] = Field(None, description="Applicant name")
    applicant_organization: Optional[str] = Field(None, description="Applicant organization")
    applicant_phone: Optional[str] = Field(None, description="Applicant phone")
    applicant_address1: Optional[str] = Field(None, description="Applicant address line 1")
    applicant_address2: Optional[str] = Field(None, description="Applicant address line 2")
    applicant_city: Optional[str] = Field(None, description="Applicant city")
    applicant_zip: Optional[str] = Field(None, description="Applicant ZIP code")
    
    # ===== PROJECT DETAILS =====
    project_description: Optional[str] = Field(None, description="Project description")
    permit_link: Optional[str] = Field(None, description="Permit link")
    
    # ===== BOOLEAN FLAGS =====
    condominium: Optional[bool] = Field(None, description="Condominium flag")
    certificate_of_occupancy: Optional[bool] = Field(None, description="Certificate of occupancy flag")
    recently_issued: Optional[bool] = Field(None, description="Recently issued flag")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text", example="commercial remodel downtown")
    filters: Optional[SearchFilters] = Field(None, description="Optional filters to apply")
    top_k: Optional[int] = Field(5, description="Number of results to return", ge=1, le=50)


class SearchResult(BaseModel):
    record_id: str = Field(..., description="Unique record identifier")
    similarity_score: float = Field(..., description="Similarity score from vector search")
    
    # ===== CORE IDENTIFIERS =====
    permit_number: Optional[str] = Field(None, description="Permit number")
    project_id: Optional[str] = Field(None, description="Project ID")
    master_permit_number: Optional[str] = Field(None, description="Master permit number")
    
    # ===== PERMIT CLASSIFICATION =====
    permit_type: Optional[str] = Field(None, description="Type of permit")
    permit_type_description: Optional[str] = Field(None, description="Permit type description")
    permit_class: Optional[str] = Field(None, description="Class of permit")
    permit_class_original: Optional[str] = Field(None, description="Original permit class")
    work_class: Optional[str] = Field(None, description="Type of work")
    status: Optional[str] = Field(None, description="Permit status")
    issue_method: Optional[str] = Field(None, description="Issue method")
    
    # ===== LOCATION DATA =====
    address: Optional[str] = Field(None, description="Property address")
    original_address: Optional[str] = Field(None, description="Original address")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State name")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    council_district: Optional[Any] = Field(None, description="Council district (string or number)")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction")
    property_id: Optional[str] = Field(None, description="Property ID")
    legal_description: Optional[str] = Field(None, description="Legal description")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")
    total_lot_sqft: Optional[float] = Field(None, description="Total lot square footage")
    
    # ===== DATES =====
    applied_date: Optional[str] = Field(None, description="Applied date")
    issue_date: Optional[str] = Field(None, description="Issue date")
    expires_date: Optional[str] = Field(None, description="Expires date")
    completed_date: Optional[str] = Field(None, description="Completed date")
    calendar_year_issued: Optional[int] = Field(None, description="Year permit was issued")
    fiscal_year_issued: Optional[int] = Field(None, description="Fiscal year permit was issued")
    day_issued: Optional[str] = Field(None, description="Day issued")
    
    # ===== VALUATION =====
    total_job_valuation: Optional[float] = Field(None, description="Total job valuation")
    total_new_addition_sqft: Optional[float] = Field(None, description="Total new addition square footage")
    total_existing_building_sqft: Optional[float] = Field(None, description="Total existing building square footage")
    remodel_repair_sqft: Optional[float] = Field(None, description="Remodel repair square footage")
    total_valuation_remodel: Optional[float] = Field(None, description="Total valuation remodel")
    number_of_floors: Optional[int] = Field(None, description="Number of floors")
    housing_units: Optional[int] = Field(None, description="Housing units")
    
    # ===== TRADE-SPECIFIC VALUATIONS =====
    building_valuation: Optional[float] = Field(None, description="Building valuation")
    building_valuation_remodel: Optional[float] = Field(None, description="Building valuation remodel")
    electrical_valuation: Optional[float] = Field(None, description="Electrical valuation")
    electrical_valuation_remodel: Optional[float] = Field(None, description="Electrical valuation remodel")
    mechanical_valuation: Optional[float] = Field(None, description="Mechanical valuation")
    mechanical_valuation_remodel: Optional[float] = Field(None, description="Mechanical valuation remodel")
    plumbing_valuation: Optional[float] = Field(None, description="Plumbing valuation")
    plumbing_valuation_remodel: Optional[float] = Field(None, description="Plumbing valuation remodel")
    medgas_valuation: Optional[float] = Field(None, description="Medical gas valuation")
    medgas_valuation_remodel: Optional[float] = Field(None, description="Medical gas valuation remodel")
    
    # ===== CONTRACTOR INFORMATION =====
    contractor_company: Optional[str] = Field(None, description="Contractor company name")
    contractor_trade: Optional[str] = Field(None, description="Contractor trade type")
    contractor_full_name: Optional[str] = Field(None, description="Contractor full name")
    contractor_phone: Optional[str] = Field(None, description="Contractor phone")
    contractor_address1: Optional[str] = Field(None, description="Contractor address line 1")
    contractor_address2: Optional[str] = Field(None, description="Contractor address line 2")
    contractor_city: Optional[str] = Field(None, description="Contractor city")
    contractor_zip: Optional[str] = Field(None, description="Contractor ZIP code")
    
    # ===== APPLICANT INFORMATION =====
    applicant_name: Optional[str] = Field(None, description="Applicant name")
    applicant_organization: Optional[str] = Field(None, description="Applicant organization")
    applicant_phone: Optional[str] = Field(None, description="Applicant phone")
    applicant_address1: Optional[str] = Field(None, description="Applicant address line 1")
    applicant_address2: Optional[str] = Field(None, description="Applicant address line 2")
    applicant_city: Optional[str] = Field(None, description="Applicant city")
    applicant_zip: Optional[str] = Field(None, description="Applicant ZIP code")
    
    # ===== PROJECT DETAILS =====
    project_description: Optional[str] = Field(None, description="Project description")
    permit_link: Optional[str] = Field(None, description="Permit link")
    
    # ===== BOOLEAN FLAGS =====
    condominium: Optional[bool] = Field(None, description="Condominium flag")
    certificate_of_occupancy: Optional[bool] = Field(None, description="Certificate of occupancy flag")
    recently_issued: Optional[bool] = Field(None, description="Recently issued flag")


class SearchResponse(BaseModel):
    query: str = Field(..., description="Original search query")
    results: List[SearchResult] = Field(..., description="Search results")
    total_results: int = Field(..., description="Total number of results")
    search_time_ms: float = Field(..., description="Search execution time in milliseconds") 