import datetime
import os


## Logger service class.
class Logger():    
    
    def __init__(self):
        if not os.path.isfile('./log.txt'):
            open('./log.txt', 'w').close()

    def logMessage(self, message):
        logSuffix = datetime.datetime.now()
        with open('./log.txt', 'a', encoding = 'utf-8') as f:
            f.write(str(logSuffix) + ": " + message + '\n')

        f.close()
