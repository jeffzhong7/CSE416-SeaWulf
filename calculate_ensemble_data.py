import json
import numpy as np
import os
import sys


def main(demo):
    post_output = "post_output" 
    
    district_data = dict()
    ensemble_quartiles = dict()
    
    for filename in os.listdir(post_output):
        filepath = os.path.join(post_output, filename)
        with open(filepath, "r") as f:
            data = json.load(f)
            
            for district in data.keys():
                if district not in district_data.keys():
                    district_data[district] = []
                district_data[district].append(data[district])
            
            for district, proportions in district_data.items():
                ensemble_quartiles[district] = [
                    min(proportions),
                    np.quantile(proportions, 0.25),
                    np.quantile(proportions, 0.75),
                    max(proportions),
                    np.quantile(proportions, 0.5)
                ]
            
    with open("post_output/final-proportions-{}.json".format(demo), "w") as f:
        json.dump(ensemble_quartiles, f)

if __name__ == "__main__":
    main(sys.argv[1])
    
    