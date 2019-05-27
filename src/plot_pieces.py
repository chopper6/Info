import os, numpy as np, math
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib.gridspec import GridSpec

from info_fns import *

# TODO
# info_bars text is too big/ andor img too small (jP fixed)
# pies add titles, fix siden (doesn't need to be equal); make nicer
# axioms should test all ex's in a set...

def PID_pie(PIDs, output_path, title):
    #ks = PIDs.keys()
    siden = int(math.ceil(math.sqrt(len(PIDs))))
    fig, axs = plt.subplots(siden, siden)

    i=0
    for k in PIDs.keys():
        one_pie(PIDs[k], k, axs, math.floor(i/siden), i%siden)
        i+=1

    # TODO: fix, curr only blanks one
    for j in range(i,int(math.pow(siden,2))):
        axs[math.floor(i/siden), i%siden].axis('off')


    plt.savefig(output_path + "/pid_pies_" + str(title) + ".png")


def one_pie(pid, key, axs, x, y):
    labels = ['R','U1','U2','S']
    fracs = [pid['R'], pid['U1'], pid['U2'], pid['S']]

    axs[x, y].pie(fracs, labels=labels)
    axs[x, y].set_title(key)



def build_info_bars(Pr, Al):
    # shows partial info decomp by instances
    num_inst = len(Al['y'])
    keys = ['i(x1,y)','i(x2,y)','i(xx,y)','i(x1,x2)']
    I = [{k:0 for k in keys} for i in range(num_inst)]
    # so I[inst][key]
    for i in range(num_inst):
        for k in keys:
            rm_chars = ['(',')','i']
            al = k
            for r in rm_chars: al = al.replace(r,'')
            al = al.split(',')
            if al[0] == 'xx': a = 'x1,x2'
            else: a = al[0]
            I[i][k] = Info(Pr,a,al[1])

            I[i]['<' + k + '>' + al[0]] = partial_info(Pr,Al,al[1],a,i)
            I[i]['<' + k + '>' + al[1]] = partial_info(Pr,Al,a,al[1],i)

    return I

def info_bars(Pr, Al, output_path, title):

    Is = build_info_bars(Pr, Al)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    colors = ['#006699','#6600cc','#cc0066','#ff6666']
    rc('font')

    bars, keyz = [], []
    for i in range(len(Is)):
        row = []
        for k in Is[0].keys():
            row += [Is[i][k]]
            keyz += [k]
        bars += [row]

    plt.figure(1,[24, 10])

    # The position of the bars on the x-axis
    # TODO: curr for #bars per set = 4, could generalize
    r = [2*i for i in range(len(bars[0]))]
    barWidth = .3
    r_xticks = [r[s]+3*(barWidth) for s in range(len(r))]
    vbars = [r[s] - .5*barWidth for s in range(len(r))]

    blackbars = []
    darkgreybars = []
    for i in range(len(vbars)):
        if i  in blackbars: a,c = .8,'black'
        elif i in darkgreybars: a,c = .6, 'grey'
        else: a,c=.3, 'grey'
        plt.axvline(x=vbars[i], alpha=a, color=c)

    hrz = [0,-1,1,2]
    for h in hrz:
        plt.axhline(y=h, alpha=.2, color='grey')
    hrz_light = [.25,.5,.75]
    for h in hrz_light:
        plt.axhline(y=h, alpha=.1, color='grey')

    labels = []
    for i in range(len(Al['y'])):
        labels += [str(Al['x1'][i]) + ', ' + str(Al['x2'][i]) + ' --> ' + str(Al['y'][i])]

    for b in range(len(bars)):
        #r = [r[s]+barWidth+.05 for s in range(len(r))]
        if b < 4: l = labels[b]
        else: l = None
        r = [r[s] + barWidth + .05 for s in range(len(r))]
        plt.bar(r, bars[b], width=barWidth, edgecolor='white',color=colors[b%4], label=l, alpha=.7)


    plt.xticks(r_xticks, keyz, fontsize='large')
    plt.ylabel("Pointwise Info (i)", fontsize='x-large')
    plt.title(title + ' pieces', fontsize = 'xx-large')
    plt.legend(fontsize='xx-large', shadow=True, title='instances')
    plt.ylim(-1.2,2.3)
    plt.yticks(fontsize='x-large')
    #plt.yticks([0,.5,1,1.5,2],[0,.5,1,1.5,2])

    plt.tight_layout()
    plt.savefig(output_path + "/info_bars_" + str(title) + ".png")
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

    plt.figure(1,[20, 6])

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
    plt.savefig(output_path + "/pr_pieces_" + str(title) + ".png")
    plt.clf()