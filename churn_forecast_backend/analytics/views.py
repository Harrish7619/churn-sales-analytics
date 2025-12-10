from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum, Case, When, Value
from django.db import models
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


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    @action(detail=False, methods=['get'])
    def top_churn_risk(self, request):
        """Get top 10 customers with highest churn risk"""
        predictions = ChurnPrediction.objects.filter(
            risk_level='High'
        ).order_by('-churn_probability')[:10]
        
        serializer = ChurnPredictionSerializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def churn_analytics(self, request):
        """Get churn analytics and trends"""
        # Get churn rate trends
        predictions = ChurnPrediction.objects.all()
        
        # Calculate overall churn rate
        total_customers = Customer.objects.count()
        high_risk_customers = predictions.filter(risk_level='High').count()
        churn_rate = (high_risk_customers / total_customers * 100) if total_customers > 0 else 0
        
        # Risk level distribution - handle empty predictions
        if predictions.exists():
            risk_distribution = predictions.values('risk_level').annotate(
                count=Count('id')
            ).order_by('risk_level')
            
            # Churn by country
            churn_by_country = predictions.select_related('customer').values(
                'customer__country'
            ).annotate(
                total_customers=Count('id'),
                high_risk=Count('id', filter=Q(risk_level='High'))
            ).order_by('-high_risk')
            
            # Churn by age group - using Django ORM instead of raw SQL
            churn_by_age = predictions.select_related('customer').annotate(
                age_group=Case(
                    When(customer__age__lt=30, then=Value('18-29')),
                    When(customer__age__lt=40, then=Value('30-39')),
                    When(customer__age__lt=50, then=Value('40-49')),
                    When(customer__age__lt=60, then=Value('50-59')),
                    default=Value('60+'),
                    output_field=models.CharField()
                )
            ).values('age_group').annotate(
                total_customers=Count('id'),
                high_risk=Count('id', filter=Q(risk_level='High'))
            ).order_by('age_group')
        else:
            # Return empty data if no predictions exist
            risk_distribution = []
            churn_by_country = []
            churn_by_age = []
        
        return Response({
            'overall_churn_rate': round(churn_rate, 2),
            'total_customers': total_customers,
            'high_risk_customers': high_risk_customers,
            'risk_distribution': list(risk_distribution),
            'churn_by_country': list(churn_by_country),
            'churn_by_age_group': list(churn_by_age),
            'predictions_exist': predictions.exists()
        })

    @action(detail=False, methods=['get'])
    def paginated_customers(self, request):
        """Get paginated customers with churn predictions"""
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        risk_filter = request.GET.get('risk_level', None)
        country_filter = request.GET.get('country', None)
        
        # Build query
        queryset = ChurnPrediction.objects.select_related('customer').all()
        
        if risk_filter:
            queryset = queryset.filter(risk_level=risk_filter)
        
        if country_filter:
            queryset = queryset.filter(customer__country=country_filter)
        
        # Order by churn probability (highest risk first)
        queryset = queryset.order_by('-churn_probability')
        
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = queryset[start:end]
        
        serializer = ChurnPredictionSerializer(paginated_data, many=True)
        
        return Response({
            'data': serializer.data,
            'page': page,
            'page_size': page_size,
            'total_count': queryset.count(),
            'has_next': end < queryset.count(),
            'has_previous': page > 1
        })


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['get'])
    def top_selling(self, request):
        """Get top 10 products with highest predicted sales"""
        # Get recent sales forecasts
        recent_forecasts = SalesForecast.objects.filter(
            forecast_date__gte=timezone.now().date()
        ).order_by('-predicted_quantity')[:10]
        
        serializer = SalesForecastSerializer(recent_forecasts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sales_analytics(self, request):
        """Get sales analytics and trends"""
        # Get sales trends
        orders = Order.objects.select_related('product', 'customer').all()
        
        # Sales by category
        sales_by_category = orders.values('product__category').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('quantity') * Avg('product__unit_price'),
            order_count=Count('id')
        ).order_by('-total_revenue')
        
        # Sales by country
        sales_by_country = orders.values('customer__country').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('quantity') * Avg('product__unit_price'),
            order_count=Count('id')
        ).order_by('-total_revenue')
        
        # Monthly sales trend
        monthly_sales = orders.extra(
            select={'year_month': "strftime('%Y-%m', order_date)"}
        ).values('year_month').annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum('quantity') * Avg('product__unit_price')
        ).order_by('year_month')
        
        return Response({
            'sales_by_category': list(sales_by_category),
            'sales_by_country': list(sales_by_country),
            'monthly_sales_trend': list(monthly_sales)
        })


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ChurnPredictionViewSet(viewsets.ModelViewSet):
    queryset = ChurnPrediction.objects.all()
    serializer_class = ChurnPredictionSerializer


class SalesForecastViewSet(viewsets.ModelViewSet):
    queryset = SalesForecast.objects.all()
    serializer_class = SalesForecastSerializer


class ModelPerformanceViewSet(viewsets.ModelViewSet):
    queryset = ModelPerformance.objects.all()
    serializer_class = ModelPerformanceSerializer