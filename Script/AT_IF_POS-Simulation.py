try:
    import time
    import os
    import subprocess
    import logging
    import os
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

    import serial.tools.list_ports

    # Create log file
    log_file_name = CreateLog(test_name = "AT_IF_POS-Simulation", working_folder = working_folder)

    # Count variables
    read_count = 0
    not_read_count = 0
    match_count = 0
    not_match_count = 0

    error_flag = False
    wireless = False
    bridge = False

    gun_comport = None
    
    WriteLog("Interface (STD / WN / OPOS / COM): ")
    interface = input().upper()
    WriteLog(interface, print_log = False)

    while interface not in ["STD","WN","OPOS","COM"]:
        WriteLog("Invalid interface")
        WriteLog("Interface (STD / WN / OPOS / COM): ")
        interface = input().upper()
        WriteLog(interface, print_log = False)
    device_comport = Comport.INTERFACE_SETTING[interface]['port']

    WriteLog("Device type (Corded/Wireless): ")
    device_type = input().upper()
    WriteLog(device_type, print_log = False)

    while device_type not in ["CORDED","WIRELESS"]:
        WriteLog("Invalid device type")
        WriteLog("Device type (Corded/Wireless): ")
        device_type = input().upper()
        WriteLog(device_type, print_log = False)

    if device_type == "WIRELESS":
        wireless = True
        WriteLog("Check gun log via (Comport/Bridge): ")
        check_gun_log_via = input().upper()
        WriteLog(check_gun_log_via, print_log = False)

        if check_gun_log_via == "BRIDGE":
            bridge = True

            WriteLog("Enter Bridge Mode command: ")
            bridge_command = input()
            WriteLog(bridge_command, print_log = False)
        elif check_gun_log_via == "COMPORT":
            gun_comport = Comport.GUN_WIRELESS['port']


    list_port = serial.tools.list_ports.comports()
    list_port_name =[x.name for x in list_port]

    if not device_comport in list_port_name:
        WriteLog("WARNING: Device's port not available")
        error_flag = True

    if wireless and not bridge:
        if not gun_comport in list_port_name:
            WriteLog("WARNING: Gun's port not available")
            error_flag = True
        elif gun_comport == device_comport:
            WriteLog("WARNING: Gun's port must be different from Device's port")
            error_flag = True

    if error_flag:
        while True:
            pass

    WriteLog("Running time (minutes): ")
    running_time = input()
    WriteLog(running_time, print_log = False)

    while not running_time.isnumeric():
        WriteLog("WARNING: Invalid running time")
        WriteLog("Running time (minutes): ")
        running_time = input()
        WriteLog(running_time, print_log = False)

    running_time = int(running_time)

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

    def compare_log(log_before_test, log_after_test):
        comparable = False
        reset = False

        if log_before_test and log_after_test:
            comparable = True
            log_during_test = {}
            # corded_base_statistic_during_test_string = ""
            for x in list(log_before_test.keys()):
                log_during_test[x] = log_after_test[x] - log_before_test[x]
                # corded_base_statistic_during_test_string += x + "\t" + str(corded_base_statistic_during_test[x]) + "\n"

            if log_during_test["AR"] or log_during_test["PC"] or log_during_test["HR"] or log_during_test["SR"]:
                reset = True
        return {"comparable": comparable, "reset": reset}

    device = None
    corded_base_reset = False
    corded_base_log_comparable = False

    gun = None
    gun_reset = False
    gun_log_comparable = False

    try:
        device = Comport.CreateComport(port=device_comport)
        device.apply_settings(Comport.INTERFACE_SETTING[interface])
        WriteLog("Open Device Comport successfully")
    except:
        WriteLog("Open Device Comport failed")
        while True:
            pass

    if wireless and not bridge:
        try:
            gun = Comport.CreateComport(port=gun_comport)
            gun.apply_settings(Comport.INTERFACE_SETTING["COM"])
            WriteLog("Open Gun Comport successfully")
        except:
            WriteLog("Open Gun Comport failed")
            while True:
                pass

    if device:
        # If comport opened, close and open again
        if device.is_open:
            device.close()
        device.open()

        device.send_command("$!")
        device.entersp()
        device.send_command("$Er")
        device.send_command("$AR")
        corded_base_statistic_before_test = device.check_statistic()
        if not wireless:
            device.exit_sp()
        elif wireless and bridge:
            root = tk.Tk()
            
            mb.showinfo('', 'Put Gun on Base and click OK to continue')
            root.wm_withdraw()

            device.send_command(bridge_command)
            device.send_command("$!")
            device.send_command("$S")
            device.send_command("$Er")
            device.send_command("$AR")
            gun_statistic_before_test = device.check_statistic()
            device.send_command("$s")
            device.send_command("$ER0")
            device.exit_sp()
        else:
            device.exit_sp()
            gun.send_command("$!")
            gun.entersp()
            gun.send_command("$Er")
            gun.send_command("$AR")
            gun_statistic_before_test = gun.check_statistic()
            gun.send_command("$s")

        device.write(b"E")
        no_label_time = start_test_time = time.time()

        WriteLog("Ready to read label")

        os.startfile(working_folder + "\\Label\\UPCA.png")

        while (time.time() - start_test_time) < (running_time * 60):
            # Disable scanner everytime read label and then enable again
            if device.inWaiting():
                no_label_time = time.time()
                received_data = device.read_label()
                if compare_data(received_data):
                    WriteLog("Compare data: Match")
                    match_count += 1
                else:
                    WriteLog("Compare data: Not Match")
                    not_match_count += 1

                device.write(b"D")
                WriteLog("Send host command D")
                time.sleep(0.1)
                device.write(b"E")
                WriteLog("Send host command E")
                read_count += 1
            # Disabled scanner after 5 seconds not read label
            if time.time() - no_label_time > 5:
                WriteLog("Not read")
                device.write(b"D")
                WriteLog("Send host command D")
                time.sleep(0.1)
                device.write(b"E")
                WriteLog("Send host command E")
                no_label_time = time.time()
                not_read_count +=1

        WriteLog("Testing Timeout")
        device.write(b"D")
        time.sleep(0.1)
        device.send_command("$!")
        device.entersp()
        corded_base_statistic_after_test = device.check_statistic()
        if not wireless:
            device.exit_sp()
        elif wireless and bridge:
            root.wm_deiconify()
            mb.showinfo('', 'Put Gun on Base and click OK to continue')
            root.wm_withdraw()
            device.send_command(bridge_command)
            device.send_command("$!")
            device.send_command("$S")
            gun_statistic_after_test = device.check_statistic()
            device.send_command("$s")
            device.send_command("$ER0")
            device.exit_sp()
        else:
            device.exit_sp()
            gun.send_command("$!")
            gun.send_command("$S")
            gun_statistic_after_test = gun.check_statistic()
            gun.send_command("$s")

        WriteLog("Total labels read: " + str(read_count) + " (Match: " + str(match_count) + " - Not Match: " + str(not_match_count) + ")")
        WriteLog("Not read: " + str(not_read_count))

        compare_corded_base_log = compare_log(corded_base_statistic_before_test, corded_base_statistic_after_test)
        
        if not wireless:
            if not compare_corded_base_log["comparable"]:
                WriteLog("Cannot compare log")
            elif compare_corded_base_log["reset"]:
                WriteLog("WARNING: Reset occured during test")
            else:
                WriteLog("No reset during test")
        else:
            compare_gun_log = compare_log(gun_statistic_before_test, gun_statistic_after_test)
            if not compare_corded_base_log["comparable"]:
                WriteLog("Cannot compare base log")
            elif compare_corded_base_log["reset"]:
                WriteLog("WARNING: Base reset during test")
            else:
                WriteLog("Base not reset during test")

            if not compare_gun_log["comparable"]:
                WriteLog("Cannot compare gun log")
            elif compare_gun_log["reset"]:
                WriteLog("WARNING: Gun reset during test")
            else:
                WriteLog("Gun not reset during test")

        device.write(b"E")
        if not not_match_count:
            WriteLog("Result: PASSED")
        else:
            WriteLog("Result: FAILED")
        WriteLog("FINISHED")
        while True:
            pass
            
except Exception as e:
    print(traceback.format_exc())
    while True:
        pass


    