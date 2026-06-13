import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Define the prices for the 5 products (in USD)
PRODUCT_PRICES = {
    "Laptop": 1200.0,
    "Smartphone": 800.0,
    "Tablet": 450.0,
    "Smartwatch": 250.0,
    "Headphones": 150.0
}

# Define the regions
REGIONS = ["North", "South", "East", "West"]

# Set random seed for reproducibility (so we get the same data every time we run it)
random.seed(42)
np.random.seed(42)

def generate_sales_data(filename="sales_data.csv", rows=150):
    """
    Generates a mock CSV file of sales data for learning/testing.
    """
    data = []
    
    # Define date range for 2024
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    # Number of days in 2024
    delta_days = (end_date - start_date).days
    
    for i in range(rows):
        # 1. Generate a random date in 2024
        random_days = random.randint(0, delta_days)
        date = start_date + timedelta(days=random_days)
        
        # 2. Randomly select a product
        product = random.choice(list(PRODUCT_PRICES.keys()))
        
        # 3. Randomly select a region
        region = random.choice(REGIONS)
        
        # 4. Generate random units sold (between 10 and 500)
        units_sold = random.randint(10, 500)
        
        # 5. Calculate revenue based on the product's price and units sold
        price = PRODUCT_PRICES[product]
        revenue = units_sold * price
        
        # Add the generated transaction record to our list
        data.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Product": product,
            "Region": region,
            "Units_Sold": units_sold,
            "Revenue": revenue
        })
        
    # Create a Pandas DataFrame from our list of transactions
    df = pd.DataFrame(data)
    
    # Sort the data by Date so it flows chronologically
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(by="Date").reset_index(drop=True)
    
    # Save the DataFrame to a CSV file
    df.to_csv(filename, index=False)
    print(f"Successfully generated {rows} rows of sample sales data and saved to '{filename}'.")

if __name__ == "__main__":
    # When this script is run, generate the data
    generate_sales_data()
