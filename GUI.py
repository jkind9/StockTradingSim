import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import numpy as np
import time
import yfinance as yf
import time
from sklearn.metrics import r2_score
import numpy as np 
import sys
import time
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
import warnings
import os
import csv 
import json

warnings.filterwarnings("ignore")
from fitting import *
from graphing import *
from simulation import Simulation
import buy_sell_logic

class App():
    def __init__(self, root):
        self.root = root
        self.cash = 10000
        self.sims = [Simulation(starting_cash=10000, logic = buy_sell_logic.a_grad, file_path= "Data.xlsx"),
                     Simulation(starting_cash=5000, file_path= "Data.xlsx", logic= buy_sell_logic.grad),
                     Simulation(starting_cash=5000, file_path= "Data.xlsx", logic= buy_sell_logic.grad)]
        self.root.bind('<Escape>', self.on_escape)

        self.root.title("Dynamic Plots")

        self.tab_control = ttk.Notebook(root)

        # Tab 1
        self.tab1 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab1, text='Live Price')
        
        # Check if only one subplot is created (which is not a list), and convert it to a list
        self.n = len(self.sims)
        self.fig, self.axes = plt.subplots(self.n, 1, figsize=(8, self.n * 3))    # Initialize a line object on the axes

        if self.n == 1:
            self.axes = [self.axes1]
        self.line_plots = [ax.plot([], [], label=f'Sim {i+1} Profit')[0] for i, ax in enumerate(self.axes)]

        self.canvas1 = FigureCanvasTkAgg(self.fig, master=self.tab1)
        self.canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # # Tab 2
        # self.tab2 = ttk.Frame(self.tab_control)
        # self.tab_control.add(self.tab2, text='Plot 2')
        # self.fig2, self.ax2 = plt.subplots()
        # self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.tab2)
        # self.canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        self.tab_control.pack(expand=1, fill="both")

        self.start_sim_button = tk.Button(root, text= "Start Simulation", command = self.start_running_sim)
        self.start_sim_button.pack()
        self.stop_sim_button = tk.Button(root, text= "Stop Simulation", command = self.stop_running_sim)
        self.stop_sim_button.pack()
        self.stop_sim_button.config(state=tk.DISABLED)

        
    def start_running_sim(self):
        self.start_sim_button.config(state=tk.DISABLED)
        self.stop_sim_button.config(state=tk.NORMAL)
        for sim in self.sims:
            sim.start_simulation()
        self.update_graph_thread()
    
    def stop_running_sim(self):
        self.stop_sim_button.config(state=tk.DISABLED)
        self.start_sim_button.config(state=tk.NORMAL)
        for sim in self.sims:
            sim.stop_simulation()

    def update_graph_thread(self):
        """Start the simulation in a separate thread."""
        self.graphing_thread = threading.Thread(target=self.update_graph_gui, daemon=True)
        self.graphing_thread.start()

    def update_graph_gui(self):
        for i, sim in enumerate(self.sims):
            profit_over_time = sim.results["TotalValue"]
            ax = self.axes[i]
            line = self.line_plots[i]

            y_data = np.array(profit_over_time)
            x_data = np.array(list(range(len(profit_over_time))))

            update_graph(ax, line, x_data, y_data)
            # print("Sim", str(i+1))
            # print("Cash:", sim.cash, "| Stock worth:", sim.total_stock_val, "| Portfolio worth:: ", sim.total_value )

        self.canvas1.draw()
        if self.sims[0].running:
            self.root.after(100, self.update_graph_gui)


    def on_escape(self,event=None):
        print("Escape key pressed!")
        for sim in self.sims:
            sim.stop_simulation()
        quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    quit()
