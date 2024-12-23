from datetime import datetime
from skyfield.api import Topos

APP_NAME = "DPLR Sat Tracker"
VFOS= ["VFO A", "VFO B", "Current"]
MODES = ["AM","USB","LSB","FM","CW"]
MIN_FREQ = 144000000
MAX_FREQ = 440000000
DEFAULT_RCV_FREQ = 437800000
DEFAULT_SND_FREQ = 145990000
MIN_PASSBAND = 500
MAX_PASSBAND = 3600
DEFAULT_PASSBAND = 2700
AVAILABLE_RIG_IDS = {"Icom IC-705":3085,"Icom IC-7300":3073,"Icom IC-7760":3092}
STATION_LAT = None
STATION_LNG = None
STATION_ELEV = None
TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP=amateur&FORMAT=tle"
TLE_FILENAME = "tle.txt"
SATELLITE_NAMES = None
MOD_DATE = datetime.now()
STATION = Topos(
    latitude_degrees=STATION_LAT or 47.165161521226466,
    longitude_degrees=STATION_LNG or 8.295906232497849,
    elevation_m=STATION_ELEV or 495
    )