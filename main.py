import os
import glob
import json
import time
from dateutil.parser import parse
from dataclasses import dataclass

# @dataclass
# class MassacreMission:
#     id: int
#     status: str
#     faction: str
#     target_faction: str
#     target_type: str
#     system: str
#     kill_count: int
#     progess: str 
#     reward: int
#     iswing: bool
#     starting_time: int
#     remaining_time: int
# 
@dataclass
class FactionMissions:
    mission_count: int 
    kill_count: int
    progress: int
    running: list[int]
    completed: list[int]
    failed: list[int]

@dataclass
class MassacreMissions:
    mission_ids: list[int]
    factions: dict[FactionMissions]
    total_bounty_claimed: int
    missions: dict[dict]

journals = glob.glob('../Journal.*.log')
latest_journal = max(journals, key=os.path.getctime)
log = open(latest_journal, "r", encoding='UTF-8').readlines()

# check if the client is running
if log[-1].find('"event":"Shutdown"') != -1:
    is_game_running = False
else:
    is_game_running = True

# check log line by line for all current missions

def find_massacre_missions(event):
    mission_status = ['Active', 'Failed', 'Complete']
    current_massacre_missions = []
    for istatus in mission_status:
        if len(event[istatus]) != 0:
            for mission in event[istatus]:
                if 'Massacre' in mission['Name']:
                    del mission['PassengerMission']
                    mission['Status'] = istatus
                    current_massacre_missions.append(mission)
    return current_massacre_missions

for event in log:
    # game logs all current missions at startup
    if '"event":"Missions"' in event:
        current_missions = json.loads(event)
        log_time = parse(current_missions['timestamp']).timestamp()
        current_massacre_missions = find_massacre_missions(current_missions)
    
    if '"event":"MissionAccepted"' in event and 'Mission_Massacre' in event:
        new_mission = json.loads(event)

# discovered_systems = []
# n_discovered_bodies = []
# for logfile in glob.glob('Journal.*.log'):
#     log = open(logfile, "r", encoding='UTF-8').readlines()
#     for event in log:
#         if event.find('MultiSellExplorationData') != -1:
#             print("Selling exploration data event found in", logfile)
#             sold_data = json.loads(event)
#             discovered = sold_data['Discovered']
#             if len(discovered) != 0:
#                 for i in discovered:
#                     discovered_systems.append(i['SystemName'])
#                     n_discovered_bodies.append(i['NumBodies'])
# 
# print(len(discovered_systems))