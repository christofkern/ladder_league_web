class LocalRunnerData:
    def __init__(self):
        # Instance variables for storing runner data
        self.race_name = ""
        self.therun_race_id = ""
        self.runner_names = ["", "", ""]
        self.runner_countries = ["", "", ""]
        self.runner_runggs = ["", "", ""]
        self.runner_gold_times = ["", "", ""]
        self.runner_sobs = ["", "", ""]
        self.runner_pbs = ["", "", ""]
        self.runner_improvements_since_seeding = ["", "", ""]
        self.override_therun = False
        self.runner_final_times = ["", "", ""]

    def everything_static_overriden(self):
        if (self.race_name != "" and all(runner_name != "" for runner_name in self.runner_names) and all(country != "" for country in self.runner_countries)):
            print(self.race_name)
            return True
        return False