from Gestures import Gesture
import keyboard
import pyautogui

class Controller:

    def __init__(self):
        self.gest = Gesture.NONE
        self.action_timestamp = float('-inf')

    def stop_yt_video(self):
        keyboard.press_and_release('space')
        
    def volumeup_video(self):
        keyboard.press_and_release('volumeup')
    def volumedown_video(self):
        keyboard.press_and_release('volumedown')
        
    def forward_video(self):
        keyboard.press_and_release('right')
    def backward_video(self):
        keyboard.press_and_release('left')
        
        
    def handle(self, gest: Gesture, timestamp: int):

        if(timestamp - self.action_timestamp < 40):
            return
        
        self.action_timestamp = timestamp

        match gest:

            case Gesture.CLOSED_FIST:
                self.stop_yt_video()
            case Gesture.THUMB_UP:
                self.volumeup_video()
            case Gesture.THUMB_DOWN:
                self.volumedown_video()
            case Gesture.POINTING_UP:
                self.forward_video()
            case Gesture.VICTORY:
                self.backward_video()
            case _:
                print("THIS ACTION DOESN'T EXIST")
        

            