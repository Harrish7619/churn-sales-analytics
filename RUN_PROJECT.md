# 🚀 How to Run the Project - Complete Guide

## Prerequisites
- Python 3.8+ installed
- Virtual environment created (`.venv` folder exists)

## Quick Start (Easiest Method)

### Step 1: Open PowerShell in Project Directory
```powershell
cd "F:\BNP - Copy"
```

### Step 2: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Run the Application
```powershell
python run_app.py
```

This will:
- ✅ Set up the database automatically
- ✅ Load sample data (2000 records)
- ✅ Start Django backend on port 8000
- ✅ Start Streamlit frontend on port 8501

### Step 4: Open in Browser
- **Frontend Dashboard**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

### Step 5: Train the Models (Important!)
1. In the Streamlit dashboard, go to **"🤖 Model Training"** in the sidebar
2. Click **"🚀 Train Churn Model"** - wait for it to complete
3. Click **"🚀 Train Sales Model"** - wait for it to complete
4. Now you can use all features!

---

## Method 2: Manual Setup (If you prefer step-by-step)

### Step 1: Navigate to Project Directory
```powershell
cd "F:\BNP - Copy"
```

### Step 2: Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies (if not already installed)
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Setup Database
```powershell
cd churn_forecast_backend
python manage.py makemigrations
python manage.py migrate
python load_data.py
cd ..
```

### Step 5: Start Django Server (Terminal 1)
```powershell
cd churn_forecast_backend
python manage.py runserver 8000
```

### Step 6: Start Streamlit App (Terminal 2 - New PowerShell Window)
```powershell
cd "F:\BNP - Copy"
.\.venv\Scripts\Activate.ps1
streamlit run streamlit_app.py --server.port 8501
```

---

## Method 3: Using PowerShell Script

### Step 1: Navigate to Project Directory
```powershell
cd "F:\BNP - Copy"
```

### Step 2: Run PowerShell Script
```powershell
.\start_app.ps1
```

This opens Django and Streamlit in separate windows.

---

## Troubleshooting

### If virtual environment is not activated:
```powershell
# Check if venv exists
Test-Path .\.venv\Scripts\Activate.ps1

# If it doesn't exist, create it:
python -m venv .venv

# Then activate:
.\.venv\Scripts\Activate.ps1
```

### If packages are not installed:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### If port 8000 or 8501 is already in use:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Find process using port 8501
netstat -ano | findstr :8501

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### If database errors occur:
```powershell
cd churn_forecast_backend
# Delete old database
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue
# Recreate database
python manage.py migrate
python load_data.py
cd ..
```

---

## Complete Command Sequence (Copy & Paste)

```powershell
# Navigate to project
cd "F:\BNP - Copy"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the application (does everything automatically)
python run_app.py
```

---

## After Starting the Application

1. **Wait for data loading** - You'll see "Loading 2000 records..." - wait for it to complete (2-5 minutes)
2. **Open browser** - Go to http://localhost:8501
3. **Train models** - Go to "Model Training" page and train both models
4. **Explore dashboards** - Use Churn Prediction and Sales Forecasting dashboards

---

## Stopping the Application

Press `Ctrl+C` in the terminal where `run_app.py` is running. This will stop both servers.

---

## Notes

- The first run will take longer as it loads 2000 records
- Make sure to train the models before using prediction features
- All data is stored in `churn_forecast_backend/db.sqlite3`
- ML models are saved in `churn_forecast_backend/ml_models/`

