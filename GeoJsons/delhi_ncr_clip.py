import geopandas as gpd

# Load the full India district GeoJSON
india = gpd.read_file("INDIA.json")

# ✅ Corrected state name for Delhi
delhi_name = "NCTofDelhi"

# 🔹 Define all Delhi NCR districts
ncr_districts_list = [
    # Delhi districts (add all from the above printout)
    "CentralDelhi", "EastDelhi", "NewDelhi", "NorthDelhi", "NorthEastDelhi",
    "NorthWestDelhi", "SouthDelhi", "SouthEastDelhi", "SouthWestDelhi",
    "West", "Shahdara",

    # Haryana
    "Faridabad", "Gurgaon", "Nuh", "Rohtak", "Sonipat", "Rewari",
    "Jhajjar", "Panipat", "Palwal", "Bhiwani", "Charkhi Dadri", "Mahendragarh", "Jind",
    "Karnal"

    # Uttar Pradesh
    "Meerut", "Ghaziabad", "GautamBuddhaNagar", "Bulandshahr", "Baghpat",
    "Hapur", "Shamli", "Muzaffarnagar",
    
    # Rajasthan
    "Alwar", "Bharatpur"
]

# 🔹 Filter all these districts (including Delhi by NAME_1)
ncr = india[
    (india["NAME_1"] == delhi_name) |
    (india["NAME_2"].isin(ncr_districts_list)) |
    (india["GID_2"] == "IND.34.55_1") | 
    (india["GID_2"] == "IND.12.13_1")
]

# 🔹 Save as GeoJSON (district-wise, not dissolved)
ncr.to_file("Delhi_NCR_Districts.geojson", driver="GeoJSON")

print("✅ Delhi NCR district-level GeoJSON created successfully!")
