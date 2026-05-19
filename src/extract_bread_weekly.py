import re
from pathlib import Path
import pandas as pd

RAW_DIR = Path("Data_raw_weekly_reports")
OUT_PATH = Path("data/processed/bread_weekly_2025.csv")

ITEM_TO_FIND = "French Bread 32 ct"

WANTED_COLS = {
    "Actual Usage": "actual_usage",
    "Theoretical Usage": "theoretical_usage",
    "Adjusted Sales": "adjusted_sales",
    "Usage Variance": "usage_variance",
    "Usage Variance ($)": "usage_variance_$",
    "Actual UPK": "actual_upk",
    "Average UPK": "avg_upk",
    "UPK Variance": "upk_variance",
    "Actual COGS %": "actual_cogs_pct",
    "Theoretical COGS %": "theoretical_cogs_pct",
    "COGS % Variance": "cogs_pct_variance",
}

def parse_week_year(filename: str):
    m = re.search(r"Week\s*(\d{1,2})\s*[, -]?\s*(\d{4})", filename, flags=re.IGNORECASE)
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2))

def find_bread_row(df_raw: pd.DataFrame):
    # Find row with the item name
    mask = df_raw.apply(lambda col: col.astype(str).str.strip().eq(ITEM_TO_FIND)).any(axis=1)
    if not mask.any():
        return None

    item_row_idx = mask.idxmax()

    # Find header row above it containing "Item"
    header_idx = None
    start = max(0, item_row_idx - 60)
    for i in range(item_row_idx, start - 1, -1):
        row = df_raw.iloc[i].astype(str).str.strip().str.lower()
        if (row == "item").any():
            header_idx = i
            break
    if header_idx is None:
        return None

    header = df_raw.iloc[header_idx].astype(str).str.strip()
    df = df_raw.iloc[header_idx + 1 :].copy()
    df.columns = header
    df = df.reset_index(drop=True)

    # Get proper item column name (case-insensitive)
    item_col = None
    for c in df.columns:
        if str(c).strip().lower() == "item":
            item_col = c
            break
    if item_col is None:
        return None

    bread = df[df[item_col].astype(str).str.strip() == ITEM_TO_FIND]
    if bread.empty:
        return None

    return bread.iloc[0], df.columns

def extract_from_file(path: Path):
    xl = pd.ExcelFile(path)
    for sheet in xl.sheet_names:
        df_raw = xl.parse(sheet_name=sheet, header=None)
        found = find_bread_row(df_raw)
        if found is None:
            continue
        bread_row, cols = found

        out = {}
        for col_label, out_name in WANTED_COLS.items():
            if col_label in cols:
                val = bread_row[col_label]
                if isinstance(val, str):
                    val = val.replace(",", "").replace("$", "").replace("%", "").strip()
                out[out_name] = pd.to_numeric(val, errors="coerce")
            else:
                out[out_name] = pd.NA
        return out

    return None

def main():
    files = sorted(RAW_DIR.glob("*.xls*"))
    if not files:
        raise FileNotFoundError(f"No Excel files found in {RAW_DIR.resolve()}")

    rows = []
    for f in files:
        week, year = parse_week_year(f.name)
        data = extract_from_file(f)
        if data is None:
            print(f"Not found in: {f.name}")
            continue
        data["week"] = week
        data["year"] = year
        data["file"] = f.name
        rows.append(data)
        print(f"Extracted: {f.name}")

    if not rows:
        raise RuntimeError("No rows extracted. Check filenames or report format.")

    df_out = pd.DataFrame(rows).sort_values(["year", "week"]).reset_index(drop=True)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(OUT_PATH, index=False)

    print("\nSaved:", OUT_PATH)
    print(df_out.head(10))

if __name__ == "__main__":
    main()
