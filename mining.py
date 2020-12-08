import secrets
import sys

def mine(block, n):
	'''
	generates n random nonces,
	and checks if they result in a valid block.
	returns true if found.
	'''
	for i in range(n):
		nonce = secrets.randbelow(sys.maxsize)
		block.setNonce(nonce)
		if (block.isValid()):
			return True, i
	return False, -1

def mineUntilFound(block):
	'''
	similar to above, but until found.
	'''
	n = 0
	while True:
		nonce = secrets.randbelow(sys.maxsize)
		block.setNonce(nonce)
		n += 1
		if (block.isValid()):
			return True, n
