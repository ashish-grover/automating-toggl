from __future__ import print_function
import sys
import os
import datetime
import pytz
import pickle
import os.path
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from togglservice import startTimeEntry

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

#Event should be within this time before triggering Toggl
THRESHOLDTIME = 5

def googleCalendarAPISetup():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'googlecalendarapicredentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)

def googleCalendarAPITrigger(service):
    now = datetime.datetime.utcnow().isoformat() + "Z" # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=1, singleEvents=True,
                                        orderBy='startTime').execute()
    return events_result.get('items', [])

def validateStartOfEvent(events):
    for event in events:
        ##start comes in the following format: "%Y-%m-%dT%H:%M:%S%z"
        ##example: 2020-06-08T10:00:00-04:00
        event_start = event['start'].get('dateTime', event['start'].get('date'))
        local_utc = datetime.datetime.now(datetime.timezone.utc) # UTC time
        local_time = local_utc.astimezone().strftime("%Y-%m-%dT%H:%M:%S%z") # local time

        ##dates suck.  convert to a string first (above) then convert back to object (below).        

        start_formatted = datetime.datetime.strptime(event_start, "%Y-%m-%dT%H:%M:%S%z")
        now_formatted = datetime.datetime.strptime(local_time, "%Y-%m-%dT%H:%M:%S%z")
        if (start_formatted < now_formatted + datetime.timedelta(minutes=THRESHOLDTIME)):
            validateAgainstRunningEvent(event)
            writeEventIdToFile(event['id'])
        else:
            print('No upcoming events within the next ' + str(THRESHOLDTIME) + ' mins found.')

def validateAgainstRunningEvent(event):
    # Grab the id of the event and check if its already been tagged.
    api_event_id = event['id']
    api_event_summary = event['summary']
    
    file_event_id = readEventIdFromFile()

    # Check if both the api_event_id and file_event_id are the same.
    # If they are, then skip this event.  If not, then start a new Toggl entry.
    
    print('api_event_id: ' + api_event_id)
    print('api_event_summary: ' + api_event_summary)
    if (api_event_id == file_event_id):
        print('event is already being toggl\'d')
        sys.exit(1)
    else:
        startTimeEntry(api_event_summary)

def readEventIdFromFile():
    json_file = open('calendardata.json', 'r')
    json_file_read = json_file.read()
    json_file.close()

    calendar_data = json.loads(json_file_read)
    return calendar_data['calendar_data']['last_event_id']

def writeEventIdToFile(event_id):
    file_data = {'calendar_data':{'last_event_id':event_id}}

    with open('calendardata.json', 'w', encoding = 'utf-8') as f:
        json.dump(file_data, f, ensure_ascii = False, indent = 4)

    f.close()

def main():
    # Setup the Calendar API
    service = googleCalendarAPISetup()
    
    # Call the Calendar API and get the events
    events = googleCalendarAPITrigger(service)

    # Check for events
    if not events:
        print('No upcoming events found.')
        sys.exit(1)

    # Now that we have an event, validate the start of the event is within the threshold
    validateStartOfEvent(events)

if __name__ == '__main__':
    main()