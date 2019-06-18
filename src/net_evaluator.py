import pr, draw_nets
from info_fns import *
from util import *

#TODO: reorganize to be cleaner with previous build?

def eval(Gs,out_dir, hnormz=False):
	#pid_keys = ['<i>x','<i>y']

	net_PIDs, node_PIDs = [], []
	for G in Gs:
		PIDs = []
		for j in rng(G.graph['hidden']):
			n = G.graph['hidden'][j]
			if len(G.in_edges(n)) == 2:
				PIDs += [eval_node_horz_PID(G,n,hnormz = hnormz)]

			else: assert(False)

		net_PIDs += [merge_node_PIDs(PIDs)]
		node_PIDs += [PIDs]

		#path_pids(G,G.graph['inputs'])

	return net_PIDs, node_PIDs


def merge_node_PIDs(PIDs):
	PID_total = {k:{'R':0, 'U1':0,'U2':0, 'S':0} for k in PIDs[0].keys()}
	for pid in PIDs:
		for k in pid.keys():
			for p in pid[k].keys():
				PID_total[k][p] += pid[k][p]

	return PID_total


def get_inputs(net,node):
	es = list(net.in_edges(node))
	e1, e2 = es[0][0],es[1][0]
	inputs = [net.nodes[e1]['hist'],net.nodes[e2]['hist']]
	return inputs

def eval_node_horz_PID(net,node, hnormz=False, output_choice='immed'):
	assert(len(net.graph['outputs']) == 1)

	inputs = get_inputs(net, node)
	if output_choice == 'final': output = net.nodes[net.graph['outputs'][0]]['hist']
	elif output_choice == 'immed': output = net.nodes[node]['hist']
	else: assert(False) #unknown 'output_choice'

	pids =  eval_node_PID(net, inputs, output, hnormz=hnormz)
	net.node[node]['pid'] = pids
	return pids



def path_pids(G):
	# curr very inefficient...only good for small nets
	
	# init reset
	for n in G.graph['hidden'] + G.graph['output']:
		G.node[n]['pid_path'] = None

	# assign pid paths
	done=False
	z=0
	while not done:
		done=True
		for n in G.graph['hidden']:
			ready=True
			for e in G.in_edges(n): #TODO: add input node handling
				if e[0] not in G.graph['inputs']:
					if G.node[e[0]]['pid_path'] is None:
						ready=done=False
						break
			if ready: a_node_path_pid(G, n)
		z+=1
		if z==10000:
			print("ERROR: infinite loop in path_pids()")
			assert(False)



def a_node_path_pid(G, node):
	# TODO: figure out how to really merge uneven amts of S from the inptus
	assert(False) #incomplete
	


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

def eval_node_PID(net,input,output,hnormz=False, x1x2logbase=4):
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
	Rs = R(Pr, Al, num_inst, hnormz=hnormz)
	PIDs = PID_decompose(Rs, Pr, print_PID=False, hnormz=hnormz, x1x2logbase=x1x2logbase)
	return PIDs



def R(Pr, Al, num_inst, hnormz=False):
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
			if hnormz: r[i]['min>x'] = min(partial_info(Pr,Al,'y','x1',i)/h(Pr[i],'x1'),partial_info(Pr,Al,'y','x2',i)/h(Pr[i],'x2'))
			else: r[i]['min>x'] = min(partial_info(Pr,Al,'y','x1',i),partial_info(Pr,Al,'y','x2',i))
			
			# PARTIAL Y
			if hnormz: r[i]['min>y'] = min(partial_info(Pr, Al,'x1','y', i)/h(Pr[i],'y'), partial_info(Pr, Al, 'x2','y', i)/h(Pr[i],'y'))
			else: r[i]['min>y'] = min(partial_info(Pr, Al,'x1','y', i), partial_info(Pr, Al, 'x2','y', i))
			

	# AVERAGE pointwise r -> R
	R = {k: 0 for k in cand_keys}
	for i in range(num_inst):
		for k in cand_keys:
			R[k] += r[i][k]
	for k in cand_keys:
		R[k] /= num_inst

	return R


def PID_decompose(R, Pr, print_PID=True, hnormz=False, x1x2logbase=4):
	# note that earlier sense of R[i] would have to be avg'd for R


	U1, U2, S =  Info(Pr,'x1','y'),  Info(Pr,'x2','y'), Info(Pr,'x1,x2','y')

	if hnormz:

		if Info(Pr,'x1','y')!=0:	
			U1y = U1/H(Pr,'y')
			U1 /= H(Pr,'x1')
		else: U1y=U1
		if Info(Pr,'x2','y')!=0:
			U2y = U2/H(Pr,'y')
			U2 /= H(Pr,'x2')
		else: U2y=U2
		if Info(Pr,'x1,x2','y')!=0: 
			Sy = S/	H(Pr,'y')
			S /= H(Pr,'x1,x2',logbase=x1x2logbase)
		else:Sy=S


	PID = {k:{'R':R[k], 'U1':U1, 'U2':U2, 'S':S}
		   for k in R.keys()}
	if hnormz: PID['min>y'] = {'R':R['min>y'], 'U1':U1y, 'U2':U2y, 'S':Sy}

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