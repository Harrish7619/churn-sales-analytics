Write-Host "🚀 Starting Customer Churn & Sales Forecasting Dashboard..." -ForegroundColor Green
Write-Host ""

# Start Django server
Write-Host "Starting Django server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd churn_forecast_backend; python manage.py runserver 8000"

# Wait for Django to start
Write-Host "Waiting for Django to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Start Streamlit app
Write-Host "Starting Streamlit app..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run streamlit_app.py --server.port 8501"

Write-Host ""
Write-Host "📱 Application URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:8501" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   Admin:    http://localhost:8000/admin" -ForegroundColor White

Write-Host ""
Write-Host "💡 Instructions:" -ForegroundColor Cyan
Write-Host "1. Open http://localhost:8501 in your browser" -ForegroundColor White
Write-Host "2. Go to 'Model Training' and train both models" -ForegroundColor White
Write-Host "3. Explore the dashboards!" -ForegroundColor White

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")





