import json
import traceback
from dotenv import load_dotenv
import mysql.connector
import os
from pathlib import Path
import sys


def main():
    state_id = sys.argv[1]
    post_output = "post_output"
    plans_dir = os.path.join(post_output, state_id)
    db_queries = "db_queries"

    with open(os.path.join(db_queries, "{}-geometry.json".format(state_id)), "r") as f:
        db_geometry = json.load(f)
    with open(os.path.join(db_queries, "{}-counties.json".format(state_id)), "r") as f:
        db_counties = json.load(f) 

    ensemble = [ plan for plan in os.listdir(plans_dir) if os.path.isdir(plans_dir) ]
    
    # i = 0
    # for plan in range(len(ensemble)):
    #     i += 1
    #     insert_in_db("Districtings", [ "id", "stateId" ], [ "{}PL{}".format(state_id, i), state_id ] )

    i = 0
    for plan in ensemble: 
        i += 1

        races = ["ASIAN", "BLACK", "HISPA", "NATIV", "OTHER", "TOTAL", "WHITE"]
        parties = ["democraticVotes", "republicanVotes", "otherVotes", "totalVotes"]
        cd_columns = ["id", "cd", "geometry", "districtingId", "electionId", "populationId", "vapId"]
        prec_columns = ["id", "districtId", "geometry", "electionId", "populationId", "vapId", "county"]
        for district in os.listdir(os.path.join(plans_dir, plan, "geometry")):
            if not district.endswith("json"):
                cd = district.split("D")[-1]
            #     plan_id = "{}PL{}".format(state_id, i)
            #     district_id = "{}D{}".format(plan_id, cd)
            #     with open(os.path.join(plans_dir, plan, "election", district + "-election.json"), "r") as f:
            #         elec = json.load(f)
            #     elec["totalVotes"] = elec["TOTAL"]
            #     elec.pop("TOTAL", None)
            #     try: 
            #         insert_in_db(
            #             "Elections", 
            #             ["id"] + [key for key in elec.keys()] + ["type"],
            #             [district_id] + [val for val in elec.values()] + ["PRE2020"]
            #         )
            #     except: 
            #         print(traceback.print_exc())
                
            #     with open(os.path.join(plans_dir, plan, "population", district + "-population.json"), "r") as f:
            #         pop = json.load(f)
            #     try: 
            #         insert_in_db(
            #             "Populations", 
            #             ["id"] + [key for key in pop.keys()],
            #             [district_id] + [val for val in pop.values()]
            #         )
            #     except:
            #         print(traceback.print_exc())

            #     with open(os.path.join(plans_dir, plan, "vap", district + "-vap.json"), "r") as f:
            #         vap = json.load(f)
            #     try: 
            #         insert_in_db(
            #             "VotingAgePopulations", 
            #             ["id"] + [key for key in vap.keys()],
            #             [district_id] + [val for val in vap.values()]
            #         )
            #     except:
            #         print(traceback.print_exc())

            #     with open(os.path.join(plans_dir, plan, "geometry", district), "r") as f:
            #         geometry = json.load(f)
            #     try: 
            #         insert_in_db("Districts", cd_columns, [ district_id, cd, geometry, plan_id, district_id, district_id, district_id ])
            #     except:
            #         print(traceback.print_exc())
        
        with open(os.path.join(plans_dir, plan, "{}-precincts.json".format(plan))) as f:
            precincts_list = json.load(f) 
        for district in precincts_list.keys(): 
            cd = district.split("D")[-1]
            plan_id = "{}PL{}".format(state_id, i)
            district_id = "{}D{}".format(plan_id, cd)
            precincts = [ 
                district_id + "P" + p.split("P")[-1] for p in precincts_list[district] 
            ]
            for precinct in precincts:
                precinct_id = "{}P{}".format(state_id, precinct.split("P")[-1])
                try: 
                    insert_in_db(
                        "Precincts", 
                        prec_columns,
                        [ "{}P{}".format(plan_id, precinct.split("P")[-1]), district_id, db_geometry[precinct_id.split("P")[-1]]["geometry"], precinct_id, precinct_id, precinct_id, db_counties[precinct_id.split("P")[-1]]["county"] ]
                    )
                except:
                    print(precinct, district)
                    print(traceback.print_exc())

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
    # print(insert)
    cursor.execute(insert)
    
    cnx.commit()
    
    cnx.close()
    cursor.close()

if __name__ == "__main__":
    main()
