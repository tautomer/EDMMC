import os
import sys
import time
# get source file directory so that the program can be executable from anywhere
# dir_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
# sys.path.append(dir_root)
import json
from readlog import ReadLog, cg
from constructors import MassacreMissions

# FIXME: this way of restarting only works if this program is run alongside with ED every time
# with open("test_log.txt", "r") as f:
#     missions = MassacreMissions.from_json(f.read())
rl = ReadLog()
missions = MassacreMissions([], {}, "", 0, 0, 0, {})
initialized = False
rl.check_ed_log_path()
rl.find_journals(initialized)
while True:
    try:
        initialized = rl.initialize(rl.current_log, missions, initialized)
    except RuntimeError:
        # TODO: also need check this when a new log is found
        os.system('cls') 
        print("The current log is empty. Waiting for log updates when the game is continued.")
        time.sleep(3)
    else:
        break

# rl.sanity_check(missions)
def update():
    rl.update(missions, initialized)
    cg.window.after(3000, update)
cg.window.after(3000, update)
cg.window.mainloop()
with open("test_log.txt", "w") as out:
    json.dump(missions.to_dict(), out, indent=4)