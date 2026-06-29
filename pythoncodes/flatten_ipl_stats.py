import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_CSV = PROJECT_ROOT / "raw_data" / "CSK_BATTING_FILE.csv"     # change per file, or loop over a list
OUTPUT_CSV = PROJECT_ROOT /"CSK_BATTING_FILE_flattened.csv"
STATS_COLUMN = "ipl_stats"


def parse_stats(value):
    if pd.isna(value) or not str(value).strip():
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}


def flatten_ipl_stats(input_csv, output_csv, stats_column=STATS_COLUMN):
    df = pd.read_csv(input_csv)

    stats_df = df[stats_column].apply(parse_stats).apply(pd.Series)

    result = pd.concat([df.drop(columns=[stats_column]), stats_df], axis=1)
    result.to_csv(output_csv, index=False)
    print(f"Wrote {len(result)} rows, {len(stats_df.columns)} new stat columns -> {output_csv}")


if __name__ == "__main__":
    flatten_ipl_stats(INPUT_CSV, OUTPUT_CSV)
