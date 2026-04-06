import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_realistic_data(num_rows=1000):
    products_db = {
        'Groceries': ['Rice', 'Wheat Flour', 'Cooking Oil', 'Sugar', 'Dal'],
        'Personal Care': ['Soap', 'Shampoo', 'Toothpaste', 'Hair Oil'],
        'Household': ['Detergent', 'Floor Cleaner', 'Dishwash Bar']
    }
    
    brands = {
        'Premium': ['Tata', 'Fortune', 'Aashirvaad', 'HUL', 'P&G'],
        'Standard': ['Patanjali', 'Reliance', 'Dabur'],
        'Budget': ['Local Brand', 'Store Brand']
    }
    
    cities = ['Mumbai', 'Pune', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Ahmedabad']
    store_types = ['Kirana Store', 'Supermarket', 'Mall']
    area_types = ['Urban', 'Semi-Urban', 'Rural']
    
    data = []
    
    start_date = datetime.now() - timedelta(days=365)
    
    for _ in range(num_rows):
        category = random.choice(list(products_db.keys()))
        product = random.choice(products_db[category])
        
        # Decide Area Type
        area = random.choices(area_types, weights=[0.5, 0.3, 0.2])[0]
        city = random.choice(cities)
        
        # Decide Store Type based on Area
        if area == 'Urban':
            store_type = random.choices(store_types, weights=[0.2, 0.5, 0.3])[0]
        elif area == 'Semi-Urban':
            store_type = random.choices(store_types, weights=[0.5, 0.4, 0.1])[0]
        else: # Rural
            store_type = random.choices(store_types, weights=[0.9, 0.1, 0.0])[0]
            
        # Decide Brand based on Area (Premium in Urban, Local in Rural)
        if area == 'Urban':
            brand_tier = random.choices(list(brands.keys()), weights=[0.6, 0.3, 0.1])[0]
        elif area == 'Semi-Urban':
            brand_tier = random.choices(list(brands.keys()), weights=[0.2, 0.6, 0.2])[0]
        else:
            brand_tier = random.choices(list(brands.keys()), weights=[0.05, 0.15, 0.8])[0]
            
        brand = random.choice(brands[brand_tier])
        
        # Base Price formulation
        if category == 'Groceries':
            base_price = random.uniform(40, 200)
        elif category == 'Personal Care':
            base_price = random.uniform(20, 300)
        else:
            base_price = random.uniform(50, 500)
            
        # Brand Price Modifier
        if brand_tier == 'Premium':
            price = base_price * random.uniform(1.2, 1.5)
        elif brand_tier == 'Standard':
            price = base_price * random.uniform(0.9, 1.1)
        else:
            price = base_price * random.uniform(0.6, 0.8)
            
        price_inr = round(price, 2)
        
        # Competitor Price
        competitor_price = round(price_inr * random.uniform(0.9, 1.1), 2)
        
        # Discount
        discount_pct = round(random.uniform(0, 30), 2)
        final_ticket = price_inr * (1 - discount_pct/100)
        
        # Quantity Logic (Lower price / higher discount -> more quantity)
        base_qty = random.randint(10, 50)
        if final_ticket < 50:
            qty_multiplier = 1.8
        elif final_ticket > 200:
            qty_multiplier = 0.5
        else:
            qty_multiplier = 1.0
            
        if discount_pct > 20:
            qty_multiplier *= 1.3
            
        quantity_sold = int(base_qty * qty_multiplier)
        quantity_sold = max(1, min(100, quantity_sold)) # Cap between 1 and 100
        
        total_sales = round(price_inr * quantity_sold, 2)
        
        # Demand Level
        if quantity_sold > 60:
            demand = 'High'
        elif quantity_sold > 30:
            demand = 'Medium'
        else:
            demand = 'Low'
            
        # Profit Margin (Premium higher margin, high discount lowers margin)
        base_margin = random.uniform(10, 25)
        if brand_tier == 'Premium': base_margin += 5
        if discount_pct > 15: base_margin -= 5
        profit_margin = round(max(5.0, min(30.0, base_margin)), 2)
        
        # Date
        random_days = random.randint(0, 365)
        date_sold = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
        
        # Rating
        rating = round(random.uniform(3.0, 5.0) if brand_tier == 'Premium' else random.uniform(1.5, 4.5), 1)

        data.append([
            product, category, brand, price_inr, quantity_sold, total_sales,
            store_type, city, area, date_sold, discount_pct, rating,
            competitor_price, demand, profit_margin
        ])
        
    df = pd.DataFrame(data, columns=[
        'Product_Name', 'Category', 'Brand', 'Price_INR', 'Quantity_Sold', 'Total_Sales',
        'Store_Type', 'City', 'Area_Type', 'Date', 'Discount_Percentage', 'Customer_Rating',
        'Competitor_Price', 'Demand_Level', 'Profit_Margin'
    ])
    
    # Save slightly nested so it runs from `d:\analysisproject`
    os.makedirs('indian_retail', exist_ok=True)
    df.to_csv("indian_retail/indian_retail_data.csv", index=False)
    print(f"Dataset generated successfully! Shape: {df.shape}")

if __name__ == "__main__":
    generate_realistic_data(1000)
