# import pandas as pd
import subprocess
import sys
# import pandas
try:
    import pandas as pd
except:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pandas'])
    import pandas as pd
    
import os
from os import path
from datetime import datetime
import logging


def CreateLog(test_name="", working_folder = os.getcwd()):
    #Check Log folder exist
    log_folder = working_folder+ "\\Log\\"
    # print(log_folder)
    if not path.exists(log_folder):
        os.mkdir(log_folder)

    # Create log file
    log_file_name = log_folder + datetime.today().strftime("%Y%m%d%H%M%S_") + str(test_name) + ".txt"
    logging.basicConfig(filename=log_file_name, 
                        level=logging.DEBUG,
                        format="%(asctime)s\t%(levelname)s\t%(message)s")
    return log_file_name


def ParseLog(log_file_name,skiprows = None):
    log_content = pd.read_csv(log_file_name,
                              sep="\t",
                              header=None, 
                              names=["Time", "Log level", "Content"],
                              skiprows=skiprows)
    # print(log_content)
    #Get content  
    info_content = log_content["Content"][log_content["Log level"]=="INFO"]
    
    #Analyze log file and add to a dictionary
    dictionary = {}
    for x in info_content.index:
        content = str(info_content.loc[x])
        key = content.split(" : ")[0].strip()
        value = content.split(" : ")[1].strip()
        
        if key in dictionary.keys():
            dictionary[key].append(value)
        else:
            dictionary[key] = [value]

    # print(dictionary)
    df = pd.DataFrame()
    # print(dictionary)
    for x in dictionary.keys():
        dictionary_temp = {x : dictionary[x]}
        df_temp = pd.DataFrame(dictionary_temp)
        df = pd.concat([df,df_temp],axis=1)

    df = df.fillna("")
    # print(df)
    analyzed_log_file = open(log_file_name.replace(".txt","") + "_Analyzed.txt","a")

    #Print the header
    for column in df.columns:
        analyzed_log_file.write(str(column) + "\t")
    analyzed_log_file.write("\n")

    #Print the result
    for row in df.index:
        for column in df.columns:
            analyzed_log_file.write(str(df[column][row]) + "\t")
        analyzed_log_file.write("\n")
    analyzed_log_file.close()


def WriteLog(message, log_level = logging.DEBUG, print_log = True):
    if log_level == logging.DEBUG:
        logging.debug(message)
    elif log_level == logging.INFO:
        logging.info(message)
    elif log_level == logging.WARNING:
        logging.warning(message)
    elif log_level == logging.ERROR:
        logging.error(message)
    elif log_level == logging.CRITICAL:
        logging.critical(message)
    if print_log:
        print(message)

# ParseLog(r"C:\Users\mnguyen2\OneDrive\Minh\OneDrive - Datalogic S.p.a\Python\Working\Ver2\Log\20221214142524_InterCharDelay.txt")