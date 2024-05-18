
def generate_carousel_items(racename, sorted_runners, delta_data, sorted_pbs, sorted_imprs, interval_data, sorted_bpts, sorted_sobs, funFacts):

    stats = {
        "TITLE":[],
        "RACE DELTA":delta_data,
        "PERSONAL BEST": sorted_pbs,
        "IMPROVEMENT SINCE SEEDING": sorted_imprs,
        "RACE delta":interval_data,
        "SUM OF BEST SEGMENTS": sorted_sobs,    
        "BEST POSSIBLE TIME": sorted_bpts,    
    }

    
    carousel_items = ''
    for idx,stat in enumerate(stats):
        color_class_first = ''
        color_class_behind = ''
        runner1 = '&nbsp'
        runner2 = '&nbsp'
        runner3 = '&nbsp'

        if (idx == 1 or idx == 6):
            runner1 = sorted_runners[0]
            runner2 = sorted_runners[1]
            runner3 = sorted_runners[2]


        if (stat.upper() == "DELTA"):
            color_class_first = 'runner-first'
            color_class_behind = 'runner-behind'

        if (stat == "TITLE"):
            carousel_items += f'''
                             <div class='carousel-item active'>
                                <div class='container' >
                                    <div class='pt-4 carousel-header'>
                                        <b>{racename}</b>
                                    </div>
                                    <div class='pt-3 carousel-commands'>                                        
                                        <b>!runners !discord !tech</b>
                                        <br>
                                        <b>!schedule !predictions</b>
                                    </div>
                                </div>
                            </div>
                            '''
        else:    
            carousel_items += f'''
            <div class='carousel-item'>
                <div class='container' >
                    <div class='row pt-4 carousel-header'>
                        <b>{stat.upper()}</b>
                    </div>
                    <div class='row pt-3'>
                        <div class='col-4 {color_class_first}'>
                            <h3 class='carousel-runner'>{runner1}</h3>
                            <h3>{stats[stat][0]}</h3>
                        </div>
                        <div class='col-4 {color_class_behind}'>
                            <h3 class='carousel-runner'>{runner2}</h3>
                            <h3>{stats[stat][1]}</h3>
                        </div>
                        <div class='col-4 {color_class_behind}'>
                            <h3 class='carousel-runner'>{runner3}</h3>
                            <h3>{stats[stat][2]}</h3>
                        </div>
                    </div>
                </div>
            </div>
            '''
        carousel_runners = f'''
        <div class='carousel-overlay'>
            <div class='carousel-overlay-item invisible'>
                <h3>{sorted_runners[0]}</h3>
            </div>
            <div class='carousel-overlay-item invisible'>
                <h3>{sorted_runners[1]}</h3>
            </div>
            <div class='carousel-overlay-item invisible'>
                <h3>{sorted_runners[2]}</h3>
            </div>
        </div>
        '''

        fun_facts = []
        for funFact in funFacts:
            fun_facts.append(f'''
                <div class="carousel-item funFact">
                    <div class="container">
                        <div class="row pt-4 carousel-header">
                            <b>Fun Fact</b>
                        </div>
                        <div class="row pt-3">
                            <div class="col-12">
                                <h3>{funFact}</h3>
                            </div>
                        </div>
                    </div>
                </div>
                ''')


    
    return carousel_runners, carousel_items, fun_facts
