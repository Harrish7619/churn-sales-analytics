from rest_framework import serializers
from .models import Customer, Product, Order, ChurnPrediction, SalesForecast, ModelPerformance


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.customer_id', read_only=True)
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = '__all__'


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

