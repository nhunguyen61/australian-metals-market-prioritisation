# clean.py
# Rebuilt ABS SITC68 cleaning pipeline placeholder.
from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUT = PROJECT_DIR / "data" / "clean"
OUT.mkdir(parents=True, exist_ok=True)

def clean_exports(input_file):
    df = pd.read_csv(input_file)
    df["date"] = pd.to_datetime(df["date"])
    df["value_aud_m"] = df["value_aud_m"]
    df = df[df["sitc_code"].astype(str).str.startswith("68")]
    df.to_csv(OUT / "exports_tidy.csv", index=False)

if __name__ == "__main__":
    print("Run clean_exports() with ABS raw CSV input.")
