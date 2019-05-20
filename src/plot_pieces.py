import os, numpy as np
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib.gridspec import GridSpec

#todo: 'i' in sep subplot, instances in sep subplot
#todo: add info (x1,x2)?

#todo: add info/entropy plot (all), with instances in legend
#todo: add p() atoms plots


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


def entinf_decomp_v2(Is, keys, input, output, output_path, title):
    # Is must be flat in form: Is[instance]{flat_keys}, where keys==flat_keys

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    colors = ['#006699','#6600cc','#cc0066','#ff6666']
    rc('font')

    bars = []
    for i in range(len(Is)):
        row = []
        for k in range(len(keys)):
            row += [Is[i][keys[k]]]
        bars += [row]



    plt.figure(1,[20, 10])

    # The position of the bars on the x-axis
    r = [2*i for i in range(len(bars[0]))]
    barWidth = .3
    r_xticks = [r[s]+3*(barWidth) for s in range(len(r))]
    vbars = [r[s] - .5*barWidth for s in range(len(r))]

    for i in range(len(vbars)):
        if i == 16 or i==9 or i==20: a,c = .8,'black'
        elif i==22: a,c = .6, 'grey'
        else: a,c=.3, 'grey'
        plt.axvline(x=vbars[i], alpha=a, color=c)

    hrz = [0,-1,1,2]
    for h in hrz:
        plt.axhline(y=h, alpha=.2, color='grey')
    hrz_light = [.25,.5,.75]
    for h in hrz_light:
        plt.axhline(y=h, alpha=.1, color='grey')

    labels = []
    for i in range(len(output)):
        labels += [str(input[0][i]) + ', ' + str(input[1][i]) + ' --> ' + str(output[i])]

    for b in range(len(bars)):
        #r = [r[s]+barWidth+.05 for s in range(len(r))]
        if b < 4: l = labels[b]
        else: l = None
        r = [r[s] + barWidth + .05 for s in range(len(r))]
        plt.bar(r, bars[b], width=barWidth, edgecolor='white',color=colors[b%4], label=l, alpha=.7)


    plt.xticks(r_xticks, keys, fontsize='large')
    plt.ylabel("Pointwise Info (i) or Entropy (h)", fontsize='x-large')
    plt.title(title + ' pieces', fontsize = 'xx-large')
    plt.legend(fontsize='xx-large', shadow=True, title='instances')
    plt.ylim(-1.2,2.3)
    plt.yticks(fontsize='x-large')
    #plt.yticks([0,.5,1,1.5,2],[0,.5,1,1.5,2])

    plt.tight_layout()
    plt.savefig(output_path + "/infoentropy_pieces_" + str(title) + ".png")
    plt.clf()


def partial_avgs(Is, keys, input, output, output_path, title):
    # Is and keys must be from info_pieces.partial_avgs()

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    colors = ['#006699', '#6600cc', '#cc0066', '#ff6666']
    rc('font')

    bars = []
    for i in range(len(Is)):
        row = []
        for k in range(len(keys)):
            row += [Is[i][keys[k]]]
        bars += [row]

    plt.figure(1, [24, 10])

    # The position of the bars on the x-axis
    r = [2 * i for i in range(len(bars[0]))]
    barWidth = .3
    r_xticks = [r[s] + 3 * (barWidth) for s in range(len(r))]
    vbars = [r[s] - .5 * barWidth for s in range(len(r))]

    for i in range(len(vbars)):
        if i == 8 or i == 12:
            a, c = .8, 'black'
        elif i==14 or i==16: a,c = .6,'grey'
        else:
            a, c = .3, 'grey'
        plt.axvline(x=vbars[i], alpha=a, color=c)

    hrz = [0,-1,1,2]
    for h in hrz:
        plt.axhline(y=h, alpha=.2, color='grey')
    hrz_light = [.25,.5,.75]
    for h in hrz_light:
        plt.axhline(y=h, alpha=.1, color='grey')

    labels = []
    for i in range(len(output)):
        labels += [str(input[0][i]) + ', ' + str(input[1][i]) + ' --> ' + str(output[i])]

    for b in range(len(bars)):
        # r = [r[s]+barWidth+.05 for s in range(len(r))]
        if b < 4:
            l = labels[b]
        else:
            l = None
        r = [r[s] + barWidth + .05 for s in range(len(r))]
        plt.bar(r, bars[b], width=barWidth, edgecolor='white', color=colors[b % 4], label=l, alpha=.7)

    plt.xticks(r_xticks, keys, fontsize='large')
    plt.ylabel("Partial Average Info", fontsize='x-large')
    plt.title(title + ' pieces', fontsize='xx-large')
    plt.legend(fontsize='xx-large', shadow=True, title='instances')
    plt.ylim(-1.2, 2.2)
    plt.yticks(fontsize='x-large')
    # plt.yticks([0,.5,1,1.5,2],[0,.5,1,1.5,2])

    plt.tight_layout()
    plt.savefig(output_path + "/partial_avgs_" + str(title) + ".png")
    plt.clf()


def prob_atoms(Ps, keys, input, output, output_path, title):
    # Is must be flat in form: Is[instance]{flat_keys}, where keys==flat_keys

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    colors = ['#006699','#6600cc','#cc0066','#ff6666']
    rc('font')

    bars = []
    for i in range(len(Ps)):
        row = []
        for k in range(len(keys)):
            row += [Ps[i][keys[k]]]
        bars += [row]



    plt.figure(1,[10, 6])

    # The position of the bars on the x-axis
    r = [2*i for i in range(len(bars[0]))]
    barWidth = .3
    r_xticks = [r[s]+3*(barWidth) for s in range(len(r))]
    vbars = [r[s] - .5*barWidth for s in range(len(r))]

    for i in range(len(vbars)):
        if i == 10 or i==7: a,c = .6,'black'
        else: a,c=.4, 'grey'
        plt.axvline(x=vbars[i], alpha=a, color=c)

    hrz = [0,.25,.5,.75,1]
    for h in hrz:
        plt.axhline(y=h, alpha=.2, color='grey')

    labels = []
    for i in range(len(output)):
        labels += [str(input[0][i]) + ', ' + str(input[1][i]) + ' --> ' + str(output[i])]

    for b in range(len(bars)):
        #r = [r[s]+barWidth+.05 for s in range(len(r))]
        if b < 4: l = labels[b]
        else: l = None
        r = [r[s] + barWidth + .05 for s in range(len(r))]
        plt.bar(r, bars[b], width=barWidth, edgecolor='white',color=colors[b%4], label=l, alpha=.7)


    plt.xticks(r_xticks, keys, fontsize='large')
    plt.ylabel("Probability", fontsize='large')
    plt.title(title + ' probability pieces', fontsize = 'x-large')
    plt.legend(fontsize='x-large', shadow=True, title='instances')
    plt.ylim(-.1,1.1)
    plt.yticks(fontsize='large')
    #plt.yticks([0,.5,1,1.5,2],[0,.5,1,1.5,2])

    plt.tight_layout()
    plt.savefig(output_path + "/prob_pieces_" + str(title) + ".png")
    plt.clf()