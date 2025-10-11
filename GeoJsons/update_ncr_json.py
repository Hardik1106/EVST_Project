import json

# File paths
delhi_file = 'delhi_districts.json'
ncr_file = 'Delhi_NCR_Districts_updated.geojson'
output_file = 'Delhi_NCR_Districts_final.geojson'

# Load files
with open(delhi_file, 'r') as f:
    delhi_geo = json.load(f)

with open(ncr_file, 'r') as f:
    ncr_geo = json.load(f)

# Get existing district names in NCR file
existing_ncr_names = set(
    feat['properties'].get('dtname', '').strip().lower()
    for feat in ncr_geo['features']
)

# Prepare new features from Delhi districts not in NCR file
new_features = []
for feat in delhi_geo['features']:
    delhi_name = feat['properties'].get('name', '').strip().lower()
    if delhi_name not in existing_ncr_names:
        # Convert to NCR format
        new_feat = feat.copy()
        # Change 'name' to 'dtname'
        new_feat['properties'] = {'dtname': feat['properties']['name']}
        new_features.append(new_feat)

# Add new features to NCR features
ncr_geo['features'].extend(new_features)

# Save to new file
with open(output_file, 'w') as f:
    json.dump(ncr_geo, f, indent=2)

print(f"Added {len(new_features)} new Delhi districts. Saved to {output_file}")