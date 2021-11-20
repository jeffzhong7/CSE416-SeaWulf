import json
import os
import pandas as pd
import pyodbc
import re
import shapely
from shapely.validation import make_valid
from shapely.geometry import Polygon
from shapely.ops import unary_union


def make_json_feature_collection(polygon):
    features = {'type': 'FeatureCollection', 
                        'features': [{ 
                            'type': 'Feature', 
                            'properties': {}, 
                            'geometry': shapely.geometry.mapping(polygon)
                        }]
    }
    
    return json.dumps(features, indent=4)
    
def write_to_file(filename, content):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(content)

def sql_to_polygon(polygon_string):
    # This is in order to find the set of points, which are always contained between parentheses. 
    pattern = "[\(]+(.*?)[\)]+"
    regex = re.findall(pattern, polygon_string)
    
    # To handle MultiPolygons, treat each set of points as separate polygons. 
    k = 0
    
    points = []
    polygons = []
    for string in regex:
        k += 1
        
        for point in string.split(','):
            point = point.strip()
            points.append([float(point.split(" ")[0]), float(point.split(" ")[1])])
        
        polygon = Polygon(points).convex_hull
        polygons.append(polygon)
    
    return polygons
       
def sql_to_geojson(polygon_string, geometry_name, output_dir):
    points = []
    
    # This is in order to find the set of points, which are always contained between parentheses. 
    pattern = "[\(]+(.*?)[\)]+"
    regex = re.findall(pattern, polygon_string)
    
    k = 0
    for string in regex:
        k += 1
        
        for point in string.split(','):
            point = point.strip()
            points.append([float(point.split(" ")[0]), float(point.split(" ")[1])])
        
        polygon = Polygon(points).convex_hull
        
        json_content = make_json_feature_collection(polygon) 
        index = "-" + str(k) if k > 1 else ""
        output_file = output_dir + geometry_name + index + ".geo.json"
        
        write_to_file(output_file, json_content)
        
def precincts_to_district(polygons, filename, output_dir):
    new_district = unary_union(polygons)
    
    json_content = make_json_feature_collection(new_district) 
    output_file = output_dir + filename + ".geo.json"
    
    write_to_file(output_file, json_content)
    
    