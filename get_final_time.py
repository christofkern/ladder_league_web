import requests

def format_milliseconds(total_milliseconds):
    if isinstance(total_milliseconds, str):
        total_milliseconds = float(total_milliseconds)
    total_seconds = total_milliseconds / 1000  # Convert milliseconds to seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"
    return formatted_time

def get_final_time(raceid, runner):
    response = requests.get("https://races.therun.gg/7szf")
    data = response.json()
    result = data["result"]
    participants = result["participants"]
    for participant in participants:
        if (participant["user"].lower() == runner.lower()):
            finalTime = participant["finalTime"]
            if (finalTime is not None):
                return finalTime
    return 0

def get_position(race_id, final_time):
    response = requests.get("https://races.therun.gg/7szf")
    data = response.json()
    result = data["result"]
    participants = result["participants"]

    final_times = []
    for participant in participants:
        finalTime = participant["finalTime"]
        if (finalTime is not None):
            final_times.append(finalTime)
    return final_times.index(final_time) + 1