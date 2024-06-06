import subprocess

# Path to your main battery monitor script
script_path = r"D:\battery\battery_monitor.py"

# Run the battery monitor script in the background
subprocess.Popen(['python', script_path], creationflags=subprocess.CREATE_NO_WINDOW)
