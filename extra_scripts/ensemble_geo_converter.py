import json
import numpy as np
import os
import plan_to_geo
import recom_to_plan
import sys


def main():
    recoms = "recom_output"
        
    for filename in os.listdir(recoms):
        filepath = os.path.join(recoms, filename)
        districting_plan = recom_to_plan.make_districting_plan(filepath)
        plan_to_geo.plan_to_geo(districting_plan, filename)

    # with open("dummy.districting", "rb") as f:
        # districting_plan = pickle.load(f)
    
if __name__ == "__main__":
    main()
    
    