import conversion as conv
from dotenv import load_dotenv
import json
import os
import pandas as pd
from pathlib import Path
import pyodbc
import sys


DRIVER = ""
SERVER = ""
PORT = ""
DATABASE = ""
UID = ""
PASS = ""

def main():
    precincts = build_precinct_graph()
    json_content = json.dumps(precincts, indent=4)
    
    output_file = sys.argv[1]
    
    conv.write_to_file(output_file, json_content)
    

def build_precinct_graph():
    conn = pyodbc.connect("DRIVER={};SERVER={};DATABASE={};UID={};PWD={};MULTI_HOST=1".
        format(DRIVER, ",".join([SERVER, PORT]), DATABASE, UID, PASS))
    
    fields = ["NEIGHBORS", "Total", "G20PREDBID", "G20PRERTRU", "CD"]
    table = "Precint"
    query = "SELECT {} FROM {}".format(", ".join(fields), table)
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
        
        district = chr(64 + int(rows[i]['CD']))
        
        precinct_data = dict()
        precinct_data['adjacent_nodes'] = rows[i]['NEIGHBORS'].split(",")
        precinct_data['population'] = rows[i]['Total']
        precinct_data['voting_history'] = voting_history
        precinct_data['district'] = district
        precincts[i] = precinct_data
    
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