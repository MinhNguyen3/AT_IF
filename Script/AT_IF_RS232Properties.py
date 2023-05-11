try:    
    import traceback
    import logging
    import os
    import sys
    from os.path import dirname, join, abspath
    working_folder = abspath(join(dirname(__file__), '..'))
    sys.path.insert(0, working_folder)  

    from Actions.GenerateBarcode import *
    from Actions.Log import *
    import Actions.Comport as Comport
    
    log_file_name = CreateLog(test_name = "AT_IF_RS232Properties", working_folder = working_folder)

    
    # displayInfo = Config(working_folder + "\\Configuration\Display.txt")
    # displayInfo.LoadIntoDictionary()
    # display_section = displayInfo.ReadProperty("display")
    # display_device = display_section["display_device"].upper()

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
    INTERFACE_LIST = ('STD', 'WN', 'OPOS', 'ALL')
    correct_interface_flag = False
    while not correct_interface_flag:
        WriteLog("Enter interface (STD / WN / OPOS / ALL)")
        interface = str(input()).upper()
        WriteLog(str(interface))
        if interface in INTERFACE_LIST:
            correct_interface_flag = True
        else:
            WriteLog("Invalid interface")

    scanner = None
    if interface == "ALL":
        INTERFACE_LIST = INTERFACE_LIST[0:3]
    else:
        INTERFACE_LIST = (interface,'')


    for interface in INTERFACE_LIST:
        if interface != '':
            # Connect COM port
            try:
                scanner = Comport.CreateComport(port=Comport.INTERFACE_SETTING[interface]["port"])
                scanner.apply_settings(Comport.INTERFACE_SETTING[interface])
                WriteLog("Open Comport successfully")
            except:
                WriteLog("Open Comport failed")
                print(traceback.format_exc())
                while True:
                    pass
            
            # scanner.search_port()
            if scanner:
                # Read and compare the result with expected result fucntion
                def read_and_compare_result():
                    result = False
                    for y in range(3):
                        WriteLog("Read time: " + str(y+1))
                        scanner.clear_buffer()
                        received_data = scanner.read_label()
                        # WriteLog("Received data: " + received_data)
                        if compare_data(received_data):
                            WriteLog("Compare data: Match")
                            result = True
                            break
                        else:
                            WriteLog("Compare data: Not Match")
                    
                    if result:
                        WriteLog("Result : PASSED", log_level=logging.INFO)
                    else:
                        WriteLog("Result : FAILED", log_level=logging.INFO)
                    ClearDisplay()
                    return result

                # def ShowLabel()
                # Open port
                scanner.close()
                scanner.open()

                scanner_baudrate = scanner.baudrate
                scanner_parity = scanner.parity
                scanner_stopbits = scanner.stopbits
                scanner_bytesize = scanner.bytesize
                

                ShowProgrammingLabel("$P,AE," + Comport.INTERFACE_CONFIGURATION[interface] + ",CSNRM03,P")
                ShowProgrammingLabel("$P,AS,P")
                #Baud rate test
                testcase_name = "Baudrate"
                for x in range(len(Comport.BAUDRATE)):
                    # Change baudrate of scanner
                    scanner.change_baudrate(scanner_baudrate)
                    scanner_baudrate = Comport.BAUDRATE[x]
                    
                    WriteLog("========================================")
                    WriteLog("Interface : " + interface,log_level=logging.INFO)
                    WriteLog("TC Name : " + str(testcase_name),log_level=logging.INFO)
                    WriteLog("Scenario : " + str(scanner_baudrate),log_level=logging.INFO)
                    WriteLog("Configuration : R2BA" + str(x).zfill(2),log_level=logging.INFO)

                    ShowProgrammingLabel("$P,CR2BA" + str(x).zfill(2) +",P")
                    scanner.change_baudrate(scanner_baudrate)
                    label = ShowLabel(123456789012,"upca")

                    result = read_and_compare_result()
                    if result:
                        os.remove(label["path"])

                #Clear configuration
                WriteLog("========================================")
                ShowProgrammingLabel("$P,HA00,P")

                scanner.apply_settings(Comport.INTERFACE_SETTING[interface])
                scanner.clear_buffer()

                #Parity Test
                testcase_name = "Parity"
                for x in range(len(Comport.PARITY)):
                    # Change baudrate of scanner
                    scanner.change_parity(scanner_parity)
                    scanner_parity = Comport.PARITY[x]
                    
                    WriteLog("========================================")
                    WriteLog("Interface : " + interface,log_level=logging.INFO)
                    WriteLog("TC Name : " + str(testcase_name),log_level=logging.INFO)
                    WriteLog("Scenario : " + str(Comport.PARITY_NAMES[scanner_parity]),log_level=logging.INFO)
                    WriteLog("Configuration : R2PA" + str(x).zfill(2),log_level=logging.INFO)

                    ShowProgrammingLabel("$P,CR2PA" + str(x).zfill(2) +",P")
                    scanner.change_parity(scanner_parity)
                    label = ShowLabel(123456789012,"upca")

                    result = read_and_compare_result()
                    if result:
                        os.remove(label["path"])

                #Clear configuration
                WriteLog("========================================")
                ShowProgrammingLabel("$P,HA00,P")
                scanner.apply_settings(Comport.INTERFACE_SETTING[interface])
                scanner.clear_buffer()

                # Databits Test
                testcase_name = "Databits"
                for x in range(len(Comport.DATABITS)):
                    # Change baudrate of scanner
                    scanner.change_bytesize(scanner_bytesize)
                    scanner_bytesize = Comport.DATABITS[x]
                    
                    WriteLog("========================================")
                    WriteLog("Interface : " + interface,log_level=logging.INFO)
                    WriteLog("TC Name : " + str(testcase_name),log_level=logging.INFO)
                    WriteLog("Scenario : " + str(Comport.DATABITS[x]),log_level=logging.INFO)
                    WriteLog("Configuration : R2DA" + str(x).zfill(2),log_level=logging.INFO)


                    ShowProgrammingLabel("$P,CR2DA" + str(x).zfill(2) +",P")
                    scanner.change_bytesize(scanner_bytesize)
                    label = ShowLabel(123456789012,"upca")

                    result = read_and_compare_result()
                    if result:
                        os.remove(label["path"])

                #Clear configuration
                WriteLog("========================================")
                ShowProgrammingLabel("$P,HA00,P")
                scanner.apply_settings(Comport.INTERFACE_SETTING[interface])
                scanner.clear_buffer()
                
                # Stopbits Test
                testcase_name = "Stopbits"
                for x in range(len(Comport.STOPBITS)):
                    # Change baudrate of scanner
                    scanner.change_stopbits(scanner_stopbits)
                    scanner_stopbits = Comport.STOPBITS[x]
                    
                    WriteLog("========================================")
                    WriteLog("Interface : " + interface,log_level=logging.INFO)
                    WriteLog("TC Name : " + str(testcase_name),log_level=logging.INFO)
                    WriteLog("Scenario : " + str(Comport.STOPBITS[x]),log_level=logging.INFO)
                    WriteLog("Configuration : R2ST" + str(x).zfill(2),log_level=logging.INFO)

                    ShowProgrammingLabel("$P,CR2ST" + str(x).zfill(2) +",P")
                    scanner.change_stopbits(scanner_stopbits)
                    label = ShowLabel(123456789012,"upca")

                    result = read_and_compare_result()
                    if result:
                        os.remove(label["path"])

                scanner.clear_buffer()
                scanner.close()
    ParseLog(log_file_name)
    WriteLog("FINISHED")
    while True:
        pass
            
except Exception as e:
    print(traceback.format_exc())
    while True:
        pass

