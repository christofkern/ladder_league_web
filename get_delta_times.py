import requests
from googleapiclient.discovery import build
import ast

from get_google_credentials import get_credentials
from get_final_time import format_delta, parse_time_to_milliseconds



def get_level_gold(runner, levels):
    
    ENDPOINT = f"https://therun.gg/api/users/{runner}"
    response  = requests.get(ENDPOINT)
    data = response.json()

    for gamedata in data:
        game = gamedata["game"]
        category = gamedata["run"]
        solo = gamedata["variables"]
        
        if ("Solo or Co-op?" in solo):
            solo = solo["Solo or Co-op?"]
        else:
            solo = {}
        if ("LEGO Star Wars: The Complete Saga (PC/Console)" in game and "Any%" in category and ("Solo" in solo or solo == {})):
            if (gamedata["gameTimeData"] is not None): 
                pass #loadless
            pass


def delta_sort(item):
    if item[1] == '-':
        return (2, float('inf')) 
    if item[1] == 'LEADER':
        return (0, float('inf'))     
    else:
        return (1, item[1])  



def get_delta_times(race_id, spreadsheet_id, runners, interval = False):
    #print(runners)

    deltas = [(runners[0],'-'),(runners[1],'-'),(runners[2],'-')]

    ENDPOINT = f"https://races.therun.gg/{race_id}/messages"

    response  = requests.get(ENDPOINT)
    data = response.json()['result']

    runner_splits = {runners[0].upper():[],runners[1].upper():[],runners[2].upper():[]}

    for entry in data:
        if ("data" in entry):
            if ("user" in entry["data"] and entry["type"] == "participant-split"):                                
                split_present = False
                if (entry["data"]["user"].upper() in runner_splits):
                    for item in runner_splits[entry["data"]["user"].upper()]:
                        if (entry["data"]["splitName"] in item):
                            split_present = True
                            break
                    if (not split_present):
                        runner_splits[entry["data"]["user"].upper()].append([entry["data"]["splitName"],entry["data"]["time"]])
                    
    most_splits = 0
    fastest_splittime = float('inf')
    fastest_runner = ""
    all_on_first = True
    for runner in runner_splits:
        splitset = runner_splits[runner]
        if (len(splitset) > 1):
            all_on_first = False
        else:
            continue
        if (len(splitset) > most_splits):
            fastest_splittime = splitset[0][1] #need to set this, so it can be compared against later
            most_splits = len(splitset)
            fastest_runner = runner
        elif (len(splitset) == most_splits and splitset[0][1] < fastest_splittime):
            fastest_splittime = splitset[0][1]
            most_splits = len(splitset) #this is kinda unnecessary but whatever
            fastest_runner = runner

    if (all_on_first):
        return deltas, runners    
    #print(fastest_runner)


    for idx,runner in enumerate(runner_splits):
        if (runner != fastest_runner):
            splitset = runner_splits[runner]
            if (len(splitset) == most_splits):#on the same split, calculate delta between times
                delta = splitset[0][1] - fastest_splittime
                deltas[idx] = (runner,delta)
            elif (len(splitset) == 0): #runner not found in race, maybe prerecorded or rungg integration not working
                pass
            else: #pull golds for the missing levels and add that to the last existing time
                RUNNERS_RANGE_NAME = 'Runners!Z2:Z5'
                creds = get_credentials()
                service = build('sheets', 'v4', credentials=creds)

                race_sheet = service.spreadsheets()      

                runners_result = race_sheet.values().get(spreadsheetId=spreadsheet_id,range=RUNNERS_RANGE_NAME).execute()
                golds = ast.literal_eval(runners_result.get('values', [])[idx][0])

                delta = splitset[0][1] - fastest_splittime
                
                for i in range (most_splits - len(splitset)):
                    #print(f"adding gold: {golds[most_splits - i - 2]}")
                    delta = delta + parse_time_to_milliseconds(golds[most_splits - i - 1])
                if (delta < 0):
                    delta = 1
                deltas[idx] = (runner,delta)
        else:
            deltas[idx] = (runner,"LEADER")

    
    #sort by deltas
    deltas = sorted(deltas, key=delta_sort)
    if (interval):
        deltas[0] = (runner,"INTERVAL")
        if (deltas[2][1] != '-'):
            deltas[2][1] = deltas[2][1] - deltas[1][1]

    runners = [deltas[i][0] for i in range(len(deltas))]
    deltas = [deltas[i][1] for i in range(len(deltas))]
    deltas = [format_delta(item) if isinstance(item, float) else item for item in deltas]
    return deltas, runners


if __name__ == '__main__':
    print(get_delta_times('m0xv', '1XmejJM1rKN3c38eRDNx-vdVZ5AuMjS9iQ7WYZ00LDIk', ['AnAnonymousSource','Raaapho','yahootles']))
    




