import os
import sys
import time
# get source file directory so that the program can be executable from anywhere
# dir_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
# sys.path.append(dir_root)
from readlog import ReadLog
from readlog import MassacreMissions
rl = ReadLog()
missions = MassacreMissions([], {}, "", 0, 0, 0, {})
initialized = False
rl.check_ed_log_path()
rl.find_journals(initialized)
initialized = rl.initialize(rl.current_log, missions, initialized)
print(missions.mission_ids)
for k,v in missions.factions.items():
    print(k, v.mission_count, v.progress, v.kill_count, v.running, v.past)
while True:
    rl.update(missions, initialized)
    os.system('cls') 
    for k,v in missions.factions.items():
        if v.mission_count != 0:
            print(k, v.mission_count, v.progress, v.kill_count, v.running, v.past)
    time.sleep(3)