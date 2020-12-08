# Blockchain Node

This was a project to simulate a blockchain protocol in Python for CMPT471.

## The Required Environment

This Python code runs on Ubuntu 20.04, using Python version 3.8.5. It has also been tested for the latest Python version, 3.9.0.

It should work for earlier versions of Python, up to version 3.6.

If you need to upgrade your Python version, you can use the following commands:
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.9

The program uses many of Python's built-in libraries, such as the following:
hashlib
time
pickle
multiprocessing
socket
secrets - (added in version 3.6)
sys
random

test.py uses matplotlib. If you want to run it, it can be installed with:
pip3 install matplotlib

## Test Case 1: Networked Blockchain Nodes

open 3 terminals, do the following:
all terminals: python3 cli.py
terminal 1: start_node port=3000 conns=conns1.txt name=term-1
terminal 2: start_node port=4000 conns=conns2.txt name=term-2
terminal 3: start_node port=5000 conns=conns3.txt name=term-3
[wait some time for the nodes to mine some blocks, about 1 per 10 seconds]
terminal 1: save file=the_blockchain.pkl
all terminals: end
terminal 1: read_blockchain file=the_blockchain.pkl
all terminals: ctrl-C

You should see the three nodes you started start mining for blocks on a blockchain, and sending blocks to each other. The save command saves a blockchain to file. The "read_blockchain" command should display the blockchain you saved to file. The "end" command ends the nodes you started.


##Test Case 2: Simulated Blockchain Nodes

To make testing this blockchain protocol simpler, I built a simulator to simulate many nodes on a network at once. Only one terminal is needed.

start_simulation num_nodes=3
[wait some time for the nodes to mine some blocks, about 1 per 10 seconds]
save file=the_blockchain2.pkl
end
read_blockchain file=the_blockchain2.pkl
ctrl-C

You should see all the nodes under the simulation mining and sharing blocks on a blockchain. The rest of the commands perform similarly to the first test case.

##Other

If you don't want to wait for your nodes/simulation to create a large blockchain, there is an example blockchain in the repo. It is called "exbc.pkl", and can be read with the "read_blockchain" command in the CLI.

There is also a block you can read, the genesis block. It is in "genblk.pkl", and can be read with the "read_block" command in the CLI.

