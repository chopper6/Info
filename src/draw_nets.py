import networkx as nx, os
from matplotlib import pyplot as plt

import plot_pieces


def save_mult(Gs, out_dir):

    if not os.path.exists(out_dir):
        print("\nCreating new directory for candidate nets at: " + str(out_dir) + '\n')
        os.makedirs(out_dir)

    plt.clf()
    i=0
    for G in Gs:
        basic(G)
        plt.savefig(out_dir + str(i))
        plt.clf()
        i+=1

def with_PID(G, out_dir,PID,title):
    plt.clf()
    fig, axs = plt.subplots(2, 2,figsize=(8,8))
    plot_pieces.one_pie(PID['min>x'], '<i>x', axs, 1, 0)
    plot_pieces.one_pie(PID['min>y'], '<i>y', axs, 1, 1)
    basic(G, ax=axs, coords=[0,0])
    axs[0,1].axis('off')

    fig.suptitle(title, size=12)
    plot_pieces.pie_legend(axs=axs,coords=[0,1])
    plt.savefig(out_dir + str(title))
    plt.clf()


def basic(net,showfig=False, ax=None, coords=None):
    pos = nx.circular_layout(net)  # positions for all nodes
    node_size, nalpha = 800, .6
    #plt.figure(1)
    nx.draw_networkx_edges(net, pos, arrows=True, ax=ax[coords[0],coords[1]])
    nx.draw_networkx_nodes(net, pos,
                           nodelist=net.graph['inputs'],
                           node_color='blue',
                           node_size=node_size, alpha=nalpha,
                           ax=ax[coords[0],coords[1]])
    nx.draw_networkx_nodes(net, pos,
                           nodelist=net.graph['hidden'],
                           node_color='grey',
                           node_size=node_size, alpha=nalpha,
                           ax=ax[coords[0],coords[1]])

    nx.draw_networkx_nodes(net, pos,
                           nodelist=net.graph['outputs'],
                           node_color='red',
                           node_size=node_size, alpha=nalpha,
                           ax=ax[coords[0],coords[1]])
    labels = {n:net.nodes[n]['op'] for n in net.nodes()}
    nx.draw_networkx_labels(net, pos, labels, font_size=8,ax=ax[coords[0],coords[1]])
    if ax is None: plt.axis('off')
    else: ax[coords[0],coords[1]].axis('off')
    if showfig: plt.show()