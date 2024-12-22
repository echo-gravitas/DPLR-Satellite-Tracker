'''Functions'''
import os
import Hamlib

def doppler_shift(freq, rad_vel):
    """Calculates doppler frquency shift"""
    return freq * (1 - (rad_vel / 299792.458))

def load_local_tle(file_path):
    """Load and read TLEs from local file"""
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    names = [lines[i].strip() for i in range(0, len(lines), 3)]
    return names

def list_devices(filter_pattern=None):
    """Read connected devices from OS, filter and list them"""
    dev_path = "/dev/"
    devices = os.listdir(dev_path)
    if filter_pattern:
        devices = [device for device in devices if filter_pattern in device]
    return devices

def get_vfo(vfo_name):
    """Returns Hamlib VFO reference based on name."""
    vfo_mapping = {
        "VFO A": Hamlib.RIG_VFO_A,
        "VFO B": Hamlib.RIG_VFO_B,
        "Current VFO": Hamlib.RIG_VFO_CURR
    }
    return vfo_mapping.get(vfo_name, Hamlib.RIG_VFO_CURR)

def get_mode(mode_name):
    """Returns Hamlib mode reference based on name."""
    mode_mapping = {
        "USB": Hamlib.RIG_MODE_USB,
        "LSB": Hamlib.RIG_MODE_LSB,
        "FM": Hamlib.RIG_MODE_FMN,
        "CW": Hamlib.RIG_MODE_CW
    }
    return mode_mapping.get(mode_name, Hamlib.RIG_MODE_USB)