from flask import Flask, render_template, send_from_directory, request, jsonify
from get_race_information import get_race_information
from therun_user_info import get_runner_sob
from update_race_information import write_sob
from states import get_state_flag_url
from get_final_time import get_final_time, format_milliseconds, get_position

app = Flask(__name__)

@app.route('/rotating_layouts/<path:filename>')
def serve_html(filename):
    return send_from_directory('rotating_layouts', filename)

@app.route('/')
def index():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    _, runners_values = get_race_information(spreadsheet_id)
    return render_template('rotating_info.html', interval = 2000, spreadsheet_id = spreadsheet_id, runner_data = runners_values)

@app.route('/recheck_data')
def recheck_data():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        return render_template('error.html', message='Please provide a valid spreadsheet_id')

    _, runners_values = get_race_information(spreadsheet_id)

    #update data from therun (sob)
    for idx, runner in enumerate(runners_values):
        rungg = runner[4]        
        sob = get_runner_sob(rungg)
        write_sob(spreadsheet_id, idx, sob)

    return jsonify({'runners' : runners_values})

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

@app.route('/racename')
def racename():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    race_info, _ = get_race_information(spreadsheet_id)
    return render_template('racename.html', text_content = race_info[0])

@app.route('/runnername')
def runnername():
    spreadsheet_id = request.args.get('spreadsheet_id')
    runner = request.args.get('runner')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    _, runners_values = get_race_information(spreadsheet_id)
    if runner is None or int(runner) >= len(runners_values):
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid runner index')

    #check if all country codes are the US, country code is index 21
    if all(r[21] == "US" for r in runners_values):
        return render_template('runnername_state.html', text_content = f"({runners_values[int(runner)][1]}) {runners_values[int(runner)][0]}", state_flag_url = get_state_flag_url(runners_values[int(runner)][22]))
    else:
        return render_template('runnername_country.html', text_content = f"({runners_values[int(runner)][1]}) {runners_values[int(runner)][0]}", country_code = runners_values[int(runner)][21])



@app.route('/runner_overlay')
def runner_overlay():
    spreadsheet_id = request.args.get('spreadsheet_id')
    runner = request.args.get('runner')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    race_info, runners_values = get_race_information(spreadsheet_id) 
    race_id = race_info[1]
    runner_rungg = runners_values[int(runner)][4]
    isTopRung = bool(race_info[4]) 
    isQualifier = bool(race_info[5])
    if runner is None or int(runner) >= len(runners_values):
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid runner index')     
    result = ""
    text_color = ""
    final_time = get_final_time(race_id, runner_rungg)
    if (final_time != 0):
        position = get_position(race_id, final_time)
        print(position)
        if (isQualifier and (position == 1 or (position == 2 and len(runners_values) == 3))):
            result = "QUALIFIED"
            text_color = "#337357"
        elif (isQualifier):
            result = "ELIMINATED"
            text_color = "#EE4266"
        elif (isTopRung and position == 1):
            result = "QUALIFIED"
            text_color = "#337357"
        elif (isTopRung and position == 2):
            result = "RUNNER-UP"
            text_color = "#FFD23F"
        elif (not isTopRung and (position == 1 or position == 2)):
            result = "PROMOTED"
            text_color = "#337357"
        else:
            result = "DEMOTED"
            text_color = "#5E1675"


    
    return render_template('overlay.html', result_string = result, text_color = text_color,  final_time = format_milliseconds(final_time))
    


@app.route('/pictures')
def pictures():
    spreadsheet_id = request.args.get('spreadsheet_id')
    runner = request.args.get('runner')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    _, runners_values = get_race_information(spreadsheet_id)
    if runner is None or int(runner) >= len(runners_values):
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid runner index')      
    return render_template('picture.html', picture_url = runners_values[int(runner)][5])


@app.route('/fonts/<path:filename>')
def custom_font_route(filename):
    return send_from_directory('static/fonts', filename, mimetype='font/ttf')


if __name__ == '__main__':
    app.run(debug=True)
