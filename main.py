import time
from skyfield.api import load, EarthSatellite
from skyfield.toposlib import wgs84
from datetime import datetime
import Hamlib

# Get TLE from online source

url ="https://celestrak.org/NORAD/elements/amateur.txt"
satellites = load.tle_file(url)
print(f"TLE Daten von {url} geladen.")

satellite = {sat.name: sat for sat in satellites}["FUNCUBE-1 (AO-73)"]

# My station details
station = wgs84.latlon(47.165101053547325, 8.295939429046944, elevation_m=495)

# Calculate Doppler

LIGHT_SPEED = 299792.458 # km/s

def doppler_shift(sent_freq, relative_velocity):
    return sent_freq * (LIGHT_SPEED / (LIGHT_SPEED - relative_velocity))

# Rig Setup

Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_ERR)
myrig = Hamlib.Rig(rig_model=3085)
myrig.set_conf("rig_pathname","/dev/tty.usbmodem142201")
myrig.set_conf("retry","5")

if myrig.open() != 0:
    print("Verbindung offen")

    uplink_freq = 145960000
    update_interval = 1

    print(satellite)

    try:
        while True:
            # Aktuelle Zeit
            ts = load.timescale()
            now = ts.now()

            # Satellitenposition und Geschwindigkeit relativ zur Bodenstation
            relative_position = (satellite - station).at(now)
            velocity = relative_position.velocity.km_per_s  # Geschwindigkeit in km/s
            relative_velocity = velocity[2]  # Sichtliniengeschwindigkeit

            # Doppler-Korrektur
            corrected_freq = round(doppler_shift(uplink_freq, relative_velocity))

            # Frequenz setzen
            if myrig.set_freq(Hamlib.RIG_VFO_CURR, corrected_freq) != 0:
                print(f"Frequenz angepasst auf: {corrected_freq} Hz")
            else:
                print(f"Error: {Hamlib.rigerror(myrig.error_status)}")

            # Wartezeit vor der nächsten Aktualisierung
            time.sleep(update_interval)

    except KeyboardInterrupt:
        print("Frequenznachführung beendet.")

else:
    print("Verbindung fehlgeschlagen")
    exit(1)
    

# myrig.set_vfo(Hamlib.RIG_VFO_B)
# myrig.set_freq(Hamlib.RIG_VFO_B, 134625000)
# myrig.set_vfo(Hamlib.RIG_VFO_A)
# #myrig.set_freq(Hamlib.RIG_VFO_A, 437800000)
# myrig.set_mode(Hamlib.RIG_MODE_CW)
# myrig.set_ptt(Hamlib.RIG_VFO_A, Hamlib.RIG_PTT_ON)
# myrig.send_morse(Hamlib.RIG_VFO_A, "73 de HB3XCO")
# myrig.set_ptt(Hamlib.RIG_VFO_A, Hamlib.RIG_PTT_OFF)
# myrig.set_powerstat(Hamlib.RIG_POWER_ON)

myrig.close()