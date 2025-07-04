"""
Utility functions for TMD data synchronization.
Contains helper functions for data conversion and processing.
"""

from datetime import datetime
from config import logger


def convert_to_float(value):
    """
    Convert a value to float if possible, otherwise return None.
    
    Args:
        value: Value to convert
        
    Returns:
        float or None: Converted value or None if conversion fails
    """
    if value is not None:
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert value to float: {value}")
            return None
    return None


def parse_timestamp(timestamp_str):
    """
    Parse timestamp string to datetime object.
    
    Args:
        timestamp_str (str): Timestamp string to parse
        
    Returns:
        datetime: Parsed datetime object or current time if parsing fails
    """
    if timestamp_str:
        try:
            # Handle ISO format with Z suffix
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str.replace('Z', '+00:00')
            return datetime.fromisoformat(timestamp_str)
        except ValueError:
            logger.warning(f"Failed to parse timestamp: {timestamp_str}, using current time")
            return datetime.now()
    else:
        return datetime.now()


def extract_station_data(station):
    """
    Extract and validate station data from API response.
    
    Args:
        station (dict): Station data from API
        
    Returns:
        dict: Processed station data
    """
    return {
        'station_id': station.get('StationId', ''),
        'station_name_thai': station.get('StationNameThai', ''),
        'station_name_eng': station.get('StationNameEng', ''),
        'latitude': convert_to_float(station.get('Latitude')),
        'longitude': convert_to_float(station.get('Longitude')),
        'province': station.get('Province', ''),
        'region': station.get('Region', '')
    }


def extract_weather_data(weather):
    """
    Extract and validate weather data from API response.
    
    Args:
        weather (dict): Weather data from API
        
    Returns:
        dict: Processed weather data
    """
    return {
        'station_id': weather.get('StationId', ''),
        'observed_timestamp': parse_timestamp(weather.get('ObservedTimestamp')),
        'temperature': convert_to_float(weather.get('Temperature')),
        'humidity': convert_to_float(weather.get('Humidity')),
        'pressure': convert_to_float(weather.get('Pressure')),
        'wind_speed': convert_to_float(weather.get('WindSpeed')),
        'wind_direction': weather.get('WindDirection', ''),
        'rainfall': convert_to_float(weather.get('Rainfall'))
    }


def validate_api_response(data, expected_type=list):
    """
    Validate API response data.
    
    Args:
        data: Response data to validate
        expected_type: Expected data type
        
    Returns:
        bool: True if valid, False otherwise
        
    Raises:
        ValueError: If data is not of expected type
    """
    if not isinstance(data, expected_type):
        raise ValueError(f"Expected {expected_type.__name__}, got {type(data).__name__}")
    return True
