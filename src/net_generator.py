import networkx as nx, pickle,os
from itertools import product
from util import *
import inform_nets
from time import time 

import examples, run_fwd, draw_nets, net_evaluator

# TODO: a healthy dose of test-based debugging
# TODO: organization relative to PID tester

# input nodes: no op, they given the input of the example
# output nodes: no op, they receive 1 input edge and compare to the output

def gen_graphs(n, ex, out_dir, protocol='combos', debug=False, draw=False):
    # generates graphs of size n
    input,output = examples.get_io(ex)
    num_out = 1 #TODO: mult outputs

    if protocol == 'combos': series = False
    elif protocol == 'series': series = True
    else: assert(False) #unknown gen_graphs() protocol

    num_in = len(input)

    assert(n >= num_out + num_in)

    net = nx.DiGraph()
    net.graph['inputs'] = [i for i in range(num_in)]
    net.graph['hidden'] = [] #add dynamically during gen_Gs
    hidden_nodes = [i for i in range(num_in, n-num_out)]
    net.graph['outputs'] = [i for i in range(n - num_out,n)]

    for i in range(n): #hidden nodes are NOT added here, but are recursively added during gen_Gs()
        if i < num_in: net.add_node(i,layer='input', op='input')
        elif i >= n - num_out: net.add_node(i,layer='output', op='output')
        #else: net.add_node(i, layer='hidden')

    if debug: init_t = time()
    dyn_trim=True

    # NOTE: need 'short_cut=False' for mult k-AND path-lng archs
    short_cut = False
    if short_cut: print("\nWARNING: short_cut is ON, cannot generate mult k-AND path-lng architectures.")
    Gs = gen_Gs(net, net.graph['outputs'], net.graph['inputs'], hidden_nodes, short_cut=short_cut, series=series, dyn_trim=dyn_trim)

    if debug: prev_t = time_n_print(init_t, Gs, 'generate Gs')

    if not dyn_trim: 
        rm_repeats(Gs)
        if debug: prev_t = time_n_print(prev_t,Gs,'trim repeats')

    Gs = rm_inversions(Gs)
    if debug: prev_t = time_n_print(prev_t, Gs, 'trim hidden inversions')

    #draw_nets.save_mult(Gs, out_dir)
    #assert(False)

    inform_nets.picklem(Gs, out_dir, n, chkpt='pre-combos')

    Gs = assign_op_combos(Gs, ex, Edge_Ops=['id','not'], Node_Ops=['and'], all_in_edges_same=True, dyn_trim=False) #dyn_trim only useful if gen huge # of graphs --> mem problem
    if debug: prev_t = time_n_print(prev_t, Gs, 'assign op combos')

    check(Gs, series)
    inform_nets.picklem(Gs, out_dir, n, chkpt='size-specific')
    
    Gs, all_Gs = keep_correct(Gs, ex)


    if debug: prev_t = time_n_print(prev_t, Gs, 'check and filter correct Gs')
    inform_nets.picklem(Gs, out_dir, n, ex=ex, chkpt='ex-specific')
    #TODO: add all_Gs to picklem

    if draw: draw_nets.save_mult(Gs, out_dir)

    return Gs, all_Gs


def time_n_print(prev_t, Gs, name):
    t= time()
    print("\n# Gs = " + str(len(Gs)))
    print("Time to " + name  + " = " + str(t - prev_t) + ' sec')
    return t


def keep_correct(Gs, ex):
    correct_Gs = []
    for G in Gs:
        accuracy, acc_entropy = run_fwd.all_instances(G, ex)
        G.graph['accuracy'] = accuracy
        G.graph['accuracy_entropy'] = acc_entropy

        if accuracy == 1: 
            correct_Gs += [G]
            G.graph['correct'] = True
        else: G.graph['correct'] = False
    return correct_Gs, Gs


def rm_repeats(Gs):
    dels = []
    for i in range(len(Gs)):
        rmd = False
        for j in range(i):
            if rmd: break

            elif Gs[i].edges() == Gs[j].edges():
                dels += [i]
                rmd = True


    for d in range(len(dels)):
        del Gs[dels[d]]
        for e in range(len(dels)): dels[e]-=1

    return Gs

def rm_inversions(Gs, ops=False, in_out_too = False):
            
    dels = []
    for i in range(len(Gs)):
        rmd = False
        for j in range(i):
            if rmd: break
            i_nodes, j_nodes = sorted(Gs[i].graph['hidden']), sorted(Gs[j].graph['hidden'])

            if i_nodes == j_nodes:
                i_in_degs = [len(Gs[i].in_edges(h)) for h in sorted(list(Gs[i].nodes()))]
                j_in_degs = [len(Gs[j].in_edges(h)) for h in sorted(list(Gs[j].nodes()))]
                if i_in_degs == j_in_degs:
                    i_out_degs = [len(Gs[i].out_edges(h)) for h in sorted(list(Gs[i].nodes()))]
                    j_out_degs = [len(Gs[j].out_edges(h)) for h in sorted(list(Gs[j].nodes()))]

                    if i_out_degs == j_out_degs:
                        diff = False
                        for k in rng(sorted(Gs[i].graph['hidden'])):
                            if diff: break
                            i_in_inputs, j_in_inputs = 0,0
                            i_node, j_node = i_nodes[k], j_nodes[k]
                            for e in Gs[i].in_edges(i_node):
                                if e[0] in Gs[i].graph['inputs']: i_in_inputs += 1
                            for e in Gs[j].in_edges(j_node):
                                if e[0] in Gs[j].graph['inputs']: j_in_inputs += 1
                            if i_in_inputs != j_in_inputs: 
                                diff=True
                                break

                        if not diff:
                            dels +=[i]
                            rmd = True


    for d in range(len(dels)):
        del Gs[dels[d]]
        for e in range(len(dels)): dels[e]-=1

    return Gs


def assign_op_combos(Gs, ex, dyn_trim=False, all_in_edges_same=False, Edge_Ops=None, Node_Ops=['and']):
    
    input_edges_id = False
    if input_edges_id: print("\nWARNING assign_op_combos(): all out edges from inputs given 'id' op.\n")
    
    Gs_opd = []
    if Edge_Ops is None: Edge_Ops = ['id','not'] #capital to distinguish from later loop

    for G in Gs:
        net = G.copy()    
        nodes_w_ops = net.graph['hidden'] #+ net.graph['outputs']

        if all_in_edges_same:
            assert(not input_edges_id)
            assert(Node_Ops == ['and'])
            for n in nodes_w_ops:
                net.nodes[n]['op'] = 'and'
            
            #poss creates an extra copy, but need to cover case where direct in->out edge
            node_in_prods = product(Edge_Ops,repeat=len(nodes_w_ops))
            node_out_prods = product(Node_Ops,repeat=len(nodes_w_ops))
            prods = product(node_in_prods,node_out_prods)

            for p in prods:
                node_in_ops,node_out_ops = p[0],p[1]
                pnet = net.copy()
                nodes_w_ops_copy = nodes_w_ops.copy() #prob not nec

                for i in rng(node_out_ops):
                    h = nodes_w_ops[i]
                    for e in pnet.out_edges(h):
                        pnet[e[0]][e[1]]['op'] = node_out_ops[i]

                for i in rng(node_in_ops):
                    h = nodes_w_ops_copy[i]
                    for e in pnet.in_edges(h):
                        pnet[e[0]][e[1]]['op'] = node_in_ops[i]

                if dyn_trim: 
                    accuracy = run_fwd.all_instances(pnet, ex)
                    if accuracy == 1: 
                        Gs_opd += [pnet]
                        if len(Gs_opd) % 100 == 0: print('assign_op_combos() found ' + str(len(Gs_opd)) + ' correct nets so far.')
                
                else: Gs_opd += [pnet]


        else:

            if input_edges_id:
                for e in net.out_edges(net.graph['inputs']):
                    net[e[0]][e[1]]['op'] = 'id'
                ordered_edges = list(net.out_edges(net.graph['hidden']))
            else: ordered_edges = list(net.out_edges(net.graph['hidden']+net.graph['inputs']))

            edge_prods = product(Edge_Ops,repeat=len(ordered_edges))
            node_prods = product(Node_Ops,repeat=len(nodes_w_ops))
            prods = product(edge_prods,node_prods)

            for p in prods:
                edge_ops,node_ops = p[0],p[1]
                pnet = net.copy()
                ord_es = ordered_edges.copy()
                assert(len(node_ops) == len(nodes_w_ops) and len(ord_es) == len(edge_ops))
                for i in rng(node_ops):
                    pnet.nodes[nodes_w_ops[i]]['op'] = node_ops[i]
                for i in rng(edge_ops):
                    e1,e2 = ord_es[i][0], ord_es[i][1]
                    pnet[e1][e2]['op'] = edge_ops[i]

                if dyn_trim: 
                    accuracy = run_fwd.all_instances(pnet, ex)
                    if accuracy == 1: 
                        Gs_opd += [pnet]
                        if len(Gs_opd) % 100 == 0: print('assign_op_combos() found ' + str(len(Gs_opd)) + ' correct nets so far.')
                else: Gs_opd += [pnet]

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

def all_hidden_in_deg(net):
    for h in net.graph['hidden']:
        if len(net.in_edges(h)) != 2: return False
    return True

def check(Gs, series):
    for G in Gs:
        assert(nx.is_directed_acyclic_graph(G))
        assert(has_an_io_path(G))
        assert(all_hidden_btwn_io(G))
        if series:
            for h in G.graph['hidden']:
                assert(len(G.in_edges(h))==2)
        for i in G.graph['inputs']:
            assert(len(G.in_edges(i)) == 0)
            assert(G.nodes[i]['layer']=='input')
        for o in G.graph['outputs']:
            assert(G.nodes[o]['layer']=='output')
            assert(len(G.in_edges(o)) in [1,2])
            assert(len(G.out_edges(o)) == 0)


def choose_source(net, sources, target_node):
    for i in rng(sources):
        if not net.has_edge(sources[i],target_node):
            return i
    return None

def gen_Gs(net_orig, target_nodes, input_nodes, hidden_nodes,short_cut=False,dyn_trim=True,series=False,max_in_degree=2, verbose=True):
    # calls rm_repeats(Gs) as Gs are built, which dramatically reduces run time
    # "series" arg refers to a population of graphs built on consecutive correct subgraphs

    Gs = []
    for t in rng(target_nodes):
        # terminate this branch if target_node already has enough edges
        num_edges = max_in_degree
        if len(net_orig.in_edges(target_nodes[t])) == num_edges: done=True
        else: done=False

        if not done:


            for i in rng(net_orig.graph['inputs']):
                if short_cut: #basically overrides the for loop above
                    chosen= choose_source(net_orig, input_nodes, target_nodes[t])
                    if chosen is not None:    i=chosen

                if not net_orig.has_edge(net_orig.graph['inputs'][i],target_nodes[t]):

                    net = net_orig.copy()
                    net.add_edge(input_nodes[i],target_nodes[t])
                    if nx.is_directed_acyclic_graph(net):
                        proper=False
                        if has_an_io_path(net) and all_hidden_btwn_io(net):
                            proper = True
                            if all_hidden_in_deg(net): Gs += [net.copy()]

                        if proper or not series:
                            # try again with same target node with new input node attached
                            Gs += gen_Gs(net, target_nodes, input_nodes, hidden_nodes, series=series, short_cut=short_cut)
                            if dyn_trim: rm_repeats(Gs)

                if short_cut: break #basically overrides the for loop above


            chosen = choose_source(net_orig, hidden_nodes, target_nodes[t])
            if chosen is not None:
                i=chosen

                net = net_orig.copy()

                #TODO: this is fucking stupid, make my own copy fn()?
                net.graph['hidden'] = net_orig.graph['hidden'].copy()
                net.add_node(hidden_nodes[i], op=None, layer='hidden')
                if hidden_nodes[i] not in net.graph['hidden']:
                    net.graph['hidden'] += [hidden_nodes[i]]

                net.add_edge(hidden_nodes[i],target_nodes[t])

                if nx.is_directed_acyclic_graph(net):
                    if series:
                        proper = False
                        if has_an_io_path(net) and all_hidden_btwn_io(net):
                            if all_hidden_in_deg(net): Gs += [net.copy()]
                            proper=True

                    if proper or not series:
                        # try again with same target node with new hidden node attached
                        Gs += gen_Gs(net, target_nodes, input_nodes, hidden_nodes, series=series, short_cut=short_cut)
                        if dyn_trim: rm_repeats(Gs)

                    # try again with the hidden node as the new target
                    # hidden_node[i] rm'd since would always cause a cycle
                    new_hidden_nodes = hidden_nodes.copy()
                    del new_hidden_nodes[i]
                    Gs += gen_Gs(net, target_nodes + [hidden_nodes[i]], input_nodes, new_hidden_nodes, series=series, short_cut=short_cut)
                    if dyn_trim: rm_repeats(Gs)
    return Gs



