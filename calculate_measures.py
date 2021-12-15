import conversion as conv
import json
import numpy as np
import os
import pickle
import shapely.wkt
import recom_to_plan
import sys


def main():
    state_id = sys.argv[1]
    index = sys.argv[2]
    recoms = "recom_output/{}".format(state_id) 
    filename = "recombination_of_districts-{}".format(index)

    # We are interested in: 
    # DISTRICTS (LIST)
    #   PRECINCTS (LIST)
    # VAP

    # For the box and whisker, find proportions of: 
    # DEM
    # REP
    # AFRAM

    filepath = os.path.join(recoms, filename)
    districting_plan = recom_to_plan.make_districting_plan(filepath, state_id)
    
    # with open("recombination_of_districts-1.districting", "rb") as f:
        # districting_plan = pickle.load(f)

    dist_to_prec = dict()
    for dist_id, district in districting_plan.districts.items():
        precincts = list(district.precincts.keys())
        precincts = [ "{}PL{}P{}".format(state_id, index, precinct) for precinct in precincts ]
        dist_to_prec[dist_id] = precincts

    # demo_proportions[filename] = districting_plan.demographic_proportions("DEM")
    # demo_proportions[filename] = districting_plan.demographic_proportions("REP")

    plan_name = "{}PL{}".format(state_id, index)
    outdir = "post_output/{}/{}/".format(state_id, plan_name)
    os.makedirs(os.path.dirname(outdir), exist_ok=True)
    with open(outdir + "{}-precincts.json".format(plan_name), "w") as f:
        json.dump(dist_to_prec, f)

    with open(outdir + "{}-props-{}.json".format(plan_name, "BLACK"), "w") as f:
        json.dump(districting_plan.demographic_proportions("BLACK"), f)
    with open(outdir + "{}-props-{}.json".format(plan_name, "DEMS"), "w") as f:
        json.dump(districting_plan.voter_proportions("democraticVotes"), f)
    with open(outdir + "{}-props-{}.json".format(plan_name, "REPS"), "w") as f:
        json.dump(districting_plan.voter_proportions("republicanVotes"), f)

    with open(outdir + "{}-polsby-popper.json".format(plan_name), "w") as f:
        json.dump(districting_plan.polsby_popper(), f)
    with open(outdir + "{}-pop-eq.json".format(plan_name), "w") as f:
        json.dump(districting_plan.population_equality(), f)

    with open(outdir + "{}-opportunity-districts.json".format(plan_name), "w") as f:
        json.dump(districting_plan.no_of_opportunity("BLACK"), f)
    with open(outdir + "{}-opportunity-districts-vap.json".format(plan_name), "w") as f:
        json.dump(districting_plan.no_of_opportunity("BLACK", vap=True), f)
    with open(outdir + "{}-objective-score.json".format(plan_name), "w") as f:
        json.dump(districting_plan.objective_score(), f)

    for dist_id, district in districting_plan.districts.items():
        os.makedirs(os.path.dirname(outdir + "geometry/"), exist_ok=True)
        with open(outdir + "geometry/{}".format(dist_id), "w") as f:
            json.dump(shapely.wkt.dumps(district.geometry), f)

        os.makedirs(os.path.dirname(outdir + "population/"), exist_ok=True)
        os.makedirs(os.path.dirname(outdir + "vap/"), exist_ok=True)
        os.makedirs(os.path.dirname(outdir + "election/"), exist_ok=True)
        pop_count = dict()
        pop_count["TOTAL"] = district.population.number
        for subtype, pop in district.population.subtypes.items():
            pop_count[subtype] = pop.number

        vap_count = dict()
        vap_count["TOTAL"] = district.vap.number
        for subtype, pop in district.vap.subtypes.items():
            vap_count[subtype] = pop.number

        elec_count = dict()
        elec_count["TOTAL"] = district.election.number
        for subtype, pop in district.election.subtypes.items():
            elec_count[subtype] = pop.number
        
        with open(outdir + "population/{}-population.json".format(dist_id), "w") as f:
            json.dump(pop_count, f)
        with open(outdir + "vap/{}-vap.json".format(dist_id), "w") as f:
            json.dump(vap_count, f)
        with open(outdir + "election/{}-election.json".format(dist_id), "w") as f:
            json.dump(elec_count, f)

    geometries = []
    for d in districting_plan.districts.values():
        geometries.append(d.geometry)
        
    conv.write_to_file(
        conv.make_json_feature_collection(
            geometries
        ), 
        outdir + "geometry/{}.geojson".format(plan_name)
    )

if __name__ == "__main__":
    main()
    
    