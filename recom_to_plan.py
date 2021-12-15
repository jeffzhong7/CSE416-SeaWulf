import classes as cl
import conversion as conv
from dotenv import load_dotenv
import json
import mysql.connector
import os
from pathlib import Path
import pickle
import shapely.wkt
import sys
import traceback


def make_districting_plan(infile, state_id):
    index = infile.split("-")[-1]
    districts = graph_to_dict(index, infile, state_id)

    precinct_prefix = state_id + "P"
    # cursor = query_from_db(["id", "geometry"], "Precincts", "WHERE id LIKE \"{}\"".format(precinct_prefix + "%"))

    pre_to_geom = dict()
    db_queries_dir = "db_queries"
    with open("{}/{}-geometry.json".format(db_queries_dir, state_id), "r") as f:
        pre_to_geom = json.load(f)

    for pre_id, row in pre_to_geom.items():
        for district in districts.keys():
            if pre_id in districts[district].precincts.keys(): 
                precincts = districts[district].precincts
                precincts[pre_id].geometry = [ shapely.wkt.loads(row["geometry"]) ]

    for d in districts.keys():
        # print("Generating new borders for {} with {} precincts and {} geometries"
        #    .format(district, len(precincts[district]), len(polygons[district])))
        try:
            district = districts[d]
            polygons = []
            
            for precinct in district.precincts.keys():
                polygons.extend(
                    district.precincts[precinct].geometry
                )
            district.geometry = conv.precincts_to_district_geom(polygons)
        except:
            print(traceback.print_exc())
    
    districting = cl.Districting(districts=districts)
    
    # with open("{}.districting".format(infile), "wb") as f:
    #     pickle.dump(districting, f)
    
    return districting
        
def graph_to_dict(index, infile, state_id):
    with open(infile) as f:
        districts = dict()

        precinct_prefix = state_id + "P"

        adj_graph = json.load(f)
        nodes = adj_graph["nodes"]

        racial_types = ["ASIAN", "BLACK", "HISPA", "NATIV", "OTHER", "WHITE"]
        # columns = ["TOTAL", "id"] 
        # columns += racial_types
        # cursor = query_from_db(columns, "Populations")


        pre_to_pop = dict()
        pre_to_vap = dict()
        # for row in cursor:
            # pre_to_pop[row["id"].split(precinct_prefix)[-1]] = row
        # cursor = query_from_db(columns, "VotingAgePopulations")
        # for row in cursor:
            # pre_to_vap[row["id"].split(precinct_prefix)[-1]] = row

        election = ["democraticVotes", "republicanVotes", "otherVotes"]
        # columns = ["totalVotes", "id"]
        # columns += election
        # cursor = query_from_db(columns, "Elections")
        pre_to_elec = dict()
        # for row in cursor: 
            # pre_to_elec[row["id"].split(precinct_prefix)[-1]] = row

        db_queries_dir = "db_queries"
        with open("{}/{}-pop.json".format(db_queries_dir, state_id), "r") as f:
            pre_to_pop = json.load(f)
        with open("{}/{}-vap.json".format(db_queries_dir, state_id), "r") as f:
            pre_to_vap = json.load(f)
        with open("{}/{}-election.json".format(db_queries_dir, state_id), "r") as f:
            pre_to_elec = json.load(f)

        for node in nodes: 
            d = str(ord(node["district"]) - 64)
            d = "{}PL{}D{}".format(state_id, index, d)
            node_id = node["id"]
            node_pop = cl.Population(
                number=node["population"], 
                type="TOTAL"
            )
            node_vap = cl.Population(
                number=pre_to_vap[node_id]["TOTAL"],
                type="TOTAL"
            )
            node_elec = cl.Population(
                number=pre_to_elec[node_id]["totalVotes"],
                type="TOTAL"
            )
            node_vote = node["voting_history"]
            
            for race in racial_types:
                node_pop.subtypes[race] = cl.Population(
                    number=pre_to_pop[node_id][race], 
                    type=race
                )
                node_vap.subtypes[race] = cl.Population(
                    number=pre_to_vap[node_id][race], 
                    type=race
                )

            for party in election:
                node_elec.subtypes[party] = cl.Population(
                    number=pre_to_elec[node_id][party],
                    type=party
                )
            
            precinct = cl.Precinct(population=node_pop, vap=node_vap, election=node_elec, voting_history=node_vote)

            if (d not in districts.keys()): 
                districts[d] = cl.District(
                    population=cl.Population(
                        number=0, 
                        type="TOTAL"
                    ),
                    vap=cl.Population(
                        number=0,
                        type="TOTAL"
                    ),
                    election=cl.Population(
                        number=0,
                        type="TOTAL"
                    )
                )
                
                for subtype in racial_types: 
                    districts[d].population.subtypes[subtype] = cl.Population(
                        number=0,
                        type=subtype
                    )

                for subtype in racial_types: 
                    districts[d].vap.subtypes[subtype] = cl.Population(
                        number=0,
                        type=subtype
                    )

                for party in election:
                    districts[d].election.subtypes[party] = cl.Population(
                        number=0,
                        type=party
                    )
                
            districts[d].precincts[node["id"]] = precinct
            districts[d].population.number += node_pop.number
            districts[d].vap.number += node_vap.number
            districts[d].election.number += node_elec.number
            for subtype, pop in precinct.population.subtypes.items():
                districts[d].population.subtypes[subtype].number += pop.number
            for subtype, pop in precinct.vap.subtypes.items():
                districts[d].vap.subtypes[subtype].number += pop.number
            for party, pop in precinct.election.subtypes.items():
                districts[d].election.subtypes[party].number += pop.number

    return districts
    