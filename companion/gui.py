import tkinter as tk
from tkinter import font
from readlog import MassacreMissions, FactionMissions, DynamicalLabels, Labels
import random
import time

class DynamicGrid(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.text = tk.Text(self, wrap="char", borderwidth=0, highlightthickness=0,
                            state="disabled")
        self.text.pack(fill="both", expand=True)
        self.boxes = []

    def add_box(self, color=None):
        bg = color if color else random.choice(("red", "orange", "green", "blue", "violet"))
        box = tk.Frame(self.text, bd=1, relief="sunken", background=bg,
                       width=100, height=100)
        self.boxes.append(box)
        self.text.configure(state="normal")
        self.text.window_create("end", window=box)
        self.text.configure(state="disabled")

class Example(object):
    def __init__(self):
        self.root = tk.Tk()
        self.dg = DynamicGrid(self.root, width=500, height=200)
        add_button  = tk.Button(self.root, text="Add", command=self.dg.add_box)

        add_button.pack()
        self.dg.pack(side="top", fill="both", expand=True)

        # add a few boxes to start
        for i in range(10):
            self.dg.add_box()

    def start(self):
        self.root.mainloop()

class CompanionGUI:
    
    def __init__(self):
        self.window = tk.Tk()
        self.font = font.nametofont("TkDefaultFont")
        self.fontsize = self.font.config(size=14)
        self.window.title("Elite: Dangerous Massacre Missions Companion")
        self.faction_labels = ["mission_count", "Progress", "KillCount"]
        self.faction_texts = ["Mission Count: ", "Progress: ", "Kill Count "]
        # TODO: change this to a dictionary, also allows for more options
        self.mission_label_text = ["System", "Station", "Target Faction",
            "Target Type", "Wing Mission", "Status", "Expiry", "Progress"]
        self.mission_label_index = [0, 1, 2, 3, 5, 6, 7, 4]
        self.mission_label_key = ["DestinationSystem", "DestinationStation", 
            "TargetFaction", "TargetType_Localised", "Wing", "Status", "Expiry"]
        self.mission_label_width = [100, 100, 120, 60, 60, 60, 100, 60]
        self.factions = {}
        self.missions = {}
    
    def add_faction(self, name: str, faction: dict):
        # add a new frame for the current faction
        frame = tk.Frame(master=self.window, relief=tk.RAISED, border=2, pady=3)
        frame.pack(fill=tk.BOTH)
        # add it to the dictionary
        self.factions[name] = [frame]

        # build labels for factions
        i = 0
        for d in Labels.faction_labels:
            frame.columnconfigure(i, weight=1)
            label = tk.Label(master=frame, text=d["text"], relief=tk.SUNKEN,
                borderwidth=2, width=d["len"], justify=tk.LEFT)
            label.grid(row=0, column=i, sticky="w")
            self.factions[name].append(label)
            i += 1
            frame.columnconfigure(i, minsize=d["minsize"], weight=1)
            label = tk.Label(master=frame, relief=tk.RIDGE, borderwidth=2,
                justify=tk.LEFT, wraplength=275, **faction[d["key"]])
            label.grid(row=0, column=i, sticky="w")
            self.factions[name].append(label)
            i += 1

        # build the title bar (what should be a proper name for this?) for this faction
        frame = tk.Frame(master=self.window, relief=tk.RAISED, border=2,
            padx=10, pady=3)
        frame.pack(fill=tk.BOTH)
        self.factions[name].append(frame)
        for i, d in enumerate(Labels.mission_labels):
            frame.columnconfigure(i, minsize=d["width"], weight=1)
            label = tk.Label(master=frame, text=d["title"], relief=tk.RIDGE,
                borderwidth=2)
            label.grid(row=0, column=i, sticky="we")
            self.factions[name].append(label)

        # # label "faction name:"
        # label = tk.Label(master=frame, text="Faction Name: ", relief=tk.FLAT,
        #     borderwidth=2, justify=tk.LEFT)
        # self.factions[name].append(label)
        # label.grid(row=0, column=0, sticky="w")
        # # actual name
        # label = tk.Label(master=frame, text=name, relief=tk.FLAT, 
        #     wraplength=175, justify=tk.LEFT)
        # self.factions[name].append(label)
        # label.grid(row=0, column=1, sticky="w")

        # # show the faction's mission counts
        # faction_dict = vars(faction)
        # content = "Mission Count: " + str(faction_dict["mission_count"])
        # label = tk.Label(master=frame, text=content, relief=tk.FLAT,
        #     borderwidth=2, justify=tk.LEFT)
        # self.factions[name].append(label)
        # label.grid(row=0, column=2, sticky="w")

        # # faction specific total progress
        # content = "Progress: " + str(faction_dict["Progress"]) + "/" + str(
        #     faction_dict["KillCount"])
        # label = tk.Label(master=frame, text=content, relief=tk.FLAT,
        #     borderwidth=2, justify=tk.LEFT)
        # self.factions[name].append(label)
        # label.grid(row=0, column=3, sticky="w")

        # # title bar for this faction's missions
        # frame = tk.Frame(master=self.window, relief=tk.RAISED, border=2,
        #     padx=10, pady=3)
        # frame.pack(fill=tk.BOTH)
        # self.factions[name].append(frame)

        # for idx, txt in enumerate(self.mission_label_text):
        #     # actual index in columns
        #     i = self.mission_label_index[idx]
        #     # width
        #     w = self.mission_label_width[idx]
        #     # setup column
        #     frame.columnconfigure(i, minsize=w, weight=1)
        #     # add label
        #     label = tk.Label(master=frame, text=txt, relief=tk.RIDGE,
        #         borderwidth=2)
        #     # append to list
        #     self.factions[name].append(label)
        #     # add to grid
        #     label.grid(row=0, column=i, sticky="we")

    def add_mission(self, id: str, name: str, mission: dict, mission_idx:int):
    # def add_mission(self, name: str, mission: dict, mission_idx:int):
        # retrieve the frame for missions
        parent = self.factions[name][7]
        # frame = tk.Frame(master=parent, relief=tk.FLAT, border=2, pady=3)
        # frame.grid(row=mission_idx, columnspan=8, sticky="nwse")
        self.missions[id] = []
        # add all labels except progress
        i = 0
        for k, v in mission.items():
            label = tk.Label(master=parent, relief=tk.FLAT, borderwidth=2, 
                **v)
            label.grid(row=mission_idx, column=i, sticky="we")
            self.missions[id].append(label)
            i += 1

        # for idx in range(6):
        #     try:
        #         txt = str(mission[self.mission_label_key[idx]])
        #     except KeyError:
        #         print("Will not be a problem next time!")
        #     i = self.mission_label_index[idx]
        #     # w = self.mission_label_width[idx]
        #     # frame.columnconfigure(i, minsize=w, weight=1)
        #     label = tk.Label(master=parent, text=txt, relief=tk.FLAT, border=2)
        #     label.grid(row=mission_idx, column=i, sticky="we")
        #     self.missions[mission["MissionID"]].append(label)
        # # progress and expiry time need to be dealt separately
        # # for mission exprie time
        # current_time = time.time()
        # time_left = mission["Expiry"] - current_time
        # if time_left <= 0:
        #     time_left = "Past Due"
        # label = tk.Label(master=parent, text=time_left, relief=tk.FLAT, border=2)
        # label.grid(row=mission_idx, column=7, sticky="we")
        # self.missions[mission["MissionID"]].append(label)
        # # for mission progress
        # progress = str(mission["Progress"]) + "/" + str(mission["KillCount"])
        # # w = self.mission_label_width[7]
        # # frame.columnconfigure(4, minsize=w, weight=1)
        # label = tk.Label(master=parent, text=progress, relief=tk.FLAT, border=2)
        # label.grid(row=mission_idx, column=4, sticky="we")
        # self.missions[mission["MissionID"]].append(label)
