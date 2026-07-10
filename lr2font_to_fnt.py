from pathlib import Path
import subprocess
import argparse


def old_magick_code(scale):
    try:
        subprocess.call(["magick", "mogrify", "-resize", str(scale * 100) + "%", "-format", "png", "*.tga"])
    except FileNotFoundError:
        print("ImageMagick not found. You'll have to convert the textures to .png yourself I guess...")


def convert_char_id(char_id):
    """Convert .lr2font glyph id to standard glyph id for .fnt files"""
    if not (char_id < 256 or char_id > 15306):
        if char_id >= 8127:
            char_id += 49281
        else:
            char_id += 32832
    char_id = char_id.to_bytes((char_id.bit_length() + 7) // 8, 'big')
    return ord(char_id.decode('cp932'))


def scale_value(value, scale):
    """Scale value based on scale factor"""
    return round(value * scale)


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
            "id": convert_char_id(item["char"]),
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


def write_fnt_file(fnt, fnt_filepath):
    """Write .fnt file to fnt_filepath"""
    output = []
    for name, records in fnt.items():
        for record in records:
            line = [name]
            for key, value in record.items():
                line.append(f"{key}={value}")
            output.append(" ".join(line))
    with open(fnt_filepath, "w") as f:
        f.write("\n".join(output))


def convert_lr2font_to_fnt(filepath_string, scale):
    """Convert .lr2font file to .fnt file"""
    lr2font_filepath = Path(filepath_string)
    lr2font = load_lr2font(lr2font_filepath)
    fnt = create_fnt_from_lr2font(lr2font, scale)
    write_fnt_file(fnt, lr2font_filepath.with_suffix(".fnt"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("lr2font", help="lr2font filename")
    parser.add_argument("-s", "--scale", type=float, default=1.0, help="scale factor")
    args = parser.parse_args()
    convert_lr2font_to_fnt(args.lr2font, args.scale)
