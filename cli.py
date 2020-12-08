help_msg = '''[CLI]: 

start_node [IP=localhost] [port=3000] [conns=conns1.txt] [blockchain=None] [name=hostname]
	- starts a node connected to the network.
	- eg: start_node IP=192.356.234.112 port=4532
	- can specify the node's IP, port, connection list, blockchain file, and name
	
start_simulation [num_nodes=5] [blockchain=None]
	- starts a simulation of many nodes on a network, with the given parameters.

save [node=0] [file=bc.pkl]
	- saves the node's current blockchain.

end
	- ends the current node/simulation.

read_block [file=genblk.pkl]
	- reads the block in the given file and prints it to screen.

read_blockchain [file=exbc.pkl]
	- reads the blockchain in the given file and prints it to screen.

help
	-prints this message.
'''

from multiprocessing import Process, Queue
import multiprocessing

from socket import *

import node
import simulator
from message import *
from utility import *
from block import *

#current state of the program
STATE = "NONE"

#the queue/process of the current node, if in NODE state
node_q = None
node_p = None

#the queue/process of the current simulation, if in SIM state
sim_q = None
sim_p = None

def get_param(params, param):
	if (param in params):
		return params[param]
	return None

def help(params):
	printl(help_msg, 0)

def start_node(params):
	global STATE
	global node_q
	global node_p
	if (STATE == "NONE"):
		STATE = "NODE"
		#get params,
		ip = get_param(params, "IP")
		port = get_param(params, "port")
		conn_file = get_param(params, "conns")
		bc_file = get_param(params, "blockchain")
		name = get_param(params, "name")
		#convert conns file to neighborlist,
		neighbour_list = list()
		if (conn_file is None):
			conn_file = "conns1.txt"
		file1 = open(conn_file, 'r') 
		Lines = file1.readlines()
		for line in Lines:
			line = line.split(":")
			tempip = line[1]
			if (tempip == "localhost"):
				tempip = gethostname()
			tempport = int(line[2])
			neighbour_list.append((tempip, tempport))
		#convert ip/port to a socket,
		tofromNet = None
		#get the node's ip (for non-sim)
		if (ip == None or ip == "localhost"):
			ip = gethostname()
		#get the node's port (non-sim)
		if (port == None):
			port = 3000
		else:
			port = int(port)
		fromNet = socket(AF_INET, SOCK_STREAM)
		fromNet.settimeout(1)
		fromNet.bind((ip, port))
		fromNet.listen(5)
		node_q = Queue()
		node_p = Process(target=node.main, args=(fromNet, False, neighbour_list, node_q, name, bc_file))
		node_p.start()
		printl("[CLI]: Started the node.", 0)
	else:
		printl("[CLI]: Looks like something has already started", 0)

def start_simulation(params):
	global STATE
	global sim_q
	global sim_p
	if (STATE == "NONE"):
		STATE = "SIM"
		#get params,
		num_nodes = get_param(params, "num_nodes")
		bc_file = get_param(params, "blockchain")
		try:
			num_nodes = int(num_nodes)
		except:
			num_nodes = 3
		sim_q = Queue()
		sim_p = Process(target=simulator.main, args=(sim_q, num_nodes, bc_file))
		sim_p.start()
		printl("[CLI]: Started the simulation.", 0)
	else:
		printl("[CLI]: Looks like something has already started", 0)

def save_node(params):
	global STATE
	num = get_param(params, "node")
	fn = get_param(params, "file")
	if (num is None):
		num = 0
	if (fn is None):
		fn = "bc.pkl"
	if (STATE == "NODE"):
		global node_q
		global node_p
		node_q.put(Message("SAVE", fn))
		printl("[CLI]: Saved the node's blockchain to "+fn+".", 0)
	elif (STATE == "SIM"):
		global sim_q
		global sim_p
		sim_q.put(Message("SAVE", [num, fn]))
		printl("[CLI]: Saved the node-"+str(num)+"'s blockchain to "+fn+".", 0)
	else:
		printl("[CLI]: Looks like there's nothing to save.", 0)

def end_func(params):
	global STATE
	if (STATE == "NODE"):
		global node_q
		global node_p
		printl("[CLI]: Sending END msg to node", 0)
		node_q.put(Message("END", None))
		node_p.join()
		printl("[CLI]: Ended the node.", 0)
	elif (STATE == "SIM"):
		global sim_q
		global sim_p
		printl("[CLI]: Sending END msg to simulation.", 0)
		sim_q.put(Message("END", None))
		sim_p.join()
		printl("[CLI]: Ended the simulation.", 0)
	STATE = "NONE"

def read_blockchain(params):
	fn = get_param(params, "file")
	try:
		bc = pickle.load(open(fn, 'rb'))
		printl("[CLI]: The blockchain:", 0)
		print(bc)
	except Exception as e:
		printl("[CLI]: Reading blockchain file caused an error.", 0)
		print(e)

def read_block(params):
	fn = get_param(params, "file")
	try:
		b = pickle.load(open(fn, 'rb'))
		printl("[CLI]: The block:", 0)
		print(b)
		printl("[CLI]: The block's string:", 0)
		print(b.toString())
	except Exception as e:
		printl("[CLI]: Reading block file caused an error.", 0)
		print(e)

cmd_dict = {"start_node": start_node, "start_simulation": start_simulation, "save": save_node, "read_block": read_block, "read_blockchain": read_blockchain, "end": end_func, "help": help}

printl("[CLI]: type help", 0)
while True:
	us_in = input()
	#process
	cmd = us_in.split(" ")[0]
	prerams = us_in.split(" ")[1:]
	params = dict()
	for p in prerams:
		temp = p.split("=")
		if (len(temp) == 2):
			params[temp[0]] = temp[1]
	printl("[CLI]: command:"+cmd, 1)
	printl("[CLI]: parameters:"+params.__str__(), 1)
	#execute
	try:
		cmd_dict[cmd](params)
	except:
		printl("[CLI]: Command went wrong.", 0)

