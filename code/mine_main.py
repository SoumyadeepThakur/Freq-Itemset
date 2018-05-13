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
sum_freq=0.0
max_count=1.0

def read_items(): #list of all items

	global itemset
	with open ("BMS/bms1_items","r") as infile:
		itemset = infile.readlines()
	for i in range(len(itemset)):
		itemset[i] = itemset[i].rstrip()

	itemset.sort()

#------------------------------------------------------------------------------------------------------------------
class FreqItemSet:

	def __init__(self, ipfile, window_size = 60, decay = 0.95, prune_norm = 3):

		self.window_size = window_size
		self.decay_rate = decay
		self.norm = prune_norm
		self.wstart = 0
		self.wend = window_size-1
		self.max_iset_size = 3
		self.inputfile = ipfile
		self._init_trans()

		#add more

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
			#if(len(cur_list)>500000):
				#print 'within -',
			#	self.prune(self._get_average(), 10)
			#temp=list()
			#temp2=list()
			if len(cur_list) > 1500000:
				print ('ALERT: Memory consumption high!')
				sys.exit(0)
			for i in range(self.max_iset_size): # all possible subsets of max size max_iset_size of transaction set
				trans_subset = list(combinations(unique_transaction, r=(i+1)))
				#print ('transaction size - '+str(len(unique_transaction))+' combination - '+str(len(trans_subset)))

				for iset in trans_subset:
					code = self._get_code(iset)

					#print (code, "----", iset, "\n")
					if code in cur_list:
						#decay=max(self.decay_rate,(cur_list[code][0])/max_count);
						#dynamic decay, low decay for frequent items
						decay=self.decay_rate;
						sum_freq=sum_freq-pow(cur_list[code][0],self.norm)
						newc = cur_list[code][0]*pow(decay,(trans_no-cur_list[code][1]-1)) + 1
						if newc>max_count:
							max_count=newc
						cur_list[code] = list([newc, trans_no])
						sum_freq=sum_freq+pow(cur_list[code][0],self.norm)
					else:
						cur_list[code] = list([1,trans_no])
						sum_freq=sum_freq+1
						#if len(cur_list)>150000:
							#cur_list[-1][-1]=-1


		#for x in cur_list:
		#	print (x,"---", cur_list[x],"\n")
		for iset in cur_list: #updates all at window end
			sum_freq=sum_freq-pow(cur_list[iset][0],self.norm)
			cur_list[iset][0] = cur_list[iset][0]*pow(self.decay_rate,(trans_no-cur_list[iset][1]-1))
			cur_list[iset][1] = trans_no
			sum_freq=sum_freq+pow(cur_list[iset][0],self.norm)

		while (len(cur_list) > 70000): 
			self.prune(self._get_average(), 10)

		#make suggestions based on itemsets
		#self._suggestions()
		self.wstart += self.window_size
		self.wend += self.window_size
		print ('size of list - '+str(len(cur_list)))





	def prune(self, thresh, max_dict):

		global cur_list,sum_freq

		removelist = [icode for icode in cur_list if cur_list[icode][0] < thresh]
		random.shuffle(removelist)
		diff = len(cur_list) - max_dict
		for ii in removelist:
			#ii = random.choice(removelist)
			#removelist.remove(ii)
			sum_freq=sum_freq-pow(cur_list[ii][0],self.norm)
			del cur_list[ii]
			if len(cur_list) <= max_dict:
				break



		#print ('size after pruning -'+str(len(cur_list)))

	def _get_average(self):
		global sum_freq
		sum=pow((sum_freq/len(cur_list)),(1/self.norm))
		return sum

	def show_topk(self):

		import operator
		global cur_list

		temp = dict()
		for iset in cur_list:
			temp[iset] = cur_list[iset][0]

		sorted_list = sorted(temp.items(), key = operator.itemgetter(1), reverse = True)
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
		with open('BMS/result_bms1_90_2','a+') as gt_file:
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
