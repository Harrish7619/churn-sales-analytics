import subprocess
import time
import os
import sys
import threading
import requests

def check_server_running(port, name):
    """Check if a server is running on the specified port"""
    try:
        response = requests.get(f"http://localhost:{port}", timeout=2)
        return True
    except:
        return False

def start_django():
    """Start Django server"""
    print("🚀 Starting Django server...")
    os.chdir('churn_forecast_backend')
    subprocess.run([sys.executable, 'manage.py', 'runserver', '8000'])

def start_streamlit():
    """Start Streamlit app"""
    print("⏳ Waiting for Django to start...")
    time.sleep(10)  # Wait for Django to start
    
    print("🚀 Starting Streamlit app...")
    subprocess.run([sys.executable, '-m', 'streamlit', 'run', '../streamlit_app.py', '--server.port', '8501'])

def main():
    print("🎯 Customer Churn & Sales Forecasting Dashboard")
    print("=" * 50)
    
    # Check if servers are already running
    if check_server_running(8000, "Django"):
        print("✅ Django server is already running on port 8000")
    else:
        print("🔄 Starting Django server...")
    
    if check_server_running(8501, "Streamlit"):
        print("✅ Streamlit app is already running on port 8501")
    else:
        print("🔄 Starting Streamlit app...")
    
    print("\n📱 Application URLs:")
    print("   Frontend: http://localhost:8501")
    print("   Backend:  http://localhost:8000")
    print("   Admin:    http://localhost:8000/admin")
    
    print("\n💡 Instructions:")
    print("1. Open http://localhost:8501 in your browser")
    print("2. Go to 'Model Training' and train both models")
    print("3. Explore the dashboards!")
    
    print("\n🛑 Press Ctrl+C to stop servers")
    print("=" * 50)
    
    # Start Django in background thread
    django_thread = threading.Thread(target=start_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Start Streamlit in main thread
    try:
        start_streamlit()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()




