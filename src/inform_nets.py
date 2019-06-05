import sys




def all_combos(n, ex, ):
    # just for testing purposes
    n = 6
    ex = 'xor'
    output_path = 'C:/Users/Crbn/Documents/Code/Info/plots/candidate_nets_' + str(ex) + '/'
    use_pickle = False
    if use_pickle:
        from_pickle(output_path, n, ex)
    else:
        Gs = gen_graphs(n, ex, output_path, debug=True, draw=False)
        net_evaluator.eval(Gs, output_path)



if __name__ == "__main__":

    assert(len(sys.argv) == 2) # args should be: n, ex

    output_path= 'C:/Users/Crbn/Documents/Code/Info/plots/'
    ex, n = sys.argv[1], sys.argv[2]
    print("\nInforming all combos on example " + str(ex) + ' with graphs max|n| = ' + str(n) + '\n')

    print("\nDone.\n")