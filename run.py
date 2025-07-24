#!/usr/bin/env python3
"""
Startup script for ConstructIQ FastAPI application.
This script can be run from the project root directory.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 