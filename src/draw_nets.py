



def basic(net, num_in):
    pos = nx.spring_layout(net)  # positions for all nodes
    nx.draw_networkx_nodes(net, pos,
                           nodelist=[i for i in range(num_in)],
                           node_color='blue',
                           node_size=500)
    nx.draw_networkx_nodes(net, pos,
                           nodelist=[i for i in range(num_in, N - 1)],
                           node_color='grey',
                           node_size=500)

    nx.draw_networkx_nodes(net, pos,
                           nodelist=[N],
                           node_color='red',
                           node_size=500)
    nx.draw_networkx_edges(net, pos)
    plt.show()