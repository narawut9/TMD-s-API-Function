import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def sync_tmd_data_to_db(db_config):
    """
    Sync TMD API data to PostgreSQL database.
    
    Args:
        db_config (dict): Database configuration containing host, database, user, password, port
    
    Returns:
        dict: Status of the synchronization process
    """
    
    # API URLs
    url_station = "https://data.tmd.go.th/api/Station/v1/?uid=demo&ukey=demokey&format=json"
    url_weathertoday = "https://data.tmd.go.th/api/WeatherToday/V2/?uid=api&ukey=api12345&format=json"
    
    conn = None
    result = {
        'stations_synced': 0,
        'weather_records_inserted': 0,
        'errors': []
    }
    
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("Connected to PostgreSQL database successfully")
        
        # Create tables if they don't exist
        create_tables(cursor)
        conn.commit()
        
        # Sync station data
        stations_result = sync_station_data(cursor, url_station)
        result['stations_synced'] = stations_result['synced_count']
        if stations_result['errors']:
            result['errors'].extend(stations_result['errors'])
        
        # Sync weather today data
        weather_result = sync_weather_today_data(cursor, url_weathertoday)
        result['weather_records_inserted'] = weather_result['inserted_count']
        if weather_result['errors']:
            result['errors'].extend(weather_result['errors'])
        
        # Commit all changes
        conn.commit()
        logger.info("Data synchronization completed successfully")
        
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        result['errors'].append(f"Database error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        result['errors'].append(f"Unexpected error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            logger.info("Database connection closed")
    
    return result

def create_tables(cursor):
    """Create database tables if they don't exist."""
    
    # Create tmd_stations table
    create_stations_table = """
    CREATE TABLE IF NOT EXISTS tmd_stations (
        station_id VARCHAR(50) PRIMARY KEY,
        station_name_thai VARCHAR(255),
        station_name_eng VARCHAR(255),
        latitude DECIMAL(10, 6),
        longitude DECIMAL(10, 6),
        province VARCHAR(100),
        region VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    # Create tmd_weather_today table
    create_weather_table = """
    CREATE TABLE IF NOT EXISTS tmd_weather_today (
        id SERIAL PRIMARY KEY,
        station_id VARCHAR(50),
        observed_timestamp TIMESTAMP,
        temperature DECIMAL(5, 2),
        humidity DECIMAL(5, 2),
        pressure DECIMAL(7, 2),
        wind_speed DECIMAL(5, 2),
        wind_direction VARCHAR(10),
        rainfall DECIMAL(6, 2),
        record_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (station_id) REFERENCES tmd_stations(station_id)
    );
    """
    
    cursor.execute(create_stations_table)
    cursor.execute(create_weather_table)
    logger.info("Database tables created/verified successfully")

def sync_station_data(cursor, url_station):
    """Fetch and sync station data from TMD API."""
    
    result = {'synced_count': 0, 'errors': []}
    
    try:
        logger.info("Fetching station data from TMD API...")
        response = requests.get(url_station, timeout=30)
        response.raise_for_status()
        
        station_data = response.json()
        
        if not isinstance(station_data, list):
            raise ValueError("Expected station data to be a list")
        
        logger.info(f"Retrieved {len(station_data)} station records")
        
        for station in station_data:
            try:
                # Extract station information
                station_id = station.get('StationId', '')
                station_name_thai = station.get('StationNameThai', '')
                station_name_eng = station.get('StationNameEng', '')
                latitude = station.get('Latitude')
                longitude = station.get('Longitude')
                province = station.get('Province', '')
                region = station.get('Region', '')
                
                # Convert latitude and longitude to float if they exist
                if latitude is not None:
                    latitude = float(latitude)
                if longitude is not None:
                    longitude = float(longitude)
                
                # Insert or update station data
                upsert_query = """
                INSERT INTO tmd_stations 
                (station_id, station_name_thai, station_name_eng, latitude, longitude, province, region, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (station_id) 
                DO UPDATE SET 
                    station_name_thai = EXCLUDED.station_name_thai,
                    station_name_eng = EXCLUDED.station_name_eng,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    province = EXCLUDED.province,
                    region = EXCLUDED.region,
                    updated_at = CURRENT_TIMESTAMP;
                """
                
                cursor.execute(upsert_query, (
                    station_id, station_name_thai, station_name_eng, 
                    latitude, longitude, province, region
                ))
                
                result['synced_count'] += 1
                
            except Exception as e:
                error_msg = f"Error processing station {station.get('StationId', 'Unknown')}: {e}"
                logger.error(error_msg)
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

def sync_weather_today_data(cursor, url_weathertoday):
    """Fetch and sync weather today data from TMD API."""
    
    result = {'inserted_count': 0, 'errors': []}
    
    try:
        logger.info("Fetching weather today data from TMD API...")
        response = requests.get(url_weathertoday, timeout=30)
        response.raise_for_status()
        
        weather_data = response.json()
        
        if not isinstance(weather_data, list):
            raise ValueError("Expected weather data to be a list")
        
        logger.info(f"Retrieved {len(weather_data)} weather records")
        
        for weather in weather_data:
            try:
                # Extract weather information
                station_id = weather.get('StationId', '')
                observed_timestamp = weather.get('ObservedTimestamp')
                temperature = weather.get('Temperature')
                humidity = weather.get('Humidity')
                pressure = weather.get('Pressure')
                wind_speed = weather.get('WindSpeed')
                wind_direction = weather.get('WindDirection', '')
                rainfall = weather.get('Rainfall')
                
                # Convert numeric values
                if temperature is not None:
                    temperature = float(temperature)
                if humidity is not None:
                    humidity = float(humidity)
                if pressure is not None:
                    pressure = float(pressure)
                if wind_speed is not None:
                    wind_speed = float(wind_speed)
                if rainfall is not None:
                    rainfall = float(rainfall)
                
                # Parse observed timestamp
                if observed_timestamp:
                    try:
                        # Assuming the timestamp is in ISO format or similar
                        observed_timestamp = datetime.fromisoformat(observed_timestamp.replace('Z', '+00:00'))
                    except ValueError:
                        # If parsing fails, use current timestamp
                        observed_timestamp = datetime.now()
                else:
                    observed_timestamp = datetime.now()
                
                # Insert weather data (always insert, never update)
                insert_query = """
                INSERT INTO tmd_weather_today 
                (station_id, observed_timestamp, temperature, humidity, pressure, 
                 wind_speed, wind_direction, rainfall, record_timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
                """
                
                cursor.execute(insert_query, (
                    station_id, observed_timestamp, temperature, humidity, 
                    pressure, wind_speed, wind_direction, rainfall
                ))
                
                result['inserted_count'] += 1
                
            except Exception as e:
                error_msg = f"Error processing weather data for station {weather.get('StationId', 'Unknown')}: {e}"
                logger.error(error_msg)
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

# Example usage
if __name__ == "__main__":
    # Database configuration
    db_config = {
        'host': 'localhost',
        'database': 'tmd_database',
        'user': 'your_username',
        'password': 'your_password',
        'port': 5432
    }
    
    print("Starting TMD data synchronization...")
    print("=" * 50)
    
    # Call the sync function
    result = sync_tmd_data_to_db(db_config)
    
    # Print results
    print(f"Stations synced: {result['stations_synced']}")
    print(f"Weather records inserted: {result['weather_records_inserted']}")
    
    if result['errors']:
        print(f"\nErrors encountered ({len(result['errors'])}):")
        for error in result['errors']:
            print(f"  - {error}")
    else:
        print("\nSynchronization completed successfully with no errors!")
    
    print("=" * 50)
    print("TMD data synchronization finished.")
