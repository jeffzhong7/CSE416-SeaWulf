class Districting():
    def __init__(self, districts=None):
        self.districts = dict() if not districts else districts
        
class District():
    def __init__(self, geometry=None, population=None, precincts=None):
        self.geometry = geometry
        self.population = population
        self.precincts = dict() if not precincts else precincts
        
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
        