try:    
    import traceback
    import logging
    import os
    import sys
    from os.path import dirname, join, abspath
    working_folder = abspath(join(dirname(__file__), '..'))
    sys.path.insert(0, working_folder)  

    from Actions.Log import *
    import Actions.Comport as Comport
    from Actions.GenerateBarcode import *
    

    log_file_name = CreateLog(test_name = "AT_IF_RS232Properties", working_folder = working_folder)

    def compare_data(data):
        expected_data = "123456789012"
        if interface == "WN":
            expected_data = "A0" + expected_data
        elif interface == "OPOS":
            expected_data = "C" + expected_data
        if data == expected_data:
            return True
        else:
            return False

    

    # Enter interface and check is it valid 
    # INTERFACE_LIST = ('STD', 'WN', 'OPOS', 'ALL')
    # correct_interface_flag = False
    # while not correct_interface_flag:
    #     WriteLog("Enter interface (STD / WN / OPOS / ALL)")
    #     interface = str(input()).upper()
    #     WriteLog("Entered: " + interface)
    #     if interface in INTERFACE_LIST:
    #         correct_interface_flag = True
    #     else:
    #         WriteLog("Invalid interface")

    # device = None
    # if interface == "ALL":
    #     INTERFACE_LIST = INTERFACE_LIST[0:3]
    # else:
    #     INTERFACE_LIST = (interface,'')

    # print(INTERFACE_LIST)

    # for interface in INTERFACE_LIST:
    #     if interface != '':
            # Connect COM port
    try:
        device = Comport.CreateComport(port=Comport.INTERFACE_SETTING["COM"]["port"],rtscts=False)
        device.apply_settings(Comport.INTERFACE_SETTING["COM"])
        # print(device.get_settings())
        WriteLog("Open Comport successfully")
    except:
        WriteLog("Open Comport failed")
        print(traceback.format_exc())
        while True:
            pass
    
    # # device.search_port()
    if device:
    #     # Read and compare the result with expected result fucntion
        # def read_and_compare_result():
        #     result = False
        #     for y in range(3):
        #         WriteLog("Read time: " + str(y+1))
        #         device.clear_buffer()
        #         received_data = device.read_label()
        #         # WriteLog("Received data: " + received_data)
        #         if compare_data(received_data):
        #             WriteLog("Compare data: Match")
        #             result = True
        #             break
        #         else:
        #             WriteLog("Compare data: Not Match")
            
    #         if result:
    #             WriteLog("Result : PASSED", log_level=logging.INFO)
    #         else:
    #             WriteLog("Result : FAILED", log_level=logging.INFO)
    #         return result

        # Open port
        device.close()
        device.open()

        scanner_baudrate = device.baudrate
        scanner_parity = device.parity
        scanner_stopbits = device.stopbits
        scanner_bytesize = device.bytesize
        
        ShowProgrammingLabel("$P,AE," + Comport.INTERFACE_CONFIGURATION["COM"] + ",CR2HC01,P",resize_scale=1.2)
       

        # ShowProgrammingLabel("$P,AS,P")
        device.rts = False
        WriteLog("Set RTS to LOW")
        temp = ShowLabel("123456789012","upca",function = device.read_label)
        if temp["result"] == "":
            print(True)
        else:
            print("False")

        device.rts = True
        WriteLog("Set RTS to HIGH")
        temp = device.read_label()
        if temp != "":
            print("True")
        else:
            print("False")
        # ShowLabel("123456789012","ean13",function = device.read_label)
        # device.read_label()
    # ParseLog(log_file_name)
    WriteLog("FINISHED")
    while True:
        pass
            
except Exception as e:
    print(traceback.format_exc())
    while True:
        pass

