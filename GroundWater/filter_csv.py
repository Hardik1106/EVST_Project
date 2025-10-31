import pandas as pd

# List of NCR districts
ncr_districts = {
    "New Delhi", "Central Delhi", "East Delhi", "North Delhi", 
    "North East Delhi", "North West Delhi", "Shahdara", "South Delhi", 
    "South East Delhi", "South West Delhi", "West Delhi",
    "Bhiwani", "Charkhi Dadri", "Faridabad", "Gurugram", "Gurgaon", 
    "Jhajjar", "Jind", "Karnal", "Mahendragarh", "Nuh", "Mewat", 
    "Palwal", "Panipat", "Rewari", "Rohtak", "Sonipat",
    "Baghpat", "Bulandshahr", "Gautam Buddha Nagar", "Ghaziabad", 
    "Hapur", "Meerut", "Muzaffarnagar", "Shamli",
    "Alwar", "Bharatpur", "Shamli", "Mewat", "Gurgaon", "Hapur", "Gautambuddhanagar", "West"
}

# Read the CSV
df = pd.read_csv("../Data/EST Data - Jatin/cgwb-changes-in-depth-to-water-level.csv")

# Filter rows where district_name matches (case-insensitive)
filtered_df = df[df['district_name'].str.title().isin(ncr_districts)]

# Save the filtered CSV
filtered_df.to_csv("filtered_ncr_districts.csv", index=False)