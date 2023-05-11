try:    
    import traceback
    import sys
    from os.path import dirname, join, abspath
    working_folder = abspath(join(dirname(__file__), '..'))
    sys.path.insert(0, working_folder)  

    from Actions.Log import *

    log_file_name = str(input("Log file name: "))
    ParseLog(working_folder +"\\Log\\" + log_file_name)
    print("FINISHED")
    while True:
        pass
except Exception as e:
    print(traceback.format_exc())
    while True:
        pass