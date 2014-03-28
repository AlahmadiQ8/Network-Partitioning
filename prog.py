""" 
file input for network traffic
"""

import networkx as nx
import matplotlib.pyplot as plt

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


if __name__ == '__main__':
	input_file = 'Traffic.dat'
	# check(input_file)
	# print 'incoming_nodes: '
	# print get_incoming_nodes(input_file)
	# print 'outgoing_nodes: '
	# print get_outgoing_nodes(input_file)
	data = map_traffic_matrix(input_file)
	G = nx.DiGraph()
	G.add_weighted_edges_from(data)
	# for x,y,z in G.edges(data=True):
	# 	print x,y,z
	# for x,y,z in data:
	# 	print x,y,z 
	processed = [(x,y,z) for x,y,z in data if x!=y]
	processed_in_out = [(x,y) for x,y,z in processed]


	print len(data)
	# print len(processed_in_out)
	# print len(get_non_duplicates(processed_in_out))
	print len(G.edges())
	

