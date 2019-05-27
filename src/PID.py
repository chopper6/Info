import sys, math
import pr, plot_pieces
import numpy as np
from math import log, pow

import examples, axioms
from info_fns import *



#TODO:
# mainly, see plot_pieces.py
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

    axioms.check_axioms(Pr, PIDs, output_path, ex)

    plot_pieces.info_bars(Pr, Al, output_path, ex)
    plot_pieces.PID_pie(PIDs, output_path, ex)


####################################### PARTIAL AVGS #################################################

def R_candidates(Pr, Al, num_inst):
    # requires a set of alphabets and probabilities
    # where Pr[i].keys() = 'x1','x2','x1,y','x2,y','x1,x2','x1,x2,y' ....???
    # Al[i].keys() = 'x1', 'x2', 'y'

    # with MANY instances, this becomes VERY INEFFICIENT
    # since partial info is computed over each m instances -> O(m^2)
    # however, I assume that instances remain near m=4

    # TODO: poss frag into smaller fns

    xkeys = ['<iii/i>x', 'I<ii/i>x', '<ii/i>x']
    ykeys = ['<iii/i>y', 'I<ii/i>y', '<ii/i>y']
    wkeys = ['III/I', 'II/I', 'sqrt(III/I)', 'sqrt(II/I)'] #w for whole

    cand_keys = xkeys + ykeys + wkeys

    defunct_keys = ['<ii1/i>x','<ii1/i>y','<ii2/i>x','<ii2/i>y','<i1/i>x','<i1/i>y','<i2/i>x','<i2/i>y'] #eventually need to clean out some

    r = [{k:0 for k in cand_keys} for i in range(num_inst)]

    for i in range(num_inst):

        # PARTIAL X CANDIDATES
        if partial_info(Pr,Al,'y','x1,x2',i) == 0:
            for k in xkeys: r[i][k] = 0
        else:
            r[i]['<ii/i>x'] = partial_info(Pr,Al,'y','x1',i) * partial_info(Pr,Al,'y','x2',i) \
                              / partial_info(Pr,Al,'y','x1,x2',i)

        r[i]['<iii/i>x'] = r[i]['<ii/i>x'] * info(Pr[i],'x1','x2')
        r[i]['I<ii/i>x'] = r[i]['<ii/i>x']

        # PARTIAL Y CANDIDATES
        if partial_info(Pr,Al,'x1,x2','y',i) == 0:
            for k in ykeys: r[i][k] = 0
        else:
            r[i]['<ii/i>y'] = partial_info(Pr,Al,'x1','y',i) * partial_info(Pr,Al,'x2','y',i) \
                              / partial_info(Pr,Al,'x1,x2','y',i)

        r[i]['<iii/i>y'] = r[i]['<ii/i>y'] * info(Pr[i], 'x1', 'x2')
        r[i]['I<ii/i>y'] = r[i]['<ii/i>y']


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

        R['sqrt(III/I)'] = pow(R['III/I'], 1 / 2)
        R['sqrt(II/I)'] = pow(R['II/I'], 1 / 2)


    # MIXED PTWISE AND WHOLE CANDIDATES
    R['I<ii/i>y'] = pow(R['I<ii/i>y'] * Info(Pr,'x1','x2'), 1 / 2)
    R['I<ii/i>x'] = pow(R['I<ii/i>y'] * Info(Pr,'x1','x2'), 1 / 2)

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

        if print_PID:
            print('\n' + k + ':')
            for p in ['R','U1','U2','S']:
                print(p + ' = ' + str(PID[k][p]))

    return PID




if __name__ == "__main__":

    assert(len(sys.argv) == 2) # arg should be run_name

    output_path= 'C:/Users/Crbn/Documents/Code/Info/plots/'

    if sys.argv[1] == 'all':
        exs = ['xor','id', 'id2','id3','and','breaker','rdnerr', 'an', 'pwunq', 'xor2','pw_v2', 'pw_v3']
        for ex in exs:
            print('\n...decomposing ' + str(ex))
            plot_ex(ex, output_path)

    else:
        plot_ex(sys.argv[1], output_path)

    print("\nDone.\n")
