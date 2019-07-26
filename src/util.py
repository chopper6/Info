import os 

def rng(x):
    return range(len(x))

def avg(x):
	return sum(x)/len(x)

def check_build_dir(dirr):
    if not os.path.exists(dirr):
        print("\nCreating new directory for output at: " + str(dirr) + '\n')
        os.makedirs(dirr)

def sort_a_by_b(A,B,reverse=False):
	#sorts by min
	a,b=A.copy(), B.copy() #otherwise will change in place
	not_done, iters = True,0
	while not_done:
		not_done = False
		for i in range(len(b)-1):
			if b[i] < b[i+1]:
				b = swap(b,i, i+1)
				a = swap(a,i, i+1)
				not_done=True
		iters += 1
		if iters > 10000: assert(False)
	if reverse:
		a.reverse(), b.reverse()
	return a,b

def swap(array,i,j):
	z=array[i]
	array[i] = array[j]
	array[j] = z
	return array

def safe_div_array(A,B):
	# a is numerator, b is divisor
	assert(len(A) == len(B))
	z=[]
	for i in rng(A):
		if B[i] == 0: z+=[0]
		else: z+=[A[i]/B[i]]
	return z