"""
Example configuration file for TMD data synchronization.
Copy this file to config.py and update with your actual database credentials.
"""

# Database configuration for PostgreSQL
DB_CONFIG = {
    'host': 'localhost',          # Your PostgreSQL host
    'database': 'tmd_database',   # Your database name
    'user': 'your_username',      # Your PostgreSQL username
    'password': 'your_password',  # Your PostgreSQL password
    'port': 5432                  # PostgreSQL port (default is 5432)
}

# Example for different environments
DB_CONFIGS = {
    'development': {
        'host': 'localhost',
        'database': 'tmd_dev',
        'user': 'dev_user',
        'password': 'dev_password',
        'port': 5432
    },
    'production': {
        'host': 'your-prod-host.com',
        'database': 'tmd_prod',
        'user': 'prod_user',
        'password': 'prod_password',
        'port': 5432
    }
}
