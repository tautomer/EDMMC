import os
import sys
import time
# get source file directory so that the program can be executable from anywhere
# dir_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
# sys.path.append(dir_root)
import json
from readlog import ReadLog
from readlog import MassacreMissions

rl = ReadLog()
missions = MassacreMissions([], {}, "", 0, 0, 0, {})
initialized = False
rl.check_ed_log_path()
rl.find_journals(initialized)
while True:
    try:
        initialized = rl.initialize(rl.current_log, missions, initialized)
    except RuntimeError:
        os.system('cls') 
        print("The current log is empty. Waiting for log updates when the game is continued.")
        time.sleep(3)
    else:
        break

# rl.sanity_check(missions)
rl.update(missions, initialized)
print(missions.target_faction_pirates_killed)
for k, v in missions.factions.items():
    print(v.progress, v.kill_count, k, v.mission_count)
    for i in v.running:
        print("    ", missions.missions[i]["Progress"], missions.missions[i]["KillCount"])
    # print(k, v.mission_count, v.progress, v.kill_count, v.running, v.past)
while True:
    try:
        rl.update(missions, initialized)
        os.system('cls') 
        for k,v in missions.factions.items():
            if v.mission_count != 0:
                print(k, v.mission_count, v.progress, v.kill_count)
            for i in v.running:
                print("    ", missions.missions[i]["Wing"], missions.missions[i]["Progress"], missions.missions[i]["KillCount"])

        print("Target faction pirates killed:", missions.target_faction_pirates_killed)
        print("Total pirates killed:", missions.pirates_killed)
        # TODO: larger interval if game isn't running. this value should be configurable ultimately
        if not rl.is_game_running:
            print("ED client is not running currently.")
        time.sleep(3)
    except KeyboardInterrupt:
        # TODO: wrap this part in a function, together with reading
        with open("test_log.txt", "w") as out:
            json.dump(missions.to_dict(), out, indent=4)
        break