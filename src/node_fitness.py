


def population(Gs):
	for G in Gs: assign(G)

def assign(G):
	# assigns fitness to each edge and calcs avg net fitness 
	# curr metric: U+S-R
	# eventually need to generalize to N inputs, and needs to coincide with multivar pids

	pid_metric = 'min>x'
	sum_fitness = 0

	for n in G.graph['hidden']:
		pid = G.nodes[n]['pid'][pid_metric]
		G.nodes[n]['fitness'] = pid['S'] - pid['R']
		sum_fitness += G.nodes[n]['fitness'] 