from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import math as m
import numpy as np
import time

day = 86400
earth_mass = 5.97219 * (10**24)
dt = 0
G = 6.67430 * (10**-11)
run_time = 0
scale = 400000
keep_decimals_velocity = 3
keep_decimals_position = 1

color_map = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

class celestial_body:
  def __init__(self, mass, posX, posY, velX, velY):
      self.mass = mass
      self.pos = np.array([posX, posY])
      self.vel = np.array([velX, velY])
  
  def set_pos(self):
      self.pos += self.vel * dt

  def set_vel(self, celestial_body):
      r = np.linalg.norm(self.pos - celestial_body.pos)
      acc = (G * celestial_body.mass) / (r**2)
      direction = (celestial_body.pos - self.pos) / r
      acceleration = acc * direction
      self.vel += acceleration * dt

class Orbit_GUI:
    def __init__(self, master):
        self.master = master

        self.middle_frame = Frame(master)
        self.middle_frame.pack()

        self.bottom_frame = Frame(master)
        self.bottom_frame.pack()

        # create middle frame sub-frames
        self.graph_frame = Frame(self.middle_frame)
        self.bodies_frame = Frame(self.middle_frame, width=640, padx=5)
        self.graph_frame.pack(side=LEFT)
        self.bodies_frame.pack(side=LEFT, fill=Y)

        self.planets_frame = LabelFrame(self.bodies_frame, text='Massive Objects', width=320)
        self.satellites_frame = LabelFrame(self.bodies_frame, text='Satellites', width=320)
        self.planets_frame.pack(side=LEFT, fill=Y, padx=(0,5))
        self.planets_frame.pack_propagate(False)
        self.satellites_frame.pack(side=LEFT, fill=Y)
        self.satellites_frame.pack_propagate(False)

        # the figure that will contain the plot 
        self.fig = Figure(figsize=(5,5), dpi=100)
        self.main_graph = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        # create planets and satellites buttons
        self.add_planet_button = Button(self.planets_frame, text='Add Body', command=self.add_celestial_body)
        self.add_planet_button.pack()

        self.add_satellite_button = Button(self.satellites_frame, text='Add Satellite', command=self.add_satellite)
        self.add_satellite_button.pack()

        # create bottom frame sub-frames
        self.constant_entry_frame = LabelFrame(self.bottom_frame, text='Specs')
        self.control_buttons_frame = Frame(self.bottom_frame)
        self.constant_entry_frame.pack(side=LEFT, padx=5)
        self.control_buttons_frame.pack(side=LEFT, fill=Y)

        # initialize constant entry frame widgets
        self.dt_label = Label(self.constant_entry_frame, text='dt (days): ')
        self.dt_entry = Entry(self.constant_entry_frame, width=6)
        self.dt_entry.insert(0,'1')
        self.dt_label.grid(row=0, column=0)
        self.dt_entry.grid(row=0, column=1)

        self.G_constant_label = Label(self.constant_entry_frame, text='G (E^-11): ')
        self.G_constant_entry = Entry(self.constant_entry_frame, width=6)
        self.G_constant_entry.insert(0,'6.67430')
        self.G_constant_label.grid(row=1, column=0)
        self.G_constant_entry.grid(row=1, column=1)

        self.run_time_label = Label(self.constant_entry_frame, text='Run Time (frames): ')
        self.run_time_entry = Entry(self.constant_entry_frame, width=6)
        self.run_time_entry.insert(0,'20')
        self.run_time_label.grid(row=2, column=0)
        self.run_time_entry.grid(row=2, column=1)

        self.scale_label = Label(self.constant_entry_frame, text='Scale (km): ')
        self.scale_entry = Entry(self.constant_entry_frame, width=8)
        self.scale_entry.insert(0,'400000')
        self.scale_label.grid(row=3, column=0)
        self.scale_entry.grid(row=3, column=1)

        # initialize control button frame widgets
        self.update_graph_button = Button(self.control_buttons_frame, text='Update Graph', command=self.update_graph)
        self.update_graph_button.pack(side=LEFT, fill=Y)

        self.simulate_button = Button(self.control_buttons_frame, text='Run Simulation', command=self.run_simulation)
        self.simulate_button.pack(side=LEFT, fill=Y)

        self.step_forward_button = Button(self.control_buttons_frame, text='Step Forward', command=self.step_trajectories)
        self.step_forward_button.pack(side=LEFT, fill=Y)

        # global variables
        self.celestial_body_frames = []
        self.satellite_frames = []
        self.celestial_bodies = []
        self.satellite_bodies = []

    def add_celestial_body(self):
        temp_frame = LabelFrame(self.planets_frame, width=320)
        temp_frame.pack(side=TOP)
        temp_frame.pack_propagate(False)

        position_label = Label(temp_frame, text='Position (km):')
        position_label.grid(row=0, column=0, sticky='w')

        # Position entries

        position_frame = Frame(temp_frame)
        position_frame.grid(row=1, column=0)

        x_label = Label(position_frame, text='X:')
        x_pos_entry = Entry(position_frame, width=12)
        x_label.pack(side=LEFT)
        x_pos_entry.pack(side=LEFT, padx=5)

        y_label = Label(position_frame, text='Y:')
        y_pos_entry = Entry(position_frame, width=12)
        y_label.pack(side=LEFT)
        y_pos_entry.pack(side=LEFT, padx=5)

        # Velocity entries

        velocity_label = Label(temp_frame, text='Velocity (m/s):')
        velocity_label.grid(row=2, column=0, sticky='w')

        velocity_frame = Frame(temp_frame)
        velocity_frame.grid(row=3, column=0)

        x_label = Label(velocity_frame, text='X:')
        x_vel_entry = Entry(velocity_frame, width=12)
        x_label.pack(side=LEFT)
        x_vel_entry.pack(side=LEFT, padx=5)

        y_label = Label(velocity_frame, text='Y:')
        y_vel_entry = Entry(velocity_frame, width=12)
        y_label.pack(side=LEFT)
        y_vel_entry.pack(side=LEFT, padx=5)

        # Mass entries

        mass_frame = Frame(temp_frame)
        mass_frame.grid(row=4, column=0, sticky='w')

        mass_label = Label(mass_frame, text='Mass (earth masses):')
        mass_label.pack(side=LEFT)

        mass_entry = Entry(mass_frame, width=7)
        mass_entry.pack(side=LEFT, padx=5)

        self.celestial_body_frames.append(temp_frame)

    def add_satellite(self):
        temp_frame = LabelFrame(self.satellites_frame, width=320)
        temp_frame.pack(side=TOP)
        temp_frame.pack_propagate(False)

        position_label = Label(temp_frame, text='Position (km):')
        position_label.grid(row=0, column=0, sticky='w')

        # Position entries

        position_frame = Frame(temp_frame)
        position_frame.grid(row=1, column=0)

        x_label = Label(position_frame, text='X:')
        x_pos_entry = Entry(position_frame, width=12)
        x_label.pack(side=LEFT)
        x_pos_entry.pack(side=LEFT, padx=5)

        y_label = Label(position_frame, text='Y:')
        y_pos_entry = Entry(position_frame, width=12)
        y_label.pack(side=LEFT)
        y_pos_entry.pack(side=LEFT, padx=5)

        # Velocity entries

        velocity_label = Label(temp_frame, text='Velocity (m/s):')
        velocity_label.grid(row=2, column=0, sticky='w')

        velocity_frame = Frame(temp_frame)
        velocity_frame.grid(row=3, column=0)

        x_label = Label(velocity_frame, text='X:')
        x_vel_entry = Entry(velocity_frame, width=12)
        x_label.pack(side=LEFT)
        x_vel_entry.pack(side=LEFT, padx=5)

        y_label = Label(velocity_frame, text='Y:')
        y_vel_entry = Entry(velocity_frame, width=12)
        y_label.pack(side=LEFT)
        y_vel_entry.pack(side=LEFT, padx=5)

        self.satellite_frames.append(temp_frame)

    def update_graph(self):
        # set the value of the variables from the specs frame
        self.update_specs()

        # reset bodies list and clear graph
        self.celestial_bodies = []
        self.satellite_bodies = []

        x_positions = []
        y_positions = []
        colors = []

        # go through each celestial body in the planets frame
        # add them to the celestial bodies list
        # and plot them on the graph
        index = 0
        for body_frame_data in self.planets_frame.winfo_children():
            widgets = body_frame_data.winfo_children()
            if len(widgets) > 0:
                position_data = widgets[1].winfo_children()
                velocity_data = widgets[3].winfo_children()
                mass_data = widgets[4].winfo_children()
                if mass_data[1].get() != '' and position_data[1].get() != '' and position_data[3].get() != '' and velocity_data[1].get() != '' and velocity_data[3].get() != '':
                    temp_mass = float(mass_data[1].get()) * earth_mass
                    temp_x_pos = float(position_data[1].get()) * 1000
                    temp_y_pos = float(position_data[3].get()) * 1000
                    temp_x_vel = float(velocity_data[1].get())
                    temp_y_vel = float(velocity_data[3].get())
                    temp_celestial_body = celestial_body(temp_mass,temp_x_pos,temp_y_pos,temp_x_vel,temp_y_vel)
                    self.celestial_bodies.append(temp_celestial_body)

                    x_positions.append(temp_x_pos)
                    y_positions.append(temp_y_pos)
                    colors.append(color_map[index % len(color_map)])
                    index += 1
        
        index = 0
        for satellite_frame_data in self.satellites_frame.winfo_children():
            widgets = satellite_frame_data.winfo_children()
            if len(widgets) > 0:
                position_data = widgets[1].winfo_children()
                velocity_data = widgets[3].winfo_children()
                if position_data[1].get() != '' and position_data[3].get() != '' and velocity_data[1].get() != '' and velocity_data[3].get() != '':
                    temp_mass = 0
                    temp_x_pos = float(position_data[1].get()) * 1000
                    temp_y_pos = float(position_data[3].get()) * 1000
                    temp_x_vel = float(velocity_data[1].get())
                    temp_y_vel = float(velocity_data[3].get())
                    temp_celestial_body = celestial_body(temp_mass,temp_x_pos,temp_y_pos,temp_x_vel,temp_y_vel)
                    self.satellite_bodies.append(temp_celestial_body)

                    x_positions.append(temp_x_pos)
                    y_positions.append(temp_y_pos)
                    colors.append(color_map[(index + len(self.celestial_bodies)) % len(color_map)])
                    index += 1

        self.main_graph.cla()
        self.main_graph.scatter(x_positions, y_positions, c=colors)
        self.main_graph.set_xlim(-1 * scale, scale)
        self.main_graph.set_ylim(-1 * scale, scale)
        self.canvas.draw()

    def run_simulation(self):
      t = time.time()
      self.update_specs()

      for i in range(run_time):
          self.step_trajectories()
          self.master.update_idletasks()
          self.master.update()

      print('Simulation time: ', time.time() - t)

    def step_trajectories(self):
       self.update_specs()

       self.update_velocities()
       self.graph_positions()

    def update_velocities(self):
      for index in range(len(self.celestial_bodies)):
          for i in range(len(self.celestial_bodies)):
              if i != index:
                  self.celestial_bodies[index].set_vel(self.celestial_bodies[i])

          body_frame_data = self.planets_frame.winfo_children()[index + 1]
          widgets = body_frame_data.winfo_children()
          velocity_data = widgets[3].winfo_children()

          body = self.celestial_bodies[index]
          velocity_data[1].delete(0,END)
          velocity_data[1].insert(0, round(body.vel[0], keep_decimals_velocity))
          velocity_data[3].delete(0,END)
          velocity_data[3].insert(0, round(body.vel[1], keep_decimals_velocity))

      for index in range(len(self.satellite_bodies)):
          for i in range(len(self.celestial_bodies)):
              self.satellite_bodies[index].set_vel(self.celestial_bodies[i])

          body_frame_data = self.satellites_frame.winfo_children()[index + 1]
          widgets = body_frame_data.winfo_children()
          velocity_data = widgets[3].winfo_children()

          body = self.satellite_bodies[index]
          velocity_data[1].delete(0,END)
          velocity_data[1].insert(0, round(body.vel[0], keep_decimals_velocity))
          velocity_data[3].delete(0,END)
          velocity_data[3].insert(0, round(body.vel[1], keep_decimals_velocity))

    def graph_positions(self):
        x_positions = []
        y_positions = []
        colors = []

        for index in range(len(self.celestial_bodies)):
            self.celestial_bodies[index].set_pos()
            body = self.celestial_bodies[index]
            body_frame_data = self.planets_frame.winfo_children()[index + 1]
            widgets = body_frame_data.winfo_children()
            position_data = widgets[1].winfo_children()

            position_data[1].delete(0,END)
            position_data[1].insert(0, round(body.pos[0]/1000, keep_decimals_position))
            position_data[3].delete(0,END)
            position_data[3].insert(0, round(body.pos[1]/1000, keep_decimals_position))

            x_positions.append(body.pos[0])
            y_positions.append(body.pos[1])
            colors.append(color_map[index % len(color_map)])

        for index in range(len(self.satellite_bodies)):
            self.satellite_bodies[index].set_pos()
            body = self.satellite_bodies[index]
            body_frame_data = self.satellites_frame.winfo_children()[index + 1]
            widgets = body_frame_data.winfo_children()
            position_data = widgets[1].winfo_children()

            position_data[1].delete(0,END)
            position_data[1].insert(0, round(body.pos[0]/1000, keep_decimals_position))
            position_data[3].delete(0,END)
            position_data[3].insert(0, round(body.pos[1]/1000, keep_decimals_position))

            x_positions.append(body.pos[0])
            y_positions.append(body.pos[1])
            colors.append(color_map[(index + len(self.celestial_bodies)) % len(color_map)])

        self.main_graph.cla()
        self.main_graph.scatter(x_positions, y_positions, c=colors)
        self.main_graph.set_xlim(-1 * scale, scale)
        self.main_graph.set_ylim(-1 * scale, scale)
        self.canvas.draw()

    def update_specs(self):
        global dt
        dt = float(self.dt_entry.get()) * day
        global G
        G = float(self.G_constant_entry.get()) * (10**-11)
        global run_time
        run_time = int(self.run_time_entry.get())
        global scale
        scale = int(self.scale_entry.get()) * 1000


### Implementation
root = Tk()
root.title("Orbit Simulator")
window = Orbit_GUI(root)
root.mainloop()