"""Generate the OST list of the Steins;Gate anime in HTML, JSON, PDF and Wikitext format.

File name: gen_ost_list.py
Author: DSAureli
Date last updated: 2021/01/31
Python version: 3.9
"""


import os
import re
import json
import datetime
import argparse

from typing import TypedDict, TypeVar, Optional

from fpdf import FPDF


proj_title = "Steins;Gate Anime OST List"

col_name_dict = {
	"episode": "Ep",
	"time": "Time",
	"track": "Track",
	"comment": "Comment",
	"scene": "Scene"
}

pe_col_list = list(col_name_dict.keys())
pt_col_list = ["track", "episode", "time", "comment", "scene"]

pe_list_key = "tracks"
pt_list_key = "episodes"

# type hinting shenanigans

pe_T = TypedDict("pe_T", {
	"episode": str,
	"tracks": list[dict[str, str]]
})

pt_T = TypedDict("pt_T", {
	"track": str,
	"episodes": list[dict[str, str]]
}, total=False) # allow empty dict


def gen_pe_ost_list(src_dir_path: str) -> list[pe_T]:
	"""Generate per-episode OST list from .txt files in 'src_dir_path'."""
	
	ost_list: list[pe_T] = []
	
	with os.scandir(src_dir_path) as e_it:
		for entry in e_it:
			if entry.is_file() and re.fullmatch(r"ep[0-9]{2}b?\.txt", entry.name): # match whole string
				
				# get list of tracks for the episode
				track_list = []
				
				with open(entry, encoding="utf-8-sig") as file: # encoding strips BOM if file encoded with UTF-8-BOM
					for line in file.readlines():
						
						# scene first as it may contain square brackets
						scene_res = re.search(r"\{(.*?)\}", line)
						if scene_res: # if scene group found
							line = line.replace(scene_res.group(0), "") # remove scene group from string
							scene = scene_res.group(1) # get content of scene group
						else:
							continue
						
						# timestamp
						ts_res = re.search(r"\[(.*?)\]", line)
						if ts_res: # if timestamp group found
							line = line.replace(ts_res.group(0), "") # remove timestamp group from string
							ts = ts_res.group(1) # get content of timestamp group
						else:
							continue
						
						# comment (optional)
						cmnt = ""
						cmnt_res = re.search(r"\((.*?)\)", line)
						if cmnt_res: # if comment group found
							line = line.replace(cmnt_res.group(0), "") # remove comment group from string
							cmnt = cmnt_res.group(1) # get content of comment group
						
						# track title
						track = line.strip()
						
						track_list.append({
							"time": ts,
							"track": track,
							"comment": cmnt,
							"scene": scene
						})
				
				ep = entry.name.split(".")[0][2:]
				
				ost_list.append({
					"episode": ep,
					pe_list_key: track_list
				})
	
	return ost_list

def gen_pt_ost_list(pe_ost_list: list[pe_T]) -> list[pt_T]:
	"""Generate per-track dictionary list."""
	
	pt_ost_dict: pt_T = {}
	for ep_dict in pe_ost_list:
		for track_dict in ep_dict[pe_list_key]:
			pt_ost_dict \
				.setdefault(track_dict["track"], []) \
				.append(
					{"episode": ep_dict["episode"]}
					|
					{key : track_dict[key] for key in col_name_dict if key not in ["track", "episode"]}
				)
	
	pt_ost_list: list[pt_T] = [
		{"track": track, pt_list_key: pt_ost_dict[track]} for track in sorted(pt_ost_dict, key=str.lower)
	]
	
	return pt_ost_list


def gen_pdf(font_path: str, pdf_path: str, pe_ost_list: list[pe_T], pt_ost_list: list[pt_T]) -> None:
	"""Generate PDF file with per-episode and per-track listings from per-episode OST list."""
	
	font_family = "ext_font"
	page_margin = 10
	font_size = 10
	cell_h = 5
	cell_padding = 10
	
	# compute cells and page size
	
	pdf = FPDF()
	pdf.add_font(font_family, fname=font_path, uni=True)
	pdf.set_font(font_family, size=font_size)
	
	page_h = 0
	max_col_w = {key : pdf.get_string_width(col_name_dict[key]) for key in col_name_dict} # init with column name width
	
	for ep_dict in pe_ost_list:
		page_h += cell_h * len(ep_dict[pe_list_key])
		first_col_key = pe_col_list[0]
		max_col_w[first_col_key] = max(max_col_w[first_col_key], pdf.get_string_width(ep_dict[first_col_key]))
		
		for track_dict in ep_dict[pe_list_key]:
			for key in track_dict:
				max_col_w[key] = max(max_col_w[key], pdf.get_string_width(track_dict[key]))
	
	col_w = {key : max_col_w[key] + cell_padding for key in max_col_w}
	
	page_w = sum(col_w.values()) + 2 * page_margin
	page_h += 3 * page_margin + font_size
	
	# init PDF
	
	pdf = FPDF(format=(page_w, page_h))
	pdf.set_author("DSAureli")
	pdf.set_creation_date(datetime.date.today())
	pdf.set_title(proj_title)
	pdf.set_margins(page_margin, page_margin)
	pdf.add_font(font_family, fname=font_path, uni=True)
	pdf.set_font(font_family, size=font_size)
	pdf.set_auto_page_break(False)
	
	# define table generating function
	
	def gen_table(col_list: list[str], ost_list: list[TypeVar("T", pe_T, pt_T)], list_key: str) -> None:
		"""
		Generate table with columns as in 'col_list' and data as in 'ost_list'.
		'list_key' is the key for the list inside each dictionary in 'ost_list'.
		"""
		
		# column titles
		for key in col_list:
			pdf.cell(w=col_w[key], h=2*cell_h, border=1, align="C", txt=col_name_dict[key])
		pdf.ln()
		
		for head_dict in ost_list:
			# header cell, spanning multiple rows
			pdf.cell(w=col_w[col_list[0]], h=len(head_dict[list_key])*cell_h, border=1, align="C", txt=head_dict[col_list[0]])
			pdf.ln(h=0) # line feed, but don't increase y coord
			
			for row_dict in head_dict[list_key]:
				pdf.set_x(pdf.get_x() + col_w[col_list[0]]) # place cursor after header cell
				
				for key in row_dict:
					pdf.cell(w=col_w[key], h=cell_h, border=1, align="C", txt=row_dict[key])
				
				pdf.ln()
	
	# generate per-episode page
	
	pdf.add_page()
	
	pdf.cell(w=0, align="C", txt=f"{proj_title}  ~  per-episode")
	pdf.ln(h=page_margin)
	
	gen_table(pe_col_list, pe_ost_list, pe_list_key)
	
	# generate per-track page
	
	pdf.add_page()
	
	pdf.cell(w=0, align="C", txt=f"{proj_title}  ~  per-track")
	pdf.ln(h=page_margin)
	
	gen_table(pt_col_list, pt_ost_list, pt_list_key)
	
	# write PDF to file
	
	pdf.output(pdf_path)

def gen_wiki(wiki_path: str, pe_ost_list: list[pe_T], pt_ost_list: list[pt_T]) -> None:
	
	# define table generating function
	
	def gen_wiki_table(tbl_title: str, col_list: list[str], ost_list: list[TypeVar("T", pe_T, pt_T)], list_key: str) -> str:
		tbl_txt = ""
		tbl_txt += '{| class="article-table mw-collapsible mw-collapsed"\n'
		tbl_txt += f'|+ class="nowrap" |{tbl_title}\n' # caption
		tbl_txt += '|-\n'
		
		for col in col_list:
			tbl_txt += f'! style="text-align: center;" |{col_name_dict[col]}\n' # header cell
		
		for head_dict in ost_list:
			tbl_txt += '|-\n'
			tbl_txt += f'| rowspan="{len(head_dict[list_key])}" style="text-align: center;" |{head_dict[col_list[0]]}\n'
			
			for row_dict_idx, row_dict in enumerate(head_dict[list_key]):
				if row_dict_idx != 0:
					tbl_txt += '|-\n'
				
				for key in row_dict:
					tbl_txt += f'| style="text-align: center;" |{row_dict[key]}\n'
			
		tbl_txt += '|}\n'
		return tbl_txt
	
	wiki_txt = ""
	
	# generate per-episode table
	
	wiki_txt += gen_wiki_table("Per-episode", pe_col_list, pe_ost_list, pe_list_key)
	
	# generate per-track table
	
	wiki_txt += gen_wiki_table("Per-track", pt_col_list, pt_ost_list, pt_list_key)
	
	# write wiki tables to file
	
	with open(wiki_path, "w", encoding="utf-8") as wiki_f:
		wiki_f.write(wiki_txt)

def gen_html(html_path: str, pe_ost_list: list[pe_T], pt_ost_list: list[pt_T]) -> None:
	
	# define table generating function
	
	def gen_html_table(tbl_title: str, col_list: list[str], ost_list: list[TypeVar("T", pe_T, pt_T)], list_key: str) -> str:
		tbl_txt = ""
		tbl_txt += '<table style="border: 1px solid black; border-collapse: collapse;">\n'
		tbl_txt += f'<caption><h2>{tbl_title}</h2></caption>\n' # caption
		
		cell_style = 'style="padding: .5em; text-align: center; border: 1px solid black;"'
		
		tbl_txt += '<tr>\n'
		for col in col_list:
			tbl_txt += f'<th {cell_style}>{col_name_dict[col]}</th>\n' # header cell
		tbl_txt += '</tr>\n'
		
		for head_dict in ost_list:
			tbl_txt += '<tr>\n'
			tbl_txt += f'<td rowspan="{len(head_dict[list_key])}" {cell_style}>{head_dict[col_list[0]]}</td>\n'
			
			for row_dict_idx, row_dict in enumerate(head_dict[list_key]):
				if row_dict_idx != 0:
					tbl_txt += '<tr>\n'
					
				for key in row_dict:
					tbl_txt += f'<td {cell_style}>{row_dict[key]}</td>\n'
					
				tbl_txt += '</tr>\n'
			
		tbl_txt += '</table>\n'
		return tbl_txt
	
	html_txt = ""
	
	# generate per-episode table
	
	html_txt += gen_html_table("Per-episode", pe_col_list, pe_ost_list, pe_list_key)
	
	# generate per-track table
	
	html_txt += gen_html_table("Per-track", pt_col_list, pt_ost_list, pt_list_key)
	
	# write html tables to file
	
	with open(html_path, "w", encoding="utf-8") as html_f:
		html_f.write(html_txt)


def main(src_dir_path: str, font_path: str, html_path: Optional[str] = None, json_path: Optional[str] = None, pdf_path: Optional[str] = None, wiki_path: Optional[str] = None):
	pe_ost_list = gen_pe_ost_list(src_dir_path)
	pt_ost_list = gen_pt_ost_list(pe_ost_list)
	
	if json_path:
		json_obj = {
			"per-episode": pe_ost_list,
			"per-track": pt_ost_list
		}
		
		with open(json_path, "w") as json_f:
			json_f.write(json.dumps(json_obj, indent="\t"))
	
	if pdf_path:
		gen_pdf(font_path, pdf_path, pe_ost_list, pt_ost_list)
	
	if html_path:
		gen_html(html_path, pe_ost_list, pt_ost_list)
	
	if wiki_path:
		gen_wiki(wiki_path, pe_ost_list, pt_ost_list)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=f"Generate {proj_title} in JSON, PDF and Wikitext format.")
	
	parser.add_argument("--src", type=str, dest="src_dir_path", default="./txt", help="Path of input source folder [default = './txt']")
	parser.add_argument("--font", type=str, dest="font_path", default="./font/ARIALUNI.TTF", help="Path of font used for the PDF [default = './font/ARIALUNI.ttf']")
	parser.add_argument("--html", type=str, dest="html_path", nargs="?", const=f"./{proj_title}.html", default=None, help=f"Path of output HTML file [default = './{proj_title}.html']")
	parser.add_argument("--json", type=str, dest="json_path", nargs="?", const=f"./{proj_title}.json", default=None, help=f"Path of output JSON file [default = './{proj_title}.json']")
	parser.add_argument("--pdf", type=str, dest="pdf_path", nargs="?", const=f"./{proj_title}.pdf", default=None, help=f"Path of output PDF file [default = './{proj_title}.pdf']")
	parser.add_argument("--wiki", type=str, dest="wiki_path", nargs="?", const=f"./{proj_title}.txt", default=None, help=f"Path of output Wikitext file [default = './{proj_title}.txt']")
	
	args = vars(parser.parse_args())
	
	if not os.path.exists(args["src_dir_path"]):
		parser.error("Provided source path does not exist.")
	
	if not os.path.isdir(args["src_dir_path"]):
		parser.error("Provided source path is not a directory.")
		
	if not os.path.exists(args["font_path"]):
		parser.error("Provided font path does not exist.")
	
	if not os.path.isfile(args["font_path"]):
		parser.error("Provided font path is not a file.")
	
	if not any(args[val] for val in ["html_path", "json_path", "pdf_path", "wiki_path"]):
		parser.error("No output argument provided. Use -h for more information.")
	
	main(args["src_dir_path"], args["font_path"], args["html_path"], args["json_path"], args["pdf_path"], args["wiki_path"])
