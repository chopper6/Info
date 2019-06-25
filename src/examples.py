import numpy as np
from util import *

def get_io(name):
    if name == 'and':
        input, output = and_problem()
    elif name == 'xor':
        input, output = xor_problem()  # will need to do some fixing first
    elif name == 'xor2':
        input, output = xor_lvl2()

    elif name == 'pw_v2':
        input, output = pw_v2()
    elif name == 'pw_v3':
        input, output = pw_v3()
    elif name == 'pwunq':
        input, output = PwUnq()
    elif name == 'rdnerr':
        input, output = RdnErr()
    elif name == 'an':
        input, output = An()
    elif name == 'breaker':
        input, output = breaker()
    elif name == 'id':
        input, output = id()
    elif name == 'id2':
        input, output = id_v2()
    elif name == 'id3':
        input, output = id_v3()
    elif name == 'xx1':
        input = [[1,1,0,0],[1,1,0,0]]
        output = [1,1,1,0]
    elif name == 'xx2':
        input = [[1,1,1,0],[1,1,1,0]]
        output = [1,1,0,0]
    elif name == 'imbalance':
        input = [[1,1,1,0,0,0],[1,0,0,0,0,0]]
        output = [1,1,1,0,0,0]
    elif name == 'imbalance2':
        input = [[1,1,1,0,0,0],[0,0,0,0,0,1]]
        output = [1,1,1,0,0,1]
    elif name == 'imbalance3':
        input = [[1,2,3,1,0,0],[0,0,0,0,2,3]]
        output = [1,2,3,1,2,3]
    elif name == 'aneg':
        input = [[1,0,1,0],[0,1,1,1]]
        output = [0,0,1,0]
    elif name == 'or':
        input = [[1,0,1,0],[1,1,0,0]]
        output = [1,1,1,0]
    elif name == 'nor':
        input = [[1,0,1,0],[1,1,0,0]]
        output = [0,0,0,1]
    elif name == 'nand':
        input = [[1,0,1,0],[1,1,0,0]]
        output = [0,1,1,1]


    elif name == 'crutch_dyadic': #note that he doesn't specify inputs vs outputs
        input = [[0,0,1,1,2,2,3,3], [0,2,0,2,1,3,1,3]]
        output = [0,1,2,3,0,1,2,3]
    elif name == 'crutch_triadic':
        input = [[0,1,0,1,2,3,2,3],[0,1,2,3,0,1,2,3]]
        output = [0,1,2,3,2,3,0,1]

    elif name == 'concat':
        input = [[0,0,1,1],[0,1,0,1]]
        output = [0,1,2,3]

    elif name == '3and':
        input = [[1,1,1,1,0,0,0,0],[1,1,0,0,1,1,0,0],[1,0,1,0,1,0,1,0]]
        output = [1,0,0,0,0,0,0,0]
    elif name == '4and':
        input = [[1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0],
        [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]]
        output = [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    elif name in ['3parity','3xor']:
        input = [[1,1,1,1,0,0,0,0],[1,1,0,0,1,1,0,0],[1,0,1,0,1,0,1,0]]
        output = [sum(input[i][j] for i in rng(input)) % 2 for j in rng(input[0])]
    elif name in ['4parity','4xor']:
        input = [[1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],[1,1,1,1,0,0,0,0,1,1,1,1,0,0,0,0],
        [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0],[1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]]
        output = [sum(input[i][j] for i in rng(input)) % 2 for j in rng(input[0])]

    else:
        assert (False)  # unknown sys.argv[1]


    #assert(np.array(input).ndim == 2) #for now, only want pairs of edges
    for i in input: assert(len(i) == len(output))
    return input, output

########################## BASE PROBLEMS ####################################
def XOR_expanded():
    x1, x2 = [1,1,0,0],[1,0,1,0]
    h1, h2 = [1,1,1,0],[0,1,1,1] #1st layer, NAND and OR
    h3 = [0,1,1,0] #2nd layer, AND(h1,h2)
    y = [0,1,1,0]

    inputs = [x1,x2,h1,h2,h3]
    output = y
    return inputs, output

def and_problem():
    input = [[1,1,0,0],[1,0,1,0]]
    output = [1,0,0,0]
    return input, output

def xor_problem():
    input = [[1,1,0,0],[1,0,1,0]]
    output = [0,1,1,0]
    return input, output

def xor_lvl2():
    input = [[1,1,1,0],[0,1,1,1]]
    output = [0,1,1,0]
    return input, output

def pw_v2():
    input = [[1,0,0,0],[0,0,1,0]]
    #output = [1,0,2,0]
    output = [1,0,2,0]
    return input, output

def pw_v3():
    input = [[0,1,0,2],[1,0,2,0]]
    output = [1,2,3,4]
    return input, output

def PwUnq(): # as in Finn & Lizier
    input = [[0,1,0,2],[1,0,2,0]]
    output = [1,1,2,2]
    return input, output

def RdnErr(): #as in Finn & Lizier
    input = [[0,1,0,1], [0,1,1,0]]
    output = [0,1,0,1]
    return input, output

def An():
    input = [[1,1,0],[1,0,1]]
    output = [1,0,0]
    return input, output

def breaker():
    input = [[1,1,0,0],[1,1,1,0]]
    output = [1,0,0,1]
    return input, output

def id():
    input = [[1,1,0,0],[1,1,0,0]]
    output = [1,1,0,0]
    return input, output

def id_v2():
    input = [[1,1,1,0],[1,1,1,0]]
    output = [1,1,1,0]
    return input, output

def id_v3():
    input = [[1,1,1,1,0],[1,1,1,1,0]]
    output = [1,1,1,1,0]
    return input, output