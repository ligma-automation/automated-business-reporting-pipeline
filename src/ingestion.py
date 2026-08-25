import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, "sample_data")


def read_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        return pd.read_csv(file_path)

    if ext in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    return None


def load_all_files():
    all_frames = []
    file_summary = []

    for filename in sorted(os.listdir(INPUT_DIR)):
        file_path = os.path.join(INPUT_DIR, filename)

        if not os.path.isfile(file_path):
            continue

        ext = os.path.splitext(filename)[1].lower()

        if ext not in [".csv", ".xlsx", ".xls"]:
            continue

        try:
            df = read_file(file_path)

            if df is None:
                continue

            df["Source_File"] = filename

            all_frames.append(df)

            file_summary.append(
                {
                    "File": filename,
                    "Rows": len(df),
                    "Status": "Loaded",
                }
            )

        except Exception as exc:
            file_summary.append(
                {
                    "File": filename,
                    "Rows": 0,
                    "Status": f"Failed: {exc}",
                }
            )

    if not all_frames:
        raise ValueError("No valid CSV or Excel files were loaded.")

    combined = pd.concat(all_frames, ignore_index=True)

    return combined, pd.DataFrame(file_summary)


if __name__ == "__main__":
    combined_df, summary_df = load_all_files()

    print("\nFILES LOADED")
    print(summary_df.to_string(index=False))

    print("\nTOTAL ROWS:", len(combined_df))