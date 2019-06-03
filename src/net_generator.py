import networkx as nx
from itertools import product

import examples, run_fwd, draw_nets, net_evaluator

# TODO: run all nets, only keep those with correct solution
# see gen_Gs
# Then eval those nets for their information
# + a healthy dose of test-based debugging
# TODO: some repeat nets since ops of lng 1 with AND = OR (ie ID)

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
    net.graph['hidden'] = [i for i in range(num_in, n-num_out)]
    net.graph['outputs'] = [i for i in range(n - num_out,n)]
    # TODO: layer -> op, where in+out don't have ops
    for i in range(n):
        if i < num_in: net.add_node(i,op='input')
        elif i >= n - num_out: net.add_node(i,op='output')
        else: net.add_node(i, op=None)

    Gs = []
    source_nodes = net.graph['inputs'] + net.graph['hidden']
    for target_node in net.graph['outputs']:
        Gs += gen_Gs(net,target_node, source_nodes)

    len_orig = len(Gs)
    Gs = assign_op_combos(Gs)
    len_final = len(Gs)
    if debug: print("\nOrigGs vs ComboOpsGs lng = " + str(len_orig) + ', ' + str(len_final) + '\n')


    check(Gs)
    Gs = keep_correct(Gs, ex)
    if debug: print("CorrectGs remaining lng = " + str(len(Gs)))

    if draw: draw_nets.save_mult(Gs, out_dir)

    return Gs



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





def gen_Gs(net_orig, target_node, source_nodes, verbose=False):
    # generates acyclic graphs with max 2 in vertices

    # TODO: CLEAN + relax the copying gat dam
    # TODO: generalize to mult out nodes
    # TODO: generalize to 0 in-edges?

    Gs = []

    if verbose:
        print('\nwith target = ' + str(target_node) + ', and source = ' + str(source_nodes))
        for o in net_orig.graph['outputs']:
            print(net_orig.in_edges(o))

    for i in range(len(source_nodes)):
        n=source_nodes[i]
        net = net_orig.copy()
        net.add_edge(n,target_node)
        if verbose: print('new edge = ' + str(n) + ', '+ str(target_node))
        if nx.is_directed_acyclic_graph(net):
            if has_an_io_path(net) and all_hidden_btwn_io(net):
                Gs += [net.copy()]
                if verbose: print("Adding net w/ edges: " + str(net.edges()))
            nodes_copy = source_nodes.copy()
            del nodes_copy[i]

            if net.nodes[n]['op'] != 'input':
                #look for more nets to new target
                if verbose:
                    print('recursing with taget, sources: ')
                    print(n, nodes_copy)
                Gs += gen_Gs(net, n, nodes_copy)

            if net.nodes[target_node]['op'] != 'output': #output nodes do not have an op, so take only 1 in_edge

                if verbose: print('looking for 2nd source with ' + str(n))
                for j in range(i,len(nodes_copy)):
                    m = nodes_copy[j]
                    met = net.copy()
                    met.add_edge(m, target_node)
                    if verbose: print('new edge = ' + str(n) + ', ' + str(target_node))

                    if nx.is_directed_acyclic_graph(met):
                        if has_an_io_path(met) and all_hidden_btwn_io(met):
                            Gs += [met.copy()]
                            if verbose: print("Adding net2 w/ edges: " + str(met.edges()))

                        if met.nodes[m]['op'] != 'input':
                            nodes_copy2 = nodes_copy.copy()
                            del nodes_copy2[j]
                            if verbose:
                                print('recursing with taget, sources: ')
                                print(m, nodes_copy2)
                            Gs += gen_Gs(met, m, nodes_copy2)

    return Gs



# just for testing purposes
n = 7
ex = 'and'
output_path= 'C:/Users/Crbn/Documents/Code/Info/plots/candidate_nets_' + str(ex) + '/'
Gs = gen_graphs(n,ex, output_path, debug=True, draw=False)
net_evaluator.judge_em(Gs, output_path)