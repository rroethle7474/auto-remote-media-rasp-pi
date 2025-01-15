import evdev
from evdev import categorize, ecodes
import subprocess
import time
import vlc
import random
import os
import sys
from pathlib import Path
import tkinter as tk
from threading import Thread
import queue

class StatusScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        
        self.status_label = tk.Label(
            self.root,
            text="Starting up...",
            font=('Arial', 48, 'bold'),
            fg='white',
            bg='black',
            wraplength=800
        )
        self.status_label.place(relx=0.5, rely=0.4, anchor='center')
        
        self.instruction_label = tk.Label(
            self.root,
            text="",
            font=('Arial', 36),
            fg='lightgreen',
            bg='black',
            wraplength=800
        )
        self.instruction_label.place(relx=0.5, rely=0.6, anchor='center')
        
        # Process GUI events periodically
        self.root.update()
        
    def update_status(self, status, instruction=""):
        try:
            self.status_label.config(text=status)
            self.instruction_label.config(text=instruction)
            self.root.update()
        except tk.TclError:
            pass  # Handle case where window was closed

    def hide(self):
        try:
            self.root.withdraw()
            self.root.update()
        except tk.TclError:
            pass

    def show(self):
        try:
            self.root.deiconify()
            self.root.update()
        except tk.TclError:
            pass

    def update(self):
        try:
            self.root.update()
        except tk.TclError:
            pass

class MediaPlayer:
    def __init__(self, video_dir):
        self.video_dir = Path(video_dir)
        
        vlc_args = [
            '--fullscreen',
            '--aout=pulse',
            '--audio-resampler=soxr',
            '--file-caching=1000',
            '--network-caching=1000'
        ]
        self.instance = vlc.Instance(' '.join(vlc_args))
        self.player = self.instance.media_player_new()
        self.player.set_fullscreen(True)
        self.player.audio_set_volume(100)
        
        self.current_video = None
        self.is_playing = False
        self.is_paused = False

    def get_random_video(self):
        try:
            video_files = [f for f in self.video_dir.glob("*")
                         if f.stem.isdigit() and 1 <= int(f.stem) <= 100]
            
            if not video_files:
                print("No valid video files found!")
                return None
                
            return random.choice(video_files)
            
        except Exception as e:
            print(f"Error selecting random video: {e}")
            return None

    def play_random_video(self):
        try:
            if self.is_playing:
                self.player.stop()
                
            video_path = self.get_random_video()
            if not video_path:
                return False
                
            media = self.instance.media_new(str(video_path))
            self.player.set_media(media)
            
            self.player.play()
            self.is_playing = True
            self.is_paused = False
            self.current_video = video_path
            
            print(f"Now playing: {video_path.name}")
            return True
            
        except Exception as e:
            print(f"Error playing video: {e}")
            return False

    def toggle_pause(self):
        if self.is_playing:
            if self.is_paused:
                print("Resuming playback...")
                self.player.play()
                self.is_paused = False
            else:
                print("Pausing playback...")
                self.player.pause()
                self.is_paused = True

    def stop_and_close(self):
        if self.is_playing:
            self.player.stop()
            self.is_playing = False
            self.is_paused = False
            self.current_video = None
        self.player.release()
        self.instance.release()

class TVController:
    def __init__(self, status_screen):
        self.status_screen = status_screen
        self.KEY_CODES = {
            'KEY_ENTER': self.handle_enter_press,
            'KEY_DOWN': self.handle_down_press
        }
        
        video_dir = "/home/rroethle/Desktop/media-player/Videos/AndyGriffith"
        self.media_player = MediaPlayer(video_dir)
        
        self.status_screen.update_status(
            "Ready to Play",
            "Press ENTER button on remote to start a show\nPress DOWN button to stop current show"
        )

    def execute_cec(self, command):
        try:
            result = subprocess.run(['echo', command, '|', 'cec-client', '-s', '-d', '1'],
                                  shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            print(f"CEC command failed: {e}")
            return None

    def check_tv_power_state(self):
        result = self.execute_cec('pow 0')
        return 'power status: on' in result.lower() if result else False

    def handle_enter_press(self):
        if self.media_player.is_playing:
            self.media_player.toggle_pause()
            self.status_screen.hide()
        else:
            self.status_screen.show()
            self.status_screen.update_status(
                "Loading your show...",
                "Please wait a moment"
            )
            
            print("Starting TV and video sequence...")
            self.turn_on_tv()
            print("Starting video playback...")
            if self.media_player.play_random_video():
                self.status_screen.hide()
            else:
                self.status_screen.update_status(
                    "Oops! Something went wrong.",
                    "Please ask for help or try again"
                )

    def handle_down_press(self):
        print("Stopping playback...")
        self.media_player.stop_and_close()
        video_dir = "/home/rroethle/Desktop/media-player/Videos/AndyGriffith"
        self.media_player = MediaPlayer(video_dir)
        
        self.status_screen.show()
        self.status_screen.update_status(
            "Ready to Play",
            "Press ENTER button on remote to start a show\nPress DOWN button to stop current show"
        )

    def turn_on_tv(self):
        print("Starting TV control sequence...")
        
        tv_was_on = self.check_tv_power_state()
        
        if not tv_was_on:
            print("TV is off, powering on...")
            self.execute_cec('on 0')
            print("Waiting for TV to fully power on...")
            time.sleep(8)
        else:
            print("TV is already on")
        
        print("Switching to HDMI 2...")
        max_retries = 3
        for attempt in range(max_retries):
            self.execute_cec('tx 4F:82:20:00')
            time.sleep(2)
            
            if attempt < max_retries - 1:
                print(f"Retry {attempt + 1} of {max_retries}...")

        print("TV setup sequence completed")

    def process_events(self, device):
        print("Starting TV controller...")
        print("Press Enter button on remote to turn on TV and play/pause video")
        print("Press Down arrow to stop current show")
        print("Press Ctrl+C to exit")
        
        try:
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_down:
                        if key_event.keycode in self.KEY_CODES:
                            self.KEY_CODES[key_event.keycode]()
                        self.status_screen.update()
                        
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.media_player.stop_and_close()

def main():
    status_screen = StatusScreen()
    status_screen.update_status(
        "Starting up...",
        "Please wait while the system initializes"
    )
    
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    flirc_device = None
    
    for device in devices:
        if 'flirc' in device.name.lower():
            flirc_device = device
            break
    
    if not flirc_device:
        status_screen.update_status(
            "Remote Control Not Found",
            "Please check the remote control connection and restart"
        )
        return
    
    print(f"Using device: {flirc_device.name}")
    
    controller = TVController(status_screen)
    controller.process_events(flirc_device)

if __name__ == "__main__":
    main()