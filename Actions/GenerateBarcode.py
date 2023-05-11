import subprocess
import sys
import os
from os import path
from os.path import dirname, join, abspath
from datetime import datetime
import logging
from random import *
import string
working_folder = abspath(join(dirname(__file__), '..'))
sys.path.insert(0,working_folder)  

# Import treepoem package
try:
    import treepoem
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'treepoem'])
    import treepoem

# Import Pillow package
try:
    from PIL import Image, ImageDraw, ImageFilter
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
    from PIL import Image, ImageDraw, ImageFilter
# Set log level of PIL higher DEBUG level to prevent unnecessary log
logging.getLogger('PIL').setLevel(logging.CRITICAL)

# Import opencv package
try:
    import cv2
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'opencv-python'])
    import cv2
import time

from Actions.Log import *
from Actions.Config import Config

# Check Label folder exist, create new Label folder if not exist
label_folder = working_folder + "\\Label"
if not path.exists(label_folder):
    os.mkdir(label_folder)

# Check today Label folder exist, create new folder if not exist
today = datetime.now().strftime("%d-%m-%Y")
today_label_folder = label_folder + "\\" + today +"\\"
if not path.exists(today_label_folder):
    os.mkdir(today_label_folder)

#====================GENERATE LABEL====================
# Add Quiet Zone to the barcode
def AddQuietZone(image_path,width=50,height=50):
    image = Image.open(image_path)
    # Default width and height of the white background
    background_width = 500
    background_height = 200

    # Expand the size of the white background if the barcode is too large
    if background_width - image.width < width*2:
        background_width = image.width + width*2
    if background_height - image.height < height*2:
        background_height = image.height + height*2
    
    # Align the image so that the barcode is in the center of the white background
    background = Image.new("L", (background_width, background_height), 255)
    background.paste(image,(((background_width - image.width) // 2), ((background_height - image.height) // 2)))
    background.save(image_path)


# Generate a barcode
def GenerateLabel(data,barcode_type):
    data = str(data)
    label = treepoem.generate_barcode(barcode_type=barcode_type,
                                        data=data, 
                                        options={"parsefnc": True,
                                                "includetext":True,
                                                })
    # Save the barcode with
    current_time = datetime.now().strftime("%H-%M-%S")
    image_path = today_label_folder + current_time + ".jpg"
    label.convert("1").save(image_path)
    # Add the Quiet Zone to the barcode
    AddQuietZone(image_path)
    return {"path":image_path,"label_data":data}


# Generate a C128 barcode with random data
def GenerateRandomDataLabel(length):
    data = ''.join(choice(string.ascii_letters + string.digits) for i in range(length))
    image_path = GenerateLabel(data=data, barcode_type="code128")["path"]
    return {"path":image_path,"label_data":data}


# Generate a Programming Label
def GenerateProgrammingLabel(data):
    data = "^FNC3" + data + "\x0d"
    image_path = GenerateLabel(data=data, barcode_type="code128")["path"]
    return {"path":image_path,"label_data":data}


displayInfo = Config(working_folder + "\\Configuration\Setting.txt")
displayInfo.LoadIntoDictionary()
display_section = displayInfo.ReadProperty("Display")
display_device = display_section["display_device"].upper()
#====================DISPLAY PC====================
if display_device == "PC":
    RESIZE_SCALE = float(display_section["PC_label_scale"])
    # Generate and display the label
    def ShowLabel(data, barcode_type):
        # Generate, resize and display the label
        tmp = GenerateLabel(data=data, barcode_type=barcode_type)
        image_path = tmp['path']
        data = tmp['label_data']
        image = cv2.imread(image_path)
        img_resized = cv2.resize(image, (0,0), fx=RESIZE_SCALE, fy=RESIZE_SCALE)
        cv2.imshow('Display Image', img_resized)
        WriteLog("Display Label: " + str(data))
        WriteLog("Label Type: " + barcode_type.upper())
        cv2.waitKey(1)
        return {"path":image_path,"label_data":data}


    # Generate and show the C128 barcode with random data
    def ShowRandomDataLabel(length=5):
        # Generate, resize and display the label
        tmp = GenerateRandomDataLabel(length)
        image_path = tmp['path']
        data = tmp['label_data']
        image = cv2.imread(image_path)
        img_resized = cv2.resize(image, (0,0), fx=RESIZE_SCALE, fy=RESIZE_SCALE)
        cv2.imshow('Display Image', img_resized)
        WriteLog("Display Label: " + str(data))
        WriteLog("Label Type: " + "code128".upper())
        cv2.waitKey(1)

        return {"path":image_path,"label_data":data}


    # Generate and show the Programming Label
    def ShowProgrammingLabel(data):
        # Generate, resize and display the label
        image_path = GenerateProgrammingLabel(data=data)["path"]
        image = cv2.imread(image_path)
        img_resized = cv2.resize(image, (0,0), fx=RESIZE_SCALE, fy=RESIZE_SCALE)
        cv2.imshow('Display Image', img_resized)
        WriteLog("Display Label: " + str(data))
        WriteLog("Label Type: " + "PROGRAMMING")
        cv2.waitKey(10000)
        cv2.destroyAllWindows()
        # Delete the label
        # os.remove(image_path)
        return {"path":image_path,"label_data":data}
    
    def ClearDisplay():
        cv2.destroyAllWindows()

#====================DISPLAY EINK====================
elif display_device == "EINK":
    from eink import *

    def clearEink():
        try:
            Sys_info = SystemInfo()
            IT8951_Cmd_SysInfo(Sys_info)

            # Get Eink size
            gulPanelW = Sys_info.uiWidth
            gulPanelH = Sys_info.uiHeight

            # set full white
            srcW = b"\xFF" * (gulPanelW*gulPanelH)
            IT8951_Cmd_LoadImageArea(srcW, (Sys_info.uiImageBufBase), 0, 0, gulPanelW, gulPanelH, gulPanelW, gulPanelH)
            IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)
        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)


    def loadEink(image_path, resize_scale):
        try: 
            Sys_info = SystemInfo()
            IT8951_Cmd_SysInfo(Sys_info)

            # Get Eink size
            gulPanelW = Sys_info.uiWidth
            gulPanelH = Sys_info.uiHeight
            # print(str(gulPanelW) + " - " + str(gulPanelH))
            # initialize
            # IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)

            # set full white
            srcW = b"\xFF" * (gulPanelW*gulPanelH)
            IT8951_Cmd_LoadImageArea(srcW, (Sys_info.uiImageBufBase), 0, 0, gulPanelW, gulPanelH, gulPanelW, gulPanelH)
            IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)
            
            # open image and convert to image compatible with device
            im = Image.open(image_path) # Replace with greyscale image you would like to load onto the display
            imresized = im.resize((int(im.width*resize_scale), int(im.height*resize_scale)))
            imstr = imresized.tobytes()

            imwidth = imresized.width
            imheight = imresized.height
            # load in image
            # [Nam Nguyen, 18-Oct-2019] Currently use coordinate 600, 300.
            IT8951_Cmd_LoadImageArea(imstr, (Sys_info.uiImageBufBase), (gulPanelW - imwidth)//2, (gulPanelH - imheight)//2, imresized.width, imresized.height, gulPanelW, gulPanelH)

            # # display loaded image
            IT8951_Cmd_DisplayArea(0, 0, gulPanelW, gulPanelH, 2, (Sys_info.uiImageBufBase), 1)
            IT8951_CloseDevice()

        except:
            err = str(sys.exc_info()[1]).replace("\n", "")
            logging.warning(err)


    RESIZE_SCALE = float(display_section["eink_label_scale"])

    def ShowLabel(data, barcode_type):
        # Generate, resize and display the label
        tmp = GenerateLabel(data=data, barcode_type=barcode_type)
        image_path = tmp['path']
        data = tmp['label_data']

        loadEink(image_path, RESIZE_SCALE)

        WriteLog("Display Label: " + str(data))
        WriteLog("Label Type: " + barcode_type.upper())

        return {"path":image_path,"label_data":data}

    # Generate and show the C128 barcode with random data
    def ShowRandomDataLabel(length=5):
        # Generate, resize and display the label
        tmp = GenerateRandomDataLabel(length)
        image_path = tmp['path']
        data = tmp['label_data']

        loadEink(image_path, RESIZE_SCALE)

        WriteLog("Display Label: " + str(data))
        WriteLog("Label Type: " + "code128".upper())

        return {"path":image_path,"label_data":data}


    # Generate and show the Programming Label
    def ShowProgrammingLabel(data):
        # Generate, resize and display the label
        image_path = GenerateProgrammingLabel(data=data)["path"]
        WriteLog("Display Label: " + str(data))
        WriteLog("Label Type: " + "PROGRAMMING")

        loadEink(image_path, RESIZE_SCALE)
        time.sleep(10)
        clearEink()

        # Delete the label
        os.remove(image_path)
        return {"path":image_path,"label_data":data}

    def ClearDisplay():
        clearEink()
# for x in range(5):
# while True:
#     a = ShowRandomDataLabelPC(randint(5,15),resize_scale=2)
#     print(a["label_data"])
# ShowLabelEink(123456789012,"upca",resize_scale=1)
# ShowLabel("aahbdkhbaskdbakjdajkc","datamatrix")
# ShowProgrammingLabelEink("$P,AE,HA47,CSNRM03,P",resize_scale=2)


