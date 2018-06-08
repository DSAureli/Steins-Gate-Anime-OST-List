##############################
#       generateJSON.py      #
# Steins;Gate Full Anime OST #
#      Author : DSAureli     #
##############################

import os;
import re;
import sys;

ep = '''
	{{
		"number" : "{}",
		"tracks" :
		[
{}
		]
	}},
'''[1:];

tr = '''
			{{
				"time" : "{}",
				"title" : "{}",
				"comment" : "{}",
				"scene" : "{}"
			}},
'''[1:];

def gen_trs(filename):
	str = "";
	with open(filename) as file:
		for line in file.readlines():
			str += tr.format( \
				line[line.find('[')+1 : line.find(']')], \
				line[line.find(']')+2 : (line.find('(')-1 if line.find('(') != -1 else line.find('{')-1)], \
				line[line.find('(')+1 : line.find(')')].replace('"', '\\"') if line.find('(') != -1 else "", \
				line[line.find('{')+1 : line.find('}')].replace('"', '\\"'));
	return str[:-2];

def gen_eps():
	dir = 'txt';
	str = '';
	for filename in [f for f in os.listdir(dir) if re.match('^ep[0-9]{2}b?\.txt$', f)]:
		str += ep.format(filename.split('.')[0][2:], gen_trs(dir + '/' + filename));
	return str[:-2];

def main(path):
	path += '/S;G_OST.json';
	if (os.path.isfile(path)):
		while True:
			ow = input('File "{}" already exists. Do you want to overwrite it? [Y/n]'.format(os.path.abspath(path)));
			if (len(ow) != 0 and ow[0].lower() != 'y'):
				if (ow[0].lower() != 'n'):
					continue;
				return -1;
			break;
	try:
		with open(path, 'w') as outfile:
			outfile.write('[\n{}\n]'.format(gen_eps()));
	except Exception as ex:
		print(ex);
		print('Press any key to exit...', end = '');
		input();
		return -1;

if __name__ == '__main__':
	arg = sys.argv[1] if len(sys.argv) > 1 else '.';
	main(arg);