import os
import sys

for filename in os.listdir(os.getcwd()):
	if filename.find('.ipynb') < 0:
		continue

	execution_count = 0
	clean_lines = []

	with open(filename, 'r', encoding='utf-8') as infile:
		for line in infile.readlines():
			if line.find('"execution_count"') > 0:
				if line.find('"') == 3:
					execution_count += 1

				clean_lines.append('%s: %d,\n' % (line[0:line.find(':')], execution_count))
			elif line.find('matplotlib.figure') > 0:
				continue
			else:
				end_string = line.rfind('\\n"')

				if end_string > 0:
					while line[end_string - 1] == ' ':
						line = line[0:(end_string-1)] + line[end_string:]

				clean_lines.append(line)

	with open(filename, 'w', encoding='utf-8') as outfile:
		outfile.write(''.join(clean_lines))