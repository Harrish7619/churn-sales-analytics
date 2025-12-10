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

def main():
    print("Starting Customer Churn & Sales Forecasting Application...")
    print("Django Backend will run on: http://localhost:8000")
    print("Streamlit Frontend will run on: http://localhost:8501")
    print("Press Ctrl+C to stop both servers")
    
    # Start Django server in a separate thread
    django_thread = threading.Thread(target=run_django_server)
    django_thread.daemon = True
    django_thread.start()
    
    # Start Streamlit app in the main thread
    try:
        run_streamlit_app()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()





