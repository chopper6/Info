import networkx as nx
from itertools import product

import examples

# TODO: run all nets, only keep those with correct solution
# see gen_Gs
# Then eval those nets for their information
# poss generate net images to help debug
# + a healthy dose of test-based debugging


# input nodes: no op, they given the input of the example
# output nodes: no op, they receive 1 input edge and compare to the output

def gen_graphs(n, ex, debug=False):
    # generates graphs of size n
    input,output = examples.get_io(ex)
    num_out = 1 #TODO: mult outputs

    num_in = len(input)

    assert(n >= num_out + num_in)

    net = nx.DiGraph()
    # TODO: layer -> op, where in+out don't have ops
    for i in range(n):
        if i < num_in: net.add_node(i,op='input')
        elif i < num_in + num_out: net.add_node(i,op='output')
        else: net.add_node(i, op=None)

    nodes_except_out = [i for i in range(n-num_out)] #exclude out_nodes
    out_nodes = [i for i in range(n - num_out,n)] #should be 1 for now
    in_nodes = [i for i in range(num_in)]

    Gs = []
    for out_node in out_nodes:
        Gs += gen_Gs(net,out_node, nodes_except_out, in_nodes, out_nodes)

    len_orig = len(Gs)
    Gs = assign_op_combos(Gs)
    len_final = len(Gs)
    print("Final vs orig Gs lng = " + str(len_orig) + ', ' + str(len_final))


    if debug and False:
        print("\nEnding nets:")
        for G in Gs: print(G.edges())



def assign_op_combos(Gs):
    # assigns all combinations of ops = [and, nand, or, nor]
    # nodes with one input use the same ops, but they are basically = [id, not]
    Gs_opd = []
    ops = ['and','nand','or','nor']

    for G in Gs:
        net = G.copy()
        ordered_nodes = []
        for n in net.nodes():
            if net.nodes[n]['op'] != 'input' and net.nodes[n]['op'] != 'output':
                ordered_nodes += [n]
        prods = product(ops,repeat=len(ordered_nodes))

        for p in prods:
            pnet = net.copy()
            for i in range(len(ordered_nodes)):
                pnet.nodes[ordered_nodes[i]]['op'] = p[i]

            Gs_opd += [pnet]

    return Gs_opd



def has_an_io_path(net, in_nodes, out_nodes):
    # at least one input node must be connected to an output
    for i in in_nodes:
        for o in out_nodes:
            if nx.has_path(net, i,o): return True

    return False



def gen_Gs(net_orig, out_node, nodes, in_nodes, out_nodes):
    # generates acyclic graphs with max 2 in vertices
    # TODO: CLEAN + relax the copying gat dam
    # TODO: rm if no path btwn at least 1 input + output
    # TODO: poss only 1 edge to output, since output nodes don't include an op
    # TODO: generalize to mult out nodes
    # TODO: generalize to 0 in-edges?

    Gs = []
    nodes = nodes.copy()

    for i in range(len(nodes)):
        n=nodes[i]
        net = net_orig.copy()
        net.add_edge(n,out_node)
        #print('new edge = ' + str(n) + ', '+ str(out_node))
        if nx.is_directed_acyclic_graph(net):
            if has_an_io_path(net, in_nodes, out_nodes):
                Gs += [net.copy()]
            #print("Adding net w/ edges: " + str(net.edges()))
            nodes_copy = nodes.copy()
            del nodes_copy[i]

            if net.nodes[n]['op'] != 'input':
                #print("Searching for nets from node: " + str(n) + ", curr edges: " + str(net.edges()) + ", avail nodes = " + str(nodes))
                Gs += gen_Gs(net, n, nodes_copy, in_nodes, out_nodes)

            if net.nodes[n]['op'] != 'output': #output nodes do not have an op, so take only 1 in_edge
                for j in range(i,len(nodes_copy)):
                    m = nodes_copy[j]
                    met = net.copy()
                    met.add_edge(m, out_node)

                    if nx.is_directed_acyclic_graph(met):
                        if has_an_io_path(met, in_nodes, out_nodes):
                            Gs += [met.copy()]

                        if met.nodes[m]['op'] != 'input':
                            nodes_copy2 = nodes_copy.copy()
                            del nodes_copy2[j]
                            Gs += gen_Gs(met, m, nodes_copy2, in_nodes, out_nodes)



    return Gs



# just for testing purposes
n = 5
ex = 'pwunq'
gen_graphs(n,ex, debug=True)