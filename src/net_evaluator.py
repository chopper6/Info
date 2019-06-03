import pr, draw_nets
from info_fns import *

#TODO: reorganize to be cleaner with previous build?

def judge_em(Gs,out_dir):
    i=0
    for G in Gs:
        PIDs = []
        for n in G.graph['hidden']+G.graph['outputs']:
            if len(G.in_edges(n)) == 2:
                PIDs += [eval_node_PID(G,n)]

            #TODO: add back nodes with one edge, all should be unique info

        PID = merge_node_PIDs(PIDs)
        draw_nets.with_PID(G, out_dir, PID,i)
        i+=1


def merge_node_PIDs(PIDs):
    PID_total = {k:{'R':0, 'U1':0, 'U2':0, 'S':0} for k in PIDs[0].keys()}
    for pid in PIDs:
        for k in pid.keys():
            for p in pid[k].keys():
                PID_total[k][p] += pid[k][p]

    return PID_total




def eval_node_PID(net,node):
    num_inst = len(net.nodes[node]['hist'])
    es = list(net.in_edges(node))
    e1, e2 = es[0][0],es[1][0]
    input = [net.nodes[e1]['hist'],net.nodes[e2]['hist']]
    output = net.nodes[node]['hist']

    # get pr's aligned by instances
    pr_y, pr_x, pr_xx, pr_xy, pr_xxy, aligned_inputs, aligned_outputs = pr.find_prs_aligned(input, output,
                                                                                            debug=False,
                                                                                            disordered=False)
    Al = {'x1': aligned_inputs[0], 'x2': aligned_inputs[1], 'y': aligned_outputs}  # alphabet dict

    # probability atom plots
    Pr, p_keys = pr.build_p_atoms(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, num_inst)

    # PID candidates
    Rs = R(Pr, Al, num_inst)
    PIDs = PID_decompose(Rs, Pr, print_PID=False)
    return PIDs



def R(Pr, Al, num_inst):
    #TODO: add back some candidates that I like less to compare with

    # requires a set of alphabets and probabilities
    # where Pr[i].keys() = 'x1','x2','x1,y','x2,y','x1,x2','x1,x2,y' ....???
    # Al[i].keys() = 'x1', 'x2', 'y'

    # with MANY instances, this becomes VERY INEFFICIENT
    # since partial info is computed over each m instances -> O(m^2)
    # however, I assume that instances remain near m=4

    cand_keys =  ['min>x', 'min>y']

    r = [{k:0 for k in cand_keys} for i in range(num_inst)]

    for i in range(num_inst):
        # PARTIAL X
        r[i]['min>x'] = min(partial_info(Pr,Al,'y','x1',i),partial_info(Pr,Al,'y','x2',i))

        # PARTIAL Y
        r[i]['min>y'] = min(partial_info(Pr, Al,'x1','y', i), partial_info(Pr, Al, 'x2','y', i))

    # AVERAGE pointwise r -> R
    R = {k: 0 for k in cand_keys}
    for i in range(num_inst):
        for k in cand_keys:
            R[k] += r[i][k]
    for k in cand_keys:
        R[k] /= num_inst

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