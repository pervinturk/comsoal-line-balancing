import tkinter as tk
from tkinter import ttk, messagebox
import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

class ComsoalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("COMSOAL Task Balancing")
        self.root.geometry("1600x1400")
        self.root.configure(bg="#2e2e2e")

        style = ttk.Style()
        default_font = ("Segoe UI", 12)
        self.root.option_add("*Font", default_font)
        
        style.configure("TLabel", font=default_font, foreground="white", background="#2e2e2e")
        style.configure("TButton", font=default_font, background="#444", foreground="white")
        style.configure("TCheckbutton", font=default_font, background="#2e2e2e", foreground="white")
        style.configure("Treeview", font=default_font, rowheight=32, background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e")
        style.configure("Treeview.Heading", font=("Segoe UI", 13, "bold"))

        style.theme_use('clam')
        style.configure("TLabel", foreground="white", background="#2e2e2e")
        style.configure("TButton", background="#444", foreground="white")
        style.configure("TCheckbutton", background="#2e2e2e", foreground="white")
        style.configure("Treeview", background="#1e1e1e", foreground="white", fieldbackground="#1e1e1e")
        style.map("Treeview", background=[('selected', '#444')])

        self.tasks = {
            "a": {"time": 20, "predecessors": []},
            "b": {"time": 6, "predecessors": ["a"]},
            "c": {"time": 5, "predecessors": ["b"]},
            "d": {"time": 21, "predecessors": []},
            "e": {"time": 8, "predecessors": []},
            "f": {"time": 35, "predecessors": []},
            "g": {"time": 15, "predecessors": ["c", "d"]},
            "h": {"time": 10, "predecessors": ["g"]},
            "i": {"time": 15, "predecessors": ["e", "h"]},
            "j": {"time": 5, "predecessors": ["c"]},
            "k": {"time": 46, "predecessors": ["f", "i", "j"]},
            "l": {"time": 16, "predecessors": ["k"]},
        }

        self.sequence = []
        self.stations = []

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.setup_input_tab()
        self.setup_diagram_tab()
        self.setup_result_tab()
        self.setup_step_tab()
        self.refresh_task_list()

    def setup_input_tab(self):
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='1. Task Entry')

        # Remove the Task Name label and entry at the top

        # Labels for the fields
        ttk.Label(self.tab1, text="Task ID").grid(row=0, column=0, padx=10)
        ttk.Label(self.tab1, text="Task Name").grid(row=0, column=1, padx=10)
        ttk.Label(self.tab1, text="Time").grid(row=0, column=2, padx=10)
        ttk.Label(self.tab1, text="Predecessors (comma-separated)").grid(row=0, column=3, padx=10)

        # Entry fields
        self.entry_taskid = ttk.Entry(self.tab1, width=15)
        self.entry_taskname = ttk.Entry(self.tab1, width=20)
        self.entry_time = ttk.Entry(self.tab1, width=10)
        self.entry_preds = ttk.Entry(self.tab1, width=50)
        self.entry_taskid.grid(row=1, column=0, padx=5, pady=5)
        self.entry_taskname.grid(row=1, column=1, padx=5, pady=5)
        self.entry_time.grid(row=1, column=2, padx=5, pady=5)
        self.entry_preds.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(self.tab1, text="Add Task", command=self.add_task).grid(row=1, column=4, padx=10, ipadx=10, ipady=5)
        ttk.Button(self.tab1, text="Delete Task", command=self.delete_selected_task).grid(row=1, column=5, padx=10, ipadx=10, ipady=5)

        # Create a frame for the table and scrollbar
        table_frame = ttk.Frame(self.tab1)
        table_frame.grid(row=2, column=0, columnspan=6, padx=10, pady=10, sticky="nsew")

        self.task_table = ttk.Treeview(
            table_frame,
            columns=["Task ID", "Task Name", "Time", "Preds"],
            show="headings",
            height=10
        )
        for col, w in zip(["Task ID", "Task Name", "Time", "Preds"], [60, 120, 60, 300]):
            self.task_table.heading(col, text=col)
            self.task_table.column(col, width=w, anchor="center")

        # Add vertical scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.task_table.yview)
        self.task_table.configure(yscrollcommand=vsb.set)
        self.task_table.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        self.task_table.bind("<Double-1>", self.on_cell_double_click)

        ttk.Label(self.tab1, text="Cycle Time:").grid(row=3, column=0)
        self.entry_cycle = ttk.Entry(self.tab1, width=5)
        self.entry_cycle.insert(0, "70")
        self.var_random = tk.BooleanVar(value=True)
        ttk.Checkbutton(self.tab1, text="Random Task Selection", variable=self.var_random).grid(row=3, column=2)
        ttk.Button(self.tab1, text="Start COMSOAL", command=self.run_comsoal).grid(row=3, column=3, pady=10)

    def refresh_task_list(self):
        for row in self.task_table.get_children():
            self.task_table.delete(row)
        for t in sorted(self.tasks):
            time = self.tasks[t]['time']
            preds = ', '.join(self.tasks[t]['predecessors']) or '-'
            task_name = self.tasks[t].get('name', '')
            self.task_table.insert("", "end", values=(t, task_name, time, preds))

    def add_task(self):
        task_id = self.entry_taskid.get().strip()
        task_name = self.entry_taskname.get().strip()
        try:
            time = int(self.entry_time.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number.")
            return
        preds = [p.strip() for p in self.entry_preds.get().split(',') if p.strip()]
        if task_id:
            self.tasks[task_id] = {"name": task_name, "time": time, "predecessors": preds}
            self.refresh_task_list()
            self.entry_taskid.delete(0, tk.END)
            self.entry_taskname.delete(0, tk.END)
            self.entry_time.delete(0, tk.END)
            self.entry_preds.delete(0, tk.END)

    def delete_selected_task(self):
        selected = self.task_table.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a task to delete.")
            return
        for item in selected:
            task_name = self.task_table.item(item)['values'][0]
            # Remove this task from all predecessors
            for t in self.tasks.values():
                if task_name in t['predecessors']:
                    t['predecessors'].remove(task_name)
            # Then delete the task
            self.tasks.pop(task_name, None)
        self.refresh_task_list()

    def on_cell_double_click(self, event):
        item_id = self.task_table.identify_row(event.y)
        col = self.task_table.identify_column(event.x)
        if not item_id or col == "#0":
            return
        col_index = int(col[1:]) - 1
        cols = ["Task ID", "Task Name", "Time", "Preds"]
        if col_index >= len(cols):
            return

        old_values = self.task_table.item(item_id)['values']
        old_value = old_values[col_index]
        entry = tk.Entry(self.tab1)
        entry.insert(0, old_value)
        bbox = self.task_table.bbox(item_id, column=col)
        if not bbox:
            return
        entry.place(x=bbox[0] + self.task_table.winfo_x(),
                    y=bbox[1] + self.task_table.winfo_y(),
                    width=bbox[2], height=bbox[3])
        entry.focus()

        def save_edit(_=None):
            new_val = entry.get()
            values = list(old_values)
            values[col_index] = new_val
            self.task_table.item(item_id, values=values)
            entry.destroy()

            task_id = values[0]
            if cols[col_index] == "Task ID":
                if new_val in self.tasks:
                    messagebox.showerror("Error", f"{new_val} already exists.")
                    return
                self.tasks[new_val] = self.tasks.pop(old_value)
                # Also update predecessor names in all other tasks
                for task in self.tasks.values():
                    task["predecessors"] = [new_val if p == old_value else p for p in task["predecessors"]]
            elif cols[col_index] == "Task Name":
                self.tasks[task_id]["name"] = new_val
            elif cols[col_index] == "Time":
                try:
                    self.tasks[task_id]["time"] = float(new_val.replace(",", "."))
                except:
                    messagebox.showerror("Error", "Time must be numeric.")
            elif cols[col_index] == "Preds":
                preds = [p for p in new_val.replace(',', ' ').split() if p.isalpha()]
                self.tasks[task_id]["predecessors"] = preds

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", save_edit)

    def setup_diagram_tab(self):
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='2. Precedence Diagram')
        ttk.Button(self.tab2, text="Draw Tree", command=self.draw_graph).pack(pady=10)
        self.canvas_frame = ttk.Frame(self.tab2)
        self.canvas_frame.pack(fill='both', expand=True)

    def setup_result_tab(self):
        self.tab3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab3, text='3. Result')
        self.output = tk.Text(self.tab3, width=110, height=30, bg="#1e1e1e", fg="white")
        self.output.pack(padx=10, pady=10)

    def setup_step_tab(self):
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text='4. Step by Step')
        self.step_table = ttk.Treeview(self.tab4, columns=["A", "B", "F", "U", "Selected", "Idle"], show="headings")
        for col in ["A", "B", "F", "U", "Selected", "Idle"]:
            self.step_table.heading(col, text=col)
            self.step_table.column(col, anchor="center", width=180)
        self.step_table.pack(fill='both', expand=True)

    def draw_graph(self):
        G = nx.DiGraph()
    
        # Check all task names and collect missing dependencies
        missing = set()
        for t, info in self.tasks.items():
            G.add_node(t)
            for p in info["predecessors"]:
                if p not in self.tasks:
                    missing.add(p)
                else:
                    G.add_edge(p, t)
    
        if missing:
            messagebox.showerror("Error", f"Missing task(s): {', '.join(sorted(missing))}")
            return
    
        # Layer calculation
        levels = {}
        for node in nx.topological_sort(G):
            preds = list(G.predecessors(node))
            levels[node] = 0 if not preds else max(levels[p] for p in preds) + 1
    
        pos = {}
        layer_map = defaultdict(list)
        for node, lvl in levels.items():
            layer_map[lvl].append(node)
        for x, nodes in layer_map.items():
            for y, node in enumerate(sorted(nodes)):
                pos[node] = (x * 2.5, -y * 2)
    
        # Draw the graph
        fig = plt.Figure(figsize=(14, 7), dpi=100)
        ax = fig.add_subplot(111)
        labels = {n: f"{n}\n{self.tasks[n]['time']}" for n in G.nodes()}
        nx.draw(G, pos, with_labels=True, labels=labels, arrows=True, ax=ax,
                node_color='#1f78b4', node_size=1800, font_size=10, edge_color='gray')
        ax.set_title("Precedence Diagram (Fully Aligned)", fontsize=12)
        ax.axis("off")
    
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
    
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

    def run_comsoal(self):
        try:
            C = float(self.entry_cycle.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Cycle Time must be numeric.")
            return

        A = set(self.tasks)
        self.sequence = []
        self.stations = []
        current_station = []
        remaining = C
        idle_total = 0

        self.output.delete("1.0", tk.END)
        for item in self.step_table.get_children():
            self.step_table.delete(item)

        self.output.insert(tk.END, f"Cycle Time = {C}\n\n")

        while A:
            B = [t for t in A if all(p not in A for p in self.tasks[t]["predecessors"])]
            F = [t for t in B if self.tasks[t]["time"] <= remaining]
            U = round(random.random(), 2)

            selected = "-"
            idle_display = "-"
            if not F:
                self.stations.append(current_station)
                idle_total += remaining
                idle_display = f"Open ({remaining:.2f})"
                current_station = []
                remaining = C
            else:
                if self.var_random.get():
                    U = round(random.random(), 2)
                else:
                    U = "-"
                
                if isinstance(U, float) and len(F) > 0:
                    index = int(U * len(F))
                    index = min(index, len(F) - 1)
                    task = sorted(F)[index]
                else:
                    task = sorted(F)[0]
            
                A.remove(task)
                current_station.append(task)
                self.sequence.append(task)
                remaining -= self.tasks[task]['time']
                selected = task
                idle_display = f"{remaining:.2f}"

            self.step_table.insert("", "end", values=[
                ','.join(sorted(A)),
                ','.join(sorted(B)),
                ','.join(sorted(F)),
                U, selected, idle_display
            ])

        self.stations.append(current_station)
        idle_total += remaining

        total_time = sum(self.tasks[t]['time'] for t in self.tasks)
        n = len(self.stations)
        self.output.insert(tk.END, f"Task Sequence: {self.sequence}\n")
        for i, st in enumerate(self.stations):
            self.output.insert(tk.END, f"Station {i+1}: {st}\n")
        self.output.insert(tk.END, f"\nEfficiency = {total_time} / ({n} * {C}) = {total_time/(n*C):.2%}\n")
        self.output.insert(tk.END, f"Balance Loss = {1 - total_time/(n*C):.2%}\n")

# Start the program
if __name__ == '__main__':
    root = tk.Tk()
    app = ComsoalApp(root)
    root.mainloop()