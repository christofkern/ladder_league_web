
import requests
from get_final_time import format_milliseconds

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