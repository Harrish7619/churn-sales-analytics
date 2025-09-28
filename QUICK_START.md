# 🚀 Quick Start Guide

## Customer Churn Prediction & Sales Forecasting Dashboard

### Prerequisites
- Python 3.8+ installed
- All dependencies installed (`pip install -r requirements.txt`)

### 🏃‍♂️ Quick Start (3 Steps)

#### Step 1: Start the Application
```bash
python run_app.py
```

This will:
- Set up the database automatically
- Load the sample data
- Start Django backend on port 8000
- Start Streamlit frontend on port 8501

#### Step 2: Open the Dashboard
Open your browser and go to: **http://localhost:8501**

#### Step 3: Train the Models
1. Click on "🤖 Model Training" in the sidebar
2. Click "🚀 Train Churn Model" to train the churn prediction model
3. Click "🚀 Train Sales Model" to train the sales forecasting model

### 🎯 What You Can Do

#### Churn Prediction Dashboard
- View churn analytics and trends
- See top 10 high-risk customers
- Filter customers by risk level, country, age
- Export high-risk customer lists
- Paginated customer browsing

#### Sales Forecasting Dashboard
- View sales trends and analytics
- See top 10 products with highest predicted sales
- Generate custom forecasts for specific products
- Export sales forecasts
- Revenue analysis by category and country

#### Data Management
- Add new customers, products, and orders
- Real-time data validation
- Automatic model updates

#### Model Training
- Train/retrain ML models
- View performance metrics
- Monitor model accuracy over time

### 🔧 Manual Setup (Alternative)

If you prefer manual setup:

```bash
# 1. Setup database
cd churn_forecast_backend
python manage.py makemigrations
python manage.py migrate
python load_data.py

# 2. Start Django server
python manage.py runserver 8000

# 3. Start Streamlit (in new terminal)
streamlit run streamlit_app.py --server.port 8501
```

### 📊 Sample Data

The application comes with 2000 sample records including:
- Customer demographics and transaction history
- Product information and categories
- Order history and sales data

### 🎨 Dashboard Features

- **Interactive Visualizations**: Plotly charts with zoom, filter, and export
- **Real-time Updates**: Data refreshes automatically
- **Responsive Design**: Works on desktop and mobile
- **Export Capabilities**: Download data as CSV or PDF
- **Advanced Filtering**: Filter by multiple criteria
- **Pagination**: Handle large datasets efficiently

### 🚨 Troubleshooting

**Cannot connect to backend?**
- Make sure Django server is running on port 8000
- Check if port 8000 is available

**Streamlit not loading?**
- Make sure Streamlit is running on port 8501
- Check if port 8501 is available

**Database errors?**
- Delete `churn_forecast_backend/db.sqlite3` and run setup again
- Make sure you have write permissions

### 📱 URLs

- **Main Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/

### 🎉 You're Ready!

The application is now running with:
- ✅ Database set up and populated
- ✅ ML models ready for training
- ✅ Interactive dashboards available
- ✅ All features functional

Enjoy exploring your customer analytics! 🎊




