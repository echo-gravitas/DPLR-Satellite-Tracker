import os
import time
import requests
from skyfield.api import load, Topos
import Hamlib

# Lade TLEs von Celestrak


TLE_url = "https://celestrak.org/NORAD/elements/amateur.txt"

response = requests.get(TLE_url)
file_name = "tle.txt"

if response.status_code == 200:
    with open(file_name, "wb") as file:
        file.write(response.content)
    print(f"TLEs von {TLE_url} geladen & gespeichert.")
else:
    print(f"TLEs konnten nicht von {TLE_url} geladen werden.")

satellites = load.tle_file(file_name)

satellite = {sat.name: sat for sat in satellites}["ISS (ZARYA)"]

# My station details
station = Topos(latitude_degrees=47.165101053547325, longitude_degrees=8.295939429046944, elevation_m=495)

def doppler_shift(freq, rad_vel):
    return freq * (1 - (rad_vel / 299792.458))

# Rig Setup
Hamlib.rig_set_debug(Hamlib.RIG_DEBUG_ERR)
myrig = Hamlib.Rig(rig_model=3085)
myrig.set_conf("rig_pathname","/dev/tty.usbmodem142201")
myrig.set_conf("retry","5")

update_interval = 1


if myrig.open() != 0:

    # Feststellen, dass die Verbindung funktioniert
    print(f"Verbindung zu {myrig.caps.mfg_name} {myrig.caps.model_name} hergestellt.\n")

    #Abfragen der aktuellen Frequenz
    current_vfo_freq = myrig.get_freq(Hamlib.RIG_VFO_A)

    try:
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

            if myrig.set_freq(Hamlib.RIG_VFO_CURR, round(doppler_shift(current_vfo_freq, radial_velocity))) != 0:
                os.system("clear")
                print(f"Satellite:\t{satellite.name}")
                print(f"Frequency:\t{round(doppler_shift(current_vfo_freq, radial_velocity) / 1000000,6)} MHz")
                print(f"Elevation:\t{round(alt.degrees)}°")
                print(f"Azimut:\t\t{round(az.degrees)}°")
                print(f"Distance:\t{round(distance.km)} km")
                print("")
            else:
                print(f"Error: {Hamlib.rigerror(myrig.error_status)}")
                
            # Wartezeit vor der nächsten Aktualisierung
            time.sleep(update_interval)

    except KeyboardInterrupt:
        if myrig.set_freq(Hamlib.RIG_VFO_CURR, current_vfo_freq) != 0:
            print(f"Frequenz wurde auf {round(current_vfo_freq)} Hz zurückgesetzt.")
        else:
            print(f"Error: {Hamlib.rigerror(myrig.error_status)}")
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