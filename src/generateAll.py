##############################
#       generateAll.py       #
# Steins;Gate Full Anime OST #
#      Author : DSAureli     #
##############################

import sys;
import generateJSON;
import generatePDF;

path = sys.argv[1] if len(sys.argv) > 1 else '..';
if (generateJSON.main(path) != -1):
	generatePDF.main(path);