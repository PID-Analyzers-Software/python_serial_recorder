import sys
import time
import serial
import tkinter as tk
from tkinter import ttk, filedialog
from serial.tools import list_ports
from threading import Thread
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def find_esp32_port():
    ports = []
    for port in list_ports.comports():
        ports.append(port.device)
    return ports

data_list = []
recording = False

def record_serial_data(port, output_file):
    global recording, data_list
    with serial.Serial(port, 115200) as ser, open(output_file, 'w') as f:
        start_time = time.time()
        while recording:
            line = float(ser.readline().decode('utf-8').strip())
            elapsed_time = time.time() - start_time
            timestamp = f"{elapsed_time:.2f}"
            f.write(f"{timestamp}: {line}\n")
            data_tree.insert("", tk.END, values=(timestamp, line))
            data_tree.yview_moveto(1.0)
            data_list.append((elapsed_time, line))
            app.update()

def start_recording():
    global recording, data_list
    data_list = []
    if not recording:
        try:
            esp32_port = com_port_var.get()
            output_file = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if not output_file:
                return

            status_label.config(text=f"Recording serial data to {output_file}")
            recording = True
            record_button.config(text="Stop Recording")
            record_thread = Thread(target=record_serial_data, args=(esp32_port, output_file))
            record_thread.start()

        except Exception as e:
            status_label.config(text=str(e))
    else:
        recording = False
        status_label.config(text="Recording stopped")
        record_button.config(text="Start Recording")

def animate(i):
    x = [x[0] for x in data_list]
    y = [x[1] for x in data_list]
    ax.clear()
    ax.plot(x, y)
    ax.set_xlabel("Time", fontsize=12)
    ax.set_ylabel("Data", fontsize=12)
    ax.grid()
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    if len(x) > 0:
        min_time = max(0, x[-1] - 10)
        ax.set_xlim(min_time, min_time + 10)


app = tk.Tk()
app.title("ESP32 Serial Data Recorder")
app.geometry("1000x1000")
com_ports = find_esp32_port()

com_port_label = tk.Label(app, text="COM Port:")
com_port_label.grid(row=0, column=0, padx=(10, 5), pady=(10, 0), sticky="e")

com_port_var = tk.StringVar()
com_port_dropdown = ttk.Combobox(app, textvariable=com_port_var, values=com_ports)
com_port_dropdown.grid(row=0, column=1, padx=(5, 10), pady=(10, 0), sticky="w")

record_button = tk.Button(app, text="Start Recording", command=start_recording)
record_button.grid(row=1, column=0, columnspan=2, pady=(5, 10))

data_label = tk.Label(app, text="Data:")
data_label.grid(row=2, column=0, padx=(10, 5), pady=(5, 0), sticky="nw")

data_tree = ttk.Treeview(app, columns=("timestamp", "data"), show="headings")
data_tree.heading("timestamp", text="Timestamp")
data_tree.heading("data", text="Data")
data_tree.column("timestamp", width=150)
data_tree.column("data", width=300)
data_tree.grid(row=2, column=1, padx=(5, 10), pady=(5, 0), sticky="w")

status_label = tk.Label(app, text="")
status_label.grid(row=3, column=0, columnspan=2, pady=(5, 0))

# Real-time plot
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=app)
canvas.get_tk_widget().grid(row=4, column=0, columnspan=2, padx=(10, 10), pady=(10, 0))

ani = animation.FuncAnimation(fig, animate, interval=1000)

app.mainloop()

