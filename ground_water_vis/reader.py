import pandas as pd

# Read your CSV file
df = pd.read_csv('/home/arnavsharma/Arnav/UG_3.1/EST/Project/EVST_Project/ground_water_vis/filtered_ncr_districts.csv')

# Get unique district names
unique_districts = df['district_name'].unique()
print(unique_districts)