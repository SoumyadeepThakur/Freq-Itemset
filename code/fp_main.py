import fp_growth
from fp_growth import find_frequent_itemsets
import json
#-------------------------------------------------------
def parse_file(path):
	'''Parse the json file and create a dict'''
	data = dict()
	with open(path,'r') as infile:
		data = json.load(infile)
	infile.close()
	print ('Total No of transactions: ',len(data))
	trans_list = list()
	for i in range(len(data)):
		trans_list.append(list(map(str,data[i]['Items'])))
	
	return trans_list
#----------------------------------------------------------
if __name__ == "__main__":
	transactions = parse_file('trans_data.json')
	result = []
	transac = transactions[0:20]
	minsup = int(input('Enter minimum support: '))
	for itemset,support in find_frequent_itemsets(transac, minsup, True): # 2nd parameter is the minimum support value.
		result.append((itemset,support))

	result = sorted(result, key=lambda i: i[0])
	for itemset, support in result:
		print (str(itemset) + ' ' + str(support))