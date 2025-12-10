"""
Customer Churn Prediction & Sales Forecasting Dashboard - Demo Guide

This script demonstrates the key features of the application.
Run this after starting both Django and Streamlit servers.
"""

import requests
import json
import time

def demo_api_features():
    """Demonstrate API features"""
    base_url = "http://localhost:8000/api"
    
    print("🚀 Customer Churn & Sales Forecasting Dashboard - Demo")
    print("=" * 60)
    
    # Test basic endpoints
    print("\n📊 Testing Basic API Endpoints...")
    
    try:
        # Test customers
        response = requests.get(f"{base_url}/customers/")
        if response.status_code == 200:
            customers = response.json()
            print(f"✅ Found {len(customers)} customers in database")
        
        # Test products
        response = requests.get(f"{base_url}/products/")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Found {len(products)} products in database")
        
        # Test orders
        response = requests.get(f"{base_url}/orders/")
        if response.status_code == 200:
            orders = response.json()
            print(f"✅ Found {len(orders)} orders in database")
        
        print("\n🤖 Training Machine Learning Models...")
        
        # Train churn model
        print("Training churn prediction model...")
        response = requests.post(f"{base_url}/ml-training/train_churn_model/")
        if response.status_code == 200:
            result = response.json()
            print("✅ Churn model trained successfully!")
            performance = result.get('performance', {})
            print(f"   - Accuracy: {performance.get('accuracy', 0):.3f}")
            print(f"   - Precision: {performance.get('precision', 0):.3f}")
            print(f"   - Recall: {performance.get('recall', 0):.3f}")
            print(f"   - F1 Score: {performance.get('f1_score', 0):.3f}")
        
        # Train sales model
        print("Training sales forecasting model...")
        response = requests.post(f"{base_url}/ml-training/train_sales_model/")
        if response.status_code == 200:
            result = response.json()
            print("✅ Sales model trained successfully!")
            performance = result.get('performance', {})
            print(f"   - R² Score: {performance.get('r2_score', 0):.3f}")
            print(f"   - MSE: {performance.get('mse', 0):.3f}")
        
        print("\n📈 Getting Analytics...")
        
        # Get churn analytics
        response = requests.get(f"{base_url}/customers/churn_analytics/")
        if response.status_code == 200:
            analytics = response.json()
            print("✅ Churn Analytics:")
            print(f"   - Overall Churn Rate: {analytics.get('overall_churn_rate', 0):.1f}%")
            print(f"   - Total Customers: {analytics.get('total_customers', 0)}")
            print(f"   - High Risk Customers: {analytics.get('high_risk_customers', 0)}")
        
        # Get top churn risk customers
        response = requests.get(f"{base_url}/customers/top_churn_risk/")
        if response.status_code == 200:
            top_risk = response.json()
            print(f"✅ Top {len(top_risk)} High-Risk Customers identified")
            if top_risk:
                print("   Sample high-risk customer:")
                customer = top_risk[0]
                print(f"   - Customer ID: {customer.get('customer_id', 'N/A')}")
                print(f"   - Churn Probability: {customer.get('churn_probability', 0)*100:.1f}%")
                print(f"   - Risk Level: {customer.get('risk_level', 'N/A')}")
        
        # Get sales analytics
        response = requests.get(f"{base_url}/products/sales_analytics/")
        if response.status_code == 200:
            sales_analytics = response.json()
            print("✅ Sales Analytics retrieved")
        
        # Get top selling products
        response = requests.get(f"{base_url}/products/top_selling/")
        if response.status_code == 200:
            top_products = response.json()
            print(f"✅ Top {len(top_products)} Products with highest predicted sales identified")
            if top_products:
                print("   Sample top product:")
                product = top_products[0]
                print(f"   - Product: {product.get('product_name', 'N/A')}")
                print(f"   - Predicted Quantity: {product.get('predicted_quantity', 0)}")
                print(f"   - Confidence: {product.get('confidence_level', 0)*100:.1f}%")
        
        print("\n🎉 Demo completed successfully!")
        print("\n📱 Next Steps:")
        print("1. Open your browser and go to: http://localhost:8501")
        print("2. Explore the interactive dashboards")
        print("3. Try the filtering and export features")
        print("4. Add new data using the Data Input interface")
        print("5. Retrain models with new data")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Django server.")
        print("   Make sure Django is running on port 8000")
        print("   Run: cd churn_forecast_backend && python manage.py runserver 8000")
    except Exception as e:
        print(f"❌ Error during demo: {e}")

def show_application_features():
    """Show application features"""
    print("\n🎯 Application Features:")
    print("=" * 40)
    
    features = [
        "📊 Interactive Dashboards with real-time data",
        "⚠️ Customer Churn Prediction with ML models",
        "📈 Sales Forecasting with demand prediction",
        "🔍 Advanced filtering and search capabilities",
        "📋 Paginated customer lists with sorting",
        "📥 Export functionality (CSV/PDF)",
        "📝 Data input interface for new records",
        "🤖 Model training and retraining interface",
        "📊 Performance monitoring and analytics",
        "🎨 Beautiful and responsive UI design"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n🔧 Technical Features:")
    print("=" * 40)
    
    tech_features = [
        "Django REST API backend",
        "Streamlit interactive frontend",
        "SQLite database (easily upgradeable to PostgreSQL)",
        "Random Forest ML models",
        "Real-time data processing",
        "CORS-enabled API",
        "Modular and extensible architecture",
        "Comprehensive error handling",
        "Performance metrics tracking",
        "Model versioning system"
    ]
    
    for feature in tech_features:
        print(f"  {feature}")

if __name__ == "__main__":
    show_application_features()
    demo_api_features()





