import requests

def isEmpty(dictionary):
    for element in dictionary:
        if element:
            return True
        return False

def format_milliseconds(total_milliseconds):
    if isinstance(total_milliseconds, str):
        total_milliseconds = float(total_milliseconds)
    total_seconds = total_milliseconds / 1000  # Convert milliseconds to seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"
    return formatted_time

def get_runner_sob(runner):
    response = requests.get(f"https://therun.gg/api/users/{runner}/")
    # Check the status of the API
    #print(response.status_code)

    data = response.json()
    for gamedata in data:
        game = gamedata["game"]
        category = gamedata["run"]       
        solo = gamedata["variables"]
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
            return format_milliseconds(sob)


    