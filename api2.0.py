import requests
import pandas as pd
import os

timeperiod = 'q=report_begin_date=08/14/2024:08/14/2025'
save_folder = "."

def process_slug(slug_id, timeperiod, save_folder="."):
    api_key = 'Your Key Here'
    url = f'https://marsapi.ams.usda.gov/services/v1.2/reports/{slug_id}?{timeperiod}'
    response = requests.get(url, auth=(api_key, ''))
    data = response.json()
    df = pd.json_normalize(data['results'])

    if df.empty:
        print(f"No data returned for slug ID {slug_id}")
        return None

    df.drop(columns=['report_begin_date', 'report_end_date', 'published_date'], inplace=True, errors='ignore')

    df['weight_class'] = pd.cut(
        df['avg_weight'],
        bins=range(0, 3001, 100),
        right=False,
        labels=[f"{i}-{i+99}" for i in range(0, 3000, 100)]
    )

    df['class_id'] = df[['commodity', 'class', 'frame', 'muscle_grade', 'quality_grade_name', 'weight_class']].astype(str).agg('_'.join, axis=1)

    value_columns = [
        'head_count', 'avg_weight_min', 'avg_weight_max', 'avg_weight',
        'avg_price_min', 'avg_price_max', 'avg_price',
        'weight_break_low', 'weight_break_high',
        'receipts', 'receipts_week_ago', 'receipts_year_ago'
    ]

    pivot_df = df.pivot_table(index='report_date', columns='class_id', values=value_columns, aggfunc='first')
    pivot_df.columns = [f"{col[1]}_{col[0]}" for col in pivot_df.columns]
    pivot_df.reset_index(inplace=True)

    meta_cols = [
        'report_date', 'office_name', 'office_state', 'office_city', 'office_code',
        'market_type', 'market_type_category', 'market_location_name', 'market_location_state',
        'market_location_city', 'slug_id', 'slug_name', 'report_title', 'group',
        'category', 'report_narrative', 'final_ind'
    ]
    meta_df = df[meta_cols].drop_duplicates(subset='report_date')

    final_df = pd.merge(meta_df, pivot_df, on='report_date', how='left')
    return final_df

# Slug IDs by state
state_slug_ids = {
    "AL": [
        '1995','1991','1979','2003','1989','1986','2001','1996','1993','1984','1988',
        '2029','2007','1985','2031','1999','2032','1998','2033','2000','1997','1987','2034'
    ],
    "AR": [
        '2052','2059','2051','1684','3475','2055','2057','2058','2053','2050','2054'
    ],
    "FL": [
        '1418','1608','1419','1607','1420','1424','1609','1422','1423'
    ],
    "GA": [
        '1946','1949','1948','1930','1935','1936','1942','1943','1940','1937','1941','1947',
        '1934','1945','1931','1938','1939','1944'
    ],
    "NC": [
        '2095','2087','2092','2088','2083','2094','2093','2089','2090'
    ],
    "SC": [
        '1960','1959','1956','1964','1961','1958'
    ],
    "MS": [
        '2117','2125','2124','2126','2120','2122','2112','2123','2116','2113','2114','2118','2119'
    ],
    "TN": [
        '2060','2061','2064','2070','2068','2066','2069','2062','2065','2067','2079'
    ]
}

for state, slugs in state_slug_ids.items():
    combined_df = pd.DataFrame()
    print(f"Processing state {state} with {len(slugs)} slug IDs")

    for slug in slugs:
        df = process_slug(slug, timeperiod, save_folder)
        if df is not None:
            df['source_slug'] = slug
            df['state'] = state
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    output_file = os.path.join(save_folder, f"All_Sale_Barns_Combined_{state}.csv")
    combined_df.to_csv(output_file, index=False)
    print(f"Saved combined data for {state} to '{output_file}'")
