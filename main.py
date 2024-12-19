'''DPLR Sat Tracking'''
import os
from datetime import datetime, timedelta
import time
import requests
import Hamlib
from skyfield.api import load, Topos
import streamlit as sl

sl.set_page_config(
    page_title="DPLR Sat Tracker",
    page_icon="📡",
    layout="centered",
    initial_sidebar_state="auto"
)

station_lat             =       None
station_lng             =       None
station_elevation       =       None
TLE_URL                 =       "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle"
TLE_FILENAME            =       "tle.txt"
SATELLITE_NAMES         =       ""
modification_date       =       datetime.now()
station                 =       Topos(
    latitude_degrees=station_lat or 47.165101053547325,
    longitude_degrees=station_lng or 8.295939429046944,
    elevation_m=station_elevation or 495
    )

def doppler_shift(freq, rad_vel):
    """Calculates doppler frquency shift"""
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

satellites = load.tle_file(TLE_FILENAME)


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

with sl.sidebar:

    sl.title("DPLR Sat Tracker")
    sl.caption("Track satellites frequencies with ease. Doppler effect correction? Sat Tracker will do it for you.")

    selected_sat = sl.selectbox("Select Satellite", SATELLITE_NAMES)

    satellite = {sat.name: sat for sat in satellites}[selected_sat]

    sl.subheader("Station Config",divider=True)

    col1,col2,col3 = sl.columns(3)

    with col1:
        station_lng = sl.text_input("QTH lng", value=47.165101053547325)

    with col2: 
        station_lat = sl.text_input("QTH lat", value=8.295939429046944)

    with col3:
        station_elevation = sl.text_input("Elevation (m)", value=495)

    sl.subheader("Radio Config",divider=True)

    col1,col2 = sl.columns(2)
    with col1:
        selected_device = sl.selectbox("Select Device", list_devices("tty.usb"))
    with col2:
        selected_rig_key = sl.selectbox("Select Rig", options=list(available_rig_ids.keys()))
        selected_rig_id = available_rig_ids[selected_rig_key]

    col1,col2 = sl.columns(2)
    with col1:
        selected_vfo = sl.selectbox("Select VFO", options=["VFO A", "VFO B", "Current"])

        if selected_vfo == "VFO A":
            vfo = Hamlib.RIG_VFO_A
        elif selected_vfo == "VFO B":
            vfo = Hamlib.RIG_VFO_B
        elif selected_vfo == "Current VFO":
            vfo = Hamlib.RIG_VFO_CURR
        else:
            vfo = Hamlib.RIG_VFO_CURR

    with col2:
        selected_mode = sl.selectbox("Select Mode", options=["USB","LSB","FM","CW"])

        if selected_mode == "USB":
            mode = Hamlib.RIG_MODE_USB
        elif selected_mode == "LSB":
            mode = Hamlib.RIG_MODE_LSB
        elif selected_mode == "FM":
            mode = Hamlib.RIG_MODE_FMN
        elif selected_mode == "CW":
            mode = Hamlib.RIG_MODE_CW
        else:
            mode = Hamlib.RIG_MODE_USB
    
    col1,col2 = sl.columns(2)
    with col1:
        selected_freq = sl.number_input(
            "Center Frequency (Hz)",
            min_value=144000000,
            max_value=440000000,
            value=437800000
        )
    
    with col2:
        selected_passband = sl.number_input(
            "Passband Width",
            min_value=500,
            max_value=3600,
            value=2700
        )

    sl.subheader("Tracking Settings", divider=True)

    selected_interval = sl.select_slider(
        "Update Interval (s)",
        options=[0.1,0.5,1,3,5,10],
        value=0.1
    )

Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_ERR)
rig = Hamlib.Rig(rig_model=selected_rig_id)
rig.set_conf("rig_pathname", f"/dev/{selected_device}")

if selected_device != None:
    rig.open()

sl.title(f"Tracking {selected_sat}")

debug = f'''
    Device:\t\t{selected_device}
    Rid ID:\t\t{selected_rig_id}
    Rig Name:\t{selected_rig_key}
    Current QRG:\t{selected_freq / 1000000:.6f} MHz
    Satellite:\t{selected_sat}
    Interval:\t{selected_interval} s
    TLE date:\t{modification_date.strftime("%A, %d. %B %Y %H:%M:%S")}
    VFO:\t\t{selected_vfo}
    Mode:\t\t{selected_mode}
    Passband:\t{selected_passband} Hz
    Latitude:\t{station_lat}°
    Longitude:\t{station_lng}°
    Elevation:\t{station_elevation} m
'''
sl.code(debug, language=None)

def sat_tracking():
    """Tracks Satellite and calculates freq shift for doppler effect"""

    output_placeholder = sl.empty()

    while True:

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
        rig.set_mode(mode, selected_passband)

        rig.set_freq(vfo, round(doppler_shift(selected_freq, radial_velocity)))
      
        output = f'''
            Satellite:\t{satellite.name}
            Frequency:\t{round(doppler_shift(selected_freq, radial_velocity) / 1000000,6)} MHz
            Elevation:\t{round(alt.degrees)}°
            Azimuth:\t{round(az.degrees)}°
            Distance:\t{round(distance.km)} km
        '''
        
        output_placeholder.code(output, language=None)

        # Wartezeit vor der nächsten Aktualisierung
        time.sleep(selected_interval)

def disconnect_rig():
    """Disconnect from rig and reset frequency"""
    rig.set_vfo(vfo)
    rig.set_freq(vfo, selected_freq)
    rig.close()

def set_split():
    """Set split mode"""
    rig.set_split_mode(Hamlib.RIG_SPLIT_ON)
    rig.set_split_freq(Hamlib.RIG_VFO_OTHER, 145500000)


if sl.sidebar.button("Start Tracking", use_container_width=True, type="primary", disabled=selected_device is None):
    sat_tracking()

if sl.sidebar.button("Stop Tracking", use_container_width=True, type="secondary", disabled=selected_device is None):
    disconnect_rig()

if sl.sidebar.button("Set Split Mode", use_container_width=True, type="secondary",disabled=selected_device is None):
    set_split()
