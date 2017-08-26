import json
from itertools import combinations
import bisect
from collections import defaultdict
import numpy as np
import time
import sys

cur_list = dict() # current items present in the frequent itemset
itemset = list() # map of item to its index (if required)
sum_freq=0.0
max_count=1.0

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
		global cur_list,max_count,sum_freq
		trans_window = self.trans_list[self.wstart:self.wend+1] # extract the current window
		print ('Window length-'+str(len(trans_window))+' start - '+str(self.wstart)+' end- '+str(self.wend))
		trans_no = self.wstart
		for transaction in trans_window:
			unique_transaction=set(transaction)
			trans_no+=1
			if len(unique_transaction) > 120:
				continue
			if(len(cur_list)>5000):
				#print 'within -',
				self.prune(self._get_average())
			#temp=list()
			#temp2=list()
			for i in range(self.max_iset_size): # all possible subsets of max size max_iset_size of transaction set
				trans_subset = list(combinations(unique_transaction, r=(i+1)))
				#print ('transaction size - '+str(len(unique_transaction))+' combination - '+str(len(trans_subset)))

				for iset in trans_subset:
					code = self._get_code(iset)
					'''
					if code in temp:
						print '------------error---------'
						print ('code - '+str(code)+' iset - '+str(iset))
						print ('clash with - '+str(temp2[temp.index(code)]))
						print ('code of that is - '+str(self._get_code(temp2[temp.index(code)])))
						for j in transaction:
							print(str(j))
						sys.exit()
					else:
						temp.append(code)
						temp2.append(iset)
					'''
					#print (code, "----", iset, "\n")
					if code in cur_list:
						#decay=max(self.decay_rate,(cur_list[code][0])/max_count);
						#dynamic decay, low decay for frequent items
						decay=self.decay_rate;
						sum_freq=sum_freq-pow(cur_list[code][0],3)
						newc = cur_list[code][0]*pow(decay,(trans_no-cur_list[code][1]-1)) + 1
						if newc>max_count:
							max_count=newc
						cur_list[code] = list([newc, trans_no])
						sum_freq=sum_freq+pow(cur_list[code][0],3)
					else:
						cur_list[code] = list([1,trans_no])
						sum_freq=sum_freq+1
						#if len(cur_list)>150000:
							#cur_list[-1][-1]=-1


		#for x in cur_list:
		#	print (x,"---", cur_list[x],"\n")
		for iset in cur_list: #updates all at window end
			sum_freq=sum_freq-pow(cur_list[iset][0],3)
			cur_list[iset][0] = cur_list[iset][0]*pow(self.decay_rate,(trans_no-cur_list[iset][1]-1))
			cur_list[iset][1] = trans_no
			sum_freq=sum_freq+pow(cur_list[iset][0],3)

		self.wstart += self.window_size
		self.wend += self.window_size
		print ('size of list - '+str(len(cur_list)))


	def prune(self, thresh):

		global cur_list,sum_freq

		remove = [icode for icode in cur_list if cur_list[icode][0] < thresh]
		for i in remove:
			sum_freq=sum_freq-pow(cur_list[i][0],3)
			del cur_list[i]

		#print ('size after pruning -'+str(len(cur_list)))

	def _get_average(self):
		global sum_freq
		'''
		global cur_list
		sum = 0.0
		count=1;

		for i in cur_list:
			#if cur_list[i][0]>.75:
			#	count+=1;
			sum+=pow(cur_list[i][0],3)
		#sum/=((count+len(cur_list))/2.0)
		sum/=len(cur_list)
		sum=pow(sum,1/3.0)
		'''
		sum=pow((sum_freq/len(cur_list)),1/3.0)
		return sum


	def show_topk(self):

		import operator
		global cur_list

		temp = dict()
		for iset in cur_list:
			temp[iset] = cur_list[iset][0]

		sorted_list = sorted(temp.items(), key = operator.itemgetter(1), reverse = True)
		#sorted_list = sorted_list.reverse()
		r=10
		if r>len(cur_list):
			r=len(cur_list)
		for i in range(r):
			print (self._get_iset(sorted_list[i][0]),sorted_list[i][1],"\n")


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
		while len(cur_list)>5000:
			temp=len(cur_list)
			fis.prune(fis._get_average())
			if temp==len(cur_list):
				break
		count+=1
		if count%25==0:
			fis.show_topk()

	fis.show_topk()
	print("--- %s seconds ---" % (time.time() - start_time))
	'''
	fis.process_window()
	fis.prune(1.5)
	fis.process_window()
	p=fis._get_average()
	fis.prune(p)
	fis.process_window()
	fis.prune(2)
	fis.process_window()
	fis.prune(2)
	fis.show_topk()'''
