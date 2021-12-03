The "flow" currently is:
1. Run build_adj_graph.py. 
	This should fetch the data from the database to produce an adjacency graph that matches the input file format (see the Iowa example). 
	
2. The output is placed into the recom_input folder, as "precincts.json", an adjacency graph of the precincts. 

3. Run the MGGG algorithm on the adjacency graph, ideally on the supercomputer. 
	The MGGG will produce outputs along the name of "recombination_of_districts-x" for some number x. These are new adjacency graphs, though with a format different to the input graph. The "parallelism" is embarrassing in nature, where it basically runs the same script many times. 
	
4. Run calculate_measures.py (misleadingly named, it currently calculates the proportion of a minority group, currently African-Americans), ideally on the supercomputer. 
	This calculates the new polygons and associated populations. The parallelism is of the same nature by which it is called on each of the output files. 
	
5. Run calculate_ensemble_data.py. This parses through all of the output files, and calculates box and whisker data. 