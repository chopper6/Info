import sys, math
import util, plot_pieces
import numpy as np
from math import log

import examples

# plots all info pieces for x's indepd and depd
# makes 3 such images
# TODO: incorporate pr_xxy, for ex some instances may occur twice

def calc_info_decomp(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, aligned_inputs, aligned_outputs, debug=False):
    all_keys = ['h(x)', 'h(x|y)', 'h(y)', 'h(y|x)', 'i']

    Is = [[] for i in range(4)]
    pr_instance = 1/len(pr_xxy)

    I_xyx = [[] for i in range(2)]

    for instance in range(len(pr_xxy)):
        for i in range(len(input)):
            Is[i] += [info_pieces(pr_xy[i][instance], pr_x[i][instance], pr_y[instance], debug=debug)]

        Is[2] += [info_pieces(pr_xxy[instance], pr_xx[instance], pr_y[instance], debug=debug)]
        Is[3] += [info_pieces(pr_xx[instance], pr_x[0][instance], pr_x[1][instance], debug=debug)]

        for i in range(len(input)):
            I_xyx[i] += [info_pieces(pr_xxy[instance], pr_xy[i][instance], pr_x[1-i][instance], debug=debug)]

    return Is, aligned_inputs, aligned_outputs, I_xyx


def flatten(I_orig, I_xyx, num_instances):
    I = [{} for i in range(num_instances)]
    orig_keys = ['h(x)', 'h(x|y)', 'h(y)', 'h(y|x)', 'i']
    new_keys = ['h(x1)', 'h(x2)', 'h(y)',
                'h(x1|x2)', 'h(x2|x1)', 'h(x1|y)', 'h(y|x1)', 'h(x2|y)', 'h(y|x2)',
                'h(xx)', 'h(xx|y)', 'h(y|xx)',
                'h(xy|x1)','h(x1|xy)','h(xy|x2)','h(x2|xy)',
                'i(x1,x2)', 'i(x1,y)', 'i(x2,y)', 'i(xx,y)']

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

    return I, new_keys


def build_p_atoms(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, num_instances):

    p_atoms = [{} for i in range(num_instances)]
    p_keys = ['p(y)','p(x1)','p(x2)','p(x1,x2)','p(x1,y)', 'p(x2,y)','p(x1,x2,y)']
    for i in range(num_instances):
        p_atoms[i]['p(y)'] = pr_y[i]
        p_atoms[i]['p(x1)'] = pr_x[0][i]
        p_atoms[i]['p(x2)'] = pr_x[1][i]
        p_atoms[i]['p(x1,x2)'] = pr_xx[i]
        p_atoms[i]['p(x1,y)'] = pr_xy[0][i]
        p_atoms[i]['p(x2,y)'] = pr_xy[1][i]
        p_atoms[i]['p(x1,x2,y)'] = pr_xxy[i]

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


    input, output = examples.get_io(sys.argv[1])

    # get pr's aligned by instances
    pr_y, pr_x, pr_xx, pr_xy, pr_xxy, pr_xx_dis, pr_xxy_dis, aligned_inputs, aligned_outputs = util.find_prs_aligned(input, output, debug=False, disordered=True)

    # regular, ordered decomp
    Is, aligned_inputs, aligned_outputs, I_xyx = calc_info_decomp(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, aligned_inputs, aligned_outputs)
    flat_I, flat_keys = flatten(Is, I_xyx, len(output))
    plot_pieces.entinf_decomp_v2(flat_I, flat_keys, aligned_inputs, aligned_outputs, output_path + '/ordered', sys.argv[1])
    p_atoms, p_keys = build_p_atoms(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, len(output))
    plot_pieces.prob_atoms(p_atoms, p_keys, aligned_inputs, aligned_outputs, output_path + '/ordered', sys.argv[1])

    #disordered decomp
    Is, aligned_inputs, aligned_outputs, I_xyx = calc_info_decomp(pr_y, pr_x, pr_xx_dis, pr_xy, pr_xxy_dis, aligned_inputs, aligned_outputs)
    flat_I, flat_keys = flatten(Is, I_xyx, len(output))
    plot_pieces.entinf_decomp_v2(flat_I, flat_keys, aligned_inputs, aligned_outputs, output_path+ '/disordered', sys.argv[1])
    p_atoms, p_keys = build_p_atoms(pr_y, pr_x, pr_xx_dis, pr_xy, pr_xxy_dis, len(output))
    plot_pieces.prob_atoms(p_atoms, p_keys, aligned_inputs, aligned_outputs, output_path+ '/disordered', sys.argv[1])
