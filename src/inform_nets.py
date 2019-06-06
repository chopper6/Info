import sys, pickle, os
import net_generator, net_evaluator, draw_nets




def all_combos(n, ex, output_path, use_pickle=False):

    output_path = output_path + 'candidate_nets_' + str(ex) + '/'

    if use_pickle:
        Gs = from_pickle(output_path, n, ex) #TODO: revise this
    else:
        Gs = net_generator.gen_graphs(n, ex, output_path, debug=True, draw=False)
    
    if len(Gs) > 0:
        net_PIDs, node_PIDs = net_evaluator.eval(Gs, output_path)
        draw_nets.set_of_nets(net_PIDs, node_PIDs, Gs, output_path)


# TODO: various poss checkpoints to load pickle from
def from_pickle(out_dir, n, ex, debug=True):
    Gs = pickle.load( open(out_dir + 'all_op_nets_size_' + str(n), "rb" ) )
    print("Loaded " + str(len(Gs)) + " pickled nets, starting to consume...")
    Gs = net_generator.keep_correct(Gs, ex)
    if debug: print("CorrectGs remaining lng = " + str(len(Gs)))
    return Gs


def picklem(Gs, out_dir, n):
    # TODO: generalize pickle syntax and save after trimming for correctness
    if not os.path.exists(out_dir):
        print("\nCreating new directory for candidate nets at: " + str(out_dir) + '\n')
        os.makedirs(out_dir)
    pickle.dump(Gs, open(out_dir + 'all_op_nets_size_' + str(n), "wb"))



if __name__ == "__main__":

    assert(len(sys.argv) in [3,4]) # args should be: ex, n, [pickle]

    output_path= 'C:/Users/Crbn/Documents/Code/Info/plots/'
    ex, n = sys.argv[1], int(sys.argv[2])
    if len(sys.argv)==4: use_pickle=sys.argv[3]
    else: use_pickle = False
    print("\nInforming all combos on example " + str(ex) + ' with graphs max|n| = ' + str(n) + '\n')
    all_combos(n, ex, output_path, use_pickle=use_pickle)

    print("\nDone.\n")