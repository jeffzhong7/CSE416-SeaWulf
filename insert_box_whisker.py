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
    plans_dir = os.path.join(post_output)
    
    box_whisker_files = [ file for file in os.listdir(plans_dir) if "box" in file and state_id in file ]

    i = -1
    for file in box_whisker_files: 
        i += 1
        with open(os.path.join(plans_dir, file), "r") as f:
            state_data = json.load(f)

            demo = os.path.splitext(file)[0].split("-")[-1]

            # MIN Q1 Q3 MAX MED
            for district, proportions in state_data.items():
                cd = district.split("D")[-1]
                columns = ["id", "basis", "lowerQuartile", "max", "median", "min", "upperQuartile", "stateId"]
                insert_in_db(
                    "BoxAndWhiskers",
                    columns,
                    [ "{}D{}BW{}".format(state_id, cd, i), demo, proportions[1], proportions[3], proportions[4], proportions[0], proportions[2], state_id ]
                )

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
