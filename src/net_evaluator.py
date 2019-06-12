import pr, draw_nets
from info_fns import *
from util import *

#TODO: reorganize to be cleaner with previous build?

def eval(Gs,out_dir):
	#pid_keys = ['<i>x','<i>y']
	net_PIDs, node_PIDs = [], []
	for G in Gs:
		PIDs = []
		for j in rng(G.graph['hidden']):
			n = G.graph['hidden'][j]
			if len(G.in_edges(n)) == 2:
				PIDs += [eval_node_horz_PID(G,n)]

			# nodes with 1 edge have entirely unique1 info
			if len(G.in_edges(n)) == 1:
				in_edges = list(G.in_edges(n))
				e1 = in_edges[0][0]
				dummy_input = [0 for i in rng(G.nodes[e1]['hist'])]
				input = [G.nodes[e1]['hist'], dummy_input]
				#output = G.nodes[G.graph['outputs'][0]]['hist']
				output = G.nodes[n]['hist']
				PIDs += [eval_node_PID(G, input, output,x1x2logbase=2)]

		net_PIDs += [merge_node_PIDs(PIDs)]
		node_PIDs += [PIDs]

	return net_PIDs, node_PIDs


def merge_node_PIDs(PIDs):
	PID_total = {k:{'R':0, 'U1':0,'U2':0, 'S':0} for k in PIDs[0].keys()}
	for pid in PIDs:
		for k in pid.keys():
			for p in pid[k].keys():
				PID_total[k][p] += pid[k][p]

	return PID_total



def eval_node_horz_PID(net,node):
	assert(len(net.graph['outputs']) == 1)

	es = list(net.in_edges(node))
	e1, e2 = es[0][0],es[1][0]
	input = [net.nodes[e1]['hist'],net.nodes[e2]['hist']]
	#output = net.nodes[net.graph['outputs'][0]]['hist']
	output = net.nodes[node]['hist']

	return eval_node_PID(net, input, output)


def eval_node_vert_PIDs(net, node):
	# BAD IDEA!!!

	PIDs = []
	for e in net.in_edges(node):
		e1 = e[0]
		input = [net.nodes[e1]['hist'],net.nodes[node]['hist']]
		#output = net.nodes[net.graph['outputs'][0]]['hist']
		output = net.nodes[node]['hist']
		PIDs += [eval_node_PID(net,input,output)]
	return PIDs

def eval_node_PID(net,input,output,x1x2logbase=4):
	assert(len(net.graph['outputs']) == 1)
	num_inst = len(input[0])

	# get pr's aligned by instances
	pr_y, pr_x, pr_xx, pr_xy, pr_xxy, aligned_inputs, aligned_outputs = pr.find_prs_aligned(input, output,
																							debug=False,
																							disordered=False)
	Al = {'x1': aligned_inputs[0], 'x2': aligned_inputs[1], 'y': aligned_outputs}  # alphabet dict

	# probability atom plots
	Pr, p_keys = pr.build_p_atoms(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, num_inst)

	# PID candidates
	Rs = R(Pr, Al, num_inst)
	PIDs = PID_decompose(Rs, Pr, print_PID=False, x1x2logbase=x1x2logbase)
	return PIDs



def R(Pr, Al, num_inst):
	#TODO: add back some candidates that I like less to compare with

	# requires a set of alphabets and probabilities
	# where Pr[i].keys() = 'x1','x2','x1,y','x2,y','x1,x2','x1,x2,y' ....???
	# Al[i].keys() = 'x1', 'x2', 'y'

	# with MANY instances, this becomes VERY INEFFICIENT
	# since partial info is computed over each m instances -> O(m^2)
	# however, I assume that instances remain near m=4

	cand_keys =  ['min>x', 'min>y']

	r = [{k:0 for k in cand_keys} for i in range(num_inst)]

	for i in range(num_inst):
		# PARTIAL X
		if info(Pr[i],'y','x1') == 0 or info(Pr[i],'y','x2') == 0: 
			r[i]['min>x'] = 0
			r[i]['min>y'] = 0
		else: 
			#r[i]['min>x'] = min(partial_info(Pr,Al,'y','x1',i),partial_info(Pr,Al,'y','x2',i))
			r[i]['min>x'] = min(partial_info(Pr,Al,'y','x1',i)/h(Pr[i],'x1'),partial_info(Pr,Al,'y','x2',i)/h(Pr[i],'x2'))

			# PARTIAL Y
			#r[i]['min>y'] = min(partial_info(Pr, Al,'x1','y', i), partial_info(Pr, Al, 'x2','y', i))
			r[i]['min>y'] = min(partial_info(Pr, Al,'x1','y', i)/h(Pr[i],'y'), partial_info(Pr, Al, 'x2','y', i)/h(Pr[i],'y'))

	# AVERAGE pointwise r -> R
	R = {k: 0 for k in cand_keys}
	for i in range(num_inst):
		for k in cand_keys:
			R[k] += r[i][k]
	for k in cand_keys:
		R[k] /= num_inst

	return R


def PID_decompose(R, Pr, print_PID=True, normz=True, x1x2logbase=4):
	# note that earlier sense of R[i] would have to be avg'd for R


	if Info(Pr,'x1','y')==0:	
		U1 = 0
	else: 
		U1 = Info(Pr,'x1','y')/H(Pr,'x1')
	if Info(Pr,'x2','y')==0:
		U2 = 0
	else: 
		U2 = Info(Pr,'x2','y')/H(Pr,'x2')
	if Info(Pr,'x1,x2','y')==0: 	
		S=0
	else: 
		S=Info(Pr,'x1,x2','y')/H(Pr,'x1,x2',logbase=x1x2logbase)


	PID = {k:{'R':R[k], 'U1':U1, 'U2':U2, 'S':S}
		   for k in R.keys()}

	for k in PID.keys():

		PID[k]['U1'] -= PID[k]['R']
		PID[k]['U2'] -= PID[k]['R']
		PID[k]['S'] -= (PID[k]['U1'] + PID[k]['U2'] + PID[k]['R'])

		for p in ['R', 'U1', 'U2', 'S']:
			PID[k][p] = round(PID[k][p],8) #rounding

		if print_PID:
			print('\n' + k + ':')
			for p in ['R','U1','U2','S']:
				print(p + ' = ' + str(PID[k][p]))

	return PID