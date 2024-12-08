import os
import requests
from datetime import datetime, timedelta
import Hamlib
import time
from skyfield.api import load, Topos
import threading
from queue import Queue
import streamlit as sl

TLE_URL                 =       "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle"
TLE_FILENAME            =       "tle.txt"
SATELLITE_NAMES         =       ""
station                 =       Topos(latitude_degrees=47.165101053547325, longitude_degrees=8.295939429046944, elevation_m=495)
satellites              =       load.tle_file(TLE_FILENAME)

def doppler_shift(freq, rad_vel):
    return freq * (1 - (rad_vel / 299792.458))

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

satellite = {sat.name: sat for sat in satellites}[selected_sat]

sl.sidebar.subheader("Radio Config",divider=True)

selected_device = sl.sidebar.selectbox("Select Device", list_devices("tty.usb"))

selected_rig_key = sl.sidebar.selectbox("Select Rig", options=list(available_rig_ids.keys()))
selected_rig_id = available_rig_ids[selected_rig_key]

selected_vfo = sl.sidebar.selectbox("Select VFO", options={"VFO A", "VFO B", "Current VFO"})

if selected_vfo == "VFO A":
    vfo = Hamlib.RIG_VFO_A
elif selected_vfo == "VFO B":
    vfo = Hamlib.RIG_VFO_B
elif selected_vfo == "Current VFO":
    vfo = Hamlib.RIG_VFO_CURR

selected_freq = sl.sidebar.number_input("Center Frequency (Hz)", min_value=144000000,max_value=440000000, value=437800000)

sl.sidebar.subheader("Tracking Settings", divider=True)

selected_interval = sl.sidebar.select_slider("Update Interval (s)", options=[0.1,0.5,1,3,5,10], value=1)

Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_ERR)
rig = Hamlib.Rig(rig_model=selected_rig_id)
rig.set_conf("rig_pathname", f"/dev/{selected_device}")

def sat_tracking():

    rig.open()
    
    count = 0

    while count < 10:

        # Aktuelle Zeit berechnen
        ts = load.timescale()
        t = ts.now()

        # Ausrechnen ob Sat schon über
        # dem Horizont ist oder nicht
        difference = satellite - station
        topocentric = difference.at(t)
        alt, az, distance = topocentric.altaz()

        # Relative Geschwindigkeit und
        # Radialgeschwindigkeit ausrechnen
        satellite_position = satellite.at(t)
        observer_position = station.at(t)
        relative_position = satellite_position - observer_position
        relative_velocity = relative_position.velocity.km_per_s
        radial_velocity = relative_position.position.km @ relative_velocity / relative_position.distance().km

        rig.set_vfo(vfo)

        if rig.set_freq(vfo, round(doppler_shift(selected_freq, radial_velocity))) != 0:
            print(f"Satellite:\t{satellite.name}")
            print(f"Frequency:\t{round(doppler_shift(selected_freq, radial_velocity) / 1000000,6)} MHz")
            print(f"Elevation:\t{round(alt.degrees)}°")
            print(f"Azimut:\t\t{round(az.degrees)}°")
            print(f"Distance:\t{round(distance.km)} km")
            print("")
        else:
            print(f"Error: {Hamlib.rigerror(rig.error_status)}")
        
        count += 1
            
        # Wartezeit vor der nächsten Aktualisierung
        time.sleep(selected_interval)

    rig.set_vfo(vfo)
    rig.set_freq(vfo, selected_freq)

sl.sidebar.button("Start Tracking", use_container_width=True, on_click=sat_tracking, type="primary")

sl.title(f"Tracking {selected_sat}")

debug = f'''
    Device:\t\t\t{selected_device}
    Rid ID:\t\t\t{selected_rig_id}
    Rig key:\t\t{selected_rig_key}
    Current freq:\t\t{selected_freq}
    Sat:\t\t\t{selected_sat}
    Interval:\t\t{selected_interval}
    TLE file date:\t\t{modification_date}
    Selected VFO:\t\t{selected_vfo}
'''

sl.code(debug, language=None)