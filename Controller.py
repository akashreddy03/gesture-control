from Gestures import Gesture
# from pyautogui import press

class Controller:

    def __init__(self):
        self.gest = Gesture.NONE
        self.action_timestamp = float('-inf')

    def stop_yt_video(self):
        press('space')
    
    def handle(self, gest: Gesture, timestamp: int):

        if(timestamp - self.action_timestamp < 40):
            return
        
        self.action_timestamp = timestamp

        match gest:

            case Gesture.CLOSED_FIST:
                self.stop_yt_video()

            case _:
                print("THIS ACTION DOESN'T EXIST")
        

            