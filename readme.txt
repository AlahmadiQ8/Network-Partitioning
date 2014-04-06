* graph must be connected, otherwize a division by zero error may occur

* input file must be in a traffic matrix format like the files Dr.Nayaki emailed me (Traffic.txt & trafficMatrix_A(original).txt)

* it is assumed that node ids are indexed from 0 to n. this is EXTREMELY important. 
  program may have incorrect results if node ids are not indexed as described 

* any self looping node is ignored 

* any pair of outgoing and incoming node can only appear once, any additional pairs are ignored 

* if program is stuck in infinite loop, it is most likely that you chose an inappropriate number of clusters

* currently, the user must hardcode parameters in main()

* runtime is a bit slow, depend on k & M

-------RUNNING PROGRAM-------
* on terminal (mac): python final.py 
* as i mentioned before, as of now, everything is hardcoded in main() 
* networkx must be installed in order to run the python script
* on a mac, it's easily installed in terminal: 'sudo easy_install networkx', I do not know how on windows but it should be easy
* current paramters assumes you have a data folder that has the input files
* results are saved in 'data/out.txt'

	

-------USER INPUTS-------
* input_file: traffic matrix 
* expected_numb_of_clusters 
	desired number of clusters, actual numer may be increased by
	one to balance all clusters 
* M : desired number of iterations 
* k : limit on how long to spend on a solution 

-------INITIALIZE--------
choose N solutions. where each solution i: 
	* form C clusters (roughly equal) with the following constraints:
		- maximum number of nodes = total number of nodes / 2 
		- minumum number of nodes = 2 
	  These constraints are maintained through each move() operation (move node from one cluster to another)
	  e.i. these constraints are alreade considered in move() operation

	* add attribute: total BB traffic (sum of outgoing traffict from each cluster). 
	  this is the attribute that we aim to minimize 

	* add attribute: probability Pi = (BB(i)/min(BB(i))) - 1

-------SORT SOLUTIONS--------
sort solutions in ascending order based on Pi attribute

------START ALGORITHM------
for l1 = 0:M:    # outer loop
	for a partiulcar solution, loop from 0:k:   # inner loop
		old_BB = current BB
		move a node from a cluster to another 
		if new_BB < old_BB: 
			accept new solution 
		else: 
			move node back to its original cluster
		if loop reached k, go to next solution 

sort solutions, 
print best solution to text file 