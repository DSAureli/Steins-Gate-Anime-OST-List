##############################
#       generatePDF.py       #
# Steins;Gate Full Anime OST #
#      Author : DSAureli     #
##############################

import os;
import sys;
import json;
from fpdf import FPDF;

def gen_pdf(jsonpath, pdfpath):
	with open(jsonpath) as data_file:
		episodes = json.load(data_file);
	pdf = FPDF();
	pdf.set_font('Arial', '', 10);
	maxw = {'number' : 0, 'time' : 0, 'title' : 0, 'comment' : 0, 'scene' : 0};
	maxh = 30;
	for episode in episodes:
		maxw['number'] = max(maxw['number'], pdf.get_string_width(episode['number']) + 10);
		for track in episode['tracks']:
			for x in track:
				maxw[x] = max(maxw[x], pdf.get_string_width(track[x]) + 10);
			maxh += 5;
	pdf = FPDF('P', 'mm', (sum(x for x in maxw.values()) + 20, maxh));
	pdf.set_auto_page_break(False);
	pdf.set_font('Arial', '', 10);
	pdf.set_title('Steins;Gate Anime OST');
	pdf.add_page();
	pdf.cell(maxw['number'], 10, 'Ep', 1, 0, 'C');
	pdf.cell(maxw['time'], 10, 'Time', 1, 0, 'C');
	pdf.cell(maxw['title'], 10, 'Title', 1, 0, 'C');
	pdf.cell(maxw['comment'], 10, 'Comment', 1, 0, 'C');
	pdf.cell(maxw['scene'], 10, 'Scene', 1, 0, 'C');
	pdf.ln();
	tracks = {};
	for episode in episodes:
		pdf.cell(maxw['number'], len(episode['tracks']) * 5, episode['number'], 1, 0, 'C');
		pdf.ln(0);
		for track in episode['tracks']:
			pdf.cell(maxw['number'], 5);
			for x in track:
				pdf.cell(maxw[x], 5, track[x], 1, 0, 'C');
			pdf.ln();
			tracks.setdefault(track['title'], []).append({'number': episode['number'], 'time': track['time'], 'comment': track['comment'], 'scene': track['scene']});
	pdf.add_page();
	pdf.cell(maxw['title'], 10, 'Title', 1, 0, 'C');
	pdf.cell(maxw['number'], 10, 'Ep', 1, 0, 'C');
	pdf.cell(maxw['time'], 10, 'Time', 1, 0, 'C');
	pdf.cell(maxw['comment'], 10, 'Comment', 1, 0, 'C');
	pdf.cell(maxw['scene'], 10, 'Scene', 1, 0, 'C');
	pdf.ln();
	for track in sorted(tracks, key=str.lower):
		pdf.cell(maxw['title'], len(tracks[track]) * 5, track, 1, 0, 'C');
		pdf.ln(0);
		for episode in tracks[track]:
			pdf.cell(maxw['title'], 5);
			for x in episode:
				pdf.cell(maxw[x], 5, episode[x], 1, 0, 'C');
			pdf.ln();
	pdf.output(pdfpath);
	
def main(path):
	pdfpath = path + '/S;G_OST.pdf';
	jsonpath = path + '/S;G_OST.json';
	if (os.path.isfile(pdfpath)):
		while True:
			ow = input('File "{}" already exists. Do you want to overwrite it? [Y/n]'.format(os.path.abspath(pdfpath)));
			if (len(ow) != 0 and ow[0].lower() != 'y'):
				if (ow[0].lower() != 'n'):
					continue;
				return -1;
			break;
	try:
		gen_pdf(jsonpath, pdfpath);
	except Exception as ex:
		print(ex);
		print('Press any key to exit...', end = '');
		input();
		return -1;

if __name__ == '__main__':
	arg = sys.argv[1] if len(sys.argv) > 1 else '.';
	main(arg);