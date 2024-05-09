from flask import Flask, render_template, send_from_directory, request, jsonify
from get_race_information import get_race_information
from therun_user_info import get_runner_sob, get_runner_bpt
from update_race_information import write_sob, write_final_time
from states import get_state_flag_url
from get_final_time import get_final_time, format_milliseconds, get_position, get_best_time, get_average_time

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
    race_data, runners_values = get_race_information(spreadsheet_id)
    for idx, runner in enumerate(runners_values):
        rungg = runner[4]
        bpt = get_runner_bpt(race_data[1], rungg)
        runners_values[idx].append(bpt)
    #print(runners_values)
    return render_template('rotating_info.html', interval = 6000, spreadsheet_id = spreadsheet_id, runner_data = runners_values)

@app.route('/recheck_data')
def recheck_data():
    spreadsheet_id = request.args.get('spreadsheet_id')
    once = request.args.get('once')
    if spreadsheet_id is None or spreadsheet_id == '':
        return render_template('error.html', message='Please provide a valid spreadsheet_id')


    race_data, runners_values = get_race_information(spreadsheet_id)

    #update data from therun (sob)
    if (once == "True"):
        for idx, runner in enumerate(runners_values):
            rungg = runner[4]
            sob = get_runner_sob(rungg)
            write_sob(spreadsheet_id, idx, sob)

            bpt = get_runner_bpt(race_data[1], rungg)
            runners_values[idx].append(bpt)
            

            final_time = get_final_time(race_data[1], rungg)
            if (final_time != 1e8):
                position = get_position(race_data[1], final_time)
                if (position != 0):
                    write_final_time(spreadsheet_id, idx, str(final_time), runners_values[idx][1], position, runners_values[idx][18])

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
    if (runner == "Test"):

        return render_template('overlay.html', result_string = "Test", text_color = "#EE4266", final_time = format_milliseconds(12345678))

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
    if (final_time != 1e8):
        position = get_position(race_id, final_time)
        if (position != 0):
            write_final_time(spreadsheet_id, runner, str(final_time), runners_values[int(runner)][1], position, runners_values[int(runner)][18])
            if (isQualifier and (position == 1 or (position == 2 and len(runners_values) == 3))):
                result = "QUALIFIED"
                text_color = "#337357"
            elif (isQualifier):
                if (len(runners_values) == 2):
                    result = "RUNNER-UP"
                    text_color = "#FFD23F"
                else:   
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

    return render_template('overlay.html', spreadsheet_id = spreadsheet_id, runner_data=runners_values, result_string = result, text_color = text_color,  final_time = format_milliseconds(final_time))
    



@app.route('/post_race_info')
def post_race_info():
    spreadsheet_id = request.args.get('spreadsheet_id')
    runner = request.args.get('runner')

    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')

    
    race_info, runners_values = get_race_information(spreadsheet_id) 


    if runner is None or int(runner) >= len(runners_values):
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid runner index')     
    race_id = race_info[1]
    runner_rungg = runners_values[int(runner)][4]
    isTopRung = bool(race_info[4]) 
    isQualifier = bool(race_info[5])
    

    final_time = get_final_time(race_id, runner_rungg)
    final_time_icon = "https://cdn.discordapp.com/attachments/1237639431352090654/1238107907963355157/image.png?ex=663e1558&is=663cc3d8&hm=08308591b0591a2db41c51a68bf5f8914dcc7feee6f7ea5ec70f0adde9334503&"
    if (final_time != 1e8):
        position = get_position(race_id, final_time)        
        if (isQualifier and (position == 1 or (position == 2 and len(runners_values) == 3))):
            final_time_icon = "https://cdn.discordapp.com/attachments/1237639431352090654/1238066966095204412/image.png?ex=663def36&is=663c9db6&hm=b2dc2c749b4b879b576f7143026ca9e87e6e1b6f68e55a1f414e7d90e25b7c84&"
        elif (isQualifier):
            if (len(runners_values) == 2):
                final_time_icon = "https://cdn.discordapp.com/attachments/1237639431352090654/1238067127429238835/image.png?ex=663def5d&is=663c9ddd&hm=5dcc8fa8bbae18496ede2615bfdf6b72017524bfbbb44f6b621b220b7cf3102c&"
            else:
                final_time_icon = "https://cdn.discordapp.com/attachments/1237639431352090654/1238066684091170836/image.png?ex=663deef3&is=663c9d73&hm=6cd0dec79557b809b1b81bd7aa80a8fb05014e863847ea3c4428fb9b8985966d&"
        elif (isTopRung and position == 1):
            final_time_icon = "https://cdn.discordapp.com/attachments/1237639431352090654/1238066966095204412/image.png?ex=663def36&is=663c9db6&hm=b2dc2c749b4b879b576f7143026ca9e87e6e1b6f68e55a1f414e7d90e25b7c84&"
        elif (isTopRung and position == 2):
            final_time_icon = "https://cdn.discordapp.com/attachments/1237639431352090654/1238067127429238835/image.png?ex=663def5d&is=663c9ddd&hm=5dcc8fa8bbae18496ede2615bfdf6b72017524bfbbb44f6b621b220b7cf3102c&"
        elif (not isTopRung and (position == 1 or position == 2)):
            if (position == 1):
                final_time_icon = "https://cdn.discordapp.com/attachments/1237639431352090654/1238066014520873011/image.png?ex=663dee54&is=663c9cd4&hm=88691780be63da897350e3999e32895f7a924cd70f727988f327dbef49ad04bf&"
            else:
                final_time_icon = "https://cdn.discordapp.com/attachments/1237639431352090654/1238066233119866900/image.png?ex=663dee88&is=663c9d08&hm=a181e16a363d061fd995bf1bb0a054e8d944d5c41e2f12451a8af3d0a639c721&"            
        else:
            final_time_icon = "https://cdn.discordapp.com/attachments/1237639431352090654/1238066376615399475/image.png?ex=663deeaa&is=663c9d2a&hm=a809d30fbdec89dbc07e69fb8276dd61547e690a4b07a24947544de4fab80cd0&"

    
        record = runners_values[int(runner)][18]
        records = record.split('-')
        records[position - 1] = str(int(records [position - 1]) + 1)
        record_string = '-'.join(records)
        best_time = get_best_time(final_time, runners_values[int(runner)][1])
        average_time = get_average_time(final_time, runners_values[int(runner)][1])
        final_time = format_milliseconds(final_time)
    else:
        record = ""
        best_time = ""
        average_time = ""
        final_time = "Awaiting Data"

    return render_template('post_race_stats.html',  final_time = final_time, final_time_icon = final_time_icon, record = record_string, best_time = best_time, average_time = average_time )


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
    app.run(host='0.0.0.0', port=35065, debug=True)
