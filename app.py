import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import json
import uuid

# Set page configuration
st.set_page_config(
    page_title="FastFood Shop Management",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #ff4b4b;
        color: white;
    }
    div.stButton > button:first-child {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.3rem;
    }
    div.stButton > button:hover {
        background-color: #ff6b6b;
        color: white;
    }
    .reportBlock {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #ff4b4b;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
    .stDateInput > div > div > input {
        min-height: 40px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'orders' not in st.session_state:
    st.session_state.orders = []

if 'menu_items' not in st.session_state:
    st.session_state.menu_items = [
        {"id": str(uuid.uuid4()), "name": "Dabeli", "price": 20, "category": "Fast Food"},
        {"id": str(uuid.uuid4()), "name": "Sandwich", "price": 30, "category": "Fast Food"},
        {"id": str(uuid.uuid4()), "name": "Vada Pav", "price": 15, "category": "Fast Food"},
        {"id": str(uuid.uuid4()), "name": "Samosa", "price": 10, "category": "Snacks"},
        {"id": str(uuid.uuid4()), "name": "Chai", "price": 10, "category": "Beverages"}
    ]

if 'menu_categories' not in st.session_state:
    st.session_state.menu_categories = ["Fast Food", "Snacks", "Beverages", "Desserts", "Others"]

if 'expenses' not in st.session_state:
    st.session_state.expenses = []

# Initialize order_completed flag
if 'order_completed' not in st.session_state:
    st.session_state.order_completed = False

# Function to save data
def save_data():
    data = {
        "orders": st.session_state.orders,
        "menu_items": st.session_state.menu_items,
        "expenses": st.session_state.expenses,
        "menu_categories": st.session_state.menu_categories
    }
    os.makedirs('data', exist_ok=True)
    with open('data/shop_data.json', 'w') as f:
        json.dump(data, f)

# Function to load data
def load_data():
    try:
        if os.path.exists('data/shop_data.json'):
            with open('data/shop_data.json', 'r') as f:
                data = json.load(f)
                st.session_state.orders = data.get("orders", [])
                st.session_state.menu_items = data.get("menu_items", st.session_state.menu_items)
                st.session_state.expenses = data.get("expenses", [])
                st.session_state.menu_categories = data.get("menu_categories", ["Fast Food", "Snacks", "Beverages", "Desserts", "Others"])
    except Exception as e:
        st.error(f"Error loading data: {e}")

# Load data at startup
load_data()

# Function to add a new order
def add_order(items, total_amount):
    order = {
        "id": str(uuid.uuid4()),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": items,
        "total": total_amount
    }
    st.session_state.orders.append(order)
    save_data()
    return order

# Function to reset order form
def reset_order_form():
    for item in st.session_state.menu_items:
        qty_key = f"qty_{item['id']}"
        st.session_state[qty_key] = 0

# Function to add a new expense
def add_expense(expense_date, category, amount, description):
    expense = {
        "id": str(uuid.uuid4()),
        "date": expense_date,
        "category": category,
        "amount": amount,
        "description": description
    }
    st.session_state.expenses.append(expense)
    save_data()
    return expense

# Function to add a new menu item
def add_menu_item(name, price, category):
    item = {
        "id": str(uuid.uuid4()),
        "name": name,
        "price": price,
        "category": category
    }
    st.session_state.menu_items.append(item)
    save_data()
    return item

# Function to add a new category
def add_menu_category(category_name):
    if category_name not in st.session_state.menu_categories:
        st.session_state.menu_categories.append(category_name)
        save_data()
        return True
    return False

# Function to delete a menu item
def delete_menu_item(item_id):
    st.session_state.menu_items = [item for item in st.session_state.menu_items if item["id"] != item_id]
    save_data()

# Function to delete an order
def delete_order(order_id):
    st.session_state.orders = [order for order in st.session_state.orders if order["id"] != order_id]
    save_data()

# Function to filter orders by date range
def filter_orders_by_date(orders, start_date, end_date):
    filtered_orders = []
    for order in orders:
        order_date = datetime.strptime(order["date"], "%Y-%m-%d %H:%M:%S").date()
        if start_date <= order_date <= end_date:
            filtered_orders.append(order)
    return filtered_orders

# Function to filter expenses by date range
def filter_expenses_by_date(expenses, start_date, end_date):
    filtered_expenses = []
    for expense in expenses:
        expense_date = datetime.strptime(expense["date"], "%Y-%m-%d").date()
        if start_date <= expense_date <= end_date:
            filtered_expenses.append(expense)
    return filtered_expenses

# Function to export orders to Excel
def export_orders_to_excel(orders):
    if not orders:
        return None
    
    # Prepare data for Excel
    order_data = []
    for order in orders:
        order_date = datetime.strptime(order["date"], "%Y-%m-%d %H:%M:%S")
        for item in order["items"]:
            order_data.append({
                "Order ID": order["id"],
                "Date": order_date.strftime("%Y-%m-%d"),
                "Time": order_date.strftime("%H:%M:%S"),
                "Item": item["name"],
                "Quantity": item["quantity"],
                "Price": item["price"],
                "Subtotal": item["subtotal"]
            })
    
    df = pd.DataFrame(order_data)
    return df

# Function to export expenses to Excel
def export_expenses_to_excel(expenses):
    if not expenses:
        return None
    
    # Prepare data for Excel
    expense_data = []
    for expense in expenses:
        expense_data.append({
            "Expense ID": expense["id"],
            "Date": expense["date"],
            "Category": expense["category"],
            "Amount": expense["amount"],
            "Description": expense["description"]
        })
    
    df = pd.DataFrame(expense_data)
    return df

# Main App UI
st.title("🍔 Jayubhai Dabeli Wala")

# Create tabs for different sections
tabs = st.tabs(["📝 New Order", "📊 Sales Report", "🍕 Menu Management", "💰 Expenses", "📈 Dashboard"])

# Tab 1: New Order
with tabs[0]:
    st.header("Create New Order")
    
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Create a form for order entry
        with st.form(key="order_form"):
            # Reset order_completed flag if an order was just completed
            if st.session_state.order_completed:
                reset_order_form()
                st.session_state.order_completed = False
                
            order_items = []
            total_amount = 0
            
            # Group menu items by their categories
            menu_categories_dict = {}
            for category in st.session_state.menu_categories:
                menu_categories_dict[category] = [item for item in st.session_state.menu_items if item.get("category", "Others") == category]
            
            # If there are items without a category, add them to Others
            for item in st.session_state.menu_items:
                if "category" not in item:
                    item["category"] = "Others"
            
            # Add horizontal scrolling for category tabs
            st.markdown("""
            <style>
            .stTabs [data-baseweb="tab-list"] {
                flex-wrap: nowrap;
                overflow-x: auto;
                white-space: nowrap;
                padding-bottom: 5px;
            }
            .stTabs [data-baseweb="tab"] {
                display: inline-block;
                min-width: 100px;
                text-align: center;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Display menu items with tabs for categories
            category_tabs = st.tabs(list(menu_categories_dict.keys()))
            
            for i, category in enumerate(menu_categories_dict.keys()):
                with category_tabs[i]:
                    if not menu_categories_dict[category]:
                        st.info(f"No items in {category} category.")
                        continue
                        
                    # Create a grid layout for items (3 columns)
                    items_in_category = menu_categories_dict[category]
                    rows = [items_in_category[i:i+3] for i in range(0, len(items_in_category), 3)]
                    
                    for row in rows:
                        cols = st.columns(3)
                        for i, item in enumerate(row):
                            with cols[i]:
                                st.write(f"**{item['name']}**")
                                st.write(f"₹{item['price']}")
                                
                                # Initialize quantity to 0 or get existing value
                                qty_key = f"qty_{item['id']}"
                                quantity = st.number_input(f"Qty", min_value=0, max_value=100, 
                                                          value=st.session_state.get(qty_key, 0), 
                                                          step=1, key=qty_key)
                                
                                if quantity > 0:
                                    subtotal = quantity * item['price']
                                    st.write(f"Subtotal: ₹{subtotal}")
                                    total_amount += subtotal
                                    order_items.append({
                                        "id": item["id"],
                                        "name": item["name"],
                                        "price": item["price"],
                                        "quantity": quantity,
                                        "subtotal": subtotal
                                    })
            
            st.markdown("---")
            st.markdown(f"### Total: ₹{total_amount}")
            
            # Make the Complete Order button more prominent
            st.markdown("""
            <style>
            div[data-testid="stFormSubmitButton"] > button {
                background-color: #4CAF50;
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 15px 25px;
                width: 100%;
                margin-top: 15px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: all 0.3s ease;
            }
            div[data-testid="stFormSubmitButton"] > button:hover {
                background-color: #45a049;
                box-shadow: 0 6px 8px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }
            </style>
            """, unsafe_allow_html=True)
            
            submit_button = st.form_submit_button(label="COMPLETE ORDER", help="Click to complete your order")
            
            if submit_button and order_items:
                # Filter out items with zero quantity
                order_items = [item for item in order_items if item["quantity"] > 0]
                if order_items:
                    new_order = add_order(order_items, total_amount)
                    st.success(f"Order added successfully! Order ID: {new_order['id'][:8]}")
                    
                    # Set order_completed flag to true
                    st.session_state.order_completed = True
                    
                    # Rerun the app to apply the reset
                    st.experimental_rerun()
                else:
                    st.warning("Please select at least one item to place an order.")
    
    with col2:
        st.subheader("Recent Orders")
        # Display recent orders
        recent_orders = sorted(st.session_state.orders, key=lambda x: x["date"], reverse=True)[:5]
        
        for order in recent_orders:
            col_order, col_delete = st.columns([5, 1])
            with col_order:
                with st.expander(f"Order {order['id'][:8]} - {order['date']} - ₹{order['total']}"):
                    for item in order["items"]:
                        st.write(f"{item['name']} x {item['quantity']} = ₹{item['subtotal']}")
            with col_delete:
                if st.button("🗑️", key=f"del_order_{order['id']}", help="Delete this order"):
                    delete_order(order['id'])
                    st.success(f"Order {order['id'][:8]} deleted successfully!")
                    st.experimental_rerun()

# Tab 2: Sales Report
with tabs[1]:
    st.header("Sales Report")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now().date())
    
    if start_date > end_date:
        st.error("Error: End date must be after start date.")
    else:
        # Filter orders by date range
        filtered_orders = filter_orders_by_date(st.session_state.orders, start_date, end_date)
        
        # Display summary metrics
        if filtered_orders:
            total_sales = sum(order["total"] for order in filtered_orders)
            total_orders = len(filtered_orders)
            avg_order_value = total_sales / total_orders if total_orders > 0 else 0
            
            # Create metrics row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("<div class='metric-card'><div class='metric-value'>₹{:,.2f}</div><div class='metric-label'>Total Sales</div></div>".format(total_sales), unsafe_allow_html=True)
            with col2:
                st.markdown("<div class='metric-card'><div class='metric-value'>{}</div><div class='metric-label'>Total Orders</div></div>".format(total_orders), unsafe_allow_html=True)
            with col3:
                st.markdown("<div class='metric-card'><div class='metric-value'>₹{:,.2f}</div><div class='metric-label'>Average Order Value</div></div>".format(avg_order_value), unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Prepare data for item-wise sales analysis
            item_sales = {}
            for order in filtered_orders:
                for item in order["items"]:
                    if item["name"] not in item_sales:
                        item_sales[item["name"]] = {
                            "quantity": 0,
                            "revenue": 0
                        }
                    item_sales[item["name"]]["quantity"] += item["quantity"]
                    item_sales[item["name"]]["revenue"] += item["subtotal"]
            
            # Convert to DataFrame for visualization
            sales_df = pd.DataFrame([
                {"Item": item, "Quantity": data["quantity"], "Revenue": data["revenue"]}
                for item, data in item_sales.items()
            ])
            
            if not sales_df.empty:
                # Create two columns for charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Item-wise Sales Quantity")
                    fig = px.bar(
                        sales_df, 
                        x="Item", 
                        y="Quantity",
                        color="Item",
                        text="Quantity"
                    )
                    fig.update_traces(texttemplate='%{text}', textposition='outside')
                    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Item-wise Revenue")
                    fig = px.pie(
                        sales_df, 
                        values="Revenue", 
                        names="Item",
                        hole=0.4
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Display detailed sales data
                st.subheader("Detailed Sales Data")
                st.dataframe(sales_df.sort_values(by="Revenue", ascending=False))
                
                # Export to Excel button
                orders_df = export_orders_to_excel(filtered_orders)
                if orders_df is not None:
                    csv = orders_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Sales Report as CSV",
                        data=csv,
                        file_name=f"sales_report_{start_date}_to_{end_date}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No sales data available for the selected date range.")
        else:
            st.info("No orders found for the selected date range.")

# Tab 3: Menu Management
with tabs[2]:
    st.header("Menu Management")
    
    # Create two columns for better layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Add New Item")
        
        # Add tabs for item and category management
        item_tabs = st.tabs(["Add Item", "Add Category"])
        
        # Tab for adding new menu item
        with item_tabs[0]:
            with st.form(key="add_item_form"):
                new_item_name = st.text_input("Item Name")
                new_item_price = st.number_input("Price (₹)", min_value=1, value=20)
                new_item_category = st.selectbox("Category", options=st.session_state.menu_categories)
                submit_button = st.form_submit_button(label="Add Item")
                
                if submit_button and new_item_name:
                    new_item = add_menu_item(new_item_name, new_item_price, new_item_category)
                    st.success(f"Added {new_item_name} to the menu!")
        
        # Tab for adding new category
        with item_tabs[1]:
            with st.form(key="add_category_form"):
                new_category_name = st.text_input("Category Name")
                category_submit_button = st.form_submit_button(label="Add Category")
                
                if category_submit_button and new_category_name:
                    if add_menu_category(new_category_name):
                        st.success(f"Added {new_category_name} category!")
                    else:
                        st.warning(f"Category {new_category_name} already exists!")
                st.success(f"Added {new_item_name} to the menu!")
    
    with col2:
        st.subheader("Current Menu Items")
        
        # Display current menu items in a table
        if st.session_state.menu_items:
            menu_df = pd.DataFrame(st.session_state.menu_items)
            menu_df = menu_df[["name", "price", "category"]]
            menu_df.columns = ["Item Name", "Price (₹)", "Category"]
            menu_df = menu_df.sort_values(by=["Category", "Item Name"])
            
            # Display with delete buttons
            for i, row in menu_df.iterrows():
                col_name, col_price, col_category, col_action = st.columns([2, 1, 1, 1])
                with col_name:
                    st.write(row["Item Name"])
                with col_price:
                    st.write(f"₹{row['Price (₹)']}")
                with col_category:
                    st.write(row["Category"])
                with col_action:
                    item_id = next(item["id"] for item in st.session_state.menu_items if item["name"] == row["Item Name"])
                    if st.button("Delete", key=f"del_{item_id}"):
                        delete_menu_item(item_id)
                        st.experimental_rerun()
        else:
            st.info("No menu items available. Add some items to get started!")

# Tab 4: Expenses
with tabs[3]:
    st.header("Expense Tracker")
    
    # Create two columns for better layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Add New Expense")
        
        # Form to add new expense
        with st.form(key="add_expense_form"):
            expense_date = st.date_input("Date", datetime.now().date())
            expense_category = st.selectbox(
                "Category", 
                ["Ingredients", "Utilities", "Rent", "Salaries", "Equipment", "Maintenance", "Other"]
            )
            expense_amount = st.number_input("Amount (₹)", min_value=1, value=100)
            expense_description = st.text_area("Description", height=100)
            submit_button = st.form_submit_button(label="Add Expense")
            
            if submit_button:
                new_expense = add_expense(
                    expense_date.strftime("%Y-%m-%d"),
                    expense_category,
                    expense_amount,
                    expense_description
                )
                st.success(f"Expense added successfully!")
    
    with col2:
        st.subheader("Expense Report")
        
        # Date range selector for expenses
        col1, col2 = st.columns(2)
        with col1:
            exp_start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=30), key="exp_start")
        with col2:
            exp_end_date = st.date_input("End Date", datetime.now().date(), key="exp_end")
        
        if exp_start_date > exp_end_date:
            st.error("Error: End date must be after start date.")
        else:
            # Filter expenses by date range
            filtered_expenses = filter_expenses_by_date(st.session_state.expenses, exp_start_date, exp_end_date)
            
            if filtered_expenses:
                total_expenses = sum(expense["amount"] for expense in filtered_expenses)
                st.markdown(f"### Total Expenses: ₹{total_expenses:,.2f}")
                
                # Prepare data for category-wise expense analysis
                category_expenses = {}
                for expense in filtered_expenses:
                    category = expense["category"]
                    if category not in category_expenses:
                        category_expenses[category] = 0
                    category_expenses[category] += expense["amount"]
                
                # Convert to DataFrame for visualization
                expense_df = pd.DataFrame([
                    {"Category": category, "Amount": amount}
                    for category, amount in category_expenses.items()
                ])
                
                # Create pie chart for category-wise expenses
                fig = px.pie(
                    expense_df, 
                    values="Amount", 
                    names="Category",
                    title="Expenses by Category"
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
                
                # Display detailed expense data
                st.subheader("Expense Details")
                expense_details = []
                for expense in filtered_expenses:
                    expense_details.append({
                        "Date": expense["date"],
                        "Category": expense["category"],
                        "Amount": f"₹{expense['amount']:,.2f}",
                        "Description": expense["description"]
                    })
                
                expense_details_df = pd.DataFrame(expense_details)
                st.dataframe(expense_details_df.sort_values(by="Date", ascending=False))
                
                # Export to Excel button
                expenses_df = export_expenses_to_excel(filtered_expenses)
                if expenses_df is not None:
                    csv = expenses_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Expense Report as CSV",
                        data=csv,
                        file_name=f"expense_report_{exp_start_date}_to_{exp_end_date}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("No expenses found for the selected date range.")

# Tab 5: Dashboard
with tabs[4]:
    st.header("Business Dashboard")
    
    # Date range selector for dashboard
    col1, col2 = st.columns(2)
    with col1:
        dash_start_date = st.date_input("Start Date", datetime.now().date() - timedelta(days=30), key="dash_start")
    with col2:
        dash_end_date = st.date_input("End Date", datetime.now().date(), key="dash_end")
    
    if dash_start_date > dash_end_date:
        st.error("Error: End date must be after start date.")
    else:
        # Filter data by date range
        filtered_orders = filter_orders_by_date(st.session_state.orders, dash_start_date, dash_end_date)
        filtered_expenses = filter_expenses_by_date(st.session_state.expenses, dash_start_date, dash_end_date)
        
        # Calculate key metrics
        total_sales = sum(order["total"] for order in filtered_orders)
        total_expenses = sum(expense["amount"] for expense in filtered_expenses)
        profit = total_sales - total_expenses
        profit_margin = (profit / total_sales * 100) if total_sales > 0 else 0
        
        # Display key metrics
        st.subheader("Key Performance Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("<div class='metric-card'><div class='metric-value'>₹{:,.2f}</div><div class='metric-label'>Total Sales</div></div>".format(total_sales), unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='metric-card'><div class='metric-value'>₹{:,.2f}</div><div class='metric-label'>Total Expenses</div></div>".format(total_expenses), unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='metric-card'><div class='metric-value'>₹{:,.2f}</div><div class='metric-label'>Profit</div></div>".format(profit), unsafe_allow_html=True)
        with col4:
            st.markdown("<div class='metric-card'><div class='metric-value'>{:.1f}%</div><div class='metric-label'>Profit Margin</div></div>".format(profit_margin), unsafe_allow_html=True)
        
        # Create daily sales and expenses chart
        if filtered_orders or filtered_expenses:
            st.subheader("Daily Sales & Expenses")
            
            # Prepare data for daily analysis
            date_range = pd.date_range(start=dash_start_date, end=dash_end_date)
            daily_data = {date.strftime("%Y-%m-%d"): {"sales": 0, "expenses": 0} for date in date_range}
            
            # Aggregate sales by day
            for order in filtered_orders:
                order_date = datetime.strptime(order["date"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                if order_date in daily_data:
                    daily_data[order_date]["sales"] += order["total"]
            
            # Aggregate expenses by day
            for expense in filtered_expenses:
                if expense["date"] in daily_data:
                    daily_data[expense["date"]]["expenses"] += expense["amount"]
            
            # Convert to DataFrame for visualization
            daily_df = pd.DataFrame([
                {"Date": date, "Sales": data["sales"], "Expenses": data["expenses"], "Profit": data["sales"] - data["expenses"]}
                for date, data in daily_data.items()
            ])
            
            # Create line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_df["Date"], y=daily_df["Sales"], mode='lines+markers', name='Sales', line=dict(color='green', width=2)))
            fig.add_trace(go.Scatter(x=daily_df["Date"], y=daily_df["Expenses"], mode='lines+markers', name='Expenses', line=dict(color='red', width=2)))
            fig.add_trace(go.Scatter(x=daily_df["Date"], y=daily_df["Profit"], mode='lines+markers', name='Profit', line=dict(color='blue', width=2)))
            
            fig.update_layout(
                title="Daily Financial Performance",
                xaxis_title="Date",
                yaxis_title="Amount (₹)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Top selling items
            if filtered_orders:
                st.subheader("Top Selling Items")
                
                # Prepare data for item-wise sales analysis
                item_sales = {}
                for order in filtered_orders:
                    for item in order["items"]:
                        if item["name"] not in item_sales:
                            item_sales[item["name"]] = {
                                "quantity": 0,
                                "revenue": 0
                            }
                        item_sales[item["name"]]["quantity"] += item["quantity"]
                        item_sales[item["name"]]["revenue"] += item["subtotal"]
                
                # Convert to DataFrame for visualization
                sales_df = pd.DataFrame([
                    {"Item": item, "Quantity": data["quantity"], "Revenue": data["revenue"]}
                    for item, data in item_sales.items()
                ])
                
                if not sales_df.empty:
                    # Sort by revenue
                    sales_df = sales_df.sort_values(by="Revenue", ascending=False)
                    
                    # Create horizontal bar chart
                    fig = px.bar(
                        sales_df.head(10), 
                        y="Item", 
                        x="Revenue",
                        color="Revenue",
                        orientation='h',
                        title="Top Items by Revenue",
                        text="Revenue"
                    )
                    fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for the selected date range.")

# Run the app
if __name__ == "__main__":
    # Remove the incomplete sidebar statement
    pass
