from googleapiclient.discovery import build
from get_google_credentials import get_credentials

def get_golds(spreadsheet_id, amount_runners):
    RUNNERS_RANGE_NAME = f'Runners!Z2:Z{2+amount_runners}'
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    race_sheet = service.spreadsheets()      

    runners_result = race_sheet.values().get(spreadsheetId=spreadsheet_id,range=RUNNERS_RANGE_NAME).execute()
    golds = [runners_result.get('values', [])[idx][0] for idx in range(amount_runners)]
    return golds