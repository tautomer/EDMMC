import tkinter as tk
from tkinter import font
from constructors import Labels
import random

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

class CompanionGUI:
    
    def __init__(self):
        self.theme = {
            "window_bg": "#c8d6e5",
            "faction_frame_bg": "#c8d6e5",
            "faction_label_bg": "#c8d6e5",
            "faction_label_fg": "#222f3e",
            "tab_frame_bg": "#8395a7",
            "tab_label_bg": "#8395a7",
            "tab_label_fg": "#130f40",
            "mission_frame_bg": ["#dfe4ea", "#ced6e0"],
            "mission_label_bg": ["#dfe4ea", "#ced6e0"],
            "mission_label_fg": ["#222f3e", "#2f3542"],
            "statusbar_frame_bg": "#57606f",
            "statusbar_label_bg": "#57606f",
            "statusbar_label_fg": "#dff9fb",
            "button_bg": "#c8d6e5",
            "button_fg": "#222f3e"
        }
        self.window = tk.Tk()
        self.font = font.nametofont("TkDefaultFont")
        self.fontsize = self.font.config(size=14)
        self.window.title("Elite: Dangerous Massacre Missions Companion")
        self.window.minsize(width=960, height=540)
        self.window.resizable(True, True)
        self.window.config(bg=self.theme["window_bg"])
        self.factions = {}
        self.missions = {}
    
    def add_faction(self, name: str, faction: dict):
        # add a new frame for the current faction
        frame = tk.Frame(self.window, relief=tk.FLAT, bd=2, pady=3,
            bg=self.theme["faction_frame_bg"])
        frame.pack(fill=tk.Y, anchor=tk.W)
        # add it to the dictionary
        self.factions[name] = [frame]

        # build labels for factions
        i = 0
        for d in Labels.faction_labels:
            frame.columnconfigure(i, weight=1)
            # set the fixed part of the labels
            label = tk.Label(frame, text=d["text"], justify=tk.LEFT, bd=2,
                relief=tk.FLAT, width=d["len"],
                bg=self.theme["faction_label_bg"],
                fg=self.theme["faction_label_fg"])
            label.grid(row=0, column=i, sticky="w")
            self.factions[name].append(label)
            i += 1
            frame.columnconfigure(i, minsize=d["minsize"], weight=1)
            # set the varying part 
            label = tk.Label(frame, relief=tk.FLAT, bd=2, justify=tk.LEFT,
                wraplength=275, bg=self.theme["faction_label_bg"],
                fg=self.theme["faction_label_fg"], **faction[d["key"]])
            label.grid(row=0, column=i, sticky=tk.W)
            self.factions[name].append(label)
            i += 1

        # build the title bar (what should be a proper name for this?) for this faction
        frame = tk.Frame(self.window, relief=tk.FLAT, bd=2, pady=0,
            bg=self.theme["tab_frame_bg"])
        frame.pack(fill=tk.BOTH)
        self.factions[name].append(frame)
        for i, d in enumerate(Labels.mission_labels):
            frame.columnconfigure(i, minsize=d["width"], weight=1)
            label = tk.Label(frame, text=d["title"], relief=tk.SOLID, bd=0,
                bg=self.theme["tab_label_bg"], fg=self.theme["tab_label_fg"])
            label.grid(row=0, column=i, sticky=tk.NSEW, padx=5)
            self.factions[name].append(label)

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
            j = mission_idx % 2
            label = tk.Label(parent, relief=tk.FLAT, bd=0,
                bg=self.theme["mission_label_bg"][j],
                fg=self.theme["mission_label_fg"][j], **v)
            label.grid(row=mission_idx, column=i, sticky="nswe")
            self.missions[id].append(label)
            i += 1

    def destroy_faction(self, name: str):
        for w in self.factions[name]:
            w.destroy()

    def destroy_missions(self, rmlist: list):
        for id in rmlist:
            for w in self.missions[id]:
                w.destroy()
        return []

    def status_bar(self, status: tk.StringVar):
        bar = tk.Frame(self.window, relief=tk.RAISED, bd=0,
            bg=self.theme["statusbar_frame_bg"])
        bar.pack(fill=tk.BOTH, side=tk.BOTTOM) 
        notif = tk.Frame(bar, bg=self.theme["statusbar_frame_bg"])
        notif.pack(side="left")
        buttons = tk.Frame(bar, bg=self.theme["statusbar_frame_bg"])
        buttons.pack(side="right")
        status = tk.Label(notif, textvariable=status, anchor="w",
            bg=self.theme["statusbar_label_bg"],
            fg=self.theme["statusbar_label_fg"])
        status.pack()
        cali = tk.Button(buttons, text="Calibrate", anchor="e",
            relief=tk.RAISED, bd=1, bg=self.theme["button_bg"],
            fg=self.theme["button_fg"])
        cali.pack(side="right", padx=5)
        setting = tk.Button(buttons, text="Settings", anchor="e",
            relief=tk.RAISED, bd=1, bg=self.theme["button_bg"],
            fg=self.theme["button_fg"])
        setting.pack(side="right")
        pass