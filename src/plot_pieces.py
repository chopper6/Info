import os, numpy as np, math
from matplotlib import pyplot as plt
from matplotlib import rc
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches

from info_fns import *
from util import *


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

    wedges, texts, autotxt = axs[x, y].pie(fracs, autopct=make_autopct(tot), shadow=True, startangle=90, colors=colors, radius=1.75, center=(2,1))

    for a in autotxt:
        a.set_fontsize(6)
        a.set_fontweight('semibold')
    for w in wedges:
        w.set_alpha(.4)

    axs[x, y].axis('equal')
    axs[x, y].set_title(key, weight='semibold')

def make_autopct(tot):
    def my_autopct(pct):
        val = round(pct*tot/100, 3)
        return '{p:.0f}% \n ({v:.2f})'.format(p=pct,v=val)
    return my_autopct

def pie_legend(axs=None, coords=None, posn=None, title=None):
    handles = []
    for c in range(len(pie_colors)):
        patch = mpatches.Patch(color=pie_colors[c], label=PID_pieces[c], alpha=.8)
        handles += [patch]
    if axs is None: lgd = plt.legend(handles=handles, title=title)
    else:
        if posn is None: lgd =axs[coords[0],coords[1]].legend(handles=handles,title=title)
        else: lgd= axs[coords[0],coords[1]].legend(handles=handles, loc=posn,title=title)
    return lgd


def build_i2_bars(Pr, Al):
    # note that specific is always performed on the second arg, ie I2(a,b) != I2(b,a)
    # TODO: generalize these 3 build fns?
    keys = ['I2(y;x1)', 'I2(y;x2)', 'I2(y;xx)','I2(x1;y)', 'I2(x2;y)', 'I2(xx;y)', 'I2(x1;x2)','I2(x2;x1)']
    keys += ['I2(x1;x2,y)', 'I2(x2;x1,y)']
    ikeys = ['i(x1;y)', 'i(x2;y)', 'i(xx;y)']
    mkeys = ['M(y|xx2)','M(y|xx1)','M(x1|xy)','M(x1|yx)', 'M(x2|xy)','M(x2|yx)']
    breaks = [3,6,8,10]
    num_inst = len(Al['y'])

    I2 = [{k:0 for k in keys+ikeys+mkeys} for i in range(num_inst)]

    for i in range(num_inst):
        ordered_keys = [] #really only need to build once

        for j in rng(keys):
            rm_chars = ['(',')','I2']
            k = keys[j]
            ordered_keys += [k]

            al = k
            for r in rm_chars: al = al.replace(r,'')
            al = al.replace('xx','x1,x2')
            letrs = al.split(';')
            I2[i][k] = i2(Pr, Al, letrs[0],letrs[1], i) 

        # non markovian's
        nonM = False
        if nonM:
            ordered_keys+=mkeys
            I2[i]['M(y|xx1)'] += non_Markv_dist_cond(Pr[i],'y','x1','x2')
            I2[i]['M(y|xx2)'] += non_Markv_dist_cond(Pr[i],'y','x2','x1')
            I2[i]['M(x1|xy)'] += non_Markv_dist_cond(Pr[i],'x1','x2','y')
            I2[i]['M(x1|yx)'] += non_Markv_dist_cond(Pr[i],'x1','y','x2')
            I2[i]['M(x2|xy)'] += non_Markv_dist_cond(Pr[i],'x2','x1','y')
            I2[i]['M(x2|yx)'] += non_Markv_dist_cond(Pr[i],'x2','y','x1')

        for j in range(len(ikeys)):
            k = ikeys[j]
            ordered_keys += [k]

            rm_chars = ['(',')','i']
            al = k
            for r in rm_chars: al = al.replace(r,'')
            al = al.split(';')
            if al[0] == 'xx': a = 'x1,x2'
            else: a = al[0]
            I2[i][k] = info(Pr[i],a,al[1])

    return I2, ordered_keys, breaks

def build_i1_bars(Pr, Al):
    # note that specific is always performed on the second arg, ie I2(a,b) != I2(b,a)
    # TODO: generalize these 3 build fns?
    keys = ['I1(y;x1)', 'I1(y;x2)', 'I1(y;xx)','I1(x1;y)', 'I1(x2;y)', 'I1(xx;y)', 'I1(x1;x2)','I1(x2;x1)']
    keys += ['I1(x1;x2,y)', 'I1(x2;x1,y)']
    ikeys = ['i(x1;y)', 'i(x2;y)', 'i(xx;y)']
    breaks = [3,6,8,10]
    num_inst = len(Al['y'])

    I1 = [{k:0 for k in keys+ikeys} for i in range(num_inst)]

    for i in range(num_inst):
        ordered_keys = [] #really only need to build once

        for j in rng(keys):
            rm_chars = ['(',')','I1']
            k = keys[j]
            ordered_keys += [k]

            al = k
            for r in rm_chars: al = al.replace(r,'')
            al = al.replace('xx','x1,x2')
            letrs = al.split(';')
            I1[i][k] = i1(Pr, Al, letrs[0],letrs[1], i) 

        for j in range(len(ikeys)):
            k = ikeys[j]
            ordered_keys += [k]

            rm_chars = ['(',')','i']
            al = k
            for r in rm_chars: al = al.replace(r,'')
            al = al.split(';')
            if al[0] == 'xx': a = 'x1,x2'
            else: a = al[0]
            I1[i][k] = info(Pr[i],a,al[1])

    return I1, ordered_keys, breaks


def build_h_cond_bars(Pr, Al):

    hkeys = ['h(x1|y)','h(x2|y)','h(xx|y)','h(y|x1)','h(y|x2)','h(y|xx)']
    ihkeys = ['i(x1,x2)/h','i(x1,y)/h','i(x2,y)/h','i(xx,y)/h']
    breaks = [3,6]
    num_inst = len(Al['y'])

    H = [{k:0 for k in hkeys+ihkeys} for i in range(num_inst)]
    # so I[inst][key]

    rm_chars = ['(',')','h','i','/']
    for i in range(num_inst):
        ordered_keys = [] #really only need to build once

        for j in rng(hkeys):
            k = hkeys[j]
            ordered_keys += [k]

            al = k
            for r in rm_chars: al = al.replace(r,'')
            al = al.replace('xx','x1,x2')
            lets = al.split('|')
            H[i][k] = h_cond(Pr[i],lets[0],lets[1])

        for j in rng(ihkeys):
            k = ihkeys[j]
            ordered_keys += [k]

            al = k
            for r in rm_chars: al = al.replace(r,'')
            lets = al.split(',')
            lets[0] = lets[0].replace('xx','x1,x2')
            H[i][k] = info(Pr[i],lets[0],lets[1])
            if H[i][k] != 0: H[i][k] /= h(Pr[i],'x1,x2,y')#h(Pr[i], lets[0]+','+lets[1])


    return H, ordered_keys, breaks



def build_info_bars(Pr, Al, hnormz=False, one_of_threes=False, use_static = False):

    if hnormz: print("\nWARNING: plot_pieces.build_info_bars: hnormz is ON\n")

    # shows partial info decomp by instances
    num_inst = len(Al['y'])
    ikeys = ['i(x1,y)','i(x2,y)','i(xx,y)'] #'i(x1,x2)'
    hkeys = []#'h(x1)','h(x2)','h(xx)','h(y)']

    static_ordered_keys =  ['I (x0_k;Y)','I (x1_k;Y)','I (xx_k;Y)','I (X0;y_j)','I (X1;y_j)','I (XX;y_j)']
    # skipped 'I (X0;Y)','I (X1;Y)','I (XX;Y)',

    reordered_keys =  ['<i(x1,y)>x1','<i(x2,y)>x2','<i(xx,y)>xx','<i(x1,y)>y','<i(x2,y)>y','<i(xx,y)>y']

    keys = hkeys + ikeys 
    if hnormz: breaks = [4,9,14,19]
    else: breaks = [0,3,6] #[4,7,10]

    I = [{k:0 for k in keys} for i in range(num_inst)]
    # so I[inst][key]
    for i in range(num_inst):
        ordered_keys = [] #really only need to build once


        for j in range(len(hkeys)):
            k = hkeys[j]
            ordered_keys += [k]

            rm_chars = ['(',')','h']
            al = k
            for r in rm_chars: al = al.replace(r,'')
            if al == 'xx': al = 'x1,x2'
            I[i][k] = h(Pr[i],al)

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

            if hnormz:
                if I[i]['<' + k + '>' + al[0]]>0: 
                    I[i]['<' + al[0] + ',' + al[1] + '>' + al[0] + '/h']= I[i]['<' + k + '>' + al[0]] /h(Pr[i],a)
                    I[i]['<' + al[0] + ',' + al[1] + '>' + al[1] + '/h']= I[i]['<' + k + '>' + al[1]]/h(Pr[i],al[1])
                else:
                    I[i]['<' + al[0] + ',' + al[1] + '>' + al[0] + '/h']= 0
                    I[i]['<' + al[0] + ',' + al[1] + '>' + al[1] + '/h']= 0
                ordered_keys += ['<' + al[0] + ',' + al[1] + '>' + al[0] + '/h']
                ordered_keys += ['<' + al[0] + ',' + al[1] + '>' + al[1] + '/h']


            if al[0] == 'xx' and one_of_threes:
                I[i]['<' + k + '>x1'] = partial_info_1of3(Pr,Al,al[1],'x2','x1',i)
                I[i]['<' + k + '>x2'] = partial_info_1of3(Pr,Al,al[1],'x1','x2',i)
                ordered_keys += ['<' + k + '>x1']
                ordered_keys += ['<' + k + '>x2']

                if hnormz: 
                    if I[i]['<' + k + '>x1']>0: 
                        I[i]['<xxy>x1/h']=I[i]['<' + k + '>x1']/ h(Pr[i],'x1')
                        I[i]['<xxy>x2/h']=I[i]['<' + k + '>x2']/ h(Pr[i],'x2')
                    else:
                        I[i]['<xxy>x1/h']=0
                        I[i]['<xxy>x2/h']=0
                    ordered_keys += ['<xxy>x1/h']
                    ordered_keys += ['<xxy>x2/h']


    if use_static: return I, reordered_keys, breaks, static_ordered_keys
    else: return I, ordered_keys, breaks, None

def info_bars(Pr, Al, output_path, title, bar_choice='I'):

    static_ordered_keys = None
    if bar_choice=='H': 
        type_title = "/h_bars_"
        Is, ordered_keys, darkgreybars = build_h_cond_bars(Pr, Al)
    elif bar_choice=='I': 
        type_title = "/info_bars_"
        Is, ordered_keys, darkgreybars, static_ordered_keys = build_info_bars(Pr, Al)
    elif bar_choice=='I2': 
        type_title = "/i2_bars_"
        Is, ordered_keys, darkgreybars = build_i2_bars(Pr, Al)
    elif bar_choice=='I1': 
        type_title = "/i1_bars_"
        Is, ordered_keys, darkgreybars = build_i1_bars(Pr, Al)
    else: assert(False) #unknown bar_choice

    num_inst = len(Al['y'])
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

    fig = plt.figure(1,[24, 10])

    # The position of the bars on the x-axis
    r = [num_inst/2*i for i in range(len(bars[0]))]
    barWidth = .3 
    r_xticks = [r[s]+num_inst*3/4*(barWidth) for s in range(len(r))]
    vbars = [r[s] - .5*barWidth for s in range(len(r))]

    blackbars = []
    #darkgreybars = [3,6,9,14] defd by build_info_bars() now
    for i in range(len(vbars)):
        if i  in blackbars: a,c = .8,'black'
        elif i in darkgreybars: a,c = .8, 'grey'
        else: a,c=.3, 'grey'
        plt.axvline(x=vbars[i], alpha=a, color=c)

    hrz = [0,-1,1,2]
    for h in hrz:
        plt.axhline(y=h, alpha=.2, color='grey')
    hrz_light = [.25,.5,.75,1.5]
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


    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Tahoma']

    if static_ordered_keys is None:
        plt.xticks(r_xticks, ordered_keys, fontsize='small')
        plt.ylabel("Pointwise Info (i)", fontsize='x-large')
        plt.title(title + ' pieces', fontsize = 'xx-large')
        plt.yticks(fontsize='x-large')
        plt.legend(fontsize='xx-large', shadow=True, title='instances', framealpha=0.5)
        plt.ylim(-1.2,2.3)
    # for report
    else: 
        plt.xticks(r_xticks, static_ordered_keys, fontsize='x-large')
        plt.ylabel("Pointwise Specific Information", fontsize='xx-large')
        plt.title('PWUNQ', fontsize = 25)
        plt.yticks(fontsize='x-large')
        plt.legend(fontsize='xx-large', shadow=True, framealpha=0.5)#, loc='upper left')
        plt.ylim(-.2,1.8)
        plt.yticks([0,.5,1,1.5])

    plt.tight_layout()
    plt.savefig(output_path + type_title + str(title) + ".png")
    plt.clf()
    #plt.close(fig) #prevents leaving them open, but results in wierd axis




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