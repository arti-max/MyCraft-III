from ursina import *
from random import choice, uniform
from ursina import Audio

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_tracks = {}
        self.current_music = None
        self.music_queue = []

    def load_sound(self, name, file_path):
        """Loads a sound file and stores it in the sounds dictionary."""
        self.sounds[name] = Audio(file_path, loop=False, autoplay=False)

    def play_sound(self, name):
        """Plays a sound by name."""
        if name in self.sounds:
            self.sounds[name].play()
        else:
            print(f"Sound '{name}' not found!")

    def load_music(self, name, file_path):
        """Loads a music track and stores it in the music_tracks dictionary."""
        self.music_tracks[name] = Audio(file_path, loop=False, autoplay=False)

    def play_random_music(self):
        """Stops currently playing music and plays a random music track."""
        if self.current_music:
            self.current_music.stop()

        if self.music_tracks:
            music_name = choice(list(self.music_tracks.keys()))
            self.current_music = self.music_tracks[music_name]
            self.current_music.play()
            print(f"Playing music: {music_name}")
            self.current_music.on_finish = self.on_music_finish

            mLen = self.current_music.length

            next_play_time = uniform(mLen+10, mLen+35)  # Random delay between 30 and 120 seconds
            invoke(self.play_random_music, delay=next_play_time)

    def on_music_finish(self):
        """Callback for when a music track finishes."""
        self.current_music = None
        print("Music finished. Waiting for manual restart...")

    def stop_music(self):
        """Stops the currently playing music track."""
        if self.current_music:
            self.current_music.stop()
            self.current_music = None

    def set_volume(self, volume):
        """Sets the volume for all sounds and music (0.0 to 1.0)."""
        Audio.volume = volume