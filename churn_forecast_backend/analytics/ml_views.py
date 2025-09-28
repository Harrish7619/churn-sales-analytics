from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .models import Customer, Product, Order, ChurnPrediction, SalesForecast, ModelPerformance
from .serializers import (
    CustomerSerializer, ProductSerializer, OrderSerializer,
    ChurnPredictionSerializer, SalesForecastSerializer, ModelPerformanceSerializer,
    CustomerChurnDataSerializer, SalesForecastDataSerializer
)
from .ml_models import ChurnPredictionModel, SalesForecastModel


class MLTrainingViewSet(viewsets.ViewSet):
    """ViewSet for ML model training and prediction"""
    
    @action(detail=False, methods=['post'])
    def train_churn_model(self, request):
        """Train the churn prediction model"""
        try:
            # Get all customer data
            customers = Customer.objects.all()
            orders = Order.objects.select_related('customer', 'product').all()
            
            # Convert to DataFrame
            customer_data = []
            for customer in customers:
                customer_orders = orders.filter(customer=customer)
                total_orders = customer_orders.count()
                avg_order_value = customer_orders.aggregate(
                    avg_value=Avg('quantity') * Avg('product__unit_price')
                )['avg_value'] or 0
                
                customer_data.append({
                    'customer_id': customer.customer_id,
                    'age': customer.age,
                    'gender': customer.gender,
                    'country': customer.country,
                    'signup_date': customer.signup_date,
                    'last_purchase_date': customer.last_purchase_date,
                    'cancellations_count': customer.cancellations_count,
                    'subscription_status': customer.subscription_status,
                    'purchase_frequency': customer.purchase_frequency,
                    'ratings': customer.ratings,
                    'total_orders': total_orders,
                    'avg_order_value': avg_order_value
                })
            
            df = pd.DataFrame(customer_data)
            
            # Train model
            churn_model = ChurnPredictionModel()
            performance = churn_model.train(df)
            
            # Save performance metrics
            ModelPerformance.objects.create(
                model_type='churn_prediction',
                model_version=churn_model.model_version,
                accuracy=performance['accuracy'],
                precision=performance['precision'],
                recall=performance['recall'],
                f1_score=performance['f1_score'],
                test_data_size=performance['test_size']
            )
            
            # Generate predictions for all customers
            ChurnPrediction.objects.all().delete()  # Clear existing predictions
            
            for _, row in df.iterrows():
                customer = Customer.objects.get(customer_id=row['customer_id'])
                prediction = churn_model.predict(row.to_dict())
                
                ChurnPrediction.objects.create(
                    customer=customer,
                    churn_probability=prediction['churn_probability'],
                    risk_level=prediction['risk_level'],
                    model_version=churn_model.model_version
                )
            
            return Response({
                'message': 'Churn prediction model trained successfully',
                'performance': performance
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def train_sales_model(self, request):
        """Train the sales forecasting model"""
        try:
            # Get all order data
            orders = Order.objects.select_related('customer', 'product').all()
            
            # Convert to DataFrame
            order_data = []
            for order in orders:
                order_data.append({
                    'order_id': order.order_id,
                    'product_id': order.product.product_id,
                    'product_name': order.product.product_name,
                    'category': order.product.category,
                    'unit_price': order.product.unit_price,
                    'quantity': order.quantity,
                    'order_date': order.order_date
                })
            
            df = pd.DataFrame(order_data)
            
            # Train model
            sales_model = SalesForecastModel()
            performance = sales_model.train(df)
            
            # Save performance metrics
            ModelPerformance.objects.create(
                model_type='sales_forecast',
                model_version=sales_model.model_version,
                accuracy=performance['r2_score'],  # Using R2 as accuracy metric
                precision=0.0,  # Not applicable for regression
                recall=0.0,     # Not applicable for regression
                f1_score=0.0,   # Not applicable for regression
                test_data_size=performance['test_size']
            )
            
            # Generate forecasts for all products
            SalesForecast.objects.all().delete()  # Clear existing forecasts
            
            products = Product.objects.all()
            for product in products:
                product_orders = orders.filter(product=product)
                if product_orders.exists():
                    # Generate monthly forecast for next 12 months
                    forecast_data = {
                        'product_id': product.product_id,
                        'product_name': product.product_name,
                        'category': product.category,
                        'unit_price': product.unit_price,
                        'historical_sales': list(product_orders.values_list('quantity', flat=True)),
                        'forecast_period': 'monthly',
                        'forecast_horizon': 12
                    }
                    
                    forecast_result = sales_model.forecast(forecast_data)
                    
                    # Save forecasts
                    for i, (date, quantity) in enumerate(zip(forecast_result['dates'], forecast_result['predictions'])):
                        SalesForecast.objects.create(
                            product=product,
                            forecast_date=date.date(),
                            predicted_quantity=int(max(0, quantity)),  # Ensure non-negative
                            confidence_level=forecast_result['confidence_level'],
                            forecast_period='monthly',
                            model_version=sales_model.model_version
                        )
            
            return Response({
                'message': 'Sales forecasting model trained successfully',
                'performance': performance
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def predict_churn(self, request):
        """Predict churn for a specific customer"""
        try:
            customer_id = request.data.get('customer_id')
            customer = get_object_or_404(Customer, customer_id=customer_id)
            
            # Get customer data
            orders = Order.objects.filter(customer=customer)
            total_orders = orders.count()
            avg_order_value = orders.aggregate(
                avg_value=Avg('quantity') * Avg('product__unit_price')
            )['avg_value'] or 0
            
            customer_data = {
                'customer_id': customer.customer_id,
                'age': customer.age,
                'gender': customer.gender,
                'country': customer.country,
                'signup_date': customer.signup_date,
                'last_purchase_date': customer.last_purchase_date,
                'cancellations_count': customer.cancellations_count,
                'subscription_status': customer.subscription_status,
                'purchase_frequency': customer.purchase_frequency,
                'ratings': customer.ratings,
                'total_orders': total_orders,
                'avg_order_value': avg_order_value
            }
            
            # Load model and predict
            churn_model = ChurnPredictionModel()
            prediction = churn_model.predict(customer_data)
            
            return Response(prediction)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def forecast_sales(self, request):
        """Generate sales forecast for a specific product"""
        try:
            product_id = request.data.get('product_id')
            forecast_period = request.data.get('forecast_period', 'monthly')
            forecast_horizon = int(request.data.get('forecast_horizon', 12))
            
            product = get_object_or_404(Product, product_id=product_id)
            orders = Order.objects.filter(product=product)
            
            if not orders.exists():
                return Response({
                    'error': 'No historical data available for this product'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Prepare forecast data
            forecast_data = {
                'product_id': product.product_id,
                'product_name': product.product_name,
                'category': product.category,
                'unit_price': product.unit_price,
                'historical_sales': list(orders.values_list('quantity', flat=True)),
                'forecast_period': forecast_period,
                'forecast_horizon': forecast_horizon
            }
            
            # Load model and forecast
            sales_model = SalesForecastModel()
            forecast_result = sales_model.forecast(forecast_data)
            
            return Response(forecast_result)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

