class Message:
	def __init__(self, header, data):
		self.header = header
		self.data = data

	def __str__(self):
		return "HEADER:\n\t" + self.header + "\nDATA:\n\t" + self.data.__str__()

	def encode(self):
		'''
		encodes the message to bytes.
		assumes that the message has a header of "Block",
		and data of a block,
		since that's the message being sent over the network.
		'''
		return self.data.encode()

