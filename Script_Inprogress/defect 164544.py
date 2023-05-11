try:    
    import traceback
    import logging
    import os
    import sys
    from os.path import dirname, join, abspath
    import time
    working_folder = abspath(join(dirname(__file__), '..'))
    sys.path.insert(0, working_folder)  

    from Actions.Log import *
    import Actions.Comport as Comport
    from Actions.ConvertStringToByte import *
    

    log_file_name = CreateLog(test_name = "RS232Test", working_folder = working_folder)


    device = None

    #Connect COM port
    try:
        device = Comport.CreateComport(port="COM5")
        device.apply_settings(Comport.INTERFACE_SETTING["COM"])
        WriteLog("Open Comport successfully")
    except:
        WriteLog("Open Comport failed")
        while True:
            pass
    
    device.close()
    device.open()

    disabled_command = str(input("Disable command: "))
    disabled_command = string_to_bytes(disabled_command)
    while len(disabled_command) > 1:
        print("Invalid, should be 1 character: ")
        disabled_command = str(input("Disable command: "))
        disabled_command = string_to_bytes(disabled_command)

    enaable_command = str(input("Enable command: "))
    enaable_command = string_to_bytes(enaable_command)
    while len(enaable_command) > 1:
        print("Invalid, should be 1 character: ")
        enaable_command = str(input("Enable command: "))
        enaable_command = string_to_bytes(enaable_command)


    while True:
        device.send_command(disabled_command,wait_response=False)
        time.sleep(5)
        device.send_command(enaable_command,wait_response=False)
        time.sleep(5)


    # # while True:
    #     # if device.read_label():
    # device.send_command(b"i")
    # # time.sleep(0.1)
    # device.send_command(b"h")
    # # time.sleep(0.1)

except Exception as e:
    print(traceback.format_exc())
    while True:
        pass