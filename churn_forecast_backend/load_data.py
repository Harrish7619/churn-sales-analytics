import os
import sys
import django
import pandas as pd
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'churn_forecast_backend.settings')
django.setup()

from analytics.models import Customer, Product, Order

def load_data_from_csv():
    """Load data from the CSV file into the database"""
    try:
        # Read the CSV file
        df = pd.read_csv('../customer_data.csv')
        
        print(f"Loading {len(df)} records...")
        
        # Clear existing data
        Order.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()
        
        # Create customers and products
        customers_dict = {}
        products_dict = {}
        
        for _, row in df.iterrows():
            # Create or get customer
            customer_id = row['customer_id']
            if customer_id not in customers_dict:
                customer = Customer.objects.create(
                    customer_id=customer_id,
                    age=row['age'],
                    gender=row['gender'],
                    country=row['country'],
                    signup_date=pd.to_datetime(row['signup_date']).date(),
                    last_purchase_date=pd.to_datetime(row['last_purchase_date']).date(),
                    cancellations_count=row['cancellations_count'],
                    subscription_status=row['subscription_status'],
                    purchase_frequency=row['purchase_frequency'],
                    ratings=row['Ratings']
                )
                customers_dict[customer_id] = customer
            
            # Create or get product
            product_id = row['product_id']
            if product_id not in products_dict:
                product = Product.objects.create(
                    product_id=product_id,
                    product_name=row['product_name'],
                    category=row['category'],
                    unit_price=row['unit_price']
                )
                products_dict[product_id] = product
            
            # Create order
            Order.objects.create(
                order_id=row['order_id'],
                customer=customers_dict[customer_id],
                product=products_dict[product_id],
                quantity=row['quantity'],
                order_date=pd.to_datetime(row['last_purchase_date']).date()
            )
        
        print(f"Successfully loaded:")
        print(f"- {Customer.objects.count()} customers")
        print(f"- {Product.objects.count()} products")
        print(f"- {Order.objects.count()} orders")
        
    except Exception as e:
        print(f"Error loading data: {e}")

if __name__ == "__main__":
    load_data_from_csv()

