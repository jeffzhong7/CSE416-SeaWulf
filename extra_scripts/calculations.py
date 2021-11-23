import pickle
import recom_to_plan
import sys

def main():
    get_measures(sys.argv[1])

def get_measures(infile):
    districting_plan = None
    districting_plan = recom_to_plan.make_districting_plan(infile)
    # with open("dummy.districting", "rb") as f:
    #    districting_plan = pickle.load(f)
    
    # Districting population equality
    print("POPULATION EQUALITY")
    pop_eq = districting_plan.population_equality()
    print(pop_eq)
    
    # Compactness
    # print("POLSBY POPPER")
    pps = districting_plan.polsby_popper()
    
    # Count the number of opportunity districts
    # TODO
    
    # Proportions
    print("DEMOGRAPHIC PROPORTION")
    proportions = districting_plan.demographic_proportion("black")
    print(proportions)
    
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
    
if __name__ == "__main__":
    main()
    
    