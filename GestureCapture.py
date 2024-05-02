import mediapipe as mp
import cv2
import os
from Controller import Controller
from Gestures import Gesture

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode

class GestureCapture:

    def __init__(self, show_output=False):
        self.model_path = os.path.abspath('gesture_recognizer.task')
        self.cap = cv2.VideoCapture(0)
        self.controller = Controller()
        self.timestamp = 0 
        self.frame_no = 0
        self.options = GestureRecognizerOptions(
            base_options = BaseOptions(model_asset_path=self.model_path),
            running_mode = VisionRunningMode.LIVE_STREAM,
            result_callback = self.update_guesture_and_call_controller
        )
        self.prev_gest = ""
        self.curr_gest = ""
        self.crct_gest = ""
        self.show_output = show_output

    def update_guesture_and_call_controller(self, result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):

        self.frame_no += 1

        if(not result.gestures):
            print("NO RESULT")
            return
        
        self.prev_gest = self.curr_gest
        self.curr_gest = Gesture[result.gestures[0][0].category_name.upper()]
        
        if(self.prev_gest == self.curr_gest):
            self.timestamp += 1
        else:
            self.timestamp = 0

        if(self.timestamp > 4):
            self.crct_gest = self.curr_gest
            self.controller.handle(self.crct_gest, timestamp_ms)
            print(self.crct_gest.name)
    
    def start(self):

        with GestureRecognizer.create_from_options(self.options) as recognizer:
        
            while(self.cap.isOpened()): 
                
                success, frame = self.cap.read() 

                if not success:
                    print("Empty Frame")
                    continue

                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                recognizer.recognize_async(mp_image, self.frame_no)

                if cv2.waitKey(1) & 0xFF == ord('q'): 
                    break

            self.cap.release()     
            cv2.destroyAllWindows() 


