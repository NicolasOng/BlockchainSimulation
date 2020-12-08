version = "simulator interface"
from multiprocessing import Process, Queue
import multiprocessing

import time

def get(serverQueue):
	'''
	gets a blockstring from the given Queue.
	'''
	was_empty = True
	blockstring = None
	if (not serverQueue.empty()):
		was_empty = False
		blockstring = serverQueue.get()
	time.sleep(1)
	return blockstring, was_empty

def putAll(neighbour_list, bs):
	'''
	sends a blockstring to the queues in the list.
	'''
	time.sleep(1)
	for n in neighbour_list:
		n.put(bs)
