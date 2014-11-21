import json
json_data=open('dc_data.json')
data = json.load(json_data)

# But to visualize it on a map, we have to add more structure to the data

type_point = {"type": "Point"}


geo_data = {
    'type': 'FeatureCollection', 
    'features': []
}

for listing in data:
    if listing['latitude']:   # (check for coord data)
        
        # Each tweet is a GeoJSON "feature"
        feature = {
            'type': 'Feature', 
            'geometry': {"type": "Point", "coordinates": [listing['longitude'], listing['latitude']]}, 
            
            # A feature's "properties" become attribute columns in GIS
            'properties': {
                'neighborhood': listing['neighborhood'],
                'title': listing['title'],
                'price': listing['price'],
                'sqft': listing['sqft']
            }
        }
        
        # Add the feature into the GeoJSON wrapper
        geo_data['features'].append(feature)

with open('dc_data.geojson', 'wb') as f:
    json.dump(geo_data, f, indent=2)
            
print len(geo_data['features']), 'geotagged tweets saved to file'

json_data.close()