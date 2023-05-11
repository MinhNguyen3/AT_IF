import os
import sys
from os.path import dirname, join, abspath

working_folder = abspath(join(dirname(__file__), '..'))
sys.path.insert(0,working_folder)  

from Actions.Config import Config

settingInfo = Config(working_folder + "\\Configuration\Setting.txt")
settingInfo.LoadIntoDictionary()
# print(interfaceInfo)

setting = settingInfo.ReadProperty("Setting")

if setting["display_device"].upper() == "PC":
    label_scale = setting["PC_label_scale"]
elif setting["display_device"].upper() == "EINK":
    label_scale = setting["eink_label_scale"]

print(label_scale)

