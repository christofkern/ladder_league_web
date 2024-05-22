from flask import Flask, render_template, send_from_directory, request, jsonify
from get_race_information import get_race_information
from therun_user_info import get_runner_sob, get_runner_bpt
from update_race_information import write_sob, write_final_time, write_bpt, write_delta_times, write_sob_by_rungg
from flags import get_state_flag_url, get_country_flag_url
from get_final_time import get_final_time, format_milliseconds, get_position, get_best_time, get_average_time, get_final_times
from get_delta_times import get_delta_times
from carousel_generator import generate_carousel_items

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    race_data, runners_values = get_race_information(spreadsheet_id)
    funFacts = race_data[7].split('.')[:-1]
    #print(funFacts)
    return render_template('rotating_info.html', interval = 10000, spreadsheet_id = spreadsheet_id, runner_data = runners_values, funFacts = funFacts)


@app.route('/layout')
def layout():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    automarathon_host = request.args.get('automarathon_host')
    race_data, runners_values = get_race_information(spreadsheet_id)
    funFacts = race_data[7].split('.')[:-1]
    #print(funFacts)

    runnernames = [f"({runners_values[i][1]}) {runners_values[i][0]}" for i in range(3)]
    if all(r[23] == "US" for r in runners_values):
        flags = [get_state_flag_url(runners_values[i][24]) for i in range(3)]
        flags = [get_country_flag_url(runners_values[i][23]) for i in range(3)]
    else:
        flags = [get_country_flag_url(runners_values[i][23]) for i in range(3)]
    runnerdata = {'runnernames': runnernames,'flags': flags}

    runners = []
    for runner in runners_values:            
        runners.append(runner[4])

    delta_data, sorted_runners_rungg = get_delta_times(race_data[1], spreadsheet_id, runners)
    interval_data, _ = get_delta_times(race_data[1], spreadsheet_id, runners, True)
    #map rungg from sorted runners back to their display names
    runner_display_names = {runner[4].upper(): f"{runner[0]}" for runner in runners_values}
    sorted_runners = [runner_display_names[runner_id.upper()] for runner_id in sorted_runners_rungg]

    runner_pb_data = {runner[0]: f"{runner[12]}" for runner in runners_values}
    sorted_pbs = [runner_pb_data[runner_id] for runner_id in sorted_runners]

    runner_impr_data = {runner[0]: f"{runner[13]}" for runner in runners_values}
    sorted_imprs = [runner_impr_data[runner_id] for runner_id in sorted_runners]

    runner_bpt_data = {runner[0]: f"{runner[17]}" for runner in runners_values}
    sorted_bpts = [runner_bpt_data[runner_id] for runner_id in sorted_runners]

    runner_sob_data = {runner[0]: f"{runner[18]}" for runner in runners_values}
    sorted_sobs = [runner_sob_data[runner_id] for runner_id in sorted_runners]

    carousel_runners, carousel_items, fun_facts = generate_carousel_items(race_data[0], sorted_runners, delta_data, sorted_pbs, sorted_imprs, interval_data, sorted_bpts, sorted_sobs, funFacts)

    return render_template('layout_3P_race.html', spreadsheet_id = spreadsheet_id, automarathon_host = automarathon_host, runnerdata = runnerdata, carousel_runners=carousel_runners, carousel_items = carousel_items, fun_facts = fun_facts)


@app.route('/opener')
def opener():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    automarathon_host = request.args.get('automarathon_host')
    race_data, runners_values = get_race_information(spreadsheet_id)
    
    racename = race_data[0]
    runnernames = [f"({runners_values[i][1]}) {runners_values[i][0]}" for i in range(3)]
    if all(r[23] == "US" for r in runners_values):
        flags = [get_state_flag_url(runners_values[i][24]) for i in range(3)]
    else:
        flags = [get_country_flag_url(runners_values[i][23]) for i in range(3)]
    runnerdata = {'runnernames': runnernames,'flags': flags}

    return render_template('opener.html', spreadsheet_id = spreadsheet_id, automarathon_host = automarathon_host, racename = racename, runnerdata = runnerdata)



@app.route('/summary')
def summary():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    automarathon_host = request.args.get('automarathon_host')
    race_data, runners_values = get_race_information(spreadsheet_id)
    
    racename = race_data[0]
    runnernames = [f"({runners_values[i][1]}) {runners_values[i][0]}" for i in range(3)]
    if all(r[23] == "US" for r in runners_values):
        flags = [get_state_flag_url(runners_values[i][24]) for i in range(3)]
    else:
        flags = [get_country_flag_url(runners_values[i][23]) for i in range(3)]
    runnerdata = {'runnernames': runnernames,'flags': flags}

    runnerimages = []
    for runner in runners_values:
        runnerimages.append(runner[5])
    

    return render_template('summary.html', spreadsheet_id = spreadsheet_id, automarathon_host = automarathon_host, racename = racename, runnerdata = runnerdata, runnerimages = runnerimages)



@app.route('/recheck_data_new')
def recheck_data_new():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    race_data, runners_values = get_race_information(spreadsheet_id)
    funFacts = race_data[7].split('.')[:-1]
    #print(runners_values)

    runners = []
    for runner in runners_values:            
        runners.append(runner[4])

    delta_data, sorted_runners_rungg = get_delta_times(race_data[1], spreadsheet_id, runners)
    interval_data, _ = get_delta_times(race_data[1], spreadsheet_id, runners, True)
    #map rungg from sorted runners back to their display names
    runner_display_names = {runner[4].upper(): f"{runner[0]}" for runner in runners_values}
    sorted_runners = [runner_display_names[runner_id.upper()] for runner_id in sorted_runners_rungg]

    runner_pb_data = {runner[0]: f"{runner[12]}" for runner in runners_values}
    sorted_pbs = [runner_pb_data[runner_id] for runner_id in sorted_runners]

    runner_impr_data = {runner[0]: f"{runner[13]}" for runner in runners_values}
    sorted_imprs = [runner_impr_data[runner_id] for runner_id in sorted_runners]

    sorted_bpts = []
    for runner_rungg in sorted_runners_rungg:
        sorted_bpts.append(get_runner_bpt(race_data[1], runner_rungg))
        
    sorted_sobs = []
    for runner_rungg in sorted_runners_rungg:
        sob = get_runner_sob(runner_rungg)
        sorted_sobs.append(sob)
        #write_sob_by_rungg(spreadsheet_id, runner_rungg, sob)

    carousel_runners, carousel_items, fun_facts = generate_carousel_items(race_data[0], sorted_runners, delta_data, sorted_pbs, sorted_imprs, interval_data, sorted_bpts, sorted_sobs, funFacts)   

    return jsonify({'carousel_runners' : carousel_runners, 'carousel_items' : carousel_items})

@app.route('/check_final')
def check_final():
    spreadsheet_id = request.args.get('spreadsheet_id')
    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    
    race_info, runners_values = get_race_information(spreadsheet_id) 
    race_id = race_info[1]
    runner_runggs = [runners_values[int(runner)][4] for runner in range(3)]
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
    isTopRung = race_info[4] == "True"
    isBottomRung = race_info[5] == "True"
    isQualifier = race_info[6] == "True"
    

    final_time = get_final_time(race_id, runner_rungg)
    final_time_icon = "https://drive.google.com/thumbnail?id=15ubkMalyP-rHUkO4NVe14sTrip34-jO3"
    if (final_time != 1e8):
        position = get_position(race_id, final_time)        
        if (isQualifier and (position == 1 or (position == 2 and len(runners_values) == 3))):
            final_time_icon = "https://drive.google.com/thumbnail?id=16-lBbCrLgAG5u3L5f2mRESTu6ONzMy6A"
        elif (isQualifier):
            if (len(runners_values) == 2):
                final_time_icon = "https://drive.google.com/thumbnail?id=15yd1Sae7tB9OZLQgHMU56ROl2ZQCYnvb"
            else:
                final_time_icon = "https://drive.google.com/thumbnail?id=16-wst51zvLrZ-hpxyeD68qRsfABBtB_y"
        elif (isTopRung and position == 1):
            final_time_icon = "https://drive.google.com/thumbnail?id=16-lBbCrLgAG5u3L5f2mRESTu6ONzMy6A"
        elif (isTopRung and not isBottomRung and position == 2):
            final_time_icon = "https://drive.google.com/thumbnail?id=15yd1Sae7tB9OZLQgHMU56ROl2ZQCYnvb"
        elif (not isTopRung and (position == 1 or position == 2)):
            if (position == 1):
                final_time_icon = "https://drive.google.com/thumbnail?id=165dA-f7dY1vpYU0Nwpxu9qh7H_fUN9u-"
            else:
                final_time_icon = "https://drive.google.com/thumbnail?id=165dA-f7dY1vpYU0Nwpxu9qh7H_fUN9u-"#"https://drive.google.com/thumbnail?id=164hSZlm6bK9XAtdfFRSXEJorT_O6a1o-"      
        elif (isBottomRung):
            final_time_icon = "https://drive.google.com/thumbnail?id=16-wst51zvLrZ-hpxyeD68qRsfABBtB_y"     
        else:
            final_time_icon = "https://drive.google.com/thumbnail?id=161VlRHWSVv8bzjS9h40PaymYHiZ4fqPG"

    
        record = runners_values[int(runner)][20]
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
        final_time = ""
        record_string = ""

    return jsonify({"final_time": final_time, "final_time_icon": final_time_icon, "record" : record_string, "best_time" : best_time, "average_time" : average_time })





@app.route('/recheck_data')
def recheck_data():
    spreadsheet_id = request.args.get('spreadsheet_id')
    once = request.args.get('once')
    if spreadsheet_id is None or spreadsheet_id == '':
        return render_template('error.html', message='Please provide a valid spreadsheet_id')


    race_data, runners_values = get_race_information(spreadsheet_id)

    #update data from therun (sob)
    if (once == "True"):  
        runners = []
        for idx, runner in enumerate(runners_values):            
            rungg = runner[4]
            runners.append(rungg)
            sob = get_runner_sob(rungg)
            if sob != "--:--:--":
                write_sob(spreadsheet_id, idx, sob)

                bpt = get_runner_bpt(race_data[1], rungg)
                write_bpt(spreadsheet_id, idx, bpt)
                          
                final_time = get_final_time(race_data[1], rungg)
                if (final_time != 1e8):
                    position = get_position(race_data[1], final_time)
                    if (position != 0):
                        write_final_time(spreadsheet_id, idx, str(final_time), runners_values[idx][1], position, runners_values[idx][18])

        delta_times = get_delta_times(race_data[1], spreadsheet_id, runners)
        write_delta_times(spreadsheet_id, delta_times)

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
    print(runners_values)
    if all(r[23] == "US" for r in runners_values):
        return render_template('runnername_state.html', text_content = f"({runners_values[int(runner)][1]}) {runners_values[int(runner)][0]}", state_flag_url = get_country_flag_url(runners_values[int(runner)][23]))
    else:
        return render_template('runnername_country.html', text_content = f"({runners_values[int(runner)][1]}) {runners_values[int(runner)][0]}", country_code = get_country_flag_url(runners_values[int(runner)][23]))



@app.route('/runner_overlay')
def runner_overlay():
    spreadsheet_id = request.args.get('spreadsheet_id')
    runner = request.args.get('runner')
    if (runner == "Test"):
        return render_template('overlay.html',spreadsheet_id = spreadsheet_id,  runner_data=['a'],   result_string = "Test", text_color = "#EE4266", final_time = format_milliseconds(12345678))

    if spreadsheet_id is None:
        # Render a template with the error message
        return render_template('error.html', message='Please provide a valid spreadsheet_id')
    race_info, runners_values = get_race_information(spreadsheet_id) 
    race_id = race_info[1]
    runner_rungg = runners_values[int(runner)][4]
    isTopRung = race_info[4] == "True"
    isBottomRung = race_info[5] == "True"
    isQualifier = race_info[6] == "True"
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
            elif (not isTopRung and (position == 1 or (position == 2 and not isBottomRung ))):
                result = "PROMOTED"
                text_color = "#337357"
            elif (isBottomRung):
                result = "ELIMINATED"
                text_color = "#EE4266"
            else:
                result = "DEMOTED"
                text_color = "#5E1675"

    return render_template('overlay.html', spreadsheet_id = spreadsheet_id, runner_data=runners_values, result_string = result, text_color = text_color,  final_time = format_milliseconds(final_time))
    



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
