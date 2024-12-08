import os
import  requests
from datetime import datetime, timedelta
import Hamlib
from skyfield.api import load, Topos
import streamlit as sl

TLE_URL                 =       "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle"
TLE_FILENAME            =       "tle.txt"
SATELLITE_NAMES         =       ""

def load_local_tle(file_path):
    """Load and read TLEs from local file"""
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    names = [lines[i].strip() for i in range(0, len(lines), 3)]
    return names

# Check TLE file and load from remote if neccessary

if os.path.exists(TLE_FILENAME):
    SATELLITE_NAMES     =   load_local_tle(TLE_FILENAME)
    modification_time   =   os.path.getmtime(TLE_FILENAME)
    modification_date   =   datetime.fromtimestamp(modification_time)
    now                 =   datetime.now()
    file_age            =   now - modification_date

    if file_age > timedelta(hours=2):
        response        =   requests.get(TLE_URL, timeout=30)

        if response.status_code == 200:
            with open(TLE_FILENAME, "wb") as file:
                file.write(response.content)

else:
    response        =   requests.get(TLE_URL)
    if response.status_code == 200:
        with open(TLE_FILENAME, "wb") as file:
            file.write(response.content)
        SATELLITE_NAMES = load_local_tle(TLE_FILENAME)


def list_devices(filter_pattern=None):
    """Read connected devices from OS, filter and list them"""
    dev_path = "/dev/"
    devices = os.listdir(dev_path)
    if filter_pattern:
        devices = [device for device in devices if filter_pattern in device]
    return devices

os_available_devices    =       list_devices("tty.usb")
available_rig_ids       =       {"Icom IC-705":3085,"Icom IC-7300":3073,"Icom IC-7760":3092}

# Sidebar Content

sl.sidebar.title("Sat Tracker")

sl.sidebar.caption("Track satellites frequencies with ease. Doppler effect correction? Sat Tracker will do it for you.")

selected_sat = sl.sidebar.selectbox("Select Satellite", SATELLITE_NAMES)

sl.sidebar.subheader("Radio Config",divider=True)

selected_device = sl.sidebar.selectbox("Select Device", list_devices("tty.usb"))

selected_rig_key = sl.sidebar.selectbox("Select Rig", options=list(available_rig_ids.keys()))
selected_rig_id = available_rig_ids[selected_rig_key]

selected_vfo = sl.sidebar.selectbox("Select VFO", options={"VFO A", "VFO B", "Current VFO"},)

freq = sl.sidebar.number_input("Center Frequency (Hz)", min_value=144000000,max_value=440000000, value=437800000)

sl.sidebar.subheader("Tracking Settings", divider=True)

selected_interval = sl.sidebar.select_slider("Update Interval (s)", options=[0.1,0.5,1,3,5,10], value=1)

sl.sidebar.button("Start Tracking", use_container_width=True, type="primary")

# Main Content

sl.title(f"Tracking {selected_sat}")

sl.subheader("Debug")

debug = f'''
    Device:\t\t{selected_device}
    Rid ID:\t\t{selected_rig_id}
    Rig key:\t{selected_rig_key}
    Current freq:\t{freq}
    Sat:\t\t{selected_sat}
    Interval:\t{selected_interval}
    TLE file date:\t{modification_date}
    Selected VFO:\t{selected_vfo}
'''

sl.code(debug, language=None)