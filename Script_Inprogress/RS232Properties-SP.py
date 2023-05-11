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
    

    log_file_name = CreateLog(test_name = "RS232Test", working_folder = working_folder)

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

    # correct_port_flag = False
    # while not correct_port_flag:
    #     WriteLog("Enter COM port (Example: COM1)")
    #     port = str(input())
    #     WriteLog("Entered: " + port)
    #     list_port = serial.tools.list_ports.comports()
    #     list_port_name =[x.name for x in list_port]
    #     if port in list_port_name:
    #         correct_port_flag = True
    #     else:
    #         WriteLog("COM port not available")
    #         if list_port_name == []:
    #             WriteLog("No COM port available")
    #         else:
    #             available_comport = ""
    #             for x in list_port:
    #                 available_comport += "\t" + str(x) + "\n"
    #             WriteLog("Available COMPORT:\n" + available_comport)

    # Enter interface and check is it valid 
    INTERFACE_LIST = ('STD', 'WN', 'OPOS')
    correct_interface_flag = False
    while not correct_interface_flag:
        WriteLog("Enter interface (STD, WN, OPOS)")
        interface = str(input()).upper()
        WriteLog("Entered: " + interface)
        if interface in INTERFACE_LIST:
            correct_interface_flag = True
        else:
            WriteLog("Invalid interface")

    device = None

    #Connect COM port
    try:
        device = Comport.CreateComport(port=Comport.INTERFACE_SETTING[interface]["port"])
        device.apply_settings(Comport.INTERFACE_SETTING[interface])
        WriteLog("Open Comport successfully")
    except:
        WriteLog("Open Comport failed")
        print(traceback.format_exc())
        while True:
            pass
    
    # device.search_port()
    if device:
        def read_and_compare_result():
            result = False
            for y in range(3):
                WriteLog("Read time: " + str(y+1))
                device.clear_buffer()
                received_data = device.read_label()
                # WriteLog("Received data: " + received_data)
                if compare_data(received_data):
                    WriteLog("Compare data: Match")
                    result = True
                    break
                else:
                    WriteLog("Compare data: Unmatch")
            
            if result:
                WriteLog("Result: PASSED", log_level=logging.INFO)
            else:
                WriteLog("Result: FAILED", log_level=logging.INFO)


        device.close()
        device.open()

        scanner_baudrate = device.baudrate
        scanner_parity = device.parity
        scanner_stopbits = device.stopbits
        scanner_bytesize = device.bytesize
        WriteLog("========================================")
        device.entersp()
        device.send_command("$CSNRM03")
        device.send_command("$AS")
        device.save_and_reset()

        os.startfile(working_folder + "\\Label\\UPCA.png")

        
        #Baud rate test
        testcase_name = "Baudrate"
        for x in range(len(Comport.BAUDRATE)):
            # Change baudrate of scanner
            device.change_baudrate(scanner_baudrate)
            scanner_baudrate = Comport.BAUDRATE[x]
            
            WriteLog("========================================")
            WriteLog("TC Name: " + str(testcase_name),log_level=logging.INFO)
            WriteLog("Scenario: " + str(scanner_baudrate),log_level=logging.INFO)

            device.entersp()
            device.send_command("$CR2BA" + str(x).zfill(2))
            # device.apply_and_exit_sp())
            device.save_and_reset()
            device.change_baudrate(scanner_baudrate)

            read_and_compare_result()

        #Clear configuration
        WriteLog("========================================")
        device.restore_factory_default()
        device.apply_settings(Comport.INTERFACE_SETTING[interface])
        device.clear_buffer()

        #Parity Test
        testcase_name = "Parity"
        for x in range(len(Comport.PARITY)):
            # Change baudrate of scanner
            device.change_parity(scanner_parity)
            scanner_parity = Comport.PARITY[x]
            
            WriteLog("========================================")
            WriteLog("TC Name: " + str(testcase_name),log_level=logging.INFO)
            WriteLog("Scenario: " + str(Comport.PARITY_NAMES[scanner_parity]),log_level=logging.INFO)

            device.entersp()
            device.send_command("$CR2PA" + str(x).zfill(2))
            # device.apply_and_exit_sp())
            device.save_and_reset()
            device.change_parity(scanner_parity)

            read_and_compare_result()
            # print(device.get_settings())

            #Clear configuration
        WriteLog("========================================")
        device.restore_factory_default()
        device.apply_settings(Comport.INTERFACE_SETTING[interface])
        device.clear_buffer()

        # Databits Test
        testcase_name = "Databits"
        for x in range(len(Comport.DATABITS)):
            # Change baudrate of scanner
            device.change_bytesize(scanner_bytesize)
            scanner_bytesize = Comport.DATABITS[x]
            
            WriteLog("========================================")
            WriteLog("TC Name: " + str(testcase_name),log_level=logging.INFO)
            WriteLog("Scenario: " + str(Comport.DATABITS[x]),log_level=logging.INFO)

            device.entersp()
            device.send_command("$CR2DA" + str(x).zfill(2))
            # device.apply_and_exit_sp())
            device.save_and_reset()
            device.change_bytesize(scanner_bytesize)

            read_and_compare_result()
        
        
        #Clear configuration
        WriteLog("========================================")
        device.restore_factory_default()
        device.apply_settings(Comport.INTERFACE_SETTING[interface])
        device.clear_buffer()
        
        # Stopbits Test
        testcase_name = "Stopbits"
        for x in range(len(Comport.STOPBITS)):
            # Change baudrate of scanner
            device.change_stopbits(scanner_stopbits)
            scanner_stopbits = Comport.STOPBITS[x]
            
            WriteLog("========================================")
            WriteLog("TC Name: " + str(testcase_name),log_level=logging.INFO)
            WriteLog("Scenario: " + str(Comport.STOPBITS[x]),log_level=logging.INFO)

            device.entersp()
            device.send_command("$CR2ST" + str(x).zfill(2))
            # device.apply_and_exit_sp())
            device.save_and_reset()
            device.change_stopbits(scanner_stopbits)

            read_and_compare_result()
        device.clear_buffer()
        device.close()
        ParseLog(log_file_name)
        WriteLog("FINISHED")
    while True:
        pass
            
except Exception as e:
    print(traceback.format_exc())
    while True:
        pass

