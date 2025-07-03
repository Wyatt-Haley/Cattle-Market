import os

# Set the folder where your Plotly HTML charts are saved
chart_dir = "charts_html"

# Get all .html files in that folder
html_files = sorted([f for f in os.listdir(chart_dir) if f.endswith(".html")])

# Print the JavaScript array
print("const chartFiles = [")
for f in html_files:
    print(f'  "{chart_dir}/{f}",')
print("];")
