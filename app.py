from flask import Flask, render_template, send_from_directory, request, jsonify

from get_race_information import get_race_information
from flags import get_country_flag_url
from local_overrides import LocalRunnerData
from get_delta_times import get_delta_times
from get_golds import get_golds




app = Flask(__name__, static_folder='static')
localOverrides = {}

#these are the pages that can be rendered
@app.route('/intro')
def intro():
    spreadsheet_id = request.args.get('spreadsheet_id')
    return render_template('intro.html')

@app.route('/layout')
def layout_2P():
    spreadsheet_id = request.args.get('spreadsheet_id')

    #depending on how many runners there are
    return render_template('layout_2P.html')
    return render_template('layout_3P.html')

@app.route('/outro')
def outro():
    spreadsheet_id = request.args.get('spreadsheet_id')

    #depending on how many runners there are
    return render_template('outro_2P.html')
    return render_template('outro_3P.html')



#this might get called from automarathon
@app.route('/runnerstwitch')
def runnerstwitch():
    spreadsheet_id = request.args.get('spreadsheet_id')
    
    _, runners_values = get_race_information(spreadsheet_id)
    
    data = []
    for runner in runners_values:
        runner_dict = {}
        runner_dict['name'] = runner[0]
        runner_dict['twitch'] = runner[3]
        data.append(runner_dict)
    return data



#this gets called once when the layout is loaded, if a change is happening, the source would need to be refreshed, which will give a flickering white screen for a second
@app.route('/static_info')
def static_info():
    spreadsheet_id = request.args.get('spreadsheet_id')
    #check validity of spreadsheet_id
    spreadsheet_valid = True
    try:
        race_info, runners_values = get_race_information(spreadsheet_id)
    except:  # noqa: E722
        spreadsheet_valid = False      
    if (spreadsheet_id not in localOverrides and not spreadsheet_valid):
        # Render a template with the error message
        return jsonify({'error':'Please provide a valid spreadsheet_id or override something with this id'})

    if (spreadsheet_id not in localOverrides):
        localOverrides[spreadsheet_id] = LocalRunnerData()

    localRunnerData = localOverrides[spreadsheet_id]
    #if everything is overriden, dont consult the sheet
    checkFile = not localRunnerData.everything_static_overriden() 
    
    racename = localRunnerData.race_name
    runners = [runner_name for runner_name in localRunnerData.runner_names]
    country_urls = [get_country_flag_url(country) for country in localRunnerData.runner_countries]
    
    if (checkFile and spreadsheet_valid):
        #only override what is on default value
        race_info, runners_values = get_race_information(spreadsheet_id)
        if (racename == ""):
            racename = race_info[0]
        for i in range(3):
            if (runners[i] == ""):
                runners[i] = f"({runners_values[i][1]}) {runners_values[i][0]}" 
            if (country_urls[i] == ""):
                country_urls[i] = get_country_flag_url(runners_values[i][23])
    else:
        print("Not checking file")    

    return jsonify({'racename': racename}, {'runners': runners}, {'country_urls': country_urls})

#this gets called every x seconds from the layouts

@app.route('/runner_positions')
def runner_positions():
    spreadsheet_id = request.args.get('spreadsheet_id')
    #check validity of spreadsheet_id
    spreadsheet_valid = True
    try:
        race_info, runners_values = get_race_information(spreadsheet_id)
    except:  # noqa: E722
        spreadsheet_valid = False      
    if (spreadsheet_id not in localOverrides and not spreadsheet_valid):
        # Render a template with the error message
        return jsonify({'error':'Please provide a valid spreadsheet_id or override something with this id'})

    if (spreadsheet_id not in localOverrides):
        localOverrides[spreadsheet_id] = LocalRunnerData()

    localRunnerData = localOverrides[spreadsheet_id]
    #if therun is disabled, order the runners how they are in the spreadsheet/local override class
    if (localRunnerData.override_therun):
        return jsonify({'runner_positions':[1,2,3]})
    #if therun is enabled, get the order from the race

    #get race id
    race_id = localRunnerData.therun_race_id
    if (race_id == ""):
        if not spreadsheet_valid:
            return jsonify({'error':'please set a therun race id in overrides or use a valid google spreadsheet'})
        race_id = race_info[1]            
    
    #get runner golds
    runner_golds = localRunnerData.runner_gold_times

    if spreadsheet_valid:  
        golds = get_golds(spreadsheet_id)
        for i in range(3):
            if (runner_golds[i] == ""):
                runner_golds[i] = golds[i]
    #get runners therungg
    runner_runggs = localRunnerData.runner_runggs
    if not spreadsheet_valid and "" in runner_runggs:
        return jsonify({'error':'please set a therun id for all runners'})

    

    if spreadsheet_valid:
        for i in range(3):
            runner_runggs[i] = runners_values[i][4]

    #reuse get delta times, as this sorts the runner array by who is in the lead
    xd, sorted_runners_rungg = get_delta_times(race_id, runner_golds, runner_runggs)
    #sort runners
    print(xd)
    print(sorted_runners_rungg)
    if spreadsheet_valid:
        runner_order = {runner[4].upper(): (idx+1) for idx,runner in enumerate(runners_values)}
    else:
        runner_order = {runner.upper(): (idx+1) for idx,runner in enumerate(runner_runggs)}
    race_order = [runner_order[runner_id.upper()] for runner_id in sorted_runners_rungg]
    return jsonify({'runner_positions':race_order})
        
        
    
    
    

#list what we need in the layout:
# - race name
# - therun race id
# - runner names
# - countries
# - runner position
# - runner split times
# - runner sob
# - runner bpt
# - runner improvement since seeding
# - runner pbs
# - runner final time


#list of overrides
# - race name
# - therun race id
# - runner names
# - countries
# - rungg (if sheet is not working)
# - gold splits (if file download is not working)
# - runner sobs (if therun not working)
# - runner pbs (if data in sheet is wrong or not there)
# - runner improvement (same as above)
# - toggle using therun, this would only show racename, sobs, pbs and improvement then
# - runner final times

@app.route('/override')
def override_info():    
    spreadsheet_id = request.args.get('spreadsheet_id')

    #try to get all request args: possible are race_name, therun_race_id, names, countries, runggs, golds, sobs, pbs, improvements, override_therun, final_times

    possible_args = [
        'race_name', 'therun_race_id', 'names', 'countries', 'runggs', 
        'golds', 'sobs', 'pbs', 'improvements', 'override_therun', 'final_times'
    ]
    
    # Initialize a dictionary to store the request arguments
    args = {arg: request.args.get(arg, '') for arg in possible_args}
    
    if (spreadsheet_id not in localOverrides):
        localOverrides[spreadsheet_id] = LocalRunnerData()
        
    # Convert the dictionary values to individual variables (strings)
    if args['race_name']:
        localOverrides[spreadsheet_id].race_name = args['race_name']
    if args['therun_race_id']:
        localOverrides[spreadsheet_id].therun_race_id = args['therun_race_id']
    if args['names']:
        localOverrides[spreadsheet_id].runner_names = args['names'].split(',')
    if args['countries']:
        localOverrides[spreadsheet_id].runner_countries = args['countries'].split(',')
    if args['runggs']:
        localOverrides[spreadsheet_id].runner_runggs = args['runggs'].split(',')
    if args['golds']:
        localOverrides[spreadsheet_id].runner_gold_times = args['golds'].split(';')
        print(localOverrides[spreadsheet_id].runner_gold_times)
    if args['sobs']:
        localOverrides[spreadsheet_id].runner_sobs = args['sobs'].split(',')
    if args['pbs']:
        localOverrides[spreadsheet_id].runner_pbs = args['pbs'].split(',')
    if args['improvements']:
        localOverrides[spreadsheet_id].runner_improvements_since_seeding = args['improvements'].split(',')
    if args['override_therun']:
        localOverrides[spreadsheet_id].override_therun = args['override_therun'].split(',')
    if args['final_times']:
        localOverrides[spreadsheet_id].runner_final_times = args['final_times'].split(',')
    

    #for id in localOverrides:
    #    print(localOverrides[id].override_runner_sobs)

    return render_template('success.html', message='The overrides have been executed')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=35065, debug=True)