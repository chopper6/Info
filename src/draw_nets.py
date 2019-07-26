import networkx as nx, os
from matplotlib import cm, colors as mpl_colors
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from util import *

import plot_pieces

EDGE_OP_COLORS = ['#336699','#660066']
EDGE_OP_STYLES = ['dashed','dotted']
EDGE_CMAP = 'PuBuGn' #'RdPu' 

NUM_NON_HIDDEN = 2

############################## Organization ################################

def set_of_nets(net_PIDs, node_PIDs, Gs, out_dir, N, feature='pid', popn_feature='num_nodes'):
    check_build_dir(out_dir)
    if feature=='fitness': fitness=True
    else: fitness = False
    
    just_popn = False
    if just_popn or popn_feature != 'num_nodes': print("\nWARNING: Only plotting population, not indiv net plots.\n")

    if len(Gs) > 0: 
        population(Gs, out_dir, net_PIDs, node_PIDs, N, fitness=fitness, popn_feature=popn_feature)
    if not just_popn and popn_feature=='num_nodes':
        for i in rng(Gs):
            if feature=='fitness': with_fitness(Gs[i], out_dir, i)
            elif feature=='pid': with_PID(Gs[i], out_dir, net_PIDs[i],node_PIDs[i], i)
            else: assert(False)






############################### POPULATION ####################################

def population(Gs, out_dir, net_PIDs, node_PIDs, N, fitness=True, correctness=True, popn_feature='num_nodes'):
    #TODO: add min>y
    # try S%/#nodes, 1/I_tot ect
    #sort nets by fitness, then bar chart 'em
    #color=#nodes + colorbar

    pid_types = ['min>x','min>y']

    pid_keys = net_PIDs[0]['min>x'].keys()
    assert(len(Gs) == len(net_PIDs))

    num_nodes = [len(Gs[i].nodes()) for i in rng(Gs)] #index since order matters
    num_edges = [len(Gs[i].edges()) for i in rng(Gs)]

    assert(len(num_nodes[i])==len(node_PIDs[i]) for i in rng(Gs))

    for pid_type in pid_types:

        # using sum_nodes(S)/sum_nodes(I) type formulas:
        # note that net_PIDs has NOT been prev normzd to num_nodes
        I_un_normzd = [sum([net_PIDs[i][pid_type][p] for p in pid_keys]) for i in range(len(net_PIDs))]
        I = [sum([net_PIDs[i][pid_type][p] for p in pid_keys])/(num_nodes[i]-NUM_NON_HIDDEN) for i in range(len(net_PIDs))]
        pid_for_plot = { p : [net_PIDs[i][pid_type][p] for i in rng(Gs)] for p in pid_keys}
        S_frac = safe_div_array(pid_for_plot['S'], I_un_normzd)
        S = [pid_for_plot['S']/(num_nodes[i]-NUM_NON_HIDDEN) for i in rng(Gs)]
        
        notR_frac = safe_div_array([(I_un_normzd[i]-pid_for_plot['R'][i])/(num_nodes[i]-NUM_NON_HIDDEN) for i in rng(Gs)], I_un_normzd) 

        # using sum_nodes(S/I) type formulas:
        S_node_frac, notR_node_frac = [], []
        for i in rng(Gs):
            node_pid = node_PIDs[i]
            this_S_node_frac, this_notR_node_frac = [], []
            assert(num_nodes[i]-NUM_NON_HIDDEN== len(node_pid))
            for j in range(num_nodes[i]-2): #-2 for 2 inputs
                S = node_pid[j][pid_type]['S']
                R = node_pid[j][pid_type]['R']
                I_tot = sum([node_pid[j][pid_type][p] for p in pid_keys])
                if I_tot != 0: 
                    this_S_node_frac += [S/I_tot]
                    this_notR_node_frac += [(I_tot - R) / I_tot]
                else: 
                    this_S_node_frac += [0]
                    this_notR_node_frac += [0]
            S_node_frac += [avg(this_S_node_frac)]
            notR_node_frac += [avg(this_notR_node_frac)]

        features = [I, S, S_node_frac, S_frac, notR_node_frac]
        titles = ['Avg Information', 'Avg Synergy','%Synergy', '% Synergy WRONG','NotR'] 
        #unused features: S_per_edge, notR_node_frac

        if fitness:
            # note that fitness is already avg edge fitness
            features += [[Gs[i].graph['fitness'] for i in rng(Gs)]]
            titles += ['fitness']

        if popn_feature == 'accuracy':
            accuracies = [Gs[i].graph['accuracy'] for i in rng(Gs)]
            entropy_of_acc = [Gs[i].graph['accuracy_entropy'] for i in rng(Gs)]
            
            for f in rng(features):
                ordered_accuracies, ordered_feature = sort_a_by_b(accuracies, features[f],reverse=True)
                one_feature_bar(ordered_accuracies , ordered_feature, 'Accuracy', titles[f], out_dir, N, cmap_choice='winter_r')

            for f in rng(features):
                ordered_ent_accuracies, ordered_feature = sort_a_by_b(entropy_of_acc, features[f],reverse=True)
                one_feature_bar(ordered_ent_accuracies , ordered_feature, 'Accuracy Entropy', titles[f], out_dir, N, cmap_choice='viridis')


        elif popn_feature == 'num_nodes':
            for f in rng(features):
                ordered_nnodes, ordered_feature = sort_a_by_b(num_nodes, features[f],reverse=True)
                one_feature_bar(ordered_nnodes , ordered_feature, '# Nodes', titles[f], out_dir, N, pid_type=pid_type)

        else: assert(False)

def one_feature_bar(x, y, x_title, y_title, out_dir, N, cmap_choice='cool_r',colorvec=None, showfig=False, third_title=None, pid_type=None):

    # TODO: 3-way plots could use improvement 
    assert(x_title == '# Nodes') #can try Acc and such later, just writing report for now
    alpha = .8

    cmap = cm.get_cmap(cmap_choice) #YlOrRd_r'
    norm = mpl_colors.Normalize(vmin=min(x),vmax=max(x)*1.1)
    colors = cmap(norm(x))
    bars = plt.bar([j for j in rng(y)],y,color=colors, alpha=alpha)
    
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm)
    cbar.set_label(x_title, size=10, weight='demibold',rotation=270,labelpad=25)
    cbar.ax.tick_params(labelsize=8)
    
    title = 'Graphs of ' + y_title + ' and Sizes ' #+ x_title
    if pid_type == 'min>y': title += ', Reverse Direction'
    plt.xticks([])
    plt.title(title)
    plt.xlabel('Various Graphs')
    plt.ylabel(y_title)
    plt.grid(alpha=.3)
    ax = plt.gca()
    ax.set_axisbelow(True)

    if showfig: plt.show()
    else: plt.savefig(out_dir + 'N' + str(N) + '_' + title.replace(' ','_'))
    plt.cla()
    plt.clf()
    plt.close()


def one_feature_scatter(x, y, x_title, y_title, out_dir, N, colorvec=None, showfig=False, third_title=None):

    # TODO: 3-way plots could use improvement 

    alpha = .2
    if len(x_title) == 2: x_title = x_title[0] + '_div_' + x_title[1]
    if len(y_title) == 2:  y_title = y_title[0] + '_div_' + y_title[1]

    if colorvec is not None:
        assert(third_title is not None) #colored scatter is for 3 features
        sc = plt.scatter(x,y, c=colorvec, alpha=alpha, cmap=plt.cm.get_cmap('plasma'))
        cbar = plt.colorbar(sc)
        cbar.set_label(third_title, rotation=270, size=10, weight='demibold')
        cbar.ax.tick_params(labelsize=8)
    else: plt.scatter(x,y,alpha=alpha)


    if third_title is not None: title = 'Population ' + third_title + ' by ' + y_title + ' by ' + x_title
    else: title = 'Population ' + y_title + ' by ' + x_title

    plt.title(title)
    plt.xlabel(x_title)
    plt.ylabel(y_title)

    if showfig: plt.show()
    else: plt.savefig(out_dir + 'N' + str(N) + '_' + title.replace(' ','_'))
    plt.cla()
    plt.clf()
    plt.close()





############################### ONE AT A TIME #################################

def save_mult(Gs, out_dir):

    check_build_dir(out_dir)

    plt.clf()
    i=0
    for G in Gs:
        basic(G)
        plt.savefig(out_dir + str(i))
        plt.clf()

        i+=1



def with_fitness(G, out_dir, title):

    check_build_dir(out_dir)
    plt.clf()
    fig, axs = plt.subplots(2, 3,figsize=(10,10))

    # eventually will add something here
    axs[1, 0].axis('off')
    axs[1, 1].axis('off')
    axs[1, 2].axis('off')

    elist = sorted(list(G.edges()))
    ecolors = []
    for i in rng(elist):
        e_s,e_t = elist[i][0], elist[i][1]
        ecolors += [G[e_s][e_t]['fitness']]

    basic_spc_ax(G, axs, [0,0], ecolors=ecolors, title='fitness')
    axs[0,1].text(1,1,'fitness = ' + str(G.graph['fitness']), size='x-large')

    maxx,minn = max(ecolors), min(ecolors)
    nets_cbar(ecolors, EDGE_CMAP, axs, [1,1], fig)
    #axs[1,1].add_artist(pie_legend)

    axs[0,1].axis('off')
    axs[0,2].axis('off')
    axs[1,1].axis('off')


    fig.suptitle(title, size=20)
    plt.savefig(out_dir + str(title))
    plt.clf()
    plt.cla()
    plt.close(fig)


def with_PID(G, out_dir,PID,node_pids, title):
    # assumes node_pids are ordered by hidden nodes, in net_evaluator.eval() this is true

    nodes_to_eval = G.graph['hidden'] #+G.graph['outputs']
    check_build_dir(out_dir)
    plt.clf()
    fig, axs = plt.subplots(2, 3,figsize=(10,10))
    plot_pieces.one_pie(PID['min>x'], '<i>x', axs, 1, 0)
    plot_pieces.one_pie(PID['min>y'], '<i>y', axs, 1, 2)
    pie_legend = plot_pieces.pie_legend(axs=axs,coords=[1,1], posn='lower left',title='PID Pie')
    axs[1, 1].axis('off')

    pid_keys = node_pids[0]['min>x'].keys()

    # generate sums, will div by, so set to 1 if 0 and make sure numer is 0
    sums = [1 for i in rng(nodes_to_eval)]
    for i in rng(nodes_to_eval):
        if sum(node_pids[i]['min>x'][k] for k in pid_keys)==0:
            assert(node_pids[i]['min>x']['S']==0)
            assert(node_pids[i]['min>x']['R']==0)
        else: sums[i] = sum(node_pids[i]['min>x'][k] for k in pid_keys)

    colors_Sx = [node_pids[i]['min>x']['S']/sums[i] for i in rng(nodes_to_eval)]


    sums = [1 for i in rng(nodes_to_eval)]
    for i in rng(nodes_to_eval):
        if sum(node_pids[i]['min>y'][k] for k in pid_keys)==0:
            assert(node_pids[i]['min>y']['S']==0)
            assert(node_pids[i]['min>y']['R']==0)
        else: sums[i] = sum(node_pids[i]['min>y'][k] for k in pid_keys)

    colors_Sy = [node_pids[i]['min>y']['S']/sums[i] for i in rng(nodes_to_eval)]

    #colors_notR = [1-node_pids[i]['min>x']['R']/sums[i] for i in rng(G.graph['hidden'])]
    

    colors_I = [sum(node_pids[i]['min>x'][k] for k in pid_keys) for i in rng(nodes_to_eval)]
    

    basic_spc_ax(G, axs, [0,0], hcolors=colors_Sx, title='S%>x')
    basic_spc_ax(G, axs, [0, 2], hcolors=colors_Sy, title='S%>y')
    basic_spc_ax(G, axs, [0, 1], hcolors=colors_I, title='Info')
    nets_cbar(colors_I, 'plasma', axs, [1,1], fig)
    nets_edge_op_legend(axs,[1,1])
    axs[1,1].add_artist(pie_legend)

    axs[1,1].axis('off')


    fig.suptitle(title, size=20)
    plt.savefig(out_dir + str(title))
    plt.clf()
    plt.cla()
    plt.close(fig)


def nets_cbar(colors, cmap_choice, ax, coords, fig):
    cmap = cm.get_cmap(cmap_choice)
    maxx, minn = max(colors), min(colors)
    im = plt.imshow(cmap(colors), cmap=cmap_choice, vmax=maxx, vmin=minn)
    im.set_visible(False)
    plt.colorbar(im, ax=ax[coords[0], coords[1]])


def nets_edge_op_legend(ax,coords, posn='upper left'):
    handles = []
    handles += [mpatches.Patch(color=EDGE_OP_COLORS[0], label='id', alpha=.6)]
    handles += [mpatches.Patch(color=EDGE_OP_COLORS[1], label='not', alpha=.6)]

    if posn is None: ax[coords[0],coords[1]].legend(handles=handles, title='Edge Ops')
    else:  ax[coords[0],coords[1]].legend(handles=handles, loc=posn, title='Edge Ops')



def basic_spc_ax(net, ax, coords,  node_label='layer',showfig=False, ecolors=None, hcolors=None, title=None, cbar=False):
    pos = nx.circular_layout(net)  # positions for all nodes
    node_size, nalpha = 800, .6
    # plt.figure(1)
    elist = sorted(list(net.edges()))

    lines, labels, eop_colors = {},{},[]
    for i in rng(elist):
        e = elist[i]
        if net[e[0]][e[1]]['op'] == 'id': 
            lines[e] = EDGE_OP_STYLES[0]
            labels[e] = 'id'
            eop_colors += [EDGE_OP_COLORS[0]]
        else: 
            lines[e] = EDGE_OP_STYLES[1]
            labels[e] = 'not'
            eop_colors += [EDGE_OP_COLORS[1]]


    if ecolors is not None:
        cmap = cm.get_cmap(EDGE_CMAP)
        ecolors=cmap(ecolors) #seems to work better than using cmap= arg in nx.draw_networkx_edges

        nx.draw_networkx_edges(net, pos, arrows=True, ax=ax[coords[0], coords[1]], label=labels, style=lines, edgelist=elist, edge_color=ecolors)
        nx.draw_networkx_edge_labels(net,pos,font_size=7, alpha=.8, edge_labels=labels,ax=ax[coords[0], coords[1]])
    else:nx.draw_networkx_edges(net, pos, arrows=True, ax=ax[coords[0], coords[1]], label=labels, style=lines, edgelist=elist, edge_color=eop_colors)
   


    nx.draw_networkx_nodes(net, pos,
                           nodelist=net.graph['inputs']+net.graph['outputs'],
                           node_color='grey',
                           node_size=node_size, alpha=nalpha,
                           ax=ax[coords[0], coords[1]])
    if hcolors is None:
        nx.draw_networkx_nodes(net, pos,
                               nodelist=net.graph['hidden'], #+net.graph['outputs'],
                               node_color='grey',
                               node_size=node_size, alpha=nalpha,
                               ax=ax[coords[0], coords[1]])
    else:
        cmap = cm.get_cmap('plasma')
        nx.draw_networkx_nodes(net, pos,
                               nodelist=net.graph['hidden'], #+net.graph['outputs'],
                               node_color=cmap(hcolors),
                               node_size=node_size, alpha=nalpha,
                               ax=ax[coords[0], coords[1]])

    # prev implmtn with grey output nodes:
    # nx.draw_networkx_nodes(net, pos,nodelist=net.graph['outputs'], node_color='grey', node_size=node_size, alpha=nalpha,ax=ax[coords[0], coords[1]])
    
    labels = {n: net.nodes[n][node_label] for n in net.nodes()}
    nx.draw_networkx_labels(net, pos, labels, font_size=6, ax=ax[coords[0], coords[1]])

    if title is not None:
        ax[coords[0], coords[1]].title.set_text(title)
        ax[coords[0], coords[1]].title.set_weight('semibold')
    ax[coords[0], coords[1]].axis('off')
    if showfig: plt.show()

def basic(net,showfig=False):
    pos = nx.circular_layout(net)  # positions for all nodes
    node_size, nalpha = 800, .6
    #plt.figure(1)

    nx.draw_networkx_edges(net, pos, arrows=True)
    nx.draw_networkx_nodes(net, pos,
                           nodelist=net.graph['inputs'],
                           node_color='blue',
                           node_size=node_size, alpha=nalpha)
    nx.draw_networkx_nodes(net, pos,
                           nodelist=net.graph['hidden'],
                           node_color='grey',
                           node_size=node_size, alpha=nalpha)
    nx.draw_networkx_nodes(net, pos,
                           nodelist=net.graph['outputs'],
                           node_color='red',
                           node_size=node_size, alpha=nalpha)
    labels = {}
    for n in net.nodes():
        if net.nodes[n]['op'] == 'hidden':  labels[n]=''
        else: labels[n]=net.nodes[n]['op']
    nx.draw_networkx_labels(net, pos, labels, font_size=8)
    plt.axis('off')
    if showfig: plt.show()