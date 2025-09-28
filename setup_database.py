import os
import sys
import django
import subprocess

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'churn_forecast_backend.settings')
django.setup()

from django.core.management import execute_from_command_line

def setup_database():
    """Setup the database and load initial data"""
    print("Setting up the database...")
    
    try:
        # Make migrations
        print("Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        
        # Apply migrations
        print("Applying migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Load data
        print("Loading initial data...")
        from churn_forecast_backend.load_data import load_data_from_csv
        load_data_from_csv()
        
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {e}")

if __name__ == "__main__":
    setup_database()




