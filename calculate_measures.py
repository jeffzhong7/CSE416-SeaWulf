import json
import numpy as np
import os
import recom_to_plan
import sys


def main(index):
    recoms = "recom_output" 
    filename = "recombination_of_districts-{}".format(index)
    demo = "Black"
    
    demo_proportions = dict()
    plan_polsby_popper = dict()
    plan_opportunity_count = dict()

    filepath = os.path.join(recoms, filename)
    districting_plan = recom_to_plan.make_districting_plan(filepath)
    demo_proportions[filename] = districting_plan.demographic_proportions(demo)
    

    with open("post_output/{}-proportions-{}.json".format(filename, demo), "w") as f:
        json.dump(demo_proportions[filename], f)
        
    with open("post_output/{}-polsby-popper-{}.json".format(filename, demo), "w") as f:
        json.dump(plan_polsby_popper[filename], f)

    with open("post_output/{}-opportunity-count-{}.json".format(filename, demo), "w") as f:
        json.dump(plan_opportunity_count[filename], f)

if __name__ == "__main__":
    main(sys.argv[1])
    
    