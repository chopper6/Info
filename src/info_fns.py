from math import log


########################################### POINTWISE ############################################

log_base = 2

def h(pr,a):
    # h(a)
    return -1*log(pr[a], log_base)

def h_cond(pr,a,b):
    # h(a|b)
    return -1*log(pr[a + ',' + b]/pr[b], log_base)

def info(pr,a,b):
    # i(a,b)
    return log(pr[a + ',' + b]/(pr[a]*pr[b]), log_base)


########################################### PARTIAL ################################################

def partial_info(Pr,Al,a,b,inst):
    # |i(a,b)>b
    # Al[i]['x1'] = digit of input 1 at instance i
    i = info(Pr[inst],a,b)

    num_inst = len(Al['y'])
    num = 1
    bb = b.split(',')
    if len(bb) == 1:
        for j in range(num_inst):
            if inst != j and Al[bb[0]][j] == Al[bb[0]][inst]:
                i += info(Pr[j],a,b)
                num += 1
    else:
        assert(len(bb)==2)
        for j in range(num_inst):
            if inst != j and Al[bb[0]][j] == Al[bb[0]][inst] and Al[bb[1]][j] == Al[bb[1]][inst]:
                i += info(Pr[j],a,b)
                num += 1
    i /= num
    return i


########################################### WHOLE #################################################

def H(Pr, a):
    num_inst = len(Pr)
    H = sum(h(Pr[i], a) for i in range(num_inst)) / num_inst
    return H

def H_cond(Pr,a,b):
    num_inst = len(Pr)
    H = sum(h_cond(Pr[i],a,b) for i in range(num_inst)) / num_inst
    return H

def Info(Pr,a,b):
    num_inst = len(Pr)
    I = sum(info(Pr[i],a,b)for i in range(num_inst)) / num_inst
    return I



