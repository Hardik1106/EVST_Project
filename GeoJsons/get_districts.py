import geopandas as gpd

india = gpd.read_file("gadm41_IND_2.json")

# print(india["NAME_1"].unique())

# List all state / union territory names
state_name = "UttarPradesh"  # Example: change as needed

# 🔹 List all districts in Delhi (to confirm)
print(india[india["NAME_1"] == state_name]["NAME_2"].unique())