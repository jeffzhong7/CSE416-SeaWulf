import conversion as conv


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
        
    def demographic_proportions(self, demographic): 
        populations = dict()
        demo_pops = dict()
        
        for d in self.districts.keys():
            population = self.districts[d].population
            populations[d] = int(population.number)
            demo_pops[d] = int(population.subtypes[demographic].number)
            
        proportions = [
            demo / total 
            for demo, total 
            in zip(demo_pops.values(), populations.values())
        ]
        
        return dict(zip(self.districts.keys(), proportions))
    
    def no_of_opportunity(self): 
        return 0

    def rep_seat_share(self):
        return 0

    def dem_seat_share(self):
        return 0

    def polsby_popper(self):
        pps = dict()
        for d in self.districts.keys():
            pps[d] = conv.polsby_popper(self.districts[d].geometry)
        return pps

    def objective_score(self):
        measures = [ self.population_equality(), ]
        weights = [ 1, ]
        
        score = sum([
            measure * weight 
            for measure, weight 
            in zip(measures, weights)
        ])
        return score
        
class District():
    def __init__(self, geometry=None, population=None, precincts=None):
        self.geometry = geometry
        self.population = population
        self.precincts = dict() if not precincts else precincts
        
    def is_opportunity(self):
        return True
        
class Precinct():
    def __init__(self, population=None, geometry=None, voting_history=None):
        self.population = population
        self.geometry = geometry
        self.voting_history = voting_history
        
class Population():
    def __init__(self, number, type):
        self.number = number
        self.type = type
        self.subtypes = dict()
        
class BoxAndWhisker():
    def __init__(self):
        self.proportions = dict()
        