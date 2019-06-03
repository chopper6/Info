import sys, math
import pr, plot_pieces
import numpy as np
from math import log, pow

import examples, axioms
from info_fns import *



#TODO:
# check axioms on all ex's at once
# some tweaks to plot_pieces.py
# later: allow for mutivariate (although always eval'd by pairs)

# eventually want to use with a recursive algo
# dyn program could involve re-use of certain eles
# but which ones remain unclear...


def plot_ex(ex, output_path):

    input, output = examples.get_io(ex)
    num_inst = len(output)

    # get pr's aligned by instances
    pr_y,  pr_x, pr_xx, pr_xy, pr_xxy, aligned_inputs, aligned_outputs = pr.find_prs_aligned(input, output, debug=False, disordered=False)
    Al = {'x1':aligned_inputs[0], 'x2':aligned_inputs[1], 'y':aligned_outputs}   # alphabet dict

    # probability atom plots
    Pr, p_keys = pr.build_p_atoms(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, num_inst)
    plot_pieces.prob_atoms(Pr, p_keys, aligned_inputs, aligned_outputs, output_path, ex)

    # PID candidates
    Rs = R_candidates(Pr, Al, num_inst)
    PIDs = PID_decompose(Rs, Pr, print_PID=False)

    #axioms.check_axioms(Pr, PIDs, output_path, ex)

    plot_pieces.info_bars(Pr, Al, output_path, ex)
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

    xkeys = ['<ii/i>x', 'min>x']
    ykeys = ['<ii/i>y', 'min>y']
    wkeys = ['II/I', 'min(II)', 'min(III)'] #w for whole

    cand_keys = xkeys + ykeys + wkeys

    # ARCHIVE OF DEAD ENDS:
    defunct_keys = ['III/I','sqrt(II/I)', 'II/I', '<iii/i>x','<iii/i>y',  '<ii1/i>x','<ii1/i>y','<ii2/i>x','<ii2/i>y','<i1/i>x','<i1/i>y','<i2/i>x','<i2/i>y'] #eventually need to clean out some
    defunct_keys_2 = ['sqrt I<ii>y/H', 'sqrt I<ii>x/H','<ii/h>y', '<ii/h>x', 'sqrt I<ii/i>x', 'sqrt I<ii/i>y','sqrt(III/I)', 'II/H']
    defunct_keys_3 = ['logH II/I','sqrt II','III/HI', 'I<ii/i>y/H', 'sqrt <ii>y', 'I<ii/i>x/H', 'sqrt <ii>x']
    defunct_keys_4 = ['min(iiii)>x', 'min(iii)>y']

    r = [{k:0 for k in cand_keys} for i in range(num_inst)]

    for i in range(num_inst):

        # PARTIAL X CANDIDATES
        if partial_info(Pr,Al,'y','x1,x2',i) == 0:
            for k in xkeys: r[i][k] = 0
        else:
            r[i]['<ii/i>x'] = partial_info(Pr,Al,'y','x1',i) * partial_info(Pr,Al,'y','x2',i) \
                              / partial_info(Pr,Al,'y','x1,x2',i)

        r[i]['<iii/i>x'] = r[i]['<ii/i>x'] * info(Pr[i],'x1','x2')
        r[i]['sqrt I<ii/i>x'] = r[i]['<ii/i>x']
        #r[i]['<ii/h>x'] = partial_info(Pr,Al,'y','x1',i) * partial_info(Pr,Al,'y','x2',i) / h(Pr[i], 'x1,x2')
        r[i]['sqrt <ii>x'] = pow(partial_info(Pr,Al,'y','x1',i) * partial_info(Pr,Al,'y','x2',i), 1/2)

        r[i]['min>x'] = min(partial_info(Pr,Al,'y','x1',i),partial_info(Pr,Al,'y','x2',i))
        r[i]['min(iiii)>x'] = min(partial_info(Pr,Al,'x2','x1',i), partial_info(Pr,Al,'x1','x2',i),  partial_info(Pr,Al,'y','x1',i),partial_info(Pr,Al,'y','x2',i))

        # PARTIAL Y CANDIDATES
        if partial_info(Pr,Al,'x1,x2','y',i) == 0:
            for k in ykeys: r[i][k] = 0
        else:
            r[i]['<ii/i>y'] = partial_info(Pr,Al,'x1','y',i) * partial_info(Pr,Al,'x2','y',i) \
                              / partial_info(Pr,Al,'x1,x2','y',i)

        r[i]['<iii/i>y'] = r[i]['<ii/i>y'] * info(Pr[i], 'x1', 'x2')
        r[i]['sqrt I<ii/i>y'] = r[i]['<ii/i>y']
        #r[i]['<ii/h>y'] = partial_info(Pr,Al,'x1','y',i) * partial_info(Pr,Al,'x2','y',i) / h(Pr[i], 'x1,x2')
        r[i]['sqrt <ii>y'] = pow(partial_info(Pr, Al, 'x1','y', i) * partial_info(Pr, Al,'x2', 'y',i), 1 / 2)

        r[i]['min>y'] = min(partial_info(Pr, Al,'x1','y', i), partial_info(Pr, Al, 'x2','y', i))
        r[i]['min(iiii)>y'] = min(partial_info_1of3(Pr, Al, 'x2', 'x1','y', i),
                              partial_info(Pr, Al, 'x1', 'y', i), partial_info(Pr, Al, 'x2','y', i))

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

    else:
        R['III/I'] = Info(Pr, 'x1', 'x2') * Info(Pr, 'x1', 'y') * Info(Pr, 'x2', 'y') / Info(Pr, 'x1,x2', 'y')
        R['II/I'] = Info(Pr, 'x1', 'y') * Info(Pr, 'x2', 'y') / Info(Pr, 'x1,x2', 'y')
        R['sqrt II'] = pow(Info(Pr, 'x1', 'y') * Info(Pr, 'x2', 'y'), 1/2)

        R['sqrt(III/I)'] = pow(R['III/I'], 1 / 2)
        R['sqrt(II/I)'] = pow(R['II/I'], 1 / 2)

        R['III/HI'] = R['III/I']/ H(Pr,'x1,x2')

        R['II/H'] = Info(Pr, 'x1', 'y') * Info(Pr, 'x2', 'y') / H(Pr, 'x1,x2')

        R['min(II)'] = min(Info(Pr, 'x1', 'y'), Info(Pr, 'x2', 'y'))
        R['min(III)'] = min(Info(Pr, 'x1', 'y'), Info(Pr, 'x2', 'y'), Info(Pr,'x1','x2'))


    # MIXED PTWISE AND WHOLE CANDIDATES
    R['sqrt I<ii/i>y'] = pow(R['<ii/i>y'] * Info(Pr,'x1','x2'), 1 / 2)
    R['sqrt I<ii/i>x'] = pow(R['<ii/i>x'] * Info(Pr,'x1','x2'), 1 / 2)
    R['I<ii/i>x/H'] = R['<ii/i>x'] * Info(Pr,'x1','x2') / H(Pr,'x1,x2')
    R['I<ii/i>y/H'] = R['<ii/i>y'] * Info(Pr,'x1','x2') / H(Pr,'x1,x2')

    R['logH II/I'] = log((H(Pr,'x1')+H(Pr,'x2'))/H(Pr,'x1,x2'),2) * R['II/I']

    # only want to plot candidates
    dels = []
    for k in R.keys():
        if k not in cand_keys:
            dels += [k]
    for k in dels: del R[k]

    return R




def PID_decompose(R, Pr, print_PID=True):
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

    output_path= 'C:/Users/Crbn/Documents/Code/Info/plots/'

    if sys.argv[1] == 'all':
        exs = ['xor','id', 'id2','id3','and','breaker','rdnerr', 'an', 'pwunq',
               'xor2','pw_v2', 'pw_v3','xx1','xx2','imbalance','imbalance2','imbalance3', 'concat']
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
