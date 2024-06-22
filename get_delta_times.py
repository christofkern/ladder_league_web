import requests

from get_final_time import format_delta, parse_time_to_milliseconds

def delta_sort(item):
    if item[1] == '-':
        return (2, float('inf')) 
    if item[1] == 'LEADER':
        return (0, float('inf'))     
    else:
        return (1, item[1])  



def get_delta_times(race_id, golds, runners, interval = False):
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
        deltas = [deltas[i][1] for i in range(len(deltas))]
        return deltas, runners    
    #print(fastest_runner)


    for idx,runner in enumerate(runner_splits):
        runner_golds = golds[idx]
        print(runner_golds)
        if (runner != fastest_runner):
            
            splitset = runner_splits[runner]
            if (len(splitset) == most_splits):#on the same split, calculate delta between times
                delta = splitset[0][1] - fastest_splittime
                deltas[idx] = (runner,delta)
            elif (len(splitset) == 0): #runner not found in race, maybe prerecorded or rungg integration not working
                #print("Passing")
                continue
            else: #use golds for the missing levels and add that to the last existing time
                if (len(golds[idx]) == 0):
                    continue
                runner_golds = golds[idx][1:-1].split(',')
                if (len(runner_golds)==0):
                    continue
                delta = splitset[0][1] - fastest_splittime                
                
                for i in range (most_splits - len(splitset)):
                    
                   # print(f"adding gold: {runner_golds[most_splits - i - 2]}")
                    
                    if (len(runner_golds) > most_splits - i - 3):
                        print(f"adding gold: {runner_golds[most_splits - i - 2]}")
                        delta = delta + parse_time_to_milliseconds(runner_golds[most_splits - i - 2][2:-1])
                    
                if (delta < 0):
                    delta = format_delta(1000)
                deltas[idx] = (runner,delta)
        else:
            deltas[idx] = (runner,"LEADER")

    #print(deltas)
    #sort by deltas
    deltas = sorted(deltas, key=delta_sort)
    if (interval):
        deltas[0] = (runner,"INTERVAL")
        if (deltas[2][1] != '-'):
            deltas[2] = (deltas[2][0], deltas[2][1] - deltas[1][1])

    runners = [deltas[i][0] for i in range(len(deltas))]
    deltas = [deltas[i][1] for i in range(len(deltas))]
    deltas = [format_delta(item) if isinstance(item, float) else item for item in deltas]
    return deltas, runners


if __name__ == '__main__':
    print(get_delta_times('m0xv', '1XmejJM1rKN3c38eRDNx-vdVZ5AuMjS9iQ7WYZ00LDIk', ['AnAnonymousSource','Raaapho','yahootles']))
    




