from flask import Flask, render_template, send_from_directory, request, jsonify

from get_race_information import get_race_information
from flags import get_country_flag_url
from local_overrides import LocalRunnerData




app = Flask(__name__, static_folder='static')


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

#this gets called once when the layout is loaded
@app.route('/static_info')
def racename():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    
    #if everything is overriden, dont consult the sheet
    checkFile = not LocalRunnerData.everything_static_overriden()
    
    racename = LocalRunnerData.race_name
    runners = [runner_name for runner_name in LocalRunnerData.runner_names]
    country_urls = [get_country_flag_url(country) for country in LocalRunnerData.runner_countries]
    
    if (checkFile):
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

#list what we need in the layout:
# - race name
# - runner names
# - countries
# - runner position
# - runner split times
# - runner sob
# - runner bpt
# - runner improvement since seeding
# - runner pbs




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=35065, debug=True)