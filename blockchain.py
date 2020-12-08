class BlockchainNode:
	def __init__(self, parent, block):
		'''
		initializes a new blockchain node.
		this class is used to construct the blockchain tree.
		we need a tree, as there will be branching nodes at times.
		'''
		self.parent = parent
		self.block = block
		self.children = []
	
	def __str__(self):
		return "("+self.block.__str__()+")"
	
	def _rstr(self, level=0):
		ret = "  "*level+self.__str__()+"\n"
		for child in self.children:
			ret += child._rstr(level+1)
		return ret
	
	def newChild(self, block):
		'''
		appends a new node with the given block as a child to the node.
		'''
		newNode = BlockchainNode(self, block)
		self.children.append(newNode)
		return self.children[-1]

class Blockchain:
	def __init__(self, genesisBlock):
		'''
		initializes the blockchain.
		needs the genesis block.
		'''
		self.orphanBlocks = list()
		self.root = BlockchainNode(None, genesisBlock)
	
	def __str__(self):
		s = "\norphans:\n"
		for ob in self.orphanBlocks:
			s += "\t"+ob.__str__()+"\n"
		s += "tree:\n"
		s += self.root._rstr()
		return s
	
	def newBlock(self, block):
		'''
		called when a new block is found or recieved.
		this function searches the blockchain for its parent.
		if not found: the block is orphaned.
		if found: checks all orphaned blocks to see if it is their parent.
		note: due to how this is implemented,
		valid nodes have hashes with 0s at the end AND must be unique.
		2^256 possible hashes, so this shouldn't be an issue for now.
		'''
		#use dfs to find a valid parent node,
		validParents = list()
		dfs(set(), self.root, 0, equalHashGen, [block.prevHash, block.generation], validParents)
		#if found,
		if (len(validParents) > 0):
			#create a (parent node, child block) tuple, and add it to a list,
			newBlocks = [(validParents[0], block)]
			#while that list is not empty,
			while newBlocks:
				#add the last pair to the blockchain,
				newBlock = newBlocks.pop()
				node = newBlock[0].newChild(newBlock[1])
				#add un orphaned blocks to the list of new blocks,
				unOrphanedBlocks = list()
				for i, ob in enumerate(self.orphanBlocks):
					if (ob.prevHash == newBlock[1].hash):
						newBlocks.append((node, ob))
						unOrphanedBlocks.append(i)
				#and remove them from the orphaned block list.
				for index in reversed(unOrphanedBlocks):
					self.orphanBlocks.pop(index)
		#if not found,
		else:
			#add the block to the list of orphaned blocks.
			self.orphanBlocks.append(block)
	
	def getDeepestNodes(self):
		'''
		gets the nodes deepest in the tree.
		if there's only one, that leaf and its parents
		represent the current blockchain.
		returns [(node, depth), ...]
		'''
		deepestBlocks = list()
		dfs(set(), self.root, 0, deepest, None, deepestBlocks)
		return deepestBlocks
	
	def getDeepestNode(self, node_id):
		'''
		gets the deepest node favoured by the given node id.
		returns node, score
		'''
		#get the deepest nodes,
		candidates = self.getDeepestNodes()
		bestScore = 0
		bestNode = candidates[0][0]
		#for each node,
		for c in candidates:
			curScore = 0
			curNode = c[0]
			#traverse it and its parents to the root,
			while curNode is not None:
				block = curNode.block
				if (block.data == node_id):
					#to find its "score"
					curScore += 1
				curNode = curNode.parent
			#get the one with the best score,
			if (curScore > bestScore):
				bestScore = curScore
				bestNode = c[0]
		#and return it.
		return bestNode, bestScore
	
	def getDeepestBlock(self, node_id):
		'''
		gets the deepest block favoured by the given node id.
		returns block, score
		'''
		bestNode, bestScore = self.getDeepestNode(node_id)
		return bestNode.block, bestScore
	
	def getDifficulty(self, node_id):
		'''
		gets the difficulty for the next block to mine.
		based on the deepest block in the blockchain,
		and on the goal of generating one block every 10s.
		'''
		#get the deepest node and its 2 latest parents,
		dn, s = self.getDeepestNode(node_id)
		dnp = dn.parent
		if (dnp is None):
			return 20
		dnpp = dnp.parent
		if (dnpp is None):
			return 20
		#find the time it took to mine it and its parent,
		ttmdn = dn.block.time - dnp.block.time
		ttmdnp = dnp.block.time - dnpp.block.time
		#find the new difficulty,
		dif = dn.block.difficulty
		if (ttmdn > 10 and ttmdnp > 10):
			dif -= 1
		elif (ttmdn < 10 and ttmdnp < 10):
			dif += 1
		return dif
	
	def blockExists(self, block):
		'''
		returns True if the given block already exists in the blockchain.
		returns False otherwise.
		'''
		identicalBlocks = list()
		dfs(set(), self.root, 0, sameBlock, [block.toString()], identicalBlocks)
		return not (len(identicalBlocks) == 0)

def equalHashGen(node, results, depth, parameters):
	'''
	helper function for dfs to get the node with a block with an equal hash.
	'''
	block = node.block
	if (block.hash == parameters[0] and block.generation == parameters[1] - 1):
		results.append(node)

def deepest(node, results, depth, parameters):
	'''
	helper function for dfs to get the deepest nodes.
	'''
	block = node.block
	if (len(results) > 0):
		curDepth = results[0][1]
		if (depth == curDepth):
			results.append((node, depth))
		elif (depth > curDepth):
			results.clear()
			results.append((node, depth))
	else:
		results.append((node, depth))

def sameBlock(node, results, depth, parameters):
	'''
	helper function for dfs to get nodes with blocks identical to the given blockstring.
	'''
	blockstring = parameters[0]
	if (blockstring == node.block.toString()):
		results.append(node)

def dfs(visited, node, depth, function, parameters, results):
	'''
	depth-first search.
	returns a list of nodes based on the function.
	'''
	if node not in visited:
		function(node, results, depth, parameters)
		visited.add(node)
		for child in node.children:
			dfs(visited, child, depth + 1, function, parameters, results)

