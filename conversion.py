import json
import math
import os
from pyproj import Geod
import re
import shapely
from shapely.geometry import Polygon
from shapely.ops import unary_union


STROKE = "#555555"
STROKE_WIDTH = "2"
STROKE_OPACITY = "1"
COLORS = ["#400000", "#ff0000", "#ff8000", "#ffff00", "#008000", "#0080c0", "#000080", "#800080"]
FILL_OPACITY = "0.5"

def make_json_feature_collection(polygon, properties):
    features = {'type': 'FeatureCollection', 
        'features': [{ 
            'type': 'Feature', 
            'properties': properties, 
            'geometry': shapely.geometry.mapping(polygon)
        }]
    }
    
    return json.dumps(features, indent=4)
    
def write_to_file(content, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w') as file:
        file.write(content)

def make_props(fill):
    props = { 
        'stroke': STROKE,
        'stroke-width': STROKE_WIDTH,
        'stroke-opacity': STROKE_OPACITY,
        'fill': COLORS[fill], 
        'fill-opacity': FILL_OPACITY
    }
    
    return props

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
            points.append([
                float(point.split(" ")[0]), 
                float(point.split(" ")[1])
            ])
        
        polygon = Polygon(points)
        polygons.append(polygon)
    
    return polygons

def precincts_to_district_geom(polygons):
    new_boundary = unary_union([
        polygon if polygon.is_valid else polygon.buffer(0) 
            for polygon in polygons
    ])
    
    return new_boundary
    
def polsby_popper(geometry):
    geod = Geod(ellps="WGS84")
    area, perimeter = geod.geometry_area_perimeter(geometry)
    
    return (4 * math.pi * abs(area))/(perimeter ** 2)
       
"""
def sql_to_geojson(polygon_string, properties, geometry_name, output_dir):
    points = []
    
    # This is in order to find the set of points, which are always contained between parentheses. 
    pattern = "[\(]+(.*?)[\)]+"
    regex = re.findall(pattern, polygon_string)
    
    k = 0
    for string in regex:
        k += 1
        
        for point in string.split(','):
            point = point.strip()
            points.append([
                float(point.split(" ")[0]), 
                float(point.split(" ")[1])
            ])
        
        polygon = Polygon(points)
        
        json_content = make_json_feature_collection(polygon, properties) 
        index = "-" + str(k) if k > 1 else ""
        output_file = output_dir + geometry_name + index + ".geo.json"
        
        write_to_file(output_file, json_content)
"""