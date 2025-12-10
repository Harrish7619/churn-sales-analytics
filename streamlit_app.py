import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json

# Configure Streamlit page
st.set_page_config(
    page_title="Customer Churn & Sales Forecasting Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE_URL = "http://localhost:8000/api"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .stButton > button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #0d5aa7;
    }
</style>
""", unsafe_allow_html=True)

def make_api_request(endpoint, method="GET", data=None):
    """Make API request to Django backend"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        # Accept both 200 (OK) and 201 (Created) status codes
        if response.status_code in [200, 201]:
            return response.json()
        else:
            # Try to parse error message from response
            try:
                error_data = response.json()
                # Handle different error formats
                if 'detail' in error_data:
                    st.error(f"**Error:** {error_data['detail']}")
                elif isinstance(error_data, dict):
                    # Display field-specific validation errors
                    st.error("**Validation Errors:**")
                    for field, errors in error_data.items():
                        if isinstance(errors, list):
                            error_text = ', '.join([str(e) for e in errors])
                        else:
                            error_text = str(errors)
                        # Format field name nicely
                        field_name = field.replace('_', ' ').title()
                        st.warning(f"  • **{field_name}**: {error_text}")
                else:
                    st.error(f"**Error:** {str(error_data)}")
            except:
                st.error(f"**API Error ({response.status_code}):** {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend API. Please make sure the Django server is running.")
        return None
    except Exception as e:
        st.error(f"Error making API request: {str(e)}")
        return None

def main():
    # Main header
    st.markdown('<h1 class="main-header">📊 Customer Churn & Sales Forecasting Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "⚠️ Churn Prediction", "📈 Sales Forecasting", "📝 Data Input", "🤖 Model Training"]
    )
    
    if page == "🏠 Home":
        show_home_page()
    elif page == "⚠️ Churn Prediction":
        show_churn_dashboard()
    elif page == "📈 Sales Forecasting":
        show_sales_dashboard()
    elif page == "📝 Data Input":
        show_data_input_page()
    elif page == "🤖 Model Training":
        show_model_training_page()

def show_home_page():
    """Display the home page with overview"""
    st.markdown("## Welcome to the Customer Analytics Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### ⚠️ Churn Prediction
        - Identify high-risk customers
        - Analyze churn trends
        - Customer segmentation
        - Retention strategies
        """)
    
    with col2:
        st.markdown("""
        ### 📈 Sales Forecasting
        - Predict future sales
        - Top performing products
        - Demand forecasting
        - Inventory optimization
        """)
    
    with col3:
        st.markdown("""
        ### 🛠️ Management Tools
        - Data input interface
        - Model training
        - Performance monitoring
        - Export capabilities
        """)
    
    # Quick stats
    st.markdown("## Quick Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get basic stats from API
    customers_data = make_api_request("customers/")
    if customers_data:
        with col1:
            st.metric("Total Customers", len(customers_data))
        
        with col2:
            st.metric("Total Products", len(make_api_request("products/") or []))
        
        with col3:
            st.metric("Total Orders", len(make_api_request("orders/") or []))
        
        with col4:
            churn_analytics = make_api_request("customers/churn_analytics/")
            if churn_analytics:
                if not churn_analytics.get('predictions_exist', True):
                    st.metric("Churn Rate", "N/A", help="Train the churn model first")
                else:
                    st.metric("Churn Rate", f"{churn_analytics.get('overall_churn_rate', 0):.1f}%")

def show_churn_dashboard():
    """Display the churn prediction dashboard"""
    st.markdown("## ⚠️ Customer Churn Prediction Dashboard")
    
    # Get churn analytics
    churn_analytics = make_api_request("customers/churn_analytics/")
    
    if churn_analytics and churn_analytics.get('predictions_exist', False):
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Overall Churn Rate",
                f"{churn_analytics['overall_churn_rate']:.1f}%",
                delta=None
            )
        
        with col2:
            st.metric(
                "Total Customers",
                churn_analytics['total_customers']
            )
        
        with col3:
            st.metric(
                "High Risk Customers",
                churn_analytics['high_risk_customers']
            )
        
        with col4:
            low_risk = churn_analytics['total_customers'] - churn_analytics['high_risk_customers']
            st.metric(
                "Low Risk Customers",
                low_risk
            )
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk level distribution
            risk_data = churn_analytics['risk_distribution']
            if risk_data:
                risk_df = pd.DataFrame(risk_data)
                fig = px.pie(risk_df, values='count', names='risk_level', 
                           title="Risk Level Distribution",
                           color_discrete_map={'High': '#ff4444', 'Medium': '#ffaa00', 'Low': '#44ff44'})
                st.plotly_chart(fig, config={'displayModeBar': True, 'displaylogo': False})
        
        with col2:
            # Churn by country
            country_data = churn_analytics['churn_by_country']
            if country_data:
                country_df = pd.DataFrame(country_data)
                country_df['churn_rate'] = (country_df['high_risk'] / country_df['total_customers'] * 100).round(1)
                fig = px.bar(country_df, x='customer__country', y='churn_rate',
                           title="Churn Rate by Country")
                fig.update_xaxes(title="Country")
                fig.update_yaxes(title="Churn Rate (%)")
                st.plotly_chart(fig, config={'displayModeBar': True, 'displaylogo': False})
        
        # Age group analysis
        age_data = churn_analytics['churn_by_age_group']
        if age_data:
            age_df = pd.DataFrame(age_data)
            age_df['churn_rate'] = (age_df['high_risk'] / age_df['total_customers'] * 100).round(1)
            fig = px.bar(age_df, x='age_group', y='churn_rate',
                       title="Churn Rate by Age Group")
            fig.update_xaxes(title="Age Group")
            fig.update_yaxes(title="Churn Rate (%)")
            st.plotly_chart(fig, config={'displayModeBar': True, 'displaylogo': False})
    
    # Top 10 high-risk customers
    st.markdown("## 🔴 Top 10 High-Risk Customers")
    
    if not churn_analytics or not churn_analytics.get('predictions_exist', False):
        st.warning("⚠️ No churn predictions available. Please train the churn prediction model first from the 'Model Training' page.")
    else:
        top_risk = make_api_request("customers/top_churn_risk/")
        if top_risk:
            risk_df = pd.DataFrame(top_risk)
            if not risk_df.empty:
                # Format the data for display
                display_df = risk_df[['customer_id', 'churn_probability', 'risk_level', 
                                    'customer_age', 'customer_gender', 'customer_country']].copy()
                display_df['churn_probability'] = (display_df['churn_probability'] * 100).round(1)
                # Add serial number starting from 1
                display_df.insert(0, 'S.No.', range(1, len(display_df) + 1))
                display_df.columns = ['S.No.', 'Customer ID', 'Churn Probability (%)', 'Risk Level', 
                                    'Age', 'Gender', 'Country']
                
                st.dataframe(display_df.reset_index(drop=True), width='stretch', hide_index=True)
                
                # Download button
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download High-Risk Customers",
                    data=csv,
                    file_name=f"high_risk_customers_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    # Paginated customer list with filters
    st.markdown("## 📋 All Customers (Paginated)")
    
    if not churn_analytics or not churn_analytics.get('predictions_exist', False):
        st.info("ℹ️ Customer predictions will appear here after training the churn model.")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_filter = st.selectbox("Filter by Risk Level", ["All", "High", "Medium", "Low"])
        
        with col2:
            country_filter = st.selectbox("Filter by Country", ["All"] + 
                                        [c['customer__country'] for c in (churn_analytics.get('churn_by_country', []) if churn_analytics else [])])
        
        with col3:
            page_size = st.selectbox("Records per page", [10, 20, 50])
        
        # Initialize session state for pagination
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        # Get paginated data first to check pagination state
        params = {
            'page': st.session_state.current_page,
            'page_size': page_size
        }
        
        if risk_filter != "All":
            params['risk_level'] = risk_filter
        
        if country_filter != "All":
            params['country'] = country_filter
        
        # Build query string
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        paginated_data = make_api_request(f"customers/paginated_customers/?{query_string}")
        
        # Handle pagination buttons based on API response
        if paginated_data:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                prev_disabled = not paginated_data.get('has_previous', False)
                if st.button("◀️ Previous", disabled=prev_disabled):
                    st.session_state.current_page -= 1
                    st.rerun()
            
            with col2:
                st.write(f"Page {st.session_state.current_page}")
            
            with col3:
                next_disabled = not paginated_data.get('has_next', False)
                if st.button("Next ▶️", disabled=next_disabled):
                    st.session_state.current_page += 1
                    st.rerun()
            
            if paginated_data and paginated_data.get('data'):
                customers_df = pd.DataFrame(paginated_data['data'])
                if not customers_df.empty:
                    # Format for display
                    display_df = customers_df[['customer_id', 'churn_probability', 'risk_level',
                                             'customer_age', 'customer_gender', 'customer_country']].copy()
                    display_df['churn_probability'] = (display_df['churn_probability'] * 100).round(1)
                    # Add serial number that continues across pages
                    # Formula: (current_page - 1) * page_size + row_index + 1
                    start_num = (st.session_state.current_page - 1) * page_size + 1
                    display_df.insert(0, 'S.No.', range(start_num, start_num + len(display_df)))
                    display_df.columns = ['S.No.', 'Customer ID', 'Churn Probability (%)', 'Risk Level',
                                        'Age', 'Gender', 'Country']
                    
                    st.dataframe(display_df.reset_index(drop=True), width='stretch', hide_index=True)
                    
                    # Pagination info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.info(f"Page {paginated_data['page']} of {(paginated_data['total_count'] // page_size) + 1}")
                    with col2:
                        st.info(f"Total Records: {paginated_data['total_count']}")
                    with col3:
                        # Show pagination status
                        if not paginated_data.get('has_next', False):
                            st.info("Last page")
                        if not paginated_data.get('has_previous', False):
                            st.info("First page")

def show_sales_dashboard():
    """Display the sales forecasting dashboard"""
    st.markdown("## 📈 Sales Forecasting Dashboard")
    
    # Get sales analytics
    sales_analytics = make_api_request("products/sales_analytics/")
    
    if sales_analytics:
        # Sales by category
        col1, col2 = st.columns(2)
        
        with col1:
            category_data = sales_analytics['sales_by_category']
            if category_data:
                category_df = pd.DataFrame(category_data)
                fig = px.pie(category_df, values='total_revenue', names='product__category',
                           title="Revenue by Product Category")
                st.plotly_chart(fig, config={'displayModeBar': True, 'displaylogo': False})
        
        with col2:
            country_data = sales_analytics['sales_by_country']
            if country_data:
                country_df = pd.DataFrame(country_data)
                fig = px.bar(country_df, x='customer__country', y='total_revenue',
                           title="Revenue by Country")
                fig.update_xaxes(title="Country")
                fig.update_yaxes(title="Revenue")
                st.plotly_chart(fig, config={'displayModeBar': True, 'displaylogo': False})
        
        # Monthly sales trend
        monthly_data = sales_analytics['monthly_sales_trend']
        if monthly_data:
            monthly_df = pd.DataFrame(monthly_data)
            monthly_df['year_month'] = pd.to_datetime(monthly_df['year_month'])
            fig = px.line(monthly_df, x='year_month', y='total_revenue',
                         title="Monthly Sales Trend")
            fig.update_xaxes(title="Month")
            fig.update_yaxes(title="Revenue")
            st.plotly_chart(fig, config={'displayModeBar': True, 'displaylogo': False})
    
    # Top 10 products with highest predicted sales
    st.markdown("## 🏆 Top 10 Products with Highest Predicted Sales")
    
    top_products = make_api_request("products/top_selling/")
    if top_products:
        products_df = pd.DataFrame(top_products)
        if not products_df.empty:
            # Format for display
            display_df = products_df[['product_name', 'product_category', 'predicted_quantity', 
                                    'confidence_level', 'forecast_date']].copy()
            display_df['confidence_level'] = (display_df['confidence_level'] * 100).round(1)
            # Add serial number starting from 1
            display_df.insert(0, 'S.No.', range(1, len(display_df) + 1))
            display_df.columns = ['S.No.', 'Product Name', 'Category', 'Predicted Quantity', 
                                'Confidence (%)', 'Forecast Date']
            
            st.dataframe(display_df.reset_index(drop=True), width='stretch', hide_index=True)
            
            # Download button
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Top Products Forecast",
                data=csv,
                file_name=f"top_products_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Sales forecast filters and visualization
    st.markdown("## 📊 Sales Forecast Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        forecast_period = st.selectbox("Forecast Period", ["daily", "weekly", "monthly", "quarterly", "yearly"])
    
    with col2:
        forecast_horizon = st.slider("Forecast Horizon", min_value=1, max_value=24, value=12)
    
    # Product selection for detailed forecast
    products = make_api_request("products/")
    if products:
        product_options = {f"{p['product_name']} ({p['product_id']})": p['product_id'] 
                          for p in products}
        selected_product = st.selectbox("Select Product for Detailed Forecast", 
                                      list(product_options.keys()))
        
        if st.button("Generate Forecast"):
            product_id = product_options[selected_product]
            forecast_data = {
                'product_id': product_id,
                'forecast_period': forecast_period,
                'forecast_horizon': forecast_horizon
            }
            
            forecast_result = make_api_request("ml-training/forecast_sales/", 
                                             method="POST", data=forecast_data)
            
            if forecast_result:
                # Create forecast visualization
                forecast_df = pd.DataFrame({
                    'Date': forecast_result['dates'],
                    'Predicted_Quantity': forecast_result['predictions']
                })
                forecast_df['Date'] = pd.to_datetime(forecast_df['Date'])
                
                fig = px.line(forecast_df, x='Date', y='Predicted_Quantity',
                             title=f"Sales Forecast for {selected_product}")
                fig.update_xaxes(title="Date")
                fig.update_yaxes(title="Predicted Quantity")
                st.plotly_chart(fig, config={'displayModeBar': True, 'displaylogo': False})
                
                # Forecast summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Predicted Sales", 
                            f"{sum(forecast_result['predictions']):.0f}")
                with col2:
                    st.metric("Average Daily Sales", 
                            f"{np.mean(forecast_result['predictions']):.1f}")
                with col3:
                    st.metric("Confidence Level", 
                            f"{forecast_result['confidence_level']*100:.1f}%")

def show_data_input_page():
    """Display the data input page"""
    st.markdown("## 📝 Data Input Interface")
    
    tab1, tab2, tab3 = st.tabs(["Add Customer", "Add Product", "Add Order"])
    
    with tab1:
        st.markdown("### Add New Customer")
        
        with st.form("customer_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.text_input("Customer ID")
                age = st.number_input("Age", min_value=18, max_value=100)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])
                country = st.text_input("Country")
            
            with col2:
                signup_date = st.date_input("Signup Date")
                last_purchase_date = st.date_input("Last Purchase Date")
                cancellations_count = st.number_input("Cancellations Count", min_value=0)
                subscription_status = st.selectbox("Subscription Status", 
                                                 ["active", "inactive", "cancelled", "paused"])
            
            purchase_frequency = st.number_input("Purchase Frequency", min_value=0)
            ratings = st.slider("Ratings", min_value=1.0, max_value=5.0, value=4.0, step=0.1)
            
            if st.form_submit_button("Add Customer"):
                customer_data = {
                    'customer_id': customer_id,
                    'age': age,
                    'gender': gender,
                    'country': country,
                    'signup_date': signup_date.isoformat(),
                    'last_purchase_date': last_purchase_date.isoformat(),
                    'cancellations_count': cancellations_count,
                    'subscription_status': subscription_status,
                    'purchase_frequency': purchase_frequency,
                    'ratings': ratings
                }
                
                result = make_api_request("customers/", method="POST", data=customer_data)
                if result:
                    st.success("Customer added successfully!")
                else:
                    st.error("Failed to add customer")
    
    with tab2:
        st.markdown("### Add New Product")
        
        with st.form("product_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                product_id = st.text_input("Product ID")
                product_name = st.text_input("Product Name")
            
            with col2:
                category = st.text_input("Category")
                unit_price = st.number_input("Unit Price", min_value=0.0, step=0.01)
            
            if st.form_submit_button("Add Product"):
                product_data = {
                    'product_id': product_id,
                    'product_name': product_name,
                    'category': category,
                    'unit_price': unit_price
                }
                
                result = make_api_request("products/", method="POST", data=product_data)
                if result:
                    st.success("Product added successfully!")
                else:
                    st.error("Failed to add product")
    
    with tab3:
        st.markdown("### Add New Order")
        
        with st.form("order_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                order_id = st.text_input("Order ID")
                customer_id = st.text_input("Customer ID")
                product_id = st.text_input("Product ID")
            
            with col2:
                quantity = st.number_input("Quantity", min_value=1)
                order_date = st.date_input("Order Date")
            
            if st.form_submit_button("Add Order"):
                order_data = {
                    'order_id': order_id,
                    'customer_id': customer_id,
                    'product_id': product_id,
                    'quantity': quantity,
                    'order_date': order_date.isoformat()
                }
                
                result = make_api_request("orders/", method="POST", data=order_data)
                if result:
                    st.success("Order added successfully!")
                else:
                    st.error("Failed to add order")

def show_model_training_page():
    """Display the model training page"""
    st.markdown("## 🤖 Model Training Interface")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Churn Prediction Model")
        st.markdown("Train the machine learning model to predict customer churn.")
        
        if st.button("🚀 Train Churn Model", key="train_churn"):
            with st.spinner("Training churn prediction model..."):
                result = make_api_request("ml-training/train_churn_model/", method="POST")
                if result:
                    st.success("Churn model trained successfully!")
                    
                    # Display performance metrics
                    performance = result.get('performance', {})
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Accuracy", f"{performance.get('accuracy', 0):.3f}")
                    with col2:
                        st.metric("Precision", f"{performance.get('precision', 0):.3f}")
                    with col3:
                        st.metric("Recall", f"{performance.get('recall', 0):.3f}")
                    with col4:
                        st.metric("F1 Score", f"{performance.get('f1_score', 0):.3f}")
                else:
                    st.error("Failed to train churn model")
    
    with col2:
        st.markdown("### Sales Forecasting Model")
        st.markdown("Train the machine learning model to forecast sales.")
        
        if st.button("🚀 Train Sales Model", key="train_sales"):
            with st.spinner("Training sales forecasting model..."):
                result = make_api_request("ml-training/train_sales_model/", method="POST")
                if result:
                    st.success("Sales model trained successfully!")
                    
                    # Display performance metrics
                    performance = result.get('performance', {})
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("R² Score", f"{performance.get('r2_score', 0):.3f}")
                    with col2:
                        st.metric("MSE", f"{performance.get('mse', 0):.3f}")
                else:
                    st.error("Failed to train sales model")
    
    # Model performance history
    st.markdown("## 📊 Model Performance History")
    
    performance_data = make_api_request("model-performance/")
    if performance_data:
        perf_df = pd.DataFrame(performance_data)
        if not perf_df.empty:
            # Format for display
            display_df = perf_df[['model_type', 'model_version', 'accuracy', 
                                'precision', 'recall', 'f1_score', 'training_date']].copy()
            display_df['training_date'] = pd.to_datetime(display_df['training_date']).dt.strftime('%Y-%m-%d %H:%M')
            # Add serial number starting from 1
            display_df.insert(0, 'S.No.', range(1, len(display_df) + 1))
            display_df.columns = ['S.No.', 'Model Type', 'Version', 'Accuracy', 'Precision', 
                                'Recall', 'F1 Score', 'Training Date']
            
            st.dataframe(display_df.reset_index(drop=True), width='stretch', hide_index=True)
            
            # Performance visualization
            fig = px.line(perf_df, x='training_date', y='accuracy', 
                         color='model_type', title="Model Accuracy Over Time")
            fig.update_xaxes(title="Training Date")
            fig.update_yaxes(title="Accuracy")
            st.plotly_chart(fig, config={'displayModeBar': True, 'displaylogo': False})

if __name__ == "__main__":
    main()

