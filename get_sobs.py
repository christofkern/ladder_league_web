
import requests
from get_final_time import format_milliseconds

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
            if (sob == ""):
                sob = float('inf')
            if (float(sob) < float(sw_sob) and float(sob)>7200000):
                sw_sob = float(sob)    
    return format_milliseconds(sw_sob)