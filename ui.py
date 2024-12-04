import streamlit as sl

def load_tle(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()
    satellite_names = [lines[i].strip() for i in range(0, len(lines), 3)]
    return satellite_names

tle_file = "tle.txt"
satellite_names = load_tle(tle_file)

sl.title("Sat Tracker")
sl.header("Input")

satellites = ["ISS","AO-7","PO-101"]

selected_sat = sl.selectbox("Wähle einen Satelliten:", satellite_names)

freq = sl.number_input("Gib die Startfrequenz (Hz) ein:", min_value=144000000,max_value=440000000, value=437800000)

start_tracking = sl.button("Tracking starten")

if start_tracking:
    sl.write(f"Tracking für {selected_sat} auf Frequenz {freq} Hz gestartet")