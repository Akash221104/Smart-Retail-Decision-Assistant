import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as plt_sns
import os

def load_and_clean_data(filepath="Superstore.csv"):
    try:
        df = pd.read_csv(filepath, encoding='latin1')
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

    # Handle missing values
    # For example, Postal Code might have missing values.
    # In some datasets it's there, in global superstore 'Postal Code' might be heavily missing. 
    if 'Postal Code' in df.columns:
        df['Postal Code'] = df['Postal Code'].fillna('Unknown')
    
    # Drop rows where critical columns like Sales, Quantity, Profit are missing
    df.dropna(subset=['Sales', 'Quantity', 'Profit', 'Order Date'], inplace=True)
    
    # Convert date columns
    # We use format='mixed' to handle potential inconsistencies or let pandas infer
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    
    # Create new features
    # Price per item = Sales / Quantity (approximate since there might be discounts)
    df['Price per Item'] = df['Sales'] / df['Quantity']
    df['Order Year'] = df['Order Date'].dt.year
    df['Order Month'] = df['Order Date'].dt.to_period('M')  # for monthly aggregation
    
    # Standardize column sizes
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
    df['Profit'] = pd.to_numeric(df['Profit'], errors='coerce')

    return df

def perform_analysis(df):
    insights = {}
    
    # 1. Price vs Quantity Correlation
    price_qty_corr = df['Price per Item'].corr(df['Quantity'])
    insights['price_qty_correlation'] = price_qty_corr
    
    # 2. Top Performing Products
    top_products = df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)
    insights['top_products'] = top_products
    
    # 3. Top Categories
    top_categories = df.groupby('Category')['Sales'].sum().sort_values(ascending=False)
    insights['top_categories'] = top_categories
    
    # 4. Region-wise and State-wise Sales
    regional_sales = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
    insights['region_sales'] = regional_sales
    
    state_sales = df.groupby('State')['Sales'].sum().sort_values(ascending=False).head(10)
    insights['state_sales'] = state_sales
    
    # 5. Monthly Trend
    monthly_sales = df.groupby('Order Month')['Sales'].sum()
    insights['monthly_sales'] = monthly_sales
    
    # 6. Underperforming Regions (Lowest Sales or Negative Profit)
    region_profit = df.groupby('Region')['Profit'].sum().sort_values(ascending=True)
    insights['underperforming_regions_by_profit'] = region_profit.head(5)
    
    # 7. Underperforming Products (Lowest Profit)
    bottom_products = df.groupby('Product Name')['Profit'].sum().sort_values(ascending=True).head(10)
    insights['underperforming_products_by_profit'] = bottom_products
    
    return insights

def generate_visualizations(df, insights, output_dir='plots'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt_sns.set_theme(style="whitegrid")
    
    # 1. Sales vs Category
    plt.figure(figsize=(10, 6))
    cat_sales = insights['top_categories'].reset_index()
    plt_sns.barplot(data=cat_sales, x='Category', y='Sales', palette='Blues_r')
    plt.title('Total Sales by Category')
    plt.ylabel('Sales ($)')
    plt.savefig(f'{output_dir}/sales_vs_category.png', bbox_inches='tight')
    plt.close()
    
    # 2. Region-wise Revenue
    plt.figure(figsize=(12, 6))
    reg_sales = insights['region_sales'].reset_index()
    plt_sns.barplot(data=reg_sales, x='Sales', y='Region', palette='viridis')
    plt.title('Total Revenue by Region')
    plt.xlabel('Sales ($)')
    plt.savefig(f'{output_dir}/region_wise_revenue.png', bbox_inches='tight')
    plt.close()
    
    # 3. Monthly Sales Trend
    plt.figure(figsize=(14, 6))
    month_sales = insights['monthly_sales'].reset_index()
    month_sales['Order Month'] = month_sales['Order Month'].astype(str)
    # just plotting as a simple lineplot over strings might be messy, let's use actual datetime for plotting
    trend_df = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    trend_df['Order Date'] = trend_df['Order Date'].dt.to_timestamp()
    plt_sns.lineplot(data=trend_df, x='Order Date', y='Sales', marker='o')
    plt.title('Monthly Sales Trend')
    plt.xlabel('Date')
    plt.ylabel('Total Sales ($)')
    plt.xticks(rotation=45)
    plt.savefig(f'{output_dir}/monthly_sales_trend.png', bbox_inches='tight')
    plt.close()
    
    # 4. Top 10 Products
    plt.figure(figsize=(10, 8))
    top_prod = insights['top_products'].reset_index()
    plt_sns.barplot(data=top_prod, x='Sales', y='Product Name', palette='magma')
    plt.title('Top 10 Products by Sales')
    plt.xlabel('Sales ($)')
    plt.savefig(f'{output_dir}/top_10_products.png', bbox_inches='tight')
    plt.close()

def main():
    print("Loading data...")
    df = load_and_clean_data()
    if df is None:
        return
    print(f"Data Loaded Successfully. Shape: {df.shape}")
    
    print("Performing analysis...")
    insights = perform_analysis(df)
    
    print("Generating visualizations...")
    generate_visualizations(df, insights)
    
    print("\n--- KEY BUSINESS INSIGHTS ---")
    print(f"1. Correlation between Price per item and Quantity: {insights['price_qty_correlation']:.4f}")
    print("\n2. Top 3 Categories by Sales:")
    print(insights['top_categories'].head(3))
    
    print("\n3. Best Region by Sales:")
    print(insights['region_sales'].head(1))
    
    print("\n4. Top States by Sales:")
    print(insights['state_sales'].head(3))
    
    print("\n5. Underperforming Region by Profit:")
    print(insights['underperforming_regions_by_profit'].head(1))
    
    print("\n6. Worst Performing Products (by Profit):")
    print(insights['underperforming_products_by_profit'].head(3))
    print("--------------------------------\n")
    print("Visualizations saved to 'plots/' directory.")

if __name__ == "__main__":
    main()
