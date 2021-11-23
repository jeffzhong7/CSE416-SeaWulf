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
    filepath = os.path.join(recoms, filename)
    districting_plan = recom_to_plan.make_districting_plan(filepath)
    demo_proportions[filename] = districting_plan.demographic_proportions(demo)
        
    with open("post_output/{}-proportions-{}.json".format(filename, demo), "w") as f:
        json.dump(demo_proportions[filename], f)

if __name__ == "__main__":
    main(sys.argv[1])
    
    