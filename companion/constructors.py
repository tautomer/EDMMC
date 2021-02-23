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
            "key": "progress",
            "len": 8,
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
    def variable_labels(missions: MassacreMissions, labels:DynamicalLabels):
        # build faction part
        for name, value in missions.factions.items():
            labels.factions[name] = {"name": {"text": name}}
            labels.factions[name]["mission_count"] = {"textvariable": 
                tk.IntVar(value=value.mission_count)}
            progress = str(value.Progress) + "/" + str(value.KillCount)
            labels.factions[name]["progress"] = {"textvariable": 
                tk.StringVar(value=progress)}
        # build mission part
        current_time = int(time.time())
        for id, details in missions.missions.items():
            labels.missions[id] = {"System": {"textvariable":
                tk.StringVar(value=details["DestinationSystem"])}}
            labels.missions[id]["Station"] = {"textvariable":
                tk.StringVar(value=details["DestinationStation"])}
            labels.missions[id]["Target Faction"] = {"text":
                details["TargetFaction"]}
            labels.missions[id]["Target Type"] = {"text":
                details["TargetType_Localised"]}
            labels.missions[id]["Progress"] = {"text":
                details["TargetType_Localised"]}
            progress = str(details["Progress"]) + "/" + str(details["KillCount"])
            labels.missions[id]["Progress"] = {"textvariable":
                tk.StringVar(value=progress)}
            labels.missions[id]["Wing Mission"] = {"text": str(details["Wing"])}
            labels.missions[id]["Status"] = {"textvariable":
                tk.StringVar(value=details["Status"])}
            dt = details["Expiry"] - current_time
            if dt <= 0:
                expiry = "Past Due"
            else:
                rt = relativedelta(seconds=dt)
                expiry = "{:01d}D {:02d}H {:02d}M".format(rt.days, rt.hours,
                    rt.minutes)
            labels.missions[id]["Expiry"] = {"textvariable":
                tk.StringVar(value=expiry)}