import conversion as conv
from dotenv import load_dotenv
import classes as cl
import json
import mysql.connector
import os
from pathlib import Path
import pickle
import pyodbc
import traceback


def make_districting_plan(infile):
    districts = graph_to_dict(infile)

    cursor = query_from_db(["ID", "CD", "geometry"], "Precint")
    
    for row in cursor:
        row_id = str(row["ID"])

        for district in districts.keys():
            if row_id in districts[district].precincts.keys(): 
                precincts = districts[district].precincts
                precincts[row_id].geometry = conv.sql_to_polygon(row["geometry"])
                # Note: sql_to_polygon may return a list, for multipolygons. 

    for d in districts.keys():
        # print("Generating new borders for {} with {} precincts and {} geometries"
        #    .format(district, len(precincts[district]), len(polygons[district])))
        try:
            district = districts[d]
            polygons = []
            
            for precinct in district.precincts.keys():
                polygons.extend(
                    district.precincts[precinct].geometry
                )
            district.geometry = conv.precincts_to_district_geom(polygons)
        except:
            print(traceback.print_exc())
    
    districting = cl.Districting(districts)
    
    # with open("{}.districting".format(infile), "wb") as f:
        # pickle.dump(districting, f)
    
    return districting
        
def graph_to_dict(infile):
    districts = dict()
    
    with open(infile) as f:
        adj_graph = json.load(f)
        nodes = adj_graph["nodes"]
        
        racial_types = ["Hispanic", "White", "Black"]
        columns = ["ID"] 
        columns += racial_types
        cursor = query_from_db(columns, "Precint")
        
        rows = dict()
        for row in cursor:
            row_id = str(row["ID"])
            rows[row_id] = row

        for node in nodes: 
            d = str(ord(node["district"]) - 64)
            node_id = node["id"]
            node_pop = cl.Population(
                number=node["population"], 
                type="total"
            )
            
            for race in racial_types:
                node_pop.subtypes[race] = cl.Population(
                    number=rows[node_id][race], 
                    type=race
                )
            
            precinct = cl.Precinct(node_pop)
            
            if (d not in districts.keys()): 
                districts[d] = cl.District(
                    population=cl.Population(
                        number=0, 
                        type="total"
                    )
                )
                
                for race in racial_types: 
                    districts[d].population.subtypes[race] = cl.Population(
                        number=0,
                        type=race
                    )
                
            districts[d].precincts[node["id"]] = precinct
            districts[d].population.number += node_pop.number
            districts[d].population.subtypes[race].number += node_pop.subtypes[race].number

    return districts
    
def query_from_db(fields, table, condition=""):
    dotenv_path = Path('db_config.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    SERVER = os.getenv("SERVER")
    DATABASE = os.getenv("DATABASE")
    UID = os.getenv("UID")
    PASS = os.getenv("PASS")
    
    config = {
        "user": UID,
        "password": PASS, 
        "host": SERVER,
        "database": DATABASE, 
    }

    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor(dictionary=True, buffered=True)
    
    query = "SELECT {} FROM {} {}".format(", ".join(fields), table, condition)
    cursor.execute(query)

    cnx.close()
    
    return cursor
    
    