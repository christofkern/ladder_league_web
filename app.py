from flask import Flask, render_template, send_from_directory, request, jsonify
import random 

from get_race_information import get_race_information
from flags import get_country_flag_url
from local_overrides import LocalRunnerData
from get_delta_times import get_delta_times
from get_golds import get_golds
from get_bpts import get_runner_bpt
from get_sobs import get_runner_sob
from get_final_time import get_final_times, format_milliseconds, get_position



app = Flask(__name__, static_folder='static')
localOverrides = {}

@app.route('/fonts/<path:filename>')
def custom_font_route(filename):
    return send_from_directory('static/fonts', filename, mimetype='font/ttf')

#these are the pages that can be rendered
@app.route('/intro')
def intro():
    spreadsheet_id = request.args.get('spreadsheet_id')
    return render_template('intro.html', spreadsheet_id = spreadsheet_id)

@app.route('/layout')
def layout_2P():
    spreadsheet_id = request.args.get('spreadsheet_id')
    #check validity of spreadsheet_id
    spreadsheet_valid = True
    try:
        race_info, runners_values = get_race_information(spreadsheet_id)
    except:  # noqa: E722
        spreadsheet_valid = False      
    if (spreadsheet_id not in localOverrides and not spreadsheet_valid):
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id or override something with this id')

    if (spreadsheet_id not in localOverrides):
        localOverrides[spreadsheet_id] = LocalRunnerData()

    localRunnerData = localOverrides[spreadsheet_id]
    
    #find out it 2P or 3P layout is to be used
    if spreadsheet_valid:
        runner_amount = len(runners_values)        
    else:
        runner_amount = 0
        for runner in localRunnerData.runner_names:
            if (runner != ""):
                runner_amount += 1

    if runner_amount == 2:
        return render_template('layout_2P.html', spreadsheet_id = spreadsheet_id)
    elif runner_amount == 3:
        return render_template('layout_3P.html', spreadsheet_id = spreadsheet_id)
    else:
        return render_template('error.html', message=f'There is no layout for {runner_amount} runner(s)')
        

    

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
    country_urls = [country for country in localRunnerData.runner_countries]


    count = len(runners_values)

    
    if (checkFile and spreadsheet_valid):
        #only override what is on default value
        race_info, runners_values = get_race_information(spreadsheet_id)
        if (racename == ""):
            racename = race_info[0]
        for i in range(count):
            if (runners[i] == ""):
                runners[i] = f"({runners_values[i][1]}) {runners_values[i][0]}" 
            if (country_urls[i] == ""):                
                country_urls[i] = get_country_flag_url(runners_values[i][23])
    else:
        print("Not checking file")    

    return jsonify({'racename': racename}, {'runners': runners[:len(runners_values)]}, {'country_urls': country_urls})

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

    #if only 2 persons, then its 1,2 anyway
    if (len(runners_values) == 2):
        return jsonify({'runner_positions':[1,2]})

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
        golds = get_golds(spreadsheet_id, len(runners_values))
        for i in range(len(runners_values)):
            if (runner_golds[i] == ""):
                runner_golds[i] = golds[i]
    #get runners therungg
    runner_runggs = localRunnerData.runner_runggs
    if not spreadsheet_valid and "" in runner_runggs:
        return jsonify({'error':'please set a therun id for all runners'})

    

    if spreadsheet_valid:
        for i in range(len(runners_values)):
            runner_runggs[i] = runners_values[i][4]

    #reuse get delta times, as this sorts the runner array by who is in the lead
    _, sorted_runners_rungg = get_delta_times(race_id, runner_golds, runner_runggs)
    #sort runners   
    if spreadsheet_valid:
        runner_order = {runner[4].upper(): (idx+1) for idx,runner in enumerate(runners_values)}
    else:
        runner_order = {runner.upper(): (idx+1) for idx,runner in enumerate(runner_runggs) if idx < len(runners_values)}
    race_order = [runner_order[runner_id.upper()] for idx,runner_id in enumerate(sorted_runners_rungg) if idx < len(runners_values)]
    return jsonify({'runner_positions':race_order[:len(runners_values)]})
        

@app.route('/runner_deltas')
def runner_deltas():
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


    #get race id
    race_id = localRunnerData.therun_race_id
    if (race_id == ""):
        if not spreadsheet_valid:
            return jsonify({'error':'please set a therun race id in overrides or use a valid google spreadsheet'})
        race_id = race_info[1]            
    
    #get runner golds
    runner_golds = localRunnerData.runner_gold_times

    if spreadsheet_valid:  
        golds = get_golds(spreadsheet_id, len(runners_values))
        for i in range(len(runners_values)):
            if (runner_golds[i] == ""):
                runner_golds[i] = golds[i]
    #get runners therungg
    runner_runggs = localRunnerData.runner_runggs
    if not spreadsheet_valid and "" in runner_runggs:
        return jsonify({'error':'please set a therun id for all runners'})

    

    if spreadsheet_valid:
        for i in range(len(runners_values)):
            runner_runggs[i] = runners_values[i][4]

    #reuse get delta times, as this sorts the runner array by who is in the lead
    deltas, _ = get_delta_times(race_id, runner_golds, runner_runggs, sort=False)

    return jsonify({'runner_deltas':deltas[:len(runners_values)]})


@app.route('/runner_pbs')
def runner_pbs():
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

    runner_pbs = localRunnerData.runner_pbs

    if spreadsheet_valid:          
        for i in range(len(runners_values)):
            if (runner_pbs[i] == ""):
                runner_pbs[i] = "0" + runners_values[i][12]

    return jsonify({'runner_pbs':runner_pbs[:len(runners_values)]})
    
@app.route('/runner_tournamentstats')
def runner_tournamentstats():
    spreadsheet_id = request.args.get('spreadsheet_id')
    #check validity of spreadsheet_id
    spreadsheet_valid = True
    try:
        race_info, runners_values = get_race_information(spreadsheet_id)
    except:  # noqa: E722
        spreadsheet_valid = False      
    if (not spreadsheet_valid):
        # Render a template with the error message
        return jsonify({'error':'Please provide a valid spreadsheet_id'})

    if (spreadsheet_id not in localOverrides):
        localOverrides[spreadsheet_id] = LocalRunnerData()

    h2h = runners_values[0][21] 
    runner_records = ["0-0-0","0-0-0","0-0-0"]
    runner_avgs = ["--:--:--","--:--:--","--:--:--"]

    for i in range(len(runners_values)):
        if (runner_records[i] == "0-0-0"):
            runner_records[i] = runners_values[i][20]
        if (runner_avgs[i] == "--:--:--"):
            runner_avgs[i] = runners_values[i][15]

    return jsonify({'h2h':h2h,'runner_records':runner_records[:len(runners_values)],'runner_avgs':runner_avgs[:len(runners_values)]})

@app.route('/runner_bpts')
def runner_bpts():
    spreadsheet_id = request.args.get('spreadsheet_id')
    #check validity of spreadsheet_id
    spreadsheet_valid = True
    try:
        race_info, runners_values = get_race_information(spreadsheet_id)
    except:  # noqa: E722
        spreadsheet_valid = False      
    if (not spreadsheet_valid):
        # Render a template with the error message
        return jsonify({'error':'Please provide a valid spreadsheet_id'})

    runner_bpts = ["--:--:--","--:--:--","--:--:--"]

    race_id = race_info[1]
    runner_runggs = ["","",""]
    for i in range(len(runners_values)):
        runner_runggs[i] = runners_values[i][4]

    runner_bpts = [get_runner_bpt(race_id, rungg) for rungg in runner_runggs if rungg != ""]
    return jsonify({'runner_bpts':runner_bpts[:len(runners_values)]})

@app.route('/runner_sobs')
def runner_sobs():
    spreadsheet_id = request.args.get('spreadsheet_id')
    #check validity of spreadsheet_id
    spreadsheet_valid = True
    try:
        race_info, runners_values = get_race_information(spreadsheet_id)
    except:  # noqa: E722
        spreadsheet_valid = False      
    if (not spreadsheet_valid):
        # Render a template with the error message
        return jsonify({'error':'Please provide a valid spreadsheet_id'})

    runner_sobs = ["--:--:--","--:--:--","--:--:--"]

    runner_runggs = ["","",""]
    for i in range(len(runners_values)):
        runner_runggs[i] = runners_values[i][4]

    runner_sobs = [get_runner_sob(rungg) for rungg in runner_runggs if rungg != ""]
    return jsonify({'runner_sobs':runner_sobs[:len(runners_values)]})

@app.route('/fun_fact')
def fun_fact():
    spreadsheet_id = request.args.get('spreadsheet_id')
    #check validity of spreadsheet_id
    spreadsheet_valid = True
    try:
        race_info, runners_values = get_race_information(spreadsheet_id)
    except:  # noqa: E722
        spreadsheet_valid = False      
    if (not spreadsheet_valid):
        # Render a template with the error message
        return jsonify({'error':'Please provide a valid spreadsheet_id or override something with this id'})

    if (spreadsheet_id not in localOverrides):
        localOverrides[spreadsheet_id] = LocalRunnerData()


    fun_facts = race_info[7].split('.')[:-1]
    fun_fact = random.choice(fun_facts)   

    return jsonify({'fun_fact':fun_fact})


@app.route('/check_final')
def check_final():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    
    race_info, runners_values = get_race_information(spreadsheet_id) 
    race_id = race_info[1]
    runner_runggs = [runners_values[int(runner)][4] for runner in range(len(runners_values))]
    isTopRung = race_info[4] == "True"
    isBottomRung = race_info[5] == "True"
    isQualifier = race_info[6] == "True"
    
    results = []
    text_colors = []
    
    final_times = get_final_times(race_id, runner_runggs)
    for final_time in final_times:    
        if (final_time != 1e8):
            position = get_position(race_id, final_time)
            if (position != 0):
                #consider doing pending when not everyone is finished??
                if (isQualifier and (position == 1 or (position == 2 and len(runners_values) == 3))):
                    results.append("QUALIFIED")
                    text_colors.append("#00ff15")
                elif (isQualifier):
                    if (len(runners_values) == 2):
                        results.append("RUNNER-UP")
                        text_colors.append("#ff9500")
                    else:   
                        results.append("ELIMINATED")
                        text_colors.append("#ff0040")
                elif(len(runners_values) == 2):
                    print(final_times)
                    print(position)
                    if (position == 1):
                        results.append("ADVANCED")
                        text_colors.append("#00ff15")
                    else:
                        results.append("ELIMINATED")
                        text_colors.append("#ff0040")
                elif (isTopRung and position == 1):
                    results.append("QUALIFIED")
                    text_colors.append("#00ff15")
                elif (isTopRung and not isBottomRung and position == 2):
                    results.append("RUNNER-UP")
                    text_colors.append("#ff9500")
                elif (not isTopRung and (position == 1 or (position == 2 and not isBottomRung ))):
                    results.append("PROMOTED")
                    text_colors.append("#00ff15")
                elif (isBottomRung):
                    results.append("ELIMINATED")
                    text_colors.append("#ff0040")
                else:
                    results.append("DEMOTED")
                    text_colors.append("#6a00ff")
            else:
                results.append('')
                text_colors.append('')  
        else:
            results.append('')
            text_colors.append('')
    final_times = [format_milliseconds(final_time) for final_time in final_times]
    return jsonify({'final_times' : final_times, 'results': results, 'text_colors' : text_colors})

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
        localOverrides[spreadsheet_id].runner_countries = [get_country_flag_url(country) if country else country for country in args['countries'].split(',')]
    if args['runggs']:
        localOverrides[spreadsheet_id].runner_runggs = args['runggs'].split(',')
    if args['golds']:
        localOverrides[spreadsheet_id].runner_gold_times = args['golds'].split(';')
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