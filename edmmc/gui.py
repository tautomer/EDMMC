import tkinter as tk
from tkinter import font
from constructors import Labels
import random

class CompanionGUI:
    
    def __init__(self):
        self.theme = {
            "font": "Calibri",
            "fontsize": [14, 13, 13, 9],
            "window_bg": "#c8d6e5",
            "faction_frame_bg": "#c8d6e5",
            "faction_label_bg": "#c8d6e5",
            "faction_label_fg": "#353b48",
            "tab_frame_bg": "#8395a7",
            "tab_label_bg": "#8395a7",
            "tab_label_fg": "#f7f1e3",
            "mission_frame_bg": ["#dfe6e9", "#b2bec3"],
            "mission_label_bg": ["#dfe6e9", "#b2bec3"],
            "mission_label_fg": ["#222f3e", "#2f3542"],
            "statusbar_frame_bg": "#57606f",
            "statusbar_label_bg": "#57606f",
            "statusbar_label_fg": "#dff9fb",
            "button_bg": "#c8d6e5",
            "button_fg": "#222f3e"
        }
        self.window = tk.Tk()
        # self.main_frame = self.window
        self.window.minsize(width=960, height=540)
        self.window.resizable(True, True)
        # frame for both the canvas and scroll bar
        self.master_frame = tk.Frame(self.window, bg=self.theme["window_bg"])
        self.master_frame.pack(expand=True, fill=tk.BOTH)
        # add a vertical scrollbar
        # initialize the canvas
        self.canvas = tk.Canvas(self.master_frame, bg=self.theme["window_bg"])
        self.canvas.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        scrollbar = tk.Scrollbar(self.master_frame, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill='both')
        self.canvas.configure(yscrollcommand = scrollbar.set)
        # main frame to draw all mission related stuff
        self.main_frame = tk.Frame(self.canvas, bg=self.theme["window_bg"])
        self.canvas_frame = self.canvas.create_window(0, 0, window=self.main_frame, anchor='w')
        def on_configure(event):
            # update scrollregion after starting 'mainloop'
            # when all widgets are in canvas
            self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        def frame_width(event):
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_frame, width = canvas_width)
        # dynamically changing the canvas size
        self.canvas.bind('<Configure>', frame_width)
        self.main_frame.bind('<Configure>', on_configure)
        # change app icon
        self.window.iconbitmap("./icons/mercenary.ico")
        self.font = font.nametofont("TkDefaultFont")
        self.font.config(size=self.theme["fontsize"][0])
        self.font.config(family=self.theme["font"])
        self.title_font = (self.theme["font"], self.theme["fontsize"][0],
            "bold")
        self.tab_font = (self.theme["font"], self.theme["fontsize"][1])
        self.mission_font = (self.theme["font"], self.theme["fontsize"][2])
        self.status_font = (self.theme["font"], self.theme["fontsize"][3])
        self.window.title("Elite: Dangerous Massacre Missions Companion")
        self.window.config(bg=self.theme["window_bg"])
        self.factions = {}
        self.missions = {}
    
    def add_faction(self, name: str, faction: dict):
        # add a new frame for the current faction
        frame = tk.Frame(self.main_frame, relief=tk.FLAT, bd=2, pady=3,
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
                relief=tk.FLAT, width=d["len"], font=self.title_font,
                bg=self.theme["faction_label_bg"],
                fg=self.theme["faction_label_fg"])
            label.grid(row=0, column=i, sticky="w")
            self.factions[name].append(label)
            i += 1
            frame.columnconfigure(i, minsize=d["minsize"], weight=1)
            # set the varying part 
            label = tk.Label(frame, relief=tk.FLAT, bd=2, justify=tk.LEFT,
                wraplength=275, bg=self.theme["faction_label_bg"],
                fg=self.theme["faction_label_fg"], font=self.title_font,
                **faction[d["key"]])
            label.grid(row=0, column=i, sticky=tk.W)
            self.factions[name].append(label)
            i += 1

        # build the title bar (what should be a proper name for this?) for this faction
        frame = tk.Frame(self.main_frame, relief=tk.FLAT, bd=2, pady=0,
            bg=self.theme["tab_frame_bg"])
        frame.pack(fill=tk.BOTH)
        self.factions[name].append(frame)
        for i, d in enumerate(Labels.mission_labels):
            frame.columnconfigure(i, minsize=d["width"], weight=1)
            label = tk.Label(frame, text=d["title"], relief=tk.SOLID, bd=0,
                bg=self.theme["tab_label_bg"], fg=self.theme["tab_label_fg"],
                font=self.tab_font)
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
                font=self.mission_font, bg=self.theme["mission_label_bg"][j],
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

    def status_bar(self, ed: tk.StringVar, log: tk.StringVar):
        bar = tk.Frame(self.window, relief=tk.RAISED, bd=0,
            bg=self.theme["statusbar_frame_bg"])
        bar.pack(fill=tk.BOTH, side=tk.BOTTOM) 
        notif = tk.Frame(bar, bg=self.theme["statusbar_frame_bg"])
        notif.pack(side="left")
        buttons = tk.Frame(bar, bg=self.theme["statusbar_frame_bg"])
        buttons.pack(side="right")
        ed_status = tk.Label(notif, textvariable=ed, font=self.status_font,
            justify=tk.LEFT, bg=self.theme["statusbar_label_bg"],
            fg=self.theme["statusbar_label_fg"])
        ed_status.pack(anchor="w")
        log_status = tk.Label(notif, textvariable=log, font=self.status_font,
            justify=tk.LEFT, bg=self.theme["statusbar_label_bg"],
            fg=self.theme["statusbar_label_fg"])
        log_status.pack(anchor="w")
        # cali = tk.Button(buttons, text="Calibrate", anchor="e",
        #     relief=tk.RAISED, bd=1, bg=self.theme["button_bg"],
        #     fg=self.theme["button_fg"])
        # cali.pack(side="right", padx=5)
        # setting = tk.Button(buttons, text="Settings", anchor="e",
        #     relief=tk.RAISED, bd=1, bg=self.theme["button_bg"],
        #     fg=self.theme["button_fg"])
        # setting.pack(side="right")
        pass