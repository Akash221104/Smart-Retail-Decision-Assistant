import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Smart Retail Assistant", layout="centered", page_icon="🛍️", initial_sidebar_state="expanded")

# --- DATA PROCESSING ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("indian_retail/indian_retail_data.csv")
    except FileNotFoundError:
        return pd.DataFrame(), {}, {}, {}, {}

    df['Price_INR'] = pd.to_numeric(df['Price_INR'], errors='coerce')
    high_demand_df = df[df['Demand_Level'].isin(['High', 'Medium'])]
    
    price_ranges = {}
    for prod in df['Product_Name'].unique():
        prod_data = high_demand_df[high_demand_df['Product_Name'] == prod]['Price_INR']
        if not prod_data.empty:
            price_ranges[prod] = (round(prod_data.quantile(0.25)), round(prod_data.quantile(0.75)))
        else:
            price_ranges[prod] = (50, 150)
            
    city_brand_revenue = df.groupby(['City', 'Brand'])['Total_Sales'].sum().reset_index()
    idx = city_brand_revenue.groupby('City')['Total_Sales'].idxmax()
    best_brands_city = city_brand_revenue.loc[idx].set_index('City')['Brand'].to_dict()
    
    city_sales = df.groupby('City')['Total_Sales'].sum()
    brand_strength_dict = {}
    brand_sales_dict = {}
    for c in df['City'].unique():
        brand_strength_dict[c] = {}
        brand_sales_dict[c] = {}
        c_data = df[df['City'] == c]
        for b in df['Brand'].unique():
            b_sales = c_data[c_data['Brand'] == b]['Total_Sales'].sum()
            brand_sales_dict[c][b] = b_sales
            brand_strength_dict[c][b] = b_sales / city_sales[c] if city_sales[c] > 0 else 0

    return df, price_ranges, best_brands_city, brand_strength_dict, brand_sales_dict

df, price_ranges, best_brands_city, brand_strength_dict, brand_sales_dict = load_data()

# --- LOGIC ENGINE ---
def calculate_success(product, brand, price, city, store_type):
    score = 0
    reasons = []
    risks = []
    
    if df.empty: return 0, "Error", "gray", [], [], {}, "", "", "", ""

    p_min, p_max = price_ranges.get(product, (50, 150))
    optimal_price = round((p_min + p_max) / 2) 
    
    if p_min <= price <= p_max:
        score += 30
        reasons.append(f"Optimal Price: ₹{price} is exactly in the market sweet spot.")
    elif price < p_min:
        score += 20
        reasons.append(f"Competitive Price: Guaranteed sales, but sacrifices some profit.")
    else:
        score += 0
        reasons.append(f"Premium Price: ₹{price} is higher than the usual market threshold.")
        risks.append(f"Price exceeds optimal range (₹{p_min}-₹{p_max}). Volumes may severely drop.")
        
    b_strength = brand_strength_dict.get(city, {}).get(brand, 0)
    if b_strength > 0.15:
        score += 30
        reasons.append(f"Dominant Trust: '{brand}' is heavily preferred in {city}.")
    elif b_strength > 0.05:
        score += 15
        reasons.append(f"Steady Power: '{brand}' holds average market traction locally.")
    else:
        score += 5
        reasons.append(f"Weak Brand: '{brand}' holds minimal local market share.")
        risks.append(f"Consumers in this region heavily prefer alternative brands over '{brand}'.")

    prod_demand = df[df['Product_Name'] == product]['Demand_Level'].value_counts(normalize=True)
    high_demand_ratio = prod_demand.get('High', 0)
    if high_demand_ratio > 0.35:
        score += 20
        reasons.append(f"High Demand: Essential item guaranteeing foot traffic.")
        demand_display = "High 🔥"
    elif high_demand_ratio > 0.15:
        score += 10
        reasons.append(f"Moderate Need: Standard good with balanced daily movement.")
        demand_display = "Medium ⚠️"
    else:
        score += 0
        reasons.append(f"Low Frequency: Not a frequent buy. Slower moving inventory.")
        demand_display = "Low ❌"
        
    store_sales = df[df['Product_Name'] == product].groupby('Store_Type')['Total_Sales'].sum()
    best_store_type = store_sales.idxmax() if not store_sales.empty else "Kirana Store"
    if store_type == best_store_type:
        score += 20
        reasons.append(f"Perfect Synergy: Naturally belongs inside a {store_type}.")
    else:
        score += 5
        reasons.append(f"Mismatched Setup: Better suited for {best_store_type} layouts.")
        risks.append("Product struggles natively in your declared store type.")

    if score >= 70:
        decision = "Good to Sell"
        alert_type = "success"
    elif score >= 40:
        decision = "Average"
        alert_type = "warning"
    else:
        decision = "Risky"
        alert_type = "error"
        
    recs = []
    recs.append(f"Aim specifically for ₹{p_min} - ₹{p_max}.")
    best_c_brand = best_brands_city.get(city)
    if brand != best_c_brand: recs.append(f"Consider stocking '{best_c_brand}' to capture local dominance.")
    if score < 60: recs.append("Try pairing heavily discounted items right next to this product.")
    else: recs.append("Ensure prominently displayed position at eye-level.")

    prod_city_df = df[(df['Product_Name'] == product) & (df['City'] == city)]
    fallback_df = df[df['Product_Name'] == product] if prod_city_df.empty else prod_city_df
    est_monthly_qty = fallback_df['Quantity_Sold'].mean() if not fallback_df.empty else 30
    inventory_sugg = f"Forecasted Requirement: {max(1, int((est_monthly_qty / 4) * 0.8))}–{int((est_monthly_qty / 4) * 1.5)} units/week"
    
    b_sales = brand_sales_dict.get(city, {}).get(brand, 1)
    best_b_sales = brand_sales_dict.get(city, {}).get(best_c_brand, 1)
    if brand != best_c_brand and b_sales > 0:
        comp_comp = f"Brand '{best_c_brand}' generates {round(((best_b_sales - b_sales) / b_sales) * 100)}% more localized revenue than '{brand}' here."
    else:
        comp_comp = f"Brand '{brand}' is the #1 Top Leading Brand locally."

    stats = {
        "score": score, "decision": decision, "alert_type": alert_type, "demand": demand_display,
        "inventory": inventory_sugg, "comp": comp_comp, "p_min": p_min, "p_max": p_max
    }
    return score, decision, alert_type, reasons, recs, risks, stats

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.title("🛍️ Smart Retail")
    page = st.radio(
        "Navigation Menu:",
        ["Dashboard Home", "Decision Assistant", "Market Research"]
    )
    st.markdown("---")
    st.caption("Retail Engine v2.0")

if df.empty:
    st.error("Critical Error: Database is offline. `indian_retail_data.csv` missing.")
    st.stop()

# --- PAGE 1: HOME ---
if page == "Dashboard Home":
    st.title("👋 Welcome to Retail Intelligence")
    st.write("A clean and simple assistant to grade your grocery plans based on localized shopping trends.")
    
    st.subheader("System Overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Products Tracked", df["Product_Name"].nunique())
    c2.metric("Cities Monitored", df["City"].nunique())
    c3.metric("Brands Indexed", df["Brand"].nunique())
    
    st.divider()
    st.info("👈 Please select **Decision Assistant** from the sidebar to evaluate a product.")
    
# --- PAGE 2: DECISION ASSISTANT (CLEAN UI) ---
elif page == "Decision Assistant":
    st.title("🛍️ Decision Assistant")
    st.write("Optimize your inventory choices effortlessly.")

    # Input Section Container
    with st.container(border=True):
        st.subheader("Input Details")
        c1, c2 = st.columns(2)
        with c1:
            prod_val = st.selectbox("Product", df['Product_Name'].unique())
            brand_val = st.selectbox("Brand Affiliation", df['Brand'].unique())
        with c2:
            city_val = st.selectbox("Market Location", df['City'].unique())
            store_val = st.selectbox("Store Format", ["Kirana Store", "Supermarket", "Mall"])
        
        price_val = st.number_input("Target Price (₹)", min_value=5.0, value=75.0, step=5.0)
        check = st.button("👉 Evaluate Plan", type="primary", use_container_width=True)

    # Output Section
    if check:
        st.divider()
        st.subheader("Executive Summary")
        sc, dcs, alert_type, reasons, recs, risks, st_d = calculate_success(prod_val, brand_val, price_val, city_val, store_val)
        
        # Consistent Native Output Box
        if alert_type == "success":
            st.success(f"### {dcs}\n**Success Probability: {sc}%**")
        elif alert_type == "warning":
            st.warning(f"### {dcs}\n**Success Probability: {sc}%**")
        else:
            st.error(f"### {dcs}\n**Success Probability: {sc}%**")
            
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Score", f"{sc} / 100")
        col_m2.metric("Market Demand", st_d["demand"])
        col_m3.metric("Competitive Threat", "High" if len(risks) > 0 else "Low")
        
        # Details & Recs
        d1, d2 = st.columns(2)
        with d1:
            with st.container(border=True):
                st.markdown("#### 🔍 Algorithm Logic")
                for r in reasons: st.write(f"- {r}")
            
        with d2:
            with st.container(border=True):
                st.markdown("#### 💡 Next Steps")
                for rc in recs: st.write(f"- {rc}")

        st.write(" ")
        
        # Extras
        w1, w2 = st.columns(2)
        with w1:
            with st.container(border=True):
                st.markdown("#### 📋 General Assessment")
                st.write(f"📦 {st_d['inventory']}")
                st.write(f"📈 {st_d['comp']}")
        with w2:
            with st.container(border=True):
                st.markdown("#### 🚨 Risk Flags")
                if risks:
                    for rsk in risks: st.write(f"- {rsk}")
                else:
                    st.write("- ✨ Zero immediate risk flags detected.")

# --- PAGE 3: MARKET RESEARCH (GRAPHS) ---
elif page == "Market Research":
    st.title("📊 Indian Retail Deep Dive")
    st.write("Explore raw competitor data separated from the main assistant.")
    
    with st.container(border=True):
        rc1, rc2 = st.columns(2)
        mr_city = rc1.selectbox("Filter by City:", ["All India"] + list(df['City'].unique()))
        mr_cat = rc2.selectbox("Filter by Category:", ["All Categories"] + list(df['Category'].unique()))
    
    temp_df = df
    if mr_city != "All India": temp_df = temp_df[temp_df['City'] == mr_city]
    if mr_cat != "All Categories": temp_df = temp_df[temp_df['Category'] == mr_cat]
    
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Top Brands by Revenue")
        if not temp_df.empty:
            b_rev = temp_df.groupby("Brand")['Total_Sales'].sum().sort_values(ascending=False).head(5).reset_index()
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.barplot(data=b_rev, y='Brand', x='Total_Sales', palette='Blues_d', ax=ax)
            ax.set_xlabel("Gross Sales (₹)")
            ax.set_ylabel("")
            sns.despine()
            st.pyplot(fig)
        else:
            st.warning("Insufficient data context.")
            
    with colB:
        st.subheader("Price Distributions")
        if not temp_df.empty:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            sns.histplot(temp_df['Price_INR'], kde=True, color='#2c3e50', ax=ax2)
            ax2.set_xlabel("Market Shelf Prices (₹)")
            sns.despine()
            st.pyplot(fig2)
