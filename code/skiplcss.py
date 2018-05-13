import json
from itertools import combinations
import bisect
from collections import defaultdict
import numpy as np
import time
import sys
import random

cur_list = dict() # current items present in the frequent itemset
itemset = list() # map of item to its index (if required)
delta=0
cmin=0
k=100   # maximum size of the list, here put our limit
def read_items(): #list of all items

	global itemset
	with open ("items.txt","r") as infile:
		itemset = infile.readlines()
	for i in range(len(itemset)):
		itemset[i] = itemset[i].rstrip()

	itemset.sort()

#------------------------------------------------------------------------------------------------------------------
class FreqItemSet:

	def __init__(self, ipfile, window_size = 30):

		self.window_size = window_size
		self.wstart = 0
		self.wend = window_size-1
		self.max_iset_size = 3
		self.inputfile = ipfile
		self._init_trans()

		#add more

	def _init_trans(self):
		'''Parse the json file and create a dict'''
		data = dict()
		with open(self.inputfile,'r') as infile:
			data = json.load(infile)
		infile.close()
		print ('Total No of transactions: '+str(len(data)))
		trans_list = list()
		for i in range(len(data)):
			trans_list.append(list(map(str,data[i]['Items'])))

		self.trans_list = trans_list

	def _get_code(self,iset):#returns a code for very set

		indices = list()
		for item in iset:
			indices.append(bisect.bisect_left(itemset, item))

		#print(indices,"\n")
		indices = sorted(indices)
		code_str=str('')
		for i in indices:
			temp = str(i)
			code_str+=str(len(temp))
			code_str+=temp

		code_val = int(code_str)
		return code_val

	def _get_iset(self,code):  # returns the itemset from the code

		code_str = str(code)
		i=0
		indices = list()
		while i<len(code_str):
			digits = int(code_str[i:i+1])
			indices.append(int(code_str[i+1:i+1+digits]))
			i+=digits+1

		iset = list()
		for index in indices:
			iset.append(itemset[index])

		return iset

	def process_window(self):
		global cur_list,delta,delta,cmin,k
		trans_window = self.trans_list[self.wstart:self.wend+1] # extract the current window
		print ('Window length-'+str(len(trans_window))+' start - '+str(self.wstart)+' end- '+str(self.wend))
		trans_no = self.wstart
		for transaction in trans_window:
			unique_transaction=set(transaction)
			trans_no+=1
			trans_subset = list()
			if len(unique_transaction) > 120:
				continue
			for i in range(self.max_iset_size): # all possible subsets of max size max_iset_size of transaction set
				temp = list(combinations(unique_transaction, r=(i+1)))
				trans_subset.extend(temp)
				#print ('transaction size - '+str(len(unique_transaction))+' combination - '+str(len(trans_subset)))

			# update existing items in list
			r=0
			for iset in trans_subset:
				code = self._get_code(iset)

				if code in cur_list:

					cur_list[code] = cur_list[code]+1
					r+=1
					trans_subset.remove(iset)

			# update me and min_val from cur_list
			me=min_val=0
			if len(cur_list)<k:
				me=k-len(cur_list)
				min_val=0
			else:
				min_val=5000
				me=0
				for code,freq in cur_list.items():
					if min_val<freq:
						min_val=freq
						me=1
					elif min_val==freq:
						me+=1
				for code,freq in cur_list.items():
					if freq==min_val:    # deleting the minimal entries
						del cur_list[code]

			cs = 2**len(unique_transaction)-r-1

			if cs >=me:
				while len(trans_subset) > me:   # making list size equal to me
					temp=random.randint(0,len(trans_subset)-1)
					# print(str(temp)+' '+str(len(trans_subset)))
					trans_subset.pop(temp)

			for iset in trans_subset:
				code = self._get_code(iset)
				cur_list[code] = delta+1

			if me>cs:
				cmin=cmin
				delta=cmin
			elif me==cs:
				temp=delta
				delta=cmin
				cmin=temp+1
			else:
				cmin=delta+1
				delta=delta+1

		self.wstart += self.window_size
		self.wend += self.window_size
		print ('size of list - '+str(len(cur_list)))


	def prune(self, thresh):

		global cur_list

		remove = [icode for icode in cur_list if cur_list[icode][0] < thresh]
		for i in remove:
			del cur_list[i]

		#print ('size after pruning -'+str(len(cur_list)))


	def show_topk(self):

		'''
		import operator
		global cur_list

		sorted_list = sorted(cur_list.items(), key = operator.itemgetter(1), reverse = True)
		#sorted_list = sorted_list.reverse()
		r=10
		if r>len(cur_list):
			r=len(cur_list)
		for i in range(r):
			print (self._get_iset(sorted_list[i][0]),sorted_list[i][1],"\n")
	'''
		import operator
		global cur_list

		#temp = dict()
		#for iset in cur_list:
		#	temp[iset] = cur_list[iset][0]

		sorted_list = sorted(cur_list.items(), key = operator.itemgetter(1), reverse = True)
		#sorted_list = sorted_list.reverse()
		r=1
		ist=list()
		'''if r>len(cur_list):
			r=len(cur_list) '''
		suggest=list()
		sug_count = list()
		for i in range(len(sorted_list)):

			ist = self._get_iset(sorted_list[i][0])
			if len(ist) > 1:
				#print (self._get_iset(sorted_list[i][0]),sorted_list[i][1],"\n")
				suggest.append(self._get_iset(sorted_list[i][0]))
				sug_count.append(sorted_list[i][1])
				r += 1
				if r > 30: # get only top 20 non-single itemsets
					break


		#suggestions
		with open('lcss1.txt','a+') as gt_file:
			win_no = int(self.wend/self.window_size)
			gt_file.write("Window")
			gt_file.write("%s\n" % win_no)
			for item, count in list(zip(suggest,sug_count)):
				gt_file.write("%s - " % item)
				gt_file.write("%s\n" % count)

#------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":

	start_time = time.time()
	''' Pruning done at the end of one window '''
	read_items()
	#print (itemset)
	fis = FreqItemSet("trans_data.json")

	count=0;
	while fis.wstart<(len(fis.trans_list)):
		print ('count of window - '+str(count))
		fis.process_window()
		fis.show_topk()

	print("--- %s seconds ---" % (time.time() - start_time))
