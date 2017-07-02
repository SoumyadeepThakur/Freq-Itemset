import fp_growth
from fp_growth import find_frequent_itemsets
import json

def parse_file(path):
	'''Parse the json file and create a dict'''
	data = dict()
	with open(path,'r') as infile:
		data = json.load(infile)
	infile.close()
	#print(list(map(str,data[0]['Items'])))
	trans_list = list()
	for i in range(1000):
		trans_list.append(list(map(str,data[i]['Items'])))

	return trans_list
	#print(trans_list)

if __name__ == "__main__":
	transactions = parse_file('trans_data.json')
	
	result = []
	for itemset,support in find_frequent_itemsets(transactions, 20, True):
		result.append((itemset,support))

	result = sorted(result, key=lambda i: i[0])
	for itemset, support in result:
		print (str(itemset) + ' ' + str(support))