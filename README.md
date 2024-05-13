# yCheck2 Decoder

## Purpose
Decrypts and converts yCheck2 files into a print-ready PDF format. Supports PC, Mac, and Linux.

## Requirements
- Python 3.12.3
- reportlab

## Installation
1. Ensure the csv, output, and fonts folders are present.
2. Ensure the fonts folder contains ```Courier New Bold.ttf``` ```Arial Bold.ttf``` ```Courier New.ttf``` ```Arial``` ```AdvMICR.ttf``` font files.
3. Install required pip modules using ```pip3 install -r requirements.txt```

## Usage
### Converting yCheck2 File to PDF
To convert a .ycheck2 file to .pdf use the following command syntax:
```python3 decode_ycheck2.py --input *.ycheck2 --output *.pdf```

macOS / Linux users can opt to use the shell script like follows:
```./ycheck2.sh *.ycheck2```

You can view the script help page by doing the following:
```python3 decode_ycheck2.py --help```

## Limitations
### Fonts
The only font styles currently implemented are regular and bold. From what the files tested with, it doesn't seem like other styles are ever used.

### Images
Embedded images are not implemented. I believe this feature is used by signature filling, I may come back and implement this later if needed.

### Rectangle Text Drawing
This is technically part of the file spec, but I've never seen it used in any test document. I've implemeneted a reverse engineered bit of code to handle it but it's untested so user beware.

## Advanced
### Debugging
To enable debug logging information, define the ```YCHECK_DEBUG``` environment variable to ```True```
