"""
Station data synchronization functions for TMD API.
Handles fetching and processing station data from TMD API.
"""

import requests
import json
from config import logger, TMD_STATION_API_URL, API_TIMEOUT
from utils import extract_station_data, validate_api_response
from database_manager import execute_upsert_station


def fetch_station_data():
    """
    Fetch station data from TMD API.
    
    Returns:
        list: Station data from API
        
    Raises:
        requests.RequestException: If API request fails
        json.JSONDecodeError: If JSON parsing fails
        ValueError: If response format is invalid
    """
    logger.info("Fetching station data from TMD API...")
    
    try:
        response = requests.get(TMD_STATION_API_URL, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        station_data = response.json()
        validate_api_response(station_data, list)
        
        logger.info(f"Retrieved {len(station_data)} station records")
        return station_data
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch station data: {e}"
        logger.error(error_msg)
        raise
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse station JSON data: {e}"
        logger.error(error_msg)
        raise
    except ValueError as e:
        error_msg = f"Invalid station data format: {e}"
        logger.error(error_msg)
        raise


def process_station_record(cursor, station):
    """
    Process a single station record.
    
    Args:
        cursor: Database cursor object
        station (dict): Raw station data from API
        
    Returns:
        bool: True if processed successfully, False otherwise
    """
    try:
        # Extract and validate station data
        station_data = extract_station_data(station)
        
        # Execute database upsert
        execute_upsert_station(cursor, station_data)
        
        return True
        
    except Exception as e:
        error_msg = f"Error processing station {station.get('StationId', 'Unknown')}: {e}"
        logger.error(error_msg)
        return False


def sync_station_data(cursor):
    """
    Fetch and sync station data from TMD API to database.
    
    Args:
        cursor: Database cursor object
        
    Returns:
        dict: Synchronization result with counts and errors
    """
    result = {'synced_count': 0, 'errors': []}
    
    try:
        # Fetch station data from API
        station_data = fetch_station_data()
        
        # Process each station record
        for station in station_data:
            if process_station_record(cursor, station):
                result['synced_count'] += 1
            else:
                error_msg = f"Failed to process station {station.get('StationId', 'Unknown')}"
                result['errors'].append(error_msg)
        
        logger.info(f"Successfully synced {result['synced_count']} station records")
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch station data: {e}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse station JSON data: {e}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error in station sync: {e}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    
    return result
