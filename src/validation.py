import pandas as pd


REQUIRED_COLUMNS = [
    "Transaction_ID",
    "Transaction_Date",
    "Location",
    "Customer",
    "Product_Service",
    "Quantity",
    "Unit_Price",
    "Revenue",
    "Sales_Rep",
    "Status",
]


def validate_schema(df):
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def build_exception_report(df):
    exceptions = []

    # Duplicate transaction IDs
    duplicate_mask = df.duplicated(
        subset=["Transaction_ID"],
        keep=False
    )

    for idx in df[duplicate_mask].index:
        exceptions.append(
            {
                "Row_Index": idx,
                "Transaction_ID": df.loc[idx, "Transaction_ID"],
                "Issue": "Duplicate Transaction ID",
            }
        )

    # Missing customer
    missing_customer = (
        df["Customer"].isna()
        | df["Customer"].astype(str).str.strip().eq("")
    )

    for idx in df[missing_customer].index:
        exceptions.append(
            {
                "Row_Index": idx,
                "Transaction_ID": df.loc[idx, "Transaction_ID"],
                "Issue": "Missing Customer",
            }
        )

    # Missing sales rep
    missing_rep = (
        df["Sales_Rep"].isna()
        | df["Sales_Rep"].astype(str).str.strip().eq("")
    )

    for idx in df[missing_rep].index:
        exceptions.append(
            {
                "Row_Index": idx,
                "Transaction_ID": df.loc[idx, "Transaction_ID"],
                "Issue": "Missing Sales Rep",
            }
        )

    # Invalid dates
    parsed_dates = pd.to_datetime(
        df["Transaction_Date"],
        errors="coerce"
    )

    invalid_date = parsed_dates.isna()

    for idx in df[invalid_date].index:
        exceptions.append(
            {
                "Row_Index": idx,
                "Transaction_ID": df.loc[idx, "Transaction_ID"],
                "Issue": "Invalid Transaction Date",
            }
        )

    # Invalid quantity
    quantity = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    invalid_quantity = quantity.isna() | quantity.le(0)

    for idx in df[invalid_quantity].index:
        exceptions.append(
            {
                "Row_Index": idx,
                "Transaction_ID": df.loc[idx, "Transaction_ID"],
                "Issue": "Invalid Quantity",
            }
        )

    # Invalid revenue
    revenue = pd.to_numeric(
        df["Revenue"],
        errors="coerce"
    )

    invalid_revenue = revenue.isna() | revenue.lt(0)

    for idx in df[invalid_revenue].index:
        exceptions.append(
            {
                "Row_Index": idx,
                "Transaction_ID": df.loc[idx, "Transaction_ID"],
                "Issue": "Invalid Revenue",
            }
        )

    return pd.DataFrame(exceptions)
