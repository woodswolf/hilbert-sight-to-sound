# the actual meat of the program
def midi_bytes(n, continuation_flag = True):
	converted_bytes = []
	while n > 0:
		last_seven = n & 127
		if len(converted_bytes) == 0 or continuation_flag == False:
			converted_bytes.insert(0, (hex(last_seven)[2:].zfill(2)))
		else:
			converted_bytes.insert(0, (hex(last_seven + 128)[2:].zfill(2)))
		n = n >> 7
	bytestring = "".join(converted_bytes).upper()
	print(bytestring)

# helper function for integer input
def get_int(prompt):
	while True:
		try:
			return int(input(prompt))
		except ValueError:
			print("Invalid input! Please enter an integer.")

# helper function for boolean input
def get_bool(prompt):
	while True:
		try:
			return {"true":True, "t":True, "yes":True, "y":True, "false":False, "f":False, "no":False, "n":False}[input(prompt).lower()]
		except KeyError:
			print("Invalid input! Please enter a boolean value.")

# for when this program is run from console
if __name__ == "__main__":
	cont = True
	while cont:
		num = get_int("Enter an integer to convert: ")
		cont_flag = get_bool("Is this a delta-time or other arbitrary-length integer that requires continuation bits? (Y/N) ")
		midi_bytes(num,cont_flag)
		cont = get_bool("Convert another number? (Y/N) ")