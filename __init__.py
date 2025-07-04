"""
TMD Data Synchronization Package

This package provides functionality to synchronize data from the Thai Meteorological Department (TMD) API
to a PostgreSQL database.

Main modules:
- main: Main synchronization function
- config: Configuration and constants
- utils: Utility functions for data processing
- database_manager: Database connection and table management
- station_sync: Station data synchronization
- weather_sync: Weather data synchronization

Usage:
    from main import sync_tmd_data_to_db
    
    db_config = {
        'host': 'localhost',
        'database': 'tmd_database',
        'user': 'username',
        'password': 'password',
        'port': 5432
    }
    
    result = sync_tmd_data_to_db(db_config)
"""

__version__ = "1.0.0"
__author__ = "TMD Data Sync Team"
__email__ = "support@example.com"

# Import main function for easy access
from main import sync_tmd_data_to_db

__all__ = ['sync_tmd_data_to_db']
