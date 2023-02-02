import glob
import os
from PIL import Image, ImageOps

for file_name in glob.iglob('*.jpg', recursive=True):
  print(os.path.splitext(file_name)[0])
  colorImage  = Image.open(file_name)
  
  img = colorImage
  
  if img.mode == "P":
    # Handle palette-mapped images
    if 'transparency' in img.info:
        img = img.convert('RGBA')
    else:
        img = img.convert('RGB')

  if img.mode == "RGBA":
    # The image has transparency
    out = Image.new("RGB", img.size, background)
    # Use the image's own alpha channel as the mask
    out.paste(img, mask=img)
  else:
    out = img
  
  colorImage = out
  
  rotated     = colorImage.rotate(45)
  transposed  = colorImage.transpose(Image.ROTATE_90)
  rotated_1     = colorImage.rotate(135)
  flipped = ImageOps.flip(colorImage)
  mirror = ImageOps.mirror(colorImage)
  
  
  rotated.save(os.path.splitext(file_name)[0]+"_1"+os.path.splitext(file_name)[1]) 
  transposed.save(os.path.splitext(file_name)[0]+"_2"+os.path.splitext(file_name)[1]) 
  rotated_1.save(os.path.splitext(file_name)[0]+"_3"+os.path.splitext(file_name)[1]) 
  flipped.save(os.path.splitext(file_name)[0]+"_4"+os.path.splitext(file_name)[1]) 
  mirror.save(os.path.splitext(file_name)[0]+"_5"+os.path.splitext(file_name)[1]) 

  
def save(im, fp, filename):

    try:
        if im.mode != "RGB":
            im = im.convert("RGB")
        rawmode = RAWMODE[im.mode]
    except KeyError:
        raise IOError("TRIGGER cannot write mode %s as JPEG" % im.mode)

    try:
        info = im.encoderinfo
    except AttributeError:
        info = im.info