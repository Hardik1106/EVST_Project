import pandas as pd

# Load your DataFrame
df = pd.read_csv('./District_Wise_Population.csv')

district_list = [
    'Gautam Buddha Nagar', 'Ghaziabad', 'Baghpat', 'Bulandshahr', 'Meerut',
    'Muzaffarnagar', 'New Delhi', 'West', 'Panipat', 'Palwal', 'Rewari',
    'Gurgaon', 'Sonipat', 'Bhiwani', 'Jind', 'Jhajjar', 'Mahendragarh',
    'Rohtak', 'Karnal', 'Faridabad', 'Mewat', 'Alwar', 'Bharatpur', 'Dadri', 
    'Shahdara', 'North East', 'Hapur', 'Shamli', 'Gurugram', 'Nuh', 
    'Dadri', 'North West', 'North', 'Central', 
    'East', 'South', 'South West', 'West', 'South East'
]

# Filter rows
filtered_df = df[
    ((df['Level'] == 'DISTRICT') &
    (
        (df['State'] == '07') |
        (df['Name'].isin(district_list)) |
        (df['District'] == 142) | 
        (df['District'] == 87) | 
        (df['District'] == 89) |
        (df['District'] == 140)
    ))
    |
    ((df['Level'] == 'SUB-DISTRICT') &
    (
        (df['Name']== "Dadri")) |
        (df['Subdistt'] == 437) |
        (df['Subdistt'] == 402)
    )

]

# Select only required columns
columns_needed = ['Level', 'Name','TRU', 'TOT_P', 'TOT_M', 'TOT_F', 'P_06', 'M_06', 'F_06']
filtered_df = filtered_df[columns_needed]

# --- Fix names so directions have 'Delhi' at the end ---
def fix_delhi_names(name):
    directions = [
        'West', 'East', 'North', 'South', 'Central', 'North West', 'North East',
        'South West', 'South East'
    ]
    name_strip = name.strip()
    for direction in directions:
        # Match exact direction or direction with space
        if name_strip.lower() == direction.lower() or name_strip.lower() == direction.lower().replace(' ', ''):
            return f"{direction} Delhi"
        # For names like 'West', 'East', etc. (not already ending with Delhi)
        if name_strip.lower().startswith(direction.lower()) and not name_strip.lower().endswith('delhi'):
            return f"{direction} Delhi"
    return name_strip

filtered_df['Name'] = filtered_df['Name'].apply(fix_delhi_names)

# Save to CSV
filtered_df.to_csv('NCR_District_Wise_Population.csv', index=False)