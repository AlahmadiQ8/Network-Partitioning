""" 
file input for network traffic
"""

import networkx as nx
import matplotlib.pyplot as plt
import random
import sys

def error(str):
	print str
	print '---> terminating'
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

def add_to_graph(input_file, G):
	data = map_traffic_matrix(input_file)
	G.add_weighted_edges_from(data)
	[nx.set_node_attributes(G,'cluster', {node: 0}) for node in G.nodes()]

def generate_solution(G, expected_numb_of_clusters):
	""" returns an initial soluction of either n clusters or n+1 clusters 
	based on divisibility of total number of nodes to n where n = expected_numb_of_clusters

	based on n, if any of the generated clusters violates constrains, program terminates
	"""
	max_constraint = int(len(G.nodes())/2)
	min_constraint = 2
	temp = divmod(len(G.nodes()),expected_numb_of_clusters)
	sample = temp[0] if temp[0] <= max_constraint else error('max_constraint violated')
	sample_last = temp[1] if temp[1]>=min_constraint or temp[1]==0 else error('min_constraint violated')
	nodelist = G.nodes()
	clusters = []
	for i in range(1,expected_numb_of_clusters+1):
		sample_nodes = random.sample(nodelist, sample)
		#print sample_nodes
		clusters.append(Cluster(G,i,sample_nodes))
		nodelist = [i for i in nodelist if i not in sample_nodes]
		#print nodelist
		if not nodelist: print 'list is empty'
	if sample_last:
		if not nodelist: error('wrong calculations of clusters')
		clusters.append(Cluster(G,expected_numb_of_clusters+1, nodelist))
	return clusters




class Cluster(object):
	""" represent a cluster 
	attributes: graph, cluster id, list of nodes
	"""
	def __init__(self, G, cluster_id, nodes):
		self.G = G
		self.cluster_id = cluster_id
		[nx.set_node_attributes(G,'cluster', {n: cluster_id}) for n in nodes]
		self.nodes = [x for x,y in G.nodes_iter(data=True) if y == {'cluster': cluster_id}]

	def node_cluster(self, node):
		""" returns cluster id of this node """ 
		return self.G.node[node].items()[0][1]

	def BB(self):
		""" returns backbone traffic of cluster """
		outgoing = [(x,y,z) for x,y,z in G.out_edges_iter(self.nodes, data=True) if self.node_cluster(y) != self.cluster_id]
		#print '---> outgoing edges from cluster_%d are %s' % (self.cluster_id, str(outgoing).strip('[]'))
		return sum([z['weight'] for x,y,z in outgoing])

	def num_of_nodes(self): return len(self.nodes)

	def __str__(self):
		return 'id: %d, # of nodes: %d, BB = %.2f' % (self.cluster_id, self.num_of_nodes(), self.BB())


if __name__ == '__main__':
	input_file = 'data/traffic.dat'

	G = nx.DiGraph()
	add_to_graph(input_file, G)

	# desired number of clusters
	expected_numb_of_clusters = 4



	clusters = generate_solution(G,expected_numb_of_clusters)

	print len(G.nodes())
	print len(G.edges())
	print len([(x,y)  for x,y in G.nodes_iter(data=True) if y == {'cluster': 0}])

	
	for i in clusters:
		print '------------------------' 
		print i
		print '------------------------' 
		print i.nodes
		print '************************' 
		#print i.nodes

