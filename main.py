'''DPLR Sat Tracking'''
import os
from datetime import datetime, timedelta
import time
import requests
import Hamlib
from skyfield.api import load, Topos
import streamlit as sl
from functions import (
    doppler_shift,
    load_local_tle,
    list_devices,
    get_vfo,
    get_mode,
    disconnect_rig,
    set_snd_settings,
    set_split,
    set_rcv_settings,
    )
from settings import (
    APP_NAME,
    DEFAULT_LAT,
    DEFAULT_LNG,
    DEFAULT_ALT,
    VFOS,
    MODES,
    MIN_FREQ,
    MAX_FREQ,
    DEFAULT_PASSBAND,
    MIN_PASSBAND,
    MAX_PASSBAND,
    AVAILABLE_RIG_IDS,
    STATION_LAT,
    STATION_LNG,
    STATION_ELEV,
    TLE_FILENAME,
    DEFAULT_RCV_FREQ,
    DEFAULT_SND_FREQ,
    TLE_URL
    )

sl.set_page_config(
    page_title = APP_NAME,
    page_icon = "📡",
    layout = "centered",
    initial_sidebar_state = "auto"
)

# Check TLE file and load from remote if neccessary

if os.path.exists(TLE_FILENAME):
    SATELLITE_NAMES = load_local_tle(TLE_FILENAME)
    modification_time = os.path.getmtime(TLE_FILENAME)
    MOD_DATE = datetime.fromtimestamp(modification_time)
    now = datetime.now()
    file_age = now - MOD_DATE

    if file_age > timedelta(hours=2):
        response = requests.get(TLE_URL, timeout=30)

        if response.status_code == 200:
            with open(TLE_FILENAME, "wb") as file:
                file.write(response.content)

else:
    response = requests.get(TLE_URL)
    if response.status_code == 200:
        with open(TLE_FILENAME, "wb") as file:
            file.write(response.content)
        SATELLITE_NAMES = load_local_tle(TLE_FILENAME)

satellites = load.tle_file(TLE_FILENAME)

os_available_devices = list_devices("tty.usb")

# Sidebar Content

with sl.sidebar:

    expander = sl.expander

    sl.title(APP_NAME)
    
    sl.caption("Track satellites frequencies with ease. Doppler effect correction? Sat Tracker will do it for you.")

    selected_sat = sl.selectbox("Select Satellite", SATELLITE_NAMES)

    satellite = {sat.name: sat for sat in satellites}[selected_sat]

    sl.subheader("Station Config",divider=True)
    
    col1,col2,col3 = sl.columns(3)

    with col1:
        
        STATION_LNG = sl.number_input("QTH Lng", value=DEFAULT_LNG, format="%0.6f", step=None)

    with col2: 
        
        STATION_LAT = sl.number_input("QTH Lat", value=DEFAULT_LAT, format="%0.6f", step=None)

    with col3:

        STATION_ELEV = sl.number_input("Elevation (m)", value=DEFAULT_ALT)

    sl.subheader("Device Settings", divider=True)

    col1,col2 = sl.columns(2)

    with col1:
        
        selected_device = sl.selectbox("Select Device", list_devices("tty.usb"))
    
    with col2:
        
        selected_rig_key = sl.selectbox("Select Rig", options=list(AVAILABLE_RIG_IDS.keys()))
       
        selected_rig_id = AVAILABLE_RIG_IDS[selected_rig_key]

    with expander("Set RCV VFO Settings"):

        col1,col2 = sl.columns(2)

        with col1:
            
            sel_rcv_vfo = get_vfo(sl.selectbox("Select RCV VFO", options=VFOS, index=0))

        with col2:
            
            sel_rcv_mode = get_mode(sl.selectbox("Select RCV Mode", options=MODES, index=3))

        col1,col2 = sl.columns(2)

        with col1:

            sel_rcv_freq = sl.number_input(
                "RCV Center Frequency (Hz)",
                min_value = MIN_FREQ,
                max_value = MAX_FREQ,
                value=DEFAULT_RCV_FREQ
            )

        with col2:

            sel_rcv_passband = sl.number_input(
                "RCV Passband Width",
                min_value = MIN_PASSBAND,
                max_value = MAX_PASSBAND,
                value=DEFAULT_PASSBAND
            )

        set_rcv_settings_btn = sl.button(
            "Set RCV Settings",
            use_container_width=True,
            type="primary",
            disabled=selected_device is None
        )

    with expander("Set SND VFO Settings"):
        
        col1,col2 = sl.columns(2)

        with col1:
            sel_snd_vfo = get_vfo(sl.selectbox("Select SND VFO", options=VFOS, index=1))

        with col2:
            sel_snd_mode = get_mode(sl.selectbox("Select SND Mode", options=MODES, index=3))
        
        col1,col2 = sl.columns(2)
        
        with col1:
            sel_snd_freq = sl.number_input(
                "SND Center Frequency (Hz)",
                min_value = MIN_FREQ,
                max_value = MAX_FREQ,
                value = DEFAULT_SND_FREQ
            )
        
        with col2:
            sel_snd_passband = sl.number_input(
                "SND Passband Width",
                min_value=MIN_PASSBAND,
                max_value=MAX_PASSBAND,
                value=DEFAULT_PASSBAND
            )

        set_snd_settings_btn = sl.button(
            "Set SND Settings",
            use_container_width=True,
            type="primary",
            disabled=selected_device is None
            )
        
    with expander("Tracking Settings"):

        selected_interval = sl.select_slider(
            "Update Interval (s)",
            options=[0.1,0.5,1,3,5,10],
            value=1
        )

        listen_only = sl.toggle("RCV only")

sl.title(f"Tracking {selected_sat}")

debug = f'''
    Device:\t\t{selected_device}
    Rid ID:\t\t{selected_rig_id}
    Rig Name:\t{selected_rig_key}
    Current QRG:\t{sel_rcv_freq / 1000000:.6f} MHz
    Satellite:\t{selected_sat}
    Interval:\t{selected_interval} s
    TLE date:\t{MOD_DATE.strftime("%A, %d. %B %Y %H:%M:%S")}
    Passband:\t{sel_rcv_passband} Hz
    Latitude:\t{STATION_LAT}°
    Longitude:\t{STATION_LNG}°
    Elevation:\t{STATION_ELEV} m
'''
sl.code(debug, language=None)

Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_ERR)
rig = Hamlib.Rig(rig_model=selected_rig_id)
rig.set_conf("rig_pathname", f"/dev/{selected_device}")

STATION = Topos(
    latitude_degrees=STATION_LAT,
    longitude_degrees=STATION_LNG,
    elevation_m=STATION_ELEV
    )

def sat_tracking():
    """Tracks Satellite and calculates freq shift for doppler effect"""

    rig.open()

    output_placeholder = sl.empty()

    while True:

        # Aktuelle Zeit berechnen
        ts = load.timescale()
        t = ts.now()

        # Ausrechnen ob Sat schon über
        # dem Horizont ist oder nicht
        difference = satellite - STATION
        topocentric = difference.at(t)
        alt, az, distance = topocentric.altaz()

        # Relative Geschwindigkeit und
        # Radialgeschwindigkeit ausrechnen
        satellite_position = satellite.at(t)
        observer_position = STATION.at(t)
        relative_position = satellite_position - observer_position
        relative_velocity = relative_position.velocity.km_per_s
        radial_velocity = relative_position.position.km @ relative_velocity / relative_position.distance().km

        rig.set_mode(sel_rcv_mode, sel_rcv_passband)
        rig.set_freq(sel_rcv_vfo, round(doppler_shift(sel_rcv_freq, radial_velocity)))

        if not listen_only:
            rig.set_mode(sel_snd_mode, sel_snd_passband)
            rig.set_freq(sel_snd_vfo, round(doppler_shift(sel_snd_freq, radial_velocity)))
      
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

if set_rcv_settings_btn:
    set_rcv_settings(
        rig,
        sel_rcv_vfo,
        sel_rcv_mode,
        sel_rcv_freq,
        sel_rcv_passband
    )

if set_snd_settings_btn:
    set_snd_settings(
        rig,
        sel_snd_vfo,
        sel_snd_mode,
        sel_snd_freq,
        sel_snd_passband
    )



if sl.sidebar.button("Start Tracking", use_container_width=True, type="primary", disabled=selected_device is None):
    sat_tracking()

if sl.sidebar.button("Stop Tracking", use_container_width=True, type="secondary", disabled=selected_device is None):
    disconnect_rig(rig, sel_rcv_vfo, sel_rcv_freq)

if sl.sidebar.button("Set Split Mode", use_container_width=True, type="secondary",disabled=selected_device is None):
    set_split(rig, sel_snd_freq)
