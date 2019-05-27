from info_fns import *

# TODO later: multivariate bounds axioms

def check_axioms(Pr, PIDs, output_path, title):
    # takes a dict of PID dicts, where PIDs.keys() = 'poss','candidates' ...
    # writes a table of T/F for each axiom for each candidate
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
    LP = True
    for p in PID.keys():
        if PID[p] < 0: LP = False
    return LP

def M(Pr, PID):
    # curr just for R, but need to check
    if PID['R'] <= Info(Pr, 'x1', 'y') and PID['R'] <= Info(Pr, 'x2', 'y'):
        M=True
    else: M=False
    return M

def XX(Pr, PID):
    # strong version
    if PID['R'] <= Info(Pr, 'x1', 'x2'): XX=True
    else: XX=False
    return XX
