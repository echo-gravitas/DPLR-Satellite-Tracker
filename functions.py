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

def vfo(vfo):
    """"Returns Hamlib VFO reference"""
    if vfo == "VFO A":
        return Hamlib.RIG_VFO_A
    if vfo == "VFO B":
        return Hamlib.RIG_VFO_B
    if vfo == "Current VFO":
        return Hamlib.RIG_VFO_CURR
    
def mode(mode):
    """Returns Hamlib mode reference"""
    if mode == "USB":
        return Hamlib.RIG_MODE_USB
    if mode == "LSB":
        return Hamlib.RIG_MODE_LSB
    if mode == "FM":
        return Hamlib.RIG_MODE_FMN
    if mode == "CW":
        return Hamlib.RIG_MODE_CW