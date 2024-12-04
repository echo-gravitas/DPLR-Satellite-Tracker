import os
import streamlit as sl

# Local Variables
tle_file = "tle.txt"

# Read TLE
def load_tle(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    satellite_names = [lines[i].strip() for i in range(0, len(lines), 3)]
    return satellite_names

satellite_names = load_tle(tle_file)

# Read connected devices
def list_devices(filter_pattern=None):
    dev_path = "/dev/"
    devices = os.listdir(dev_path)
    if filter_pattern:
        devices = [device for device in devices if filter_pattern in device]
    return devices

devices = list_devices("tty.")

sl.sidebar.title(
    "Sat Tracker"
)
sl.sidebar.caption("Track satellites frequencies with ease. Doppler effect correction? Sat Tracker will do it for you.")

sl.sidebar.subheader("Radio Config",divider=True)

selected_sat = sl.sidebar.selectbox("Select Satellite", satellite_names)

freq = sl.sidebar.number_input("Center Frequency (Hz)", min_value=144000000,max_value=440000000, value=437800000)

selscted_device = sl.sidebar.selectbox("Select device", devices)

rig = sl.sidebar.selectbox("Select Rig",{"ICOM IC-705":3085,"ICOM IC-7300":3073,"ICOM IC-7760":3092})

start_tracking = sl.sidebar.button("Start Tracking", use_container_width=True, type="primary")

stop_tracking = sl.sidebar.button("Stop Tracking", use_container_width=True, type="secondary")

if start_tracking:
    sl.write(f"Tracking für {selected_sat} auf Frequenz {freq} Hz gestartet")

