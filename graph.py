import matplotlib
import os

def is_interactive():
    """
    Check if the script is running in an interactive environment (e.g., Jupyter, Colab).
    This is more robust than checking for __file__ because of how %run works.
    """
    try:
        # This function is available in iPython environments (Jupyter, Colab, etc.)
        get_ipython()
        return True
    except NameError:
        # This will be the case for a standard Python script execution (e.g., in Docker)
        return False

# Use 'Agg' backend for non-interactive environments (like Docker) to run headlessly.
# In interactive environments (like Colab), the default backend allows plt.show().
if not is_interactive():
    matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
import urllib.request
import pandas as pd
import io
import sys

# Download modern font (Roboto)
font_url = 'https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf'
font_path = 'Roboto-Regular.ttf'
if not os.path.exists(font_path):
    urllib.request.urlretrieve(font_url, font_path)

fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Roboto' # Set Roboto as the default font

# --- Data Loading from CSV ---
# Read data from the CSV file
try:
    # Use a robust parser to handle potential whitespace around delimiters
    df = pd.read_csv('data.csv', sep=r'\s*,\s*', engine='python')
except FileNotFoundError:
    print("ERROR: data.csv not found. Please ensure the data file is in the same directory.")
    # In a notebook environment, exit() can terminate the cell silently.
    # Raising the exception ensures the error is visible to the user.
    raise

# Set the fuel type as the index
# Dynamically determine the index column from the first column of the CSV.
index_col_name = df.columns[0]
df = df.set_index(index_col_name)

# Dynamically get years from column headers
years = df.columns.tolist()

# Get the order of fuel types directly from the CSV file's first column (now the DataFrame index).
# This removes the redundant hardcoded list and makes the script more maintainable.
order = df.index.tolist()
# Convert the DataFrame to the dictionary format expected by the plotting code
data = df.T.to_dict('list')

colors = {
    'BEV': 'blue',
    'Hybrid': '#2ca02c',
    'Brennstoffzelle': '#17becf',
    'Gas': '#ff7f0e',
    'Benzin': '#d62728',
    'Diesel': '#383e42'
}

fig, ax1 = plt.subplots(figsize=(12, 7))
ax2 = ax1.twinx()

# Plot lines
for col in order:
    if col == 'Diesel':
        ax2.plot(years, data[col], marker='o', color=colors[col], label=col, linewidth=2.5)
    else:
        ax1.plot(years, data[col], marker='o', color=colors[col], label=col, linewidth=2.5)

# Axis labels
ax1.set_ylabel('Neuzulassungen (ohne Diesel)')
ax2.set_ylabel('Neuzulassungen (nur Diesel)')
ax2.tick_params(axis='y', labelcolor=colors['Diesel'])

# Format y-axes with thousands separator
def format_thousands(x, pos):
    return f"{int(x):,}".replace(",", ".")

ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))

# Hide standard X-axis
ax1.set_xticks([])

# Prepare data for the table (with thousands separator)
cell_text = []
for col in order:
    cell_text.append([f"{val:,}".replace(",", ".") for val in data[col]])

# Add table
table = ax1.table(cellText=cell_text,
                  rowLabels=order,
                  colLabels=years,
                  loc='bottom',
                  cellLoc='center')

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 1.8)

# Enforce exact vertical centering and styling
for (row, col_idx), cell in table.get_celld().items():
    cell.set_text_props(va='center')
    cell.get_text().set_y(0.5)

    if col_idx == -1 and row > 0:
        col_name = order[row-1]
        cell.set_text_props(color=colors[col_name], weight='bold', ha='left')
    elif col_idx >= 0 and row > 0:
        col_name = order[row-1]
        cell.set_text_props(color=colors[col_name], weight='bold')
    elif row == 0 and col_idx >= 0:
        cell.set_text_props(weight='bold')

# Legend
lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

# Dynamically create the title based on the year range from the data
start_year = years[0]
end_year = years[-1]
title_text = f'Neuzulassungen von Sattelzugmaschinen nach Antriebsart ({start_year}-{end_year})'
plt.title(title_text, fontweight='bold', pad=20)
ax1.grid(True, axis='y', linestyle='--', alpha=0.6)

# Adjust spacing
plt.subplots_adjust(bottom=0.34)

# Source information
plt.figtext(0.9, 0.03, "Daten: Kraftfahrt-Bundesamt, 03/2026 | Grafik: Eike, lizenziert unter CC0 1.0",
            ha="right", va="bottom", fontsize=9, color="gray")

# In interactive environments (like Colab), display the plot.
if is_interactive():
    plt.show()
else:
    # In non-interactive environments (like Docker), write the image to standard output.
    # This allows the calling process to redirect the output to a file, avoiding
    # filesystem and permission issues with mounted volumes.
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300, facecolor='white')
    buffer.seek(0)
    sys.stdout.buffer.write(buffer.getvalue())
    # Print status message to stderr, as stdout is used for the image data.
    print("Graph data successfully written to standard output.", file=sys.stderr)
