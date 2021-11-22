import conversion as conv
from dotenv import load_dotenv
import classes as cl
import json
import marshal
import os
from pathlib import Path
import pickle
import pyodbc
import re
import shapely
import shapely.ops as ops
from shapely.geometry import Polygon
from shapely.ops import unary_union
import sys
import traceback


def make_districting_plan(infile, outfile):
    districts = graph_to_dict(infile)
    
    cursor = query_from_db(["ID", "geometry", "CD"], "Precint")
    data = cursor.fetchall()
    
    rows = dict()
    columns = [column[0] for column in cursor.description]
    for row in data:
        row_data = dict(zip(columns, row))
        rows[str(row_data["ID"])] = row_data
        
    for i in range(len(rows)):
        id = str(i)
        district_of_precinct = rows[id]["CD"]
        precincts = districts[district_of_precinct].precincts
        precincts[id].geometry = conv.sql_to_polygon(rows[id]["geometry"])
        # Note: sql_to_polygon may return a list, for multipolygons. 
    
    for d in districts.keys():
        # print("Generating new borders for {} with {} precincts and {} geometries"
        #    .format(district, len(precincts[district]), len(polygons[district])))
        try:
            props = conv.make_props(int(d) - 1)
            district = districts[d]
            polygons = []
            
            for precinct in district.precincts.keys():
                polygons.extend(
                    district.precincts[precinct].geometry
                )
            district.geometry = conv.precincts_to_district_geom(
                polygons, props, d, outfile
            )
        except:
            print(traceback.print_exc())
    
    districting = cl.Districting(districts)
    
    with open("dummy.districting", "wb") as f:
        pickle.dump(districting, f)
    
    return districting
        
def graph_to_dict(infile):
    districts = dict()
    
    with open(infile) as f:
        data = json.load(f)
        nodes = data["nodes"]
        
        cursor = query_from_db(["ID", "Black"], "Precint")
        data = cursor.fetchall()
        
        rows = dict()
        columns = [column[0] for column in cursor.description]
        for row in data:
            row_data = dict(zip(columns, row))
            rows[str(row_data["ID"])] = row_data
        
        for node in nodes: 
            d = str(ord(node["district"]) - 64)
            node_id = node["id"]
            node_pop = cl.Population(
                number=node["population"], 
                type="total"
            )
            black_pop = cl.Population(
                number=rows[node_id]["Black"], 
                type="black"
            )
            node_pop.subtypes["black"] = black_pop
            
            precinct = cl.Precinct(node_pop)
            
            if (d not in districts.keys()): 
                districts[d] = cl.District(
                    population=cl.Population(
                        number=0, 
                        type="total"
                    )
                )
                
                districts[d].population.subtypes["black"] = cl.Population(
                    number=0,
                    type="black"
                )
                
            districts[d].precincts[node["id"]] = precinct
            districts[d].population.number += node_pop.number
            districts[d].population.subtypes["black"].number += black_pop.number
            
    return districts
    
def query_from_db(fields, table):
    dotenv_path = Path('db_config.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    DRIVER = os.getenv("DRIVER")
    SERVER = os.getenv("SERVER")
    PORT = os.getenv("PORT")
    DATABASE = os.getenv("DATABASE")
    UID = os.getenv("UID")
    PASS = os.getenv("PASS")
    
    conn = pyodbc.connect("DRIVER={};SERVER={};DATABASE={};UID={};PWD={};MULTI_HOST=1".
        format(DRIVER, ",".join([SERVER, PORT]), DATABASE, UID, PASS))
    
    query = "SELECT {} FROM {}".format(", ".join(fields), table)
    cursor = conn.execute(query)
    
    return cursor
    
    