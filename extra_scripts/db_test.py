from dotenv import load_dotenv
import json
import mysql.connector
import os
from pathlib import Path
import sys

def main():
    plan = "24PL1"
    district = plan + "D1"
    dir = "../post_output/24/{}/".format(plan)
    
    democraticVotes = 0
    republicanVotes = 0
    otherVotes = 0 
    totalVotes = 0
    type = "PRE2020"
    
    with open(dir + "geometry/24PL1D1", "r") as f:
        polygon = json.load(f)
        
        # Districting has FK dependency on State
        # District has FK dependencies on districtingId, electionId, populationId, vapId
        insert_into_db(
            "Districting",
            ["id", "stateId"],
            ["24PL1", "24"]
        )
        
        insert_into_db(
            "District",
            ["id", "cd", "districtingId", "electionId", "populationId", "vapId"],
            [district, district.split("D")[-1], "24PL1", "24PL1D1", "24PL1D1", "24PL1D1" ]
        )

def insert_into_db(table, columns, fields):
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
    
    query = "INSERT INTO {} ({}) VALUES ({})".format(table, ", ".join(columns), "\"{}\"".format("\", \"".join(fields)))
    cursor.execute(query)
    cnx.commit()
    
    return cursor
                
if __name__ == "__main__":
    main()
    
