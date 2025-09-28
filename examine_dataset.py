import pandas as pd
import numpy as np

# Read the Excel file
try:
    df = pd.read_excel('E-Commerce Customer Insights and Churn Dataset3938d09.xls')
    print("Dataset loaded successfully!")
    print(f"Shape: {df.shape}")
    print("\nColumn names:")
    print(df.columns.tolist())
    print("\nFirst few rows:")
    print(df.head())
    print("\nData types:")
    print(df.dtypes)
    print("\nBasic statistics:")
    print(df.describe())
    print("\nMissing values:")
    print(df.isnull().sum())
    
    # Save as CSV for easier handling
    df.to_csv('customer_data.csv', index=False)
    print("\nDataset saved as customer_data.csv")
    
except Exception as e:
    print(f"Error reading Excel file: {e}")

