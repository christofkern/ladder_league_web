import requests
from get_final_time import format_milliseconds

def isEmpty(dictionary):
    for element in dictionary:
        if element:
            return True
        return False



def get_runner_sob(runner):
    response = requests.get(f"https://therun.gg/api/users/{runner}/")
    # Check the status of the API   
    #print(response.status_code)
    if response.status_code == 500:
        return "--:--:--"
    data = response.json()
    sw_sob = float('inf')
    #print(data)
    for gamedata in data:
        game = gamedata["game"]
        category = gamedata["run"]    
        if ("variables" in gamedata): 
            solo = gamedata["variables"]
        else:
            solo = {}
        sob = gamedata["sumOfBests"]
        #print(f"SOB of {runner} is {sob}")
        if ("Solo or Co-op?" in solo):
            solo = solo["Solo or Co-op?"]
        else:
            solo = {}
        if ("LEGO Star Wars: The Complete Saga (PC/Console)" in game and "Any%" in category and ("Solo" in solo or solo == {})):  
            #print(gamedata)
            if (gamedata["gameTimeData"] is not None):  
                #use loadless if available		 
                sob = gamedata["gameTimeData"]["sumOfBests"]
        if (float(sob) < sw_sob):
            sw_sob = float(sob)    
    return format_milliseconds(sw_sob)


def get_runner_bpt(race_id, rungg):
    response = requests.get(f"https://races.therun.gg/{race_id}")
    if response.status_code == 500:
        return "--:--:--"
    data = response.json()
    result = data["result"]
    participants = result["participants"]
    for participant in participants:
        if (participant["user"].lower() == rungg.lower()):
            if ("liveData" in participant):
                liveData = participant["liveData"]
                if ("bestPossibleTime" in liveData):
                    bpt = liveData["bestPossibleTime"]
                    if (bpt is not None):
                        return format_milliseconds(bpt)
    return "--:--:--"
    
