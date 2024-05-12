from googleapiclient.discovery import build
from get_google_credentials import get_credentials


def get_race_information(spreadsheet_id):
    RACE_RANGE_NAME = 'Race!A2:G2'
    RUNNERS_RANGE_NAME = 'Runners!A2:Z5'

    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    race_sheet = service.spreadsheets()
    if (spreadsheet_id == ''):
        return None,None 
    race_result = race_sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=RACE_RANGE_NAME).execute()
    race_values = race_result.get('values', [])

    runners_result = race_sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=RUNNERS_RANGE_NAME).execute()
    runners_values = runners_result.get('values', [])

    #print(race_values)
    #print(runners_values)

    return race_values[0], runners_values
