import pandas as pd
import plotly.express as px
import os
import re
import glob

print("Loading...")

# Output folder
os.makedirs("charts_html", exist_ok=True)

# Define filters you're interested in
filters_to_plot = [
    "Feeder Cattle_Bulls_Medium and Large_1_None_",
    "Feeder Cattle_Bulls_Medium and Large_2_None_",
    "Feeder Cattle_Bulls_Medium and Large_3_None_",
    "Feeder Cattle_Heifers_Medium and Large_1_None_",
    "Feeder Cattle_Heifers_Medium and Large_2_None_",
    "Feeder Cattle_Heifers_Medium and Large_3_None_",
    "Feeder Cattle_Steers_Medium and Large_1_None_",
    "Feeder Cattle_Steers_Medium and Large_2_None_",
    "Feeder Cattle_Steers_Medium and Large_3_None_",
    "Replacement Cattle_Bred Cows_Large_1-2_None_",
    "Replacement Cattle_Bred Cows_Medium and Large_1-2_None_",
    "Replacement Cattle_Bred Cows_Medium and Large_2-3_None_",
    "Replacement Cattle_Bred Cows_Small and Medium_1-2_None_",
    "Replacement Cattle_Bred Heifers_Medium and Large_1-2_None_",
    "Replacement Cattle_Cow-Calf Pairs_Medium and Large_1-2_None_",
    "Replacement Cattle_Cow-Calf Pairs_Small and Medium_1-2_None_",
    "Replacement Cattle_Cow-Calf Pairs_Small and Medium_2-3_None_",
    "Replacement Cattle_Cow-Calf Pairs_Small_3_None_",
    "Replacement Cattle_Stock Cows_Large_1-2_None_",
    "Replacement Cattle_Stock Cows_Medium and Large_1-2_None_",
    "Slaughter Cattle_Bulls_N/A_N/A_N/A_",
    "Slaughter Cattle_Cows_N/A_N/A_Boner 80-85%_",
    "Slaughter Cattle_Cows_N/A_N/A_Breaker 75-80%_",
    "Slaughter Cattle_Cows_N/A_N/A_Lean 85-90%_"
]

# Find all combined state CSV files
data_files = glob.glob("All_Sale_Barns_Combined_*.csv")

for file_path in data_files:
    # Extract state code, e.g. All_Sale_Barns_Combined_FL.csv -> FL
    state_abbr = re.search(r"All_Sale_Barns_Combined_([A-Z]{2})\.csv", file_path)
    if state_abbr:
        state_abbr = state_abbr.group(1)
    else:
        print(f"⚠️ Could not parse state from filename: {file_path}")
        continue

    print(f"Processing charts for state: {state_abbr}")

    df = pd.read_csv(file_path)

    df["date"] = pd.to_datetime(df["report_date"], errors="coerce")
    df = df.dropna(subset=["date"])
    df["week"] = df["date"] - pd.to_timedelta(df["date"].dt.weekday, unit='d')

    for base_filter in filters_to_plot:
        matching_cols = [col for col in df.columns if col.startswith(base_filter) and col.endswith("_avg_price")]

        if not matching_cols:
            print(f"⚠️ No columns found for {base_filter} in {state_abbr}")
            continue

        melted = pd.melt(
            df[["week"] + matching_cols],
            id_vars=["week"],
            value_vars=matching_cols,
            var_name="filter_weight",
            value_name="avg_price"
        )
        melted = melted.dropna(subset=["avg_price"])

        melted["weight_class"] = melted["filter_weight"].str.extract(rf"{re.escape(base_filter)}(.+)_avg_price")

        if melted["weight_class"].isna().all():
            print(f"⚠️ No weight class parsed for {base_filter} in {state_abbr}")
            continue

        melted = melted.sort_values(by=["weight_class", "week"])
        melted = melted.groupby(["week", "weight_class"], as_index=False)["avg_price"].mean()

        melted["weight_sort"] = melted["weight_class"].str.extract(r"(\d+)", expand=False).astype(float)
        weight_order = (
            melted[["weight_class", "weight_sort"]]
            .drop_duplicates()
            .sort_values("weight_sort", ascending=True)["weight_class"]
            .tolist()
        )

        clean_title = base_filter.replace('_', ' ')
        clean_title = re.sub(r'\b(None|N/A|N A)\b', '', clean_title, flags=re.IGNORECASE)
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()

        clean_filename = base_filter.replace(" ", "_")
        clean_filename = re.sub(r'[%/:]', '', clean_filename)
        clean_filename = re.sub(r'(None|N/A|N_A)', '', clean_filename, flags=re.IGNORECASE)
        clean_filename = re.sub(r'_+', '_', clean_filename).strip('_')

        # Prefix filename with state abbreviation
        output_path = f"charts_html/{state_abbr}_{clean_filename}.html"

        fig = px.line(
            melted,
            x="week",
            y="avg_price",
            color="weight_class",
            category_orders={"weight_class": weight_order},
            title=f"Weekly Avg Price by Weight: {clean_title} ({state_abbr})",
            labels={"week": "Week", "avg_price": "Average Price ($/cwt)", "weight_class": "Weight Class"},
            markers=True
        )
        fig.update_layout(
            template="plotly_white",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
            hovermode="x unified",
            legend=dict(title="Weight Class")
        )

        fig.write_html(output_path)
        print(f"✅ Saved: {output_path}")

print("✅ All interactive charts saved to the 'charts_html/' folder.")
