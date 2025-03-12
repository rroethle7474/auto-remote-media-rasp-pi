# Raspberry Pi Auto Remote Media Player

A simple media player application designed for Raspberry Pi that allows playing media files using a remote control. This project is specifically designed to work on Raspberry Pi (Linux) and uses VLC for media playback and evdev for remote control input handling.

## Overview

This application allows users to:
- Play random media files from a specified directory
- Control playback using a FLIRC-compatible remote control
- Automatically control TV power and input selection via CEC
- Display status messages on screen

## Requirements

- Raspberry Pi (tested on Raspberry Pi 4)
- Raspbian/Raspberry Pi OS
- Python 3.7+
- VLC media player
- FLIRC USB receiver and compatible remote control
- TV with CEC support (for automatic TV control)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/auto-remote-media-raspberry-pi.git
cd auto-remote-media-raspberry-pi
```

### 2. Set Up Virtual Environment

```bash
# Create a virtual environment
python3 -m venv rasp-pi

# Activate the virtual environment
source rasp-pi/bin/activate
```

### 3. Install Dependencies

```bash
# Install required Python packages
pip install python-vlc evdev

# Install system dependencies
sudo apt-get update
sudo apt-get install vlc cec-utils
```

### 4. Configure Media Directory

Edit the `app.py` file to set your media directory path:

```python
# Find this line in app.py and update it with your media directory path
video_dir = "/path/to/your/media/files"
```

### 5. Configure FLIRC (if needed)

If you haven't already configured your FLIRC device:

1. Install FLIRC software on a computer (can be downloaded from [flirc.tv](https://flirc.tv/downloads))
2. Connect your FLIRC device to the computer
3. Configure the buttons according to your remote control
4. Once configured, connect the FLIRC to your Raspberry Pi

## Running the Application

### Manual Start

```bash
# Make sure you're in the project directory
cd auto-remote-media-raspberry-pi

# Activate the virtual environment
source rasp-pi/bin/activate

# Run the application
python app.py
```

### Automatic Start as a Service

1. Edit the `media-player.service` file to update paths if necessary
2. Edit the `start_media_player.sh` script to update paths if necessary
3. Install the service:

```bash
# Copy the service file to systemd
sudo cp media-player.service /etc/systemd/system/

# Make the start script executable
chmod +x start_media_player.sh

# Enable and start the service
sudo systemctl enable media-player.service
sudo systemctl start media-player.service
```

## Usage

Once the application is running:

- Press the **ENTER** button on your remote to start playing a random video
- Press the **ENTER** button again to pause/resume playback
- Press the **DOWN** button to stop the current video and return to the ready screen

## Troubleshooting

### Remote Control Not Detected

1. Check if the FLIRC device is properly connected
2. Run `ls /dev/input/by-id/` to see if the FLIRC device is listed
3. Make sure the FLIRC device is properly configured

### VLC Playback Issues

1. Make sure VLC is installed: `sudo apt-get install vlc`
2. Check if the media files are in a supported format
3. Verify the media directory path in the code

### CEC Control Issues

1. Make sure cec-utils is installed: `sudo apt-get install cec-utils`
2. Check if your TV supports CEC
3. Run `cec-client -l` to list CEC devices
4. You may need to adjust the CEC commands in the code for your specific TV

## Development Notes

This project is specifically designed for Linux (Raspberry Pi) and uses Linux-specific libraries:

- **evdev**: For handling input from the FLIRC device
- **cec-client**: For controlling the TV via HDMI-CEC
- **python-vlc**: For media playback

Attempting to run or develop this application on Windows or macOS will require significant modifications.

### File Structure Notes

- **app.py**: The main application file that should be used for running the media player
- **app2.py**: This is a duplicate of app.py and can be safely removed
- **test_input.py**: A debugging/testing script with verbose output for troubleshooting input devices and media playback. It contains the same core functionality as app.py but with additional debug logging and without the GUI interface. Useful when diagnosing issues with remote control input or media playback.
- **start_media_player.sh**: Shell script for launching the application
- **media-player.service**: Systemd service file for automatic startup

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
