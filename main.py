'''DPLR Sat Tracking'''
import os
from datetime import datetime, timedelta
import requests
import Hamlib
from skyfield.api import load,  Topos
import streamlit as sl
import time
from functions import *

sl.set_page_config(
    page_title="DPLR Sat Tracker",
    page_icon="📡",
    layout="centered",
    initial_sidebar_state="auto"
)

VFOS= ["VFO A", "VFO B", "Current"]
MODES = ["USB","LSB","FM","CW"]
STATION_LAT = None
STATION_LNG = None
STATION_ELEV = None
TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle"
TLE_FILENAME = "tle.txt"
SATELLITE_NAMES = None
MOD_DATE = datetime.now()
station = Topos(
    latitude_degrees=STATION_LAT or 47.165161521226466,
    longitude_degrees=STATION_LNG or 8.295906232497849,
    elevation_m=STATION_ELEV or 495
    )

# Check TLE file and load from remote if neccessary

if os.path.exists(TLE_FILENAME):
    SATELLITE_NAMES     =   load_local_tle(TLE_FILENAME)
    modification_time   =   os.path.getmtime(TLE_FILENAME)
    MOD_DATE   =   datetime.fromtimestamp(modification_time)
    now                 =   datetime.now()
    file_age            =   now - MOD_DATE

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
        STATION_LNG = sl.text_input("QTH Lng", value=47.165101053547325)

    with col2: 
        STATION_LAT = sl.text_input("QTH Lat", value=8.295939429046944)

    with col3:
        STATION_ELEV = sl.text_input("Elevation (m)", value=495)

    sl.subheader("Device Settings", divider=True)

    col1,col2 = sl.columns(2)

    with col1:
        selected_device = sl.selectbox("Select Device", list_devices("tty.usb"))
    with col2:
        selected_rig_key = sl.selectbox("Select Rig", options=list(available_rig_ids.keys()))
        selected_rig_id = available_rig_ids[selected_rig_key]

    sl.subheader("RCV VFO Settings",divider=True)

    col1,col2 = sl.columns(2)

    with col1:
        sel_rcv_vfo = sl.selectbox("Select RCV VFO", options=VFOS, index=0)

    with col2:
        sel_rcv_mode = sl.selectbox("Select RCV Mode", options=MODES, index=2)
    
    col1,col2 = sl.columns(2)
    
    with col1:
        sel_rcv_freq = sl.number_input(
            "RCV Center Frequency (Hz)",
            min_value=144000000,
            max_value=440000000,
            value=437800000
        )
    
    with col2:
        sel_rcv_passband = sl.number_input(
            "RCV Passband Width",
            min_value=500,
            max_value=3600,
            value=2700
        )

    sl.subheader("SND VFO Settings",divider=True)

    col1,col2 = sl.columns(2)

    with col1:
        sel_snd_vfo = vfo(sl.selectbox("Select SND VFO", options=VFOS, index=0))

    with col2:
        sel_snd_mode = mode(sl.selectbox("Select SND Mode", options=MODES, index=2))
    
    col1,col2 = sl.columns(2)
    
    with col1:
        sel_snd_freq = sl.number_input(
            "SND Center Frequency (Hz)",
            min_value=144000000,
            max_value=440000000,
            value=437800000
        )
    
    with col2:
        sel_snd_passband = sl.number_input(
            "SND Passband Width",
            min_value=500,
            max_value=3600,
            value=2700
        )

    sl.subheader("Tracking Settings", divider=True)

    selected_interval = sl.select_slider(
        "Update Interval (s)",
        options=[0.1,0.5,1,3,5,10],
        value=1
    )

Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_ERR)
rig = Hamlib.Rig(rig_model=selected_rig_id)
rig.set_conf("rig_pathname", f"/dev/{selected_device}")

if selected_device is not None:
    rig.open()

sl.title(f"Tracking {selected_sat}")

debug = f'''
    Device:\t\t{selected_device}
    Rid ID:\t\t{selected_rig_id}
    Rig Name:\t{selected_rig_key}
    Current QRG:\t{sel_rcv_freq / 1000000:.6f} MHz
    Satellite:\t{selected_sat}
    Interval:\t{selected_interval} s
    TLE date:\t{MOD_DATE.strftime("%A, %d. %B %Y %H:%M:%S")}
    VFO:\t\t{sel_rcv_vfo}
    Mode:\t\t{sel_rcv_mode}
    Passband:\t{sel_rcv_passband} Hz
    Latitude:\t{STATION_LAT}°
    Longitude:\t{STATION_LNG}°
    Elevation:\t{STATION_ELEV} m
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

        rig.set_vfo(vfo(sel_rcv_vfo))
        rig.set_mode(sel_snd_mode, sel_rcv_passband)

        rig.set_freq(vfo(sel_rcv_vfo), round(doppler_shift(sel_rcv_freq, radial_velocity)))
      
        output = f'''
            Satellite:\t{satellite.name}
            Frequency:\t{round(doppler_shift(sel_rcv_freq, radial_velocity) / 1000000,6)} MHz
            Elevation:\t{round(alt.degrees)}°
            Azimuth:\t{round(az.degrees)}°
            Distance:\t{round(distance.km)} km
        '''
        
        output_placeholder.code(output, language=None)

        # Wartezeit vor der nächsten Aktualisierung
        time.sleep(selected_interval)

def disconnect_rig():
    """Disconnect from rig and reset frequency"""
    rig.set_vfo(vfo(sel_rcv_vfo))
    rig.set_freq(vfo(sel_rcv_vfo), sel_rcv_freq)
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
