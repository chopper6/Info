import sys, pickle, os
import net_generator, net_evaluator, draw_nets, edge_fitness
from util import *



def all_combos(n, ex, protocol, output_path, pickle_type=None, output_choice='immed'):
    orig_output_path = output_path
    output_path = output_path + 'candidates_' + str(ex) + '/'

    if pickle_type:
        Gs = from_pickle(orig_output_path + 'pickled_nets/', n, ex, pickle_type) 
    else:
        Gs, all_Gs = net_generator.gen_graphs(n, ex, output_path, debug=True, draw=False,protocol=protocol)
    
    if len(Gs) > 0:
        net_PIDs, node_PIDs = net_evaluator.eval(Gs, output_path, hnormz=False, pid_protocol='single',output_choice=output_choice)
        edge_fitness.population(Gs)
        draw_nets.set_of_nets(net_PIDs, node_PIDs, Gs, output_path, n, popn_feature='num_nodes')

        #all_net_PIDs, all_node_PIDs = net_evaluator.eval(all_Gs, output_path, hnormz=False, pid_protocol='single',output_choice=output_choice)
        #draw_nets.set_of_nets(all_net_PIDs, all_node_PIDs, all_Gs, output_path, n, popn_feature='accuracy')
    
    else:
        print("\nWARNING: no viable networks were returned so no plots were generated ... ):\n")


def from_pickle(out_dir, n, ex, pickle_type, debug=True):


    if pickle_type in ['size-specific','size-spc','ss']: 
        # could change to 'for-ex'

        Gs = pickle.load( open(out_dir + 'all_nets_size_' + str(n), "rb" ) )
        print("Loaded " + str(len(Gs)) + " pickled nets, starting to consume...")
        Gs = net_generator.keep_correct(Gs, ex)
        picklem(Gs, out_dir, n, ex=ex) 
        if debug: print("CorrectGs remaining lng = " + str(len(Gs)))
        
    elif pickle_type in ['ex-specific','ex-spc','es']: #i.e. the keep_correct() filtering has already occured, just want to plot
        # could change to 'for-plot'
        Gs = pickle.load( open(out_dir + 'all_nets_size_' + str(n) + '_filtered_' + str(ex), "rb" ) )
        print("Loaded " + str(len(Gs)) + " pickled nets, using directly for plotting...")
    
    elif pickle_type == 'pre-combos':
        Gs = pickle.load( open(out_dir + 'all_nets_size_' + str(n) + '_precombos', "rb" ) )

    else: 
        print('\nERROR: unknown pickle_type:',pickle_type)
        assert(False) #unknown pickle_type arg

    return Gs


def picklem(Gs, out_dir, n, ex=None, chkpt=''):

    check_build_dir(out_dir)
    path = out_dir + 'all_nets_size_' + str(n)
    if chkpt=='pre-combos': path += '_precombos'
    if ex is not None: path += '_filtered_' + str(ex)
    pickle.dump(Gs, open(path, "wb"))
    print("\nPickled nets to " + str(path))



if __name__ == "__main__":

    assert(len(sys.argv) in [4,5]) # args should be: ex, n, proto, [pickle]

    output_path= 'C:/Users/Crbn/Documents/Code/Info/plots/'
    ex, n, protocol = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    if len(sys.argv)==5: 
        pickle_type=sys.argv[4]
    else: pickle_type = None
    print("\nInforming all combos on example " + str(ex) + ' with graphs max|n| = ' + str(n) + '\n')
    all_combos(n, ex, protocol, output_path, pickle_type=pickle_type)

    print("\nDone.\n")