import datetime
## Logger service.

LOGSUFFIX = datetime.datetime.now()

def logMessage(message):
    with open('C:\\Users\\agrover\\pythonprojects\\Toggl\\log.txt', 'a', encoding = 'utf-8') as f:
        f.write(str(LOGSUFFIX) + ": " + message + '\n')

    f.close()
