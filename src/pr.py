import numpy as np
from util import *




def build_p_atoms(pr_y, pr_x, pr_xx, pr_xy, pr_xxy, num_instances):

    # NOTE: each atom has mult poss labels

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

        p_atoms[i]['y'] = pr_y[i]
        p_atoms[i]['x1'] = pr_x[0][i]
        p_atoms[i]['x2'] = pr_x[1][i]
        p_atoms[i]['x1,x2'] = pr_xx[i]
        p_atoms[i]['x2,x1'] = pr_xx[i]
        p_atoms[i]['xx'] = pr_xx[i]
        p_atoms[i]['x1,y'] = pr_xy[0][i]
        p_atoms[i]['y,x1'] = pr_xy[0][i]
        p_atoms[i]['x2,y'] = pr_xy[1][i]
        p_atoms[i]['y,x2'] = pr_xy[1][i]
        p_atoms[i]['x1,x2,y'] = pr_xxy[i]
        p_atoms[i]['x2,x1,y'] = pr_xxy[i]
        p_atoms[i]['y,x1,x2'] = pr_xxy[i]
        p_atoms[i]['y,x2,x1'] = pr_xxy[i]
        p_atoms[i]['xxy'] = pr_xxy[i]
        p_atoms[i]['xx,y'] = pr_xxy[i]
        p_atoms[i]['y,xx'] = pr_xxy[i]


        p_atoms[i]['p(y|x1)'] = pr_xy[0][i]/pr_x[0][i]
        p_atoms[i]['p(y|x2)'] = pr_xy[1][i]/pr_x[1][i]
        p_atoms[i]['p(y|xx)'] = pr_xxy[i]/pr_xx[i]
        p_atoms[i]['p(x1|y)'] = pr_xy[0][i]/pr_y[i]
        p_atoms[i]['p(x2|y)'] = pr_xy[1][i]/pr_y[i]
        p_atoms[i]['p(xx|y)'] = pr_xxy[i]/pr_y[i]

    return p_atoms, p_keys




def find_prs_aligned(input, output, debug=False, disordered=False):
    # returns aligned pr_x[x_i][instances], pr_y[instances], pr_xy[xs][instances], pr_xxy[x1][x2][y][instances]
    # where instances are def'd and aligned by x1,x2,y possibilities

    # treats [0,1] != [0,1]
    # may need to improve effic over time

    # assumes all inputs have same max val

    if disordered: assert(False) #need to fix for inputs of len > 2

    if np.array(input).ndim > 1:
        num_rows = len(input)       #edges
        num_cols = len(input[0])    #instances
    else:
        assert(False) #shouldn't be using 1D
        num_rows = 1
        num_cols = len(input)

    assert(np.array(output).ndim == 1)

    max_input = max(max(input[i]) for i in rng(input))+1 #assumes all inputs have same max
    max_output = max(output)+1  # +1 since these are values (if max = 1, there are two vals, 0 & 1)

    # first sets are for counting, aligned for ordering
    pr_y = np.array([0 for i in range(max_output)])
    pr_x = np.array([[0 for i in range(max_input)] for j in range(num_rows)])
    pr_xx = np.array([[0 for i in range(max_input)] for j in range(max_input)])
    pr_xy = np.array([[[0 for i in range(max_output)] for j in range(max_input)] for k in range(num_rows)])
    pr_xxy = np.array([[[0 for i in range(max_output)] for j in range(max_input)] for k in range(max_input)])

    # disordered pr's
    if disordered:
        pr_xx_dis = [[0 for i in range(max_input)] for j in range(max_input)]
        pr_xxy_dis = [[[0 for i in range(max_output)] for j in range(max_input)] for k in range(max_input)]

    aligned_pr_y, aligned_pr_xx, aligned_pr_x, aligned_pr_xy, aligned_pr_xxy = [],[], [[] for i in range(num_rows)],[[] for i in range(num_rows)],[]
    if disordered:
        aligned_pr_xx_dis, aligned_pr_xxy_dis = [], []

    for i in range(num_cols): #each instance

        if disordered:
            in_dis = [input[0][i],input[1][i]]
            in_dis.sort()
            pr_xxy_dis[in_dis[0]][in_dis[1]][output[i]] +=1
            pr_xx_dis[in_dis[0]][in_dis[1]] +=1

        pr_xxy[[input[j][i] for j in rng(input)]+[output[i]]] += 1
        pr_xxy[input[0][i]][input[1][i]][output[i]] += 1
        pr_xx[input[0][i]][input[1][i]] += 1
        pr_y[output[i]] += 1

        for j in range(num_rows): #each edge
            pr_x[j][input[j][i]] += 1
            pr_xy[j][input[j][i]][output[i]] += 1

    #normalize
    for b in range(max_output):
        pr_y[b] /= num_cols
        if debug: assert(pr_y[b] <= 1 and pr_y[b] >= 0)

    for b in range(max_input):
        for d in range(max_input):
            pr_xx[b][d] /= num_cols
            if disordered:
                pr_xx_dis[b][d] /= num_cols
            if debug: assert (pr_xx[b][d] <= 1 and pr_xx[b][d] >= 0)
            for e in range(max_output):
                pr_xxy[b][d][e] /= num_cols
                if disordered:
                    pr_xxy_dis[b][d][e] /= num_cols
                if debug: assert(pr_xxy[b][d][e] <= 1 and pr_xxy[b][d][e] >= 0)

    for j in range(num_rows):
        for b in range(max_input):
            pr_x[j][b] /= num_cols
            if debug: assert(pr_x[j][b] <= 1 and pr_x[j][b] >= 0)
            for d in range(max_output):
                pr_xy[j][b][d] /= num_cols
                if debug: assert(pr_xy[j][b][d] <= 1 and pr_xy[j][b][d] >= 0)

    #align
    aligned_inputs, aligned_outputs = [[] for i in range(len(input))],[]
    for x1 in range(max_input):
        for x2 in range(max_input):
            for y in range(max_output):
                if pr_xxy[x1][x2][y] != 0:
                    aligned_pr_xxy += [pr_xxy[x1][x2][y]]

                    if disordered:
                        in_dis = [x1,x2]
                        in_dis.sort()
                        aligned_pr_xxy_dis += [pr_xxy_dis[in_dis[0]][in_dis[1]][y]]
                        aligned_pr_xx_dis += [pr_xx_dis[in_dis[0]][in_dis[1]]]


                    aligned_pr_y += [pr_y[y]]

                    aligned_pr_x[0] += [pr_x[0][x1]]
                    aligned_pr_x[1] += [pr_x[1][x2]]

                    aligned_pr_xx += [pr_xx[x1][x2]]

                    aligned_pr_xy[0] += [pr_xy[0][x1][y]]
                    aligned_pr_xy[1] += [pr_xy[1][x2][y]]

                    aligned_inputs[0] += [x1]
                    aligned_inputs[1] += [x2]
                    aligned_outputs += [y]


    # add back duplicates
    added = []
    for i in range(len(output)):
        for j in range(i):
            if i!=j and j not in added:
                if input[0][i] == input[0][j] and input[1][i] == input[1][j] and output[i] == output[j]:
                    x1,x2,y = input[0][i], input[1][i], output[i]
                    aligned_pr_xxy += [pr_xxy[x1][x2][y]]
                    aligned_pr_y += [pr_y[y]]

                    if disordered:
                        aligned_pr_xxy_dis += [pr_xxy_dis[x1][x2][y]]
                        #aligned_pr_xxy_dis += [pr_xxy_dis[x2][x1][y]]
                        aligned_pr_xx_dis += [pr_xx_dis[x1][x2]]
                        #aligned_pr_xx_dis += [pr_xx_dis[x2][x1]]

                    aligned_pr_x[0] += [pr_x[0][x1]]
                    aligned_pr_x[1] += [pr_x[1][x2]]

                    aligned_pr_xx += [pr_xx[x1][x2]]

                    aligned_pr_xy[0] += [pr_xy[0][x1][y]]
                    aligned_pr_xy[1] += [pr_xy[1][x2][y]]

                    aligned_inputs[0] += [x1]
                    aligned_inputs[1] += [x2]
                    aligned_outputs += [y]
                    added += [j]

    if debug:
        assert(len(aligned_pr_x[0]) == len(aligned_pr_xxy) == len(aligned_pr_xy[1]) == len(aligned_pr_y))

        print('\nutil.find_prs_aligned:\naligned_pr_y, aligned_pr_x, aligned_pr_xy, aligned_pr_xxy :')
        print(aligned_pr_y, aligned_pr_x, aligned_pr_xy, aligned_pr_xxy)
        print("\n")

    if disordered:
        return aligned_pr_y, aligned_pr_x, aligned_pr_xx, aligned_pr_xy, aligned_pr_xxy, \
               aligned_pr_xx_dis, aligned_pr_xxy_dis, \
               aligned_inputs, aligned_outputs

    else: return aligned_pr_y, aligned_pr_x, aligned_pr_xx, aligned_pr_xy, aligned_pr_xxy, aligned_inputs, aligned_outputs



