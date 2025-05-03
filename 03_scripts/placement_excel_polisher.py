import pandas as pd
import numpy as np
import os

def polish_final_dataframe(df: pd.DataFrame, sheet_name: str, report: dict) -> pd.DataFrame:
    original_rows = len(df)
    report[sheet_name] = {
        "original_rows": original_rows
    }

    # Clean column names
    df.columns = [
        col.strip().replace("\n", " ").replace("\xa0", " ").replace("  ", " ")
        for col in df.columns
    ]

    # Strip text values
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Convert numeric-looking strings to numbers
    for col in df.columns:
        if df[col].dtype == object:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                pass

    # Drop rows where all key fields are null
    df.dropna(subset=["Program", "Year", "Graduates", "Placed"], how="all", inplace=True)

    # Remove impossible placements
    if "Placement %" in df.columns:
        df = df[df["Placement %"].fillna(0) <= 100]

    # Smart remove: zero values but allow recent years
    if all(col in df.columns for col in ["Graduates", "Placed", "Higher Studies", "Year"]):
        def is_meaningful(row):
            if row["Graduates"] == 0 and row["Placed"] == 0 and row["Higher Studies"] == 0:
                year = str(row["Year"])
                return any(y in year for y in ["2022", "2021"])
            return True
        df = df[df.apply(is_meaningful, axis=1)]

    cleaned_rows = len(df)
    report[sheet_name]["cleaned_rows"] = cleaned_rows
    report[sheet_name]["removed_rows"] = original_rows - cleaned_rows

    return df


def clean_excel_file(input_path: str, output_path: str):
    excel = pd.ExcelFile(input_path)
    report = {}

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for sheet in excel.sheet_names:
            df = pd.read_excel(excel, sheet_name=sheet)
            cleaned_df = polish_final_dataframe(df, sheet, report)
            cleaned_df.to_excel(writer, index=False, sheet_name=sheet[:31])

    print(f"\n✅ Cleaned file saved to: {output_path}")
    print("\n📝 Cleaning Report:")
    for sheet, stats in report.items():
        print(f"  - {sheet}: {stats['original_rows']} → {stats['cleaned_rows']} (Removed: {stats['removed_rows']})")


# Example usage
if __name__ == "__main__":
    input_excel = r"D:\\Projects\\Not_completed\\Educational_Employment_Data_Project\\nirf_pdfs\\NIRF_Placements_Split_Yearwise.xlsx"
    output_excel = input_excel.replace(".xlsx", "_CLEANED.xlsx")
    clean_excel_file(input_excel, output_excel)
