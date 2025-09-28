from django.db import models
from django.utils import timezone


class Customer(models.Model):
    customer_id = models.CharField(max_length=50, unique=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    signup_date = models.DateField()
    last_purchase_date = models.DateField()
    cancellations_count = models.IntegerField(default=0)
    subscription_status = models.CharField(max_length=20)
    purchase_frequency = models.IntegerField(default=0)
    ratings = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'

    def __str__(self):
        return f"Customer {self.customer_id}"


class Product(models.Model):
    product_id = models.CharField(max_length=50, unique=True)
    product_name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    unit_price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return f"{self.product_name} ({self.product_id})"


class Order(models.Model):
    order_id = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.IntegerField()
    order_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order {self.order_id}"

    @property
    def total_amount(self):
        return self.quantity * self.product.unit_price


class ChurnPrediction(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='churn_predictions')
    churn_probability = models.FloatField()
    risk_level = models.CharField(max_length=20)  # High, Medium, Low
    prediction_date = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(max_length=50, default='v1.0')

    class Meta:
        db_table = 'churn_predictions'

    def __str__(self):
        return f"Churn prediction for {self.customer.customer_id}"


class SalesForecast(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_forecasts')
    forecast_date = models.DateField()
    predicted_quantity = models.IntegerField()
    confidence_level = models.FloatField()
    forecast_period = models.CharField(max_length=20)  # daily, weekly, monthly, quarterly, yearly
    model_version = models.CharField(max_length=50, default='v1.0')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sales_forecasts'

    def __str__(self):
        return f"Sales forecast for {self.product.product_name} on {self.forecast_date}"


class ModelPerformance(models.Model):
    model_type = models.CharField(max_length=50)  # churn_prediction, sales_forecast
    model_version = models.CharField(max_length=50)
    accuracy = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    f1_score = models.FloatField()
    training_date = models.DateTimeField(auto_now_add=True)
    test_data_size = models.IntegerField()

    class Meta:
        db_table = 'model_performance'

    def __str__(self):
        return f"{self.model_type} v{self.model_version} - Accuracy: {self.accuracy:.3f}"