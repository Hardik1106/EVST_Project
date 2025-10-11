import pandas as pd

# Load your DataFrame
df = pd.read_csv('./2011-IndiaStateDistSbDist-0000.csv')

# Specify the row numbers you want to select (0-based indexing)
index = 2634

row_numbers = [index, index + 1, index + 2]  # <-- Replace with your desired row numbers

# Select the rows
selected_rows = df.iloc[row_numbers]

# Select only required columns
columns_needed = ['Level', 'Name','TRU', 'TOT_P', 'TOT_M', 'TOT_F', 'P_06', 'M_06', 'F_06']
selected_rows = selected_rows[columns_needed]

# Save to CSV
selected_rows.to_csv('selected_rows_population.csv', index=False)
print("Selected rows saved to selected_rows_population.csv")