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
            
            # First, get all predictions with probabilities
            all_predictions = []
            predictions_created = 0
            
            for _, row in df.iterrows():
                try:
                    customer = Customer.objects.get(customer_id=row['customer_id'])
                    customer_dict = row.to_dict()
                    
                    # Get probability first (without risk level)
                    df_temp = pd.DataFrame([customer_dict])
                    X, _ = churn_model.prepare_features(df_temp)
                    X_scaled = churn_model.scaler.transform(X)
                    churn_probability = churn_model.model.predict_proba(X_scaled)[0, 1]
                    
                    all_predictions.append({
                        'customer': customer,
                        'churn_probability': churn_probability
                    })
                except Exception as e:
                    print(f"Error predicting for customer {row.get('customer_id', 'unknown')}: {str(e)}")
                    continue
            
            # Calculate percentile-based thresholds to ensure <10% high risk
            if all_predictions:
                probabilities = [p['churn_probability'] for p in all_predictions]
                high_threshold = np.percentile(probabilities, 90)  # Top 10% are high risk
                medium_threshold = np.percentile(probabilities, 70)  # 10-30% are medium risk
                
                # Ensure thresholds are reasonable
                if high_threshold < 0.75:
                    high_threshold = 0.75  # Minimum threshold for high risk
                if medium_threshold < 0.50:
                    medium_threshold = 0.50  # Minimum threshold for medium risk
                
                percentile_thresholds = {
                    'high': high_threshold,
                    'medium': medium_threshold
                }
                
                # Now assign risk levels using percentile-based thresholds
                predictions_to_create = []
                for pred in all_predictions:
                    prob = pred['churn_probability']
                    if prob >= high_threshold:
                        risk_level = "High"
                    elif prob >= medium_threshold:
                        risk_level = "Medium"
                    else:
                        risk_level = "Low"
                    
                    predictions_to_create.append(ChurnPrediction(
                        customer=pred['customer'],
                        churn_probability=prob,
                        risk_level=risk_level,
                        model_version=churn_model.model_version
                    ))
                    predictions_created += 1
                
                # Bulk create predictions
                ChurnPrediction.objects.bulk_create(predictions_to_create, batch_size=500)
                
                # Verify distribution
                total = ChurnPrediction.objects.count()
                high_count = ChurnPrediction.objects.filter(risk_level='High').count()
                medium_count = ChurnPrediction.objects.filter(risk_level='Medium').count()
                low_count = ChurnPrediction.objects.filter(risk_level='Low').count()
                
                print(f"Created {predictions_created} churn predictions")
                print(f"Risk distribution - High: {high_count} ({high_count/total*100:.1f}%), "
                      f"Medium: {medium_count} ({medium_count/total*100:.1f}%), "
                      f"Low: {low_count} ({low_count/total*100:.1f}%)")
                print(f"Thresholds used - High: {high_threshold:.3f}, Medium: {medium_threshold:.3f}")
            else:
                print("No predictions generated")
            
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
            
            import time
            start_time = time.time()
            
            print("=" * 60)
            print("Starting sales forecasting model training...")
            print(f"Processing {len(df)} order records...")
            
            # Train model
            sales_model = SalesForecastModel()
            print("Training the Random Forest model...")
            train_start = time.time()
            performance = sales_model.train(df)
            train_time = time.time() - train_start
            
            print(f"✓ Model trained successfully in {train_time:.2f} seconds!")
            print(f"  R² Score: {performance['r2_score']:.3f}")
            print(f"  MSE: {performance['mse']:.2f}")
            
            # Save performance metrics
            ModelPerformance.objects.create(
                model_type='sales_forecast',
                model_version=sales_model.model_version,
                accuracy=performance['r2_score'],
                precision=0.0,
                recall=0.0,
                f1_score=0.0,
                test_data_size=performance['test_size']
            )
            
            # Only generate forecasts for top 20 products to speed up training
            # Users can generate forecasts on-demand for specific products via the API
            print("\nGenerating forecasts for top 20 products (for dashboard display)...")
            SalesForecast.objects.all().delete()
            
            # Get top products by order count
            top_products = Product.objects.annotate(
                order_count=Count('orders')
            ).filter(order_count__gt=0).order_by('-order_count')[:20]
            
            if not top_products.exists():
                print("No products with orders found. Skipping forecast generation.")
                total_time = time.time() - start_time
                return Response({
                    'message': 'Sales forecasting model trained successfully',
                    'performance': performance,
                    'forecasts_generated': 0,
                    'products_forecasted': 0,
                    'training_time_seconds': round(train_time, 2),
                    'total_time_seconds': round(total_time, 2),
                    'note': 'No products with orders found. Model is ready for on-demand forecasting.'
                })
            
            forecasts_to_create = []
            forecast_start = time.time()
            
            for idx, product in enumerate(top_products, 1):
                try:
                    # Generate monthly forecast for next 12 months
                    forecast_data = {
                        'unit_price': product.unit_price,
                        'forecast_period': 'monthly',
                        'forecast_horizon': 12
                    }
                    
                    forecast_result = sales_model.forecast(forecast_data)
                    
                    # Prepare forecasts for bulk creation
                    for date, quantity in zip(forecast_result['dates'], forecast_result['predictions']):
                        forecasts_to_create.append(SalesForecast(
                            product=product,
                            forecast_date=date.date() if hasattr(date, 'date') else date,
                            predicted_quantity=int(max(0, quantity)),
                            confidence_level=forecast_result['confidence_level'],
                            forecast_period='monthly',
                            model_version=sales_model.model_version
                        ))
                    
                    if idx % 5 == 0:
                        print(f"  Processed {idx}/{len(top_products)} products...")
                        
                except Exception as e:
                    print(f"  ⚠ Error forecasting for product {product.product_id}: {str(e)}")
                    continue
            
            # Bulk insert all forecasts at once
            if forecasts_to_create:
                print(f"Inserting {len(forecasts_to_create)} forecasts into database...")
                SalesForecast.objects.bulk_create(forecasts_to_create, batch_size=500)
                forecast_time = time.time() - forecast_start
                print(f"✓ Generated {len(forecasts_to_create)} forecasts for {len(top_products)} products in {forecast_time:.2f} seconds")
            else:
                print("⚠ No forecasts generated")
            
            total_time = time.time() - start_time
            print("=" * 60)
            print(f"✓ Sales forecasting model training completed in {total_time:.2f} seconds!")
            print("=" * 60)
            
            return Response({
                'message': 'Sales forecasting model trained successfully',
                'performance': performance,
                'forecasts_generated': len(forecasts_to_create),
                'products_forecasted': len(top_products),
                'training_time_seconds': round(train_time, 2),
                'forecast_generation_time_seconds': round(forecast_time if forecasts_to_create else 0, 2),
                'total_time_seconds': round(total_time, 2),
                'note': 'Forecasts generated for top 20 products. Use forecast_sales endpoint for other products.'
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
            
            # Save forecasts to database for top_selling endpoint
            SalesForecast.objects.filter(product=product).delete()  # Clear existing forecasts
            
            for i, (date, quantity) in enumerate(zip(forecast_result['dates'], forecast_result['predictions'])):
                SalesForecast.objects.create(
                    product=product,
                    forecast_date=date.date(),
                    predicted_quantity=int(max(0, quantity)),
                    confidence_level=forecast_result['confidence_level'],
                    forecast_period=forecast_period,
                    model_version=sales_model.model_version
                )
            
            return Response(forecast_result)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def generate_all_forecasts(self, request):
        """Generate sales forecasts for all products with extended periods"""
        try:
            from datetime import datetime, timedelta
            
            # Get all products
            products = Product.objects.all()
            orders = Order.objects.select_related('product').all()
            
            # Clear existing forecasts
            SalesForecast.objects.all().delete()
            
            sales_model = SalesForecastModel()
            
            for product in products:
                product_orders = orders.filter(product=product)
                if product_orders.exists():
                    # Generate forecasts for different periods
                    periods = [
                        {'period': 'quarterly', 'horizon': 4, 'freq': 'Q'},  # Next 4 quarters
                        {'period': 'yearly', 'horizon': 3, 'freq': 'Y'},     # Next 3 years (2025-2027)
                    ]
                    
                    for period_config in periods:
                        forecast_data = {
                            'unit_price': product.unit_price,
                            'forecast_period': period_config['period'],
                            'forecast_horizon': period_config['horizon']
                        }
                        
                        forecast_result = sales_model.forecast(forecast_data)
                        
                        # Save forecasts
                        for i, (date, quantity) in enumerate(zip(forecast_result['dates'], forecast_result['predictions'])):
                            SalesForecast.objects.create(
                                product=product,
                                forecast_date=date.date(),
                                predicted_quantity=int(max(0, quantity)),
                                confidence_level=forecast_result['confidence_level'],
                                forecast_period=period_config['period'],
                                model_version=sales_model.model_version
                            )
            
            return Response({
                'message': f'Generated forecasts for {products.count()} products',
                'forecast_periods': ['quarterly', 'yearly'],
                'time_horizon': '2025-2027'
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

