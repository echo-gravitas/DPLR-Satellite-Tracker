import os

# Read connected devices
def list_devices(filter_pattern=None):
    dev_path = "/dev/"
    devices = os.listdir(dev_path)
    if filter_pattern:
        devices = [device for device in devices if filter_pattern in device]
    return devices

# Read TLE
def load_tle(file_path):
    """Load and read TLEs from file"""
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    satellite_names = [lines[i].strip() for i in range(0, len(lines), 3)]
    return satellite_names

