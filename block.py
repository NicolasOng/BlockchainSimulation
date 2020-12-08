import hashlib
import time
import pickle

from mining import *

class Block:
	def __init__(self, prevHash, generation, difficulty, data):
		'''
		creates and returns a new block.
		'''
		self.prevHash = prevHash
		self.generation = generation
		self.difficulty = difficulty
		self.data = data
		self.time = time.time()
		self.setNonce(0)
	
	def __str__(self):
		return "Block: gen="+str(self.generation)+", dif="+str(self.difficulty)+", mined by "+self.data
	
	def next(self, data, difficulty):
		'''
		creates and returns a block following the current block,
		with the given parameters.
		'''
		return Block(self.hash, self.generation + 1, difficulty, data)
	
	def calcHash(self):
		'''
		calculates and returns the current block's hash,
		with its current nonce.
		does this by combining all the block's information.
		'''
		strar = [self.prevHash.hex(),
				str(self.generation),
				str(self.difficulty),
				self.data,
				str(self.time),
				str(self.nonce)]
		toHash = ":".join(strar)
		return hashlib.sha256(toHash.encode()).digest()
	
	def setNonce(self, nonce):
		'''
		sets the nonce of the block,
		and updates the hash.
		'''
		self.time = time.time()
		self.nonce = nonce
		self.hash = self.calcHash()
		
	def isValid(self):
		'''
		returns if the block is valid,
		by checking the hash and difficulty.
		this is the "validation protocol".
		'''
		binHash = format(int(self.hash.hex(), 16), '0>42b')
		return binHash[-self.difficulty:]=="0"*self.difficulty
	
	def toString(self):
		'''
		encodes to string.
		'''
		strar = [self.prevHash.hex(),
				self.hash.hex(),
				str(self.generation),
				str(self.difficulty),
				self.data,
				str(self.time),
				str(self.nonce)]
		return ":".join(strar)
	
	def fromString(self, string):
		'''
		decodes from string.
		assumes no : in the data
		'''
		e = string.split(":")
		self.prevHash = bytes.fromhex(e[0])
		self.hash = bytes.fromhex(e[1])
		self.generation = int(e[2])
		self.difficulty = int(e[3])
		self.data = e[4]
		self.time = float(e[5])
		self.nonce = int(e[6])
		

def getGenesisBlock(difficulty):
	'''
	creates a genesis block with the specified difficulty.
	note that the block's nonce still has to be mined.
	difficulty: (0, 256]
	'''
	return Block(bytes(32), 0, difficulty, "0")

def createGenesisBlockFile():
	b0 = getGenesisBlock(20)
	mineUntilFound(b0)
	pickle.dump(b0, open("genblk.pkl", 'wb'))

