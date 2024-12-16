'''
This code is a 1 dimensional Finite Element Modelling GUI.
The inputs are length, area, and modulus of elasticity of 1 or more materials.
The outputs are the displacements of the beam when the given forces are applied.
All deformation is assumed to be elastic.

Created as a project for Solids 1 at TCU
Authors: Elliott Miles, Johnathan Bajuk, Spencer Moller, and Evan Evangelista
'''

import math as m
from tkinter import *
import numpy as np
import sigfig

class FEM_GUI:
    def __init__(self, master):
        self.master = master
        
        # configure the window size
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        #self.master.minsize(screen_width-200, screen_height-200)
        self.master.geometry(f"{screen_width}x{screen_height}")

        # frames
        self.top_frame = LabelFrame(master)
        self.fem_inputs_frame = LabelFrame(master, text='Finite Element Values')
        self.output_frame = LabelFrame(master, text='Outputs')
        self.top_frame.pack(side=TOP, fill=X, padx=10, pady=(5,0))
        self.fem_inputs_frame.pack(side=TOP, fill=BOTH, expand=True, padx=10, pady=5)
        self.output_frame.pack(side=BOTTOM, fill=X, padx=10, pady=(0,5))

        # top frame widgets
        self.entry_frame = Frame(self.top_frame)
        self.entry_frame.pack()

        self.element_count_label = Label(self.entry_frame, text='Number of nodes:')
        self.nodes_count_entry = Entry(self.entry_frame, width=6)
        self.element_count_label.grid(row=0, column=0, pady=5)
        self.nodes_count_entry.grid(row=0, column=1, pady=5)

        self.generate_inputs_button = Button(self.top_frame, text='Ready', command=self.generate_inputs)
        self.generate_inputs_button.pack(pady=5)

        # input frame widgets
        self.fem_general_inputs = Frame(self.fem_inputs_frame)
        self.fem_general_inputs.pack()

        # output frame widgets
        self.answer_button = Button(self.output_frame, text='Calculate', command=self.calculate_nodes)
        self.answer_button.pack()

        self.answer_frame = Frame(self.output_frame)
        self.answer_frame.pack()

    def generate_inputs(self):
        # try to convert the value in the nodes count box to an integer
        # if this fails, the program doesn't do anything
        try:
            nodes_count = int(self.nodes_count_entry.get())
            element_count = nodes_count - 1
        except:
            nodes_count = self.nodes_count_entry.get()

        # if the value was converted to an integer, it generates the correct number of element frames and output frames
        if isinstance(nodes_count, int) and nodes_count >= 0 and element_count <= 12:
            # destroy the frames that are already there
            for widget in self.fem_general_inputs.winfo_children():
                widget.destroy()
            # create the new ones
            for index in range(element_count):
                self.create_element_frame(index)

            # destroy the frames that are already there
            for widget in self.answer_frame.winfo_children():
                widget.destroy()
            # create the new ones
            for index in range(nodes_count):
                self.create_answer_frame(index)
            

    def create_element_frame(self, frame_num):
        # helper function for generate_inputs

        # create the label frame that stores the element and plot it in the correct location in the grid
        element_frame = LabelFrame(self.fem_general_inputs, text='Element ' + str(frame_num+1))
        column = m.floor((frame_num)/6)
        row = frame_num - column*6
        element_frame.grid(row=row, column=column, padx=4, pady=5)

        # create the labels and entries for area, modulus of elasticity, and length
        area_label = Label(element_frame, text='Area (m^2):')
        area_entry = Entry(element_frame, width=6)
        MoE_label = Label(element_frame, text='E (GPa):')
        MoE_entry = Entry(element_frame, width=6)
        length_label = Label(element_frame, text='Length (m):')
        length_entry = Entry(element_frame, width=6)
        force_label = Label(element_frame, text='Force (N):')
        force_entry = Entry(element_frame, width=6)

        # plot the labels and entries
        area_label.grid(row=0, column=0, padx=(2,0), pady=5)
        area_entry.grid(row=0, column=1, padx=(2,10), pady=5)
        MoE_label.grid(row=0, column=2, pady=5)
        MoE_entry.grid(row=0, column=3, padx=(2,10), pady=5)
        length_label.grid(row=0, column=4, pady=5)
        length_entry.grid(row=0, column=5, padx=2, pady=5)
        force_label.grid(row=0, column=6, pady=5)
        force_entry.grid(row=0, column=7, padx=2, pady=5)

    def create_answer_frame(self, frame_num):
        # helper function for generate_inputs

        # create label frame for a displacement value
        node_frame = LabelFrame(self.answer_frame, text='Delta for Node ' + str(frame_num + 1) + ' (m)')
        row = m.floor(frame_num/8)
        column = frame_num - row*8
        node_frame.grid(row=row, column=column, padx=5, pady=5)
        
        # create a label to enter the answer into
        answer = Label(node_frame, text='')
        answer.pack(padx=3)

    def calculate_nodes(self):
        # initialize necessary lists
        areas = []
        MoEs = []
        lengths = []
        list_of_k = []
        forces = []

        # get the number of nodes
        num_of_nodes = int(len(self.answer_frame.winfo_children()))

        # initialize sizes of spring and force matrices
        spring_matrix = np.zeros((num_of_nodes, num_of_nodes))
        force_vector = np.zeros((num_of_nodes-1,1))

        # populate lists with data for each element
        for frame in self.fem_general_inputs.winfo_children():
            widgets = frame.winfo_children()
            areas.append(float(widgets[1].get()))
            MoEs.append(float(widgets[3].get())*(10**9))
            lengths.append(float(widgets[5].get()))
            forces.append(float(widgets[7].get()))

        # calculate k for each element and add it to a list
        for index in range(len(self.fem_general_inputs.winfo_children())):
            k = areas[index] * MoEs[index] / lengths[index]
            list_of_k.append(k)
            force_vector[index,0] = forces[index]

        # create spring matrix
        for index in range(len(list_of_k)):
            temp_matrix = np.zeros((num_of_nodes, num_of_nodes))
            temp_matrix[index,index] = list_of_k[index]
            temp_matrix[index,index+1] = list_of_k[index] * -1
            temp_matrix[index+1,index] = list_of_k[index] * -1
            temp_matrix[index+1,index+1] = list_of_k[index]

            spring_matrix += temp_matrix

        # display spring matrix
        print('Spring Matrix:\n\n' + str(spring_matrix))
        print()
        print('Reaction at wall:\n\n' + str(sum(force_vector)[0] * -1))
        print()

        # cut spring matrix
        spring_matrix = np.array(spring_matrix[1:,1:])

        # inverse spring matrix
        spring_inv = np.linalg.inv(spring_matrix)

        # calculate displacements
        displacements = np.matmul(spring_inv, force_vector)

        # display the displacement values
        self.set_outputs(displacements)

    def set_outputs(self, displacements):
        displacement_frames = self.answer_frame.winfo_children()

        # set the value of the label in each frame to the corresponding value in the matrix
        for index in range(len(self.answer_frame.winfo_children())):
            if index == 0:
                # the first on is always 0
                displacement_frames[index].winfo_children()[0].config(text='0')
            else:
                displacement_frames[index].winfo_children()[0].config(text=sigfig.round(displacements[index-1][0], sigfigs=6))

root = Tk()
root.title("FEM Simulator")
window = FEM_GUI(root)
root.mainloop()