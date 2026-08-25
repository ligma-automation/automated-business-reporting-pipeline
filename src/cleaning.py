
import pandas as pd


def clean_data(df):
    df = df.copy()

    # Clean text columns
    text_columns = [
        "Transaction_ID",
        "Location",
        "Customer",
        "Product_Service",
        "Sales_Rep",
        "Status",
    ]

    for col in text_columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
        )

    # Standardize location names
    df["Location"] = (
        df["Location"]
        .str.title()
    )

    # Parse dates
    df["Transaction_Date"] = pd.to_datetime(
        df["Transaction_Date"],
        errors="coerce"
    )

    # Numeric fields
    for col in ["Quantity", "Unit_Price", "Revenue"]:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Remove exact duplicate transaction IDs
    df = df.drop_duplicates(
        subset=["Transaction_ID"],
        keep="first"
    )

    return df.reset_index(drop=True)


def get_valid_records(df):
    valid_mask = (
        df["Transaction_ID"].notna()
        & df["Transaction_Date"].notna()
        & df["Customer"].notna()
        & df["Sales_Rep"].notna()
        & df["Quantity"].gt(0)
        & df["Revenue"].ge(0)
    )

    return df[valid_mask].copy()