import networkx as nx, pickle,os
from itertools import product
from util import *
import inform_nets
from time import time 

import examples, run_fwd, draw_nets, net_evaluator

# TODO: a healthy dose of test-based debugging
# TODO: poss seperate this completely from the PID tester? or at least diff subfolders?
# TODO: scaling issues, too many combo['op'] graphs, leading to v slow keep_correct()


# input nodes: no op, they given the input of the example
# output nodes: no op, they receive 1 input edge and compare to the output

def gen_graphs(n, ex, out_dir, debug=False, draw=False):
    # generates graphs of size n
    input,output = examples.get_io(ex)
    num_out = 1 #TODO: mult outputs

    num_in = len(input)

    assert(n >= num_out + num_in)

    net = nx.DiGraph()
    net.graph['inputs'] = [i for i in range(num_in)]
    net.graph['hidden'] = [] #add dynamically during gen_Gs
    hidden_nodes = [i for i in range(num_in, n-num_out)]
    net.graph['outputs'] = [i for i in range(n - num_out,n)]

    for i in range(n): #hidden nodes are NOT added here, but are recursively added during gen_Gs()
        if i < num_in: net.add_node(i,op='input')
        elif i >= n - num_out: net.add_node(i,op='output')
        #else: net.add_node(i, op=None)

    if debug: init_t = time()
    Gs = gen_Gs(net, net.graph['outputs'], net.graph['inputs'], hidden_nodes)

    if debug: prev_t = time_n_print(init_t, Gs, 'generate Gs')

    Gs = rm_repeats(Gs)
    if debug: prev_t = time_n_print(prev_t, Gs, 'trim Gs')

    Gs = rm_hidden_repeats(Gs)
    if debug: prev_t = time_n_print(prev_t, Gs, 'trim hidden inversions')

    #draw_nets.save_mult(Gs, out_dir)
    #assert(False)

    Gs = assign_op_combos(Gs)
    if debug: prev_t = time_n_print(prev_t, Gs, 'assign op combos')

    #Gs = rm_op_repeats(Gs)
    print('\nWARNING: not filtering op repeats')
    if debug: prev_t = time_n_print(prev_t, Gs, 'trim op combos')

    check(Gs)
    inform_nets.picklem(Gs, out_dir, n)
    Gs = keep_correct(Gs, ex)
    if debug: prev_t = time_n_print(prev_t, Gs, 'check and filter correct Gs')

    if draw: draw_nets.save_mult(Gs, out_dir)

    return Gs


def time_n_print(prev_t, Gs, name):
    t= time()
    print("\n# Gs = " + str(len(Gs)))
    print("Time to " + name  + " = " + str(t - prev_t) + ' sec')
    return t


def keep_correct(Gs, ex):
    correct_Gs = []
    for G in Gs:
        accuracy = run_fwd.all_instances(G, ex)
        if accuracy == 1: correct_Gs += [G]
    return correct_Gs

def rm_repeats(Gs):
    dels = []
    for i in range(len(Gs)):
        rmd = False
        for j in range(i):
            if rmd: break
            if Gs[i].edges() == Gs[j].edges():
                dels += [i]
                rmd = True

    for d in range(len(dels)):
        del Gs[dels[d]]
        for e in range(len(dels)): dels[e]-=1

    return Gs

def rm_hidden_repeats(Gs, ops=False):
    #TODO: woah damn, clean this filthy ass mess
    #TODO: likely cuts too many nets in the case of asym inputs...

    dels = []
    for i in range(len(Gs)):
        rmd = False
        for j in range(i):
            if rmd: break
            #TODO: poss for 2 acyclic nets with same in an out degrees for all hidden nodes to have different connectivity?
            if sorted(Gs[i].graph['hidden']) == sorted(Gs[j].graph['hidden']):
                i_in_degs = [len(Gs[i].in_edges(h)) for h in sorted(list(Gs[i].nodes()))]
                j_in_degs = [len(Gs[j].in_edges(h)) for h in sorted(list(Gs[j].nodes()))]
                if i_in_degs == j_in_degs:
                    i_out_degs = [len(Gs[i].out_edges(h)) for h in sorted(list(Gs[i].nodes()))]
                    j_out_degs = [len(Gs[j].out_edges(h)) for h in sorted(list(Gs[j].nodes()))]

                    if i_out_degs == j_out_degs:
                        same_paths=True
                        for in_ in rng(Gs[i].graph['inputs']):
                            for out_ in rng(Gs[i].graph['outputs']):
                                input_i, output_i = sorted(Gs[i].graph['inputs'])[in_], sorted(Gs[i].graph['outputs'])[out_]
                                input_j, output_j = sorted(Gs[j].graph['inputs'])[in_], sorted(Gs[j].graph['outputs'])[out_]
                                
                                paths_i, lng_paths_i = nx.all_simple_paths(Gs[i], input_i, output_i), []
                                if ops: op_paths_i = []
                                for p in paths_i: 
                                    lng_paths_i += [len(p)]
                                    if ops: op_paths_i += [[Gs[i].nodes[p[n]]['op'] for n in rng(p)]]

                                paths_j, lng_paths_j = nx.all_simple_paths(Gs[j], input_j, output_j), []
                                if ops: op_paths_j = []
                                for p in paths_j: 
                                    lng_paths_j += [len(p)]
                                    if ops: op_paths_j += [[Gs[j].nodes[p[n]]['op'] for n in rng(p)]]

                                if sorted(lng_paths_i) != sorted(lng_paths_j):
                                    if ops:
                                        if sorted(op_paths_i) != sorted(op_paths_j):
                                            same_paths=False
                                            break
                                    else:
                                        same_paths=False
                                        break

                        if same_paths:
                            dels +=[i]
                            rmd = True


    for d in range(len(dels)):
        del Gs[dels[d]]
        for e in range(len(dels)): dels[e]-=1

    return Gs


def rm_op_repeats(Gs):
    dels = []
    for i in range(len(Gs)):
        rmd = False
        for j in range(i):
            if rmd: break
            if sorted(Gs[i].edges()) == sorted(Gs[j].edges()):
                if Gs[i].nodes(data=True) == Gs[j].nodes(data=True):
                    dels += [i]
                    rmd = True

    for d in range(len(dels)):
        del Gs[dels[d]]
        for e in range(len(dels)): dels[e]-=1

    return Gs


def assign_op_combos(Gs):
    # assigns all combinations of ops = [and, nand, or, nor]
    # nodes with one input use the same ops, but they are basically = [id, not]
    Gs_opd = []
    ops1 = ['id','not']
    ops2 = ['and','nand','or','nor']

    for G in Gs:
        net = G.copy()
        h1,h2 = 0,0
        for h in net.graph['hidden']:
            if len(net.in_edges(h)) == 1: h1 += 1
            elif len(net.in_edges(h)) == 2: h2 += 1
            else: assert(False)

        prods1 = list(product(ops1,repeat=h1))
        prods2 = list(product(ops2,repeat=h2))
        prods = list(product(prods1,prods2))
        #but then need all combos of these 2 subsets...

        for p in prods:
            p1,p2 = p[0],p[1]
            pnet = net.copy()
            i1,i2 = 0,0
            for i in range(len(net.graph['hidden'])):
                h = net.graph['hidden'][i]
                if len(pnet.in_edges(h)) == 1:
                    pnet.nodes[h]['op'] = p1[i1]
                    i1+=1
                elif len(pnet.in_edges(h)) == 2:
                    pnet.nodes[h]['op'] = p2[i2]
                    i2+=1
                else: assert(False)
            Gs_opd += [pnet]

    return Gs_opd



def has_an_io_path(net):
    # for each output, at least one input node must be along a path to the output
    for o in net.graph['outputs']:
        o_path = False
        for i in net.graph['inputs']:
            if nx.has_path(net, i,o): o_path=True
        if not o_path: return False

    return True

def all_hidden_btwn_io(net):
    for h in net.graph['hidden']:
        if len(net.in_edges(h))==0 or len(net.out_edges(h))==0: return False

        ih_path, ho_path = False, False
        for i in net.graph['inputs']:
            if nx.has_path(net, i,h): ih_path=True
        for o in net.graph['outputs']:
            if nx.has_path(net, h,o): ho_path=True
        if not ih_path and ho_path: return False

    return True


def check(Gs):
    for G in Gs:
        assert(nx.is_directed_acyclic_graph(G))
        assert(has_an_io_path(G))
        assert(all_hidden_btwn_io(G))
        for i in G.graph['inputs']:
            assert(len(G.in_edges(i)) == 0)
            assert(G.nodes[i]['op']=='input')
        for o in G.graph['outputs']:
            assert(G.nodes[o]['op']=='output')
            assert(len(G.in_edges(o)) < 2)
            assert(len(G.out_edges(o)) == 0)



def gen_Gs(net_orig, target_nodes, input_nodes, hidden_nodes,max_in_degree=2, verbose=True):

    Gs = []
    for t in rng(target_nodes):
        # terminate this branch if target_node already has enough edges
        if net_orig.nodes[target_nodes[t]]['op'] == 'output': num_edges = 1
        else: num_edges = max_in_degree
        if len(net_orig.in_edges(target_nodes[t])) == num_edges: done=True
        else: done=False

        if not done:
            # try starting with all input_nodes
            for i in range(len(input_nodes)):
                if not net_orig.has_edge(input_nodes[i], target_nodes[t]):
                    net = net_orig.copy()
                    net.add_edge(input_nodes[i],target_nodes[t])
                    new_input_nodes = input_nodes.copy()
                    del new_input_nodes[i]
                    if nx.is_directed_acyclic_graph(net):
                        if has_an_io_path(net)and all_hidden_btwn_io(net):
                            Gs += [net.copy()]

                        # try again with same target node with new input node attached
                        Gs += gen_Gs(net, target_nodes, input_nodes, hidden_nodes)


            for i in range(len(hidden_nodes)):
                if not net_orig.has_edge(hidden_nodes[i],target_nodes[t]):
                    net = net_orig.copy()

                    #TODO: this is fucking stupid, make my own copy fn()?
                    net.graph['hidden'] = net_orig.graph['hidden'].copy()
                    net.add_node(hidden_nodes[i], op=None)
                    if hidden_nodes[i] not in net.graph['hidden']:
                        net.graph['hidden'] += [hidden_nodes[i]]

                    net.add_edge(hidden_nodes[i],target_nodes[t])
                    new_hidden_nodes = hidden_nodes.copy()
                    del new_hidden_nodes[i]
                    if nx.is_directed_acyclic_graph(net):

                        if has_an_io_path(net) and all_hidden_btwn_io(net):
                            Gs += [net.copy()]

                        # try again with same target node with new hidden node attached
                        Gs += gen_Gs(net, target_nodes, input_nodes, hidden_nodes)

                        # try again with the hidden node as the new target
                        # hidden_node[i] rm'd since would always cause a cycle
                        Gs += gen_Gs(net, target_nodes + [hidden_nodes[i]], input_nodes, new_hidden_nodes)

    return Gs



