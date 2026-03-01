# COMSOAL Assembly Line Balancing Tool

## Overview
This repository contains a Python-based desktop application designed to solve the **Assembly Line Balancing Problem (ALBP)** using the **COMSOAL** (Computer Method of Sequencing Operations for Assembly Lines) heuristic. The tool provides an interactive environment to assign manufacturing tasks to workstations efficiently, minimizing idle time and maximizing line efficiency.

## Key Features
* **Dynamic Task Management:** Users can input tasks, process times, and predecessor relationships directly through the GUI.
* **Automated Precedence Diagrams:** Integrates `NetworkX` and `Matplotlib` to automatically generate and visualize the precedence network of tasks.
* **Step-by-Step COMSOAL Execution:** Runs the COMSOAL algorithm and displays the iterative selection process (Eligible tasks, Fit tasks, Random variable U, and Selected task) in a detailed data table.
* **Performance Metrics:** Automatically calculates and reports final line efficiency, balance loss, and optimal station assignments based on the target cycle time.

## Technologies Used
* **Language:** Python
* **GUI Framework:** `Tkinter` & `ttk`
* **Graph Visualization:** `NetworkX` & `Matplotlib`

## How to Run
1. Clone this repository.
2. Install the required libraries:
   ```bash
   pip install networkx matplotlib
