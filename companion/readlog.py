import os
import sys
import glob
import json
# import ujson as json
import time
from typing import IO, Union
from dataclasses_json.api import dataclass_json
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from typing import List, Dict
from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class FactionMissions:
    mission_count: int 
    kill_count: int
    progress: int
    running: List[int]
    ready: List[int]
    past: List[int]

@dataclass_json
@dataclass
class MassacreMissions:
    mission_ids: List[int]
    factions: Dict[str, FactionMissions]
    target_faction: str
    pirates_killed: int
    target_faction_pirates_killed: int
    total_bounty_claimed: int
    missions: Dict[int, Dict]

class ReadLog:

    def __init__(self):
        self.log_path = ""
        self.current_log = IO
        self.current_log_name = ""
        self.log_time = 0
        self.log_7days = []
        self.is_game_running = False
        self.sanity = True
        self.past_missions = False
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

    def find_journals(self, initialized: bool):
        """find the latest journal and journals in the past 7 days for resumed misisons
        """
        # FIXME: this way of checking new files is way too bad
        # TODO: `glob` could be slow
        journals = glob.glob(self.log_path + "\Journal.*.log")
        journals.sort(key=os.path.getmtime, reverse=True)
        latest = journals.pop(0)
        if self.current_log_name != latest:
            self.current_log_name = latest
            if not self.current_log:
                self.current_log.close()
            self.current_log = open(latest, "r")
            self.is_game_running = True
        # TODO: is there a saner way to do this?
        if not initialized:
            ctime = os.path.getctime(latest)
            for i in journals:
                mtime = os.path.getmtime(i)
                dt = ctime - mtime
                # if dt <= 172_800:
                #     self.log_2days.append(i)
                if dt <= 604_800:
                    self.log_7days.append(i)
                else:
                    break
            self.log_7days.reverse()

    def check_ed_status(self, event: str):
        # check if the game is running
        if '"event":"Shutdown"' == event[38:56]:
            self.is_game_running = False
        else:
            self.is_game_running = True

    def initialize(self, log: IO, missions: MassacreMissions, initialized: bool):
        # have to store the current log in RAM
        # TODO: possbily avoid this way?
        events = log.readlines()
        if not events:
            raise RuntimeError
        self.check_ed_status(events[-1])
        ln = 0
        # find the latest login event for existing missions
        for line in reversed(events):
            ln += 1
            if '"event":"Missions"' in line:
                current_missions = json.loads(line)
                self.log_time = parse(current_missions['timestamp']).timestamp()
                # grab all mission ID's
                self.find_resumed_missions(current_missions)
                # find mission details in old journals
                self.find_mission_details(missions)
                # mark initialized as done
                initialized = True
                break
        if not initialized:
            raise RuntimeError
        # every entry before the restarting will be useless
        cut = len(events) - ln + 1
        # check possible mission events before resume in current log
        self.read_event(events[:cut-1], missions, False)
        # check all new mission and bounty events
        self.read_event(events[cut:], missions, initialized)
        # self.cleanup(missions)
        return initialized

    def find_resumed_missions(self, event: dict):
        """find all existing missions at startup

        Args:
            event (string): string contains the ED evernt in json
        """
        mission_status = ["Active", "Failed", "Complete"]
        for istatus in mission_status:
            if len(event[istatus]) != 0:
                for mission in event[istatus]:
                    mission_name = mission["Name"]
                    if "Massacre" in mission_name:
                        # find the starting timestamp for missions
                        if "Wing" in mission_name:
                            start = self.log_time - 604_800 + mission["Expires"]
                        else:
                            start = self.log_time - 172_800 - mission["Expires"]
                        self.current_missions[mission['MissionID']] = start

    def find_mission_details(self, massacre_missions: MassacreMissions):
        try:
            oldest_mission = min(self.current_missions.values())
            for journal in self.log_7days:
                if os.path.getmtime(journal) >= oldest_mission:
                    with open(journal, 'r') as log:
                        self.read_event(log, massacre_missions, False)
        except ValueError:
            print("Empty mission list")

    def mission_accepted(self, id: int, mission: dict, massacre_missions: MassacreMissions):
        # there could be multiple resumed sessions
        if id in massacre_missions.mission_ids:
            return
        # get rid of useless items
        for i in self.rm_key_list:
            try:
                mission.pop(i)
            # TODO: there are massacre mission on clean ships when war state
            except KeyError:
                pass
        if not massacre_missions.target_faction:
            massacre_missions.target_faction = mission["TargetFaction"]
        # add my own status
        mission["Status"] = "Active"
        # convert both starting and ending time to Unix timpstamps
        mission["timestamp"] = parse(mission["timestamp"]).timestamp() 
        mission["Expiry"] = parse(mission["Expiry"]).timestamp() 
        # current progress
        # TODO: this should be also read from input or history
        mission["Progress"] = 0
        faction = mission["Faction"]
        # add faction-specific information
        if faction not in massacre_missions.factions:
            massacre_missions.factions[faction] = FactionMissions(1,
                mission["KillCount"], mission["Progress"], [id], [], [])
        else:
            massacre_missions.factions[faction].mission_count += 1
            massacre_missions.factions[faction].kill_count += mission["KillCount"]
            massacre_missions.factions[faction].progress += mission["Progress"]
            massacre_missions.factions[faction].running.append(id)
        # add to id list for easy check
        massacre_missions.mission_ids.append(id)
        # add modified mission details to dictionary
        massacre_missions.missions[id] = mission

    def mission_redirected(self, id, redirection, massacre_missions):
        # find mission details based on mission ID
        mission = massacre_missions.missions[id]
        # update mission status
        mission["Status"] = "Done"
        mission["DestinationSystem"] = redirection["NewDestinationSystem"]
        # check progess and kill counts
        progress = mission["Progress"]
        kill_count = mission["KillCount"]
        # find mission faction info
        faction = massacre_missions.factions[mission["Faction"]]
        # update faction info
        faction.running.remove(id)
        faction.ready.append(id)
        # if there is any discrepancy
        if progress != kill_count:
            self.sanity = False
            print("Discrepancy in mission progress detected. Update information "
                "based on ED log.")
            delta = kill_count - progress
            mission["Progress"] = kill_count
            faction.progress += delta
    
    # TODO: seems `completed` and `failed` can be merged
    def mission_completed(self, id: int, massacre_missions: MassacreMissions):
        # find mission details based on mission ID
        mission = massacre_missions.missions[id]
        # update mission status
        mission["Status"] = "Claimed"
        # find mission faction info
        faction = massacre_missions.factions[mission["Faction"]]
        # update faction info
        faction.ready.remove(id)
        faction.past.append(id)
        self.past_missions = True

    def mission_failed(self, id: int, massacre_missions: MassacreMissions, status: str):
        # find mission details based on mission ID
        mission = massacre_missions.missions[id]
        # update mission status
        mission["Status"] = status
        # find mission faction info
        faction = massacre_missions.factions[mission["Faction"]]
        # update faction info
        # TODO: normally I'm not this stupid to abandon finished missions, so better go with try/except
        if id in faction.running:
            faction.running.remove(id)
        if id in faction.ready:
            faction.ready.remove(id)
        faction.past.append(id)
        self.past_missions = True

    # TODO: does killing in another system count?
    def bounty_awarded(self, bounty: dict, massacre_missions: MassacreMissions):
        massacre_missions.pirates_killed += 1
        massacre_missions.total_bounty_claimed += bounty["TotalReward"]
        if bounty["VictimFaction"] == massacre_missions.target_faction:
            massacre_missions.target_faction_pirates_killed += 1
            for i in massacre_missions.factions.values():
                if len(i.running) != 0:
                    i.progress += 1
                    massacre_missions.missions[i.running[0]]["Progress"] += 1

    def read_event(self, events: Union[IO, list], missions: MassacreMissions, initialized: bool):    
        # initialize missions
        for event in events:
            # find mission information related to massacre missions
            if "Mission_Massacre" in event:
                if '"event":"Missions"' == event[38:56]:
                    continue
                mission = json.loads(event)
                id = mission["MissionID"] 
                if not initialized and id not in self.current_missions:
                    continue
                status = mission["event"].split("Mission", 1)[1]
                if status == "Accepted":
                    self.mission_accepted(id, mission, missions)
                elif status == "Redirected":
                    self.mission_redirected(id, mission, missions)
                elif status == "Completed":
                    self.mission_completed(id, missions)
                else:
                    # for failed or abondoned missions
                    self.mission_failed(id, missions, status)
            # find event for pirates killeed
            elif initialized:
                if '"event":"Bounty"' in event:
                    bounty = json.loads(event)
                    self.bounty_awarded(bounty, missions)
                else:
                    self.check_ed_status(event)

    def discard_past_missions(self, missions: MassacreMissions):
        for f in missions.factions.values():
            if len(f.past) != 0:
                for id in f.past:
                    details = missions.missions.pop(id)
                    missions.mission_ids.remove(id)
                    kill_count = details["KillCount"]
                    progress = details["Progress"]
                    f.kill_count -= kill_count 
                    f.progress -= progress
                    f.mission_count -= 1
                f.past.clear()
        self.past_missions = False

    def update(self, missions: MassacreMissions, initialized: bool):
        # only check if there are new journals when ED is not running
        # FIXME: this way isn't able to handle game crash
        if not self.is_game_running:
            self.find_journals(initialized)
        else:
            # read log file updates
            new_events = self.current_log.readlines()
            # if there are new events
            if len(new_events) != 0:
                self.check_ed_status(new_events[-1])
                self.read_event(new_events, missions, initialized)
            self.cleanup(missions)

    def cleanup(self, missions: MassacreMissions):
        if self.past_missions:
            self.discard_past_missions(missions)
        if not self.sanity:
            pass
            # self.sanity_check(missions)

    def sanity_check(self, massacre_missions: MassacreMissions):
        print(" There are discrepancies in mission progress being detected.",
            "Please consider maunally update all mission progesses by",
            "providing information in the prompt below. You can skip this by",
            "leaving all input blank.")
        for i in massacre_missions.missions.values():
            prompt = "Mission information:\nFaction name: " + i["Faction"] + \
                "\nMission kill count: " + str(i["KillCount"]) + "\nCurrently logged " + \
                "mission progress: " + str(i["Progress"]) + "\nActual progess shown " + \
                "in-game: " 
            try:
                progress = int(input(prompt))
                delta = progress - i["Progress"] 
                i["Progress"] = progress
                faction = i["Faction"]
                massacre_missions.factions[faction].progress -= delta
            except ValueError:
                print("Invalid input. Progress unchanged.")
            self.sanity = True
