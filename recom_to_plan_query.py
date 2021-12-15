from dotenv import load_dotenv
import json
import mysql.connector
import os
from pathlib import Path
import pickle
import shapely.wkt
import sys
import traceback


def main():
    state_id = sys.argv[1]
    precinct_prefix = state_id + "P"
    cb_prefix = state_id + "B"

    # racial_types = ["ASIAN", "BLACK", "HISPA", "NATIV", "OTHER", "WHITE"]
    # columns = ["TOTAL", "id"] 
    # columns += racial_types
    # cursor = query_from_db(columns, "Populations")
    # pre_to_pop = dict()
    # pre_to_vap = dict()
    # for row in cursor:
    #     pre_to_pop[row["id"].split(precinct_prefix)[-1]] = row
    # cursor = query_from_db(columns, "VotingAgePopulations")
    # for row in cursor:
    #     pre_to_vap[row["id"].split(precinct_prefix)[-1]] = row

    # with open("{}-pop.json".format(state_id), "w") as f:
    #     json.dump(pre_to_pop, f)
    # with open("{}-vap.json".format(state_id), "w") as f:
    #     json.dump(pre_to_vap, f)

    # election = ["democraticVotes", "republicanVotes", "otherVotes"]
    # columns = ["totalVotes", "id"]
    # columns += election
    # cursor = query_from_db(columns, "Elections")
    # pre_to_elec = dict()
    # for row in cursor: 
    #     pre_to_elec[row["id"].split(precinct_prefix)[-1]] = row

    # with open("{}-election.json".format(state_id), "w") as f:
    #     json.dump(pre_to_elec, f)
        
    # cursor = query_from_db(["id", "geometry"], "Precincts", "WHERE id LIKE \"{}\"".format(precinct_prefix + "%"))
    # pre_to_geom = dict()
    # for row in cursor: 
    #     pre_to_geom[row["id"].split(precinct_prefix)[-1]] = row

    # with open("{}-geometry.json".format(state_id), "w") as f:
    #     json.dump(pre_to_geom, f)
        
    # cursor = query_from_db(["id", "county"], "Precincts", "WHERE id LIKE \"{}\"".format(precinct_prefix + "%"))
    # pre_to_cnty = dict()
    # for row in cursor: 
    #     pre_to_cnty[row["id"].split(precinct_prefix)[-1]] = row

    # with open("{}-counties.json".format(state_id), "w") as f:
    #     json.dump(pre_to_cnty, f)
    
    cursor = query_from_db(["id", "geometry", "precinctId"], "CensusBlocks", "WHERE id LIKE \"{}\"".format(cb_prefix + "%"))
    pre_to_cb = dict()
    for row in cursor: 
        if row["precinctId"] not in pre_to_cb.keys():
            pre_to_cb[row["precinctId"]] = []
        pre_to_cb[row["precinctId"]].append(row)

    with open("{}-cbs.json".format(state_id), "w") as f:
        json.dump(pre_to_cb, f)

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
    
if __name__ == "__main__":
    main()
