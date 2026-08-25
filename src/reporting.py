import os
from datetime import datetime

import pandas as pd

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output_examples"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# SUMMARY TABLES
# ============================================================

def build_summary(df):
    completed = df[
        df["Status"].str.lower().eq("completed")
    ].copy()

    total_revenue = completed["Revenue"].sum()

    average_transaction = (
        completed["Revenue"].mean()
        if len(completed) > 0
        else 0
    )

    summary = [
        ("Total Revenue", total_revenue),
        ("Completed Transactions", len(completed)),
        ("Average Transaction Value", average_transaction),
        ("Unique Customers", df["Customer"].nunique()),
        ("Locations", df["Location"].nunique()),
        ("Total Reporting Records", len(df)),
    ]

    return pd.DataFrame(
        summary,
        columns=["Metric", "Value"]
    )


def build_location_summary(df):
    result = (
        df.groupby("Location", dropna=False)
        .agg(
            Transactions=("Transaction_ID", "count"),
            Revenue=("Revenue", "sum"),
            Customers=("Customer", "nunique"),
        )
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    return result


def build_product_summary(df):
    result = (
        df.groupby("Product_Service", dropna=False)
        .agg(
            Transactions=("Transaction_ID", "count"),
            Revenue=("Revenue", "sum"),
            Quantity=("Quantity", "sum"),
        )
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    return result


def build_monthly_summary(df):
    temp = df.copy()

    temp = temp[temp["Transaction_Date"].notna()].copy()

    temp["Month"] = (
        temp["Transaction_Date"]
        .dt.to_period("M")
        .astype(str)
    )

    result = (
        temp.groupby("Month")
        .agg(
            Transactions=("Transaction_ID", "count"),
            Revenue=("Revenue", "sum"),
        )
        .reset_index()
        .sort_values("Month")
    )

    return result


# ============================================================
# EXCEL FORMATTING HELPERS
# ============================================================

def set_standard_column_widths(worksheet, widths):
    for col_num, width in widths.items():
        worksheet.set_column(
            col_num,
            col_num,
            width
        )


def add_table(
    worksheet,
    df,
    start_row,
    start_col,
    table_name
):
    if df.empty:
        return

    end_row = start_row + len(df)
    end_col = start_col + len(df.columns) - 1

    worksheet.add_table(
        start_row,
        start_col,
        end_row,
        end_col,
        {
            "name": table_name,
            "columns": [
                {"header": col}
                for col in df.columns
            ],
            "style": "Table Style Medium 2",
        }
    )


# ============================================================
# MAIN EXPORT
# ============================================================

def export_reports(
    cleaned_df,
    valid_df,
    exceptions_df,
    file_summary_df,
):
    report_path = os.path.join(
        OUTPUT_DIR,
        "Management_Report.xlsx"
    )

    cleaned_csv_path = os.path.join(
        OUTPUT_DIR,
        "Cleaned_Data.csv"
    )

    exception_csv_path = os.path.join(
        OUTPUT_DIR,
        "Exceptions.csv"
    )

    # --------------------------------------------------------
    # CSV OUTPUTS
    # --------------------------------------------------------

    cleaned_df.to_csv(
        cleaned_csv_path,
        index=False
    )

    exceptions_df.to_csv(
        exception_csv_path,
        index=False
    )

    # --------------------------------------------------------
    # SUMMARY DATA
    # --------------------------------------------------------

    summary_df = build_summary(valid_df)
    location_df = build_location_summary(valid_df)
    product_df = build_product_summary(valid_df)
    monthly_df = build_monthly_summary(valid_df)

    report_generated = datetime.now()

    min_date = valid_df["Transaction_Date"].min()
    max_date = valid_df["Transaction_Date"].max()

    if pd.notna(min_date) and pd.notna(max_date):
        reporting_period = (
            f"{min_date:%b %Y} - "
            f"{max_date:%b %Y}"
        )
    else:
        reporting_period = "Not Available"

    # --------------------------------------------------------
    # BUILD EXCEL WORKBOOK
    # --------------------------------------------------------

    with pd.ExcelWriter(
        report_path,
        engine="xlsxwriter"
    ) as writer:

        workbook = writer.book

        # ====================================================
        # FORMATS
        # ====================================================

        title_format = workbook.add_format({
            "bold": True,
            "font_size": 20,
            "font_color": "#0F3D2E",
        })

        subtitle_format = workbook.add_format({
            "font_size": 10,
            "font_color": "#66706C",
        })

        section_format = workbook.add_format({
            "bold": True,
            "font_size": 12,
            "font_color": "#1F2937",
            "bottom": 1,
            "bottom_color": "#E2E8E5",
        })

        metric_label_format = workbook.add_format({
            "bold": True,
            "font_color": "#66706C",
        })

        metric_number_format = workbook.add_format({
            "bold": True,
            "font_size": 14,
            "font_color": "#0F3D2E",
            "num_format": "#,##0",
        })

        metric_currency_format = workbook.add_format({
            "bold": True,
            "font_size": 14,
            "font_color": "#0F3D2E",
            "num_format": "$#,##0.00",
        })

        currency_format = workbook.add_format({
            "num_format": "$#,##0.00",
        })

        integer_format = workbook.add_format({
            "num_format": "#,##0",
        })

        date_format = workbook.add_format({
            "num_format": "yyyy-mm-dd",
        })

        exception_format = workbook.add_format({
            "bg_color": "#FDECEC",
            "font_color": "#9B1C1C",
        })

        # ====================================================
        # EXECUTIVE SUMMARY
        # ====================================================

        summary_sheet = workbook.add_worksheet(
            "Executive Summary"
        )

        writer.sheets["Executive Summary"] = summary_sheet

        summary_sheet.hide_gridlines(2)

        summary_sheet.write(
            "A1",
            "LIGNUM AUTOMATION"
        )

        summary_sheet.write(
            "A2",
            "Automated Business Reporting Pipeline",
            title_format
        )

        summary_sheet.write(
            "A3",
            f"Reporting Period: {reporting_period}",
            subtitle_format
        )

        summary_sheet.write(
            "A4",
            f"Generated: {report_generated:%Y-%m-%d %H:%M}",
            subtitle_format
        )

        summary_sheet.write(
            "A6",
            "EXECUTIVE SUMMARY",
            section_format
        )

        summary_map = dict(
            zip(
                summary_df["Metric"],
                summary_df["Value"]
            )
        )

        metrics = [
            (
                "A8",
                "B8",
                "Total Revenue",
                summary_map.get("Total Revenue", 0),
                metric_currency_format,
            ),
            (
                "D8",
                "E8",
                "Completed Transactions",
                summary_map.get(
                    "Completed Transactions",
                    0
                ),
                metric_number_format,
            ),
            (
                "A11",
                "B11",
                "Average Transaction Value",
                summary_map.get(
                    "Average Transaction Value",
                    0
                ),
                metric_currency_format,
            ),
            (
                "D11",
                "E11",
                "Unique Customers",
                summary_map.get(
                    "Unique Customers",
                    0
                ),
                metric_number_format,
            ),
            (
                "A14",
                "B14",
                "Locations",
                summary_map.get(
                    "Locations",
                    0
                ),
                metric_number_format,
            ),
            (
                "D14",
                "E14",
                "Reporting Records",
                summary_map.get(
                    "Total Reporting Records",
                    0
                ),
                metric_number_format,
            ),
        ]

        for (
            label_cell,
            value_cell,
            label,
            value,
            value_format
        ) in metrics:

            summary_sheet.write(
                label_cell,
                label,
                metric_label_format
            )

            summary_sheet.write(
                value_cell,
                value,
                value_format
            )

        # ----------------------------------------------------
        # LOCATION TABLE
        # ----------------------------------------------------

        summary_sheet.write(
            "A18",
            "LOCATION PERFORMANCE",
            section_format
        )

        location_start_row = 19

        location_df.to_excel(
            writer,
            sheet_name="Executive Summary",
            startrow=location_start_row,
            startcol=0,
            index=False
        )

        add_table(
            summary_sheet,
            location_df,
            location_start_row,
            0,
            "LocationPerformance"
        )

        revenue_col_index = (
            location_df.columns.get_loc("Revenue")
        )

        summary_sheet.set_column(
            revenue_col_index,
            revenue_col_index,
            16,
            currency_format
        )

        # ----------------------------------------------------
        # LOCATION CHART
        # ----------------------------------------------------

        if not location_df.empty:

            chart = workbook.add_chart({
                "type": "column"
            })

            chart.add_series({
                "name": "Revenue by Location",
                "categories": [
                    "Executive Summary",
                    location_start_row + 1,
                    0,
                    location_start_row + len(location_df),
                    0,
                ],
                "values": [
                    "Executive Summary",
                    location_start_row + 1,
                    revenue_col_index,
                    location_start_row + len(location_df),
                    revenue_col_index,
                ],
            })

            chart.set_title({
                "name": "Revenue by Location"
            })

            chart.set_y_axis({
                "num_format": "$#,##0"
            })

            chart.set_legend({
                "none": True
            })

            chart.set_style(10)

            summary_sheet.insert_chart(
                "G7",
                chart,
                {
                    "x_scale": 1.25,
                    "y_scale": 1.15,
                }
            )

        set_standard_column_widths(
            summary_sheet,
            {
                0: 28,
                1: 18,
                2: 15,
                3: 28,
                4: 18,
            }
        )

        summary_sheet.freeze_panes(6, 0)

        # ====================================================
        # LOCATION PERFORMANCE
        # ====================================================

        location_df.to_excel(
            writer,
            sheet_name="Location Performance",
            index=False
        )

        ws_location = writer.sheets[
            "Location Performance"
        ]

        ws_location.hide_gridlines(2)

        add_table(
            ws_location,
            location_df,
            0,
            0,
            "LocationPerformanceDetail"
        )

        ws_location.set_column(
            0,
            0,
            22
        )

        ws_location.set_column(
            1,
            1,
            16,
            integer_format
        )

        ws_location.set_column(
            2,
            2,
            18,
            currency_format
        )

        ws_location.set_column(
            3,
            3,
            16,
            integer_format
        )

        ws_location.freeze_panes(1, 0)

        # ====================================================
        # PRODUCT PERFORMANCE
        # ====================================================

        product_df.to_excel(
            writer,
            sheet_name="Product Performance",
            index=False
        )

        ws_product = writer.sheets[
            "Product Performance"
        ]

        ws_product.hide_gridlines(2)

        add_table(
            ws_product,
            product_df,
            0,
            0,
            "ProductPerformanceDetail"
        )

        ws_product.set_column(
            0,
            0,
            24
        )

        ws_product.set_column(
            1,
            1,
            16,
            integer_format
        )

        ws_product.set_column(
            2,
            2,
            18,
            currency_format
        )

        ws_product.set_column(
            3,
            3,
            14,
            integer_format
        )

        ws_product.freeze_panes(1, 0)

        # ====================================================
        # MONTHLY TREND
        # ====================================================

        monthly_df.to_excel(
            writer,
            sheet_name="Monthly Trend",
            index=False
        )

        ws_monthly = writer.sheets[
            "Monthly Trend"
        ]

        ws_monthly.hide_gridlines(2)

        add_table(
            ws_monthly,
            monthly_df,
            0,
            0,
            "MonthlyTrendDetail"
        )

        ws_monthly.set_column(
            0,
            0,
            14
        )

        ws_monthly.set_column(
            1,
            1,
            16,
            integer_format
        )

        ws_monthly.set_column(
            2,
            2,
            18,
            currency_format
        )

        if not monthly_df.empty:

            trend_chart = workbook.add_chart({
                "type": "line"
            })

            trend_chart.add_series({
                "name": "Monthly Revenue",
                "categories": [
                    "Monthly Trend",
                    1,
                    0,
                    len(monthly_df),
                    0,
                ],
                "values": [
                    "Monthly Trend",
                    1,
                    2,
                    len(monthly_df),
                    2,
                ],
                "marker": {
                    "type": "circle"
                },
            })

            trend_chart.set_title({
                "name": "Monthly Revenue Trend"
            })

            trend_chart.set_y_axis({
                "num_format": "$#,##0"
            })

            trend_chart.set_legend({
                "none": True
            })

            ws_monthly.insert_chart(
                "E2",
                trend_chart,
                {
                    "x_scale": 1.25,
                    "y_scale": 1.15,
                }
            )

        # ====================================================
        # EXCEPTIONS
        # ====================================================

        exceptions_df.to_excel(
            writer,
            sheet_name="Exceptions",
            index=False
        )

        ws_exceptions = writer.sheets[
            "Exceptions"
        ]

        ws_exceptions.hide_gridlines(2)

        if not exceptions_df.empty:

            add_table(
                ws_exceptions,
                exceptions_df,
                0,
                0,
                "ExceptionDetail"
            )

            ws_exceptions.conditional_format(
                1,
                0,
                len(exceptions_df),
                len(exceptions_df.columns) - 1,
                {
                    "type": "no_errors",
                    "format": exception_format,
                }
            )

        ws_exceptions.set_column(
            0,
            len(exceptions_df.columns) - 1
            if len(exceptions_df.columns) > 0
            else 0,
            24
        )

        ws_exceptions.freeze_panes(1, 0)

        # ====================================================
        # PROCESSING LOG
        # ====================================================

        file_summary_df.to_excel(
            writer,
            sheet_name="Processing Log",
            index=False
        )

        ws_log = writer.sheets[
            "Processing Log"
        ]

        ws_log.hide_gridlines(2)

        add_table(
            ws_log,
            file_summary_df,
            0,
            0,
            "ProcessingLog"
        )

        ws_log.set_column(
            0,
            0,
            34
        )

        ws_log.set_column(
            1,
            1,
            12
        )

        ws_log.set_column(
            2,
            2,
            30
        )

        # ====================================================
        # CLEAN DATA
        # ====================================================

        valid_df.to_excel(
            writer,
            sheet_name="Clean Data",
            index=False
        )

        ws_clean = writer.sheets[
            "Clean Data"
        ]

        ws_clean.hide_gridlines(2)

        add_table(
            ws_clean,
            valid_df,
            0,
            0,
            "CleanData"
        )

        ws_clean.freeze_panes(1, 0)

        # Set reasonable widths
        for i, column in enumerate(
            valid_df.columns
        ):
            width = max(
                12,
                min(
                    30,
                    max(
                        len(str(column)) + 2,
                        valid_df[column]
                        .astype(str)
                        .str.len()
                        .max()
                        + 2
                        if not valid_df.empty
                        else 12
                    )
                )
            )

            ws_clean.set_column(
                i,
                i,
                width
            )

        # Apply formats to known columns
        if "Revenue" in valid_df.columns:
            idx = valid_df.columns.get_loc(
                "Revenue"
            )
            ws_clean.set_column(
                idx,
                idx,
                16,
                currency_format
            )

        if "Unit_Price" in valid_df.columns:
            idx = valid_df.columns.get_loc(
                "Unit_Price"
            )
            ws_clean.set_column(
                idx,
                idx,
                14,
                currency_format
            )

        if "Quantity" in valid_df.columns:
            idx = valid_df.columns.get_loc(
                "Quantity"
            )
            ws_clean.set_column(
                idx,
                idx,
                12,
                integer_format
            )

        if "Transaction_Date" in valid_df.columns:
            idx = valid_df.columns.get_loc(
                "Transaction_Date"
            )
            ws_clean.set_column(
                idx,
                idx,
                14,
                date_format
            )

    return {
        "report": report_path,
        "cleaned_csv": cleaned_csv_path,
        "exceptions_csv": exception_csv_path,
    }