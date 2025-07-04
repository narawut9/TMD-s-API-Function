# TMD API to Database Sync Function

This Python application synchronizes data from the Thai Meteorological Department (TMD) API to a PostgreSQL database. The application is built with a modular architecture for better maintainability and reusability.

## Features

- **Modular Architecture**: Separated into focused modules for better organization
- Fetches station data from TMD API and stores in `tmd_stations` table
- Fetches weather data from TMD API and stores in `tmd_weather_today` table
- Handles database table creation automatically
- Implements upsert logic for stations (insert or update based on StationId)
- Always inserts new weather records with timestamps
- Comprehensive error handling and logging
- PostgreSQL database support

## Project Structure

```
├── main.py                 # Main synchronization coordinator
├── config.py              # Configuration and constants
├── utils.py               # Utility functions for data processing
├── database_manager.py    # Database connection and table management
├── station_sync.py        # Station data synchronization
├── weather_sync.py        # Weather data synchronization
├── example_usage.py       # Usage example
├── requirements.txt       # Python dependencies
├── config_example.py      # Configuration template
├── README.md             # This file
└── __init__.py           # Package initialization
```

## Requirements

- Python 3.7+
- PostgreSQL database
- Required Python packages (see requirements.txt)

## Installation

1. Clone or download this project
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your PostgreSQL database and create a database for TMD data

## Configuration

1. Copy `config_example.py` to `config.py`
2. Update the database configuration with your PostgreSQL credentials:
   ```python
   DB_CONFIG = {
       'host': 'your_host',
       'database': 'your_database',
       'user': 'your_username',
       'password': 'your_password',
       'port': 5432
   }
   ```

## Usage

### Basic Usage

```python
from main import sync_tmd_data_to_db

# Database configuration
db_config = {
    'host': 'localhost',
    'database': 'tmd_database',
    'user': 'your_username',
    'password': 'your_password',
    'port': 5432
}

# Run synchronization
result = sync_tmd_data_to_db(db_config)

# Check results
print(f"Stations synced: {result['stations_synced']}")
print(f"Weather records inserted: {result['weather_records_inserted']}")
if result['errors']:
    print("Errors:", result['errors'])
```

### Running the Example

```bash
python example_usage.py
```

## Database Schema

### tmd_stations Table
- `station_id` (VARCHAR, PRIMARY KEY): Unique station identifier
- `station_name_thai` (VARCHAR): Thai name of the station
- `station_name_eng` (VARCHAR): English name of the station
- `latitude` (DECIMAL): Station latitude
- `longitude` (DECIMAL): Station longitude
- `province` (VARCHAR): Province where station is located
- `region` (VARCHAR): Region where station is located
- `created_at` (TIMESTAMP): Record creation timestamp
- `updated_at` (TIMESTAMP): Record last update timestamp

### tmd_weather_today Table
- `id` (SERIAL, PRIMARY KEY): Auto-incrementing ID
- `station_id` (VARCHAR, FOREIGN KEY): Reference to station
- `observed_timestamp` (TIMESTAMP): When the weather was observed
- `temperature` (DECIMAL): Temperature reading
- `humidity` (DECIMAL): Humidity percentage
- `pressure` (DECIMAL): Atmospheric pressure
- `wind_speed` (DECIMAL): Wind speed
- `wind_direction` (VARCHAR): Wind direction
- `rainfall` (DECIMAL): Rainfall amount
- `record_timestamp` (TIMESTAMP): When record was inserted to database

## API Endpoints

- **Stations**: `https://data.tmd.go.th/api/Station/v1/?uid=demo&ukey=demokey&format=json`
- **Weather Today**: `https://data.tmd.go.th/api/WeatherToday/V2/?uid=api&ukey=api12345&format=json`

## Error Handling

The function includes comprehensive error handling for:
- Network connection issues
- Invalid JSON responses
- Database connection problems
- Data parsing errors
- Individual record processing errors

All errors are logged and returned in the result dictionary for review.

## Logging

The application uses Python's logging module to provide detailed information about the synchronization process. Set the logging level to `INFO` or `DEBUG` for more detailed output.

## Scheduling

To run this synchronization regularly, you can:

1. **Use cron (Linux/Mac)**:
   ```bash
   # Run every hour
   0 * * * * /usr/bin/python3 /path/to/your/sync_script.py
   ```

2. **Use Windows Task Scheduler**:
   Create a scheduled task to run the Python script at desired intervals

3. **Use Python scheduling libraries**:
   ```python
   import schedule
   import time
   
   schedule.every().hour.do(lambda: sync_tmd_data_to_db(db_config))
   
   while True:
       schedule.run_pending()
       time.sleep(1)
   ```

## Troubleshooting

1. **Database Connection Issues**: Verify your PostgreSQL server is running and credentials are correct
2. **API Timeout**: The function uses a 30-second timeout for API calls
3. **Missing Dependencies**: Run `pip install -r requirements.txt`
4. **Permission Issues**: Ensure your database user has CREATE, INSERT, UPDATE permissions

## License

This project is provided as-is for educational and development purposes.
#   T M D - s - A P I - F u n c t i o n 
 
