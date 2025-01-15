import evdev
from evdev import categorize, ecodes
import subprocess
import time
import vlc
import random
import os
import sys
from pathlib import Path

class MediaPlayer:
    def __init__(self, video_dir):
        """Initialize the VLC media player instance"""
        self.video_dir = Path(video_dir)
        
        # Debug: Print directory information
        print(f"Checking video directory: {self.video_dir}")
        print(f"Directory exists: {self.video_dir.exists()}")
        if self.video_dir.exists():
            print("Files in directory:")
            for file in self.video_dir.glob("*"):
                print(f"  - {file.name}")
        
        # Create a VLC instance with verbose output
        self.instance = vlc.Instance('--verbose=2 --fullscreen')
        # Create a MediaPlayer instance
        self.player = self.instance.media_player_new()
        
        # Set fullscreen
        self.player.set_fullscreen(True)
        
        # Current video tracking
        self.current_video = None
        self.is_playing = False

    def get_random_video(self):
        """Get a random video file from the specified directory"""
        try:
            # List all files and filter for numbers 1-100
            video_files = [f for f in self.video_dir.glob("*")
                         if f.stem.isdigit() and 1 <= int(f.stem) <= 100]
            
            print(f"Found {len(video_files)} valid video files")  # Debug
            
            if not video_files:
                print("No valid video files found!")
                return None
                
            chosen_video = random.choice(video_files)
            print(f"Selected video: {chosen_video}")  # Debug
            return chosen_video
            
        except Exception as e:
            print(f"Error selecting random video: {e}")
            return None

    def play_random_video(self):
        """Play a random video file"""
        try:
            # Stop any current playback
            if self.is_playing:
                self.player.stop()
                
            video_path = self.get_random_video()
            if not video_path:
                return False
                
            # Create a new Media instance
            print(f"Attempting to play: {video_path}")  # Debug
            media = self.instance.media_new(str(video_path))
            
            # Set the media to the player
            self.player.set_media(media)
            
            # Play the media
            result = self.player.play()
            print(f"Play result: {result}")  # Debug
            
            self.is_playing = True
            self.current_video = video_path
            
            print(f"Now playing: {video_path.name}")
            
            # Add a small delay to let VLC initialize
            time.sleep(1)
            
            # Check player state
            state = self.player.get_state()
            print(f"Player state after play: {state}")  # Debug
            
            return True
            
        except Exception as e:
            print(f"Error playing video: {e}")
            print(f"Error type: {type(e)}")  # Debug
            print(f"Error details: {str(e)}")  # Debug
            return False

    def stop(self):
        """Stop the current video"""
        if self.is_playing:
            self.player.stop()
            self.is_playing = False
            self.current_video = None


class TVController:
    def __init__(self):
        self.KEY_CODES = {
            'KEY_ENTER': self.handle_enter_press,
        }
        
        # Initialize the media player
        video_dir = "/home/rroethle/Desktop/media-player/Videos/AndyGriffith"
        print(f"Initializing MediaPlayer with directory: {video_dir}")  # Debug
        self.media_player = MediaPlayer(video_dir)
        
    def execute_cec(self, command):
        """Execute a CEC command and return the output"""
        try:
            result = subprocess.run(['echo', command, '|', 'cec-client', '-s', '-d', '1'],
                                  shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            print(f"CEC command failed: {e}")
            return None

    def check_tv_power_state(self):
        """Check if TV is powered on"""
        result = self.execute_cec('pow 0')
        return 'power status: on' in result.lower() if result else False

    def handle_enter_press(self):
        """Handle enter button press - turn on TV and play random video"""
        print("Starting TV and video sequence...")
        
        # First handle TV power and input
        self.turn_on_tv()
        
        # Then play a random video
        print("Starting video playback...")
        success = self.media_player.play_random_video()
        print(f"Video playback success: {success}")  # Debug


    def turn_on_tv(self):
        """Handle TV power on and input switching with proper delays"""
        print("Starting TV control sequence...")
        
        # Check current TV state
        tv_was_on = self.check_tv_power_state()
        
        if not tv_was_on:
            print("TV is off, powering on...")
            self.execute_cec('on 0')
            print("Waiting for TV to fully power on...")
            time.sleep(8)  # Increased delay to ensure TV is ready
        else:
            print("TV is already on")
        
        # Switch to HDMI 2 with retry logic
        print("Switching to HDMI 2...")
        max_retries = 3
        for attempt in range(max_retries):
            self.execute_cec('tx 4F:82:20:00')  # HDMI 2 command
            time.sleep(2)  # Wait between attempts
            
            if attempt < max_retries - 1:
                print(f"Retry {attempt + 1} of {max_retries}...")

        print("TV setup sequence completed")

    def process_events(self, device):
        """Process input events from the FLIRC device"""
        print("Starting TV controller...")
        print("Press Enter button on remote to turn on TV and play a random Andy Griffith episode")
        print("Press Ctrl+C to exit")
        
        try:
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_down:
                        if key_event.keycode in self.KEY_CODES:
                            self.KEY_CODES[key_event.keycode]()
                        
        except KeyboardInterrupt:
            print("\nShutting down...")
            # Clean up media player
            self.media_player.stop()

def main():
    # Find FLIRC device
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    flirc_device = None
    
    for device in devices:
        if 'flirc' in device.name.lower():
            flirc_device = device
            break
    
    if not flirc_device:
        print("FLIRC device not found!")
        return
    
    print(f"Using device: {flirc_device.name}")
    
    controller = TVController()
    controller.process_events(flirc_device)

if __name__ == "__main__":
    main()