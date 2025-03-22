import ast
import sqlite3
import pandas as pd
import json

# Database Configuration
DB_FILE = "images.db"
TABLE_NAME = "images"

# Open SQLite connection
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Query for expenses and revenues
query_expenses = f"SELECT id, details FROM {TABLE_NAME} WHERE revenue_expense = 0"
query_revenues = f"SELECT id, details FROM {TABLE_NAME} WHERE revenue_expense = 1"

# Fetch data for expenses and revenues
expenses_df = pd.read_sql(query_expenses, conn)
revenues_df = pd.read_sql(query_revenues, conn)

# Function to extract JSON details
def extract_json_details(df):
    # Parse the 'details' column as JSON
    details_data = df['details'].apply(lambda x: ast.literal_eval(x) if x else {})
    
    # Convert JSON data into separate columns and merge with the original dataframe
    details_df = pd.json_normalize(details_data)
    
    # Concatenate the original dataframe with the parsed JSON data
    df = pd.concat([df, details_df], axis=1)
    
    return df

# Extract the JSON details for both expenses and revenues
expenses_df = extract_json_details(expenses_df)
revenues_df = extract_json_details(revenues_df)

# Drop the 'details' column as it's no longer needed
expenses_df = expenses_df.drop(columns=['details'])
revenues_df = revenues_df.drop(columns=['details'])

# Prepare the CSV file paths
expenses_csv = 'expenses.csv'
revenues_csv = 'revenues.csv'

# Save expenses data to CSV
expenses_df.to_csv(expenses_csv, index=False)
print(f"Expenses data with JSON details successfully written to {expenses_csv}")

# Save revenues data to CSV
revenues_df.to_csv(revenues_csv, index=False)
print(f"Revenues data with JSON details successfully written to {revenues_csv}")

# Close the SQLite connection
conn.close()
