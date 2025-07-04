"""
Main TMD data synchronization module.
Coordinates the synchronization of TMD API data to PostgreSQL database.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from config import logger
from database_manager import get_database_connection, create_tables, close_database_connection
from station_sync import sync_station_data
from weather_sync import sync_weather_today_data


def sync_tmd_data_to_db(db_config):
    """
    Sync TMD API data to PostgreSQL database.
    
    This is the main function that coordinates the entire synchronization process:
    1. Connects to the database
    2. Creates tables if they don't exist
    3. Syncs station data from TMD API
    4. Syncs weather data from TMD API
    5. Handles errors and cleanup
    
    Args:
        db_config (dict): Database configuration containing host, database, user, password, port
    
    Returns:
        dict: Status of the synchronization process containing:
            - stations_synced (int): Number of stations synchronized
            - weather_records_inserted (int): Number of weather records inserted
            - errors (list): List of error messages if any occurred
    """
    
    conn = None
    result = {
        'stations_synced': 0,
        'weather_records_inserted': 0,
        'errors': []
    }
    
    try:
        # Connect to PostgreSQL database
        conn = get_database_connection(db_config)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create tables if they don't exist
        create_tables(cursor)
        conn.commit()
        
        # Sync station data
        logger.info("Starting station data synchronization...")
        stations_result = sync_station_data(cursor)
        result['stations_synced'] = stations_result['synced_count']
        if stations_result['errors']:
            result['errors'].extend(stations_result['errors'])
        
        # Sync weather today data
        logger.info("Starting weather data synchronization...")
        weather_result = sync_weather_today_data(cursor)
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
        close_database_connection(conn)
    
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
