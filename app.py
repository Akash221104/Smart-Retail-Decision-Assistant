import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Superstore Sales Dashboard", layout="wide")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Superstore.csv", encoding='latin1')
        df.dropna(subset=['Sales', 'Quantity', 'Profit', 'Order Date'], inplace=True)
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        df['Price per Item'] = df['Sales'] / df['Quantity']
        df['Order Year'] = df['Order Date'].dt.year
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}. Please ensure data is downloaded.")
        return pd.DataFrame()

st.title("🛒 Retail Pricing & Store Performance Dashboard")
st.markdown("Analyze Superstore Sales dataset to derive pricing and regional insights.")

df = load_data()

if df.empty:
    st.warning("No data found. Please run `python fetch_data.py` first.")
else:
    # Key Metrics
    total_sales = df['Sales'].sum()
    total_profit = df['Profit'].sum()
    total_orders = df['Order ID'].nunique()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Sales", f"${total_sales:,.2f}")
    col2.metric("Total Profit", f"${total_profit:,.2f}")
    col3.metric("Total Orders", f"{total_orders:,}")
    
    st.markdown("---")
    
    # Visualizations
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Sales by Category")
        category_sales = df.groupby('Category')['Sales'].sum().sort_values(ascending=False).reset_index()
        fig, ax = plt.subplots(figsize=(8,4))
        sns.barplot(data=category_sales, x='Category', y='Sales', palette='Blues_r', ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        
    with col_chart2:
        st.subheader("Profit by Region (Underperforming check)")
        region_profit = df.groupby('Region')['Profit'].sum().sort_values().reset_index()
        fig, ax = plt.subplots(figsize=(8,4))
        sns.barplot(data=region_profit, x='Profit', y='Region', palette='coolwarm_r', ax=ax)
        st.pyplot(fig)

    st.subheader("Monthly Sales Trend")
    trend_df = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    trend_df['Order Date'] = trend_df['Order Date'].dt.to_timestamp()
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.lineplot(data=trend_df, x='Order Date', y='Sales', marker='o', ax=ax)
    st.pyplot(fig)
    
    st.markdown("---")
    st.subheader("Top 10 Performing Products")
    top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
    st.dataframe(top_products, use_container_width=True)

    st.subheader("Top 10 Underperforming Products (by Profit)")
    bottom_products = df.groupby('Product Name')['Profit'].sum().sort_values(ascending=True).head(10).reset_index()
    st.dataframe(bottom_products, use_container_width=True)
