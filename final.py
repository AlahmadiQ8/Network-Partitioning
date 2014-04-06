""" 
file input for network traffic
"""

import networkx as nx
import random
import sys
from math import ceil

def error(str):
	print str
	print '----> terminating'
	sys.exit(1)

def check(input_file):
	""" for debuging only """
	with open(input_file) as f:
		count = len(f.readline().split())
		for line in f:
			if len(line.split()) != count: 
				print 'error22: line numbers are not the same'
				break
		print 'file2: each line has ', count, ' nums'

def get_non_duplicates(list1):
	""" for debuging """
	newlist = []
	for i in list1:
		if i not in newlist:
			newlist.append(i)
	return newlist

def get_incoming_nodes(input_file):
	""" returns incoming nodes as list """
	incoming_nodes = []
	with open(input_file, 'r') as f:
		incoming_nodes = f.readline().split()
		incoming_nodes.pop(0)
	return [int(x) for x in incoming_nodes]

def get_outgoing_nodes(input_file):
	""" returns outgoing nodes as list """
	outgoing_nodes = []
	with open(input_file, 'r') as f:
		next(f)
		for line in f:
			outgoing_nodes.append(line.split()[0])
	return [int(x) for x in outgoing_nodes]

def filter_data(list1):
	""" helper function for map_traffic_matrix
	removes any duplicates for outgoing & incoming pairs """
	newlist = [] 
	flag = True
	for x,y,z in list1:
		for x1,y1,z1 in newlist:
			if (x,y) == (x1,y1): flag = False
		if flag: newlist.append((x,y,z))
		flag = True 
	return newlist

def map_traffic_matrix(input_file):
	"""
	create a list in the form of [ (incoming, outgoing, traffic), (incoming2, outgoing2, traffic) ...etc]
	this format is needed as input for the directed graph object from networkx
	"""
	incoming_nodes = get_incoming_nodes(input_file)
	outgoing_nodes = get_outgoing_nodes(input_file)
	mapped_list = []
	with open(input_file, 'r') as f:
		count = 0 # current line reference (correspond to outgoing node)
		next(f)
		for line in f:
			line = line.split()
			edges = [int(x) for x in line]
			edges = edges[1:]
			#print edges 
			for i in range(len(edges)):
				if edges[i]: 
					# we form (out, incom, traffic) for a driected graph using zip
					# then it's appended to mapped_list 
					#print zip(outgoing_nodes[count:count+1], incoming_nodes[i:i+1], edges[i:i+1])
					mapped_list.extend(zip(outgoing_nodes[count:count+1], incoming_nodes[i:i+1], edges[i:i+1]))
			count+=1
	# remove any nodes connecting to themselves
	mapped_list = [(x,y,z) for x,y,z in mapped_list if x!=y]
	# remove any duplicates 
	mapped_list = filter_data(mapped_list)
	return mapped_list

def create_graph(data):
	"""due to what it seems to be bugs in copying graphs (attributes are not copied
	this function returns a graph based on input data. it will serve as to create copies of the graph"""
	graph = nx.DiGraph()
	graph.add_weighted_edges_from(data)
	[nx.set_node_attributes(graph,'cluster', {node: 0}) for node in graph.nodes()]
	return graph


class Cluster(object):
	""" represent a cluster 
	attributes: graph, cluster id, list of nodes

	here, we get the graph G by reference since a collection of clusters have to refer
	to the same graph, hence, we don't use self.G = G as we do in the Solution object
	"""
	def __init__(self, graph, cluster_id, nodes):
		self.graph = graph
		self.cluster_id = cluster_id
		[nx.set_node_attributes(self.graph,'cluster', {n: cluster_id}) for n in nodes]
		self.nodes = [x for x,y in self.graph.nodes_iter(data=True) if y == {'cluster': cluster_id}]

	def node_cluster(self, node):
		""" returns cluster id of this node """ 
		return self.graph.node[node].items()[0][1]

	def get_nodes_attributes(self):
		return self.graph.nodes(data=True)

	def BB(self):
		""" returns backbone traffic of cluster """
		outgoing = [(x,y,z) for x,y,z in self.graph.out_edges_iter(self.nodes, data=True)\
				    if self.node_cluster(y) != self.cluster_id and self.node_cluster(x) == self.cluster_id]
		return sum([z['weight'] for x,y,z in outgoing])

	def num_of_nodes(self): return len(self.nodes)

	def __str__(self):
		return 'id: %d, # of nodes: %d, BB = %.2f' % (self.cluster_id, self.num_of_nodes(), self.BB())

	def add_node(self,node):
		""" HAS TO BE USED ONLY WITH REMOVE FOR SWAP OPERATION ONLY 
		otherwords, never use this function (assume private)"""
		nx.set_node_attributes(self.graph,'cluster', {node: self.cluster_id})
		self.nodes.append(node)

	def remove_node(self, node):
		""" randomly removes a node and returns it
		HAS TO BE USED ONLY WITH ADD FOR SWAP OPERATION ONLY 
		otherwords, never use this function (assume private)"""
		self.nodes.remove(node)
		return node

class Solution(object):
	""" Solution object representing n clusters 

	Here we do get a new copy of graph (G) because a solution is unique to the other solutions"""
	def __init__(self,G,expected_numb_of_clusters):
		""" initializes an initial solution of either n clusters or n+1 clusters 
		based on divisibility of total number of nodes to n where n = expected_numb_of_clusters.
		based on n, if any of the generated clusters violates constrains, program terminates
		"""
		self.G = G
		[nx.set_node_attributes(self.G,'cluster', {n: -1}) for n in self.G.nodes()]
		# the code divide nodes into balanced clusters 
		n = len(self.G.nodes())
		min_diff = 3   # minimum difference in the number of nodes between clusters (to balance clusters)
		(x,y) = divmod(n,expected_numb_of_clusters)
		if (abs(x-y) <= min_diff):
			sample = x 
			sample_last = y 
		else: 
			while(True):
				n -= 1
				x = n/expected_numb_of_clusters 
				y = len(self.G.nodes()) - x*expected_numb_of_clusters
				if (abs(x-y) <= min_diff):
					sample = x 
					sample_last = y
					break;
				if n == 0: 
					error("----> error, cannot balance clusters, adjust number of clusters")
		# construct clusters 
		nodelist = self.G.nodes()
		self.clusters = []
		for i in range(expected_numb_of_clusters):
			sample_nodes = random.sample(nodelist, sample)
			self.clusters.append(Cluster(self.G,i,sample_nodes))
			nodelist = [n for n in nodelist if n not in sample_nodes]
		if sample_last:
			if not nodelist: error('wrong calculations of clusters')
			self.clusters.append(Cluster(self.G,expected_numb_of_clusters, nodelist))

		sorted_clusters = sorted(self.clusters, key=lambda x: x.num_of_nodes())
		self.min_constraint = sorted_clusters[0].num_of_nodes()
		self.max_constraint = ceil(len(self.G.nodes())/2.0)

	def num_of_nodes(self): return sum([i.num_of_nodes() for i in self.clusters])

	def total_BB(self):
		"""returns total BB from clusters """
		return sum([i.BB() for i in self.clusters])

	def assign_Pi(self, minBB):
		""" assigns probability Pi = BB/minBB - 1 as dicussed with Nayaki """
		self.Pi = float(self.total_BB())/minBB - 1 

	def move(self):
		""" randomly moves a node from a cluster to another while 
		maintaining constraints """

		templist1 = [x for x in self.clusters if x.num_of_nodes() > self.min_constraint]
		c1 = random.choice(templist1).cluster_id
		templist2 = [x for x in self.clusters if (x.cluster_id != c1) and (x.num_of_nodes() <= self.max_constraint)]
		c2 = random.choice(templist2).cluster_id 
		removed_node = self.clusters[c1].remove_node(random.choice(self.clusters[c1].nodes))
		self.clusters[c2].add_node(removed_node)
		return (c1,c2,removed_node)

	def move_back(self, info):
		(c1,c2,removed_node) = info
		self.clusters[c1].add_node(self.clusters[c2].remove_node(removed_node))



if __name__ == '__main__':

	input_file = 'data/trafficMatrix_A(original).txt'

	# declare new graph
	data = map_traffic_matrix(input_file)
	G1 = create_graph(data)
	nn = len(G1.nodes())
	print '----> number of nodes = ', nn
	expected_numb_of_clusters = input('enter expected_numb_of_clusters:\n')
	print '----> expected_numb_of_clusters = ', expected_numb_of_clusters
	temp_solution = Solution(G1, expected_numb_of_clusters)   # this solution is only to obtain paratmers (min_contraint and max_constraint)
	print '----> max_constraint = ', temp_solution.max_constraint 
	print '----> min_constraint = ', temp_solution.min_constraint
	print '----> number of clusters = ' , len(temp_solution.clusters)

	# M : desired number of iterations 
	# k : limit on how long to spend on a solution 
	max_constraint = temp_solution.max_constraint
	min_constraint = temp_solution.min_constraint
	N = 10
	M = 50 
	k = 50 

	# ------generate N solutions------ 
	solutions = []
	for i in range(N):
		new_graph = create_graph(data)
		solutions.append(Solution(new_graph,expected_numb_of_clusters))
	
	# ------get solution with minimum BB------
	print '\ninitial solutions...'
	print [i.total_BB() for i in solutions]
	print ''
	solutions.sort(key=lambda x: x.total_BB())
	minBB = solutions[0].total_BB()
	[i.assign_Pi(minBB) for i in solutions]
	
	# ------sort solution based on Pi (actually, they will have the same ordering as with BB())------
	solutions.sort(key=lambda x: x.Pi)

	# ------START ALGORITHM------
	print '---> start algorithm...'
	i = 0
	for l1 in range(M):
		if i == N: i = 0

		for l2 in range(k):
			old_BB = solutions[i].total_BB()
			info = solutions[i].move()
			if solutions[i].total_BB() < old_BB:
				pass   # accept new solution 
			else: 
				solutions[i].move_back(info) # reject new solution 

		i+=1

	solutions.sort(key=lambda x: x.total_BB())
	print '---> finished algorithm, new solutions are...'
	print [i.total_BB() for i in solutions]
	print ''

	print 'clusters for best solution are...'
	print '----> check total number of nodes = ', len(solutions[0].G.nodes())
	for v in solutions[0].clusters: 
		print v
		print '\t', v.nodes

	print 'writing results to out.txt...'
	lines = []
	for v in solutions[0].clusters:
		line1 = 'cluster%d:' %(v.cluster_id)
		line2 = " ".join(str(e) for e in v.nodes)
		lines.extend([line1,line2])
		lines.append('')
	lines = '\n'.join(lines)

	with open('data/out.txt', 'w') as f:
		f.writelines(lines)