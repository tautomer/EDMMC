import os
import sys
import glob
import json
# import ujson as json
from typing import Dict, IO, Union
from dateutil.parser import parse
from constructors import MassacreMissions, FactionMissions, DynamicalLabels
from constructors import Labels
from gui import CompanionGUI, tk

cg = CompanionGUI()
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
        self.rm_key_list = ["event", "Name", "LocalisedName", "Influence",
            "Reputation"]
        self.label_texts = DynamicalLabels({}, {}, tk.StringVar())

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
            self.label_texts.ed_status.set("ED client is running")
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
            self.label_texts.ed_status.set("ED client is NOT running")
        else:
            self.is_game_running = True
            self.label_texts.ed_status.set("ED client is running")

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
        # assign values to the labels
        cg.status_bar(self.label_texts.ed_status)
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
        mission["Expiry"] = int(parse(mission["Expiry"]).timestamp())
        # current Progress
        # TODO: this should be also read from input or history
        mission["Progress"] = 0
        faction_name = mission["Faction"]
        # add faction-specific information
        try:
            faction = massacre_missions.factions[faction_name]
        except KeyError:
            faction = FactionMissions(0, 0, 0, [], [], [], [])
            massacre_missions.factions[faction_name] = faction
            # create dynamical label text for this faction
            Labels.faction_label_text_setup(faction_name, self.label_texts)
            cg.add_faction(faction_name, self.label_texts.factions[faction_name])
        # only deal with missions with priates as the target
        if mission["TargetType_Localised"] == "Pirates":
            faction.KillCount += mission["KillCount"]
            faction.Progress += mission["Progress"]
            faction.running.append(id)
        else:
            faction.other.append(id)
        massacre_missions.factions[faction_name].mission_count += 1
        Labels.update_faction_label_text(faction_name, faction, self.label_texts)
        # add to id list for easy check
        massacre_missions.mission_ids.append(id)
        # add modified mission details to dictionary
        massacre_missions.missions[id] = mission
        # add dynamical label text for this mission
        Labels.mission_label_text_setup(id, mission, self.label_texts)
        cg.add_mission(id, faction_name, self.label_texts.missions[id],
            faction.mission_count)

    def mission_redirected(self, id: int, redirection: Dict, massacre_missions: MassacreMissions):
        # find mission details based on mission ID
        mission = massacre_missions.missions[id]
        faction_name = mission["Faction"]
        # update mission status
        mission["Status"] = "Done"
        mission["DestinationSystem"] = redirection["NewDestinationSystem"]
        mission["DestinationStation"] = redirection["NewDestinationStation"]
        self.label_texts.missions[id]["Status"]["textvariable"].set("Done")
        self.label_texts.missions[id]["System"]["textvariable"].set(mission["DestinationSystem"])
        self.label_texts.missions[id]["Station"]["textvariable"].set(mission["DestinationStation"])
        # check progess and kill counts
        progress = mission["Progress"]
        kill_count = mission["KillCount"]
        # find mission faction info
        faction = massacre_missions.factions[faction_name]
        # update faction info
        faction.running.remove(id)
        faction.ready.append(id)
        # if there is any discrepancy
        if progress != kill_count:
            self.sanity = False
            print("Discrepancy in mission Progress detected. Update information "
                "based on ED log.")
            delta = kill_count - progress
            mission["Progress"] = kill_count
            progress = str(mission["Progress"]) + "/" + str(kill_count)
            self.label_texts.missions[id]["Progress"]["textvariable"].set(progress)
            faction.Progress += delta
            Labels.update_faction_label_text(faction_name, faction, self.label_texts)
    
    # TODO: seems `completed` and `failed` can be merged
    def mission_completed(self, id: int, massacre_missions: MassacreMissions):
        # find mission details based on mission ID
        mission = massacre_missions.missions[id]
        # update mission status
        mission["Status"] = "Claimed"
        self.label_texts.missions[id]["Status"]["textvariable"].set("Claimed")
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
        self.label_texts.missions[id]["Status"]["textvariable"].set(status)
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
            for k, v in massacre_missions.factions.items():
                if len(v.running) != 0:
                    v.Progress += 1
                    Labels.update_faction_label_text(k, v, self.label_texts)
                    mission = massacre_missions.missions[v.running[0]]
                    mission["Progress"] += 1
                    progress = str(mission["Progress"]) + "/" + str(mission["KillCount"])
                    self.label_texts.missions[v.running[0]]["Progress"]["textvariable"].set(progress)

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
        rmlist = []
        for k, f in missions.factions.items():
            if len(f.past) != 0:
                for id in f.past:
                    details = missions.missions.pop(id)
                    missions.mission_ids.remove(id)
                    kill_count = details["KillCount"]
                    progress = details["Progress"]
                    f.KillCount -= kill_count 
                    f.Progress -= progress
                    f.mission_count -= 1
                    rmlist.append(id)
                f.past.clear()
            if f.mission_count == 0:
                cg.destroy_faction(k)
            else:
                Labels.update_faction_label_text(k, f, self.label_texts)
        rmlist = cg.destroy_missions(rmlist)
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
        for k, v in missions.missions.items():
            expiry = Labels.calculate_expiry_time(v["Expiry"])
            self.label_texts.missions[k]["Expiry"]["textvariable"].set(expiry)

    def cleanup(self, missions: MassacreMissions):
        if self.past_missions:
            self.discard_past_missions(missions)
        if not self.sanity:
            pass
            # self.sanity_check(missions)

    def sanity_check(self, massacre_missions: MassacreMissions):
        print(" There are discrepancies in mission Progress being detected.",
            "Please consider maunally update all mission progesses by",
            "providing information in the prompt below. You can skip this by",
            "leaving all input blank.")
        for i in massacre_missions.missions.values():
            prompt = "Mission information:\nFaction name: " + i["Faction"] + \
                "\nMission kill count: " + str(i["KillCount"]) + "\nCurrently logged " + \
                "mission Progress: " + str(i["Progress"]) + "\nActual progess shown " + \
                "in-game: " 
            try:
                Progress = int(input(prompt))
                delta = Progress - i["Progress"] 
                i["Progress"] = Progress
                faction = i["Faction"]
                massacre_missions.factions[faction].Progress -= delta
            except ValueError:
                print("Invalid input. Progress unchanged.")
            self.sanity = True
