import os
import sys
# get source file directory so that the program can be executable from anywhere
# dir_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
# sys.path.append(dir_root)
import glob
import json
import time
from typing import IO
from dateutil.parser import parse
from collections import deque
from main import MassacreMissions as mm
from main import FactionMissions as fm

class ReadLog:

    def __init__(self):
        self.log_path = ""
        self.current_log = ""
        self.log_2days = []
        self.log_7days = []
        self.is_game_running = True
        self.current_missions = {}
        self.current_massacre_missions = []
        self.mission_id = {}
        self.rm_key_list = ["event", "Name", "LocalisedName", "TargetType",
            "DestinationStation", "Influence", "Reputation"]

    def check_ed_log_path(self):
        """find ED log path and client status
        """
        home = os.path.expanduser("~")
        ed_save = home + "\Saved Games\Frontier Developments\Elite Dangerous"
        # TODO: user specified save path
        if not os.path.isdir(ed_save):
            print("wrong path")
            exit
        self.log_path = ed_save

    def find_journals(self):
        """find the latest journal and journals in the past 7 days for resumed misisons
        """
        journals = glob.glob(self.log_path + "\Journal.*.log")
        journals.sort(key=os.path.getmtime, reverse=True)
        latest = journals.pop(0)
        self.current_log = open(latest, "rt")
        # TODO: is there a saner way to do this?
        ctime = os.path.getctime(latest)
        for i in journals:
            mtime = os.path.getmtime(i)
            dt = ctime - mtime
            if dt <= 172_800:
                self.log_2days.append(i)
            elif dt <= 604_800:
                self.log_7days.append(i)
            else:
                break

    def find_resumed_missions(self, event):
        """find all existing missions at startup

        Args:
            event (string): string contains the ED evernt in json
        """
        mission_status = ["Active", "Failed", "Complete"]
        for istatus in mission_status:
            if len(event[istatus]) != 0:
                for mission in event[istatus]:
                    if "Massacre" in mission["Name"]:
                        # if "Wing" in mission["name"]:
                        #     is_wing = True
                        # else:
                        #     is_wing = False
                        # mission["Status"] = istatus
                        self.current_missions[mission['MissionID']] = istatus

    def find_mission_details(self, massacre_missions: mm):
        # try to find mission details within 2-day old logs
        for journal in self.log_2days:
            with open(journal, 'r') as log:
                self.read_event(log, massacre_missions, True)
        # non-wing missions accepted more than 2 days old should have been failed
        for m in massacre_missions.missions.values():
            if not m["Wing"]:
                self.current_missions.pop(m["MissionID"])
        for journal in self.log_2days:
            with open(journal, 'r') as log:
                self.read_event(log, massacre_missions, True)
        # TODO: should check if this part is done properly
        self.current_missions = {}

    def mission_accepted(self, id: int, mission: dict, massacre_missions: mm):
        # there could be multiple resumed sessions
        if id in massacre_missions.mission_ids:
            return
        # get rid of useless items
        [mission.pop(_) for _ in self.rm_key_list]
        # add my own status
        mission["Status"] = self.current_missions[id]
        # convert both starting and ending time to Unix timpstamps
        mission["timestamp"] = parse(mission["timestamp"]).timestamp() 
        mission["Expiry"] = parse(mission["Expiry"]).timestamp() 
        # current progress
        # TODO: this should be also read from input or history
        mission["Progress"] = 0
        faction = mission["Faction"]
        # add faction-specific information
        if faction not in massacre_missions.factions:
            massacre_missions.factions[faction] = fm(1, mission["KillCount"],
                mission["Progress"], [id], [], [])
        else:
            massacre_missions.factions[faction].mission_count += 1
            massacre_missions.factions[faction].kill_count += mission["KillCount"]
            massacre_missions.factions[faction].progress += mission["Progress"]
            massacre_missions.factions[faction].running.append(id)
        # add modified mission details to dictionary
        massacre_missions.missions[id] = mission
        # add to id list for easy check
        massacre_missions.mission_ids.append(id)

    def mission_redirected(self, id, mission, massacre_missions):
        pass

    def mission_completed(self, id, massacre_missions):
        pass

    def mission_failed(self, id, massacre_missions):
        pass

    def mission_abandoned(self, id, massacre_missions):
        pass

    def read_event(self, log: IO, missions: mm, historical: bool):    
        # initialize missions
        events = log.readlines()
        if '"event":"Shutdown"' in events[-1]:
            self.is_game_running = False
        else:
            self.is_game_running = True
        for event in events:
            # game logs all current missions at startup
            if '"event":"Missions"' in event:
                if not historical:
                    current_missions = json.loads(event)
                    # log_time = parse(current_missions['timestamp']).timestamp()
                    self.find_resumed_missions(current_missions)
                    self.find_mission_details(missions)
                    break
            elif "Mission_Massacre" in event:
                mission = json.loads(event)
                id = mission["MissionID"] 
                if '"event":"MissionAccepted"' in event:
                    if id in self.current_missions:
                        self.mission_accepted(id, mission, missions)
                    elif not historical:
                        pass
                elif '"event":"MissionRedirected"' in event:
                    if id in self.current_missions:
                        self.mission_redirected(id, mission, missions)
                    elif not historical:
                        pass
                elif '"event":"MissionCompleted"' in event:
                    self.mission_completed(id, missions)
        return missions

rl = ReadLog()
rl.check_ed_log_path()
rl.find_journals()
missions = mm([], {}, 0, {})
missions = rl.read_event(rl.current_log, missions, False)
for k,v in missions.factions.items():
    print(k, v.mission_count, v.kill_count, v.running)