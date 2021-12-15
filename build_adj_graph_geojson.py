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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--state_id", help="id of the state")
    parser.add_argument("-i", "--input_file", help="dir to input data")
    parser.add_argument("-o", "--output_file", help="dir to output adjacency graph")
    args = parser.parse_args()
    
    state_id = args.state_id
    input_file = args.input_file
    output_file = args.output_file

    precincts = build_precinct_graph(input_file, str(state_id))
    json_content = json.dumps(precincts, indent=4)
    
    conv.write_to_file(json_content, output_file)
    

def build_precinct_graph(input_file, state_id):
    fields = ["NEIGHBORS", "Total", "G20PREDBID", "G20PRERTRU", "CD"]
    
    precincts = dict()
    
    with open(input_file, "r") as f:
        precinct_json = json.load(f)

        for i in range(len(precinct_json["features"])):
            precinct_props = precinct_json["features"][i]["properties"] 
            dems = precinct_props["democraticVotes"]
            reps = precinct_props["republicanVotes"]
            voting_history = 'D'

            if (reps and dems): 
                if (reps > dems):
                    voting_history = 'R'

            try: 
                district = chr(64 + int(precinct_props['CD']))
                idx = precinct_props["index"].split("P")[-1]

                precinct_data = dict()
                precinct_data['adjacent_nodes'] = [ p.split("P")[-1] for p in precinct_props['NEIGHBORS'].split(",") ]
                precinct_data['population'] = precinct_props['TOTAL']
                precinct_data['voting_history'] = voting_history
                precinct_data['district'] = district
                precincts[idx] = precinct_data
            except: 
                print(traceback.print_exc())

    return precincts
        
if __name__ == "__main__":
    main()