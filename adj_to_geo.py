import conversion as conv
from dotenv import load_dotenv
import json
import os
from pathlib import Path
import pyodbc
import re
import shapely
from shapely.validation import make_valid
from shapely.geometry import Polygon
from shapely.ops import unary_union
import sys


STROKE = "#555555"
STROKE_WIDTH = "2"
STROKE_OPACITY = "1"
COLORS = ["#400000", "#ff0000", "#ff8000", "#ffff00", "#008000", "#0080c0", "#004080", "#800080"]
FILL_OPACITY = "0.5"

def main():
    infile = sys.argv[1]
    outfile = sys.argv[2]
    
    precincts = dict()
    polygons = dict()
    
    with open(infile) as f:
        data = json.load(f)
        for key in data.keys():
            district = data[key]["district"]
            if district in precincts.keys():
                precincts[district].append(int(key))
            else:
                precincts[district] = [int(key)]
            
    polygons = {k: [] for k in precincts.keys()}
    
    conn = pyodbc.connect("DRIVER={};SERVER={};DATABASE={};UID={};PWD={};MULTI_HOST=1".
        format(DRIVER, ",".join([SERVER, PORT]), DATABASE, UID, PASS))
    
    fields = ["ID", "geometry"]
    table = "Precint"
    query = "SELECT {} FROM {}".format(", ".join(fields), table)
    cursor = conn.execute(query)
    
    data = cursor.fetchall()
    
    rows = []
    columns = [column[0] for column in cursor.description]
    for row in data:
        rows.append(dict(zip(columns, row)))
    for i in range(len(rows)):
        for district in precincts.keys():
            if i in precincts[district]:
                polygons[district].extend(conv.sql_to_polygon(rows[i]['geometry']))
                # sql_to_geojson(rows[i]['geometry'], str(i))
            
    for district in polygons.keys():
        print("Generating new borders for {} with {} precincts and {} geometries"
            .format(district, len(precincts[district]), len(polygons[district])))
        props = {
            'stroke': STROKE,
            'stroke-width': STROKE_WIDTH,
            'stroke-opacity': STROKE_OPACITY,
            'fill': COLORS[ord(district) - 65], 
            'fill-opacity': FILL_OPACITY
        }
        try: 
            conv.precincts_to_district_geom(polygons[district], props, district, outfile)
        except ValueError: 
            print(district + " failed to generate")
    
if __name__ == "__main__":
    dotenv_path = Path('db_config.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    DRIVER = os.getenv("DRIVER")
    SERVER = os.getenv("SERVER")
    PORT = os.getenv("PORT")
    DATABASE = os.getenv("DATABASE")
    UID = os.getenv("UID")
    PASS = os.getenv("PASS")
    
    main()
    
    