import streamlit as sl
from functions import list_devices, load_tle
from variables import available_radios

satellite_names     = load_tle("tle.txt")
devices             = list_devices("tty.usb")

sl.sidebar.title("Sat Tracker")

sl.sidebar.caption("Track satellites frequencies with ease. Doppler effect correction? Sat Tracker will do it for you.")

selected_sat = sl.sidebar.selectbox("Select Satellite", satellite_names)

sl.sidebar.subheader("Radio Config",divider=True)

selscted_device = sl.sidebar.selectbox("Select device", devices)

rig = sl.sidebar.selectbox("Select Rig", available_radios)

freq = sl.sidebar.number_input("Center Frequency (Hz)", min_value=144000000,max_value=440000000, value=437800000)

sl.sidebar.subheader("Settings", divider=True)

sl.sidebar.select_slider("Update interval (s)", options=[0.1,0.5,1,3,5,10], value=1)

start_tracking = sl.sidebar.button("Start Tracking", use_container_width=True, type="primary")

stop_tracking = sl.sidebar.button("Stop Tracking", use_container_width=True, type="secondary")

if start_tracking:
    False

sl.title(f"Tracking {selected_sat}")

sl.write("Hallo blabla")