from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dateutil.relativedelta import relativedelta
import time
import tkinter as tk
from typing import List, Dict

@dataclass_json
@dataclass
class FactionMissions:
    mission_count: int 
    KillCount: int
    Progress: int
    Reward: int
    running: List[int]
    ready: List[int]
    past: List[int]
    other: List[int]

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

@dataclass
class DynamicalLabels:
    factions: Dict[str, Dict[str, tk.StringVar]]
    missions: Dict[str, Dict[str, tk.StringVar]]
    ed_status: tk.StringVar
    current_log_status: tk.StringVar

class Labels:
    faction_labels = [ {
            "text": "Faction Name:",
            "key": "name",
            "len": 11,
            "minsize": 275
        },
        {
            "text": "Mission Count:",
            "key": "mission_count",
            "len": 12,
            "minsize": 50
        },
        {
            "text": "Progress:",
            "key": "Progress",
            "len": 8,
            "minsize": 100
        } ,
        {
            "text": "Reward:",
            "key": "Reward",
            "len": 6,
            "minsize": 50
        } 
    ]
    mission_labels = [ {
        "title": "System",
        "key:": "DestinationSystem",
        "width": 150 
    }, {
        "title": "Station",
        "key:": "DestinationStation",
        "width": 150 
    }, {
        "title": "Target Faction",
        "key:": "TargetFaction",
        "width": 150
    }, {
        "title": "Target Type",
        "key:": "TargetType_Localised",
        "width": 75
    }, {
        "title": "Progress",
        "key": "Progress",
        "width": 60
    }, {
        "title": "Wing Mission",
        "key:": "Wing",
        "width": 75
    }, {
        "title": "Status",
        "key:": "DestinationStation",
        "width": 75
    }, {
        "title": "Expiry",
        "key:": "Expiry",
        "width": 100 
    }
    ]

    @staticmethod
    def faction_label_text_setup(name: str, labels: DynamicalLabels):
        labels.factions[name] = {"name": {"text": name}}
        labels.factions[name]["mission_count"] = {"textvariable": tk.IntVar()}
        labels.factions[name]["Progress"] = {"textvariable": tk.StringVar()}
        labels.factions[name]["Reward"] = {"textvariable": tk.IntVar()}

    @staticmethod
    def mission_label_text_setup(id: int, mission: dict, labels:DynamicalLabels):
        # build mission part
        labels.missions[id] = {"System": {"textvariable":
            tk.StringVar(value=mission["DestinationSystem"])}}
        labels.missions[id]["Station"] = {"textvariable":
            tk.StringVar(value=mission["DestinationStation"])}
        labels.missions[id]["Target Faction"] = {"text":
            mission["TargetFaction"]}
        labels.missions[id]["Target Type"] = {"text":
            mission["TargetType_Localised"]}
        labels.missions[id]["Progress"] = {"text":
            mission["TargetType_Localised"]}
        progress = str(mission["Progress"]) + "/" + str(mission["KillCount"])
        labels.missions[id]["Progress"] = {"textvariable":
            tk.StringVar(value=progress)}
        labels.missions[id]["Wing Mission"] = {"text": str(mission["Wing"])}
        labels.missions[id]["Status"] = {"textvariable":
            tk.StringVar(value=mission["Status"])}
        expiry = Labels.calculate_expiry_time(mission["Expiry"])
        labels.missions[id]["Expiry"] = {"textvariable":
            tk.StringVar(value=expiry)}

    @staticmethod
    def calculate_expiry_time(expiry_time: int):
        current_time = int(time.time())
        dt = expiry_time - current_time
        if dt <= 0:
            expiry = "Past Due"
        else:
            rt = relativedelta(seconds=dt)
            expiry = "{:01d}D {:02d}H {:02d}M".format(rt.days, rt.hours,
                rt.minutes)
        return expiry
    
    @staticmethod
    def update_faction_label_text(name: str, faction: FactionMissions, labels: DynamicalLabels):

        progress = str(faction.Progress) + "/" + str(faction.KillCount)
        labels.factions[name]["mission_count"]["textvariable"].set(
            faction.mission_count)
        labels.factions[name]["Progress"]["textvariable"].set(progress)
        labels.factions[name]["Reward"]["textvariable"].set(f'{faction.Reward:,}')