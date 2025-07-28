import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class QueryLoggingService:
    def __init__(self, log_file_path: str = "logs/search_queries.jsonl"):
        self.log_file_path = log_file_path
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure the log directory exists."""
        log_dir = Path(self.log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_query(self, 
                  query_text: str,
                  filters: Optional[Dict[str, Any]] = None,
                  top_results: List[Dict[str, Any]] = None,
                  search_time_ms: Optional[float] = None,
                  user_agent: Optional[str] = None,
                  client_ip: Optional[str] = None) -> Dict[str, Any]:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query_text": query_text,
            "filters": filters or {},
            "top_results": self._prepare_results_for_logging(top_results or []),
            "search_time_ms": search_time_ms,
            "user_agent": user_agent,
            "client_ip": client_ip,
            "total_results": len(top_results) if top_results else 0
        }
        
        try:
            # Append to JSONL file
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            logger.info(f"Logged query: '{query_text[:50]}...' with {len(top_results) if top_results else 0} results")
            return log_entry
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            return log_entry
    
    def _prepare_results_for_logging(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logged_results = []
        
        for result in results:
            logged_result = {
                "record_id": result.get("id", ""),
                "similarity_score": result.get("score", 0.0),
                "permit_number": result.get("metadata", {}).get("permit_number", ""),
                "address": result.get("metadata", {}).get("address", ""),
                "permit_type": result.get("metadata", {}).get("permit_type", ""),
                "status": result.get("metadata", {}).get("status", ""),
                "total_job_valuation": result.get("metadata", {}).get("total_job_valuation"),
                "calendar_year_issued": result.get("metadata", {}).get("calendar_year_issued")
            }
            logged_results.append(logged_result)
        
        return logged_results
    
    def get_recent_logs(self, limit: int = 25) -> List[Dict[str, Any]]:
        if not os.path.exists(self.log_file_path):
            return []
        
        try:
            logs = []
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            log_entry = json.loads(line.strip())
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in log file: {line.strip()}")
                            continue
            
            # Return the most recent logs (last entries in file)
            return logs[-limit:] if logs else []
            
        except Exception as e:
            logger.error(f"Failed to read logs: {e}")
            return []