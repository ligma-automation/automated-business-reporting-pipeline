import os
import random
from datetime import datetime, timedelta

import pandas as pd

# ============================================================
# CONFIG
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "sample_data")

os.makedirs(OUTPUT_DIR, exist_ok=True)

random.seed(42)

LOCATIONS = [
    "Atlanta",
    "Charlotte",
    "Nashville",
    "Dallas",
]

PRODUCTS = {
    "Implementation": (2500, 7500),
    "Consulting": (1000, 5000),
    "Support": (500, 2500),
    "Data Services": (1500, 6000),
    "Automation": (2000, 8000),
}

SALES_REPS = [
    "Jordan Lee",
    "Taylor Smith",
    "Morgan Davis",
    "Alex Johnson",
    "Casey Brown",
]

CUSTOMERS = [
    "Atlas Medical",
    "Northstar Logistics",
    "Pioneer Manufacturing",
    "Summit Financial",
    "Blue Ridge Services",
    "Evergreen Retail",
    "Vertex Technology",
    "Crescent Health",
    "Oakline Partners",
    "Redwood Operations",
]


# ============================================================
# HELPERS
# ============================================================

def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def create_transaction(transaction_id, location):
    product = random.choice(list(PRODUCTS.keys()))
    low_price, high_price = PRODUCTS[product]

    quantity = random.randint(1, 5)
    unit_price = round(random.uniform(low_price, high_price), 2)
    revenue = round(quantity * unit_price, 2)

    transaction_date = random_date(
        datetime(2026, 1, 1),
        datetime(2026, 8, 15),
    )

    return {
        "Transaction_ID": transaction_id,
        "Transaction_Date": transaction_date.strftime("%Y-%m-%d"),
        "Location": location,
        "Customer": random.choice(CUSTOMERS),
        "Product_Service": product,
        "Quantity": quantity,
        "Unit_Price": unit_price,
        "Revenue": revenue,
        "Sales_Rep": random.choice(SALES_REPS),
        "Status": random.choice(
            ["Completed", "Completed", "Completed", "Pending", "Cancelled"]
        ),
    }


# ============================================================
# CREATE CLEAN BASE DATA
# ============================================================

def create_location_data(location, rows=150):
    data = []

    for i in range(rows):
        transaction_id = f"{location[:3].upper()}-{10000 + i}"
        data.append(create_transaction(transaction_id, location))

    return pd.DataFrame(data)


# ============================================================
# INTRODUCE REALISTIC DATA QUALITY ISSUES
# ============================================================

def introduce_data_issues(df, location):
    df = df.copy()

    # --------------------------------------------------------
    # 1. Duplicate records
    # --------------------------------------------------------
    duplicate_rows = df.sample(3, random_state=1)
    df = pd.concat([df, duplicate_rows], ignore_index=True)

    # --------------------------------------------------------
    # 2. Missing customers
    # --------------------------------------------------------
    missing_customer_indexes = random.sample(
        list(df.index),
        3,
    )
    df.loc[missing_customer_indexes, "Customer"] = None

    # --------------------------------------------------------
    # 3. Missing sales reps
    # --------------------------------------------------------
    missing_rep_indexes = random.sample(
        list(df.index),
        2,
    )
    df.loc[missing_rep_indexes, "Sales_Rep"] = None

    # --------------------------------------------------------
    # 4. Negative revenue
    # --------------------------------------------------------
    negative_revenue_index = random.choice(list(df.index))
    df.loc[negative_revenue_index, "Revenue"] = (
        -abs(df.loc[negative_revenue_index, "Revenue"])
    )

    # --------------------------------------------------------
    # 5. Invalid quantity
    # --------------------------------------------------------
    quantity_index = random.choice(list(df.index))
    df.loc[quantity_index, "Quantity"] = 0

    # --------------------------------------------------------
    # 6. Inconsistent location formatting
    # --------------------------------------------------------
    location_variations = {
        "Atlanta": ["ATLANTA", "Atlanta ", "atlanta"],
        "Charlotte": ["CHARLOTTE", "Charlotte ", "charlotte"],
        "Nashville": ["NASHVILLE", "Nashville ", "nashville"],
        "Dallas": ["DALLAS", "Dallas ", "dallas"],
    }

    variation_indexes = random.sample(
        list(df.index),
        4,
    )

    for idx in variation_indexes:
        df.loc[idx, "Location"] = random.choice(
            location_variations[location]
        )

    # --------------------------------------------------------
    # 7. Invalid date
    # --------------------------------------------------------
    invalid_date_index = random.choice(list(df.index))
    df.loc[invalid_date_index, "Transaction_Date"] = "INVALID_DATE"

    return df


# ============================================================
# EXPORT FILES
# ============================================================

def generate_files():
    print("\nGenerating sample business data...\n")

    for location in LOCATIONS:
        df = create_location_data(location)
        df = introduce_data_issues(df, location)

        if location in ["Atlanta", "Nashville"]:
            file_path = os.path.join(
                OUTPUT_DIR,
                f"{location}_Transactions.csv",
            )

            df.to_csv(file_path, index=False)

        else:
            file_path = os.path.join(
                OUTPUT_DIR,
                f"{location}_Transactions.xlsx",
            )

            df.to_excel(file_path, index=False)

        print(
            f"{location:<12} "
            f"{len(df):>4} rows -> "
            f"{os.path.basename(file_path)}"
        )

    print("\nSample data generation complete.")
    print(f"Files created in:\n{OUTPUT_DIR}\n")


if __name__ == "__main__":
    generate_files()