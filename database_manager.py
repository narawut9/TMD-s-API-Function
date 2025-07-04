"""
Database management functions for TMD data synchronization.
Handles database connections and table creation.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from config import logger


def get_database_connection(db_config):
    """
    Create and return a PostgreSQL database connection.
    
    Args:
        db_config (dict): Database configuration
        
    Returns:
        psycopg2.connection: Database connection object
        
    Raises:
        psycopg2.Error: If connection fails
    """
    try:
        conn = psycopg2.connect(**db_config)
        logger.info("Connected to PostgreSQL database successfully")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


def create_tables(cursor):
    """
    Create database tables if they don't exist.
    
    Args:
        cursor: Database cursor object
    """
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
    
    try:
        cursor.execute(create_stations_table)
        cursor.execute(create_weather_table)
        logger.info("Database tables created/verified successfully")
    except psycopg2.Error as e:
        logger.error(f"Failed to create tables: {e}")
        raise


def execute_upsert_station(cursor, station_data):
    """
    Execute upsert operation for station data.
    
    Args:
        cursor: Database cursor object
        station_data (dict): Station data to upsert
    """
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
        station_data['station_id'],
        station_data['station_name_thai'],
        station_data['station_name_eng'],
        station_data['latitude'],
        station_data['longitude'],
        station_data['province'],
        station_data['region']
    ))


def execute_insert_weather(cursor, weather_data):
    """
    Execute insert operation for weather data.
    
    Args:
        cursor: Database cursor object
        weather_data (dict): Weather data to insert
    """
    insert_query = """
    INSERT INTO tmd_weather_today 
    (station_id, observed_timestamp, temperature, humidity, pressure, 
     wind_speed, wind_direction, rainfall, record_timestamp)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
    """
    
    cursor.execute(insert_query, (
        weather_data['station_id'],
        weather_data['observed_timestamp'],
        weather_data['temperature'],
        weather_data['humidity'],
        weather_data['pressure'],
        weather_data['wind_speed'],
        weather_data['wind_direction'],
        weather_data['rainfall']
    ))


def close_database_connection(conn):
    """
    Close database connection safely.
    
    Args:
        conn: Database connection object
    """
    if conn:
        conn.close()
        logger.info("Database connection closed")
