from googleapiclient.discovery import build
from get_google_credentials import get_credentials


def write_sob(spreadsheet_id, index, value):
    RANGE_NAME = f'Runners!Q{index+2}'  # Specify the cell to write to

    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    # Prepare the request body
    request_body = {
        'values': [[value]]  # Provide the value to be written in a 2D array
    }

    # Call the Sheets API to update the cell value
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=request_body
    ).execute()

    