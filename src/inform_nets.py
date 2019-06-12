import sys, pickle, os
import net_generator, net_evaluator, draw_nets
from util import *



def all_combos(n, ex, output_path, pickle_type=None):
    orig_output_path = output_path
    output_path = output_path + 'candidates_' + str(ex) + '/'

    if pickle_type:
        Gs = from_pickle(orig_output_path + 'pickled_nets/', n, ex, pickle_type) 
    else:
        Gs = net_generator.gen_graphs(n, ex, output_path, debug=True, draw=False)
    
    if len(Gs) > 0:
        net_PIDs, node_PIDs = net_evaluator.eval(Gs, output_path)
        draw_nets.set_of_nets(net_PIDs, node_PIDs, Gs, output_path)
    else:
        print("\nWARNING: no viable networks were returned so no plots were generated ... ):\n")


def from_pickle(out_dir, n, ex, pickle_type, debug=True):

    if pickle_type == 'size-specific': 
        # could change to 'for-ex'

        Gs = pickle.load( open(out_dir + 'all_nets_size_' + str(n), "rb" ) )
        print("Loaded " + str(len(Gs)) + " pickled nets, starting to consume...")
        Gs = net_generator.keep_correct(Gs, ex)
        picklem(Gs, out_dir, n, ex=ex) 
        if debug: print("CorrectGs remaining lng = " + str(len(Gs)))
        
    elif pickle_type == 'ex-specific': #i.e. the keep_correct() filtering has already occured, just want to plot
        # could change to 'for-plot'
        Gs = pickle.load( open(out_dir + 'all_nets_size_' + str(n) + '_filtered_' + str(ex), "rb" ) )
        print("Loaded " + str(len(Gs)) + " pickled nets, using directly for plotting...")
    
    else: assert(False) #unknown pickle_type arg

    return Gs


def picklem(Gs, out_dir, n, ex=None):
    check_build_dir(out_dir)
    path = out_dir + 'all_nets_size_' + str(n)
    if ex is not None: path += '_filtered_' + str(ex)
    pickle.dump(Gs, open(path, "wb"))



if __name__ == "__main__":

    assert(len(sys.argv) in [3,4]) # args should be: ex, n, [pickle]

    output_path= 'C:/Users/Crbn/Documents/Code/Info/plots/'
    ex, n = sys.argv[1], int(sys.argv[2])
    if len(sys.argv)==4: 
        pickle_type=sys.argv[3]
    else: pickle_type = None
    print("\nInforming all combos on example " + str(ex) + ' with graphs max|n| = ' + str(n) + '\n')
    all_combos(n, ex, output_path, pickle_type=pickle_type)

    print("\nDone.\n")