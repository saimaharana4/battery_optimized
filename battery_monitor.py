# import psutil
# import time
# import threading
# import tkinter as tk
# from tkinter import messagebox, scrolledtext
# from datetime import datetime
# from queue import Queue, Empty
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.pyplot as plt
# from matplotlib.dates import DateFormatter
# import sqlite3
#
# # Function to create a new database connection
# def create_connection():
#     conn = sqlite3.connect(r'D:\battery\battery_data.db')
#     c = conn.cursor()
#     c.execute('''CREATE TABLE IF NOT EXISTS battery_data
#                  (timestamp TEXT, date TEXT, time TEXT, percentage INTEGER, plugged BOOLEAN)''')
#     conn.commit()
#     return conn
#
# def insert_battery_data(conn, timestamp, date, time, percentage, plugged):
#     with conn:
#         c = conn.cursor()
#         c.execute("INSERT INTO battery_data (timestamp, date, time, percentage, plugged) VALUES (?, ?, ?, ?, ?)",
#                   (timestamp, date, time, percentage, plugged))
#
# def fetch_battery_data():
#     conn = create_connection()
#     c = conn.cursor()
#     c.execute("SELECT timestamp, percentage FROM battery_data")
#     data = c.fetchall()
#     conn.close()
#     return data
#
# def clear_battery_data():
#     conn = create_connection()
#     with conn:
#         c = conn.cursor()
#         c.execute("DELETE FROM battery_data")
#     conn.close()
# def send_notification(title, message):
#     try:
#         messagebox.showinfo(title, message)
#         log_message(f"Notification: {title} - {message}")
#     except Exception as e:
#         log_message(f"Error sending notification: {e}")
#
# def log_message(message):
#     timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     full_message = f"[{timestamp}] {message}"
#     log_text.config(state=tk.NORMAL)
#     log_text.insert(tk.END, f"{full_message}\n")
#     log_text.config(state=tk.DISABLED)
#     log_text.see(tk.END)
#     print(full_message)  # Debugging statement
#
# def monitor_battery(stop_event, log_queue):
#     last_percent = None
#     last_plugged = None
#     conn = create_connection()
#
#     while not stop_event.is_set():
#         try:
#             battery = psutil.sensors_battery()
#             percent = battery.percent
#             plugged = battery.power_plugged
#
#             now = datetime.now()
#             timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
#             date = now.strftime('%Y-%m-%d')
#             time_str = now.strftime('%H:%M:%S')
#
#             insert_battery_data(conn, timestamp, date, time_str, percent, plugged)
#
#             if percent != last_percent or plugged != last_plugged:
#                 log_queue.put(f"Battery status: {percent}%, Plugged in: {plugged}")
#                 last_percent = percent
#                 last_plugged = plugged
#
#                 if plugged and percent >= 80:
#                     send_notification("Battery is 80%, Remove the Charger.", f"Battery is at {percent}%. Unplug the charger.")
#                 elif not plugged and percent <= 30:
#                     send_notification("Battery is in 30%, Connect the Charger. ", f"Battery is at {percent}%. Please charge your battery.")
#                 elif plugged and percent == 100:
#                     send_notification("Battery Fully Charged", "Battery is at 100%. Please unplug the charger.")
#                 elif not plugged and percent <= 5:
#                     send_notification("Critical Battery Level", f"Battery is critically low at {percent}%. Charge immediately!")
#                 elif not plugged and percent == 0:
#                     send_notification("Battery Depleted", "Battery is depleted. Shutting down soon.")
#         except Exception as e:
#             log_queue.put(f"Error in monitoring battery: {e}")
#
#         time.sleep(240)  # Check every 20 seconds
#
#     conn.close()
#
# def process_log_queue(log_queue):
#     while not log_queue.empty():
#         try:
#             message = log_queue.get_nowait()
#             log_message(message)
#         except Empty:
#             break
#
# def start_monitoring():
#     global stop_event
#     stop_event.clear()
#     monitor_thread = threading.Thread(target=monitor_battery, args=(stop_event, log_queue))
#     monitor_thread.daemon = True
#     monitor_thread.start()
#     messagebox.showinfo("Battery Monitor", "Battery monitoring started!")
#     log_message("Monitoring started")
#
# def stop_monitoring():
#     global stop_event
#     stop_event.set()
#     clear_battery_data()
#     messagebox.showinfo("Battery Monitor", "Battery monitoring stopped and data cleared!")
#     log_message("Monitoring stopped")
#
# def update_log():
#     process_log_queue(log_queue)
#     update_graph()
#     root.after(90000, update_log)  # Schedule the next update
#
# def update_graph():
#     data = fetch_battery_data()
#     if data:
#         times, percents = zip(*data)
#         times = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S') for t in times]
#         ax.clear()
#         ax.bar(times, percents, label='Battery Level', color='purple')
#         ax.set_ylabel('Battery Level (%)', fontsize=12, fontweight='bold')
#         ax.set_xlabel('Time', fontsize=12, fontweight='bold')
#         ax.legend()
#         ax.grid(True)
#         ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
#         fig.autofmt_xdate()
#         canvas.draw()
#
# def clear_logs():
#     log_text.config(state=tk.NORMAL)
#     log_text.delete('1.0', tk.END)
#     log_text.config(state=tk.DISABLED)
#     log_message("Logs cleared")
#
# if __name__ == "__main__":
#     # Creating the main window
#     root = tk.Tk()
#     root.title("Battery Monitor")
#     root.geometry("1200x800")
#     root.configure(bg='#f0f0f0')
#
#     stop_event = threading.Event()
#     log_queue = Queue()
#
#     # Adding Start button
#     start_button = tk.Button(root, text="Start Monitoring", command=start_monitoring, bg='#28a745', fg='white', font=('Helvetica', 12, 'bold'))
#     start_button.pack(pady=10)
#
#     # Adding Stop button
#     stop_button = tk.Button(root, text="Stop Monitoring", command=stop_monitoring, bg='#dc3545', fg='white', font=('Helvetica', 12, 'bold'))
#     stop_button.pack(pady=10)
#
#     # Frame for log window and graph
#     frame = tk.Frame(root)
#     frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
#
#     # Adding a scrolled text widget for monitoring logs
#     log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state=tk.DISABLED, width=100, height=10, bg='#000', fg='#fff', font=('Consolas', 12))
#     log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
#
#     # Create a figure for the plot
#     fig, ax = plt.subplots()
#     ax.set_title("Battery Level Over Time", fontsize=16, color='blue', fontweight='bold')
#
#     # Create a canvas to display the plot
#     canvas = FigureCanvasTkAgg(fig, master=frame)
#     canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
#
#     # Adding Clear Logs button
#     clear_button = tk.Button(root, text="Clear Logs", command=clear_logs, bg='#ffc107', fg='black',
#                              font=('Helvetica', 12, 'bold'))
#     clear_button.pack(pady=10)
#
#     # Schedule the first log update
#     root.after(90000, update_log)
#
#     # Running the Tkinter main loop
#     root.mainloop()
#
#
# #-------------------------------------

import psutil
import time
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
from queue import Queue, Empty
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import sqlite3

# Function to create a new database connection
def create_connection():
    conn = sqlite3.connect(r'D:\battery\battery_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS battery_data
                 (timestamp TEXT, date TEXT, time TEXT, percentage INTEGER, plugged BOOLEAN)''')
    conn.commit()
    return conn

def insert_battery_data(conn, timestamp, date, time, percentage, plugged):
    with conn:
        c = conn.cursor()
        c.execute("INSERT INTO battery_data (timestamp, date, time, percentage, plugged) VALUES (?, ?, ?, ?, ?)",
                  (timestamp, date, time, percentage, plugged))

def fetch_battery_data():
    conn = create_connection()
    c = conn.cursor()
    c.execute("SELECT timestamp, percentage FROM battery_data")
    data = c.fetchall()
    conn.close()
    return data

def clear_battery_data():
    conn = create_connection()
    with conn:
        c = conn.cursor()
        c.execute("DELETE FROM battery_data")
    conn.close()

def send_notification(title, message):
    try:
        messagebox.showinfo(title, message)
        log_message(f"Notification: {title} - {message}")
    except Exception as e:
        log_message(f"Error sending notification: {e}")

def log_message(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    full_message = f"[{timestamp}] {message}"
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, f"{full_message}\n")
    log_text.config(state=tk.DISABLED)
    log_text.see(tk.END)
    print(full_message)  # Debugging statement

def clear_logs():
    log_text.config(state=tk.NORMAL)
    log_text.delete('1.0', tk.END)
    log_text.config(state=tk.DISABLED)
    log_message("Logs cleared")

def monitor_battery(stop_event, log_queue):
    last_percent = None
    last_plugged = None
    conn = create_connection()

    while not stop_event.is_set():
        try:
            battery = psutil.sensors_battery()
            percent = battery.percent
            plugged = battery.power_plugged

            now = datetime.now()
            timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
            date = now.strftime('%Y-%m-%d')
            time_str = now.strftime('%H:%M:%S')

            insert_battery_data(conn, timestamp, date, time_str, percent, plugged)

            if percent != last_percent or plugged != last_plugged:
                log_queue.put(f"Battery status: {percent}%, Plugged in: {plugged}")
                last_percent = percent
                last_plugged = plugged

                if plugged and percent >= 80:
                    send_notification("Battery is 80%, Remove the Charger.", f"Battery is at {percent}%. Unplug the charger.")
                elif not plugged and percent <= 30:
                    send_notification("Battery is in 30%, Connect the Charger. ", f"Battery is at {percent}%. Please charge your battery.")
                elif plugged and percent == 100:
                    send_notification("Battery Fully Charged", "Battery is at 100%. Please unplug the charger.")
                elif not plugged and percent <= 5:
                    send_notification("Critical Battery Level", f"Battery is critically low at {percent}%. Charge immediately!")
                elif not plugged and percent == 0:
                    send_notification("Battery Depleted", "Battery is depleted. Shutting down soon.")
        except Exception as e:
            log_queue.put(f"Error in monitoring battery: {e}")

        time.sleep(240)  # Check every 240 seconds (4 minutes)

    conn.close()

def process_log_queue(log_queue):
    while not log_queue.empty():
        try:
            message = log_queue.get_nowait()
            log_message(message)
        except Empty:
            break

def start_monitoring():
    global stop_event
    stop_event.clear()
    monitor_thread = threading.Thread(target=monitor_battery, args=(stop_event, log_queue))
    monitor_thread.daemon = True
    monitor_thread.start()
    messagebox.showinfo("Battery Monitor", "Battery monitoring started!")
    log_message("Monitoring started")

def stop_monitoring():
    global stop_event
    stop_event.set()
    clear_battery_data()
    messagebox.showinfo("Battery Monitor", "Battery monitoring stopped and data cleared!")
    log_message("Monitoring stopped")

def update_log():
    process_log_queue(log_queue)
    update_graph()
    root.after(90000, update_log)  # Schedule the next update

def update_graph():
    data = fetch_battery_data()
    if data:
        times, percents = zip(*data)
        times = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S') for t in times]
        ax.clear()
        ax.bar(times, percents, label='Battery Level', color='purple')
        ax.set_ylabel('Battery Level (%)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Time', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True)
        ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate()
        canvas.draw()

if __name__ == "__main__":
    # Creating the main window
    root = tk.Tk()
    root.title("Battery Monitor")
    root.geometry("1200x800")
    root.configure(bg='#f0f0f0')

    stop_event = threading.Event()
    log_queue = Queue()

    # Adding Start button
    start_button = tk.Button(root, text="Start Monitoring", command=start_monitoring, bg='#28a745', fg='white', font=('Helvetica', 12, 'bold'))
    start_button.pack(pady=10)

    # Adding Stop button
    stop_button = tk.Button(root, text="Stop Monitoring", command=stop_monitoring, bg='#dc3545', fg='white', font=('Helvetica', 12, 'bold'))
    stop_button.pack(pady=10)

    # Adding Clear Logs button
    clear_button = tk.Button(root, text="Clear Logs", command=clear_logs, bg='#ffc107', fg='black', font=('Helvetica', 12, 'bold'))
    clear_button.pack(pady=10)

    # Frame for log window and graph
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Adding a scrolled text widget for monitoring logs
    log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, state=tk.DISABLED, width=100, height=10, bg='#000', fg='#fff', font=('Consolas', 12))
    log_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create a figure for the plot
    fig, ax = plt.subplots()
    ax.set_title("Battery Level Over Time", fontsize=16, color='blue', fontweight='bold')

    # Create a canvas to display the plot
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    # Schedule the first log update
    root.after(90000, update_log)

    # Running the Tkinter main loop
    root.mainloop()

