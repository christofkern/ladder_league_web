class LocalRunnerData:
    # Class variables for storing runner data
    race_name = ""
    runner_names = ["", "", ""]
    runner_countries = ["", "", ""]
    runner_runggs = ["", "", ""]
    override_runner_positions = [0, 0, 0]
    override_runner_split_times = [[], [], []]
    override_runner_sobs = ["", "", ""]
    override_runner_bpts = ["", "", ""]
    override_runner_improvements_since_seeding = ["", "", ""]
    override_runner_pbs = ["", "", ""]

    def everything_static_overriden():
        if (LocalRunnerData.race_name != "" and all(runner_name != "" for runner_name in LocalRunnerData.runner_names) and all(country != "" for country in LocalRunnerData.runner_countries)):
            print(LocalRunnerData.race_name)
            return True
        return False
    
