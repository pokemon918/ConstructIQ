# Current API version
API_VERSION = "v1"

# API base path
API_BASE_PATH = f"/api/{API_VERSION}"

# Router prefixes
SEARCH_ROUTER_PREFIX = f"{API_BASE_PATH}"
LOGS_ROUTER_PREFIX = f"{API_BASE_PATH}/logs"
HEALTH_ROUTER_PREFIX = ""  # Health check doesn't need versioning

# Future v2 configuration (for reference)
# API_VERSION = "v2"
# API_BASE_PATH = f"/api/{API_VERSION}"
# SEARCH_ROUTER_PREFIX = f"{API_BASE_PATH}"
# LOGS_ROUTER_PREFIX = f"{API_BASE_PATH}/logs" 