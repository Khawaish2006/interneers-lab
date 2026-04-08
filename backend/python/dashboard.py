# dashboard.py
# Streamlit dashboard for Product Inventory
# Run with: streamlit run dashboard.py

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add project root to path so we can import our models
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Connect to MongoDB
from db_connection import connect_to_mongodb
connect_to_mongodb()

# Import models directly
from products.models import Product
from products.category_model import ProductCategory

# ─── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="Product Inventory Dashboard",
    page_icon="📦",
    layout="wide"
)

# ─── TITLE ─────────────────────────────────────────────────────
st.title("📦 Product Inventory Dashboard")
st.markdown("---")

# ─── HELPER FUNCTIONS ──────────────────────────────────────────

def get_all_products():
    """Fetch all products from MongoDB"""
    products = Product.objects.all()
    data = []
    for p in products:
        try:
            category_title = p.category.title if p.category else "Unknown"
        except Exception:
            category_title = "Unknown"
        data.append({
            "ID": str(p.id),
            "Name": p.name,
            "Category": category_title,
            "Brand": p.brand,
            "Price (₹)": float(str(p.price)),
            "Stock": p.quantity_in_warehouse,
            "Description": p.description,
        })
    return pd.DataFrame(data)


def get_all_categories():
    """Fetch all categories from MongoDB"""
    return list(ProductCategory.objects.all())


# ─── SIDEBAR ───────────────────────────────────────────────────
st.sidebar.title("🔧 Controls")
st.sidebar.markdown("---")

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

# Filter by category
st.sidebar.subheader("Filter Products")
categories = get_all_categories()
category_options = ["All"] + [c.title for c in categories]
selected_category = st.sidebar.selectbox("Category", category_options)

# Filter by brand
brand_filter = st.sidebar.text_input("Brand contains")

# Filter by price
st.sidebar.subheader("Price Range")
min_price = st.sidebar.number_input("Min Price", min_value=0, value=0)
max_price = st.sidebar.number_input("Max Price", min_value=0, value=1000000)

# ─── MAIN CONTENT ──────────────────────────────────────────────

# Load products
df = get_all_products()

# Apply filters
if not df.empty:
    if selected_category != "All":
        df = df[df["Category"] == selected_category]
    if brand_filter:
        df = df[df["Brand"].str.contains(brand_filter, case=False)]
    df = df[(df["Price (₹)"] >= min_price) & (df["Price (₹)"] <= max_price)]

# ─── METRICS ───────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Products", len(df))
with col2:
    total_stock = df["Stock"].sum() if not df.empty else 0
    st.metric("Total Stock", total_stock)
with col3:
    avg_price = round(df["Price (₹)"].mean(), 2) if not df.empty else 0
    st.metric("Avg Price", f"₹{avg_price}")
with col4:
    low_stock = len(df[df["Stock"] < 10]) if not df.empty else 0
    st.metric("Low Stock Items", low_stock)

st.markdown("---")

# ─── PRODUCTS TABLE ────────────────────────────────────────────
st.subheader("📋 Product Inventory")

if df.empty:
    st.warning("No products found. Add some products first!")
else:
    st.dataframe(
        df.drop(columns=["ID"]),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# ─── TASK 3: ADD PRODUCT FORM ──────────────────────────────────
st.subheader("➕ Add New Product")

with st.form("add_product_form"):
    col1, col2 = st.columns(2)

    with col1:
        new_name = st.text_input("Product Name *")
        new_brand = st.text_input("Brand *")
        new_price = st.number_input("Price *", min_value=0.01, value=100.0)
        new_quantity = st.number_input("Quantity", min_value=0, value=0)

    with col2:
        new_description = st.text_area("Description")
        category_titles = [c.title for c in categories]
        new_category = st.selectbox("Category *", category_titles)

    submitted = st.form_submit_button("Add Product")

    if submitted:
        if not new_name or not new_brand:
            st.error("Name and Brand are required!")
        else:
            try:
                # Find the selected category object
                category_obj = ProductCategory.objects.get(title=new_category)

                # Create the product
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)

                product = Product(
                    name=new_name,
                    brand=new_brand,
                    price=new_price,
                    quantity_in_warehouse=new_quantity,
                    description=new_description,
                    category=category_obj,
                    created_at=now,
                    updated_at=now
                )
                product.save()
                st.success(f"✅ Product '{new_name}' added successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error adding product: {e}")

st.markdown("---")

# ─── TASK 3: REMOVE PRODUCT ────────────────────────────────────
st.subheader("🗑️ Remove Product")

if df.empty:
    st.info("No products to remove.")
else:
    product_options = df["Name"] + " (" + df["ID"] + ")"
    selected_product = st.selectbox("Select product to remove", product_options)

    if st.button("🗑️ Delete Selected Product", type="primary"):
        # Extract ID from selection
        product_id = selected_product.split("(")[-1].replace(")", "").strip()
        try:
            product = Product.objects.get(id=product_id)
            product_name = product.name
            product.delete()
            st.success(f"✅ Product '{product_name}' deleted successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting product: {e}")