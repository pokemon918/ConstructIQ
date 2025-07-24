from fastapi import APIRouter, HTTPException, Depends
import time
import logging

from ..models.search import SearchRequest, SearchResponse, SearchResult
from ..services.permit import PermitService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])

def get_permit_service() -> PermitService:
    from ..main import permit_service
    if not permit_service:
        raise HTTPException(status_code=503, detail="Permit service not available")
    return permit_service


@router.post("/search", response_model=SearchResponse)
async def search_permits(
    request: SearchRequest,
    permit_service: PermitService = Depends(get_permit_service)
):
    start_time = time.time()
    
    try:
        filter_dict = None
        if request.filters:
            filter_dict = {}
            filters_data = request.filters.dict(exclude_none=True)
            
            for key, value in filters_data.items():
                if isinstance(value, dict):
                    filter_dict[key] = value
                else:
                    filter_dict[key] = value
        
        results = permit_service.search_permits(
            query_text=request.query,
            top_k=request.top_k,
            index_name="austin-permits",
            filter_dict=filter_dict
        )
        
        search_results = []
        for result in results:
            metadata = result.metadata
            
            # Filter out null values from metadata
            filtered_metadata = {k: v for k, v in metadata.items() if v is not None}
            
            # Create SearchResult with only non-null metadata fields
            search_result_data = {
                'record_id': filtered_metadata.get('record_id', ''),
                'similarity_score': result.score,
            }
            
            # Add all non-null metadata fields dynamically
            for key, value in filtered_metadata.items():
                if key != 'record_id':  # Already added above
                    search_result_data[key] = value
            
            # Create SearchResult object with only the fields that have values
            search_result = SearchResult(**search_result_data)
            search_results.append(search_result)
        
        search_time = (time.time() - start_time) * 1000
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=round(search_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")