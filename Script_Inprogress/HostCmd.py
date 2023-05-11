try:
    import codecs
    import pandas as pd
    import os
    import time
    import subprocess
    import logging
    import sys
    import traceback

    try:
        from tkinter import messagebox as mb
        import tkinter as tk
    except:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tk'])
        from tkinter import messagebox as mb
        import tkinter as tk

    from os.path import dirname, join, abspath
    working_folder = abspath(join(dirname(__file__), '..'))
    sys.path.insert(0, working_folder)  

    from Actions.Log import *
    import Actions.Comport as Comport
    from Actions.Config import Config


    log_file_name = CreateLog(test_name = "HostCMD", working_folder = working_folder)

    def get_substring(source,start,stop):
        tmp = source
        result = []
        while (start in tmp) and (stop in tmp):
            start_position = tmp.find(start)
            stop_position = tmp.find(stop)
            result.append(tmp[start_position+len(start) : stop_position])
            tmp = tmp[stop_position+len(stop) :]
        return result


    def get_parameter(source):
        parameter_list =  get_substring(source=source,start="\\x02",stop="\\x03")
        parameter_dict = {}
        for x in parameter_list:
            parameter_dict[x[0]] = x[1:]
        return parameter_dict


    def str_to_hex(string):
        result = codecs.encode(bytes(string,"utf-8"),"hex").upper()
        return str(result).removeprefix("b'").removesuffix("'")


    # Get Interface
    WriteLog("Interface (STD / WN / OPOS / COM): ")
    interface = input().upper()
    WriteLog(interface, print_log = False)

    while interface not in ["STD","WN","OPOS","COM"]:
        WriteLog("Invalid interface")
        WriteLog("Interface (STD / WN / OPOS / COM): ")
        interface = input().upper()
        WriteLog(interface, print_log = False)
    device_comport = Comport.INTERFACE_SETTING[interface]['port']
    print(device_comport)

    device = None
    try:
        device = Comport.CreateComport(port=device_comport)
        device.apply_settings(Comport.INTERFACE_SETTING[interface])

        # device = Comport.CreateComport(port=device_comport)
        # device.apply_settings(Comport.INTERFACE_DEFAULT_SETTING[interface])
        WriteLog("Connect COMPORT Succeed")
    except:
        WriteLog("Connect COMPORT Failed")
        while True:
            pass

    if device:
        device.close()
        device.open()


        # Interfaces's default setting
        Information = Config(working_folder + "\\Configuration\Information.txt")
        Information.LoadIntoDictionary()


        #Read expected indentification information
        # identification = pd.read_excel(os.getcwd() + "\\Identification.xlsx",index_col="Parameter")
        # application = str(identification["Value"]["Application"])
        # bootloader  = str(identification["Value"]["Bootloader"])
        # ec_level = str(identification["Value"]["EC Level"]).zfill(4)
        # configuration_id = str(identification["Value"]["Configuration File ID"])
        # interface = str(identification["Value"]["Interface"]).zfill(2)
        # model_number =  str(identification["Value"]["Model Number"])
        # mainboard_serial_number = str(identification["Value"]["Main Board Serial Number"])
        # serial_number = str(identification["Value"]["Serial Number"])

        Information_dict = Information.ReadProperty("Information")
        # print(Information_dict)
        
        device.entersp()
        device.send_command("$NS" + str_to_hex(str(Information_dict["S"])))
        time.sleep(5)
        device.send_command("$NB" + str_to_hex(str(Information_dict["m"])))
        time.sleep(5)
        device.send_command("$NM" + str_to_hex(str(Information_dict["M"])))
        time.sleep(5)
        device.send_command("$YF" + str_to_hex(str(Information_dict["C"])))
        time.sleep(5)
        # # device.send_command("CABCEFG")
        # device_statistic = device.check_statistic()
        # # print(device_statistic["WHH"])
        # # print(device_statistic["LB"])
        device.save_and_reset()


        information = device.send_command("i")
        # print(information)
        information_paremeters = get_parameter(information)
        print("\n",information_paremeters,"\n")

        if information_paremeters["A"] != Information_dict["A"]:
            WriteLog("APPLICATION UNMATCH")
        if information_paremeters["B"] != Information_dict["B"]:
            WriteLog("BOOTLOADER UNMATCH")
        if information_paremeters["R"] != Information_dict["R"]:
            WriteLog("EC LEVEL UNMATCH")
        if information_paremeters["S"] != Information_dict["S"]:
            WriteLog("SERIAL NUMBER UNMATCH")
        if information_paremeters["M"] != Information_dict["M"]:
            WriteLog("MODEL NUMBER UNMATCH")
        if information_paremeters["m"] != Information_dict["m"]:
            WriteLog("MAIN BOARD SERIAL NUMBER UNMATCH")
        if information_paremeters["C"] != Information_dict["C"]:
            WriteLog("CONFIGURATION FILE ID UNMATCH")
        if information_paremeters["I"] != Information_dict["I"]:
            WriteLog("INTERFACE UNMATCH")
except Exception as e:
    print(traceback.format_exc())
    while True:
        pass