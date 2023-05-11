try:
    import time
    import os
    import subprocess
    import logging
    import os
    import sys
    import traceback
    from random import *
    from os.path import dirname, join, abspath
    working_folder = abspath(join(dirname(__file__), '..'))
    sys.path.insert(0, working_folder)  

    from Actions.GenerateBarcode import *
    from Actions.Log import *
    import Actions.Comport as Comport
    

    import serial.tools.list_ports

    log_file_name = CreateLog(test_name = "AT_IF_InterCharacterDelay_RS232", working_folder = working_folder)
    
    # correct_display_flag = False
    # while not correct_display_flag:
    #     WriteLog("Display device (PC/EINK):")
    #     display_device = input().upper()
    #     WriteLog(str(display_device))
    #     if display_device in ("PC","EINK"):
    #         correct_display_flag = True
    #     else:
    #         WriteLog("Invalid display device")

    INTERFACE_LIST = ("STD","WN","OPOS")
    # INTERFACE_LIST = ("WN","OPOS")
    device_comport = Comport.INTERFACE_SETTING["STD"]['port']
    try:
        scanner = Comport.CreateComport(port=device_comport)
        scanner.apply_settings(Comport.INTERFACE_SETTING["STD"])
        WriteLog("Open scanner Comport successfully")
    except:
        WriteLog("Open scanner Comport failed")
        while True:
            pass

    if scanner:
        # If comport opened, close
        if scanner.is_open:
            scanner.close()
        scanner.open()

    number = 0
    for interface in INTERFACE_LIST:
        prefix = ""
        if interface == "WN":
            prefix = "K"
        elif interface == "OPOS":
            prefix = "T"

        ShowProgrammingLabel("$P,AE," + Comport.INTERFACE_CONFIGURATION[interface] + ",CSNRM03,P")

        scanner.apply_settings(Comport.INTERFACE_SETTING[interface])
        for x in range(5):
            WriteLog("==================================================")
            delay_time = randint(5,99)
            configuration_value = hex(delay_time).removeprefix("0x").zfill(2).upper()

            ShowProgrammingLabel("$P,CR2IC" + configuration_value + ",P")

            number = number + 1
            WriteLog("No : " + str(number),log_level=logging.INFO)
            WriteLog("Interface : " + interface,log_level=logging.INFO)
            WriteLog("Configuration : R2IC" + str(configuration_value),log_level=logging.INFO)


            label = ShowRandomDataLabel(randint(5,15))

            result = scanner.read_and_measure_reading_time()
            delay_time_result = False
            data_result = False

            WriteLog("Expected Data : " + prefix + label["label_data"],log_level=logging.INFO)
            WriteLog("Actual Data : " + result["received_data"],log_level=logging.INFO)
            if (prefix + label["label_data"]) == result["received_data"]:
                WriteLog("Data Result : PASSED",log_level=logging.INFO)
                data_result = True
            else:
                WriteLog("Data Result : FAILED",log_level=logging.INFO)
                data_result = False


            WriteLog("Expected Delay : " + str(delay_time*10) + " ms", log_level=logging.INFO)
            WriteLog("Actual Delay : " + str(result["average_time"]) + " ms", log_level=logging.INFO)
            if result["average_time"] in range((delay_time-1)*10,(delay_time+1)*10):
                WriteLog("Delay Time Result : PASSED",log_level=logging.INFO)
                delay_time_result = True
            else:
                WriteLog("Delay Time Result : FAILED",log_level=logging.INFO)
                delay_time_result = False

            if data_result and delay_time_result:
                WriteLog("Final Result : PASSED",log_level=logging.INFO)
                os.remove(label["path"])
                WriteLog("Image Location : ",log_level=logging.INFO)
            else:
                WriteLog("Final Result : FAILED",log_level=logging.INFO)
                WriteLog("Image Location : " + str(label["path"]),log_level=logging.INFO)
        
    ParseLog(log_file_name)
    WriteLog("FINISHED")
    while True:
        pass
except Exception as e:
    print(traceback.format_exc())
    while True:
        pass