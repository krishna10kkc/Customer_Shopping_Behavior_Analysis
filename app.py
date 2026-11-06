import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Customer Shopping Behavior Analysis",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom Styling
# ---------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .metric-card-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-card-val {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-card-sub {
        font-size: 0.8rem;
        color: #10B981;
        font-weight: 500;
        margin-top: 4px;
    }
    .sql-box {
        background-color: #0f172a;
        color: #38bdf8;
        padding: 14px;
        border-radius: 8px;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 0.9rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# US State Abbreviations for Choropleth Map
# ---------------------------------------------------------
US_STATE_ABBR = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# ---------------------------------------------------------
# Data Loading & Preprocessing
# ---------------------------------------------------------
@st.cache_data
def load_data():
    csv_candidates = [
        "customer_shopping_behavior.csv",
        os.path.join(os.path.dirname(__file__), "customer_shopping_behavior.csv"),
        os.path.join(os.path.dirname(__file__), "Dataset", "customer_shopping_behavior.csv")
    ]
    file_path = None
    for path in csv_candidates:
        if os.path.exists(path):
            file_path = path
            break
            
    if not file_path:
        st.error("Error: 'customer_shopping_behavior.csv' file not found. Please ensure it is present in the repository.")
        st.stop()
        
    df = pd.read_csv(file_path)
    
    # Fill missing Review Rating with Category median
    if 'Review Rating' in df.columns and df['Review Rating'].isnull().any():
        df['Review Rating'] = df.groupby('Category')['Review Rating'].transform(lambda x: x.fillna(x.median()))
        
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
    if 'purchase_amount_(usd)' in df.columns:
        df = df.rename(columns={'purchase_amount_(usd)': 'purchase_amount'})
        
    # Age Group Categorization
    labels = ['Young Adult', 'Adult', 'Middle-aged', 'Senior']
    df['age_group'] = pd.qcut(df['age'], q=4, labels=labels)
    
    # Frequency mapping to days
    freq_map = {
        'Fortnightly': 14,
        'Weekly': 7,
        'Monthly': 30,
        'Quarterly': 90,
        'Bi-Weekly': 14,
        'Annually': 365,
        'Every 3 Months': 90
    }
    df['purchase_frequency_days'] = df['frequency_of_purchases'].map(freq_map)
    
    # Customer Segmentation
    def assign_segment(purchases):
        if purchases == 1:
            return 'New'
        elif 2 <= purchases <= 10:
            return 'Returning'
        else:
            return 'Loyal'
            
    df['customer_segment'] = df['previous_purchases'].apply(assign_segment)
    
    # Map state codes for map
    df['state_code'] = df['location'].map(US_STATE_ABBR)
    
    return df

df = load_data()

# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3081/3081559.png", width=65)
st.sidebar.markdown("## 🔍 **Filter Dashboard**")

# Category Filter
all_categories = sorted(df['category'].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect("Category", all_categories, default=all_categories)

# Gender Filter
all_genders = sorted(df['gender'].dropna().unique().tolist())
selected_genders = st.sidebar.multiselect("Gender", all_genders, default=all_genders)

# Season Filter
all_seasons = sorted(df['season'].dropna().unique().tolist())
selected_seasons = st.sidebar.multiselect("Season", all_seasons, default=all_seasons)

# Age Group Filter
all_age_groups = ['Young Adult', 'Adult', 'Middle-aged', 'Senior']
selected_age_groups = st.sidebar.multiselect("Age Group", all_age_groups, default=all_age_groups)

# Subscription Status
all_sub_statuses = sorted(df['subscription_status'].dropna().unique().tolist())
selected_sub_statuses = st.sidebar.multiselect("Subscription Status", all_sub_statuses, default=all_sub_statuses)

# Shipping Type Filter
all_shipping = sorted(df['shipping_type'].dropna().unique().tolist())
selected_shipping = st.sidebar.multiselect("Shipping Type", all_shipping, default=all_shipping)

# Filter Data
filtered_df = df[
    (df['category'].isin(selected_categories)) &
    (df['gender'].isin(selected_genders)) &
    (df['season'].isin(selected_seasons)) &
    (df['age_group'].isin(selected_age_groups)) &
    (df['subscription_status'].isin(selected_sub_statuses)) &
    (df['shipping_type'].isin(selected_shipping))
]

if filtered_df.empty:
    st.warning("⚠️ No data matches your filter criteria. Please adjust sidebar selections.")
    st.stop()

# Sidebar Project & Author Info
st.sidebar.markdown("---")
st.sidebar.markdown("### 👨‍💻 **Project Author**")
st.sidebar.markdown("**Krishna Kumar Chaurasia**")
st.sidebar.markdown("💼 [LinkedIn Profile](https://linkedin.com/in/krishna-kumar-chaurasia-3154a132b)")
st.sidebar.markdown("🐙 [GitHub Repository](https://github.com/krishna10kkc/Customer_Shopping_Behavior_Analysis)")
st.sidebar.caption("Data Analytics Portfolio Project")

# ---------------------------------------------------------
# Header & Project Overview
# ---------------------------------------------------------
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown('<div class="main-header">🛍️ Customer Shopping Behavior Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">End-to-end Data Analytics dashboard analyzing customer demographics, purchase drivers, loyalty segmentation, and promotional effectiveness.</div>', unsafe_allow_html=True)

with col_h2:
    st.markdown("""
        <div style="text-align: right; padding-top: 10px;">
            <span style="background-color: #E0E7FF; color: #4338CA; padding: 6px 12px; border-radius: 20px; font-weight: 600; font-size: 0.85rem;">
                🚀 Live App
            </span>
        </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Top KPI Metric Cards
# ---------------------------------------------------------
total_revenue = filtered_df['purchase_amount'].sum()
total_customers = len(filtered_df)
avg_spend = filtered_df['purchase_amount'].mean()
avg_rating = filtered_df['review_rating'].mean()
sub_rate = (filtered_df['subscription_status'] == 'Yes').mean() * 100
discount_rate = (filtered_df['discount_applied'] == 'Yes').mean() * 100

kpi_cols = st.columns(6)
metrics = [
    ("Total Revenue", f"${total_revenue:,.0f}", f"{total_customers:,} orders"),
    ("Total Customers", f"{total_customers:,}", "Analyzed Profiles"),
    ("Avg Order Value", f"${avg_spend:.2f}", "Per Transaction"),
    ("Avg Review Rating", f"{avg_rating:.2f} ⭐", "Out of 5.0"),
    ("Subscribed Users", f"{sub_rate:.1f}%", f"{(filtered_df['subscription_status']=='Yes').sum()} Subscribers"),
    ("Discount Usage", f"{discount_rate:.1f}%", f"{(filtered_df['discount_applied']=='Yes').sum()} Promo Orders")
]

for col, (title, val, sub) in zip(kpi_cols, metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-card-title">{title}</div>
            <div class="metric-card-val">{val}</div>
            <div class="metric-card-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Tabs
# ---------------------------------------------------------
tab_overview, tab_segmentation, tab_discounts, tab_sql, tab_data = st.tabs([
    "📊 Executive Dashboard",
    "👥 Customer Segmentation",
    "🏷️ Discounts & Shipping",
    "⚡ SQL Business Questions (10)",
    "📁 Raw Data & Export"
])

# =========================================================
# TAB 1: EXECUTIVE DASHBOARD
# =========================================================
with tab_overview:
    # Row 1: Category Revenue & Gender Breakdown
    row1_c1, row1_c2 = st.columns([3, 2])
    
    with row1_c1:
        cat_gender = filtered_df.groupby(['category', 'gender'])['purchase_amount'].sum().reset_index()
        fig_cat_gender = px.bar(
            cat_gender,
            x='category',
            y='purchase_amount',
            color='gender',
            barmode='group',
            title='<b>Revenue by Category & Gender</b>',
            labels={'purchase_amount': 'Total Revenue ($)', 'category': 'Product Category', 'gender': 'Gender'},
            color_discrete_sequence=['#3B82F6', '#EC4899'],
            text_auto='$,.0f'
        )
        fig_cat_gender.update_layout(template='plotly_white', hovermode='x unified', margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_cat_gender, use_container_width=True)
        
    with row1_c2:
        cat_share = filtered_df.groupby('category')['purchase_amount'].sum().reset_index()
        fig_cat_donut = px.pie(
            cat_share,
            names='category',
            values='purchase_amount',
            hole=0.45,
            title='<b>Category Revenue Share</b>',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_cat_donut.update_traces(textposition='inside', textinfo='percent+label')
        fig_cat_donut.update_layout(template='plotly_white', margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_cat_donut, use_container_width=True)
        
    # Row 2: US Geographic Distribution & Age Groups
    row2_c1, row2_c2 = st.columns([3, 2])
    
    with row2_c1:
        state_data = filtered_df.groupby('state_code').agg(
            revenue=('purchase_amount', 'sum'),
            orders=('customer_id', 'count')
        ).reset_index()
        
        fig_map = px.choropleth(
            state_data,
            locations='state_code',
            locationmode="USA-states",
            color='revenue',
            scope="usa",
            title='<b>Geographic Revenue Distribution across US States</b>',
            color_continuous_scale="Blues",
            labels={'revenue': 'Total Sales ($)', 'state_code': 'State'}
        )
        fig_map.update_layout(template='plotly_white', margin=dict(t=40, b=10, l=10, r=10))
        st.plotly_chart(fig_map, use_container_width=True)
        
    with row2_c2:
        age_rev = filtered_df.groupby('age_group', observed=False)['purchase_amount'].sum().reset_index()
        fig_age = px.bar(
            age_rev,
            x='age_group',
            y='purchase_amount',
            color='age_group',
            title='<b>Revenue Contribution by Age Group</b>',
            labels={'purchase_amount': 'Total Revenue ($)', 'age_group': 'Age Group'},
            color_discrete_sequence=['#6366F1', '#8B5CF6', '#A855F7', '#D946EF'],
            text_auto='$,.0f'
        )
        fig_age.update_layout(template='plotly_white', showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_age, use_container_width=True)
        
    # Row 3: Seasonal Trends & Top 10 Items
    row3_c1, row3_c2 = st.columns([2, 3])
    
    with row3_c1:
        season_sales = filtered_df.groupby('season')['purchase_amount'].agg(['sum', 'count']).reset_index()
        season_sales.columns = ['season', 'revenue', 'order_count']
        fig_season = px.bar(
            season_sales,
            x='season',
            y='revenue',
            color='season',
            title='<b>Sales by Season</b>',
            labels={'revenue': 'Total Sales ($)', 'season': 'Season'},
            color_discrete_sequence=['#10B981', '#F59E0B', '#EF4444', '#3B82F6'],
            text_auto='$,.0f'
        )
        fig_season.update_layout(template='plotly_white', showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_season, use_container_width=True)
        
    with row3_c2:
        top_items = filtered_df.groupby('item_purchased')['purchase_amount'].sum().nlargest(10).reset_index()
        fig_items = px.bar(
            top_items,
            x='purchase_amount',
            y='item_purchased',
            orientation='h',
            title='<b>Top 10 Selling Products Overall</b>',
            labels={'purchase_amount': 'Total Sales ($)', 'item_purchased': 'Product Name'},
            color='purchase_amount',
            color_continuous_scale='Tealgrn',
            text_auto='$,.0f'
        )
        fig_items.update_layout(template='plotly_white', yaxis=dict(autorange="reversed"), margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_items, use_container_width=True)

# =========================================================
# TAB 2: CUSTOMER SEGMENTATION
# =========================================================
with tab_segmentation:
    st.markdown("### 👥 **Customer Loyalty Segmentation & Subscription Analysis**")
    st.markdown("Customers are segmented by transaction history: **New** (1 purchase), **Returning** (2-10 purchases), and **Loyal** (>10 purchases).")
    
    seg_c1, seg_c2, seg_c3 = st.columns(3)
    
    seg_summary = filtered_df.groupby('customer_segment').agg(
        total_customers=('customer_id', 'count'),
        total_revenue=('purchase_amount', 'sum'),
        avg_spend=('purchase_amount', 'mean'),
        avg_previous=('previous_purchases', 'mean')
    ).reindex(['New', 'Returning', 'Loyal']).reset_index()
    
    with seg_c1:
        fig_seg_count = px.pie(
            seg_summary,
            names='customer_segment',
            values='total_customers',
            title='<b>Customer Distribution by Segment</b>',
            color='customer_segment',
            color_discrete_map={'New': '#94A3B8', 'Returning': '#38BDF8', 'Loyal': '#10B981'},
            hole=0.4
        )
        fig_seg_count.update_layout(template='plotly_white')
        st.plotly_chart(fig_seg_count, use_container_width=True)
        
    with seg_c2:
        fig_seg_rev = px.bar(
            seg_summary,
            x='customer_segment',
            y='total_revenue',
            title='<b>Total Revenue by Segment</b>',
            color='customer_segment',
            color_discrete_map={'New': '#94A3B8', 'Returning': '#38BDF8', 'Loyal': '#10B981'},
            text_auto='$,.0f'
        )
        fig_seg_rev.update_layout(template='plotly_white', showlegend=False)
        st.plotly_chart(fig_seg_rev, use_container_width=True)
        
    with seg_c3:
        fig_seg_avg = px.bar(
            seg_summary,
            x='customer_segment',
            y='avg_spend',
            title='<b>Average Spend ($) per Segment</b>',
            color='customer_segment',
            color_discrete_map={'New': '#94A3B8', 'Returning': '#38BDF8', 'Loyal': '#10B981'},
            text_auto='$.2f'
        )
        fig_seg_avg.update_layout(template='plotly_white', showlegend=False)
        st.plotly_chart(fig_seg_avg, use_container_width=True)
        
    st.markdown("---")
    
    # Subscription Analysis (SQL Q5 & Q9)
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.markdown("#### 🌟 **Subscribers vs Non-Subscribers Performance (SQL Q5)**")
        sub_analysis = filtered_df.groupby('subscription_status').agg(
            total_customers=('customer_id', 'count'),
            avg_spend=('purchase_amount', 'mean'),
            total_revenue=('purchase_amount', 'sum')
        ).reset_index()
        
        fig_sub = px.bar(
            sub_analysis,
            x='subscription_status',
            y='total_revenue',
            color='subscription_status',
            title='<b>Total Revenue: Subscribers vs Non-Subscribers</b>',
            labels={'subscription_status': 'Subscribed?', 'total_revenue': 'Total Sales ($)'},
            color_discrete_sequence=['#818CF8', '#C7D2FE'],
            text_auto='$,.0f'
        )
        fig_sub.update_layout(template='plotly_white', showlegend=False)
        st.plotly_chart(fig_sub, use_container_width=True)
        
    with sub_col2:
        st.markdown("#### 🔁 **Repeat Buyers (>5 purchases) Subscription Propensity (SQL Q9)**")
        repeat_buyers = filtered_df[filtered_df['previous_purchases'] > 5]
        repeat_sub = repeat_buyers['subscription_status'].value_counts().reset_index()
        repeat_sub.columns = ['subscription_status', 'count']
        
        fig_repeat = px.pie(
            repeat_sub,
            names='subscription_status',
            values='count',
            title='<b>Repeat Buyers (>5 Purchases) Subscription Share</b>',
            color='subscription_status',
            color_discrete_map={'Yes': '#10B981', 'No': '#CBD5E1'},
            hole=0.4
        )
        fig_repeat.update_layout(template='plotly_white')
        st.plotly_chart(fig_repeat, use_container_width=True)

    # Payment Methods & Purchase Frequency
    st.markdown("---")
    st.markdown("#### 💳 **Payment Preferences & Purchasing Frequency**")
    pay_c1, pay_c2 = st.columns(2)
    with pay_c1:
        pay_df = filtered_df.groupby('payment_method')['customer_id'].count().reset_index()
        pay_df.columns = ['payment_method', 'transactions']
        fig_pay = px.bar(
            pay_df.sort_values(by='transactions', ascending=False),
            x='payment_method',
            y='transactions',
            color='transactions',
            title='<b>Transaction Volume by Payment Method</b>',
            color_continuous_scale='Blues',
            text_auto=True
        )
        fig_pay.update_layout(template='plotly_white', showlegend=False)
        st.plotly_chart(fig_pay, use_container_width=True)
        
    with pay_c2:
        freq_df = filtered_df['frequency_of_purchases'].value_counts().reset_index()
        freq_df.columns = ['frequency', 'count']
        fig_freq = px.bar(
            freq_df,
            x='frequency',
            y='count',
            color='count',
            title='<b>Distribution of Purchase Frequencies</b>',
            color_continuous_scale='Purples',
            text_auto=True
        )
        fig_freq.update_layout(template='plotly_white', showlegend=False)
        st.plotly_chart(fig_freq, use_container_width=True)

# =========================================================
# TAB 3: DISCOUNTS, PRICING & SHIPPING
# =========================================================
with tab_discounts:
    st.markdown("### 🏷️ **Promotional Effectiveness, Pricing & Shipping Impact**")
    
    disc_c1, disc_c2 = st.columns(2)
    
    with disc_c1:
        # Top 5 products with highest discount rate (SQL Q6)
        prod_disc = df.groupby('item_purchased').agg(
            total_orders=('customer_id', 'count'),
            discount_orders=('discount_applied', lambda x: (x == 'Yes').sum())
        ).reset_index()
        prod_disc['discount_rate'] = (prod_disc['discount_orders'] / prod_disc['total_orders']) * 100
        top5_disc = prod_disc.sort_values(by='discount_rate', ascending=False).head(5)
        
        fig_top_disc = px.bar(
            top5_disc,
            x='discount_rate',
            y='item_purchased',
            orientation='h',
            title='<b>Top 5 Products with Highest Discount Rate (%) (SQL Q6)</b>',
            labels={'discount_rate': 'Discounted Purchases (%)', 'item_purchased': 'Product'},
            color='discount_rate',
            color_continuous_scale='Oranges',
            text_auto='.1f'
        )
        fig_top_disc.update_layout(template='plotly_white', yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig_top_disc, use_container_width=True)
        
    with disc_c2:
        # Shipping types comparison (SQL Q4)
        ship_summary = filtered_df.groupby('shipping_type')['purchase_amount'].agg(['mean', 'count']).reset_index()
        ship_summary.columns = ['shipping_type', 'avg_spend', 'order_count']
        
        fig_ship = px.bar(
            ship_summary.sort_values(by='avg_spend', ascending=False),
            x='shipping_type',
            y='avg_spend',
            title='<b>Average Spend by Shipping Method (SQL Q4)</b>',
            labels={'avg_spend': 'Avg Purchase Amount ($)', 'shipping_type': 'Shipping Type'},
            color='avg_spend',
            color_continuous_scale='Viridis',
            text_auto='$.2f'
        )
        fig_ship.update_layout(template='plotly_white')
        st.plotly_chart(fig_ship, use_container_width=True)
        
    st.markdown("---")
    
    # High-Value Discount Customers (SQL Q2)
    st.markdown("#### 💎 **High-Value Discount Users (SQL Q2)**")
    st.caption("Customers who utilized a promotional discount but still exceeded the overall average order value ($59.76).")
    
    overall_avg = df['purchase_amount'].mean()
    high_val_discount = filtered_df[(filtered_df['discount_applied'] == 'Yes') & (filtered_df['purchase_amount'] >= overall_avg)]
    
    hvd_c1, hvd_c2, hvd_c3 = st.columns(3)
    hvd_c1.metric("High-Value Promo Customers", f"{len(high_val_discount):,}", f"{(len(high_val_discount)/len(filtered_df))*100:.1f}% of total")
    hvd_c2.metric("Total Revenue from This Segment", f"${high_val_discount['purchase_amount'].sum():,.0f}")
    hvd_c3.metric("Their Average Spend", f"${high_val_discount['purchase_amount'].mean():.2f}", f"+${high_val_discount['purchase_amount'].mean() - overall_avg:.2f} vs overall avg")
    
    # Review Rating distribution & Top 5 Rated items (SQL Q3)
    st.markdown("---")
    rev_c1, rev_c2 = st.columns(2)
    with rev_c1:
        top5_rated = df.groupby('item_purchased')['review_rating'].mean().nlargest(5).reset_index()
        top5_rated.columns = ['item_purchased', 'avg_rating']
        fig_rated = px.bar(
            top5_rated,
            x='avg_rating',
            y='item_purchased',
            orientation='h',
            title='<b>Top 5 Products by Average Customer Rating ⭐ (SQL Q3)</b>',
            labels={'avg_rating': 'Avg Review Rating', 'item_purchased': 'Product'},
            color='avg_rating',
            color_continuous_scale='YlGn',
            text_auto='.2f'
        )
        fig_rated.update_layout(template='plotly_white', yaxis=dict(autorange='reversed'))
        st.plotly_chart(fig_rated, use_container_width=True)
        
    with rev_c2:
        fig_rating_box = px.box(
            filtered_df,
            x='category',
            y='review_rating',
            color='category',
            title='<b>Review Rating Distribution by Category</b>',
            labels={'review_rating': 'Review Rating (1 to 5)', 'category': 'Category'}
        )
        fig_rating_box.update_layout(template='plotly_white', showlegend=False)
        st.plotly_chart(fig_rating_box, use_container_width=True)

# =========================================================
# TAB 4: SQL BUSINESS QUESTIONS (10)
# =========================================================
with tab_sql:
    st.markdown("### ⚡ **SQL Analysis & Business Questions Explorer**")
    st.markdown("This section presents the 10 core business analytical queries written for PostgreSQL and executes them interactively with visual outputs.")
    
    sql_questions = {
        "Q1. Total revenue generated by Male vs Female customers": 1,
        "Q2. Customers who used a discount but spent more than the average amount": 2,
        "Q3. Top 5 products with the highest average review rating": 3,
        "Q4. Average purchase amount comparison between Standard & Express Shipping": 4,
        "Q5. Do subscribed customers spend more? (Subscribers vs Non-subscribers)": 5,
        "Q6. Top 5 products with highest percentage of purchases with discount": 6,
        "Q7. Segment customers into New, Returning, and Loyal": 7,
        "Q8. Top 3 most purchased products within each category": 8,
        "Q9. Are repeat buyers (>5 purchases) likely to subscribe?": 9,
        "Q10. Revenue contribution of each age group": 10
    }
    
    selected_query_title = st.selectbox("Select a Business Analytics Query to Inspect:", list(sql_questions.keys()))
    q_num = sql_questions[selected_query_title]
    
    if q_num == 1:
        st.markdown("**Business Goal:** Compare revenue contribution between male and female shoppers.")
        st.code("""
SELECT gender, SUM(purchase_amount) AS revenue
FROM customer
GROUP BY gender;
        """, language="sql")
        
        q1_res = df.groupby('gender')['purchase_amount'].sum().reset_index()
        q1_res.columns = ['Gender', 'Revenue ($)']
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(q1_res.style.format({'Revenue ($)': '${:,.2f}'}), use_container_width=True)
        with c2:
            fig_q1 = px.pie(q1_res, names='Gender', values='Revenue ($)', title='Male vs Female Revenue Share', hole=0.45)
            fig_q1.update_layout(template='plotly_white')
            st.plotly_chart(fig_q1, use_container_width=True)

    elif q_num == 2:
        st.markdown("**Business Goal:** Identify high-value discount buyers spending >= average ticket size ($59.76).")
        st.code("""
SELECT customer_id, purchase_amount 
FROM customer 
WHERE discount_applied = 'Yes' 
  AND purchase_amount >= (SELECT AVG(purchase_amount) FROM customer);
        """, language="sql")
        
        avg_amt = df['purchase_amount'].mean()
        q2_res = df[(df['discount_applied'] == 'Yes') & (df['purchase_amount'] >= avg_amt)][['customer_id', 'purchase_amount', 'item_purchased', 'category']]
        c1, c2 = st.columns([2, 1])
        with c1:
            st.dataframe(q2_res.head(20).style.format({'purchase_amount': '${:.2f}'}), use_container_width=True)
        with c2:
            st.metric("Total Qualified Customers", f"{len(q2_res):,}")
            st.metric("Avg Spend of this group", f"${q2_res['purchase_amount'].mean():.2f}")
            st.metric("Benchmark Avg Spend", f"${avg_amt:.2f}")

    elif q_num == 3:
        st.markdown("**Business Goal:** Find top 5 rated items to highlight customer satisfaction champions.")
        st.code("""
SELECT item_purchased, ROUND(AVG(review_rating::numeric), 2) AS "Average Product Rating"
FROM customer
GROUP BY item_purchased
ORDER BY AVG(review_rating) DESC
LIMIT 5;
        """, language="sql")
        
        q3_res = df.groupby('item_purchased')['review_rating'].mean().round(2).nlargest(5).reset_index()
        q3_res.columns = ['Item Purchased', 'Average Rating']
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(q3_res, use_container_width=True)
        with c2:
            fig_q3 = px.bar(q3_res, x='Average Rating', y='Item Purchased', orientation='h', color='Average Rating', color_continuous_scale='Teal')
            fig_q3.update_layout(template='plotly_white', yaxis=dict(autorange='reversed'))
            st.plotly_chart(fig_q3, use_container_width=True)

    elif q_num == 4:
        st.markdown("**Business Goal:** Compare average order amount for Standard vs Express shipping.")
        st.code("""
SELECT shipping_type, ROUND(AVG(purchase_amount), 2) AS avg_spend
FROM customer
WHERE shipping_type IN ('Standard', 'Express')
GROUP BY shipping_type;
        """, language="sql")
        
        q4_res = df[df['shipping_type'].isin(['Standard', 'Express'])].groupby('shipping_type')['purchase_amount'].mean().round(2).reset_index()
        q4_res.columns = ['Shipping Type', 'Average Purchase Amount ($)']
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(q4_res.style.format({'Average Purchase Amount ($)': '${:.2f}'}), use_container_width=True)
        with c2:
            fig_q4 = px.bar(q4_res, x='Shipping Type', y='Average Purchase Amount ($)', color='Shipping Type', text_auto='$.2f')
            fig_q4.update_layout(template='plotly_white', showlegend=False)
            st.plotly_chart(fig_q4, use_container_width=True)

    elif q_num == 5:
        st.markdown("**Business Goal:** Evaluate whether subscribed customers generate higher revenue and spend per transaction.")
        st.code("""
SELECT subscription_status,
       COUNT(customer_id) AS total_customers,
       ROUND(AVG(purchase_amount), 2) AS avg_spend,
       ROUND(SUM(purchase_amount), 2) AS total_revenue
FROM customer
GROUP BY subscription_status
ORDER BY total_revenue, avg_spend DESC;
        """, language="sql")
        
        q5_res = df.groupby('subscription_status').agg(
            total_customers=('customer_id', 'count'),
            avg_spend=('purchase_amount', 'mean'),
            total_revenue=('purchase_amount', 'sum')
        ).reset_index()
        q5_res.columns = ['Subscription Status', 'Total Customers', 'Avg Spend ($)', 'Total Revenue ($)']
        st.dataframe(q5_res.style.format({'Avg Spend ($)': '${:.2f}', 'Total Revenue ($)': '${:,.2f}'}), use_container_width=True)

    elif q_num == 6:
        st.markdown("**Business Goal:** Find top 5 products with highest proportion of purchases made using discounts.")
        st.code("""
SELECT item_purchased,
       ROUND(100.0 * SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS discount_rate
FROM customer
GROUP BY item_purchased
ORDER BY discount_rate DESC
LIMIT 5;
        """, language="sql")
        
        q6_res = df.groupby('item_purchased').agg(
            discount_count=('discount_applied', lambda x: (x == 'Yes').sum()),
            total_count=('customer_id', 'count')
        ).reset_index()
        q6_res['Discount Rate (%)'] = ((q6_res['discount_count'] / q6_res['total_count']) * 100).round(2)
        q6_res = q6_res.sort_values(by='Discount Rate (%)', ascending=False).head(5)
        st.dataframe(q6_res[['item_purchased', 'Discount Rate (%)', 'discount_count', 'total_count']], use_container_width=True)

    elif q_num == 7:
        st.markdown("**Business Goal:** Segment customers into New (1), Returning (2-10), and Loyal (>10) based on purchase counts.")
        st.code("""
WITH customer_type AS (
    SELECT customer_id, previous_purchases,
    CASE 
        WHEN previous_purchases = 1 THEN 'New'
        WHEN previous_purchases BETWEEN 2 AND 10 THEN 'Returning'
        ELSE 'Loyal'
    END AS customer_segment
    FROM customer
)
SELECT customer_segment, COUNT(*) AS "Number of Customers" 
FROM customer_type 
GROUP BY customer_segment;
        """, language="sql")
        
        q7_res = df['customer_segment'].value_counts().reindex(['New', 'Returning', 'Loyal']).reset_index()
        q7_res.columns = ['Customer Segment', 'Number of Customers']
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(q7_res, use_container_width=True)
        with c2:
            fig_q7 = px.bar(q7_res, x='Customer Segment', y='Number of Customers', color='Customer Segment', text_auto=True)
            fig_q7.update_layout(template='plotly_white', showlegend=False)
            st.plotly_chart(fig_q7, use_container_width=True)

    elif q_num == 8:
        st.markdown("**Business Goal:** Rank and extract the top 3 best-selling products inside each category using window functions.")
        st.code("""
WITH item_counts AS (
    SELECT category,
           item_purchased,
           COUNT(customer_id) AS total_orders,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY COUNT(customer_id) DESC) AS item_rank
    FROM customer
    GROUP BY category, item_purchased
)
SELECT item_rank, category, item_purchased, total_orders
FROM item_counts
WHERE item_rank <= 3;
        """, language="sql")
        
        item_c = df.groupby(['category', 'item_purchased']).size().reset_index(name='total_orders')
        item_c['item_rank'] = item_c.groupby('category')['total_orders'].rank(method='first', ascending=False).astype(int)
        q8_res = item_c[item_c['item_rank'] <= 3].sort_values(by=['category', 'item_rank'])
        q8_res = q8_res[['item_rank', 'category', 'item_purchased', 'total_orders']]
        st.dataframe(q8_res, use_container_width=True)

    elif q_num == 9:
        st.markdown("**Business Goal:** Check whether repeat customers (>5 previous transactions) tend to subscribe.")
        st.code("""
SELECT subscription_status,
       COUNT(customer_id) AS repeat_buyers
FROM customer
WHERE previous_purchases > 5
GROUP BY subscription_status;
        """, language="sql")
        
        rep = df[df['previous_purchases'] > 5]
        q9_res = rep['subscription_status'].value_counts().reset_index()
        q9_res.columns = ['Subscription Status', 'Repeat Buyers (>5 Purchases)']
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(q9_res, use_container_width=True)
        with c2:
            fig_q9 = px.pie(q9_res, names='Subscription Status', values='Repeat Buyers (>5 Purchases)', hole=0.4)
            fig_q9.update_layout(template='plotly_white')
            st.plotly_chart(fig_q9, use_container_width=True)

    elif q_num == 10:
        st.markdown("**Business Goal:** Analyze total revenue contribution by age quartile segments.")
        st.code("""
SELECT 
    age_group,
    SUM(purchase_amount) AS total_revenue
FROM customer
GROUP BY age_group
ORDER BY total_revenue DESC;
        """, language="sql")
        
        q10_res = df.groupby('age_group', observed=False)['purchase_amount'].sum().reset_index()
        q10_res.columns = ['Age Group', 'Total Revenue ($)']
        q10_res = q10_res.sort_values(by='Total Revenue ($)', ascending=False)
        c1, c2 = st.columns([1, 2])
        with c1:
            st.dataframe(q10_res.style.format({'Total Revenue ($)': '${:,.2f}'}), use_container_width=True)
        with c2:
            fig_q10 = px.bar(q10_res, x='Age Group', y='Total Revenue ($)', color='Age Group', text_auto='$,.0f')
            fig_q10.update_layout(template='plotly_white', showlegend=False)
            st.plotly_chart(fig_q10, use_container_width=True)

# =========================================================
# TAB 5: RAW DATA & EXPORT
# =========================================================
with tab_data:
    st.markdown("### 📁 **Filtered Dataset & Export**")
    st.markdown(f"Displaying **{len(filtered_df):,}** matching records based on active sidebar filters.")
    
    # Download Button
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="filtered_customer_shopping_behavior.csv",
        mime="text/csv"
    )
    
    st.dataframe(filtered_df, use_container_width=True, height=450)
    
    st.markdown("#### 📐 **Statistical Summary**")
    st.dataframe(filtered_df.describe().T, use_container_width=True)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748B; font-size: 0.88rem; padding: 10px;">
    Crafted with ❤️ by <b>Krishna Kumar Chaurasia</b> | Built with Python, Pandas, Plotly & Streamlit | 
    <a href="https://github.com/krishna10kkc/Customer_Shopping_Behavior_Analysis" target="_blank" style="color: #3B82F6;">GitHub Repo</a> | 
    <a href="https://linkedin.com/in/krishna-kumar-chaurasia-3154a132b" target="_blank" style="color: #3B82F6;">LinkedIn</a>
</div>
""", unsafe_allow_html=True)
