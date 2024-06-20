from flask import Flask, render_template, send_from_directory, request, jsonify

from get_race_information import get_race_information
from flags import get_country_flag_url
import ssl




app = Flask(__name__, static_folder='static')
ssl._create_default_https_context = ssl._create_unverified_context


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
    race_info, runners_values= get_race_information(spreadsheet_id)
    racename = race_info[0]
    runners = [None] * len(runners_values)

    for i in range(len(runners_values)):        
        #check if all country codes are the US, country code is index 21
        print(runners_values)
        runners[i] = f"({runners_values[i][1]}) {runners_values[i][0]}" 
        country_url = get_country_flag_url(runners_values[i][23])

    return jsonify({'racename': racename}, {'runners': runners}, {'country_url': country_url})

#this gets called every x seconds from the layouts

#list what we need:
# - runner position
# - runner split times
# - runner sob


#overrides (with bot commands?)
# - final time
# - ignore runner



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=35065, debug=True)