version = "net interface"
from socket import *

def get(serverSocket):
	'''
	gets a blockstring from the serverSocket.
	times out in 1 second if there are none.
	'''
	tod = False
	blockstring = None
	try:
		connectionSocket, addr = serverSocket.accept()
		blockstring = connectionSocket.recv(1024).decode()
		connectionSocket.close()
	except Exception as e:
		print(e)
		tod = True
	return blockstring, tod

def put(clientSocket, serverTuple, bs):
	'''
	sends a blockstring to the specified node.
	'''
	error = False
	try:
		clientSocket.connect(serverTuple)
		clientSocket.send(bs.encode())
		clientSocket.close()
	except Exception as e:
		print(e)
		error = True
	return error

def putAll(neighbour_list, bs):
	'''
	sends a blockstring to the nodes in the list.
	'''
	for n in neighbour_list:
		print(n)
		cs1 = socket(AF_INET, SOCK_STREAM)
		cs1.settimeout(5)
		e = put(cs1, n, bs)
