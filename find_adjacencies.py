from dotenv import load_dotenv
import json
import mysql.connector
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import pprint
from shapely import wkt
import sys
import traceback


def main():
    pp = pprint.PrettyPrinter(indent=4, depth=6)
    
    # DISTRICT NEIGHBORS
    state_id = sys.argv[1]
    post_output = "post_output"
    # plan = "PL7503"
    geom_dir = "geometry"
    
    plans_dir = os.path.join(post_output, state_id)

    ensemble = [ plan for plan in os.listdir(plans_dir) if os.path.isdir(plans_dir) ]

    # DISTRICT NEIGHBORS
    i = 0
    for plan in ensemble: 
        i += 1
        path_dir = join(plans_dir, plan, geom_dir)
        dist_geom_files = [f for f in listdir(path_dir) if not f.endswith("json")]
        
        districts = dict()
        adjacency_list = dict()
        for f in dist_geom_files:
            with open(join(path_dir, f), "r") as file: 
                cd = f.split("D")[-1]
                district_id = "{}PL{}D{}".format(state_id, i, cd)
                districts[district_id] = wkt.loads(json.load(file))
                adjacency_list[district_id] = []
        
        for district, geom in districts.items():
            for other_d, other_g in districts.items():
                if district != other_d:
                    if geom.intersects(other_g):
                        adjacency_list[district].append(other_d)
        
        for district in adjacency_list:
            for neighbor in adjacency_list[district]:
                insert_in_db(
                    "DistrictNeighbors", 
                    ["districtId", "neighborId"], 
                    [ [ district, neighbor ] ]
                )
    
        # BORDER PRECINCTS
        db_dir = "db_queries"
        prec_geom_dir = "{}-geometry.json".format(state_id)

        prec_list_file = plan + "-precincts.json"
        with open(join(db_dir, prec_geom_dir)) as f:
            prec_geom_file = json.load(f)
            precinct_geom = { "{}PL{}P{}".format(state_id, i, v["id"].split("P")[-1]) : wkt.loads(v["geometry"]) for v in prec_geom_file.values() }

        with open(join(post_output, state_id, plan, prec_list_file), "r") as f: 
            precinct_list = json.load(f)

        d_to_p_list = dict()
        for d, pl in precinct_list.items():
            dist = "{}PL{}D{}".format(state_id, i, d.split("D")[-1])
            pre_list = [ "{}PL{}{}".format(state_id, i, "".join(p.split(plan))) for p in pl ]

            d_to_p_list[dist] = pre_list

        border_precinct_list = dict()
        for key in districts.keys():
            border_precinct_list[key] = []

        for district, pl in d_to_p_list.items():
            pl = [ "".join(p.split(plan)) for p in pl ]
            for prec in pl:
                if districts[district].boundary.overlaps(precinct_geom[prec].boundary):
                    border_precinct_list[district].append(prec)
        
        columns = ["districtId", "borderPrecinctId"]
        for district, pl in border_precinct_list.items():
            p_list = pl
            while (len(p_list)):
                try: 
                    insert_in_db(
                        "DistrictBorderPrecincts", 
                        columns, 
                        [ [ district, p ] for p in p_list[:1000] ]
                    )
                    p_list = p_list[1000:]
                except: 
                    print(traceback.print_exc())

        
        # BORDER PRECINCT CENSUS BLOCKS
        columns = ["precinctId", "censusBlockId"]
        cb_dir = "{}-cbs.json".format(state_id)
        with open(join(db_dir, cb_dir)) as f:
            cb_file = json.load(f)
        for pl in border_precinct_list.values():
            for p in pl: 
                try: 
                    insert_in_db(
                        "PrecinctCensusBlocks",
                        columns,
                        [ [ p, cb["id"] ] for cb in cb_file["{}P{}".format(state_id, p.split("P")[-1])] ]
                    )
                except: 
                    print(traceback.print_exc())

        # CENSUS BLOCKS ON DISTRICT BORDER  
        columns = ["precinctId", "borderBlockId"]
        precinct_border_blocks = dict() 
        for district, pl in border_precinct_list.items():
            for p in pl:
                if p not in precinct_border_blocks.keys():
                    precinct_border_blocks[p] = []
                for cb in cb_file["{}P{}".format(state_id, p.split("P")[-1])]:
                    if districts[district].boundary.overlaps(wkt.loads(cb["geometry"]).boundary):
                        precinct_border_blocks[p].append(cb["id"])
        
        for p in precinct_border_blocks.keys():
            try: 
                insert_in_db(
                    "PrecinctBorderBlocks",
                    columns,
                    [ [ p, cb ] for cb in precinct_border_blocks[p] ]
                )
            except: 
                print(traceback.print_exc())
    
    # PRECINCT NEIGHBORS
    i = 1
    input_graph_dir = os.path.join("recom_input", "mi.json")
    columns = ["precinctId", "neighborId"]
    for plan in ensemble:
        with open(os.path.join(input_graph_dir),  "r") as f:
            data = json.load(f)
            node_list = []
            for node, properties in data.items():
                node_list += [ [ "{}PL{}P{}".format(state_id, i, node), "{}PL{}P{}".format(state_id, i, neighbor) ] for neighbor in properties["adjacent_nodes"] ]
            while (len(node_list)):
                try: 
                    insert_in_db(
                        "PrecinctNeighbors", 
                        columns,
                        node_list[:1000]
                    )
                    node_list = node_list[1000:]
                except: 
                    print(traceback.print_exc())
        i += 1

def insert_in_db(table, columns, values):
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

    values_list = ""
    for value in values:
        values_list += "(\"{}\"),".format(("\",\"").join(value))

    insert = "INSERT INTO {} ({}) VALUES {}".format(table, ", ".join(columns), values_list[:-1])
    print(insert)
    # cursor.execute(insert)
    
    cnx.commit()
    
    cnx.close()
    cursor.close()
    
if __name__ == "__main__":
    main()