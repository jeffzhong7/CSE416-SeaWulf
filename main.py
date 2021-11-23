import json
from pathlib import Path
from dotenv.main import load_dotenv
import numpy as np
import os
import pyodbc
import recom_to_plan
import sys


def main():
    recoms = "recom_output"
    
    demo_proportions = dict()
    
    # filename = sys.argv[1]
    # filepath = os.path.join(recoms, filename)
    # districting_plan = recom_to_plan.make_districting_plan(filepath)
    # demo_proportions[filename] = districting_plan.demographic_proportions("black")
    
    ensemble = dict()
    ensemble_quartiles = dict()

    for filename in os.listdir(recoms):
        print(filename)
        filepath = os.path.join(recoms, filename)
        districting_plan = recom_to_plan.make_districting_plan(filepath)
        demo_proportions[filename] = districting_plan.demographic_proportions("Black")

        ensemble[filename] = districting_plan
        
        with open("post_output/proportions.json", "a") as f:
            json.dump({ filename : demo_proportions[filename] }, f)

    district_data = dict()
    for district in districting_plan.districts.keys():
        district_data[district] = []
        ensemble_quartiles[district] = []

    for district in district_data.keys():
        for plan in demo_proportions.keys():
            district_data[district].append(demo_proportions[plan][district])

    for district in district_data.keys():
        ensemble_quartiles[district] = [
            min(district_data[district]),
            np.quantile(district_data[district], 0.25),
            np.quantile(district_data[district], 0.75),
            max(district_data[district]),
            np.quantile(district_data[district], 0.5)
        ]

    # Test on a small batch first. 
    count = 3
    threshold = 0

    good_plans = dict()
    for plan in ensemble.keys():
        if (ensemble[plan].objective_score() > threshold): 
            good_plans[plan] = ensemble[plan]
        if len(good_plans.keys()) > count: 
            break

    # Insert the plans to the database. 
    # (How? What information?)
    # for plan in good_plans:
        # put_plan_in_db(plan)
    
    # Insert the ensemble quartiles for a state.
    # (Where?) 
    for district in ensemble_quartiles.keys():
        state = "MD"
        fields = [state, district]
        fields.extend(ensemble_quartiles[district])

        # insert_in_db(
        #     "EnsembleData",
        #     ["STATE", "CD", "MAX", "Q3", "MED", "Q1", "MIN"], 
        #     fields
        # )

    # with open("dummy.districting", "rb") as f:
        # districting_plan = pickle.load(f)

    with open("post_output/district_data.json", "w") as f: 
        json.dump(district_data, f)

    with open("post_output/ensemble_quartiles.json", "w") as f:
        json.dump(ensemble_quartiles, f)
    
    with open("post_output/proportions_final.json", "w") as f:
        json.dump(demo_proportions, f)

def put_plan_in_db(plan): 
    # insert_in_db("Districtings")
    return

def insert_in_db(table, columns, fields):
    dotenv_path = Path('db_config.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    SERVER = os.getenv("SERVER")
    DATABASE = os.getenv("DATABASE")
    UID = os.getenv("UID")
    PASS = os.getenv("PASS")
    
    conn = pyodbc.connect("DRIVER={};SERVER={};DATABASE={};UID={};PWD={};MULTI_HOST=1".
        format(DRIVER, ",".join([SERVER, PORT]), DATABASE, UID, PASS))
    cursor = conn.cursor()

    insert = "INSERT INTO {} ({}) VALUES ({})".format(table, ", ".join(columns), ", ".join([str(val) for val in fields]))
    cursor.execute(insert)
    conn.commit()
    
    return cursor

if __name__ == "__main__":
    main()
    
    