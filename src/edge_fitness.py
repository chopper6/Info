def population(Gs):
	for G in Gs: assign(G)

def assign(G):
	# assigns fitness to each edge and calcs avg net fitness 
	# curr metric: U+S-R
	# eventually need to generalize to N inputs, and needs to coincide with multivar pids

	pid_metric = 'min>x'
	sum_fitness, num_assigned = 0,0

	for n in G.nodes():
		if G.in_edges(n):
			es = sorted(list(G.in_edges(n)))
			if len(es) == 2:
				e1,e2 = es[0],es[1]
				pid = G.nodes[n]['pid'][pid_metric]
				G[e1[0]][e1[1]]['fitness'] = pid['U1']+pid['S']-pid['R']
				G[e2[0]][e2[1]]['fitness'] = pid['U2']+pid['S']-pid['R']
				sum_fitness += G[e1[0]][e1[1]]['fitness']
				sum_fitness += G[e2[0]][e2[1]]['fitness']
				num_assigned += 2
			else:
				assert(len(es)==1 and n in G.graph['outputs'])
				G[es[0][0]][es[0][1]]['fitness'] = 1 #also a temp fix, H(target)?
				# TODO: need to add fitness to output, presumably just MI?

	G.graph['edge_fitness'] = sum_fitness/len(G.edges())
