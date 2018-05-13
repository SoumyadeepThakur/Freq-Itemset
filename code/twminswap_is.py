import json
from itertools import combinations
import bisect
from collections import defaultdict
import numpy as np
import time
import sys
import random
import heapq as hq
import bisect

class TWMinSwap:
	def __init__(self, ipfile, max_size, decay = 0.95, window_size=60):
		self.window_size = window_size
		self.decay_rate = decay
		self.max_iset_size = 3
		self.inputfile = ipfile
		self.max_size = max_size
		self.K = [(set({}),0)]*max_size
		self._init_trans()

	
	def _init_trans(self):
		#Parse the json file and create a dict
		data = dict()
		with open(self.inputfile,'r') as infile:
			data = json.load(infile)
		infile.close()
		print ('Total No of transactions: '+str(len(data)))
		trans_list = list()
		for i in range(len(data)):
			trans_list.append(list(map(str,data[i]['Items'])))

		self.trans_list = trans_list
	
	'''
	def _init_trans(self):  # THIS IS ONLY FOR BMS
		#Parse bms data files and create dict
		trans_list = list()
		with open(self.inputfile, 'r') as infile:
			for line in infile:
				temp = line.split(" ")
				temp = temp[0:len(temp)-1]
				trans_list.append(temp)

		self.trans_list = trans_list
	'''

	def _ordering(self, trans):
		# cur_set is the set K
		# trans is the transaction I as set
		# phi is sorted list
		#psi = [itemset for itemset in self.K if itemset[0].issubset(trans)] # K intersection 2^I
		#print ('K-',self.K[0])
		psi = list(map(lambda t:t[0], filter(lambda t: len(t[0])>0 and t[0].issubset(trans), self.K)))
		itemset = set()
		psi.append(itemset)
		psi = sorted(psi, key = lambda x : len(x), reverse = True) # psi sorted descending in order of length
		T = set()
		phi = list()
		z = dict()
		#print ('Psi-',psi)
		for mu in psi:
			T.add(tuple(mu))
			#print('T=',T)
			z[tuple(mu)] = len(mu)+1
			L1mu = self._get_1larger_superset(mu, trans)
			#print ('L1mu=',L1mu)
			for nu in L1mu:
				#print ('nu=',nu)
				#print (nu == None)
				#print ('T in =',T)
				if tuple(nu) in T:
					z[tuple(nu)] = min(z[tuple(nu)]+1, len(nu)+1)
				else:
					z[tuple(nu)] = 1
					T.add(tuple(nu))
					#print ('T in else=',T)
				if z[tuple(nu)] == len(nu):
					phi.append(nu)
		#end	
		return (T,phi,z) # omega = (T,phi,z)


	def _most_rel(self, T, phi, z, trans):
		if len(phi)>0: mu = phi.pop(0)
		else: mu=set()

		if len(mu) == 0: return mu # ADDED

		L1mu = self._get_1larger_superset(mu, trans)
		for nu in L1mu:
			if tuple(nu) in T :
				z[tuple(nu)] += 1
			else:
				z[tuple(nu)] = 1
				T = T.union(tuple(nu))
			if z[tuple(nu)] == len(nu):
				phi = [nu] + phi # push front

		z[tuple(mu)] += 1
		return mu;

	def _get_1larger_superset(self, iset, transaction):
		# iset is as set
		# transaction is a set

		#size = len(iset) + 1
		#L1mu = list(filter(lambda u: iset.issubset(t) ,map(lambda t:set(t), list(combinations(transaction, r=size)))))
		L1mu = list()
		if len(iset) != len(transaction):
			L1mu = list(map(lambda u: {u}.union(iset), filter(lambda t: t not in iset, transaction)))
		return L1mu

	def _faded(self, trans):
		
		# Hotness Calculation
		#keys = list(map(lambda t: t[0], self.K))
		I = set(trans);
		hvaluetuple = list(filter(lambda t: len(t[0])==0 or (t[1]<1 and not t[0].issubset(I)), self.K))
		#print('hvaluetuple-',hvaluetuple)
		hvaluetuple = sorted(list(map(lambda t: (t[0],t[1]+1) if set(t[0]).issubset(I) else (t[0],t[1]), hvaluetuple)), key=lambda u:u[1]) #get sets and y values
		hottuplpes=list()
		for i in range(len(hvaluetuple)):
			hottuplpes.append((hvaluetuple[i][0],i+1))
		#hvalues = list(map(lambda t:t[1], inttuple))
		#h = dict()
		#for mu in K:
		#	mu_tuple = tuple(mu)
		#	h[mu_tuple] = bisect.bisect_right(inttuple, hvalues)

		#hot_queue = list[]
		hottuplpes = list(map(lambda t:(t[1]+1/(1+len(t[0])),t[0]), hottuplpes))
		#hottuplpes = list(filter(lambda t: t[0]<1 and not t[1].issubset(I), hvaluetuple))
		hq.heapify(hottuplpes)
		#print('Hot tuples-',hvaluetuple)
		return hottuplpes

	def _most_cold(self, theta):
		
		coldtuple = hq.heappop(theta)
		return set(coldtuple[1])

	def mine(self):

		#count = dict()
		trans_no = 0
		for trans in self.trans_list:
			#decay each item
			self.K = list(map(lambda t: (t[0], t[1]*self.decay_rate), self.K))
			# Faded
			# normal priority queue
			theta = self._faded(trans)
			# Ordering
			#print ('THETA-',theta)
			omega_T, omega_phi, omega_z = self._ordering(trans)
			while len(omega_T) > 0 or len(omega_phi)>0 or len(omega_z) >0:
				mostRel = self._most_rel(omega_T, omega_phi, omega_z, trans)
				if len(mostRel) > 0:
					if tuple(mostRel) in self.K:
						count[mostRel] += 1
					elif len(theta) > 0:
						mostCold = self._most_cold(theta)
						#self.K.remove((mostCold,_))
						for item,cnt in self.K:
							if item == mostCold:
								self.K.remove((item,cnt))
								break
						self.K.append((mostRel,1))
						#count[mostRel] = 1
					else:
						break
				else:
					break
			trans_no+=1;

			if trans_no % self.window_size == 0:
				# print to file
				#print('K=',self.K)
				self.show_topk(trans_no)
				#for iset in self.K:
				#	print('elem',iset)
				print('window',  trans_no//self.window_size)
				
			
	def show_topk(self, trans_no):

		klist = sorted(self.K, key=lambda t: t[1], reverse=True)
		num = 0
		for i in range(min(30,len(klist))):
			print (list(klist[i][0])," - ",klist[i][1])
		
		with open('tw3.txt','a+') as gt_file: # all  itemsets
			win_no = trans_no//self.window_size

			gt_file.write("Window")
			gt_file.write("%s\n" % win_no)
			#for item, count in list(zip(suggest,sug_count)):
			#	gt_file.write("%s - " % item)
			#	gt_file.write("%s\n" % count)
			for i in range(min(30,len(klist))):
				gt_file.write("%s" % list(klist[i][0]))
				gt_file.write(" - ")
				gt_file.write("%s\n" % klist[i][1])
				#gt_file.write


		with open('tw4.txt','a+') as gt_file: # only non singular itemsets
			win_no = trans_no//self.window_size

			gt_file.write("Window")
			gt_file.write("%s\n" % win_no)
			#for item, count in list(zip(suggest,sug_count)):
			#	gt_file.write("%s - " % item)
			#	gt_file.write("%s\n" % count)
			for i in range(len(klist)):
				if len(klist[i][0]) > 1:
					gt_file.write("%s" % list(klist[i][0]))
					gt_file.write(" - ")
					gt_file.write("%s\n" % klist[i][1])
				#gt_file.write


if __name__ == '__main__':
	start_time = time.time();
	#tw = TWMinSwap('BMS/bms1_data',200)
	tw = TWMinSwap('trans_data.json',100)
	tw.mine()
	print("--- %s seconds ---" % (time.time() - start_time))
