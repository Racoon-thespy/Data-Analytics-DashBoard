import streamlit as sl
import pandas as pd
import plotly.express as px

#Configuring the page:
sl.set_page_config(page_title = "Sales Analysis DashBoard", layout = "wide")
sl.markdown("""
<style>
    .header {
        background-color: #2C3E50;
        color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
</style>
<div class="header">
    <h1>Supermarket Sales Dashboard</h1>
</div>
""", unsafe_allow_html=True)


#Loading the data
@sl.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path, encoding = "latin1")
    data["Date"] = pd.to_datetime(data["Date"], errors = 'coerce')
    data = data.dropna(subset = ['Date'])
    return data
data_path = "./supermarket_sales.csv"
data = load_data(data_path)
sl.dataframe(data.head())

#Sidebar Feautures and filters
sl.sidebar.header("Filters")
selected_branch = sl.sidebar.multiselect(
    "Select Branch", options = data["Branch"].unique(), 
    default = data["Branch"].unique())

selected_product_line = sl.sidebar.multiselect(
    "Select Product Line", options = data["Product line"].unique(), 
    default = data["Product line"].unique())

selected_customer_type = sl.sidebar.multiselect(
    "Select Customer type", options = data["Customer type"].unique(), 
    default = data["Customer type"].unique())

min_date = data['Date'].min().date()
max_date = data['Date'].max().date()
selected_date = sl.sidebar.date_input(
    "Select Date Range",
    value = (min_date, max_date),
    min_value = min_date,
    max_value = max_date
)

filtered_data = data[
    (data["Branch"].isin(selected_branch))&
    (data["Product line"].isin(selected_product_line))&
    (data["Customer type"].isin(selected_customer_type))&
    (data['Date'] >= pd.to_datetime(selected_date[0]))&
    (data['Date'] <= pd.to_datetime(selected_date[1]))
    ]

if not selected_date or len(selected_date) != 2:
    sl.warning("Please selected valid date range!!")
    sl.stop()

if filtered_data.empty:
    sl.warning("No data for the given filtered range!!")
    sl.stop()

filtered_data['Total'] = filtered_data['Total'].round(2)
filtered_data['gross income'] = filtered_data['gross income'].round(2)
filtered_data['Rating'] = filtered_data['Rating'].round(2)
filtered_data['Quantity'] = filtered_data['Quantity'].round(2)

total_sales = filtered_data['Total'].sum()
gross_income = filtered_data['gross income'].sum()
avg_rating = filtered_data['Rating'].mean()
total_quantity = filtered_data['Quantity'].sum()

sl.subheader("Key Metrics")
col1, col2, col3, col4 = sl.columns(4)
with col1:
    sl.metric(label = "Total Sales", value = f"${total_sales:,.1f}")
with col2:
    sl.metric(label = "Gross Income", value = f"${gross_income:,.1f}")
with col3:
    sl.metric(label = "Total Quantity", value = f"{total_quantity:,.1f}")
with col4:
    sl.metric(label = "Average Rating", value = f"{avg_rating:,.2f}")

sales_by_branch = filtered_data.groupby('Branch')['Total'].sum().reset_index()
sales_by_branch['Total'] = sales_by_branch['Total'].round(1)
sl.subheader("Total Sales by Branch")
fig_branch = px.bar(
    sales_by_branch,
    x = "Branch",
    y = "Total",
    title = 'Total sales by branch',
    text = 'Total',
    color = 'Branch',
    color_discrete_sequence = px.colors.sequential.Teal
)
sl.plotly_chart(fig_branch, use_container_width = True)

sales_by_product = filtered_data.groupby('Product line')['Total'].sum().reset_index()
avg_rating_by_product = filtered_data.groupby('Product line')['Rating'].mean().reset_index()
sales_by_customer = filtered_data.groupby('Customer type')['Total'].sum().reset_index()
sales_by_payment = filtered_data.groupby('Payment')['Total'].sum().reset_index()
sales_trends = filtered_data.groupby('Date')['Total'].sum().reset_index()


sales_by_product['Total'] = sales_by_product['Total'].round(1)
avg_rating_by_product['Rating'] = avg_rating_by_product['Rating'].round(2)
sales_by_customer['Total'] = sales_by_customer['Total'].round(1)
sales_by_payment['Total'] = sales_by_payment['Total'].round(1)


#Sales and Ratings by Product Line
sl.subheader("Sales and Rating by Product Line")
col1, col2 = sl.columns(2)
with col1:
    fig_product_sales = px.bar(
        sales_by_product, x = "Total", y = "Product line", orientation = 'h',
        title = 'Sales by Product Line', text = 'Total', color = 'Product line',
        color_discrete_sequence = px.colors.sequential.Plasma
    )
    sl.plotly_chart(fig_product_sales, use_container_width=True)

with col2:
    fig_product_ratings = px.bar(
        avg_rating_by_product, x = "Rating",y = "Product line", orientation = 'h',
        title = 'Average Rating by Product Line', text = 'Rating', color = 'Product line',
        color_discrete_sequence = px.colors.sequential.Viridis
    )
    sl.plotly_chart(fig_product_ratings, use_container_width=True)

#Sales by Branch
sl.markdown("### Sales by Branch")
fig_branch_sales = px.bar(
    sales_by_branch, x = "Branch", y = "Total", 
    title = "Total sales by Branch", text = "Total", color = "Branch",
    color_discrete_sequence=px.colors.sequential.Teal
    )
sl.plotly_chart(fig_branch_sales, use_container_width = True)

#Sales by Customer Type
sl.markdown("### Sales by Customer Type")
fig_customer_sales = px.pie(
    sales_by_customer, names = "Customer type", values = "Total",
    title = "Sales Distribution by Customer Type", color = "Customer type", 
    color_discrete_sequence=px.colors.sequential.Teal 
)
sl.plotly_chart(fig_customer_sales, use_container_width=True)

#Sales by payment Method
sl.markdown("### Sales by Payment Method")
fig_payment_sales = px.pie(
    sales_by_payment, names = "Payment", values = "Total",
    title = "Sales by Payment Method", color = "Payment",
    color_discrete_sequence=px.colors.sequential.Purples
)
sl.plotly_chart(fig_payment_sales, use_container_width = True)

#Sales Trends
sl.markdown('### Sales Trends over time')
fig_sales_trends = px.line(
    sales_trends, x = "Date", y = "Total", 
    title = "Sales Trends over time", markers = True, 
    color_discrete_sequence=["#2C3E50"] 
)
sl.plotly_chart(fig_sales_trends, use_container_width=True)