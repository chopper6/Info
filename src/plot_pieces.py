import os, numpy as np, math
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches

from info_fns import *


pie_colors = ['#66ff33','#cc66ff','#ff0066','#00ffff']
bar_colors = ['#006699','#6600cc','#cc0066','#ff6666']
PID_pieces = ['R','U1','U2','S']

# TODO
# better colors w/o shadow for pies
# larger info title
# pies fix siden (doesn't need to be equal); make nicer

# add back vertical partitions to bar plots

def PID_pie(PIDs, output_path, title):
    #ks = PIDs.keys()
    siden = int(math.ceil(math.sqrt(len(PIDs))))
    fig, axs = plt.subplots(siden, siden,figsize=(8,8))

    i=0
    for k in PIDs.keys():
        one_pie(PIDs[k], k, axs, math.floor(i/siden), i%siden)
        i+=1

    for j in range(i,int(math.pow(siden,2))):
        axs[math.floor(j/siden), j%siden].axis('off')

    fig.suptitle(title, size=20)
    pie_legend()
    plt.savefig(output_path + "/pid_pies_" + str(title) + ".png")


def one_pie(pid, key, axs, x, y):
    tot = pid['R'] + pid['U1'] + pid['U2'] + pid['S']
    fracs = [pid['R']/tot, pid['U1']/tot, pid['U2']/tot, pid['S']/tot]
    colors, dels = [], []
    for f in range(len(fracs)):
        if fracs[f] == 0: dels += [f]
        else: colors += [pie_colors[f]]
    for f in dels:
        #print(f, fracs, dels)
        del fracs[f]
        for i in range(len(dels)): #need to shift remaining dels since list shrinks
            dels[i] -= 1

    wedges, texts, autotxt = axs[x, y].pie(fracs, autopct=make_autopct(tot), shadow=True, startangle=90, colors=colors)

    for a in autotxt:
        a.set_fontsize(6)
        a.set_fontweight('semibold')
    for w in wedges:
        w.set_alpha(.4)

    axs[x, y].axis('equal')
    axs[x, y].set_title(key)

def make_autopct(tot):
    def my_autopct(pct):
        val = round(pct*tot/100, 3)
        return '{p:.0f}% \n ({v:.2f})'.format(p=pct,v=val)
    return my_autopct

def pie_legend():
    handles = []
    for c in range(len(pie_colors)):
        patch = mpatches.Patch(color=pie_colors[c], label=PID_pieces[c], alpha=.8)
        handles += [patch]
    plt.legend(handles=handles)


def build_info_bars(Pr, Al):
    # shows partial info decomp by instances
    num_inst = len(Al['y'])
    ikeys = ['i(x1,x2)','i(x1,y)','i(x2,y)','i(xx,y)']
    hkeys = ['h(xx)']
    keys = ikeys + hkeys
    I = [{k:0 for k in keys} for i in range(num_inst)]
    # so I[inst][key]
    for i in range(num_inst):
        ordered_keys = [] #really only need to build once
        for j in range(len(ikeys)):
            k = ikeys[j]
            ordered_keys += [k]

            rm_chars = ['(',')','i']
            al = k
            for r in rm_chars: al = al.replace(r,'')
            al = al.split(',')
            if al[0] == 'xx': a = 'x1,x2'
            else: a = al[0]
            I[i][k] = info(Pr[i],a,al[1])

            I[i]['<' + k + '>' + al[0]] = partial_info(Pr,Al,al[1],a,i)
            I[i]['<' + k + '>' + al[1]] = partial_info(Pr,Al,a,al[1],i)
            ordered_keys += ['<' + k + '>' + al[0]]
            ordered_keys += ['<' + k + '>' + al[1]]

            if al[0] == 'xx':
                I[i]['<' + k + '>x1'] = partial_info_1of3(Pr,Al,al[1],'x2','x1',i)
                I[i]['<' + k + '>x2'] = partial_info_1of3(Pr,Al,al[1],'x1','x2',i)
                ordered_keys += ['<' + k + '>x1']
                ordered_keys += ['<' + k + '>x2']


        for j in range(len(hkeys)):
            k = hkeys[j]
            ordered_keys += [k]

            rm_chars = ['(',')','h']
            al = k
            for r in rm_chars: al = al.replace(r,'')
            if al == 'xx': al = 'x1,x2'
            I[i][k] = H(Pr,al)

    return I, ordered_keys

def info_bars(Pr, Al, output_path, title):

    Is, ordered_keys = build_info_bars(Pr, Al)
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    colors = bar_colors
    rc('font')

    bars = []
    for i in range(len(Is)):
        row = []
        for k in range(len(ordered_keys)):
            row += [Is[i][ordered_keys[k]]]
        bars += [row]

    plt.figure(1,[24, 10])

    # The position of the bars on the x-axis
    # TODO: curr for #bars per set = 4, could generalize
    r = [2*i for i in range(len(bars[0]))]
    barWidth = .3
    r_xticks = [r[s]+3*(barWidth) for s in range(len(r))]
    vbars = [r[s] - .5*barWidth for s in range(len(r))]

    blackbars = []
    darkgreybars = [3,6,9,14]
    for i in range(len(vbars)):
        if i  in blackbars: a,c = .8,'black'
        elif i in darkgreybars: a,c = .8, 'grey'
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


    plt.xticks(r_xticks, ordered_keys, fontsize='large')
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