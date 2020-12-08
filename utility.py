#0 - user should see
#1 - testing - basic steps, only prints after the user types.
#2 - testing - if continues printing, so the prompt never prints.
gl = 2
def printl(string, level):
	if (level <= gl):
		print(string)
