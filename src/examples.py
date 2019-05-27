import numpy as np

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

    else:
        assert (False)  # unknown sys.argv[1]


    assert(np.array(input).ndim == 2) #for now, only want pairs of edges
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