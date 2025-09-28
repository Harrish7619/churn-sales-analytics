@echo off
echo Starting Customer Churn & Sales Forecasting Dashboard...
echo.

echo Starting Django server...
start "Django Server" cmd /k "cd churn_forecast_backend && python manage.py runserver 8000"

echo Waiting for Django to start...
timeout /t 10 /nobreak > nul

echo Starting Streamlit app...
start "Streamlit App" cmd /k "streamlit run streamlit_app.py --server.port 8501"

echo.
echo Application is starting...
echo Frontend: http://localhost:8501
echo Backend:  http://localhost:8000
echo.
echo Press any key to exit...
pause > nul