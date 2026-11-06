# 🛍️ Customer Shopping Behavior Analysis — End-to-End Data Analytics Project

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-PostgreSQL-336791.svg)](https://www.postgresql.org/)
[![PowerBI](https://img.shields.io/badge/PowerBI-Dashboard-F2C811.svg)](https://powerbi.microsoft.com/)

> An end-to-end Data Analytics project analyzing retail transactional data to uncover customer demographic trends, promotional effectiveness, loyalty tiers, and purchasing patterns across 3,900 consumer profiles.

---

## 🌐 Live Interactive Streamlit Web App
The project has been converted into an interactive web dashboard built with **Streamlit** and **Plotly**.
- **Run Locally:** `streamlit run app.py`
- **Cloud Deployment:** Streamlit Community Cloud

---

## 📌 Business Objectives & Key Insights

1. **Revenue Distribution:** Analyzed male vs. female revenue splits across four core categories (Clothing, Footwear, Outerwear, Accessories).
2. **Promotional Optimization:** Evaluated high-spending customers utilizing discounts who still exceed the average order value ($59.76).
3. **Product Ratings:** Identified top 5 items with the highest customer review ratings.
4. **Shipping Performance:** Compared average ticket sizes across standard, express, next day air, and free shipping.
5. **Subscription Valuation:** Analyzed average spend and total revenue contributions from subscribed vs non-subscribed customers.
6. **Customer Segmentation:** Segmented buyers into **New** (1 order), **Returning** (2-10 orders), and **Loyal** (>10 orders) to measure lifetime retention.
7. **Geographic Distribution:** Interactive US choropleth mapping state-by-state shopping trends across all 50 states.

---

## 🛠️ Tech Stack & Tools

- **Programming:** Python (Pandas, NumPy)
- **Interactive App & Visualization:** Streamlit, Plotly Express & Graph Objects
- **Database Analysis:** PostgreSQL (Advanced SQL with CTEs, Window Functions, Aggregate Joins)
- **Business Intelligence:** Microsoft Power BI (`customer_behavior_dashboard.pbix`)
- **Presentation & Documentation:** PowerPoint, Gamma AI, Business Problem Spec

---

## 📂 Repository Structure

```text
├── app.py                                   # Full interactive Streamlit Web Dashboard
├── requirements.txt                         # Dependencies for Streamlit Cloud deployment
├── customer_shopping_behavior.csv           # Transactional dataset (3,900 records)
├── Customer_Shopping_Behavior_Analysis.ipynb# Jupyter Notebook for EDA & Data Cleaning
├── customer_behavior_sql_queries_Postgre.sql# 10 core PostgreSQL business questions
├── customer_behavior_dashboard.pbix         # Power BI interactive report
├── Dashboard_ss.png                         # Power BI dashboard screenshot
├── Business Problem Document.pdf            # Business context documentation
├── Customer Shopping Behavior Analysis.pdf  # Project analytical report
└── Customer-Shopping-Behavior-Analysis.pptx # Project presentation deck
```

---

## 🚀 How to Run Locally

1. **Clone this repository:**
   ```bash
   git clone https://github.com/krishna10kkc/Customer_Shopping_Behavior_Analysis.git
   cd Customer_Shopping_Behavior_Analysis
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

---
## Streamlit App URL ##

URL : https://customershoppingbehavioranalysis-kkc.streamlit.app/

## 👨‍💻 Author

**Krishna Kumar Chaurasia**
- 🐙 GitHub: [@krishna10kkc](https://github.com/krishna10kkc)
- 💼 LinkedIn: [Krishna Kumar Chaurasia](https://linkedin.com/in/krishna-kumar-chaurasia-3154a132b)
