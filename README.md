# DPLR Satellite Tracker

DPLR Satellite Tracker is a Python-based tool designed for tracking amateur radio satellites with automatic Doppler effect corrections. It leverages modern libraries and provides an intuitive interface for radio enthusiasts to enhance satellite communication workflows.

## Overview

This application simplifies satellite tracking and frequency management by:

- Automatically adjusting frequencies to compensate for Doppler shifts.
- Tracking amateur satellites using up-to-date TLE (Two-Line Element) data.
- Integrating seamlessly with Hamlib-supported radio devices.
- Providing a user-friendly interface via Streamlit.

## Key Features

1. **Doppler Shift Calculation**

   - Dynamically adjusts frequencies in real-time based on satellite movement.

2. **Satellite Tracking**

   - Supports TLE-based satellite tracking and updates the satellite list automatically if the local file is outdated.

3. **Radio Device Integration**

   - Compatible with multiple devices through Hamlib.
   - Configurable options for VFO, modes, and frequencies.

4. **Streamlit Interface**
   - Easy-to-navigate sidebar for selecting satellites, configuring radios, and controlling tracking sessions.

## System Requirements

- Python 3.8 or later
- Hamlib library installed on your system
- Internet connection for downloading TLE files

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/dplr-satellite-tracker.git
   cd dplr-satellite-tracker
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Hamlib is installed:

   - On Debian/Ubuntu:
     ```bash
     sudo apt-get install libhamlib-utils
     ```
   - On macOS:
     ```bash
     brew install hamlib
     ```

4. Run the application:
   ```bash
   streamlit run main.py
   ```

## Configuration

### Station Location

Update the `station` variable in `main.py` with your location coordinates:

```python
station = Topos(
    latitude_degrees=47.165101053547325,
    longitude_degrees=8.295939429046944,
    elevation_m=495
)
```

### TLE File Management

The application downloads and caches TLE data in `tle.txt`. If the file is older than 2 hours, it is automatically updated from [CelesTrak](https://celestrak.org/).

### Supported Devices

Ensure your Hamlib-compatible device is connected and listed under `/dev/`. The application includes pre-configured support for common Icom radios:

- IC-705
- IC-7300
- IC-7760

## How to Use

1. Start the application with `streamlit run main.py`.
2. Use the sidebar to:
   - Select a satellite from the loaded TLE list.
   - Choose your connected radio device, VFO, and operating mode.
3. Begin tracking by clicking **Start Tracking**. The application will:
   - Adjust frequencies for Doppler shift in real-time.
   - Display satellite position, frequency, and tracking information.
4. Stop tracking or set split mode using the sidebar controls.

## Technical Details

### Doppler Shift Calculation

The Doppler shift is calculated using the formula:

```python
def doppler_shift(freq, rad_vel):
    return freq * (1 - (rad_vel / 299792.458))
```

Where:

- `freq` is the original frequency in Hz.
- `rad_vel` is the radial velocity in km/s.
- `299792.458` is the speed of light in km/s.

### TLE Handling

The application loads satellite data using the Skyfield library, which reads TLE files to calculate satellite positions:

```python
satellites = load.tle_file(TLE_FILENAME)
```

### Hamlib Integration

Hamlib is used to communicate with the connected radio device:

```python
rig = Hamlib.Rig(rig_model=selected_rig_id)
rig.open()
rig.set_freq(vfo, adjusted_frequency)
rig.close()
```

## Contribution

We welcome contributions! To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with detailed descriptions of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Skyfield** for satellite calculations.
- **Hamlib** for radio device integration.
- **Streamlit** for the interactive interface.

---

Enjoy seamless satellite tracking and efficient communication with DPLR Satellite Tracker!
