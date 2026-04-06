import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os

st.set_page_config(page_title="Indian Grocery Intelligence", layout="wide")

# 1. LOAD AND PROCESS DATA
@st.cache_data
def load_data():
    df = pd.read_csv("indian_retail/indian_retail_data.csv")
    # Clean data (ensure numeric)
    df['Price_INR'] = pd.to_numeric(df['Price_INR'], errors='coerce')
    # Target definition for MLEngine: Success = High Demand
    df['Success'] = (df['Demand_Level'] == 'High').astype(int)
    return df

df = load_data()

# 2. ML MODEL SETUP (Decision Engine)
@st.cache_resource
def train_model(df):
    ml_df = df.copy()
    
    # Encode categorical variables for model
    le_dict = {}
    cat_cols = ['Product_Name', 'Brand', 'City', 'Store_Type']
    for col in cat_cols:
        le = LabelEncoder()
        ml_df[col] = le.fit_transform(ml_df[col])
        le_dict[col] = le
        
    X = ml_df[['Product_Name', 'Brand', 'Price_INR', 'City', 'Store_Type']]
    y = ml_df['Success']
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    return clf, le_dict

clf, le_dict = train_model(df)

# Helper function to predict
def predict_success(product, brand, price, city, store_type):
    # Handle unseen labels gracefully by mapping to closest or most frequent
    def encode_safe(le, val):
        if val in le.classes_:
            return le.transform([val])[0]
        else:
            return 0  # fallback
            
    p_enc = encode_safe(le_dict['Product_Name'], product)
    b_enc = encode_safe(le_dict['Brand'], brand)
    c_enc = encode_safe(le_dict['City'], city)
    s_enc = encode_safe(le_dict['Store_Type'], store_type)
    
    features = np.array([[p_enc, b_enc, price, c_enc, s_enc]])
    prob = clf.predict_proba(features)[0][1] * 100
    return prob

# UI Dashboard
st.title("🛒 Retail Intelligence System (Indian Grocery)")
st.markdown("Enter hypothetical product parameters below to predict success probability, and explore regional insights!")

# Sidebar Filters & Inputs
st.sidebar.header("Input New Product Data")
in_product = st.sidebar.selectbox("Product Name", df['Product_Name'].unique())
in_brand = st.sidebar.selectbox("Brand/Company", df['Brand'].unique())
in_price = st.sidebar.number_input("Price (₹ INR)", min_value=10.0, max_value=1000.0, value=50.0)
in_qty_expected = st.sidebar.slider("Expected Quantity to Sell", 1, 100, 30)
in_city = st.sidebar.selectbox("Store Location (City)", df['City'].unique())
in_store_type = st.sidebar.selectbox("Store Type", df['Store_Type'].unique())

if st.sidebar.button("Analyze & Predict"):
    prob = predict_success(in_product, in_brand, in_price, in_city, in_store_type)
    st.sidebar.markdown(f"### 📈 Success Probability: **{prob:.1f}%**")
    if prob > 60:
        st.sidebar.success(f"High likelihood of success for {in_product} in {in_city}!")
    else:
        st.sidebar.warning(f"Consider adjusting pricing or brand. Lower success predicted.")

st.markdown("---")

# DASHBOARD FILTER (Bonus)
st.header("📊 Market Insights Dashboard")
selected_city = st.selectbox("Filter Analysis by City (Bonus)", ['All India'] + list(df['City'].unique()))

if selected_city == 'All India':
    filtered_df = df
else:
    filtered_df = df[df['City'] == selected_city]

col1, col2 = st.columns(2)

# Chart 1: Price vs Sales
with col1:
    st.subheader("Price vs Revenue (Sales)")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.scatterplot(data=filtered_df, x='Price_INR', y='Total_Sales', hue='Demand_Level', alpha=0.6, ax=ax1)
    ax1.set_title("How Pricing Affects Gross Sales")
    st.pyplot(fig1)

# Chart 2: Brand Comparison
with col2:
    st.subheader("Brand Performance")
    brand_sales = filtered_df.groupby('Brand')['Total_Sales'].sum().sort_values(ascending=False).reset_index()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=brand_sales.head(10), x='Total_Sales', y='Brand', palette='rocket', ax=ax2)
    ax2.set_title(f"Top Brands Revenue - {selected_city}")
    st.pyplot(fig2)

# Automated Recommendations (Bonus)
st.markdown("### 💡 AI Business Recommendations")

# Best Price Range
city_product_data = filtered_df[filtered_df['Product_Name'] == in_product]
if not city_product_data.empty and len(city_product_data) > 3:
    high_demand_prices = city_product_data[city_product_data['Demand_Level'] == 'High']['Price_INR']
    if not high_demand_prices.empty:
        rec_price_min = high_demand_prices.min()
        rec_price_max = high_demand_prices.max()
        st.info(f"**Recommended Price Range for {in_product} in {selected_city}:** ₹{rec_price_min} - ₹{rec_price_max}")
    else:
        st.info(f"**Recommended Price Range:** Not enough 'High Demand' data to suggest exact pricing. Try lower prices.")
else:
    st.info("Select a different product/city filter for price recommendations.")

# Best Brand per Location
best_brand_loc = filtered_df.groupby('Brand')['Total_Sales'].sum().idxmax()
st.success(f"**Best Performing Brand in {selected_city}:** {best_brand_loc}")

# Underperforming
worst_product = filtered_df.groupby('Product_Name')['Total_Sales'].sum().idxmin()
st.warning(f"**Underperforming Product Risk in {selected_city}:** {worst_product} has the lowest total revenue currently.")
