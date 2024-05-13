#!/usr/bin/env python3

import zipfile, argparse, os, sys, shutil, csv, logging

from enum import Enum
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import *
from reportlab.lib.pagesizes import letter
from typing import List

if 'YCHECK_DEBUG' in os.environ:
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logging.debug('Logging interface enabled')

ZIP_PASSWORD = '*6-/&c-qHUp =p*!*4U@8xF=(|:!+f'
LEADING_MARGIN = 50
LEADING_MARGIN_ALT = 30
SIDE_MARGIN = 5


pdfmetrics.registerFont(TTFont('Courier New', 'fonts/Courier New.ttf'))
pdfmetrics.registerFont(TTFont('Courier New Bold', 'fonts/Courier New Bold.ttf'))
pdfmetrics.registerFont(TTFont('Arial', 'fonts/Arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial Bold', 'fonts/Arial Bold.ttf'))
pdfmetrics.registerFont(TTFont('AdvMICR', 'fonts/AdvMICR.ttf'))

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', type=str, required=True, help='Input yCheck2 file')
parser.add_argument('-o', '--output', type=str, required=True, help='Output pdf file')

args = parser.parse_args()

class FontStyle(Enum):
    """Font Display Style"""
    REGULAR = 0
    BOLD = 1
    ITALIC = 2
    UNDERLINE = 4
    STRIKEOUT = 8

class ScaleMode(Enum):
    """Coordinate Scaling Mode"""
    TWIPS = 1
    POINTS = 2

class YCheckData:
    """yCheck2 State Data"""
    font_name = ''
    font_size = 0
    font_style = FontStyle.REGULAR 
    scale_mode = ScaleMode.TWIPS 
    current_x = 0.0
    current_y = 0.0

check_data = YCheckData()
    
def extract_ycheck2(input: str, directory: str):
    with zipfile.ZipFile(file=input, mode='r') as zip_ref:
        for member in zip_ref.namelist():
            filename = os.path.basename(member)
            if not filename:
                continue
            source = zip_ref.open(member, pwd=bytes(ZIP_PASSWORD, 'utf-8'))
            target = open(os.path.join(directory, filename), 'wb')
            with source, target:
                shutil.copyfileobj(source, target)
                return filename

    return None

def read_command_csv(file: str):
    commands = []

    with open(file, 'r') as csv_ref:
        reader = csv.reader(csv_ref)
        
        for row in reader:
            commands.append(row)
        
    return commands

def execute_command(command: List[str], canvas: Canvas, is_copy: bool):
    type = command[0]
    if (type is None):
        return None
    
    match type:
        case 'FontName':
            logging.debug(f'Changing document font to {command[1]}')
            check_data.font_name = command[1]
            check_data.font_style = FontStyle.REGULAR

        case 'FontSize':
            logging.debug(f'Changing document font size to {command[1]}')
            if (check_data.font_name == 'AdvMICR'):
                check_data.font_size = float(command[1]) * 1.5
            else:
                check_data.font_size = float(command[1])

        case 'FontBold':
            logging.debug(f'Changing font style to bold')
            if int(command[1]) != -1:
                check_data.font_style = FontStyle.REGULAR
                check_data.font_name = check_data.font_name.split('Bold')[0].strip()
            else:
                check_data.FontStyle = FontStyle.BOLD
                if not check_data.font_name.endswith('Bold'):
                    check_data.font_name = f'{check_data.font_name} Bold'

        case 'FontItalic':
            logging.debug(f'Changing font style to italic')
            if (int(command[1] == -1)):
                check_data.FontStyle |= FontStyle.ITALIC
            else:
                num = int(command[1])
                if (num == 2):
                    check_data.font_style = FontStyle.ITALIC

        case 'FontUnderline':
            logging.debug(f'Changing font style to underline')
            if (int(command[1] == -1)):
                check_data.FontStyle |= FontStyle.UNDERLINE
            else:
                num = int(command[1])
                if (num == 4):
                    check_data.font_style = FontStyle.UNDERLINE

        case 'FontStrikethru':
            logging.debug(f'Changing font style to strikeout')
            if (int(command[1] == -1)):
                check_data.FontStyle |= FontStyle.STRIKEOUT
            else:
                num = int(command[1])
                if (num == 8):
                    check_data.font_style = FontStyle.STRIKEOUT

        case 'ScaleMode':
            match int(command[1]):
                case 1:
                    logging.debug(f'Changing scaling mode to twips')
                    check_data.scale_mode = ScaleMode.TWIPS
                case 2:
                    logging.debug(f'Changing scaling mode to points')
                    check_data.scale_mode = ScaleMode.POINTS

        # Spec Dictates This Does Nothing
        case 'PaperSize':
            logging.debug(f'Changing printed page size')

        case 'CurrentX':
            logging.debug(f'Changing current X coordinate to {command[1]}')
            if (check_data.scale_mode == ScaleMode.TWIPS):
                check_data.current_x = (float(command[1]) / 20) + SIDE_MARGIN
            else:
                check_data.current_x = float(command[1]) + SIDE_MARGIN

        case 'CurrentY':
            logging.debug(f'Changing current Y coordinate to {command[1]}')
            offset = LEADING_MARGIN_ALT if float(command[1]) < 493.2 else LEADING_MARGIN
            if (check_data.scale_mode == ScaleMode.TWIPS):
                check_data.current_y = (float(command[1]) / 20) + offset
            else:
                check_data.current_y = float(command[1]) + offset

        case 'Print':
            if not (is_copy and check_data.font_name == 'AdvMICR'):
                logging.debug(f'Writing text "{command[1]}" to canvas')
                canvas.setFont(check_data.font_name, check_data.font_size)
                if (check_data.font_name == 'AdvMICR'):
                    canvas.drawString(check_data.current_x, check_data.current_y + check_data.font_size / 2, command[1])
                else:
                    canvas.drawString(check_data.current_x, check_data.current_y + check_data.font_size, command[1])

        case 'Print2':
            if not (is_copy and check_data.font_name == 'AdvMICR'):
                logging.debug(f'Writing text "{command[1]}" to canvas')
                canvas.setFont(check_data.font_name, check_data.font_size)
                if (check_data.font_name == 'AdvMICR'):
                    canvas.drawString(check_data.current_x, check_data.current_y + check_data.font_size / 2, command[1])
                else:
                    canvas.drawString(check_data.current_x, check_data.current_y + check_data.font_size, command[1])

        case 'PrintR':
            logging.debug(f'Writing text w/ rectangle to canvas: {command[1]}')
            if ( not (is_copy and check_data.font_name != 'AdvMICR') ):
                canvas.setFont(check_data.font_name, check_data.font_size)
                canvas.rect(10, 10, 80 + round(check_data.current_x), round(check_data.current_y))
                canvas.drawRightString(check_data.current_x, check_data.current_y + check_data.font_size, command[1])

        case 'PaintPicture':
            logging.debug(f'Drawing image raster to canvas')
            # TODO
        case 'PaintPicture2':
            logging.debug(f'Drawing image raster to canvas')
            # TODO
        case 'NonNegotiable':
            if is_copy:
                logging.debug(f'Drawing non-negotiable to canvas')
                canvas.setFont('Arial', 14)
                if (check_data.scale_mode == ScaleMode.TWIPS):
                    canvas.drawString(check_data.current_x * 20, check_data.current_y * 20, command[1])
                else:
                    canvas.drawString(check_data.current_x, check_data.current_y, command[1])

        case 'Orientation':
            logging.debug(f'Changing document orientation')
            # TODO
        case 'ForeColor':
            logging.debug(f'Changing document foreground color')
            # TODO
        case 'Line':
            logging.debug(f'Writing line element to canvas')
            # TODO
        case 'Line2':
            logging.debug(f'Writing line element to canvas')
            # TODO
        case 'Line3':
            logging.debug(f'Writing line element to canvas')
            # TODO
        case 'Line4':
            logging.debug(f'Writing line element to canvas')
            # TODO
        case 'Line5':
            logging.debug(f'Writing line element to canvas')
            # TODO
        case 'Line6':
            logging.debug(f'Writing line element to canvas')
            # TODO
        case 'DrawStyle':
            logging.debug(f'Changing drawing style')
            # TODO
        case 'FillStyle':
            logging.debug(f'Changing fill style')
            # TODO
        case 'FillColor':
            logging.debug(f'Changing fill color')
            # TODO
        case 'DrawMode':
            logging.debug(f'Changing drawing mode')
            # TODO
        case 'DrawWidth':
            logging.debug(f'Changing drawing stroke width')
            # TODO
        case 'PaperBin':
            logging.debug(f'Changing document paper bin')
            # TODO
        case 'AuditInfo':
            logging.debug(f'Changing document audit information')
            # TODO
        case 'EndDoc':
            logging.debug(f'End document processing')
        case _:
            logging.error(f'Uknown operation of type: {type}')

def main():
    command_csv = extract_ycheck2(args.input, os.path.join(os.getcwd(), 'csv'))
    if (command_csv is None):
        sys.exit(1)

    commands = read_command_csv(os.path.join('csv', command_csv))

    canvas = Canvas(args.output, pagesize=letter, bottomup=0)
    
    # Check
    for command in commands:
        execute_command(command, canvas, False)
    
    canvas.showPage()

    # Copy
    for command in commands:
        execute_command(command, canvas, True)

    canvas.save()

if __name__ == '__main__':
    main()
