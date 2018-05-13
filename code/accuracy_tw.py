import sys

def measure_accuracy(ground, actual, skip):

	ground_data = list()
	temp = list()
	win_no = 0
	with open(ground, 'r') as ground_file:
		#if win_no
		add_flag = True
		for line in ground_file:
			if line[0:6] == "Window":
				win_no = (win_no+1) % skip
				if win_no % skip > 0:
					add_flag = False 
					continue
				else: add_flag = True
				ground_data.append(temp)
				temp = list()
			else:
				if add_flag:
					line = line.split('-')[0]
					line = line.strip(" ")
					temp.append(line)

	win_no = 0
	temp = list()
	sum1 = 0
	try:
		with open(actual, 'r') as actual_file:
			for line in actual_file:
				if line[0:6] == "Window":
					if win_no != 0:
						sground = set(ground_data[win_no])
						sactual = set(temp[0:30])
						inter=0
						for x1 in sactual:
							for x2 in sground:
								if x1 in x2: inter+=1
						#inter = sground.intersection(sactual)
						#print(inter, len(inter), '\n\n')
						percent = 100 * inter/30
						sum1 += percent
						print (win_no, '---', percent, '\n')
						temp = list()

					win_no += 1


				else:
					line = line.split('-')[0]
					line = line.strip(" ")
					temp.append(line)

	except IndexError as ie:
		print(ie)
		sum1 = sum1/win_no
		print(sum1)

	else: pass

	sum1 = sum1/win_no
	print(sum1)


	#with open(actual, 'r') as actual_file:
	#	actual_list = actual_file.readlines()

	#print (ground_list)



#measure_accuracy() 
	
if __name__ == '__main__':
	#measure_accuracy('BMS/ground2_bms1.txt', 'BMS/tw1_bms1_100.txt', 1)
	measure_accuracy('ground1.txt', 'tw4.txt', 1)