from Gestures import Gesture
from pynput.keyboard import Key, Controller as PynputController
import numpy as np
import math
import subprocess
import platform

# Variables used for on Windows platform
volume = None
minVol, maxVol = None, None

# If the platform is Windows then import PyCaw
if platform.system() == "Windows":
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    minVol, maxVol = volRange[0], volRange[1]

# Create instance of PynputController
keyboard = PynputController()


class Controller:

    def __init__(self):
        self.gest = Gesture.NONE
        self.action_timestamp = float("-inf")
        self.distance_capture_timestamp = float("-inf")
        self.distance_capture_mode = False
        self.window_size = 5
        self.window = [0] * self.window_size
        self.window_idx = 0

    def stop_yt_video(self):
        keyboard.press(Key.space)
        keyboard.release(Key.space)

    def forward_video(self):
        keyboard.press(Key.right)
        keyboard.release(Key.right)

    def backward_video(self):
        keyboard.press(Key.left)
        keyboard.release(Key.left)

    # Sets the system volume to given volume percentage
    def set_volume(self, volper):
        if platform.system() == "Windows":
            vol = np.interp(volper, [0, 100], [minVol, maxVol])
            volume.SetMasterVolumeLevel(vol, None)
        elif platform.system() == "Linux":
            subprocess.call(["pactl", "set-sink-volume", "0", str(volper) + "%"])

    # Calculates the distance given the index and thumb landmarks
    def calculate_distance(self, index_landmark, thumb_landmark, w: int, h: int):
        x1, y1 = index_landmark.x * w, index_landmark.y * h
        x2, y2 = thumb_landmark.x * w, thumb_landmark.y * h

        return math.hypot(x2 - x1, y2 - y1)

    # Calculates the moving average with specified window size to reduce the effect of noise
    def calculate_moving_average(self, value):

        self.window[self.window_idx] = value
        self.window_idx += 1
        self.window_idx %= self.window_size

        sum = 0
        for i in self.window:
            sum += i
        avg = sum / self.window_size

        return int(avg)

    # This function handles the process when distance capture mode is ON
    def handle_distance_capture(self, landmarks, gest, w: int, h: int, timestamp: int):

        if gest == "THUMB_UP":
            self.distance_capture_mode = False
            return

        index_landmark = landmarks[4]
        thumb_landmark = landmarks[8]

        length = self.calculate_distance(index_landmark, thumb_landmark, w, h)
        volPer = np.interp(length, [50, 220], [0, 100])
        volPerAvg = self.calculate_moving_average(volPer)
        print(volPerAvg)

        if timestamp - self.distance_capture_timestamp > 5:
            print("SETTING VOLUME TO " + str(volPerAvg))
            self.set_volume(volPerAvg)
            self.distance_capture_timestamp = timestamp

    # This function handles the general logic whenever the gesture is updated
    def handle(self, gest: Gesture, timestamp: int):

        if timestamp - self.action_timestamp < 20:
            return

        match gest:

            case Gesture.CLOSED_FIST:
                self.stop_yt_video()
            case Gesture.THUMB_UP:
                self.distance_capture_mode = False
            case Gesture.POINTING_UP:
                self.forward_video()
            case Gesture.VICTORY:
                self.backward_video()
            case Gesture.OPEN_PALM:
                self.distance_capture_mode = True

        self.action_timestamp = timestamp
