import json
from itertools import combinations
import bisect
from collections import defaultdict
import numpy as np
import time
import sys
import random
from trie import Trie

cur_list = dict() # current items present in the frequent itemset
itemset = list() # map of item to its index (if required)
sum_freq=0.0
max_count=1.0

def read_items(): #list of all items

	global itemset
	with open ("BMS/bms1_items","r") as infile:
		itemset = infile.readlines()
	for i in range(len(itemset)):
		itemset[i] = itemset[i].rstrip()

	itemset.sort()

class FrequentItemSet(object):

	def __init__(self, ipfile, window_size = 60, decay = 0.95, prune_norm = 3):

		self.window_size = window_size
		self.decay_rate = decay
		self.norm = prune_norm
		self.wstart = 0
		self.wend = window_size-1
		self.max_iset_size = 3
		self.inputfile = ipfile
		self.trie = Trie(decay)
		self._init_trans()

	'''
	def _init_trans(self): # THIS IS ONLY FOR ONLINE RETAIL
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

	def _get_code(self,iset):#returns a code for very set

		indices = list()
		for item in iset:
			indices.append(bisect.bisect_left(itemset, item))

		return indices

	def _get_iset(self,indices):

		iset = list()
		for index in indices:
			iset.append(itemset[index])

		return iset

	def process_window(self):
		global max_count, sum_freq
		trans_window = self.trans_list[self.wstart:self.wend+1] # extract the current window
		print ('Window length-'+str(len(trans_window))+' start - '+str(self.wstart)+' end- '+str(self.wend))
		trans_no = self.wstart
		for transaction in trans_window:
			unique_transaction=set(transaction)
			trans_no+=1
			if len(unique_transaction) > 120:
				continue
			if len(cur_list) > 1500000:
				print ('ALERT: Memory consumption high!')
				sys.exit(0)

			

	def _get_average(self):
		global sum_freq
		sum=pow((sum_freq/len(cur_list)),(1/self.norm))
		return sum



if __name__ == "__main__":

	start_time = time.time()
	''' Pruning done at the end of one window '''
	read_items()
	#print (itemset)
	#fis = FreqItemSet("trans_data.json", 90, 0.95, 2.5)
	fis = FreqItemSet("BMS/bms1_data", 90, 0.95, 2)
	count=0;
	while fis.wstart<(len(fis.trans_list)):
		print ('count of window - '+str(count))
		fis.process_window()
		while len(cur_list)>70000:
			temp=len(cur_list)
			fis.prune(fis._get_average(), 10)
			if temp==len(cur_list):
				break
		count+=1
		#if count%5==0:
		fis.show_topk()

	fis.show_topk()
	print("--- %s seconds ---" % (time.time() - start_time))
