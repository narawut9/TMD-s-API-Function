"""
Example usage of the TMD data synchronization function.
"""

from sync_tmd_data import sync_tmd_data_to_db
import logging

# Configure logging to see detailed output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Database configuration - Update these values with your actual database credentials
    db_config = {
        'host': 'localhost',
        'database': 'tmd_database',
        'user': 'your_username',
        'password': 'your_password',
        'port': 5432
    }
    
    print("TMD Data Synchronization Example")
    print("=" * 40)
    print("This script will:")
    print("1. Connect to your PostgreSQL database")
    print("2. Create necessary tables if they don't exist")
    print("3. Fetch station data from TMD API and sync to database")
    print("4. Fetch weather data from TMD API and insert to database")
    print("=" * 40)
    
    try:
        # Run the synchronization
        result = sync_tmd_data_to_db(db_config)
        
        # Display results
        print("\nSynchronization Results:")
        print("-" * 25)
        print(f"✓ Stations synced: {result['stations_synced']}")
        print(f"✓ Weather records inserted: {result['weather_records_inserted']}")
        
        if result['errors']:
            print(f"\n⚠ Errors encountered: {len(result['errors'])}")
            for i, error in enumerate(result['errors'], 1):
                print(f"  {i}. {error}")
        else:
            print("\n🎉 All operations completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Failed to run synchronization: {e}")
        print("Please check your database configuration and network connection.")

if __name__ == "__main__":
    main()
