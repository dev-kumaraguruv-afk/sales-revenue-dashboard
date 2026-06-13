import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# STEP 1: PAGE CONFIGURATION & STYLING
# ==========================================
# We set up the app layout to be "wide" (takes up full screen) and set a tab title and icon.
st.set_page_config(
    page_title="Sales & Revenue Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to give the dashboard a premium, modern design with smooth styling
st.markdown("""
    <style>
    /* Main dashboard background color */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    /* Style the sidebar elements */
    .css-1d391kg {
        background-color: #161b22;
    }
    /* Style the card metrics containers */
    div[data-testid="stMetricContainer"] {
        background-color: #1f2937;
        border: 1px solid #374151;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetricContainer"]:hover {
        transform: translateY(-3px);
        border-color: #10b981; /* Highlight with green on hover */
    }
    /* Title typography */
    h1 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        background: linear-gradient(45deg, #00dbde, #fc00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Main Title of the Dashboard
st.write("# 📊 Sales & Revenue Analysis Dashboard")
st.write("Welcome to your dashboard! Upload a dataset or explore the default generated sales data.")

# ==========================================
# STEP 2: DATA LOADING FUNCTION
# ==========================================
@st.cache_data # Cache the data load so it doesn't reload the file on every click
def load_data(file_path_or_buffer):
    """
    Loads sales data from CSV or Excel, formats columns, and returns a Pandas DataFrame.
    """
    # Check if the file is a buffer (from streamlit uploader) or a local file path
    if isinstance(file_path_or_buffer, str):
        # Local file path
        df = pd.read_csv(file_path_or_buffer)
    else:
        # Uploaded file object
        if file_path_or_buffer.name.endswith('.csv'):
            df = pd.read_csv(file_path_or_buffer)
        else:
            df = pd.read_excel(file_path_or_buffer)
            
    # Format Date column to pandas datetime objects for easier filtering
    df['Date'] = pd.to_datetime(df['Date'])
    return df

# ==========================================
# STEP 3: FILE UPLOAD & DEFAULT DATA SETTING
# ==========================================
# A file uploader block that accepts CSV or Excel files
uploaded_file = st.file_uploader("Upload your sales report (CSV or Excel formats)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Load the uploaded file
        df = load_data(uploaded_file)
        
        # Verify required columns exist
        required_cols = {'Date', 'Product', 'Region', 'Units_Sold', 'Revenue'}
        if not required_cols.issubset(df.columns):
            st.error(f"⚠️ Error: The uploaded file must contain the columns: {', '.join(required_cols)}")
            st.stop()
            
    except Exception as e:
        st.error(f"⚠️ Failed to parse file: {e}")
        st.stop()
else:
    # If no file is uploaded, fallback to 'sales_data.csv'. 
    # If the file does not exist, we run generate_data.py on the fly.
    csv_filename = "sales_data.csv"
    if not os.path.exists(csv_filename):
        try:
            from generate_data import generate_sales_data
            generate_sales_data(csv_filename)
        except ImportError:
            st.warning("Could not import generate_data.py to create sales data. Creating basic dataframe locally...")
            # Fallback code to create dummy data in case generate_data.py is missing
            dates = pd.date_range(start="2024-01-01", end="2024-12-31", periods=150)
            df = pd.DataFrame({
                "Date": dates,
                "Product": [f"Product {i%5+1}" for i in range(150)],
                "Region": ["North", "South", "East", "West"] * 37 + ["North"] * 2,
                "Units_Sold": [int(x) for x in pd.Series(range(150)) * 2 + 50],
                "Revenue": [float(x) for x in (pd.Series(range(150)) * 2 + 50) * 100]
            })
            df.to_csv(csv_filename, index=False)
            
    df = load_data(csv_filename)

# Ensure 'Date' column is a Datetime type
df['Date'] = pd.to_datetime(df['Date'])

# ==========================================
# STEP 4: SIDEBAR FILTERS
# ==========================================
st.sidebar.header("🎯 Dashboard Filters")
st.sidebar.write("Refine the visualizations below:")

# Find min and max dates in dataset
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()

# Date range picker filter
date_range = st.sidebar.date_input(
    "1. Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Region filter (Multi-select)
all_regions = sorted(df['Region'].dropna().unique())
selected_regions = st.sidebar.multiselect(
    "2. Select Region(s)",
    options=all_regions,
    default=all_regions
)

# Product filter (Multi-select)
all_products = sorted(df['Product'].dropna().unique())
selected_products = st.sidebar.multiselect(
    "3. Select Product(s)",
    options=all_products,
    default=all_products
)

# ==========================================
# STEP 5: FILTER THE DATAFRAME
# ==========================================
# Check if date range is a valid range (contains both start and end date)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    # Fallback to entire dataset limits if dates are partially selected
    start_date, end_date = pd.to_datetime(min_date), pd.to_datetime(max_date)

# Apply filters
df_filtered = df[
    (df['Date'] >= start_date) &
    (df['Date'] <= end_date) &
    (df['Region'].isin(selected_regions)) &
    (df['Product'].isin(selected_products))
]

# If filters leave us with empty data, display warning and exit gracefully
if df_filtered.empty:
    st.warning("⚠️ No data available matching the selected filters. Please adjust your date range, regions, or products.")
    st.stop()

# ==========================================
# STEP 6: CALCULATE KPIS & PERFORMANCE METRICS
# ==========================================
# 1. Total Revenue
total_revenue = df_filtered['Revenue'].sum()

# 2. Total Units Sold
total_units = df_filtered['Units_Sold'].sum()

# 3. Top Product by Revenue
top_product_rev = df_filtered.groupby('Product')['Revenue'].sum()
top_product_name = top_product_rev.idxmax()
top_product_val = top_product_rev.max()

# 4. Best Region by Revenue
best_region_rev = df_filtered.groupby('Region')['Revenue'].sum()
best_region_name = best_region_rev.idxmax()
best_region_val = best_region_rev.max()

# 5. Month-over-Month (MoM) Growth (Pro Feature)
# We calculate MoM revenue growth for the selected data range
df_mom = df_filtered.copy()
df_mom['YearMonth'] = df_mom['Date'].dt.to_period('M')
monthly_revs = df_mom.groupby('YearMonth')['Revenue'].sum().reset_index().sort_values('YearMonth')

mom_growth = 0.0
mom_display = "N/A"
if len(monthly_revs) >= 2:
    last_month_val = monthly_revs.iloc[-1]['Revenue']
    prev_month_val = monthly_revs.iloc[-2]['Revenue']
    if prev_month_val > 0:
        mom_growth = ((last_month_val - prev_month_val) / prev_month_val) * 100
        mom_display = f"{mom_growth:+.1f}%"
    else:
        mom_display = "0.0%"

# ==========================================
# STEP 7: RENDER KPI CARDS
# ==========================================
st.write("---")
# Create 5 columns for our metric cards
kpi_cols = st.columns(5)

with kpi_cols[0]:
    st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}")
    
with kpi_cols[1]:
    st.metric(label="Total Units Sold", value=f"{total_units:,}")

with kpi_cols[2]:
    st.metric(label="Top Product", value=top_product_name, delta=f"${top_product_val:,.0f} Rev")

with kpi_cols[3]:
    st.metric(label="Best Region", value=best_region_name, delta=f"${best_region_val:,.0f} Rev")

with kpi_cols[4]:
    # MoM growth is colored positive green or negative red automatically
    st.metric(label="MoM Revenue Growth", value=mom_display, delta=f"{mom_growth:+.1f}% vs Prev Month" if mom_display != "N/A" else None)

st.write("---")

# ==========================================
# STEP 8: RENDER INTERACTIVE CHARTS
# ==========================================
# Layout setup: Row 1 has Line Trend (Width 7) and Region Pie (Width 5)
chart_cols1 = st.columns([7, 5])

with chart_cols1[0]:
    # A. MONTHLY REVENUE TREND (Line Chart)
    # Group data by year-month to track chronological performance
    df_trend = df_filtered.copy()
    df_trend['YearMonth'] = df_trend['Date'].dt.to_period('M')
    # Summarize revenue by month
    monthly_trend = df_trend.groupby('YearMonth')['Revenue'].sum().reset_index()
    monthly_trend['Month_Label'] = monthly_trend['YearMonth'].dt.strftime('%b %Y')
    
    fig_line = px.line(
        monthly_trend,
        x='Month_Label',
        y='Revenue',
        title="📈 Monthly Revenue Trend",
        markers=True,
        labels={'Revenue': 'Revenue ($)', 'Month_Label': 'Month'}
    )
    # Customise Plotly theme and color to match standard dark dashboard look
    fig_line.update_traces(line_color='#00d4ff', line_width=3, marker=dict(size=8, color='#ff007f'))
    fig_line.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig_line, width="stretch")

with chart_cols1[1]:
    # B. REVENUE BY REGION (Donut Chart)
    # Group by Region and aggregate Revenue
    df_region = df_filtered.groupby('Region')['Revenue'].sum().reset_index()
    
    fig_pie = px.pie(
        df_region,
        values='Revenue',
        names='Region',
        title="🌍 Revenue Share by Region",
        hole=0.4, # Hole size of 0.4 makes it a modern donut chart
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_pie, width="stretch")

# Layout setup: Row 2 has Bar Chart (Width 6) and Top 5 Table (Width 6)
chart_cols2 = st.columns([6, 6])

with chart_cols2[0]:
    # C. REVENUE BY PRODUCT (Bar Chart)
    # Group by Product and sum revenue, sort to display cleanest hierarchy
    df_prod = df_filtered.groupby('Product')['Revenue'].sum().reset_index()
    df_prod = df_prod.sort_values(by='Revenue', ascending=True)
    
    fig_bar = px.bar(
        df_prod,
        x='Revenue',
        y='Product',
        orientation='h', # Horizontal chart is cleaner for products labels
        title="🏷️ Revenue by Product",
        labels={'Revenue': 'Revenue ($)', 'Product': 'Product'},
        color='Revenue',
        color_continuous_scale='viridis'
    )
    fig_bar.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_bar, width="stretch")

with chart_cols2[1]:
    # D. TOP 5 PRODUCTS (Data Table)
    st.write("### 🏆 Top Products Table")
    # Group by Product, get sum of units and revenue, then sort
    df_top = df_filtered.groupby('Product').agg({
        'Units_Sold': 'sum',
        'Revenue': 'sum'
    }).reset_index().sort_values(by='Revenue', ascending=False).head(5)
    
    # Format Table for elegant display
    df_top.columns = ["Product", "Units Sold", "Total Revenue"]
    df_top["Units Sold"] = df_top["Units Sold"].map("{:,}".format)
    df_top["Total Revenue"] = df_top["Total Revenue"].map("${:,.2f}".format)
    
    # Hide indices and display table
    st.dataframe(df_top, width="stretch", hide_index=True)

# ==========================================
# STEP 9: DOWNLOAD FILTERED DATA (Pro Feature)
# ==========================================
# Place a handy CSV download button in the sidebar under all filters
st.sidebar.write("---")
st.sidebar.subheader("📥 Export Data")

# Convert the filtered DataFrame back to CSV in memory
filtered_csv = df_filtered.to_csv(index=False).encode('utf-8')

st.sidebar.download_button(
    label="Download Filtered CSV",
    data=filtered_csv,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
    help="Export the current filtered view of your dashboard data as a CSV file."
)
