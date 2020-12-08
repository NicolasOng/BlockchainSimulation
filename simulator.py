from multiprocessing import Process, Queue
import multiprocessing

import random

import node
from message import *
from utility import *

def main(myQueue, numNodes, bc_file):
	'''
	the thread that manages the nodes in the simulation.
	'''
	#1. create all the queues for the network simulation,
	nodeNetQueueList = list()
	contactNode = list()
	for i in range(numNodes):
		nodeNetQueueList.append(Queue())
		contactNode.append(Queue())
	printl("[SIM]: Created all queues.", 1)
	
	#2. create all the processes to run as nodes in the simulation,
	nodeList = list()
	for i in range(numNodes):
		neighbours_list = random.sample(nodeNetQueueList, int(numNodes/2))
		nodeList.append(Process(target=node.main, args=(nodeNetQueueList[i], True, neighbours_list, contactNode[i], "node-"+str(i), bc_file)))
	printl("[SIM]: Created all nodes.", 1)
	
	#3. start all the processes,
	for i in range(numNodes):
		nodeList[i].start()
	printl("[SIM]: Started all nodes.", 1)
	
	#4. wait for commands from above,
	while True:
		msg = myQueue.get()
		if (msg.header == "END"):
			printl("[SIM]: Recieved END.", 1)
			break
		elif (msg.header == "SAVE"):
			printl("[SIM]: Telling node #"+str(msg.data[0])+" to save its blockchain.", 0)
			contactNode[msg.data[0]].put(Message("SAVE", msg.data[1]))
	
	#5. send a message to each node to stop gracefully,
	printl("[SIM]: Sending END msg to all nodes.", 1)
	for i in range(numNodes):
		contactNode[i].put(Message("END", None))
	
	#6. join the processes,
	for i in range(numNodes):
		nodeList[i].join()
	
	#7. end,
	printl("[SIM]: Ending.", 1)

