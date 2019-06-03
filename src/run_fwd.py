import networkx as nx
import examples, draw_nets
from matplotlib import pyplot as plt

# op: layer or activation function
# out: the output value that the node passes, post activation fn

#TODO: not yet sure how to handle non binary ex's and with logical ops...
# TODO: assumes 1 output

def all_instances(net, ex):
    acc = 0
    input,output = examples.get_io(ex)
    for i in range(len(output)):
        acc += one_instance(net, ex, i)

    acc /= len(output)
    return acc


def one_instance(net, ex, instance):
    init(net)

    input,output = examples.get_io(ex)
    N = nx.number_of_nodes(net)-1
    num_out = 1
    out_nodes = [i for i in range(N-(num_out),N)]

    i=0
    # while loop relies on existence of a path to each output from the input
    while not done(net, out_nodes):
        fwd_pass(net, ex, instance)
        i+=1
        if i>100:
            draw_nets.basic(net, len(inputs))
            assert(False) #infinite loop on run_fwd.one_instance()

    accuracy = eval(net, output, out_nodes)
    return accuracy


def init(net):
    for n in net.nodes():
        net.nodes[n]['out'] = None
        net.nodes[n]['in'] = []

def done(net, out_nodes):
    # all outputs must have received something
    for o in out_nodes:
        if net.nodes[o]['out'] is None:
            return False
    return True


def activate(net,n, ex, instance):
    #TODO: non binary?

    op = net.nodes[n]['op']
    if op == 'input':
        input,output = examples.get_io(ex)
        net.nodes[n]['out'] = input[n][instance]

    # node with one input, which it has received
    if len(net.nodes[n]['in']) == 1 and len(net.nodes[n]['in']) == len(net.in_edges(n)):
        if op == 'and' or op == 'or' or op=='output':
            net.nodes[n]['out'] = net.nodes[n]['in'][0]
        elif op == 'nand' or op == 'nor':
            net.nodes[n]['out'] = 1-net.nodes[n]['in'][0]
        else: assert(False) #unknown op

    elif len(net.nodes[n]['in']) == 2:
        assert(len(net.nodes[n]['in']) == len(net.in_edges(n)))

        if op == 'and':
            if net.nodes[n]['in'][0] == 1 and net.nodes[n]['in'][1] == 1:
                net.nodes[n]['out'] = 1
            else: net.nodes[n]['out'] = 0
        elif op == 'nand':
            if net.nodes[n]['in'][0] == 1 and net.nodes[n]['in'][1] == 1:
                net.nodes[n]['out'] = 0
            else: net.nodes[n]['out'] = 1
        elif op == 'or':
            if net.nodes[n]['in'][0] == 1 or net.nodes[n]['in'][1] == 1:
                net.nodes[n]['out'] = 1
            else: net.nodes[n]['out'] = 0
        elif op == 'nor':
            if net.nodes[n]['in'][0] == 1 or net.nodes[n]['in'][1] == 1:
                net.nodes[n]['out'] = 0
            else: net.nodes[n]['out'] = 1
        elif op == 'output':
            assert(False) #outputs should not have > 1 in_edges
        else: assert(False) #unknown op


def fwd_pass(net, ex, instance):
    # activate nodes that have received all their inputs
    for n in net.nodes():
        if len(net.nodes[n]['in']) == len(net.in_edges(n)):
            activate(net,n, ex, instance)

    # pass output of activated nodes to their descendants
    for n in net.nodes():
        if net.nodes[n]['out'] is not None:
            for e in net.out_edges(n):
                net.nodes[e[1]]['in'] += [net.nodes[n]['out']]


def eval(net, output, out_nodes):
    num, num_correct = 0,0

    assert(len(out_nodes) == 1) #not ready for mult out yet

    for n in out_nodes:
        if net.nodes[n]['out'] == output:
            num_correct +=1
        num += 1

    accuracy = num_correct/num
    return accuracy
