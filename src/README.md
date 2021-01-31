## Structure

The main script for generating the list is `gen_ost_list.py`. The `txt` directory contains the source text files from which the list is generated. The `font` directory contains the font used.

## Requirements

The script requires Python 3.9 and depends on the `FPDF2` package, which you can install with `pip`:

```bash
pip install -r requirements.txt
```

The default font is `Arial Unicode MS`, which must be placed in the `font` directory with the name `ARIALUNI.TTF`. You can specify a custom font with the option `--font`.

## Usage

```
gen_ost_list.py [-h] [--src SRC_DIR_PATH] [--font FONT_PATH] [--html [HTML_PATH]] [--json [JSON_PATH]] [--pdf [PDF_PATH]] [--wiki [WIKI_PATH]]

optional arguments:
	-h, --help          show this help message and exit
	--src SRC_DIR_PATH  Path of input source folder [default = './txt']
	--font FONT_PATH    Path of font used for the PDF [default = './font/ARIALUNI.ttf']
	--html [HTML_PATH]  Path of output HTML file [default = './Steins;Gate Anime OST List.html']
	--json [JSON_PATH]  Path of output JSON file [default = './Steins;Gate Anime OST List.json']
	--pdf [PDF_PATH]    Path of output PDF file [default = './Steins;Gate Anime OST List.pdf']
	--wiki [WIKI_PATH]  Path of output Wikitext file [default = './Steins;Gate Anime OST List.txt']
```

Options `--html`, `--json`, `--pdf`, `--wiki` act as switches for the possible outputs. At least one should be specified. For example, in order to generate the list in HTML and PDF format with default paths one should execute the command:

```bash
python gen_ost_list.py --html --pdf
```

In order to specify a custom path, one should execute the command:

```bash
python gen_ost_list.py --html "custom_path.html" --pdf "custom_path.pdf"
```