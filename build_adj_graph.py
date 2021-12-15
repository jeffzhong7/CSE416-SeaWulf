import argparse
import conversion as conv
from dotenv import load_dotenv
import json
import os
import pandas as pd
from pathlib import Path
import pyodbc
import sys
import traceback


DRIVER = ""
SERVER = ""
PORT = ""
DATABASE = ""
UID = ""
PASS = ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("state_id", help="id of the state")
    parser.add_argument("output_file", help="dir to output adjacency graph")
    args = parser.parse_args()
    
    state_id = args.state_id
    output_file = args.output_file

    precincts = build_precinct_graph(str(state_id))
    json_content = json.dumps(precincts, indent=4)
    
    conv.write_to_file(json_content, output_file)
    

def build_precinct_graph(state_id):
    conn = pyodbc.connect("DRIVER={};SERVER={};DATABASE={};UID={};PWD={};MULTI_HOST=1".
        format(DRIVER, ",".join([SERVER, PORT]), DATABASE, UID, PASS))
    
    fields = ["NEIGHBORS", "Total", "G20PREDBID", "G20PRERTRU", "CD"]
    table = "Precint"
    query = "SELECT {} FROM {}{}".format(", ".join(fields), table, " WHERE STATE LIKE " + state_id)
    cursor = conn.execute(query)
    
    # names = pd.read_sql_query("SELECT NAME_E FROM MD_DISTRICTS", conn)
    
    data = cursor.fetchall()
    
    rows = []
    columns = [column[0] for column in cursor.description]
    for row in data:
        rows.append(dict(zip(columns, row)))
        
    precincts = dict()
    
    for i in range(len(rows)):
        dems = rows[i]['G20PREDBID']
        reps = rows[i]['G20PRERTRU']
        voting_history = 'D' 
        
        if (reps and dems): 
            if (reps > dems):
                voting_history = 'R'
        
        try: 
            district = chr(64 + int(rows[i]['CD']))
            
            precinct_data = dict()
            precinct_data['adjacent_nodes'] = rows[i]['NEIGHBORS'].split(",")
            precinct_data['population'] = rows[i]['Total']
            precinct_data['voting_history'] = voting_history
            precinct_data['district'] = district
            precincts[i] = precinct_data
        except: 
            print(traceback.print_exc())
    
    return precincts
        
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