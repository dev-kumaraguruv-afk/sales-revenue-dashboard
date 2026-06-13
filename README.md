# Sales & Revenue Analysis Dashboard

A beginner-friendly, premium interactive dashboard built using **Python**, **Streamlit**, **Pandas**, and **Plotly**. This project generates a realistic transaction dataset for 2024 and allows users to explore KPIs, filter data dynamically, and export results.

---

## 🚀 Key Features

* **Custom Filters**: Interactive sidebar filters for Date Range, Region, and Products.
* **Key Performance Indicators (KPIs)**:
  * Total Revenue (USD)
  * Total Units Sold
  * Top Product (and revenue generated)
  * Best Region (and revenue generated)
  * **Month-over-Month (MoM) Revenue Growth %** (Highlights changes dynamically!)
* **Interactive Charts**:
  * Line chart showing the monthly revenue trend.
  * Horizontal bar chart displaying product-wise revenue.
  * Donut chart representing regional contribution share.
* **Top 5 Table**: Highlights the best-performing items.
* **Data Exporter**: Filtered records can be downloaded directly as a CSV file.
* **File Uploader**: Drag and drop custom CSV or Excel files.

---

## 📁 File Structure

```
sales_dashboard/
├── generate_data.py   # Generates sales_data.csv (150 rows of mock sales data)
├── app.py             # Main Streamlit dashboard application
├── requirements.txt   # List of package dependencies
└── README.md          # Setup and operation guide (this file)
```

---

## 🛠️ Step-by-Step Setup

Follow these simple steps in your terminal to set up and run the application.

### 1. Install Dependencies
Install all required packages using `pip`:
```bash
pip install -r requirements.txt
```
*Alternatively, you can install them individually:*
```bash
pip install streamlit pandas plotly openpyxl
```

### 2. Generate the Sample Data
Run the generator script to create your mock dataset (`sales_data.csv`):
```bash
python generate_data.py
```
This script creates a CSV file with 150 rows representing transactions from January to December 2024.

### 3. Run the Dashboard
Start the local Streamlit web server:
```bash
streamlit run app.py
```
Your browser will open automatically at [http://localhost:8501](http://localhost:8501) displaying the dashboard!

---

## 💡 How to Customize
1. **Change Product Prices**: Open `generate_data.py` and modify the `PRODUCT_PRICES` dictionary.
2. **Add More Data**: Modify the `rows` parameter in the `generate_sales_data(rows=150)` call in `generate_data.py` to generate larger datasets (e.g., 1000 rows).
3. **Upload Your Own File**: Click the **"Upload your sales report"** button at the top of the dashboard to process external datasets. (Make sure they match the required columns: `Date`, `Product`, `Region`, `Units_Sold`, `Revenue`).
