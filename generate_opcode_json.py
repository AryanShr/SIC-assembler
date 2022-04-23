import json


# the file to be converted
filename = 'OPCODE.txt'

# resultant dictionary
dict1 = {}

# fields in the sample file
fields =['Format', 'OPCODE']

with open(filename) as fh:
	
	for line in fh:
		
		# reading line by line from the text file
		description = list( line.strip().split(None, 4))
		
		# for output see below
		print(description)
		
		# For creation of each mnemonic
		sno =description[0]
	
		# loop variable
		i = 0
		# intermediate dictionary
		dict2 = {}
		while i<len(fields):
			
				# creating dictionary for each mnemonic and adding Format and OPcode for each
				dict2[fields[i]]= description[i+1]
				i = i + 1
				
		# appending the record of each mnemonic to
		# the main dictionary
		dict1[sno]= dict2


# creating json file		
out_file = open("Instruction_set.json", "w")
json.dump(dict1, out_file, indent = 4)
out_file.close()

        