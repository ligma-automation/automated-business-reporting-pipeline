from ingestion import load_all_files
from validation import validate_schema, build_exception_report
from cleaning import clean_data, get_valid_records
from reporting import export_reports


def main():
    print("\n" + "=" * 60)
    print("LIGNUM AUTOMATION - BUSINESS REPORTING PIPELINE")
    print("=" * 60)

    print("\n1. Loading files...")
    raw_df, file_summary_df = load_all_files()

    print(file_summary_df.to_string(index=False))
    print(f"\nRaw Rows: {len(raw_df):,}")

    print("\n2. Validating schema...")
    validate_schema(raw_df)
    print("Schema validation passed.")

    print("\n3. Detecting data-quality issues...")
    exceptions_df = build_exception_report(raw_df)
    print(
        f"Exceptions Detected: "
        f"{len(exceptions_df):,}"
    )

    print("\n4. Cleaning data...")
    cleaned_df = clean_data(raw_df)

    valid_df = get_valid_records(cleaned_df)

    print(f"Cleaned Rows: {len(cleaned_df):,}")
    print(f"Valid Reporting Rows: {len(valid_df):,}")

    print("\n5. Generating outputs...")

    outputs = export_reports(
        cleaned_df=cleaned_df,
        valid_df=valid_df,
        exceptions_df=exceptions_df,
        file_summary_df=file_summary_df,
    )

    print("\nOUTPUTS CREATED")

    for name, path in outputs.items():
        print(f"✓ {name}: {path}")

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
