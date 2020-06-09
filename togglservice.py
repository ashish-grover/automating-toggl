import os
import time
from toggl.TogglPy import Toggl

##project pid for General - Internal Meeting
toggl_pid = 1651809

toggl = Toggl()
toggl.setAPIKey(os.environ['TOGGL_TOKEN'])

def startTimeEntry(event_summary):
    toggl.startTimeEntry(event_summary, toggl_pid)