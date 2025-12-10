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
        print("Reading CSV file...")
        df = pd.read_csv('../customer_data.csv')
        
        print(f"Processing {len(df)} records...")
        
        # Clear existing data
        print("Clearing existing data...")
        Order.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()
        
        # Prepare data for bulk creation
        print("Preparing data...")
        customers_dict = {}
        products_dict = {}
        customers_to_create = []
        products_to_create = []
        orders_to_create = []
        
        # Process each row
        for idx, row in df.iterrows():
            if (idx + 1) % 500 == 0:
                print(f"  Processed {idx + 1}/{len(df)} records...")
            
            # Prepare customer
            customer_id = row['customer_id']
            if customer_id not in customers_dict:
                customers_to_create.append(Customer(
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
                ))
                customers_dict[customer_id] = len(customers_to_create) - 1
            
            # Prepare product
            product_id = row['product_id']
            if product_id not in products_dict:
                products_to_create.append(Product(
                    product_id=product_id,
                    product_name=row['product_name'],
                    category=row['category'],
                    unit_price=row['unit_price']
                ))
                products_dict[product_id] = len(products_to_create) - 1
        
        # Bulk create customers
        print(f"Creating {len(customers_to_create)} customers...")
        Customer.objects.bulk_create(customers_to_create, ignore_conflicts=True)
        
        # Fetch created customers to get their IDs
        created_customers = {c.customer_id: c for c in Customer.objects.all()}
        
        # Bulk create products
        print(f"Creating {len(products_to_create)} products...")
        Product.objects.bulk_create(products_to_create, ignore_conflicts=True)
        
        # Fetch created products to get their IDs
        created_products = {p.product_id: p for p in Product.objects.all()}
        
        # Prepare orders
        print("Preparing orders...")
        for idx, row in df.iterrows():
            if (idx + 1) % 500 == 0:
                print(f"  Prepared {idx + 1}/{len(df)} orders...")
            
            customer_id = row['customer_id']
            product_id = row['product_id']
            
            orders_to_create.append(Order(
                order_id=row['order_id'],
                customer=created_customers[customer_id],
                product=created_products[product_id],
                quantity=row['quantity'],
                order_date=pd.to_datetime(row['last_purchase_date']).date()
            ))
        
        # Bulk create orders in batches
        print(f"Creating {len(orders_to_create)} orders...")
        batch_size = 500
        for i in range(0, len(orders_to_create), batch_size):
            batch = orders_to_create[i:i + batch_size]
            Order.objects.bulk_create(batch, ignore_conflicts=True)
            print(f"  Created {min(i + batch_size, len(orders_to_create))}/{len(orders_to_create)} orders...")
        
        print(f"\n✅ Successfully loaded:")
        print(f"   - {Customer.objects.count()} customers")
        print(f"   - {Product.objects.count()} products")
        print(f"   - {Order.objects.count()} orders")
        
    except Exception as e:
        import traceback
        print(f"❌ Error loading data: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    load_data_from_csv()

