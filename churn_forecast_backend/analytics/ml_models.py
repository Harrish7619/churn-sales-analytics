import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from datetime import datetime, timedelta
import joblib
import os
from django.conf import settings


class ChurnPredictionModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.model_version = "v1.0"
        
    def prepare_features(self, df):
        """Prepare features for churn prediction"""
        # Create churn label based on cancellations and purchase frequency
        df['churn'] = ((df['cancellations_count'] > 2) | 
                      (df['purchase_frequency'] < 5) | 
                      (df['ratings'] < 3.0)).astype(int)
        
        # Calculate days since last purchase
        df['last_purchase_date'] = pd.to_datetime(df['last_purchase_date'])
        df['days_since_last_purchase'] = (datetime.now() - df['last_purchase_date']).dt.days
        
        # Encode categorical variables
        categorical_columns = ['gender', 'country', 'subscription_status']
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
            else:
                df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        # Select features
        feature_columns = [
            'age', 'cancellations_count', 'purchase_frequency', 'ratings',
            'days_since_last_purchase', 'gender_encoded', 'country_encoded', 'subscription_status_encoded'
        ]
        
        self.feature_columns = feature_columns
        return df[feature_columns], df['churn']
    
    def train(self, df):
        """Train the churn prediction model"""
        X, y = self.prepare_features(df.copy())
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        # Save model
        self.save_model()
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'test_size': len(X_test)
        }
    
    def predict(self, customer_data):
        """Predict churn probability for a customer"""
        if self.model is None:
            self.load_model()
        
        # Prepare features
        df = pd.DataFrame([customer_data])
        X, _ = self.prepare_features(df)
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict
        churn_probability = self.model.predict_proba(X_scaled)[0, 1]
        
        # Determine risk level
        if churn_probability > 0.7:
            risk_level = "High"
        elif churn_probability > 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            'churn_probability': churn_probability,
            'risk_level': risk_level
        }
    
    def save_model(self):
        """Save the trained model"""
        model_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        os.makedirs(model_dir, exist_ok=True)
        
        joblib.dump(self.model, os.path.join(model_dir, 'churn_model.pkl'))
        joblib.dump(self.scaler, os.path.join(model_dir, 'churn_scaler.pkl'))
        joblib.dump(self.label_encoders, os.path.join(model_dir, 'churn_encoders.pkl'))
        joblib.dump(self.feature_columns, os.path.join(model_dir, 'churn_features.pkl'))
    
    def load_model(self):
        """Load the trained model"""
        model_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        
        self.model = joblib.load(os.path.join(model_dir, 'churn_model.pkl'))
        self.scaler = joblib.load(os.path.join(model_dir, 'churn_scaler.pkl'))
        self.label_encoders = joblib.load(os.path.join(model_dir, 'churn_encoders.pkl'))
        self.feature_columns = joblib.load(os.path.join(model_dir, 'churn_features.pkl'))


class SalesForecastModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_version = "v1.0"
    
    def prepare_sales_data(self, df):
        """Prepare sales data for forecasting"""
        # Group by product and date
        sales_data = df.groupby(['product_id', 'order_date']).agg({
            'quantity': 'sum',
            'unit_price': 'mean'
        }).reset_index()
        
        # Create time series features
        sales_data['order_date'] = pd.to_datetime(sales_data['order_date'])
        sales_data['year'] = sales_data['order_date'].dt.year
        sales_data['month'] = sales_data['order_date'].dt.month
        sales_data['day_of_week'] = sales_data['order_date'].dt.dayofweek
        sales_data['day_of_year'] = sales_data['order_date'].dt.dayofyear
        
        return sales_data
    
    def train(self, df):
        """Train the sales forecasting model"""
        sales_data = self.prepare_sales_data(df)
        
        # Prepare features and target
        feature_columns = ['year', 'month', 'day_of_week', 'day_of_year', 'unit_price']
        X = sales_data[feature_columns]
        y = sales_data['quantity']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Save model
        self.save_model()
        
        return {
            'mse': mse,
            'r2_score': r2,
            'test_size': len(X_test)
        }
    
    def forecast(self, product_data, forecast_period='monthly', forecast_horizon=12):
        """Generate sales forecast for a product"""
        if self.model is None:
            self.load_model()
        
        # Generate future dates
        if forecast_period == 'daily':
            dates = pd.date_range(start=datetime.now(), periods=forecast_horizon, freq='D')
        elif forecast_period == 'weekly':
            dates = pd.date_range(start=datetime.now(), periods=forecast_horizon, freq='W')
        elif forecast_period == 'monthly':
            dates = pd.date_range(start=datetime.now(), periods=forecast_horizon, freq='M')
        elif forecast_period == 'quarterly':
            dates = pd.date_range(start=datetime.now(), periods=forecast_horizon, freq='Q')
        else:  # yearly
            dates = pd.date_range(start=datetime.now(), periods=forecast_horizon, freq='Y')
        
        # Prepare features for forecast
        forecast_data = []
        for date in dates:
            features = {
                'year': date.year,
                'month': date.month,
                'day_of_week': date.dayofweek,
                'day_of_year': date.dayofyear,
                'unit_price': product_data.get('unit_price', 0)
            }
            forecast_data.append(features)
        
        X_forecast = pd.DataFrame(forecast_data)
        X_forecast_scaled = self.scaler.transform(X_forecast)
        
        # Generate predictions
        predictions = self.model.predict(X_forecast_scaled)
        
        # Calculate confidence level (simplified)
        confidence_level = 0.8  # This could be calculated based on model uncertainty
        
        return {
            'dates': dates.tolist(),
            'predictions': predictions.tolist(),
            'confidence_level': confidence_level
        }
    
    def save_model(self):
        """Save the trained model"""
        model_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        os.makedirs(model_dir, exist_ok=True)
        
        joblib.dump(self.model, os.path.join(model_dir, 'sales_model.pkl'))
        joblib.dump(self.scaler, os.path.join(model_dir, 'sales_scaler.pkl'))
    
    def load_model(self):
        """Load the trained model"""
        model_dir = os.path.join(settings.BASE_DIR, 'ml_models')
        
        self.model = joblib.load(os.path.join(model_dir, 'sales_model.pkl'))
        self.scaler = joblib.load(os.path.join(model_dir, 'sales_scaler.pkl'))

