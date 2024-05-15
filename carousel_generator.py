
def generate_carousel_items(sorted_runners, delta_data, interval_data):

    stats = {
        "DELTA":delta_data,
        "PERSONAL BEST": ['-','-','-'],
        "IMPROVEMENT": ['-','-','-'],
        "delta":interval_data,
        "BEST POSSIBLE TIME": ['-','-','-'],
        "SUM OF BEST SEGMENTS": ['-','-','-'],        
    }

    
    carousel_items = ''
    for idx,stat in enumerate(stats):
        active = ''
        if (idx == 0):
            active = 'active'
        carousel_items += f'''
        <div class="carousel-item {active}">
            <div class="container" style="width:100%; text-align: center; color:#cacacb;">
                <div class="row pt-4">
                    <h3><b>{stat.upper()}</b></h3>
                </div>
                <div class="row pt-3">
                    <div class="col-4">
                        <h3>&nbsp</h3>
                        <h3>{stats[stat][0]}</h3>
                    </div>
                    <div class="col-4">
                        <h3>&nbsp</h3>
                        <h3>{stats[stat][1]}</h3>
                    </div>
                    <div class="col-4">
                        <h3>&nbsp</h3>
                        <h3>{stats[stat][2]}</h3>
                    </div>
                </div>
            </div>
        </div>
        '''
        carousel_runners = f'''
        <div class="carousel-overlay">
            <div class="carousel-overlay-item">
                <h3>{sorted_runners[0]}</h3>
            </div>
            <div class="carousel-overlay-item">
                <h3>{sorted_runners[1]}</h3>
            </div>
            <div class="carousel-overlay-item">
                <h3>{sorted_runners[2]}</h3>
            </div>
        </div>
        '''
    return carousel_runners, carousel_items