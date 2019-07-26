from math import log


########################################### POINTWISE ############################################

log_base = 2

def h(pr,a,logbase=2):
    # h(a)
    return -1*log(pr[a], logbase)

def h_cond(pr,a,b):
    # h(a|b)
    return -1*log(pr[a + ',' + b]/pr[b], log_base)

def info(pr,a,b):
    # i(a,b)
    return log(pr[a + ',' + b]/(pr[a]*pr[b]), log_base)


########################################### PARTIAL ################################################

def i1(Pr,Al,a,b,inst):
    # just renaming
    return partial_info(Pr,Al,a,b,inst)

def i3(Pr,Al,a,b,inst):
    # from D.A. Butts, Network (2003)
    # "stimulus-specific information"
    num_inst = len(Al['y'])
    i3=0
    for j in range(num_inst):
        #if Al[a][j]==Al[a][inst]: #incld Al[a][inst]==Al[a][inst]
        i3 += Pr[j][a+','+b]/Pr[j][a] * i2(Pr,Al,a,b,j)
        # TODO: not quite, return to this though


def partial_info(Pr,Al,a,b,inst):
    # ie i1
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


def i2(Pr, Al, a, b, inst):
    # from DeWeese & Meister, I(A;B_inst)
    Hx = H(Pr,a)
    #if a=='x1,x2': Hx=H(Pr,a,logbase=4)
    num_inst = len(Al['y'])
    num = 1
    
    hx_y = h_cond(Pr[inst],a,b)
    bb = b.split(',')


    if len(bb) == 1:
        for j in range(num_inst):
            if inst != j and Al[b][j] == Al[b][inst]:
                hx_y += h_cond(Pr[j],a,b)
                num += 1
    else:
        assert(len(bb) == 2)
        for j in range(num_inst):
            if inst != j and Al[bb[0]][j] == Al[bb[0]][inst] and Al[bb[1]][j] == Al[bb[1]][inst]:
                hx_y += h_cond(Pr[j],a,b)
                num += 1

    hx_y /= num
    return Hx - hx_y


def non_Markv_dist_cond(pr, a,b,c):
    full_h_cond = h_cond(pr, a, b+',' +c)
    h_a = h(pr,a)
    markv_fwd = -1*log(pr[a+','+b]/pr[b] * pr[b+','+c]/pr[c],2)
    markv_rev = -1*log(pr[c+','+b]/pr[b] * pr[b+','+a]/pr[a],2)
    #print(markv_fwd,markv_rev)
    #return markv_fwd-markv_rev
    #return h_a - full_h_cond
    return markv_fwd - full_h_cond


def partial_info_1of3(Pr,Al,a,b,c,inst):
    # |i(a,bc)>c
    # Al[i]['x1'] = digit of input 1 at instance i
    # shit naming
    i = info(Pr[inst],a,b + ',' + c)

    num_inst = len(Al['y'])
    num = 1
    bb = b.split(',')
    assert( len(bb) == 1 ) #since bc is a unit

    for j in range(num_inst):
        if inst != j and Al[c][j] == Al[c][inst]:
            i += info(Pr[j],a,b + ',' + c)
            num += 1

    i /= num
    return i


########################################### WHOLE #################################################

def H(Pr, a, logbase=2):
    num_inst = len(Pr)
    H = sum(h(Pr[i], a,logbase=logbase) for i in range(num_inst)) / num_inst
    return H

def H_cond(Pr,a,b):
    num_inst = len(Pr)
    H = sum(h_cond(Pr[i],a,b) for i in range(num_inst)) / num_inst
    return H

def Info(Pr,a,b):
    num_inst = len(Pr)
    I = sum(info(Pr[i],a,b)for i in range(num_inst)) / num_inst
    return I



