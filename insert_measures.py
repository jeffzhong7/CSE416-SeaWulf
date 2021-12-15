import json
import traceback
from dotenv import load_dotenv
import mysql.connector
import numpy as np
import os
from pathlib import Path
import sys


def main():
    state_id = sys.argv[1]
    post_output = "post_output"
    plans_dir = os.path.join(post_output, state_id)

    ensemble = [ plan for plan in os.listdir(plans_dir) if os.path.isdir(plans_dir) ]
    
    # i = 0
    # for plan in range(len(ensemble)):
    #     i += 1
    #     insert_in_db("Districtings", [ "id", "stateId" ], [ "{}PL{}".format(state_id, i), state_id ] )

    i = 1
    for plan in ensemble: 
        plan_id = "{}PL{}".format(state_id, i)
        objective_score_file = "{}-objective-score.json".format(plan)
        opportunity_districts_file = "{}-opportunity-districts.json".format(plan)
        polsby_popper_file = "{}-polsby-popper.json".format(plan)
        pop_eq_file = "{}-pop-eq.json".format(plan)
        with open(os.path.join(plans_dir, plan, objective_score_file), "r") as f:
           objective_score = json.load(f)
        with open(os.path.join(plans_dir, plan, opportunity_districts_file), "r") as f:
           opportunity_districts = json.load(f)
        with open(os.path.join(plans_dir, plan, polsby_popper_file), "r") as f:
           compactness = json.load(f)
        with open(os.path.join(plans_dir, plan, pop_eq_file), "r") as f:
           pop_eq = json.load(f)
        
        columns = ["id", "objectiveFunction", "opportunityDistricts", "polsbyPopper", "populationEquality", "districtingId" ]
        insert_in_db(
            "Measures",
            columns,
            [ plan_id, objective_score, opportunity_districts, np.mean(list(compactness.values())), pop_eq, plan_id ]
        )
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

    insert = "INSERT INTO {} ({}) VALUES ({})".format(table, ", ".join(columns), "\"{}\"".format("\", \"".join([str(val) for val in values])))
    cursor.execute(insert)
    
    # print(insert)
    cnx.commit()
    
    cnx.close()
    cursor.close()

if __name__ == "__main__":
    main()
