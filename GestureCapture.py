import mediapipe as mp
import cv2
import os
from Controller import Controller
from Gestures import Gesture
from mediapipe.framework.formats import landmark_pb2

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
VisionRunningMode = mp.tasks.vision.RunningMode
solutions = mp.solutions

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
        self.recognizer = GestureRecognizer.create_from_options(self.options)
        self.prev_gest = ""
        self.curr_gest = ""
        self.crct_gest = ""
        self.show_output = show_output
        self.result = ""

    def update_guesture_and_call_controller(self, result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int):

        self.result = result

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

        while(True): 
            success, frame = self.cap.read() 
            self.frame_no += 1

            if not success:
                print("Empty Frame")
                continue

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            self.recognizer.recognize_async(mp_image, self.frame_no)

            if(self.show_output):
                annotated_image = frame
                
                if(self.result and len(self.result.hand_landmarks) > 0): # type: ignore
                    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList() # type: ignore
                    hand_landmarks_proto.landmark.extend([
                        landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in self.result.hand_landmarks[0] # type: ignore
                    ])
                    solutions.drawing_utils.draw_landmarks( # type: ignore
                        annotated_image,
                        hand_landmarks_proto,
                        solutions.hands.HAND_CONNECTIONS,  # type: ignore
                        solutions.drawing_styles.get_default_hand_landmarks_style(),  # type: ignore
                        solutions.drawing_styles.get_default_hand_connections_style()) # type: ignore
                            
                cv2.imshow('Output', annotated_image)
                if cv2.waitKey(1) & 0xFF == ord('q'): 
                    break

        self.cap.release()     
        cv2.destroyAllWindows()