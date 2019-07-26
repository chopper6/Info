import sys, math
import pr, plot_pieces
import numpy as np
from math import log, pow

import examples, axioms
from info_fns import *
from util import *

#TODO: normalized PIDs require proper normalization for all R,U,S...

#TODO:
# check axioms on all ex's at once
# some tweaks to plot_pieces.py
# later: allow for mutivariate (although always eval'd by pairs)

# eventually want to use with a recursive algo
# dyn program could involve re-use of certain eles
# but which ones remain unclear...


def plot_ex(ex, output_path, normalize=False, debug=False):

    input, output = examples.get_io(ex)
    num_inst = len(output)

    # get pr's aligned by instances
    pr_y,  pr_x, pr_xx, pr_xy, pr_xxy, aligned_inputs, aligned_outputs = pr.find_prs_aligned(input, output, debug=debug, disordered=False)
    Al = {'x1':aligned_inputs[0], 'x2':aligned_inputs[1], 'y':aligned_outputs}   # alphabet dict

    # probability atom plots
    Pr, p_keys = pr.build_p_atoms(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, num_inst)
    plot_pieces.prob_atoms(Pr, p_keys, aligned_inputs, aligned_outputs, output_path, ex)

    # PID candidates
    Rs = R_candidates(Pr, Al, num_inst)
    if normalize: 
        print("\nWARNING: PID.plot_ex(): using normalized version.")
        PIDs = PID_decompose_normzd(Rs, Pr, Al, print_PID=False)
    else: PIDs = PID_decompose(Rs, Pr)

    #axioms.check_axioms(Pr, PIDs, output_path, ex)

    #plot_pieces.info_bars(Pr, Al, output_path, ex, bar_choice='H')
    plot_pieces.info_bars(Pr, Al, output_path, ex, bar_choice='I')
    plot_pieces.info_bars(Pr, Al, output_path, ex, bar_choice='I2')
    plot_pieces.info_bars(Pr, Al, output_path, ex, bar_choice='I1')
    plot_pieces.PID_pie(PIDs, output_path, ex)

    return Pr, PIDs


####################################### PARTIAL AVGS #################################################

def R_candidates(Pr, Al, num_inst):
    # requires a set of alphabets and probabilities
    # where Pr[i].keys() = 'x1','x2','x1,y','x2,y','x1,x2','x1,x2,y' ....???
    # Al[i].keys() = 'x1', 'x2', 'y'

    # with MANY instances, this becomes VERY INEFFICIENT
    # since partial info is computed over each m instances -> O(m^2)
    # however, I assume that instances remain near m=4

    # TODO: poss frag into smaller fns

    xkeys = ['<ii/i>x','<ii>x/h','<ii>x/hi','min>x','min h(x|y)','i2>x']
    ykeys = ['<ii/i>y','<ii>y/h','<ii>y/hi','min>y','min h(y|x)','i2>y']
    wkeys = [] #['II/I', 'min(II)', 'min(III)'] #w for whole

    cand_keys = xkeys + ykeys + wkeys

    # ARCHIVE OF DEAD ENDS:
    defunct_keys = ['III/I','sqrt(II/I)', 'II/I', '<iii/i>x','<iii/i>y',  '<ii1/i>x','<ii1/i>y','<ii2/i>x','<ii2/i>y','<i1/i>x','<i1/i>y','<i2/i>x','<i2/i>y'] #eventually need to clean out some
    defunct_keys_2 = ['sqrt I<ii>y/H', 'sqrt I<ii>x/H','<ii/h>y', '<ii/h>x', 'sqrt I<ii/i>x', 'sqrt I<ii/i>y','sqrt(III/I)', 'II/H']
    defunct_keys_3 = ['logH II/I','sqrt II','III/HI', 'I<ii/i>y/H', 'sqrt <ii>y', 'I<ii/i>x/H', 'sqrt <ii>x']
    defunct_keys_4 = ['min(iiii)>x', 'min(iii)>y']
    defunct_keys_5 = ['II/I', 'min(II)', 'min(III)']

    r = [{k:0 for k in cand_keys} for i in range(num_inst)]

    for i in range(num_inst):

        # PARTIAL X CANDIDATES
        if partial_info(Pr,Al,'y','x1,x2',i) == 0:
            for k in xkeys: r[i][k] = 0
        else:
            r[i]['<ii/i>x'] = partial_info(Pr,Al,'y','x1',i) * partial_info(Pr,Al,'y','x2',i) \
                              / partial_info(Pr,Al,'y','x1,x2',i)

        r[i]['<ii>x/hi'] = r[i]['<ii/i>x']/h(Pr[i],'x1,x2')
        r[i]['<ii>x/h'] = partial_info(Pr,Al,'y','x1',i) * partial_info(Pr,Al,'y','x2',i)/h(Pr[i],'x1,x2')
        r[i]['min>x'] = min(partial_info(Pr,Al,'y','x1',i),partial_info(Pr,Al,'y','x2',i))
        r[i]['min>>'] = min(partial_info(Pr,Al,'y','x1',i),partial_info(Pr,Al,'y','x2',i),partial_info(Pr,Al,'x1','y',i),partial_info(Pr,Al,'x2','y',i))

        i2_1,i2_2 = max(i2(Pr, Al, 'y', 'x1', i),0),max(i2(Pr, Al, 'y', 'x2', i),0)
        #i2_1,i2_2 = i2(Pr, Al, 'y', 'x1', i),i2(Pr, Al, 'y', 'x2', i)
        r[i]['i2>x'] = min(i2_1,i2_2)

        r[i]['min h(x|y)'] = min(h(Pr[i],'x1')-h_cond(Pr[i],'x1','y'),h(Pr[i],'x2')-h_cond(Pr[i],'x2','y'))

        # PARTIAL Y CANDIDATES
        if partial_info(Pr,Al,'x1,x2','y',i) == 0:
            for k in ykeys: r[i][k] = 0
        else:
            r[i]['<ii/i>y'] = partial_info(Pr,Al,'x1','y',i) * partial_info(Pr,Al,'x2','y',i) \
                              / partial_info(Pr,Al,'x1,x2','y',i)

        r[i]['<ii>y/hi'] = r[i]['<ii/i>y']/h(Pr[i],'x1,x2')
        r[i]['<ii>x/h'] = partial_info(Pr,Al,'x1','y',i) * partial_info(Pr,Al,'x2','y',i)/h(Pr[i],'y')
        r[i]['min>y'] = min(partial_info(Pr, Al,'x1','y', i), partial_info(Pr, Al, 'x2','y', i))

        i2_1,i2_2 = max(i2(Pr, Al, 'x1','y', i),0),max(i2(Pr, Al,'x2','y', i),0)
        #i2_1,i2_2 = i2(Pr, Al, 'x1','y', i),i2(Pr, Al,'x2','y', i)
        r[i]['i2>y'] = min(i2_1,i2_2)

        r[i]['min h(y|x)'] = min(h(Pr[i],'y')-h_cond(Pr[i],'y','x1'),h(Pr[i],'y')-h_cond(Pr[i],'y','x2'))

    # AVERAGE pointwise r -> R
    R = {k: 0 for k in cand_keys}

    for i in range(num_inst):
        for k in cand_keys:
            R[k] += r[i][k]
    for k in cand_keys:
        R[k] /= num_inst


    # NON-PTWISE CANDIDATES
    if Info(Pr, 'x1,x2', 'y') == 0:
        for k in wkeys: R[k] = 0

    # only want to plot candidates
    dels = []
    for k in R.keys():
        if k not in cand_keys:
            dels += [k]
    for k in dels: del R[k]

    return R



def PID_decompose_normzd(R, Pr, Al, print_PID=False, x1x2logbase=2):
    # note that earlier sense of R[i] would have to be avg'd for R
    # TODO: rm Al arg if unused

    PID = {k:{'R':R[k], 'U1':Info(Pr,'x1','y'),
        'U2':Info(Pr,'x2','y'),'S':Info(Pr,'x1,x2','y')} for k in R.keys()}


    PID['min h(x|y)'] = {'R':R['min h(x|y)'], 'U1':H(Pr,'x1')-H_cond(Pr,'x1','y'),
            'U2':H(Pr,'x2')-H_cond(Pr,'x2','y'), 'S':H(Pr,'x1,x2')-H_cond(Pr,'x1,x2','y')}
    PID['min h(y|x)'] = {'R':R['min h(y|x)'], 'U1':H(Pr,'y')-H_cond(Pr,'y','x1'),
            'U2':H(Pr,'y')-H_cond(Pr,'y','x2'), 'S':H(Pr,'y')-H_cond(Pr,'y','x1,x2')}
    
    
    normz_keys = [['<ii>x/hi','<ii>y/hi'],['<ii>x/h','<ii>y/h']]

    for z in normz_keys:
        x,y=z[0],z[1]
        if Info(Pr,'x1','y')!=0:    
            PID[x]['U1'] = avg([partial_info(Pr,Al,'y','x1',i)/h(Pr[i],'x1') for i in rng(Pr)])
            PID[y]['U1'] = avg([partial_info(Pr,Al,'x1','y',i)/h(Pr[i],'y') for i in rng(Pr)])
        else: 
            PID[x]['U1'] = 0
            PID[y]['U1'] = 0
        if Info(Pr,'x2','y')!=0:
            PID[x]['U2'] = avg([partial_info(Pr,Al,'y','x2',i)/h(Pr[i],'x2') for i in rng(Pr)])
            PID[y]['U2'] = avg([partial_info(Pr,Al,'x2','y',i)/h(Pr[i],'y') for i in rng(Pr)])
        else: 
            PID[x]['U2'] = 0
            PID[y]['U2'] = 0
        if Info(Pr,'x1,x2','y')!=0: 
            PID[x]['S'] = avg([partial_info(Pr,Al,'y','x1,x2',i)/h(Pr[i],'x1,x2',logbase=x1x2logbase) for i in rng(Pr)])
            PID[y]['S'] = avg([partial_info(Pr,Al,'x1,x2','y',i)/h(Pr[i],'y') for i in rng(Pr)]) 
            #PID[x]['S'] = avg([partial_info(Pr,Al,'y','x1,x2',i) for i in rng(Pr)])
            #PID[y]['S'] = avg([partial_info(Pr,Al,'x1,x2','y',i) for i in rng(Pr)]) 
        else: 
            PID[x]['S'] = 0
            PID[y]['S'] = 0
            
    for k in PID.keys():
    	for p in ['R', 'U1', 'U2', 'S']:
            PID[k][p] = round(PID[k][p],8) #rounding

    if print_PID: 
    	print('\noriginal PID = ' + str(PID))

    for k in PID.keys():

        PID[k]['U1'] -= PID[k]['R']
        PID[k]['U2'] -= PID[k]['R']
        PID[k]['S'] -= (PID[k]['U1'] + PID[k]['U2'] + PID[k]['R'])

        for p in ['R', 'U1', 'U2', 'S']:
            PID[k][p] = round(PID[k][p],8) #rounding, again

        if print_PID:
            print('\n' + k + ':')
            for p in ['R','U1','U2','S']:
                print(p + ' = ' + str(PID[k][p]))


    return PID


def PID_decompose(R, Pr, print_PID=False):
    # note that earlier sense of R[i] would have to be avg'd for R

    PID = {k:{'R':R[k], 'U1':Info(Pr,'x1','y'),
            'U2':Info(Pr,'x2','y'), 'S':Info(Pr,'x1,x2','y')}
           for k in R.keys()}

    for k in PID.keys():

        PID[k]['U1'] -= PID[k]['R']
        PID[k]['U2'] -= PID[k]['R']
        PID[k]['S'] -= (PID[k]['U1'] + PID[k]['U2'] + PID[k]['R'])

        for p in ['R', 'U1', 'U2', 'S']:
            PID[k][p] = round(PID[k][p],8) #rounding

        if print_PID:
            print('\n' + k + ':')
            for p in ['R','U1','U2','S']:
                print(p + ' = ' + str(PID[k][p]))


    return PID




if __name__ == "__main__":

    assert(len(sys.argv) == 2) # arg should be run_name

    output_path= 'C:/Users/Crbn/Documents/Code/Info/plots/metrics/'

    if sys.argv[1] == 'all':
        exs = ['xor','id', 'id2','id3','and','breaker','rdnerr', 'an', 'pwunq',
               'xor2','pw_v2', 'pw_v3','xx1','xx2','imbalance','imbalance2','imbalance3', 'concat', 
               'nor','nand','aneg','asym','asym2','asym3','asym4']
        #crutch_dyadic', 'crutch_triadic'
        PIDS,PR = {}, {}
        for ex in exs:
            print('\n...decomposing ' + str(ex))
            Pr, PIDs = plot_ex(ex, output_path)
            PIDS[ex] = PIDs
            PR[ex] = Pr
        axioms.check_axioms_many(PR, PIDS, output_path)

    else:
        Pr, PIDs = plot_ex(sys.argv[1], output_path)
        axioms.check_axioms(Pr, PIDs, output_path, sys.argv[1])

    print("\nDone.\n")


