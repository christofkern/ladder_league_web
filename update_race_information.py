from googleapiclient.discovery import build
from get_google_credentials import get_credentials
from get_final_time import format_milliseconds


def write_sob(spreadsheet_id, index, value):
    RANGE_NAME = f'Runners!Q{int(index)+2}'  # Specify the cell to write to

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

def write_sob_by_rungg(spreadsheet_id, rungg, value):
    FIND_INDEX_RANGE= 'RUNNERS!E2:E4'
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    runners_result = service.values().get(spreadsheetId=spreadsheet_id,
                                range=FIND_INDEX_RANGE).execute()
    #print(runners_result)
    runners = runners_result.get('values', [])[0]
    
    for idx, runner in enumerate(runners):
        if runner == rungg:
            index = idx
            break

    RANGE_NAME = f'Runners!Q{int(index)+2}'  # Specify the cell to write to

  

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

def write_bpt(spreadsheet_id, index, value):
    RANGE_NAME = f'Runners!R{int(index)+2}'  # Specify the cell to write to

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

def write_delta_times(spreadsheet_id, delta_times):
    RANGE_NAME = 'Runners!S2:S4'
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    delta_values = [[delta] for delta in delta_times[:3]]

    # Prepare the request body
    request_body = {'values': delta_values}

    # Call the Sheets API to update the cell value
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=request_body
    ).execute()
    
def write_final_time(spreadsheet_id, index, value, seed, position, tournamen_record):
    RANGE_NAME = f'Runners!T{int(index)+2}'  # Specify the cell to write to
    print(format_milliseconds(value))
    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    # Prepare the request body
    request_body = {
        'values': [[format_milliseconds(value)]]  # Provide the value to be written in a 2D array
    }
    #print(spreadsheet_id)
    #print(value)
    # Call the Sheets API to update the cell value
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=RANGE_NAME,
        valueInputOption='RAW',
        body=request_body
    ).execute()

    return

    #skip for now
    #update in LL database
    spreadsheet_id = "1i4DUK9SuWknyS1QW2MXGchRZ4s1cu44CSrNRUP03tvY"
    RANGE_NAME = RANGE_NAME = f'Runners!I{int(seed)+1}'

    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    #Retrieve current value from the spreadsheet
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=RANGE_NAME).execute()
    current_value = result.get('values', [])[0][0]

    #append new_time
    if not current_value:
        current_value = [value]  # If no current value, set it to the new time
    else:
        current_value = current_value[:-1] + value + current_value[-1]

    # Prepare the update request
    body = {
        'values': [[current_value]]
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=RANGE_NAME,
        valueInputOption='RAW', body=body).execute()

    #write w-n-l
    records = tournamen_record.split('-')
    records[position - 1] = str(int(records [position - 1]) + 1)

    RANGE_NAME = RANGE_NAME = f'Runners!J{int(seed)+1}'

    record_string = '-'.join(records)

    body = {
        'values': [[record_string]]
        }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=RANGE_NAME,
        valueInputOption='RAW', body=body).execute()

    