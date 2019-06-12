import os 

def rng(x):
    return range(len(x))

def avg(x):
	return sum(x)/len(x)

def check_build_dir(dirr):
    if not os.path.exists(dirr):
        print("\nCreating new directory for output at: " + str(dirr) + '\n')
        os.makedirs(dirr)