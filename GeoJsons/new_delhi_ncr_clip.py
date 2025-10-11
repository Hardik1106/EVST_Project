import geopandas as gpd

# Load the full India district GeoJSON
india = gpd.read_file("output.geojson")

# 🔹 Define all Delhi NCR districts using dtname
ncr_districts_list = [
    # Delhi districts
    "Central Delhi", "East Delhi", "New Delhi", "North Delhi", "North East Delhi",
    "North West Delhi", "South Delhi", "South East Delhi", "South West Delhi",
    "West", "Shahdara",

    # Haryana
    "Faridabad", "Gurugram", "Nuh", "Rohtak", "Sonipat", "Rewari",
    "Jhajjar", "Panipat", "Palwal", "Bhiwani", "Charki Dadri", "Mahendragarh", "Jind",
    "Karnal",

    # Uttar Pradesh
    "Meerut", "Ghaziabad", "Gautam Buddha Nagar", "Bulandshahr", "Baghpat",
    "Hapur", "Shamli", "Muzaffarnagar",
    
    # Rajasthan
    "Alwar", "Bharatpur"
]

# 🔹 Filter using the 'dtname' property
ncr = india[india["dtname"].isin(ncr_districts_list)]

# 🔹 Save as GeoJSON (district-wise, not dissolved)
ncr.to_file("Delhi_NCR_Districts_updated.geojson", driver="GeoJSON")

print("✅ Delhi NCR district-level GeoJSON created successfully!")