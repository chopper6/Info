

def build_XOR():
    if sys.argv[1] == 'XOR':
        all_i, output = examples.XOR_expanded()
        i_titles = ['x1','x2','h1','h2','h3']
        for i in range(len(all_i)):
            for j in range(i):

                print("\n######################### Comparing " + str(i_titles[i]) + ' vs ' + str(i_titles[j]) + ' ###########################')
                Is,aligned_inputs, aligned_outputs = calc_info_decomp([all_i[i],all_i[j]], output, version)
                plot_pieces.decomp_plot(Is, aligned_inputs, aligned_outputs, output_path + '/XOR/', str(i_titles[i]) + ' vs ' + str(i_titles[j]) + '   ')

        print("\nDone.\n")




def partial_avg(Pr, I, inputs, outputs):
    # inputs and output MUST be aligned
    # I MUST be flattened first
    num_instances = len(outputs)

    avg_titles = {'<i(x1,x2)>':['x1','x2'], '<i(x1,y)>':['x','y'], '<i(x2,y)>':['x','y'], '<i(xx,y)>':['x1','x2','xx','y']}
    avg_keys = []

    for i in range(num_instances):

        # i(x1,y), i(x2,y)
        for ix in ['i(x1,y)', 'i(x2,y)']:
            if ix == 'i(x1,y)': in_num = 0
            else: in_num = 1

            I[i]['<' + ix + '>'], num = {}, {}
            I[i]['<' + ix + '>']['y'] = I[i]['<' + ix + '>']['x'] = I[i][ix]
            num['y'], num['x'] = 1,1
            for j in range(num_instances):
                if i!=j and outputs[i]==outputs[j]:
                    num['y'] += 1
                    I[i]['<' + ix + '>']['y'] += I[j][ix]
                if i!=j and inputs[in_num][i] == inputs[in_num][j]:
                    num['x'] += 1
                    I[i]['<' + ix + '>']['x'] += I[j][ix]
            I[i]['<' + ix + '>']['y'] /= num['y']
            I[i]['<' + ix + '>']['x'] /= num['x']


        # i(x1,x2)
        I[i]['<i(x1,x2)>'], num = {}, {}
        I[i]['<i(x1,x2)>']['x1'] = I[i]['<i(x1,x2)>']['x2'] = I[i][ix]
        num['x1'], num['x2'] = 1,1
        for j in range(num_instances):
            if i!=j and inputs[0][i] == inputs[0][j]:
                num['x1'] += 1
                I[i]['<i(x1,x2)>']['x1'] += I[j][ix]
            if i!=j and inputs[1][i] == inputs[1][j]:
                num['x2'] += 1
                I[i]['<i(x1,x2)>']['x2'] += I[j][ix]
        I[i]['<i(x1,x2)>']['x1'] /= num['x1']
        I[i]['<i(x1,x2)>']['x2'] /= num['x2']


        # i(xx,y)
        I[i]['<i(xx,y)>'], num = {}, {}
        for k in avg_titles['<i(xx,y)>']:
            I[i]['<i(xx,y)>'][k] = I[i]['i(xx,y)']
            num[k] = 1

        for j in range(num_instances):
            if i!=j:
                if outputs[i]==outputs[j]:
                    num['y'] += 1
                    I[i]['<i(xx,y)>']['y'] += I[j]['i(xx,y)']
                if inputs[0][i] == inputs[0][j]:
                    num['x1'] += 1
                    I[i]['<i(xx,y)>']['x1'] += I[j]['i(xx,y)']
                if inputs[1][i] == inputs[1][j]:
                    num['x2'] += 1
                    I[i]['<i(xx,y)>']['x2'] += I[j]['i(xx,y)']
                if inputs[0][i] == inputs[0][j] and inputs[1][i] == inputs[1][j]:
                    num['xx'] += 1
                    I[i]['<i(xx,y)>']['xx'] += I[j]['i(xx,y)']

        for k in avg_titles['<i(xx,y)>']: I[i]['<i(xx,y)>'][k] /= num[k]

        #flatten
        for k in avg_titles.keys():
            for j in avg_titles[k]:
                I[i][k + j] = I[i][k][j]
                if i==0: avg_keys += [k+j]

    avg_keys += ['i(x1,y)','i(x2,y)','i(xx,y)','i(x1,x2)']
    return I, avg_keys



def decomp_plot(Is, input, output, output_path, title):
    # should have Is[x1], Is[x2], Is[both]

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    keys = ['h(x)', 'h(x|y)', 'h(y)', 'h(y|x)'] #, 'i']
    keys_xx = ['(x1)', '(x1|x2)', '(x2)', '(x2|x1)']
    subtitles = ['x1-y','x2-y','x1x2-y','x1-x2']
    colors = ['#006699','#6600cc','#cc0066','#ff6666']
    rc('font')
    for z in range(4):

        # Values of each group
        bars, btms, i_bars = [], [], []
        for i in range(len(Is[0])):
            row = []
            for k in range(len(keys)):
                row += [Is[z][i][keys[k]]]
            bars += [row]

            i_bars += [Is[z][i]['i']]
            #if i==0: btms += [None] # for i in range(len(bars[0]))]
            #elif i==1: btms += [bars[0]]
            #else: btms += [[btms[-1][i] + bars[-1][i] for i in range(len(bars[-1]))]]

            #if i == 0: btms += [None]  # for i in range(len(bars[0]))]
            #elif i == 1: btms += [[max(bars[0]) for d in range(len(bars[0]))]]
            #else:  btms += [[btms[-1][i] + max(bars[-1]) for i in range(len(bars[-1]))]]

        # The position of the bars on the x-axis
        r = [1,3,5,7]
        barWidth = .3
        r_xticks = [r[s]+2.5*(barWidth+.02) for s in range(len(r))]

        # main H pieces
        #f, (a0, a1) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [3, 1]})

        plt.subplot(1,3,1)
        plt.plot()
        plt.xlim(0,4)
        plt.ylim(0,4)
        plt.xticks([],[])
        plt.yticks([],[])
        for i in range(len(output)):
            s= str(input[0][i]) + ', ' + str(input[1][i]) + ' --> ' + str(output[i])
            plt.text(1,(i+1)/2,s,color=colors[i], fontweight='bold')


        plt.subplot(1, 3, 2)
        for b in range(len(bars)):
            r = [r[s]+barWidth+.05 for s in range(len(r))]
            plt.bar(r, bars[b], width=barWidth, edgecolor='white',color=colors[b%4], label='mi ' + str(b), alpha=.7)
        plt.axvline(x=4.85, alpha=.4, color='grey')

        if z==3: plt.xticks(r_xticks, keys_xx)
        else: plt.xticks(r_xticks, keys)
        #plt.xlabel("Lattice")
        plt.ylabel("Entropy")
        plt.title(title + ' ' + str(subtitles[z]))
        #plt.legend()
        plt.ylim(0,2)
        plt.yticks([0,.5,1,1.5,2],[0,.5,1,1.5,2])

        # just i
        f=plt.subplot(1, 3, 3)
        barWidth = .25
        for b in range(len(i_bars)):
            plt.bar(1+b/4, i_bars[b], width=barWidth, edgecolor='white',color=colors[b%4], label='mi ' + str(b), alpha=.7)
        plt.axhline(y=0, color='grey', alpha=.5)

        plt.xlabel('total info')
        plt.ylim(-2,2)
        plt.yticks([-2,-1,0,1,2],[-2,-1,0,1,2])
        plt.xticks([],[])

        f.yaxis.tick_right()

        plt.tight_layout()
        plt.savefig(output_path + "/" + str(title) + "_" + str(subtitles[z]) + "_info_pieces.png")
        plt.clf()
