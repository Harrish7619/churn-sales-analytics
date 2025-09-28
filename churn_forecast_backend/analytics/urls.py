from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, ml_views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'churn-predictions', views.ChurnPredictionViewSet)
router.register(r'sales-forecasts', views.SalesForecastViewSet)
router.register(r'model-performance', views.ModelPerformanceViewSet)
router.register(r'ml-training', ml_views.MLTrainingViewSet, basename='ml-training')

urlpatterns = [
    path('', include(router.urls)),
]

