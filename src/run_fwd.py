import networkx as nx
import examples, draw_nets

# op: layer or activation function
# out: the output value that the node passes, post activation fn

# TODO: not yet sure how to handle non binary ex's and with logical ops...
# TODO: assumes 1 output and binary problem

def all_instances(net, ex):
    acc = 0
    for n in net.nodes(): net.nodes[n]['hist'] = []
    input,output = examples.get_io(ex)
    for i in range(len(output)):

        acc += one_instance(net, ex, i)

        # save output for later evaluation
        for n in net.nodes(): net.nodes[n]['hist'] += [net.nodes[n]['out']]

    acc /= len(output)
    return acc


def one_instance(net, ex, instance):
    init(net)


    input,output = examples.get_io(ex)

    i=0
    # while loop relies on existence of a path to each output from the input
    while not done(net):
        fwd_pass(net, ex, instance)
        i+=1
        if i>200:
            print("ERROR: infinite loop on the following net:")
            draw_nets.basic(net, showfig=True)
            assert(False) #infinite loop on run_fwd.one_instance()

    accuracy = eval(net, output,instance)
    return accuracy

###################################### MAIN STAGES #######################################

def init(net):
    # eventually all node['out'] == node.out_edges['out']
    for n in net.nodes():
        net.nodes[n]['out'] = None
    for e in net.edges():
        net[e[0]][e[1]]['out'] = None


def fwd_pass(net, ex, instance):
    # edge ops ASSUME binary (otherwise what is 'not'?)
    # activate nodes that have received all their inputs
    for n in net.nodes():
        activate(net,n, ex, instance)

    # pass output of activated nodes to their descendants
    for n in net.nodes():
        if net.nodes[n]['out'] is not None:
            for e in net.out_edges(n):
                assert(n==e[0])

                if net[e[0]][e[1]]['op'] == 'id':
                    net[n][e[1]]['out'] = net.nodes[n]['out']
                else: #op == 'not'
                    net[n][e[1]]['out'] = 1-net.nodes[n]['out']
                assert(net[n][e[1]]['out'] == 0 or net[n][e[1]]['out'] == 1)


def eval(net, output, instance):
    num, num_correct = 0,0

    assert(len(net.graph['outputs']) == 1) #not ready for mult out yet

    for n in net.graph['outputs']:
        if net.nodes[n]['out'] == output[instance]:
            num_correct +=1
        num += 1

    accuracy = num_correct/num
    return accuracy

###################################### HELPERS #######################################


def done(net):
    # all outputs must have received something
    for o in net.graph['outputs']:
        if net.nodes[o]['out'] is None:
            return False
    return True


def all_inputs_arrived(net,n):
    if net.nodes[n]['op'] == 'input': return True #always ready

    for e in net.in_edges(n):
        if net[e[0]][e[1]]['out'] is None: return False

    return True

def activate(net,n, ex, instance):
    #TODO: non binary?
    es = list(net.in_edges(n))
    op = net.nodes[n]['op']

    if op == 'input':
        input, output = examples.get_io(ex)
        net.nodes[n]['out'] = input[n][instance]

    elif all_inputs_arrived(net,n) and len(es) > 0:

        # node with one input, which it has received
        if len(es)==1:
            e=es[0]
            if op in ['id','and', 'or', 'output']:
                net.nodes[n]['out'] = net[e[0]][e[1]]['out']
            elif op in ['not','nand','nor']:
                net.nodes[n]['out'] = 1-net[e[0]][e[1]]['out']
            else:
                print(op)
                assert(False) #unknown op

        elif len(es) == 2:
            e1,e2 = net[es[0][0]][n]['out'], net[es[1][0]][n]['out']
            if op == 'and':
                if e1 == 1 and e2 == 1:
                    net.nodes[n]['out'] = 1
                else: net.nodes[n]['out'] = 0
            elif op == 'nand':
                if e1 == 1 and e2 == 1:
                    net.nodes[n]['out'] = 0
                else: net.nodes[n]['out'] = 1
            elif op == 'or':
                if e1 == 1 or e2 == 1:
                    net.nodes[n]['out'] = 1
                else: net.nodes[n]['out'] = 0
            elif op == 'nor':
                if e1 == 1 or e2 == 1:
                    net.nodes[n]['out'] = 0
                else: net.nodes[n]['out'] = 1
            elif op == 'output':
                assert(False) #outputs should not have > 1 in_edges
            else: 
                print('\nunknown op:',op,'from edge:',e1,e2)
                assert(False) #unknown op


