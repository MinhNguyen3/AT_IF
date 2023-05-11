import os
import subprocess
import sys
# import serial
try:
    import serial
    from serial.serialutil import *
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyserial'])
    import serial
    from serial.serialutil import *

import time
import logging


from os.path import dirname, join, abspath

working_folder = abspath(join(dirname(__file__), '..'))
sys.path.insert(0,working_folder)  

from Actions.Config import Config
from Actions.Log import *
from Actions.GenerateBarcode import *
# from Config import Config
# from Log import *




BAUDRATE = (1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200)
PARITY = (PARITY_NONE, PARITY_EVEN, PARITY_ODD)
PARITY_NAMES = {
    PARITY_NONE: 'None',
    PARITY_EVEN: 'Even',
    PARITY_ODD: 'Odd',
}
DATABITS = (SEVENBITS, EIGHTBITS)
STOPBITS = (STOPBITS_ONE, STOPBITS_TWO)



# Interfaces's default setting
interfaceInfo = Config(working_folder + "\\Configuration\Setting.txt")
interfaceInfo.LoadIntoDictionary()
# print(interfaceInfo)

RS232_STD = interfaceInfo.ReadProperty("RS232-STD")
# print(RS232_STD)
RS232_WN = interfaceInfo.ReadProperty("RS232-WN")
# print(RS232_WN)
RS232_OPOS = interfaceInfo.ReadProperty("RS232-OPOS")
# print(RS232_OPOS)
SERVICE_PORT = interfaceInfo.ReadProperty("SERVICEPORT-RS232")
USBCOM = interfaceInfo.ReadProperty("USBCOM")
GUN_WIRELESS = interfaceInfo.ReadProperty("WIRELESS-GUN")
TIMEOUT = interfaceInfo.ReadProperty("Timeout")

SEND_COMMAND_TIMEOUT = float(TIMEOUT["write_timeout"])
GET_RESPONSE_TIMEOUT = float(TIMEOUT["read_timeout"])


# print(type(RS232_OPOS["bytesize"]))
# RS232_STD =  {'baudrate': 9600,
#                       'bytesize': EIGHTBITS,
#                       'parity': PARITY_NONE,
#                       'stopbits': STOPBITS_ONE}

# RS232_WN =   {'baudrate': 9600,
#                       'bytesize': EIGHTBITS,
#                       'parity': PARITY_ODD,
#                       'stopbits': STOPBITS_ONE}

# RS232_OPOS = {'baudrate': 115200,
#                       'bytesize': EIGHTBITS,
#                       'parity': PARITY_NONE,
#                       'stopbits': STOPBITS_ONE}

# # Service port setting
# SERVICE_PORT = {'baudrate': 115200,
#                 'bytesize': EIGHTBITS,
#                 'parity': PARITY_NONE,
#                 'stopbits': STOPBITS_ONE}
                    
# Interface's default setting dictionary
INTERFACE_SETTING = {"STD": RS232_STD,
                    "WN": RS232_WN,
                    "OPOS": RS232_OPOS,
                    "COM": USBCOM}

INTERFACE_CONFIGURATION = {"STD":"HA05",
                            "WN":"HA12",
                            "OPOS":"HA13",
                            "COM":"HA47"
                        }

# Create ComPort class that inherited from serial.Serial class
class CreateComport(serial.Serial):
    
    def __init__(self,**kwargs):
        serial.Serial.__init__(self,**kwargs)
        # self.average_time = 0
    
    # Get the response from scanner
    def read_data(self, timeout=GET_RESPONSE_TIMEOUT,return_type = str):
        start_time = time.time()
        data = b""
        while time.time() - start_time < timeout:
            if self.inWaiting():
                while self.inWaiting():
                    data += self.read_all()
                    time.sleep(0.01)
        #Return byte or string
        if return_type == bytes:
            return data
        else:
            data = str(data).removesuffix("'").removeprefix("b'").replace("\\r","\n").replace("\\n","\n").strip()
        return data
    
    
    # Read data until stop_char is received or timeout expired
    def read_data_until(self, timeout=GET_RESPONSE_TIMEOUT,return_type = str, stop_char=b"\r"):
        if type(stop_char) != bytes:
            stop_char = bytes(str(stop_char),"utf-8")

        start_time = time.time()
        data = b""
        while ((time.time() - start_time) < timeout):
            if stop_char not in data:
                if self.in_waiting:
                    data += self.read()
            else:
                break
                # time.sleep(0.01)

        if return_type == bytes:
            return data
        else:
            data = str(data).removesuffix("'").removeprefix("b'").replace("\\r","\n").replace("\\n","\n").strip()
        return data


    # Read data and measure the reading time
    def read_and_measure_reading_time(self, timeout=GET_RESPONSE_TIMEOUT,return_type = str ,stop_char=b"\r"):
        if type(stop_char) != bytes:
            stop_char_byte = bytes(str(stop_char),"utf-8")
        else:
            stop_char_byte = stop_char

        start_time = time.time()
        data = b""

        reading_time = 0
        while ((time.time() - start_time) < timeout):
            if self.in_waiting:
                if reading_time == 0:
                    reading_time = time.time()
                    # Close image immediately when receive data
                    ClearDisplay()
                data += self.read_all()
                if stop_char_byte in data:
                    reading_time = time.time() - reading_time
                    print("Response : " + str(data).removesuffix("'").removeprefix("b'").replace("\\r","\n").replace("\\n","\n").strip())
                    break
                start_time = time.time()
                print("Response : " + str(data).removesuffix("'").removeprefix("b'").replace("\\r","\n").replace("\\n","\n").strip(),end="\r")
                # time.sleep(0.01)
        average_time = 0
        if len(data) > 1:
            average_time = int(reading_time*1000/(len(data)-1))
            # WriteLog("Response : " + str(data).removesuffix("'").removeprefix("b'").replace("\\r","\n").replace("\\n","\n").strip(),print_log=False)
            # WriteLog("Inter Character Delay Time: " + str(average_time)+ " ms")


        if return_type == bytes:
            return {"received_data":data,"stop_char":stop_char_byte,"average_time" : average_time}
        else:
            data = str(data).removesuffix("'").removeprefix("b'").replace("\\r","\n").replace("\\n","\n").strip()
        return {"received_data":data,"stop_char":stop_char,"average_time" : average_time}

    
    def read_label(self, timeout=GET_RESPONSE_TIMEOUT, log_level = logging.DEBUG,stop_char=b"\r"):
        received_data = self.read_data_until(timeout=timeout,stop_char=stop_char)
        WriteLog("Response : " + received_data, log_level)
        return received_data


    #Clear buffer
    def clear_buffer(self):
        self.flush()
        self.flushInput()
        self.flushOutput()
        tmp = self.read_all()


    # Send command to scanner and wait for the scanner response
    def send_command(self, command, timeout=SEND_COMMAND_TIMEOUT, return_type = str, log_level = logging.DEBUG, write_log = True, wait_response = True):
        self.clear_buffer()
        start_time = time.time()

        if type(command) == bytes:
            pass
        else:
            command = bytes(command,"utf-8")


        if write_log:
            WriteLog("Send command: " + str(command).removesuffix("'").removeprefix("b'").replace("\\r","\n").replace("\\n","\n"), log_level)
        response = ""

        # Wait HH response
        if wait_response:
            if b'$' in command:
                while ((time.time() - start_time) < timeout) and (response != '$>') and (response != '$%'):
                    self.write(command + b"\r\n")
                    response = self.read_data(timeout = 1, return_type = return_type)
            else:
                self.write(command + b"\r")
                response = self.read_data(timeout = 1, return_type = return_type)
            if write_log:
                WriteLog("Response : " + str(response).removesuffix("'").removeprefix("b'").replace("\\r","\n").replace("\\n","\n"), log_level)        
            return response
        else:
            self.write(command + b"\r")


    # Send host command
    def send_host_command(self, command, timeout=SEND_COMMAND_TIMEOUT, return_type=str, log_level=logging.DEBUG, write_log=True):
        self.send_command(command=command, timeout=timeout, return_type=return_type, log_level=log_level, write_log=write_log, wait_response=False)
        

    # Enter service port and change baudrate
    def entersp(self,timeout=SEND_COMMAND_TIMEOUT):
        start_time = time.time()
        # Retry to send command if timeout is not expired
        while (time.time() - start_time) < timeout:
            response = self.send_command("$S")
            if response == '$>':
                break
        self.current_setting = self.get_settings()
        self.apply_settings(SERVICE_PORT)
        return response


    # Exit service port
    def exit_sp(self,timeout=SEND_COMMAND_TIMEOUT):
        start_time = time.time()
        # Retry to send command if timeout is not expired
        while (time.time() - start_time) < timeout:
            response = self.send_command("$s")
            if response == '$>':
                break
        self.apply_settings(self.current_setting)
        time.sleep(0.5)
        return response


    # Save configuration to user block and reset the scanner
    def save_and_reset(self,timeout=SEND_COMMAND_TIMEOUT):
        start_time = time.time()
        # Retry to send command if timeout is not expired
        while (time.time() - start_time) < timeout:
            response = self.send_command("$Ar")
            if response == '$>':
                break
        self.apply_settings(self.current_setting)
        time.sleep(10)
        self.clear_buffer()
        return response
    

    # Apply configuration and exit sp, not save to memory
    def apply_and_exit_sp(self,timeout=SEND_COMMAND_TIMEOUT):
        response = self.send_command("$r01")
        start_time = time.time()
        # Retry to send command if timeout is not expired
        while (time.time() - start_time) < timeout:
            response = self.send_command("$r01")
            if response == '$>':
                break
        self.apply_settings(self.current_setting)
        time.sleep(0.5)
        return response  


    # Restore Factory Default
    def restore_factory_default(self,timeout=SEND_COMMAND_TIMEOUT):
        self.entersp()
        start_time = time.time()
        # Retry to send command if timeout is not expired
        while (time.time() - start_time) < timeout:
            response = self.send_command("$HA00")
            if response == '$>':
                break
        self.save_and_reset()
        

    # Get statistic part of the log
    def check_statistic(self, timeout=GET_RESPONSE_TIMEOUT):
        start_time = time.time()
        self.write(bytes("$El\r\n",'utf-8'))
        WriteLog("Send command: $El")
        flag = 0
        data = b""
        while (time.time() - start_time) < timeout:
           
            if self.inWaiting():
                statistic = None
                
                while self.inWaiting():
                    if not flag:
                        data += self.read_until(b"--")
                        if b"--" in data:
                            statistic = data.removesuffix(b"--")
                            flag = 1
                    else:
                        data += self.read_all()
                    time.sleep(0.1)
                data = str(data).removesuffix("'").removeprefix("b'").replace("\\r","\n").replace("\\n","\n")
                WriteLog("Response : " + data)

                if flag:
                    return self.analyze_statistic(statistic)
                else:
                    WriteLog("Response : " + str(data))
                    return ""
        WriteLog("Response : ")
        return ""


    # Change baudrate
    def change_baudrate(self, baudrate = 9600):
        self.baudrate = baudrate
        self.apply_settings(self.get_settings())


    # Change parity
    def change_parity(self, parity = serial.PARITY_NONE):
        self.parity = parity
        self.apply_settings(self.get_settings())


    # Change stop bits
    def change_stopbits(self, stopbits = serial.STOPBITS_TWO):
        self.stopbits = stopbits
        self.apply_settings(self.get_settings())


    # Change byte size
    def change_bytesize(self, bytesize = serial.EIGHTBITS):
        self.bytesize = bytesize
        self.apply_settings(self.get_settings())


    # Analyze the statistic
    def analyze_statistic(self, statistic_data):
    # Remove unneed character in statistic
        statistic_data = statistic_data.replace(b"\r",b"\n")
        splited_statistic = bytes(statistic_data).split(b"\n")
        while b"" in splited_statistic:
            splited_statistic.remove(b'')
        while b"$>" in splited_statistic:
            splited_statistic.remove(b"$>")

        # Seperate the parameter and its value
        for x in range(len(splited_statistic)):
            splited_statistic[x] = splited_statistic[x].split(b" ")

        for x in range(len(splited_statistic)):
            for y in range(len(splited_statistic[x])):
                while  b"" in splited_statistic[x]:
                    splited_statistic[x].remove(b'')
        statistic_dict = {}
        for x in range(len(splited_statistic)):
            statistic_dict[splited_statistic[x][0].decode()] = int(splited_statistic[x][1])
        return(statistic_dict)


    def search_port(self):
        flag = False
        WriteLog("START SEARCHING PORT")
        for x in BAUDRATE:
            for y in PARITY:
                self.change_baudrate(x)
                self.change_parity(y)
                WriteLog("Baudrate: " + str(x) + ", Parity: " + y)
                # print(self.get_settings())
                self.clear_buffer()
                for z in range(2):
                    self.send_command("t",write_log=False)
                    time.sleep(0.5)
                    response = self.read_data(timeout=1,return_type=bytes)
                    # print(response)
                    if response == b" \n\r!\"#$%&\'()*+,-./0123456789:;<=>?@\n\rABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`\n\rabcdefghijklmnopqrstuvwxyz{|}\n\r":
                        flag = True
                        break
                if flag:
                    break
            if flag:
                break
        if flag:
            WriteLog("SEARCHING PORT SUCCEED")
        else:
            WriteLog("SEARCHING PORT FAILED")
        return flag
        