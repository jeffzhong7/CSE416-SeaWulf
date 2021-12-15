import json
import numpy as np
import os
import sys
import traceback


def main():
    demo = sys.argv[1]
    state_id = sys.argv[2]
    
    post_output = "post_output/{}".format(state_id) 
    
    district_data = dict()
    ensemble_quartiles = dict()

    obj_scores = dict()
    pp_scores = dict()
    pop_eq_scores = dict()
    opp_counts = dict()
    opp_counts_vap = dict()

    for plan in os.listdir(post_output):
        filepath = os.path.join(post_output, plan)
        prop_file = "{}-props-{}.json".format(plan, demo)
        with open(os.path.join(filepath, prop_file), "r") as f:
            data = json.load(f)
            
            for district in data.keys():
                cd = district.split("D")[-1]
                if cd not in district_data.keys():
                    district_data[cd] = []
                district_data[cd].append(data[district])
        try: 
            obj_score = "{}-objective-score.json".format(plan)
            with open(os.path.join(filepath, obj_score), "r") as f:
                data = json.load(f)
                obj_scores[plan] = data
            pop_eq = "{}-pop-eq.json".format(plan)
            with open(os.path.join(filepath, pop_eq), "r") as f:
                data = json.load(f)
                pop_eq_scores[plan] = data
            pp = "{}-polsby-popper.json".format(plan)
            with open(os.path.join(filepath, pp), "r") as f:
                data = json.load(f)
                pp_scores[plan] = np.mean(list(data.values()))
            opps = "{}-opportunity-districts.json".format(plan)
            with open(os.path.join(filepath, opps), "r") as f:
                data = json.load(f)
                opp_counts[plan] = data
            opps_vap = "{}-opportunity-districts-vap.json".format(plan)
            with open(os.path.join(filepath, opps_vap), "r") as f:
                data = json.load(f)
                opp_counts_vap[plan] = data
        except: 
            print(plan)
            print(traceback.print_exc())

    for district, proportions in district_data.items():
        ensemble_quartiles[district] = [
            min(proportions),
            np.quantile(proportions, 0.25),
            np.quantile(proportions, 0.75),
            max(proportions),
            np.quantile(proportions, 0.5)
        ]
    
    sorted_scores = sorted(obj_scores, key=obj_scores.get)
    sorted_pop_eq = sorted(pop_eq_scores, key=pop_eq_scores.get)
    sorted_pp = sorted(pp_scores, key=pp_scores.get)
    sorted_opps = sorted(opp_counts, key=opp_counts.get)
    sorted_opps_vap = sorted(opp_counts_vap, key=opp_counts_vap.get)
    ensemble = []
    while (len(ensemble) < 6):
        if sorted_scores[0] not in ensemble:
            ensemble.append(sorted_scores.pop(0))
    while (len(ensemble) < 12):
        if sorted_pop_eq[0] not in ensemble:
            ensemble.append(sorted_pop_eq.pop(0))
    while (len(ensemble) < 18):
        if sorted_pp[0] not in ensemble:
            ensemble.append(sorted_pp.pop(0))
    while (len(ensemble) < 24):
        if sorted_opps[0] not in ensemble:
            ensemble.append(sorted_opps.pop(0))
    while (len(ensemble) < 30):
        if sorted_opps_vap[0] not in ensemble:
            ensemble.append(sorted_opps_vap.pop(0))
            
    with open("post_output/{}-box-whisker-{}.json".format(state_id, demo.lower()), "w") as f:
        json.dump(ensemble_quartiles, f)

    with open("post_output/{}-ensemble.json".format(state_id), "w") as f:
        json.dump(ensemble, f)

if __name__ == "__main__":
    main()
    
    