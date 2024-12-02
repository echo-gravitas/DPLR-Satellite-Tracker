import time
from skyfield.api import load, EarthSatellite
from skyfield.toposlib import wgs84
from datetime import datetime
import Hamlib

# Get TLE from online source

url ="https://celestrak.org/NORAD/elements/amateur.txt"
satellites = load.tle_file(url)
print(f"TLE Daten von {url} geladen.")

satellite = {sat.name: sat for sat in satellites}["DIWATA-2B"]

# My station details
station = wgs84.latlon(47.165101053547325, 8.295939429046944, elevation_m=495)

# Calculate Doppler

LIGHT_SPEED = 299792.458 # km/s

def doppler_shift(freq, rad_vel):
    return freq * (1 - (rad_vel / LIGHT_SPEED))

# Rig Setup

Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_ERR)
myrig = Hamlib.Rig(rig_model=3085)
myrig.set_conf("rig_pathname","/dev/tty.usbmodem142201")
myrig.set_conf("retry","5")
downlink_freq = 145900000
update_interval = 1

if myrig.open() != 0:
    print(f"Verbindung zu {myrig.caps.mfg_name} {myrig.caps.model_name} hergestellt.")

    try:
        while True:
            
            ts = load.timescale()
            t = ts.now()

            satellite_position = satellite.at(t)
            observer_position = station.at(t)
            relative_position = satellite_position - observer_position

            relative_velocity = relative_position.velocity.km_per_s

            radial_velocity = relative_position.position.km @ relative_velocity / relative_position.distance().km

            #print(f"Radialgeschwindigkeit von {satellite.name}: {radial_velocity:.3f} km/s")

            #print(f"Doppler: {round(doppler_shift(downlink_freq, radial_velocity))}")

            # Frequenz setzen
            if myrig.set_freq(Hamlib.RIG_VFO_CURR, round(doppler_shift(downlink_freq, radial_velocity))) != 0:
                print(f"Frequenz angepasst auf: {round(doppler_shift(downlink_freq, radial_velocity))} Hz")
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