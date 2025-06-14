print("Loading...")

import pandas as pd
import plotly.express as px
import os
import re

# Load data
df = pd.read_csv("All_Sale_Barns_Combined.csv")

# Convert and clean date
df["date"] = pd.to_datetime(df["report_date"], errors="coerce")
df = df.dropna(subset=["date"])
df["week"] = df["date"] - pd.to_timedelta(df["date"].dt.weekday, unit='d')

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

# For each filter, find matching weight class columns and plot
for base_filter in filters_to_plot:
    matching_cols = [col for col in df.columns if col.startswith(base_filter) and col.endswith("_avg_price")]

    if not matching_cols:
        print(f"⚠️ No columns found for {base_filter}")
        continue

    # Combine data for all matching weight classes
    melted = pd.melt(
        df[["week"] + matching_cols],
        id_vars=["week"],
        value_vars=matching_cols,
        var_name="filter_weight",
        value_name="avg_price"
    )
    melted = melted.dropna(subset=["avg_price"])

    # Extract weight class (e.g., "400-499") from column name
    melted["weight_class"] = melted["filter_weight"].str.extract(rf"{re.escape(base_filter)}(.+)_avg_price")

    # Skip if extraction fails
    if melted["weight_class"].isna().all():
        print(f"⚠️ No weight class parsed for {base_filter}")
        continue

    # Sort by weight_class and week to avoid jumping lines
    melted = melted.sort_values(by=["weight_class", "week"])

    # Group by week and weight_class to get average avg_price per group
    melted = melted.groupby(["week", "weight_class"], as_index=False)["avg_price"].mean()
    
    # Sort weight_class values numerically by their lower bound, ascending
    melted["weight_sort"] = melted["weight_class"].str.extract(r"(\d+)", expand=False).astype(float)
    weight_order = (
        melted[["weight_class", "weight_sort"]]
        .drop_duplicates()
        .sort_values("weight_sort", ascending=True)["weight_class"]
        .tolist()
    )

    # Plot
    fig = px.line(
        melted,
        x="week",
        y="avg_price",
        color="weight_class",
        category_orders={"weight_class": weight_order},
        title=f"Weekly Avg Price by Weight: {base_filter}",
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

    # Clean filename
    safe_name = base_filter.replace(" ", "_").replace("/", "_").replace(":", "_")
    fig.write_html(f"charts_html/{safe_name}.html")

print("✅ All interactive charts saved to the 'charts_html/' folder.")
