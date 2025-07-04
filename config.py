"""
Configuration file for TMD data synchronization.
Contains API URLs, logging configuration, and constants.
"""

import logging

# API URLs
TMD_STATION_API_URL = "https://data.tmd.go.th/api/Station/v1/?uid=demo&ukey=demokey&format=json"
TMD_WEATHER_TODAY_API_URL = "https://data.tmd.go.th/api/WeatherToday/V2/?uid=api&ukey=api12345&format=json"

# API Configuration
API_TIMEOUT = 30  # seconds

# Database Configuration
DEFAULT_DB_CONFIG = {
    'host': 'localhost',
    'database': 'tmd_database',
    'user': 'your_username',
    'password': 'your_password',
    'port': 5432
}

# Logging Configuration
def setup_logging(level=logging.INFO):
    """Setup logging configuration."""
    logging.basicConfig(
        level=level, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

# Initialize logger
logger = setup_logging()
