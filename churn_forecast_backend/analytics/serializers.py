from rest_framework import serializers
from .models import Customer, Product, Order, ChurnPrediction, SalesForecast, ModelPerformance


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
    
    def validate(self, data):
        """Validate customer data"""
        errors = {}
        
        # Check for duplicate customer_id
        customer_id = data.get('customer_id')
        if customer_id and Customer.objects.filter(customer_id=customer_id).exists():
            if not self.instance or self.instance.customer_id != customer_id:
                errors['customer_id'] = [f'Customer with ID "{customer_id}" already exists. Please use a different customer ID.']
        
        # Validate dates
        signup_date = data.get('signup_date')
        last_purchase_date = data.get('last_purchase_date')
        if signup_date and last_purchase_date and last_purchase_date < signup_date:
            errors['last_purchase_date'] = ['Last purchase date cannot be before signup date.']
        
        # Validate age
        age = data.get('age')
        if age is not None and (age < 18 or age > 120):
            errors['age'] = ['Age must be between 18 and 120.']
        
        # Validate ratings
        ratings = data.get('ratings')
        if ratings is not None and (ratings < 1.0 or ratings > 5.0):
            errors['ratings'] = ['Ratings must be between 1.0 and 5.0.']
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
    
    def validate(self, data):
        """Validate product data"""
        errors = {}
        
        # Check for duplicate product_id
        product_id = data.get('product_id')
        if product_id and Product.objects.filter(product_id=product_id).exists():
            if not self.instance or self.instance.product_id != product_id:
                errors['product_id'] = [f'Product with ID "{product_id}" already exists. Please use a different product ID.']
        
        # Validate unit_price
        unit_price = data.get('unit_price')
        if unit_price is not None and unit_price < 0:
            errors['unit_price'] = ['Unit price cannot be negative.']
        
        # Validate required fields
        if not data.get('product_name'):
            errors['product_name'] = ['Product name is required.']
        
        if not data.get('category'):
            errors['category'] = ['Category is required.']
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.customer_id', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    total_amount = serializers.ReadOnlyField()
    # Write-only fields for accepting IDs
    customer_id = serializers.CharField(write_only=True, required=False)
    product_id = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer', 'product', 'customer_name', 'product_name', 
                 'quantity', 'order_date', 'total_amount', 'created_at', 'updated_at',
                 'customer_id', 'product_id']
        read_only_fields = ['id', 'customer', 'product', 'customer_name', 'product_name', 
                          'total_amount', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Handle both 'customer'/'product' and 'customer_id'/'product_id' formats
        customer_id = validated_data.pop('customer_id', None)
        product_id = validated_data.pop('product_id', None)
        
        # If customer/product are already ForeignKey objects, use them
        customer = validated_data.get('customer')
        product = validated_data.get('product')
        
        # Collect validation errors
        errors = {}
        
        # Otherwise, look them up by ID
        if not customer:
            if not customer_id:
                errors['customer_id'] = ['Customer ID is required']
            else:
                try:
                    customer = Customer.objects.get(customer_id=customer_id)
                except Customer.DoesNotExist:
                    errors['customer_id'] = [f'Customer with ID "{customer_id}" does not exist. Please create the customer first.']
        
        if not product:
            if not product_id:
                errors['product_id'] = ['Product ID is required']
            else:
                try:
                    product = Product.objects.get(product_id=product_id)
                except Product.DoesNotExist:
                    errors['product_id'] = [f'Product with ID "{product_id}" does not exist. Please create the product first.']
        
        # Check for duplicate order_id
        order_id = validated_data.get('order_id')
        if order_id and Order.objects.filter(order_id=order_id).exists():
            errors['order_id'] = [f'Order with ID "{order_id}" already exists. Please use a different order ID.']
        
        # Raise all validation errors at once
        if errors:
            raise serializers.ValidationError(errors)
        
        validated_data['customer'] = customer
        validated_data['product'] = product
        
        return super().create(validated_data)


class ChurnPredictionSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(source='customer.customer_id', read_only=True)
    customer_age = serializers.IntegerField(source='customer.age', read_only=True)
    customer_gender = serializers.CharField(source='customer.gender', read_only=True)
    customer_country = serializers.CharField(source='customer.country', read_only=True)

    class Meta:
        model = ChurnPrediction
        fields = '__all__'


class SalesForecastSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_category = serializers.CharField(source='product.category', read_only=True)
    unit_price = serializers.FloatField(source='product.unit_price', read_only=True)

    class Meta:
        model = SalesForecast
        fields = '__all__'


class ModelPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelPerformance
        fields = '__all__'


class CustomerChurnDataSerializer(serializers.Serializer):
    customer_id = serializers.CharField()
    age = serializers.IntegerField()
    gender = serializers.CharField()
    country = serializers.CharField()
    cancellations_count = serializers.IntegerField()
    subscription_status = serializers.CharField()
    purchase_frequency = serializers.IntegerField()
    ratings = serializers.FloatField()
    days_since_last_purchase = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    avg_order_value = serializers.FloatField()


class SalesForecastDataSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    product_name = serializers.CharField()
    category = serializers.CharField()
    historical_sales = serializers.ListField(child=serializers.FloatField())
    forecast_period = serializers.CharField()
    forecast_horizon = serializers.IntegerField()

