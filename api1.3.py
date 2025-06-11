import requests
import pandas as pd
import os

# === Change this to get your information ===
slug_ids = ['1418', '1608', '1419', '1607', '1420', '1424', '1609', '1422', '1423']   # Add as many as you like
timeperiod = 'q=report_begin_date=06/06/2022:06/03/2025'
save_folder = "."

# Function to fetch and process report data for a given slug_id and time period
def process_slug(slug_id, timeperiod, save_folder="."):
    # Construct API URL
    api_key = 'N/KUHW09nFDKpw8mkA5qDQyXwgbfKhqmp/Y/thtybGo='
    url = f'https://marsapi.ams.usda.gov/services/v1.2/reports/{slug_id}?{timeperiod}'

    # Pull and parse data
    response = requests.get(url, auth=(api_key, ''))
    data = response.json()
    df = pd.json_normalize(data['results'])

    if df.empty:
        print(f"No data returned for slug ID {slug_id}")
        return

    # Drop unnecessary columns
    df.drop(columns=['report_begin_date', 'report_end_date', 'published_date'], inplace=True, errors='ignore')

    # Adding 100 pound weight class
    df['weight_class'] = pd.cut(
    df['avg_weight'],
    bins=range(0, 2001, 100),  # 0-99, 100–199, ..., 1900–1999
    right=False,
    labels=[f"{i}-{i+99}" for i in range(0, 2000, 100)]
)

    # Create class identifier
    df['class_id'] = df[['commodity', 'class', 'frame', 'muscle_grade', 'quality_grade_name', 'weight_class']].astype(str).agg('_'.join, axis=1)

    # Select value columns to pivot
    value_columns = [
        'head_count', 'avg_weight_min', 'avg_weight_max', 'avg_weight',
        'avg_price_min', 'avg_price_max', 'avg_price',
        'weight_break_low', 'weight_break_high',
        'receipts', 'receipts_week_ago', 'receipts_year_ago'
    ]

    # Pivot data by report_date and class
    pivot_df = df.pivot_table(index='report_date', columns='class_id', values=value_columns, aggfunc='first')
    pivot_df.columns = [f"{col[1]}_{col[0]}" for col in pivot_df.columns]
    pivot_df.reset_index(inplace=True)

    # Keep metadata
    meta_cols = [
        'report_date', 'office_name', 'office_state', 'office_city', 'office_code',
        'market_type', 'market_type_category', 'market_location_name', 'market_location_state',
        'market_location_city', 'slug_id', 'slug_name', 'report_title', 'group',
        'category', 'report_narrative', 'final_ind'
    ]
    meta_df = df[meta_cols].drop_duplicates(subset='report_date')

    # Merge metadata and pivoted data
    final_df = pd.merge(meta_df, pivot_df, on='report_date', how='left')

    # Save final output
    output_file = os.path.join(save_folder, f"Sale Barn {slug_id}.csv")
    final_df.to_csv(output_file, index=False)
    print(f"Saved to '{output_file}'")

for slug in slug_ids:
    process_slug(slug, timeperiod)
# Combine all output CSVs into one master file
combined_df = pd.DataFrame()

for slug in slug_ids:
    file_path = os.path.join(save_folder, f"Sale Barn {slug}.csv")
    if os.path.exists(file_path):
        temp_df = pd.read_csv(file_path)
        temp_df['source_slug'] = slug  # Optional: track origin
        combined_df = pd.concat([combined_df, temp_df], ignore_index=True)

# Save the combined CSV
combined_df.to_csv(os.path.join(save_folder, "All_Sale_Barns_Combined.csv"), index=False)
print("Combined file saved as 'All_Sale_Barns_Combined.csv'")
