import re

f = open("thucmorphs.txt")
i = 0

for l in f:
	
	print(re.split('\t', l))

	i += 1
	if i > 5:
		break

f.close()
