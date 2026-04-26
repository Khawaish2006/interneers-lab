# dashboard.py
# Streamlit dashboard for Product Inventory
# Run with: streamlit run dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
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

# ─── SEMANTIC SEARCH SETUP ─────────────────────────────────────
from sentence_transformers import SentenceTransformer

@st.cache_resource
def load_model(model_name="all-MiniLM-L6-v2"):
    """Load sentence transformer model — cached so it only loads once"""
    return SentenceTransformer(model_name)

@st.cache_data
def load_product_embeddings(model_name="all-MiniLM-L6-v2"):
    """Fetch all products and generate embeddings — cached"""
    _model = load_model(model_name)
    all_products = list(Product.objects.all())
    texts, names, descriptions, categories, brands, prices, stocks = [], [], [], [], [], [], []

    for p in all_products:
        try:
            cat = p.category.title if p.category else ""
        except:
            cat = ""
        text = f"{p.name}. Category: {cat}. {p.description}"
        texts.append(text)
        names.append(p.name)
        descriptions.append(p.description)
        categories.append(cat)
        brands.append(p.brand)
        prices.append(float(str(p.price)))
        stocks.append(p.quantity_in_warehouse)

    embeddings = _model.encode(texts)
    return names, descriptions, categories, brands, prices, stocks, embeddings

def cosine_similarity(vec1, vec2):
    dot = np.dot(vec1, vec2)
    mag = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    return float(dot / mag) if mag != 0 else 0.0

def semantic_search(query, embeddings, names, top_k=5, model_name="all-MiniLM-L6-v2"):
    """Search products by semantic similarity"""
    _model = load_model(model_name)
    query_vec = _model.encode([query])[0]
    scores = [(names[i], cosine_similarity(query_vec, embeddings[i])) for i in range(len(names))]
    scores.sort(key=lambda x: x[1], reverse=True)
    # Filter out results below minimum threshold
    scores = [s for s in scores if s[1] >= 0.35]
    return scores[:top_k]

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
    st.cache_data.clear()
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

# ─── TASK 5: SEMANTIC SEARCH ───────────────────────────────────
st.subheader("🧠 Semantic Search")
st.markdown("Search products by **meaning** — not just keywords!")


semantic_query = st.text_input(
        "Search query",
        placeholder="e.g. 'wireless audio device', 'something to wear', 'mobile phone'"
    )


if semantic_query:
    with st.spinner("🔍 Searching..."):
        names, descriptions, categories_list, brands, prices, stocks, embeddings = load_product_embeddings()
        results = semantic_search(semantic_query, embeddings, names, top_k=100)

    st.markdown(f"**Results for:** *'{semantic_query}'*")

    result_data = []
    for rank, (name, score) in enumerate(results, 1):
        idx = names.index(name)
        result_data.append({
            "Rank": rank,
            "Name": name,
            "Category": categories_list[idx],
            "Brand": brands[idx],
            "Price (₹)": prices[idx],
            "Stock": stocks[idx],
            "Similarity Score": round(score, 4)
        })

    result_df = pd.DataFrame(result_data)
    st.dataframe(result_df, use_container_width=True, hide_index=True)
    st.caption("💡 Similarity Score: closer to 1.0 = more relevant to your query")

st.markdown("---")

# ─── ADVANCED 1: FIND SIMILAR PRODUCTS ─────────────────────────
st.subheader("🔁 Find Similar Products")
st.markdown("Select any product and find the most similar items in your inventory!")

all_product_names = df["Name"].tolist() if not df.empty else []

if all_product_names:
    selected_product_name = st.selectbox(
        "Select a product",
        all_product_names,
        key="similar_product_select"
    )
    

    if st.button("🔍 Find Similar Products"):
        with st.spinner("Finding similar products..."):
            names, descriptions, categories_list, brands, prices, stocks, embeddings = load_product_embeddings()

            if selected_product_name in names:
                idx = names.index(selected_product_name)
                selected_vec = embeddings[idx]

                # Calculate similarity with all other products
                similarities = []
                for i, name in enumerate(names):
                    if name != selected_product_name:
                        score = cosine_similarity(selected_vec, embeddings[i])
                        similarities.append((name, score, i))

                # Sort by score
                similarities.sort(key=lambda x: x[1], reverse=True)
                similarities = [s for s in similarities if s[1] >= 0.5]
                top_similar = similarities[:50]

                st.markdown(f"**Products similar to:** *{selected_product_name}*")

                similar_data = []
                for rank, (name, score, i) in enumerate(top_similar, 1):
                    similar_data.append({
                        "Rank": rank,
                        "Name": name,
                        "Category": categories_list[i],
                        "Brand": brands[i],
                        "Price (₹)": prices[i],
                        "Stock": stocks[i],
                        "Similarity Score": round(score, 4)
                    })

                st.dataframe(
                    pd.DataFrame(similar_data),
                    use_container_width=True,
                    hide_index=True
                )
                st.caption("💡 Higher similarity score = more similar to your selected product")
            else:
                st.warning("Product not found in embeddings. Try refreshing!")
else:
    st.info("No products available.")

st.markdown("---")

# ─── CREATE CATEGORY ───────────────────────────────────────────
st.subheader("🗂️ Add New Category")

with st.form("add_category_form"):
    col1, col2 = st.columns(2)

    with col1:
        new_category_title = st.text_input("Category Name *")
    with col2:
        new_category_description = st.text_area("Description")

    category_submitted = st.form_submit_button("Add Category")

    if category_submitted:
        if not new_category_title:
            st.error("Category name is required!")
        else:
            try:
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)

                existing = ProductCategory.objects(title=new_category_title).first()
                if existing:
                    st.error(f"❌ Category '{new_category_title}' already exists!")
                else:
                    category = ProductCategory(
                        title=new_category_title,
                        description=new_category_description,
                        created_at=now,
                        updated_at=now
                    )
                    category.save()
                    st.success(f"✅ Category '{new_category_title}' added successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error adding category: {e}")

st.markdown("---")

# ─── ADD PRODUCT FORM ──────────────────────────────────────────
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
                category_obj = ProductCategory.objects.get(title=new_category)

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

# ─── REMOVE PRODUCT ────────────────────────────────────────────
st.subheader("🗑️ Remove Product")

if df.empty:
    st.info("No products to remove.")
else:
    product_options = df["Name"] + " (" + df["ID"] + ")"
    selected_product = st.selectbox("Select product to remove", product_options)

    if st.button("🗑️ Delete Selected Product", type="primary"):
        product_id = selected_product.split("(")[-1].replace(")", "").strip()
        try:
            product = Product.objects.get(id=product_id)
            product_name = product.name
            product.delete()
            st.success(f"✅ Product '{product_name}' deleted successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting product: {e}")

st.markdown("---")

# ─── ADVANCED: SCENARIO SELECTOR ───────────────────────────────
st.subheader("🎯 AI Scenario Selector")
st.markdown("Choose a warehouse scenario and let AI populate the database with relevant products!")

SCENARIOS = {
    "🎄 Holiday Rush": {
        "description": "Festive season — high demand for gifts, decorations, and party items",
        "stock_min": 300,
        "stock_max": 500,
        "prompt_hint": "festive holiday season products like gifts, decorations, party supplies, winter clothing, and electronics"
    },
    "☀️ Summer Collection": {
        "description": "Summer season — outdoor, cooling, and seasonal products",
        "stock_min": 200,
        "stock_max": 400,
        "prompt_hint": "summer season products like light clothing, outdoor gear, cooling appliances, summer foods and beverages"
    },
    "📚 Back to School": {
        "description": "School season — stationery, books, electronics, and essentials",
        "stock_min": 150,
        "stock_max": 350,
        "prompt_hint": "back to school products like books, stationery, bags, electronics like laptops and calculators, and school essentials"
    },
    "🎆 New Year Sale": {
        "description": "New Year — discounted items, party supplies, and fresh start products",
        "stock_min": 250,
        "stock_max": 450,
        "prompt_hint": "new year sale products like party supplies, fitness equipment, kitchen appliances, and lifestyle products"
    },
}

selected_scenario = st.selectbox("Select a Scenario", list(SCENARIOS.keys()))
scenario_info = SCENARIOS[selected_scenario]
st.info(f"📌 {scenario_info['description']}")
st.markdown(f"**Stock levels will be:** {scenario_info['stock_min']} – {scenario_info['stock_max']} units")
num_products = st.slider("How many products to generate?", min_value=5, max_value=30, value=10)

if st.button("🚀 Generate & Save Products", type="primary"):
    try:
        from groq import Groq
        from dotenv import load_dotenv
        from pydantic import BaseModel, field_validator
        from typing import Optional
        from datetime import datetime, timezone
        import os
        import json

        load_dotenv()
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        all_categories = get_all_categories()
        category_map = {cat.title: cat for cat in all_categories}
        category_names = list(category_map.keys())

        prompt = f"""
Generate exactly {num_products} realistic warehouse products for a "{selected_scenario.replace('🎄 ', '').replace('☀️ ', '').replace('📚 ', '').replace('🎆 ', '')}" scenario as a JSON array.
Focus on: {scenario_info['prompt_hint']}
Each product must belong to one of these categories only: {category_names}
Each product must have exactly these fields:
- name: string
- description: string (1-2 sentences)
- category: string (must be exactly one of: {category_names})
- price: float (min 0.01)
- brand: string
- quantity_in_warehouse: integer (between {scenario_info['stock_min']} and {scenario_info['stock_max']})
Rules: Return ONLY a valid JSON array, no explanation, no markdown, no extra text
"""

        with st.spinner("🤖 AI is generating products..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

        raw_output = response.choices[0].message.content
        cleaned = raw_output.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        products_data = json.loads(cleaned)

        class ProductSchema(BaseModel):
            name: str
            description: Optional[str] = ""
            category: str
            price: float
            brand: str
            quantity_in_warehouse: int

            @field_validator('price')
            def price_must_be_positive(cls, v):
                if v <= 0:
                    raise ValueError("Price must be greater than 0")
                return round(v, 2)

            @field_validator('quantity_in_warehouse')
            def quantity_must_be_non_negative(cls, v):
                if v < 0:
                    raise ValueError("Quantity cannot be negative")
                return v

            @field_validator('category')
            def category_must_exist(cls, v):
                if v not in category_names:
                    raise ValueError(f"Invalid category: {v}")
                return v

        valid_products = []
        invalid_count = 0

        for product in products_data:
            try:
                validated = ProductSchema(**product)
                valid_products.append(validated)
            except Exception:
                invalid_count += 1

        saved = 0
        now = datetime.now(timezone.utc)

        for vp in valid_products:
            try:
                category_obj = category_map.get(vp.category)
                if not category_obj:
                    continue
                Product(
                    name=vp.name,
                    description=vp.description,
                    category=category_obj,
                    price=vp.price,
                    brand=vp.brand,
                    quantity_in_warehouse=vp.quantity_in_warehouse,
                    created_at=now,
                    updated_at=now
                ).save()
                saved += 1
            except Exception:
                invalid_count += 1

        st.success(f"🎉 Successfully saved {saved} products for '{selected_scenario}' scenario!")
        if invalid_count > 0:
            st.warning(f"⚠️ {invalid_count} products were skipped due to validation errors.")

        preview_data = [{"Name": vp.name, "Category": vp.category, "Brand": vp.brand,
                         "Price (₹)": vp.price, "Stock": vp.quantity_in_warehouse}
                        for vp in valid_products]
        st.dataframe(pd.DataFrame(preview_data), use_container_width=True, hide_index=True)
        st.info("🔄 Click 'Refresh Data' in the sidebar to see updated products!")

    except Exception as e:
        st.error(f"❌ Something went wrong: {e}")