import subprocess
import threading
import time
import os
import sys

def run_django_server():
    """Run Django development server"""
    os.chdir('churn_forecast_backend')
    subprocess.run([sys.executable, 'manage.py', 'runserver', '8000'])

def run_streamlit_app():
    """Run Streamlit application"""
    time.sleep(5)  # Wait for Django to start
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', '../streamlit_app.py', '--server.port', '8501'])

def setup_database():
    """Setup database and load data"""
    print("Setting up database...")
    os.chdir('churn_forecast_backend')
    
    # Make migrations
    subprocess.run([sys.executable, 'manage.py', 'makemigrations'])
    
    # Apply migrations
    subprocess.run([sys.executable, 'manage.py', 'migrate'])
    
    # Load data
    subprocess.run([sys.executable, 'load_data.py'])
    
    os.chdir('..')
    print("Database setup completed!")

def main():
    print("Starting Customer Churn & Sales Forecasting Application...")
    print("=" * 60)
    
    # Setup database first
    setup_database()
    
    print("\nApplication URLs:")
    print("   Frontend (Streamlit): http://localhost:8501")
    print("   Backend API (Django): http://localhost:8000")
    print("   Admin Panel: http://localhost:8000/admin")
    print("\nPress Ctrl+C to stop both servers")
    print("=" * 60)
    
    # Start Django server in a separate thread
    django_thread = threading.Thread(target=run_django_server)
    django_thread.daemon = True
    django_thread.start()
    
    # Start Streamlit app in the main thread
    try:
        run_streamlit_app()
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        print("Thank you for using the Customer Analytics Dashboard!")
        sys.exit(0)

if __name__ == "__main__":
    main()




