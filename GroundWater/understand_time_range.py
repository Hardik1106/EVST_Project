import pandas as pd

# Load your data into a DataFrame
df = pd.read_csv('filtered_ncr_districts.csv', parse_dates=['date'])

# By state
state_range = df.groupby('state_name')['date'].agg(['min', 'max'])

# By district (within each state)
district_range = df.groupby(['state_name', 'district_name'])['date'].agg(['min', 'max'])

print(state_range)
print(district_range)