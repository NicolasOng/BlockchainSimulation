from block import *
from mining import *
from blockchain import *

import random
import pickle
import matplotlib.pyplot as plt


#block module:
print("Block Module")
#create genesis block,
b0 = getGenesisBlock(8)
print(b0)
#try some nonces,
mineUntilFound(b0)
print("good nonce:", b0.nonce)
nonces = [1, 2, 3, 4]
for i in nonces:
	b0.setNonce(i)
	print("Genesis Block's hash w/ nonce=" + str(i) + ": " + b0.calcHash().hex())
	print("is block valid?", b0.isValid())
#try to and from string:
tempb = getGenesisBlock(9)
print(b0.toString())
tempb.fromString(b0.toString())
print(tempb.toString())
#create next block,
mineUntilFound(b0)
b1 = b0.next("1", 4)
print(b1)


#mining module:
print("Mining Module")
#mine b1 until a nonce is found.
found, tn = mineUntilFound(b1)
print("valid nonce found for b1 after " + str(tn) + " hashes.")
#try mining at different difficulties to see how it increases hashes.
if (True):
	t = 5
	avg_hashes = list()
	for i in range(15):
		dif = i + 1
		hashes = list()
		for j in range(t):
			nb = getGenesisBlock(dif)
			found, n = mineUntilFound(nb)
			hashes.append(n)
		avg_hashes.append(sum(hashes)/t)
	plt.plot(range(16)[1:], avg_hashes)
	plt.xlabel("Difficulty")
	plt.ylabel("Hashes")
	plt.title("Number of Hashes to Mine a Block Over Difficulty")
	plt.show()
#create more valid blocks
b1a = b0.next("2", 5)
mineUntilFound(b1a)
b2 = b1.next("3", 4)
mineUntilFound(b2)
b2a = b1a.next("2", 4)
mineUntilFound(b2a)

#blockchain module
print("Blockchain Module")
blocks = [b1, b1a, b2, b2a]
#create a blockchain and try giving the blocks to the blockchain in a random order.
#this is to simulate the randomness of a network.
bc = Blockchain(b0)
for i in range(3):
	print("Tree #"+str(i))
	bc = Blockchain(b0)
	print(bc)
	random.shuffle(blocks)
	for b in blocks:
		bc.newBlock(b)
		print(bc)
#get the deepest nodes of the tree:
dn = bc.getDeepestNodes()
print("deepest nodes:")
for n in dn:
	print(n[0], "at depth", n[1])
#get the deepest block for the current node to continue mining:
for i in range(4):
	b, s = bc.getDeepestBlock(str(i))
	print(i, b, s)
