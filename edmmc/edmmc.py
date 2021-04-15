import os
import sys
import time
# get source file directory so that the program can be executable from anywhere
# dir_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
# sys.path.append(dir_root)
import json
from readlog import ReadLog, cg
from constructors import MassacreMissions, Labels
from gui import tk

# FIXME: this way of restarting only works if this program is run alongside with ED every time
# with open("test_log.txt", "r") as f:
#     missions = MassacreMissions.from_json(f.read())
rl = ReadLog()
class MassacreCompanion:

    def __init__(self):
        self.initialized = False
        self.missions = MassacreMissions([], {}, "", 0, 0, 0, {})
        rl.check_ed_log_path()
        cg.status_bar(rl.label_texts.ed_status, rl.label_texts.current_log_status, rl.label_texts.total_reward)
        self.refresh_int = 3000

    def update(self):
        if self.initialized:
            rl.update(self.missions, self.initialized)
        else:
            rl.find_journals(self.initialized)
            try:
                self.initialized = rl.initialize(rl.current_log, self.missions,
                    self.initialized)
            except RuntimeError:
                rl.label_texts.current_log_status.set("Waiting for log file update")
        cg.window.after(self.refresh_int, self.update)

    def run(self):
        cg.window.after(self.refresh_int, self.update)
        cg.window.mainloop()
        with open("data/edmmc_history.txt", "w") as out:
            json.dump(self.missions.to_dict(), out, indent=4)

mc = MassacreCompanion()
mc.run()