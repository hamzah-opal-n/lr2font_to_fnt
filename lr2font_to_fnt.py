import os
import subprocess

print ("LR2FONT to FNT")


def glyphConvert(id):
  if id >= 256 and id <= 8126:
    id += 32832
  elif id >= 8127 and id <= 15306:
    id += 49281
  id = id.to_bytes((id.bit_length() + 7) // 8, 'big')
  return ord(id.decode('cp932'))

def resize(thing):
  thing = round(float(thing) * scale)
  return str(thing)



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





# LOAD LR2FONT AND SORT TAGS

inputFile = open(os.path.expanduser(fileName) , "r", errors="ignore")
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

line = "info face=\"" + fontName + "\" size=" + resize(listS[-1][1]) + " bold=0 italic=0 charset=\"\" unicode=0 stretchH=100 smooth=1 aa=1 padding=0,0,0,0 spacing=0,0"
output.append(line)



# COMMON

line = "common lineHeight=" + resize(listS[-1][1]) + " base=" + resize(listS[-1][1]) + " scaleW=0 scaleH=0 pages=" + str(len(listT)) + " packed=0"
output.append(line)



# THIS IS WHERE THE FUN BEGINS
# PAGE

for item in listT:
  line = "page id=" + item[1] + " file=\"" + item[2].replace(".tga", ".png") + "\""
  output.append(line)



# CHAR

spacing = int(resize(listM[-1][1]))

line = "chars count=" + str(len(listR))
output.append(line)


for item in listR:
  line = "char id=" + str(glyphConvert(int(item[1]))) + " x=" + resize(item[3]) + " y=" + resize(item[4]) + " width=" + resize(item[5]) + " height=" + resize(item[6]) + " xoffset=0 yoffset=0 xadvance=" + str(int(resize(item[5])) + spacing) + " page=" + item[2] + " chnl=0"
  output.append(line)


output.append("kernings count=0")



with open(fontName + ".fnt", 'w') as f:
  for line in output:
    f.write(line)
    f.write('\n')


try:
  subprocess.call(["magick", "mogrify", "-resize", str(scale*100) + "%", "-format", "png", "*.tga"])
except FileNotFoundError:
  print("ImageMagick not found. You'll have to convert the textures to .png yourself I guess...")