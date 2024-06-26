import requests
from googleapiclient.discovery import build
from get_google_credentials import get_credentials
import time
import random

def format_milliseconds(total_milliseconds):
    if isinstance(total_milliseconds, str):
        total_milliseconds = float(total_milliseconds)
    total_seconds = total_milliseconds / 1000  # Convert milliseconds to seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    formatted_time = f"{hours}:{minutes:02}:{seconds:02}"
    return formatted_time

def format_delta(total_milliseconds):
    if isinstance(total_milliseconds, str):
        total_milliseconds = float(total_milliseconds)
    total_seconds = total_milliseconds / 1000  # Convert milliseconds to seconds
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    if (minutes > 0):
        formatted_time = f"+ {minutes}:{seconds:02}"
    else:
        formatted_time = f"+ {seconds}"
    return formatted_time

def parse_time_to_milliseconds(formatted_time):
    formatted_time = str(formatted_time)
    if (formatted_time == ''):
        return 1e8
    hours, minutes, seconds = map(int, formatted_time.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    total_milliseconds = total_seconds * 1000
    return total_milliseconds

def calculate_average_time(all_times):
    total_milliseconds = sum(all_times)
    average_milliseconds = total_milliseconds / len(all_times)
    return average_milliseconds


def get_final_time(raceid, runner):
    response = requests.get(f"https://races.therun.gg/{raceid}")
    data = response.json()
    result = data["result"]
    participants = result["participants"]
    for participant in participants:
        if (participant["user"].lower() == runner.lower()):
            finalTime = participant["finalTime"]
            if (finalTime is not None):
                return finalTime
    return 1e8

def get_final_times(raceid, runners):
    response = requests.get(f"https://races.therun.gg/{raceid}")
    data = response.json()
    result = data["result"]
    participants = result["participants"]
    final_times = [1e8,1e8,1e8]
    
    for participant in participants:
        for idx, runner in enumerate(runners):
            if (participant["user"].lower() == runner.lower()):
                finalTime = participant["finalTime"]
                if (finalTime is not None):
                    final_times[idx] = finalTime
                    break               
            

    return final_times

def get_position(race_id, final_time):
    response = requests.get(f"https://races.therun.gg/{race_id}")
    data = response.json()
    result = data["result"]
    participants = result["participants"]

    final_times = []
    for participant in participants:
        finalTime = participant["finalTime"]
        if (finalTime is not None):
            final_times.append(finalTime)
    try:
        return final_times.index(final_time) + 1
    except ValueError:
        return 1

    return final_times.index(final_time) + 1

def get_best_time(final_time, seed):
    #delay = random.randint(1, 10)
    #time.sleep(delay / 0.5)

    spreadsheet_id = "1i4DUK9SuWknyS1QW2MXGchRZ4s1cu44CSrNRUP03tvY"
    RANGE_NAME = RANGE_NAME = f'Runners!I{int(seed)+1}'

    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    #Retrieve current value from the spreadsheet
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=RANGE_NAME).execute()
    current_value =  result.get('values', [])[0][0][1:-1].split(",")

    lowest_time = final_time
    for value in current_value:
        value = parse_time_to_milliseconds(value)
        if (value < lowest_time):
            lowest_time = value   
    return format_milliseconds(lowest_time)

def get_average_time(final_time, seed):
    #delay = random.randint(1, 10)
    #time.sleep(delay / 0.5)

    spreadsheet_id = "1i4DUK9SuWknyS1QW2MXGchRZ4s1cu44CSrNRUP03tvY"
    RANGE_NAME = RANGE_NAME = f'Runners!I{int(seed)+1}'

    creds = get_credentials()
    service = build('sheets', 'v4', credentials=creds)

    #Retrieve current value from the spreadsheet
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=RANGE_NAME).execute()
    current_value =  result.get('values', [])[0][0]
    parts = current_value[1:-1].split(',')
    all_times = [final_time]
    for value in parts:
        if (value == ''):
            continue
        all_times.append(parse_time_to_milliseconds(value))
    
    
    average_time = calculate_average_time(all_times)
    
    return format_milliseconds(average_time)