import json
from itertools import combinations
import bisect
from collections import defaultdict
import numpy as np

cur_list = dict() # current items present in the frequent itemset
itemset = list()
#map of item to its index (if required)


def read_items(): #list of all items
	
	global itemset
	with open ("items.txt","r") as infile:
		itemset = infile.readlines()
	for i in range(len(itemset)):
		itemset[i] = itemset[i].rstrip()

	itemset.sort()
	
#------------------------------------------------------------------------------------------------------------------
class FreqItemSet:

	def __init__(self, ipfile, window_size = 20, decay = 0.95):

		self.window_size = window_size
		self.decay_rate = decay
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
		print ('Total No of transactions: ',len(data))
		trans_list = list()
		for i in range(len(data)):
			trans_list.append(list(map(str,data[i]['Items'])))
	
		self.trans_list = trans_list

	def _get_code(self,iset):

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

	def _get_iset(self,code):

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
		global cur_list
		trans_window = self.trans_list[self.wstart:self.wend+1] # extract the current window
		print(len(trans_window), self.wstart, self.wend)
		trans_no = self.wstart
		for transaction in trans_window:
			if len(transaction) > 120:
				continue
			trans_no+=1
			for i in range(self.max_iset_size): # all possible subsets of max size max_iset_size of transaction set 
				trans_subset = list(combinations(transaction, r=(i+1)))
				for iset in trans_subset:
					code = self._get_code(iset)
					#print (code, "----", iset, "\n")
					if code in cur_list:
						newc = cur_list[code][0]*pow(self.decay_rate,(trans_no-cur_list[code][1])) + 1
						cur_list[code] = list([newc, trans_no])
					else:
						if len(cur_list) >= 500000:
							raise ValueError("Out of memory")
						cur_list[code] = list([1,trans_no])

			

		#for x in cur_list:
		#	print (x,"---", cur_list[x],"\n")
		for iset in cur_list:
			cur_list[iset][0] = cur_list[iset][0]*pow(self.decay_rate,(trans_no-cur_list[code][1]-1))

		self.wstart += self.window_size
		self.wend += self.window_size
		print(len(cur_list))


	def prune(self, thresh):
		
		global cur_list

		remove = [icode for icode in cur_list if cur_list[icode][0] < thresh]
		for i in remove:
			del cur_list[i]

		print(len(cur_list))

	def show_topk(self):

		import operator
		global cur_list

		temp = dict()
		for iset in cur_list:
			temp[iset] = cur_list[iset][0]

		sorted_list = sorted(temp.items(), key = operator.itemgetter(1), reverse = True)
		#sorted_list = sorted_list.reverse()
		for i in range(10):
			print (self._get_iset(sorted_list[i][0]),sorted_list[i][1],"\n")



#------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":

	''' Pruning done at the end of one window '''
	read_items()
	#print (itemset)
	fis = FreqItemSet("trans_data.json")
	fis.process_window()
	fis.prune(1.5)
	fis.process_window()
	fis.prune(2)
	fis.process_window()
	fis.prune(3)
	'''
	fis.process_window()
	fis.prune(5)
	fis.process_window()
	fis.prune(8)
	fis.process_window()
	fis.prune(10)
	fis.process_window()
	fis.prune(12)
	fis.process_window()
	fis.prune(15)
	fis.process_window()
	fis.prune(15)
	fis.process_window()
	fis.prune(18)
	fis.process_window()
	fis.prune(20)
	fis.process_window()
	fis.prune(25)
	'''
	fis.show_topk()

