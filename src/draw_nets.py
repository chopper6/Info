import networkx as nx, os
from matplotlib import cm
from matplotlib import pyplot as plt
from util import *

import plot_pieces


############################## Organization ################################

def set_of_nets(net_PIDs, node_PIDs, Gs, out_dir):
    check_build_dir(out_dir)

    if len(Gs) > 0: 
        population(Gs, out_dir, net_PIDs)

    for i in rng(Gs):
        with_PID(Gs[i], out_dir, net_PIDs[i],node_PIDs[i], i)






############################### POPULATION ####################################

def population(Gs, out_dir, PIDS):
    #TODO: add min>y
    pid_keys = PIDS[0]['min>x'].keys()
    assert(len(Gs) == len(PIDS))
    num_nodes = [len(Gs[i].nodes()) for i in range(len(Gs))] #index since order matters
    num_edges = [len(Gs[i].edges()) for i in range(len(Gs))]
    I = [sum([PIDS[i]['min>x'][p] for p in pid_keys]) for i in range(len(PIDS))]
    pid_for_plot = { p : [PIDS[i]['min>x'][p] for i in range(len(PIDS))] for p in pid_keys}

    numers = [num_nodes, num_edges, I] + [pid_for_plot[p] for p in pid_keys]
    numer_titles = ['# Nodes', '# Edges', 'Total Information'] + [p for p in PIDS[0].keys()]
    denoms = [num_nodes, num_edges, I]
    denom_titles = ['# Nodes', '# Edges', 'Total Information']

    x = [[numers[i][k] / denoms[j][k] for k in rng(numers[i])] for i in rng(numers) for j in rng(denoms)] + denoms

    x_titles = [[numer_titles[i] , denom_titles[j]] for i in rng(numer_titles) for j in rng(denom_titles)] + denom_titles

    #TODO: this is overkill
    for i in rng(x):
        for j in rng(x):
            #one_feature(x[i], x[j],x_titles[i],x_titles[j])
            pass

    S_frac = [pid_for_plot['S'][i]/I[i] for i in rng(I)]
    notR_frac = [1-pid_for_plot['R'][i]/I[i] for i in rng(I)]
    one_feature(num_edges, S_frac, '#Edges', 'S% ',out_dir)
    one_feature(num_nodes, S_frac, '#Nodes', 'S% ',out_dir)
    one_feature(num_edges, num_nodes, '#Edges', '#Nodes', out_dir,colorvec=S_frac, third_title='S%')
    #one_feature(num_edges, num_nodes, '#Edges', '#Nodes', out_dir,colorvec=notR_frac, third_title='notR%')
    one_feature(num_edges, num_nodes, '#Edges', '#Nodes', out_dir,colorvec=[pid_for_plot['S'][i] for i in rng(I)], third_title='S')
    one_feature(num_edges, num_nodes, '#Edges', '#Nodes', out_dir, colorvec=I, third_title='Itot')
    one_feature(num_edges, I, '#Edges', 'Itot',out_dir)
    one_feature(num_nodes, I, '#Nodes', 'Itot',out_dir)
    # TODO: seems some discrepancy btwn 2-way and 3-way plots...

def one_feature(x, y, x_title, y_title, out_dir, colorvec=None, showfig=False, third_title=None):

    # TODO: some form of annotation?

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
    else: plt.savefig(out_dir + title.replace(' ','_'))
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
        '''
        plot=True
        for input in G.graph['inputs']:

            if len(G.out_edges(input)) != 2: plot=False
        if plot:
            basic(G)
            plt.savefig(out_dir + str(i))
            plt.clf()

            i+=1
        '''

def with_PID(G, out_dir,PID,ordered_pids, title):
    # assumes ordered_pids are ordered by hidden nodes, in net_evaluator.eval() this is true

    check_build_dir(out_dir)
    plt.clf()
    fig, axs = plt.subplots(2, 3,figsize=(10,10))
    plot_pieces.one_pie(PID['min>x'], '<i>x', axs, 1, 0)
    plot_pieces.one_pie(PID['min>y'], '<i>y', axs, 1, 2)
    plot_pieces.pie_legend(axs=axs,coords=[1,1], posn='center')
    axs[1, 1].axis('off')

    pid_keys = ordered_pids[0]['min>x'].keys()

    # generate sums, will div by, so set to 1 if 0 and make sure numer is 0
    sums = [1 for i in rng(G.graph['hidden'])]
    for i in rng(G.graph['hidden']):
        if sum(ordered_pids[i]['min>x'][k] for k in pid_keys)==0:
            assert(ordered_pids[i]['min>x']['S']==0)
            assert(ordered_pids[i]['min>x']['R']==0)
        else: sums[i] = sum(ordered_pids[i]['min>x'][k] for k in pid_keys)

    colors_S = [ordered_pids[i]['min>x']['S']/sums[i] for i in rng(G.graph['hidden'])]

    colors_notR = [1-ordered_pids[i]['min>x']['R']/sums[i] for i in rng(G.graph['hidden'])]
    


    colors_I = [sum(ordered_pids[i]['min>x'][k] for k in pid_keys) for i in rng(G.graph['hidden'])]
    basic_spc_ax(G, axs, [0,0], hcolors=colors_S, title='S%')
    basic_spc_ax(G, axs, [0, 2], hcolors=colors_I, title='Info')
    #basic_spc_ax(G, axs, [0, 2], hcolors=colors_notR, title='NotR%')
    nets_cbar(colors_I, 'plasma', axs, [0,1], fig)
    axs[0,1].axis('off')

    fig.suptitle(title, size=20)
    plt.savefig(out_dir + str(title))
    plt.clf()
    plt.cla()
    plt.close(fig)


def nets_cbar(hcolors, cmap_choice, ax, coords, fig):
    cmap = cm.get_cmap(cmap_choice)
    im = plt.imshow(cmap(hcolors), cmap=cmap_choice, vmax=1, vmin=0)
    im.set_visible(False)
    plt.colorbar(im, ax=ax[coords[0], coords[1]])

def basic_spc_ax(net, ax, coords,  showfig=False, hcolors=None, title=None, cbar=False):
    pos = nx.circular_layout(net)  # positions for all nodes
    node_size, nalpha = 800, .6
    # plt.figure(1)

    nx.draw_networkx_edges(net, pos, arrows=True, ax=ax[coords[0], coords[1]])
    nx.draw_networkx_nodes(net, pos,
                           nodelist=net.graph['inputs'],
                           node_color='grey',
                           node_size=node_size, alpha=nalpha,
                           ax=ax[coords[0], coords[1]])
    if hcolors is None:
        nx.draw_networkx_nodes(net, pos,
                               nodelist=net.graph['hidden'],
                               node_color='grey',
                               node_size=node_size, alpha=nalpha,
                               ax=ax[coords[0], coords[1]])
    else:
        cmap = cm.get_cmap('plasma')
        nx.draw_networkx_nodes(net, pos,
                               nodelist=net.graph['hidden'],
                               node_color=cmap(hcolors),
                               node_size=node_size, alpha=nalpha,
                               ax=ax[coords[0], coords[1]])

    nx.draw_networkx_nodes(net, pos,
                           nodelist=net.graph['outputs'],
                           node_color='grey',
                           node_size=node_size, alpha=nalpha,
                           ax=ax[coords[0], coords[1]])
    labels = {n: net.nodes[n]['op'] for n in net.nodes()}
    nx.draw_networkx_labels(net, pos, labels, font_size=8, ax=ax[coords[0], coords[1]])
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
    labels = {n:net.nodes[n]['op'] for n in net.nodes()}
    nx.draw_networkx_labels(net, pos, labels, font_size=8)
    plt.axis('off')
    if showfig: plt.show()