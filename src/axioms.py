from info_fns import *

# TODO later: multivariate bounds axioms

def check_axioms_many(PR, PIDS, output_path):
    # PIDS = {} of exs, each with {} of candidates, each with RUUS pieces
    # PR = {} of exs


    axiom_titles = ['LP','M','XX']

    # init
    for p in PIDS.keys():
        axioms = {k: {} for k in PIDS[p].keys()}
        for k in PIDS[p].keys():
            for t in axiom_titles:
                axioms[k][t] = True
        break

    # for all examples
    for p in PIDS.keys():

        # for all candidates
        for k in PIDS[p].keys():

            # for all axioms
            for t in axiom_titles:
                if t == 'LP': a = LP(PIDS[p][k])
                elif t == 'M': a = M(PR[p], PIDS[p][k])
                elif t == 'XX': a = XX(PR[p], PIDS[p][k])
                else: assert(False)

                # if breaks axiom, add name of example
                if a == False:
                    if axioms[k][t] == True:
                        axioms[k][t] = p
                    else: axioms[k][t] = axioms[k][t] + ' ' + p


    write_axioms(axioms, output_path + 'axioms_ALL.csv')



def check_axioms(Pr, PIDs, output_path, title):
    # takes a dict of PID dicts, where PIDs.keys() = 'poss','candidates' ...
    # writes a table of T/F for each axiom for each candidate

    # axioms should test all ex's in a set...

    axioms = {k:{} for k in PIDs.keys()}
    for k in PIDs.keys():
        axioms[k]['LP'] = LP(PIDs[k])
        axioms[k]['M'] = M(Pr, PIDs[k])
        axioms[k]['XX'] = XX(Pr, PIDs[k])

    write_axioms(axioms, output_path + 'axioms_' + title + '.csv')

    return axioms

def write_axioms(axioms, file):
    #file should be a csv, full path
    with open(file, 'w') as f:
        axs = []
        f.write(',')
        for k in axioms.keys():
            for ax in axioms[k].keys():
                axs += [ax]
                f.write(str(ax) + ',')
            break #lol just want axioms[0].keys
        f.write('\n')
        for k in axioms.keys():
            f.write(k +',')
            for ax in axs:
                f.write(str(axioms[k][ax]) + ',')
            f.write('\n')


def LP(PID):
    # local positivity
    LP = True
    for p in PID.keys():
        if PID[p] < 0: LP = False
    return LP

def M(Pr, PID):
    # monotonicity
    # automatically holds for U and S, if LP holds
    if PID['R'] <= Info(Pr, 'x1', 'y') +.00001 and PID['R'] <= Info(Pr, 'x2', 'y') + .00001:
        M=True
    else: M=False
    return M

def XX(Pr, PID):
    # dependence and proportionality to i(x,x)
    # strong version
    if PID['R'] <= Info(Pr, 'x1', 'x2') + .00001 : XX=True
    else: XX=False

    return XX
