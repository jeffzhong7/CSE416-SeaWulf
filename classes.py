import conversion as conv
import math
import numpy as np
from pyproj import Geod


class Districting():
    def __init__(self, districts=None):
        self.districts = dict() if not districts else districts
        
    def population_equality(self):
        populations = dict()
        for d in self.districts.keys():
            populations[d] = int(self.districts[d].population.number)
        
        ideal_pop = sum(list(populations.values())) / len(self.districts.keys())
        # print("Expected pop/district: {}".format(ideal_pop))
        
        sum_of_squares = 0
        for d in populations:
            ratio = populations[d] / ideal_pop - 1
            square = ratio ** 2
            sum_of_squares += square
        return sum_of_squares ** 0.5
        
    def population_equality_norm(self): 
        populations = dict()
        for d in self.districts.keys():
            populations[d] = int(self.districts[d].population.number)
        
        ideal_pop = sum(list(populations.values())) / len(self.districts.keys())
        # print("Expected pop/district: {}".format(ideal_pop))
        
        diffs = [ abs(pop / ideal_pop - 1) for pop in populations.values() ]
        max_diff = max(diffs)
        sum_of_squares = 0
        for d in populations:
            ratio = (populations[d] / ideal_pop - 1) / (max_diff * len(list(populations.values())) ** 0.5)
            square = ratio ** 2
            sum_of_squares += square

        return 1 - (sum_of_squares ** 0.5)

    def demographic_proportions(self, demographic, vap=False): 
        proportions = dict()
        
        for district_id, d in self.districts.items():
            proportions[district_id] = d.demographic_proportion(demographic, vap)

        return proportions 

    def voter_proportions(self, party): 
        proportions = dict()
        
        for district_id, d in self.districts.items():
            proportions[district_id] = d.voting_proportion(party)

        return proportions 
    
    def no_of_opportunity(self, demo, vap=False): 
        count = 0
        if vap:
            for d in self.districts.values():
                if d.is_opportunity(demo, vap=vap):
                    count += 1
        else: 
            for d in self.districts.values():
                if d.is_opportunity(demo, vap=vap):
                    count += 1

        return count

    def no_rep_seats(self):
        rep_share = 0
        for d in self.districts.values():
            is_rep = False
            rep_count = 0

            for p in d.precincts.values():
                if p.voting_history == "R":
                    rep_count += 1
                if (rep_count > len(d.precincts) / 2):
                    is_rep = True
                    break 

            if is_rep:
                rep_share += 1

        return rep_share

    def no_dem_seats(self):
        dem_share = 0
        for d in self.districts.values():
            is_dem = False
            dem_count = 0

            for p in d.precincts.values():
                if p.voting_history == "D":
                    dem_count += 1
                if (dem_count > len(d.precincts) / 2):
                    is_dem = True
                    break 

            if is_dem:
                dem_share += 1

        return dem_share

    def polsby_popper(self):
        pps = dict()
        for d in self.districts.keys():
            pps[d] = self.districts[d].polsby_popper()
        return pps

    def objective_score(self):
        measures = [ self.population_equality_norm(), np.mean(list(self.polsby_popper().values())) ]
        weights = [ 0.7, 0.3 ]
        
        score = sum([
            measure * weight 
            for measure, weight 
            in zip(measures, weights)
        ])
        return score
        
class District():
    def __init__(self, population=None, vap=None, geometry=None, election=None, voting_history=None, precincts=None):
        self.population = population
        self.vap = vap
        self.geometry = geometry
        self.election = election
        self.voting_history = voting_history
        self.precincts = dict() if not precincts else precincts

    def polsby_popper(self):
        geod = Geod(ellps="WGS84")
        area, perimeter = geod.geometry_area_perimeter(self.geometry)
        
        return (4 * math.pi * abs(area))/(perimeter ** 2)
        
    def demographic_proportion(self, demo, vap=False):
        population = 0
        demo_pop = 0

        if vap:
            population = self.vap.number
            demo_pop = self.vap.subtypes[demo].number
        else: 
            population = self.population.number
            demo_pop = self.population.subtypes[demo].number
        
        return demo_pop / population

    def voting_proportion(self, party):
        total_votes = self.election.number
        votes = self.election.subtypes[party].number
        return votes / total_votes

    def is_opportunity(self, demo, vap=False):
        threshold = 0.5
        return self.demographic_proportion(demo, vap) > threshold
        
class Precinct():
    def __init__(self, population=None, vap=None, geometry=None, election=None, voting_history=None):
        self.population = population
        self.vap = vap
        self.geometry = geometry
        self.election = election
        self.voting_history = voting_history
        
class Population():
    def __init__(self, number, type):
        self.number = number
        self.type = type
        self.subtypes = dict()
        
class BoxAndWhisker():
    def __init__(self):
        self.proportions = dict()
        