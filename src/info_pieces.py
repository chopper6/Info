import sys, math
import util, plot_pieces
import numpy as np
from math import log, pow

import examples


#TODO: clean this convoluted shitshow

def plot_ex(ex, disordered = False):

    input, output = examples.get_io(ex)

    # get pr's aligned by instances
    if disordered: pr_y, pr_x, pr_xx, pr_xy, pr_xxy, pr_xx_dis, pr_xxy_dis, aligned_inputs, aligned_outputs = util.find_prs_aligned(input, output, debug=False, disordered=disordered)
    else: pr_y, pr_x, pr_xx, pr_xy, pr_xxy, aligned_inputs, aligned_outputs = util.find_prs_aligned(input, output, debug=False, disordered=disordered)

    # regular, ordered decomp
    Is, aligned_inputs, aligned_outputs, I_xyx = calc_info_decomp(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, aligned_inputs, aligned_outputs)
    flat_I, flat_keys = flatten(Is, I_xyx, len(output))

    avgs_I, avg_keys = partial_avg(flat_I, aligned_inputs, aligned_outputs)
    I, avg_keys = partial_avg_guesses(avgs_I, avg_keys, len(output))
    plot_pieces.partial_avgs(avgs_I, avg_keys,aligned_inputs, aligned_outputs, output_path, ex)

    plot_pieces.entinf_decomp_v2(flat_I, flat_keys, aligned_inputs, aligned_outputs, output_path, ex)
    p_atoms, p_keys = build_p_atoms(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, len(output))
    plot_pieces.prob_atoms(p_atoms, p_keys, aligned_inputs, aligned_outputs, output_path, ex)

    #disordered decomp
    if disordered:
        Is, aligned_inputs, aligned_outputs, I_xyx = calc_info_decomp(pr_y, pr_x, pr_xx_dis, pr_xy, pr_xxy_dis, aligned_inputs, aligned_outputs)
        flat_I, flat_keys = flatten(Is, I_xyx, len(output))
        plot_pieces.entinf_decomp_v2(flat_I, flat_keys, aligned_inputs, aligned_outputs, output_path+ '/disordered', ex)
        p_atoms, p_keys = build_p_atoms(pr_y, pr_x, pr_xx_dis, pr_xy, pr_xxy_dis, len(output))
        plot_pieces.prob_atoms(p_atoms, p_keys, aligned_inputs, aligned_outputs, output_path+ '/disordered', ex)





def calc_info_decomp(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, aligned_inputs, aligned_outputs, debug=False):
    all_keys = ['h(x)', 'h(x|y)', 'h(y)', 'h(y|x)', 'i']

    Is = [[] for i in range(4)]
    pr_instance = 1/len(pr_xxy)

    I_xyx = [[] for i in range(2)]

    for instance in range(len(pr_xxy)):
        for i in range(len(aligned_inputs)):
            Is[i] += [info_pieces(pr_xy[i][instance], pr_x[i][instance], pr_y[instance], debug=debug)]

        Is[2] += [info_pieces(pr_xxy[instance], pr_xx[instance], pr_y[instance], debug=debug)]
        Is[3] += [info_pieces(pr_xx[instance], pr_x[0][instance], pr_x[1][instance], debug=debug)]

        for i in range(len(aligned_inputs)):
            I_xyx[i] += [info_pieces(pr_xxy[instance], pr_xy[i][instance], pr_x[1-i][instance], debug=debug)]

    return Is, aligned_inputs, aligned_outputs, I_xyx


def partial_avg_guesses(I, keys, num_instances):
    new_keys = ['<iii/i>x','<iii/i>y', 'I<ii/i>x','I<ii/i>y', '<ii/i>x', '<ii/i>y']
    defunct_keys = ['<ii1/i>x','<ii1/i>y','<ii2/i>x','<ii2/i>y','<i1/i>x','<i1/i>y','<i2/i>x','<i2/i>y'] #eventually need to clean out some

    # '<ii1/i>x' would be U, not R. But broken by RdnErr

    Ixx_avg, Itot = 0,0 #Itot curr unused
    pow2 = 1/2
    for i in range(num_instances):
        Ixx_avg+=I[i]['i(x1,x2)']
        Itot +=I[i]['i(xx,y)']
    Ixx_avg /= num_instances
    Itot /= num_instances

    for i in range(num_instances):
        if I[i]['<i(xx,y)>xx'] == 0: I[i]['<i1/i>x'] = I[i]['<i2/i>x'] = I[i]['<ii/i>x'] \
            =I[i]['<ii1/i>x'] =I[i]['<ii2/i>x']  = 0
        else:
            I[i]['<ii/i>x'] = I[i]['<i(x1,y)>x']*I[i]['<i(x2,y)>x'] / I[i]['<i(xx,y)>xx']

            I[i]['<i1/i>x'] = I[i]['<i(x1,y)>x'] / I[i]['<i(xx,y)>xx']
            I[i]['<i2/i>x'] = I[i]['<i(x2,y)>x'] / I[i]['<i(xx,y)>xx']

            I[i]['<ii1/i>x'] = I[i]['<i(x1,y)>x'] * Ixx_avg / I[i]['<i(xx,y)>xx']
            I[i]['<ii2/i>x'] = I[i]['<i(x2,y)>x'] * Ixx_avg / I[i]['<i(xx,y)>xx']

        I[i]['<iii/i>x'] = I[i]['<ii/i>x'] * I[i]['i(x1,x2)']
        I[i]['I<ii/i>x'] = pow(I[i]['<ii/i>x'] * Ixx_avg, pow2)
        #I[i]['<ii/i>x'] = pow(I[i]['<ii/i>x'], 1/2)


        if I[i]['<i(xx,y)>y'] == 0: I[i]['<i1/i>y'] = I[i]['<i2/i>y'] = I[i]['<ii/i>y'] \
            = I[i]['<ii1/i>y'] = I[i]['<ii2/i>y'] = 0
        else:
            I[i]['<ii/i>y'] = I[i]['<i(x1,y)>y']*I[i]['<i(x2,y)>y'] / I[i]['<i(xx,y)>y']

            I[i]['<i1/i>y'] = I[i]['<i(x1,y)>y'] / I[i]['<i(xx,y)>y']
            I[i]['<i2/i>y'] = I[i]['<i(x2,y)>y'] / I[i]['<i(xx,y)>y']

            I[i]['<ii1/i>y'] = I[i]['<i(x1,y)>y'] * Ixx_avg / I[i]['<i(xx,y)>y']
            I[i]['<ii2/i>y'] = I[i]['<i(x2,y)>y'] * Ixx_avg / I[i]['<i(xx,y)>y']

        I[i]['<iii/i>y'] = I[i]['<ii/i>y'] * I[i]['i(x1,x2)']
        I[i]['I<ii/i>y'] = pow(I[i]['<ii/i>y'] * Ixx_avg, pow2)
        #I[i]['<ii/i>y'] = pow(I[i]['<ii/i>y'], 1/2) #do this after such that the above takes un-powd val




    # TODO: clean this up and turn into a plot + axiom checker
    pieces = {'R':{'I<ii/i>y':0, '<ii/i>y':0, 'I<ii/i>x':0, '<ii/i>x':0, 'NewY':0, 'NewX':0},
              'U1':{'I<ii/i>y':0, '<ii/i>y':0, 'I<ii/i>x':0, '<ii/i>x':0, 'NewY':0, 'NewX':0},
              'U2': {'I<ii/i>y': 0, '<ii/i>y': 0, 'I<ii/i>x':0, '<ii/i>x':0,'NewY':0, 'NewX':0},
              'S': {'I<ii/i>y': 0, '<ii/i>y': 0, 'I<ii/i>x':0, '<ii/i>x':0, 'NewY':0, 'NewX':0}
              }

    for i in range(num_instances):
        I[i]['NewX'] = I[i]['<ii/i>x']
        I[i]['NewY'] = I[i]['<ii/i>y']

    for i in range(num_instances):
        for k in pieces['R'].keys(): #messy, assuming all have same keys
            pieces['R'][k] += I[i][k]
            pieces['U1'][k] += I[i]['i(x1,y)']
            pieces['U2'][k] += I[i]['i(x2,y)']
            pieces['S'][k] += I[i]['i(xx,y)']


    for k in pieces['R'].keys():
        for p in pieces.keys():
            pieces[p][k] /= num_instances
            if k == 'NewY' and p=='R': pieces[p][k] = pow(pieces[p][k] * Ixx_avg, 1/2)
            if k == 'NewX' and p=='R': pieces[p][k] = pow(pieces[p][k] * Ixx_avg, 1/2)

        pieces['U1'][k] -= pieces['R'][k]
        pieces['U2'][k] -= pieces['R'][k]
        pieces['S'][k] -= (pieces['U1'][k] + pieces['U2'][k] + pieces['R'][k])

        print('\nPARTIALS, ' + k + ':')
        for p in pieces.keys():
            print(p + ' = ' + str(pieces[p][k]))



    for k in new_keys: keys += [k]
    return I, keys

def partial_avg(I, inputs, outputs):
    # inputs and output MUST be aligned
    # I MUST be flattened first
    num_instances = len(outputs)

    avg_titles = {'<i(x1,y)>':['x','y'], '<i(x2,y)>':['x','y'], '<i(xx,y)>':['x1','x2','xx','y']}
    avg_keys = []

    for i in range(num_instances):

        for ix in ['i(x1,y)', 'i(x2,y)']:
            if ix == 'i(x1,y)': in_num = 0
            else: in_num = 1

            I[i]['<' + ix + '>'], num = {}, {}
            I[i]['<' + ix + '>']['y'] = I[i]['<' + ix + '>']['x'] = I[i][ix]
            num['y'], num['x'] = 1,1
            for j in range(num_instances):
                if i!=j and outputs[i]==outputs[j]:
                    num['y'] += 1
                    I[i]['<' + ix + '>']['y'] += I[j][ix]
                if i!=j and inputs[in_num][i] == inputs[in_num][j]:
                    num['x'] += 1
                    I[i]['<' + ix + '>']['x'] += I[j][ix]
            I[i]['<' + ix + '>']['y'] /= num['y']
            I[i]['<' + ix + '>']['x'] /= num['x']


        I[i]['<i(xx,y)>'], num = {}, {}
        for k in avg_titles['<i(xx,y)>']:
            I[i]['<i(xx,y)>'][k] = I[i]['i(xx,y)']
            num[k] = 1

        for j in range(num_instances):
            if i!=j:
                if outputs[i]==outputs[j]:
                    num['y'] += 1
                    I[i]['<i(xx,y)>']['y'] += I[j]['i(xx,y)']
                if inputs[0][i] == inputs[0][j]:
                    num['x1'] += 1
                    I[i]['<i(xx,y)>']['x1'] += I[j]['i(xx,y)']
                if inputs[1][i] == inputs[1][j]:
                    num['x2'] += 1
                    I[i]['<i(xx,y)>']['x2'] += I[j]['i(xx,y)']
                if inputs[0][i] == inputs[0][j] and inputs[1][i] == inputs[1][j]:
                    num['xx'] += 1
                    I[i]['<i(xx,y)>']['xx'] += I[j]['i(xx,y)']

        for k in avg_titles['<i(xx,y)>']: I[i]['<i(xx,y)>'][k] /= num[k]

        #flatten
        for k in avg_titles.keys():
            for j in avg_titles[k]:
                I[i][k + j] = I[i][k][j]
                if i==0: avg_keys += [k+j]

    avg_keys += ['i(x1,y)','i(x2,y)','i(xx,y)','i(x1,x2)']
    return I, avg_keys


def flatten(I_orig, I_xyx, num_instances):
    I = [{} for i in range(num_instances)]
    orig_keys = ['h(x)', 'h(x|y)', 'h(y)', 'h(y|x)', 'i']
    new_keys = ['h(x1)', 'h(x2)', 'h(y)',
                'h(x1|x2)', 'h(x2|x1)', 'h(x1|y)', 'h(y|x1)', 'h(x2|y)', 'h(y|x2)',
                'h(xx)', 'h(xx|y)', 'h(y|xx)',
                'h(xy|x1)','h(x1|xy)','h(xy|x2)','h(x2|xy)',
                'i(x1,x2)', 'i(x1,y)', 'i(x2,y)', 'i(xx,y)',
                'II/I', 'sqrt(III/I)']
    obsolete_keys = ['sqrt(II/I)','III/I']

    for i in range(num_instances):
        I[i]['h(x1)'] = I_orig[0][i]['h(x)']
        I[i]['h(x2)'] = I_orig[1][i]['h(x)']
        I[i]['h(y)'] = I_orig[0][i]['h(y)']
        I[i]['h(x1|x2)'] = I_orig[3][i]['h(x|y)']
        I[i]['h(x2|x1)'] = I_orig[3][i]['h(y|x)']
        I[i]['h(x1|y)'] = I_orig[0][i]['h(x|y)']
        I[i]['h(y|x1)'] = I_orig[0][i]['h(y|x)']
        I[i]['h(x2|y)'] = I_orig[1][i]['h(x|y)']
        I[i]['h(y|x2)'] = I_orig[1][i]['h(y|x)']
        I[i]['h(xx)'] = I_orig[2][i]['h(x)']
        I[i]['h(xx|y)'] = I_orig[2][i]['h(x|y)']
        I[i]['h(y|xx)'] = I_orig[2][i]['h(y|x)']

        I[i]['h(xy|x1)'] = I_xyx[0][i]['h(x|y)']
        I[i]['h(x1|xy)'] = I_xyx[0][i]['h(y|x)']
        I[i]['h(xy|x2)'] = I_xyx[1][i]['h(x|y)']
        I[i]['h(x2|xy)'] = I_xyx[1][i]['h(y|x)']

        I[i]['i(x1,x2)'] = I_orig[3][i]['i']
        I[i]['i(x1,y)'] = I_orig[0][i]['i']
        I[i]['i(x2,y)'] = I_orig[1][i]['i']
        I[i]['i(xx,y)'] = I_orig[2][i]['i']

        # TODO: sep guesses into new img
        if False: #obsolete attempts
            if I[i]['i(xx,y)'] == 0: I[i]['iii/i'] = 0
            else: I[i]['iii/i'] = I[i]['i(x1,x2)']*I[i]['i(x1,y)']*I[i]['i(x2,y)'] / I[i]['i(xx,y)']

            if (1-I[i]['h(y|xx)']) == 0: I[i]['1-hhh/h'] = 0
            else: I[i]['1-hhh/h'] =I[i]['i(x1,x2)']*(1-I[i]['h(y|x1)'])*(1-I[i]['h(y|x2)']) / (1-I[i]['h(y|xx)'])

    I_avg = {}
    avg_keys = ['i(x1,x2)', 'i(x1,y)', 'i(x2,y)', 'i(xx,y)']
    for k in avg_keys: I_avg[k] = 0
    for i in range(num_instances):
        for k in avg_keys:
            I_avg[k] += I[i][k]
    for k in avg_keys: I_avg[k] /= num_instances

    for i in range(num_instances):
        if I_avg['i(xx,y)'] == 0: I[i]['III/I'] = I[i]['II/I'] = 0
        else:
            I[i]['III/I'] = I_avg['i(x1,x2)'] * I_avg['i(x1,y)'] * I_avg['i(x2,y)'] / I_avg['i(xx,y)']
            I[i]['II/I']= I_avg['i(x1,y)'] * I_avg['i(x2,y)'] / I_avg['i(xx,y)']

            I[i]['sqrt(III/I)'] = pow(I[i]['III/I'], 1/2)
            I[i]['sqrt(II/I)'] = pow(I[i]['II/I'], 1/2)

    # TODO: clean this up and turn into a plot + axiom checker
    pieces = {'R':{'sqrt(III/I)':0, 'II/I':0},
              'U1':{'sqrt(III/I)':0, 'II/I':0},
              'U2': {'sqrt(III/I)': 0, 'II/I': 0},
              'S': {'sqrt(III/I)': 0, 'II/I': 0}
              }

    for i in range(num_instances):
        for k in pieces['R'].keys(): #messy, assuming all have same keys
            pieces['R'][k] += I[i][k]
            pieces['U1'][k] += I[i]['i(x1,y)']
            pieces['U2'][k] += I[i]['i(x2,y)']
            pieces['S'][k] += I[i]['i(xx,y)']
    for k in pieces['R'].keys():
        for p in pieces.keys():
            pieces[p][k] /= num_instances

        pieces['U1'][k] -= pieces['R'][k]
        pieces['U2'][k] -= pieces['R'][k]
        pieces['S'][k] -= (pieces['U1'][k] + pieces['U2'][k] + pieces['R'][k])

        print('\n' + k + ':')
        for p in pieces.keys():
            print(p + ' = ' + str(pieces[p][k]))

    return I, new_keys


def build_p_atoms(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, num_instances):

    p_atoms = [{} for i in range(num_instances)]
    p_keys = ['p(y)','p(x1)','p(x2)','p(x1,x2)','p(x1,y)', 'p(x2,y)','p(x1,x2,y)', 'p(y|x1)','p(y|x2)','p(y|xx)','p(x1|y)','p(x2|y)','p(xx|y)']
    for i in range(num_instances):
        p_atoms[i]['p(y)'] = pr_y[i]
        p_atoms[i]['p(x1)'] = pr_x[0][i]
        p_atoms[i]['p(x2)'] = pr_x[1][i]
        p_atoms[i]['p(x1,x2)'] = pr_xx[i]
        p_atoms[i]['p(x1,y)'] = pr_xy[0][i]
        p_atoms[i]['p(x2,y)'] = pr_xy[1][i]
        p_atoms[i]['p(x1,x2,y)'] = pr_xxy[i]


        p_atoms[i]['p(y|x1)'] = pr_xy[0][i]/pr_x[0][i]
        p_atoms[i]['p(y|x2)'] = pr_xy[1][i]/pr_x[1][i]
        p_atoms[i]['p(y|xx)'] = pr_xxy[i]/pr_xx[i]
        p_atoms[i]['p(x1|y)'] = pr_xy[0][i]/pr_y[i]
        p_atoms[i]['p(x2|y)'] = pr_xy[1][i]/pr_y[i]
        p_atoms[i]['p(xx|y)'] = pr_xxy[i]/pr_y[i]

    return p_atoms, p_keys




########################## LIL CALCS ###################################

def info_pieces(pr_xy, pr_x, pr_y, debug=False):
    # seems that this piece may be < 0, if prior contains more info basically
    log_base = 2

    i_spe_fwd = -1*log(pr_x) / log(log_base)
    i_amb_fwd = -1*log(pr_xy)/log(log_base)+log(pr_y)/ log(log_base)
    #(checked, is same) i_amb_fwd2 = -1*log((pr_xy)/(pr_y)) / log(log_base)

    i_spe_rev = -1*log(pr_y)/ log(log_base)
    i_amb_rev = -1*log(pr_xy)/ log(log_base)+log(pr_x)/ log(log_base)

    #assert_bounds([i_spe_fwd, i_spe_rev, i_amb_fwd, i_amb_rev])

    info = log((pr_xy)/pr_x)
    i_tot = log((pr_xy) / (pr_x * pr_y)) / log(log_base)

    assert(i_tot < i_spe_fwd - i_amb_fwd + .0001 and i_tot > i_spe_fwd - i_amb_fwd - .0001)
    assert(i_tot < i_spe_rev - i_amb_rev + .0001 and i_tot > i_spe_rev - i_amb_rev - .0001)

    i_dict = {'h(x)':i_spe_fwd, 'h(x|y)':i_amb_fwd, 'h(y)':i_spe_rev,'h(y|x)':i_amb_rev, 'i':i_tot}
    return i_dict


def assert_bounds(vals):
    for val in vals:
        assert(val <=2 and val >= 0) #TODO: why is the upper bound 2 instead of 1?


def tot_corr(pr_xxy, pr_x, pr_y):
    #unlike piece this is done over instances
    log_base=2
    H_xxy, H_x, H_y = 0,[0 for i in range(len(pr_x))], 0
    for i in range(len(pr_xxy)):
        H_xxy += pr_xxy[i]*log(pr_xxy)/log(log_base)
        H_y += pr_y[i]*log(pr_y) / log(log_base)
        for j in range(len(pr_x)):
            H_x[j] += pr_x[j][i] * log(pr_x[j][i]) / log(log_base)

    info = sum(H_x) + H_y - H_xxy
    return info


def tot_corr_piece(pr_xxy, pr_x1, pr_x2, pr_y):
    #unlike above, this is just for pairwise
    log_base=2
    H_xxy = -1*pr_xxy*log(pr_xxy)/log(log_base)
    H_y = -1*pr_y*log(pr_y) / log(log_base)
    H_x1 = -1*pr_x1 * log(pr_x1) / log(log_base)
    H_x2 = -1*pr_x2 * log(pr_x2) / log(log_base)

    info = H_x1 + H_x2 + H_y - H_xxy

    print("total corr piece = " + str(info))
    assert(info >= 0 and info <= 1)

    return info


################## OBSOLETE ######################
def build_XOR():
    if sys.argv[1] == 'XOR':
        all_i, output = examples.XOR_expanded()
        i_titles = ['x1','x2','h1','h2','h3']
        for i in range(len(all_i)):
            for j in range(i):

                print("\n######################### Comparing " + str(i_titles[i]) + ' vs ' + str(i_titles[j]) + ' ###########################')
                Is,aligned_inputs, aligned_outputs = calc_info_decomp([all_i[i],all_i[j]], output, version)
                plot_pieces.decomp_plot(Is, aligned_inputs, aligned_outputs, output_path + '/XOR/', str(i_titles[i]) + ' vs ' + str(i_titles[j]) + '   ')

        print("\nDone.\n")

#########################################################

def print_soln(Irdn, Iunq, Isyn, Itot):
    Is, titles = [Irdn, Iunq[0], Iunq[1], Isyn, Itot], ['Irdn', 'Iunq[0]', 'Iunq[1]', 'Isyn', 'Itot']
    print("\nSolution:")
    for i in range(len(Is)):
        print(titles[i] + " : " + str(Is[i]))



if __name__ == "__main__":

    assert(len(sys.argv) == 2 or len(sys.argv) == 3) # arg should be run_name

    output_path= 'C:/Users/Crbn/Documents/Code/Info/plots/'

    if len(sys.argv) == 3:
        version = sys.argv[2]
    else: version = None

    if sys.argv[1] == 'all':
        exs = ['xor','id', 'id2','id3','and','breaker','rdnerr', 'an', 'pwunq', 'xor2','pw_v2', 'pw_v3']
        for ex in exs:
            print('\n...decomposing ' + str(ex))
            plot_ex(ex)

    else:
        plot_ex(sys.argv[1])

    print("\nDone.\n")
