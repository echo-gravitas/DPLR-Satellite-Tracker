# DPLR Sat Tracker

DPLR Sat Tracker is a Python-based project for tracking satellites and managing amateur radio communication. The application is built to automate frequency adjustments to account for the Doppler effect and provides a user-friendly interface for configuring tracking settings, radio devices, and satellite details.

## Features

- **Real-time Satellite Tracking**: Leverages TLE (Two-Line Element) data to track satellites in real-time.
- **Doppler Effect Correction**: Automatically adjusts transmit and receive frequencies to compensate for the Doppler shift.
- **Device Integration**: Supports popular amateur radio rigs like the Icom IC-705 and IC-7300 using Hamlib.
- **Interactive UI**: Provides a Streamlit-powered GUI for easy interaction and configuration.
- **Dynamic TLE Updates**: Fetches updated TLE data from CelesTrak if the local TLE file is outdated.
- **Customizable Settings**: Includes adjustable parameters for passband width, modes, and tracking intervals.

## Getting Started

### Prerequisites

- Python 3.8+
- Streamlit
- Hamlib
- Requests
- Skyfield

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/echo-gravitas/Sat-Track.git
   cd Sat-Track
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run main.py
   ```

## Usage

1. Configure your station location (latitude, longitude, and elevation) in the sidebar.
2. Select your device and rig from the available options.
3. Set receive (RCV) and send (SND) VFO settings.
4. Start tracking a satellite from the list, and the app will display real-time tracking information.

## File Structure

- `main.py`: Entry point of the application with Streamlit integration.
- `functions.py`: Helper functions for Doppler shift calculation, TLE loading, and device management.
- `settings.py`: Contains default configuration settings such as frequency ranges and URLs.
- `tle.txt`: Stores the TLE data for satellite tracking.

## Configuration

Modify `settings.py` to customize the application:

- `DEFAULT_LAT`, `DEFAULT_LNG`, `DEFAULT_ALT`: Default location settings.
- `MIN_FREQ`, `MAX_FREQ`: Frequency range for tracking.
- `AVAILABLE_RIG_IDS`: Supported rigs and their IDs.
- `TLE_URL`: URL to fetch TLE data.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.

## Acknowledgments

- [CelesTrak](https://celestrak.org/) for TLE data.
- [Hamlib](https://hamlib.github.io/) for radio control libraries.
- [Streamlit](https://streamlit.io/) for the interactive web application framework.
- [Skyfield](https://rhodesmill.org/skyfield/) for accurate astronomical computations.
