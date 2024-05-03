from Gestures import Gesture
import keyboard

class Controller:

    def __init__(self):
        self.gest = Gesture.NONE
        self.action_timestamp = float('-inf')

    def stop_yt_video(self):
        keyboard.press_and_release('space')
    
    def handle(self, gest: Gesture, timestamp: int):

        if(timestamp - self.action_timestamp < 40):
            return
        
        self.action_timestamp = timestamp

        match gest:

            case Gesture.CLOSED_FIST:
                self.stop_yt_video()

            case _:
                print("THIS ACTION DOESN'T EXIST")
        

            