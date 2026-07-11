from pathlib import Path
import argparse


def convert_char_id(char_id):
    """
    Convert .lr2font character id to standard character id for .fnt files

    .lr2font character id information referenced from https://right-stick.sub.jp/lr2skinhelp.html
    """
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
    """
    Load .lr2font file and return info as dict

    .lr2font file specs referenced from https://right-stick.sub.jp/lr2skinhelp.html
    """
    lr2font = {"name": lr2font_filepath.stem, "#S": [], "#M": [], "#T": [], "#R": []}
    with lr2font_filepath.open(errors="ignore") as input_file:
        for line in input_file:
            if line[0] != "#":  # all necessary lines start with #
                continue
            record = line.strip().split(",")
            if record[0] == "#S":  # S lines - define font size
                lr2font["#S"].append({
                    "size": int(record[1])
                })
            elif record[0] == "#M":  # M lines - define font spacing
                lr2font["#M"].append({
                    "spacing": int(record[1])
                })
            elif record[0] == "#T":  # T lines - define image files
                lr2font["#T"].append({
                    "img": int(record[1]),
                    "file": record[2]
                })
            elif record[0] == "#R":  # R lines - define characters
                lr2font["#R"].append({
                    "char": int(record[1]),
                    "img": int(record[2]),
                    "x": int(record[3]),
                    "y": int(record[4]),
                    "w": int(record[5]),
                    "h": int(record[6])
                })
    return lr2font


def create_fnt_from_lr2font(lr2font, scale):
    """Create .fnt dict from .lr2font dict with values adjusted based on scale"""
    font_size = scale_value(lr2font["#S"][-1]["size"], scale)  # take only the value from the last #S line
    spacing = scale_value(lr2font["#M"][-1]["spacing"], scale)  # take only the value from the last #M line
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
    # page records
    for item in lr2font["#T"]:
        fnt["page"].append({
            "id": item["img"],
            "file": f"\"{item['file'].replace('.tga', '.png')}\""
        })
    # char records
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


def convert_lr2font_to_fnt(lr2font_filepath, scale):
    """Convert .lr2font file to .fnt file"""
    lr2font = load_lr2font(lr2font_filepath)
    fnt = create_fnt_from_lr2font(lr2font, scale)
    write_fnt_file(fnt, lr2font_filepath.with_suffix(".fnt"))
    print(f"Wrote to {lr2font_filepath.with_suffix(".fnt")}")


def convert_tga_textures(directory_path, scale):
    """Convert .tga texture files to .png"""
    try:
        from PIL import Image
        tga_textures = sorted(directory_path.glob("*.tga"))  # create list of all .tga files in the directory
        for tga_texture in tga_textures:
            img = Image.open(tga_texture)
            if scale != 1.0:  # no need to resize if the scale is 1.0 aka no change
                img = img.resize((scale_value(img.width, scale), scale_value(img.height, scale)))
            img.save(tga_texture.with_suffix(".png"))
            print(f"Wrote to {tga_texture.with_suffix('.png')}")
    except ImportError:
        print("Error: PIL is not installed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("lr2font", help="lr2font filename")
    parser.add_argument("-s", "--scale", type=float, default=1.0, help="scale factor")
    parser.add_argument("-c", "--convert-tga", action="store_true", help="convert .tga textures to .png")
    args = parser.parse_args()
    input_filepath = Path(args.lr2font)
    try:
        convert_lr2font_to_fnt(input_filepath, args.scale)
    except FileNotFoundError:
        print("Error: .lr2font file not found!")
    if args.convert_tga:
        convert_tga_textures(input_filepath.parent, args.scale)
