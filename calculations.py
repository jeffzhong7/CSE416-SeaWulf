import math
import pickle
from pyproj import Geod
import recom_to_plan
import sys

def main():
    get_measures(sys.argv[1], sys.argv[2])

def get_measures(infile, outfile):
    districting_plan = None
    # districting_plan = recom_to_plan.make_districting_plan(infile, outfile)
    with open("dummy.districting", "rb") as f:
        districting_plan = pickle.load(f)
    
    # Districting population equality
    print("POPULATION EQUALITY")
    pop_eq = measure_population_equality(districting_plan)
    print(pop_eq)
    
    # Compactness
    # print("POLSBY POPPER")
    pp = plan_polsby_popper(districting_plan)
    
    # Count the number of opportunity districts
    # TODO
    
    measures = [pop_eq]
    weights = [1]
    
    # m_2 = 0
    # w_2 = 0.5
    
    of_score = sum([
        measure * weight 
        for measure, weight in zip(measures, weights)
    ])
    
    measures = [of_score]
    
    return measures 
    
def measure_population_equality(districting):
    populations = dict()
    black_pops = dict()
    districts = districting.districts
    for d in districts.keys():
        populations[d] = int(districts[d].population.number)
        black_pops[d] = int(districts[d].population.subtypes["black"].number)
        
    print(populations)
    print(black_pops)
    print([afram / total for afram, total in zip(black_pops.values(), populations.values())])
    
    ideal_pop = sum(list(populations.values())) / len(districts.keys())
    # print("Expected pop/district: {}".format(ideal_pop))
    
    sum_of_squares = 0
    for d in populations:
        ratio = populations[d] / ideal_pop - 1
        square = ratio ** 2
        sum_of_squares += square
    return sum_of_squares ** 0.5
    
def plan_polsby_popper(districting_plan):
    pp = dict()
    districts = districting_plan.districts
    
    for d in districts.keys():
        pp[d] = polsby_popper(districts[d].geometry)
    
    return pp
         
def polsby_popper(geometry):
    geod = Geod(ellps="WGS84")
    area, perimeter = geod.geometry_area_perimeter(geometry)
    
    return (4 * math.pi * abs(area))/(perimeter ** 2)
    
def is_opportunity(district):
    return True
    
if __name__ == "__main__":
    main()
    
    