import os
from pathlib import Path
import subprocess


def convert_glyph_id(glyph_id):
    if not (glyph_id < 256 or glyph_id > 15306):
        if glyph_id >= 8127:
            glyph_id += 49281
        else:
            glyph_id += 32832
    glyph_id = glyph_id.to_bytes((glyph_id.bit_length() + 7) // 8, 'big')
    return ord(glyph_id.decode('cp932'))


def resize_old(thing, scale):
    thing = round(float(thing) * scale)
    return str(thing)


def scale_value(value, scale):
    return round(value * scale)


def old_converter(fileName, scale):
    # LOAD LR2FONT AND SORT TAGS
    inputFile = open(os.path.expanduser(fileName), "r", errors="ignore")
    listS = []
    listM = []
    listT = []
    listR = []
    output = []
    fontName = fileName.replace(".lr2font", "")

    while True:
        line = inputFile.readline()
        if not line:
            break
        if line[0:2] == "#S":
            listS.append(line.strip().split(","))
        elif line[0:2] == "#M":
            listM.append(line.strip().split(","))
        elif line[0:2] == "#T":
            listT.append(line.strip().split(","))
        elif line[0:2] == "#R":
            listR.append(line.strip().split(","))
    inputFile.close()

    # INFO
    line = "info face=\"" + fontName + "\" size=" + resize_old(
        listS[-1][1],
        scale) + " bold=0 italic=0 charset=\"\" unicode=0 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0"
    output.append(line)

    # COMMON
    line = "common lineHeight=" + resize_old(listS[-1][1], scale) + " base=" + resize_old(
        listS[-1][1], scale) + " scaleW=0 scaleH=0 pages=" + str(len(listT)) + " packed=0"
    output.append(line)

    # THIS IS WHERE THE FUN BEGINS
    # PAGE
    for item in listT:
        line = "page id=" + item[1] + " file=\"" + item[2].replace(".tga", ".png") + "\""
        output.append(line)

    # CHAR
    spacing = int(resize_old(listM[-1][1], scale))
    line = "chars count=" + str(len(listR))
    output.append(line)
    for item in listR:
        line = "char id=" + str(convert_glyph_id(int(item[1]))) + " x=" + resize_old(item[3],
                                                                                     scale) + " y=" + resize_old(
            item[4], scale) + " width=" + resize_old(item[5], scale) + " height=" + resize_old(item[6],
                                                                                               scale) + " xoffset=0 yoffset=0 xadvance=" + str(
            int(resize_old(item[5], scale)) + spacing) + " page=" + item[2] + " chnl=0"
        output.append(line)

    output.append("kernings count=0")

    with open(fontName + ".fnt", 'w') as f:
        for line in output:
            f.write(line)
            f.write('\n')

    try:
        subprocess.call(["magick", "mogrify", "-resize", str(scale * 100) + "%", "-format", "png", "*.tga"])
    except FileNotFoundError:
        print("ImageMagick not found. You'll have to convert the textures to .png yourself I guess...")


def load_lr2font(lr2font_filepath):
    """Load .lr2font file and return info as dict"""
    lr2font = {"name": lr2font_filepath.stem, "#S": [], "#M": [], "#T": [], "#R": []}
    with lr2font_filepath.open(errors="ignore") as input_file:
        for line in input_file:
            if line[0] != "#":
                continue
            record = line.strip().split(",")
            if record[0] == "#S":  # S lines - define font size
                lr2font["#S"].append({"size": int(record[1])})
            elif record[0] == "#M":  # M lines - define font spacing
                lr2font["#M"].append({"spacing": int(record[1])})
            elif record[0] == "#T":  # T lines - define image files
                lr2font["#T"].append({"img": int(record[1]), "file": record[2]})
            elif record[0] == "#R":  # R lines - define characters
                lr2font["#R"].append(
                    {"char": int(record[1]), "img": int(record[2]), "x": int(record[3]), "y": int(record[4]),
                     "w": int(record[5]), "h": int(record[6])})
    return lr2font


def convert_lr2font_to_fnt(filepath_string, scale):
    """Convert .lr2font file to .fnt file"""
    lr2font_filepath = Path(filepath_string)
    lr2font = load_lr2font(lr2font_filepath)
    font_name = lr2font_filepath.stem
    fnt = create_fnt_from_lr2font(lr2font, scale)
    print(fnt)
    create_and_write_fnt_old(lr2font, font_name, scale)


def create_and_write_fnt_old(lr2font, font_name, scale):
    output = []

    # INFO
    line = "info face=\"" + font_name + "\" size=" + resize_old(
        lr2font["#S"][-1]["size"],
        scale) + " bold=0 italic=0 charset=\"\" unicode=0 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0"
    output.append(line)

    # COMMON
    line = "common lineHeight=" + resize_old(lr2font["#S"][-1]["size"], scale) + " base=" + resize_old(
        lr2font["#S"][-1]["size"], scale) + " scaleW=0 scaleH=0 pages=" + str(len(lr2font["#T"])) + " packed=0"
    output.append(line)

    # THIS IS WHERE THE FUN BEGINS
    # PAGE
    for item in lr2font["#T"]:
        line = "page id=" + item["img"] + " file=\"" + item["file"].replace(".tga", ".png") + "\""
        output.append(line)

    # CHAR
    spacing = int(resize_old(lr2font["#M"][-1]["spacing"], scale))
    line = "chars count=" + str(len(lr2font["#R"]))
    output.append(line)
    for item in lr2font["#R"]:
        line = "char id=" + str(convert_glyph_id(int(item["char"]))) + " x=" + resize_old(item["x"],
                                                                                          scale) + " y=" + resize_old(
            item["y"], scale) + " width=" + resize_old(item["w"], scale) + " height=" + resize_old(item["h"],
                                                                                                   scale) + " xoffset=0 yoffset=0 xadvance=" + str(
            int(resize_old(item["w"], scale)) + spacing) + " page=" + item["img"] + " chnl=0"
        output.append(line)

    output.append("kernings count=0")
    with open(f"{font_name}.fnt", 'w') as f:
        for line in output:
            f.write(line)
            f.write('\n')


def create_fnt_from_lr2font(lr2font, scale):
    """Create .fnt dict from .lr2font dict with values adjusted based on scale"""
    font_size = scale_value(lr2font["#S"][-1]["size"], scale)
    spacing = scale_value(lr2font["#M"][-1]["spacing"], scale)
    fnt = {
        "info": [
            {
                "face": f"\"{lr2font['name']}\"",
                "size": font_size,
                "bold": 0,
                "italic": 0,
                "charset": "\"\"",
                "unicode": 0,
                "stretchH": 100,
                "smooth": 1,
                "aa": 1,
                "padding": "0,0,0,0",
                "spacing": "0,0"
            }
        ],
        "common": [
            {
                "lineHeight": font_size,
                "base": font_size,
                "scaleW": 0,
                "scaleH": 0,
                "pages": len(lr2font["#T"]),
                "packed": 0
            }
        ],
        "page": [],
        "chars": [
            {
                "count": len(lr2font["#R"])
            }
        ],
        "char": [],
        "kernings": [
            {
                "count": 0
            }
        ]
    }

    # page
    for item in lr2font["#T"]:
        fnt["page"].append({
            "id": item["img"],
            "file": f"\"{item['file'].replace('.tga', '.png')}\""
        })

    # char
    for item in lr2font["#R"]:
        fnt["char"].append({
            "id": convert_glyph_id(item["char"]),
            "x": scale_value(item["x"], scale),
            "y": scale_value(item["y"], scale),
            "width": scale_value(item["w"], scale),
            "height": scale_value(item["h"], scale),
            "xoffset": 0,
            "yoffset": 0,
            "xadvance": scale_value(item["w"], scale) + spacing,
            "page": item["img"],
            "chnl": 0
        })

    return fnt


def main():
    print("LR2FONT to FNT")
    # USER INPUT
    while True:
        receivedInput = input("Enter lr2font filename: ")
        try:
            fileName = str(receivedInput)
        except ValueError:
            print("Invalid input received.")
        else:
            break

    while True:
        receivedInput = input("Enter scaling factor (decimal): ")
        try:
            scale = float(receivedInput)
        except ValueError:
            print("Invalid input received.")
        else:
            break

    old_converter(fileName, scale)


def test():
    filename = "TEST.lr2font"
    convert_lr2font_to_fnt(filename, 1)
    with open("SAMPLE.fnt", 'r') as f:
        sample_file = f.read()
    with open("TEST.fnt", 'r') as f:
        test_file = f.read()
    if sample_file == test_file:
        print("TEST OK")
    else:
        print("TEST FAILED")


test()
