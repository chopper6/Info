import networkx as nx
from itertools import product

import examples, run_fwd

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
    net.graph['inputs'] = [i for i in range(num_in)]
    net.graph['hidden'] = [i for i in range(num_in, n-num_out)]
    net.graph['outputs'] = [i for i in range(n - num_out,n)]
    # TODO: layer -> op, where in+out don't have ops
    for i in range(n):
        if i < num_in: net.add_node(i,op='input')
        elif i < num_in + num_out: net.add_node(i,op='output')
        else: net.add_node(i, op=None)

    Gs = []
    for out_node in net.graph['outputs']:
        Gs += gen_Gs(net,out_node, nodes_except_out, in_nodes, out_nodes)

    len_orig = len(Gs)
    Gs = assign_op_combos(Gs)
    len_final = len(Gs)
    if debug: print("\nComboOpsGs vs OrigGs lng = " + str(len_orig) + ', ' + str(len_final) + '\n')


    check(Gs)
    Gs = keep_correct(Gs, ex)
    if debug: print("CorrectGs remaining lng = " + str(len(Gs)))


    if debug and False:
        print("\nEnding nets:")
        for G in Gs: print(G.edges())



def keep_correct(Gs, ex):
    correct_Gs = []
    for G in Gs:
        accuracy = run_fwd.all_instances(G, ex)
        if accuracy == 1: correct_Gs += [G]
    return correct_Gs

def assign_op_combos(Gs):
    # assigns all combinations of ops = [and, nand, or, nor]
    # nodes with one input use the same ops, but they are basically = [id, not]
    Gs_opd = []
    ops = ['and','nand','or','nor']

    for G in Gs:
        net = G.copy()
        prods = product(ops,repeat=len(net.graph['hidden']))

        for p in prods:
            pnet = net.copy()
            for i in range(len(net.graph['hidden'])):
                pnet.nodes[net.graph['hidden'][i]]['op'] = p[i]

            Gs_opd += [pnet]

    return Gs_opd



def has_an_io_path(net):
    # at least one input node must be connected to an output
    for o in net.graph['outputs']:
        o_path = False
        for i in net.graph['inputs']:
            if nx.has_path(net, i,o): o_path=True
        if not o_path: return False

    return True



def check(Gs):
    for G in Gs:
        assert(nx.is_directed_acyclic_graph(G))
        assert(has_an_io_path(G))
        for i in G.graph['inputs']: assert(G.nodes[i]['op']=='input')
        for o in G.graph['outputs']:
            print(o)
            assert(G.nodes[o]['op']=='output')



def gen_Gs(net_orig, out_node, nodes):
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
ex = 'and'
gen_graphs(n,ex, debug=True)