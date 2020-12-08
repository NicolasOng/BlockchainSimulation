from multiprocessing import Process, Queue
import multiprocessing

import pickle

from socket import *

from block import *
from blockchain import *
from mining import *
from message import *
from utility import *

MINE_TO = 1000

def main(fromNet, inSimulator, neighbours_list, myQueue, name, bc_file):
	'''
	to start the program.
	'''
	printl("[NODE]: Started Node.", 1)
	#change the interface if in a sim,
	if (inSimulator):
		import sim_interface as interfacel
	else:
		import net_interface as interfacel
	global interface
	interface = interfacel
	printl("[NODE]: Using " + interface.version, 1)
	#create the Qs to send messages to the threads,
	toMine, toComms = Queue(), Queue()
	#create and start the mine process,
	mine_proc = Process(target=mine_thread, args=(toMine, toComms))
	mine_proc.start()
	#create and start the comms process,
	comms_proc = Process(target=comms_thread, args=(toComms, toMine, fromNet, name, bc_file, neighbours_list))
	comms_proc.start()
	printl("[NODE]: Started Communications and Mine.", 1)
	
	#wait for commands from above,
	while True:
		msg = myQueue.get()
		if (msg.header == "END"):
			printl("[NODE]: Recieved END.", 1)
			break
		elif (msg.header == "SAVE"):
			printl("[NODE]: Telling COMMS to save its blockchain.", 1)
			toComms.put(Message("SAVE", msg.data))
	
	#send a message to both processes to stop gracefully,
	printl("[NODE]: Sending END msg to children.", 1)
	toMine.put(Message("END", None))
	toComms.put(Message("END", None))
	#join the processes,
	mine_proc.join()
	comms_proc.join()
	printl("[NODE]: Ending.", 1)

def comms_thread(myQueue, toMine, fromNet, name, bc_file, neighbours_list):
	'''
	this thread waits for new blocks from the network/mine thread.
	if it gets one, it adds it to the local blockchain,
	then informs the mining thread. (if the new mining block is different).
	it also sends blocks to the network.
	'''
	printl("[COMMS]: Communications thread started.", 1)
	#initilize the thread:
	#deal with the name,
	if (name is None):
		name = gethostname()
	printl("[COMMS]: Name is " + name + ".", 1)
	#create or load a blockchain:
	mb = pickle.load(open("genblk.pkl", 'rb'))
	bc = Blockchain(mb)
	e = False
	if (bc_file is not None):
		try:
			bc = pickle.load(open(bc_file, 'rb'))
			printl("[COMMS]: Loaded blockchain from file.", 1)
		except:
			e = True
	if (bc_file is None or e):
		printl("[COMMS]: Started new blockchain.", 1)
	#get and send a block to the mine thread,
	mb, s = bc.getDeepestBlock(name)
	mb = mb.next(name, 8)
	toMine.put(Message("Block", mb))
	printl("[COMMS]: Sent first block to mine.", 1)
	
	#start the thread.
	while True:
		#1. check for messages from the main thread or the mine thread:
		if (not myQueue.empty()):
			#handle them:
			msg = myQueue.get()
			if (msg.header == "END"):
				printl("[COMMS]: Recieved END.", 1)
				break
			elif (msg.header == "SAVE"):
				pickle.dump(bc, open(msg.data, 'wb'))
				printl("[COMMS]: Saved blockchain.", 1)
			elif (msg.header == "Block"):
				printl("[COMMS]: Receieved a mined block from the mine.", 2)
				#add it to the local blockchain,
				bc.newBlock(msg.data)
				#send a new block to the mine thread,
				mb, s = bc.getDeepestBlock(name)
				mb = mb.next(name, bc.getDifficulty(name))
				toMine.put(Message("Block", mb))
				#send it over the network to this node's connections.
				interface.putAll(neighbours_list, msg.data.toString())
				printl("[COMMS]: Put it in blockchain, sent to neighboring nodes, and sent mine a new block.", 2)
		
		#2. After handling them, wait for network blockstrings with a timeout:
		printl("[COMMS]: Checking for blocks from the network.", 2)
		blockstring, tod = interface.get(fromNet)
		#if a blockstring was recieved:
		if (not tod):
			printl("[COMMS]: Receieved a block from the network.", 2)
			nb = getGenesisBlock(10)
			try:
				#1. try to create a block object from the string,
				nb.fromString(blockstring)
				#2. check if it is valid,
				if (not nb.isValid()):
					printl("[COMMS]: ERROR: Block recieved from network is invalid.", 2)
					raise Exception('Block from network is invalid.')
				#3. check if our blockchain already has it,
				if (bc.blockExists(nb)):
					printl("[COMMS]: ERROR: Block recieved from network already exists in the local blockchain.", 2)
					raise Exception("Block recieved from network already exists.")
				#4. add it to the local blockchain,
				bc.newBlock(nb)
				#5. get the new deepest block,
				mb, s = bc.getDeepestBlock(name)
				mb = mb.next(name, bc.getDifficulty(name))
				#6. send it to the mine,
				toMine.put(Message("Block", mb))
				printl("[COMMS]: Updated blockchain and sent a new block to the Mine.", 2)
				interface.putAll(neighbours_list, blockstring)
				printl("[COMMS]: Propagated the new block to neighbour nodes.", 2)
			except:
				printl("[COMMS] Block recieved from network caused an error.", 2)
		else:
			printl("[COMMS]: Nothing from the network.", 2)
	printl("[COMMS]: Ending", 1)

def mine_thread(myQueue, toComms):
	'''
	this thread mines the given block
	until either one is found,
	or a block was received.
	if found, tell recv thread, and continue mining.
	'''
	printl("[MINE]: Mine thread started.", 1)
	mb = None
	found = None
	#initialize thread:
	while True:
		#check for a new message:
		if (not myQueue.empty()):
			msg = myQueue.get()
			#handle the message:
			if (msg.header == "END"):
				printl("[MINE]: Recieved END.", 1)
				break
			elif (msg.header == "Block"):
				printl("[MINE]: Recieved block to mine from COMMS.", 2)
				mb = msg.data
		#mine:
		if (mb is not None):
			printl("[MINE]: Mining attempt.", 3)
			found, numhash = mine(mb, MINE_TO)
		if (found):
			found = False
			toComms.put(Message("Block", mb))
			mb = None
			printl("[MINE]: Successfully mined a block. Sent to COMMS.", 2)
			
	printl("[MINE]: Ending.", 1)

