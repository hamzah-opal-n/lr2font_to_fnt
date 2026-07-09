import os
import subprocess


def convert_glyph_id(glyph_id):
    if glyph_id >= 256 and glyph_id <= 8126:
        glyph_id += 32832
    elif glyph_id >= 8127 and glyph_id <= 15306:
        glyph_id += 49281
    glyph_id = glyph_id.to_bytes((glyph_id.bit_length() + 7) // 8, 'big')
    return ord(glyph_id.decode('cp932'))


def resize(thing, scale):
    thing = round(float(thing) * scale)
    return str(thing)


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
    line = "info face=\"" + fontName + "\" size=" + resize(
        listS[-1][1],
        scale) + " bold=0 italic=0 charset=\"\" unicode=0 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0"
    output.append(line)

    # COMMON
    line = "common lineHeight=" + resize(listS[-1][1], scale) + " base=" + resize(
        listS[-1][1], scale) + " scaleW=0 scaleH=0 pages=" + str(len(listT)) + " packed=0"
    output.append(line)

    # THIS IS WHERE THE FUN BEGINS
    # PAGE
    for item in listT:
        line = "page id=" + item[1] + " file=\"" + item[2].replace(".tga", ".png") + "\""
        output.append(line)

    # CHAR
    spacing = int(resize(listM[-1][1], scale))
    line = "chars count=" + str(len(listR))
    output.append(line)
    for item in listR:
        line = "char id=" + str(convert_glyph_id(int(item[1]))) + " x=" + resize(item[3], scale) + " y=" + resize(item[4], scale) + " width=" + resize(item[5], scale) + " height=" + resize(item[6],scale) + " xoffset=0 yoffset=0 xadvance=" + str(int(resize(item[5], scale)) + spacing) + " page=" + item[2] + " chnl=0"
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
    old_converter(filename, 1)
    with open("SAMPLE.fnt", 'r') as f:
        sample_file = f.read()
    with open("TEST.fnt", 'r') as f:
        test_file = f.read()
    if sample_file == test_file:
        print("TEST OK")
    else:
        print("TEST FAILED")


test()
