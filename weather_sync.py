"""
Weather data synchronization functions for TMD API.
Handles fetching and processing weather data from TMD API.
"""

import requests
import json
from config import logger, TMD_WEATHER_TODAY_API_URL, API_TIMEOUT
from utils import extract_weather_data, validate_api_response
from database_manager import execute_insert_weather


def fetch_weather_data():
    """
    Fetch weather data from TMD API.
    
    Returns:
        list: Weather data from API
        
    Raises:
        requests.RequestException: If API request fails
        json.JSONDecodeError: If JSON parsing fails
        ValueError: If response format is invalid
    """
    logger.info("Fetching weather today data from TMD API...")
    
    try:
        response = requests.get(TMD_WEATHER_TODAY_API_URL, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        weather_data = response.json()
        validate_api_response(weather_data, list)
        
        logger.info(f"Retrieved {len(weather_data)} weather records")
        return weather_data
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch weather data: {e}"
        logger.error(error_msg)
        raise
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse weather JSON data: {e}"
        logger.error(error_msg)
        raise
    except ValueError as e:
        error_msg = f"Invalid weather data format: {e}"
        logger.error(error_msg)
        raise


def process_weather_record(cursor, weather):
    """
    Process a single weather record.
    
    Args:
        cursor: Database cursor object
        weather (dict): Raw weather data from API
        
    Returns:
        bool: True if processed successfully, False otherwise
    """
    try:
        # Extract and validate weather data
        weather_data = extract_weather_data(weather)
        
        # Execute database insert
        execute_insert_weather(cursor, weather_data)
        
        return True
        
    except Exception as e:
        error_msg = f"Error processing weather data for station {weather.get('StationId', 'Unknown')}: {e}"
        logger.error(error_msg)
        return False


def sync_weather_today_data(cursor):
    """
    Fetch and sync weather today data from TMD API to database.
    
    Args:
        cursor: Database cursor object
        
    Returns:
        dict: Synchronization result with counts and errors
    """
    result = {'inserted_count': 0, 'errors': []}
    
    try:
        # Fetch weather data from API
        weather_data = fetch_weather_data()
        
        # Process each weather record
        for weather in weather_data:
            if process_weather_record(cursor, weather):
                result['inserted_count'] += 1
            else:
                error_msg = f"Failed to process weather data for station {weather.get('StationId', 'Unknown')}"
                result['errors'].append(error_msg)
        
        logger.info(f"Successfully inserted {result['inserted_count']} weather records")
        
    except requests.RequestException as e:
        error_msg = f"Failed to fetch weather data: {e}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse weather JSON data: {e}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error in weather sync: {e}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    
    return result
