import gc, sys

class TrieNode(object):

	def __init__(self, last=0, count=-1, leaf=False):

		self._leaf = leaf
		self._prefix = list()
		self._count = count
		self._last = last
		self._nodes = 0
		self._children = dict() # change here


class Trie(object):

	def __init__(self, decay=0.95):
		self._root = TrieNode(last=0, count=-1, leaf=True)
		self._decay = decay

	def addElem(self, elem, time):
		self._add(self._root, elem, time)

	def find(self, elem):
		self._find(self._root, elem)

	def pruneApriori(self, thresh):
		self._pruneApriori(self._root, thresh)

	def decayAll(self, time):
		self._decayAll(self._root, time)

	def display(self):
		self._display(self._root)

	def _add(self, vertex, newElem, time):
		#if newElem == None or newElem == []:
		if vertex._count == -1:
			vertex._count = 1
		else: vertex._count = vertex._count*pow(self._decay, (time - vertex._last - 1)) + 1
		vertex._last = time
		#vertex._leaf = True 

		if newElem != [] and newElem != None:
			first = newElem[0]
			if first not in vertex._children:
				vertex._children[first] = TrieNode(last=time)
				vertex._children[first]._prefix = vertex._prefix + [first]

			nextElem = newElem[1:len(newElem)]
			nextChild = vertex._children[first]
			self._add(nextChild, nextElem, time)

	def _find(self, vertex, newElem):
		if (newElem == None or newElem == []):
			if vertex._count >= 0: print('found ',vertex._count)
			else: print('not found')


		else:
			first = newElem[0]
			if first not in vertex._children:
				print('not found')
				return
			nextElem = newElem[1:len(newElem)]
			nextChild = vertex._children[first]
			self._find(nextChild, nextElem)

	def _pruneApriori(self, vertex, thresh):		
		#print ('Prefix: ', vertex._prefix, ' Count: ', vertex._count)
		if vertex._count < thresh: # all children of this are to be pruned
			print ('Pruning')
			vertex = None
			del vertex # delete the entire subtree
			return False

		else:
			for next in list(vertex._children):
				if next != None:
					isPresent = self._pruneApriori(vertex._children[next], thresh)
					if isPresent == False: # children has become empty
						vertex._children[next] = None
						del vertex._children[next]

			return True

	def _decayAll(self, vertex, time):
		#print ('Prefix: ', vertex._prefix, ' Count: ', vertex._count)
		#if vertex == None: return
		vertex._count = vertex._count*pow(self._decay, (time - vertex._last - 1))
		vertex._last = time
		for next in list(vertex._children):
			self._decayAll(vertex._children[next], time)

	def _display(self, vertex):
		print ('Prefix: ', vertex._prefix, ' Count: ', vertex._count)
		for next in list(vertex._children):
			self._display(vertex._children[next])



def main():
	trie = Trie(decay = 0.95)
	trie.addElem([1,2,3],1)
	trie.addElem([1,3,6],1)
	trie.addElem([1,3,6,7],1)
	trie.addElem([1,2],1)
	trie.addElem([1,2],2)
	trie.addElem([1,2],2)
	trie.addElem([1,2,4,6],3)
	trie.addElem([1,2,3,4],3)
	print("--------------------------------------------\nTrie after all inserttions:\n--------------------------------------------")
	trie.display()
	trie.decayAll(10)
	print("--------------------------------------------\nTrie after all decay:\n--------------------------------------------")
	trie.display()
	trie.pruneApriori(2)
	print("--------------------------------------------\nTrie after pruning:\n--------------------------------------------")
	trie.display()
	trie.find([1,2])
	trie.find([1,3,6])
	trie.find([1,3,6,7])
	trie.find([1])
	trie.find([1,2,4,6])

if __name__ == "__main__":
	main()

