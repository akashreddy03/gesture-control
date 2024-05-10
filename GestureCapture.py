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
        self.model_path = os.path.abspath("gesture_recognizer1.task")
        self.cap = cv2.VideoCapture(0)
        self.controller = Controller()
        self.timestamp = 0
        self.frame_no = 0
        self.options = GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_path=self.model_path),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.update_guesture_and_call_controller,
            num_hands=2,
        )
        self.recognizer = GestureRecognizer.create_from_options(self.options)
        self.show_output = show_output
        self.prev_gest = None
        self.curr_gest = None
        self.crct_gest = None
        self.result = None

    # Updates current gesture if valid and calls controller only if the same gesture repeats for about 3 frames (to avoid noise)
    def update_guesture_and_call_controller(
        self, result: GestureRecognizerResult, output_image: mp.Image, timestamp_ms: int
    ):

        self.result = result

        if not result.gestures or not result.gestures[0][0].category_name.upper():
            print("NO RESULT")
            return
        if result.gestures[0][0].category_name.upper() == "NONE":
            print("NONE")
            return

        self.prev_gest = self.curr_gest
        self.curr_gest = Gesture[result.gestures[0][0].category_name.upper()]

        if self.prev_gest == self.curr_gest:
            self.timestamp += 1
        else:
            self.timestamp = 0

        if self.timestamp > 3:
            self.crct_gest = self.curr_gest
            self.controller.handle(self.crct_gest, timestamp_ms)
            print(self.crct_gest.name)

    # Starts capturing frames from camera, draws handlandmarks if specified and predicts the gesture at each frame
    def start(self):

        while True:
            success, frame = self.cap.read()
            self.frame_no += 1

            if not success:
                print("Empty Frame")
                continue

            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            self.recognizer.recognize_async(mp_image, self.frame_no)

            if self.show_output:
                annotated_image = frame

                if self.result and len(self.result.hand_landmarks) > 0:
                    for i in self.result.hand_landmarks:
                        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                        hand_landmarks_proto.landmark.extend(
                            [
                                landmark_pb2.NormalizedLandmark(
                                    x=landmark.x, y=landmark.y, z=landmark.z
                                )
                                for landmark in i
                            ]
                        )
                        solutions.drawing_utils.draw_landmarks(
                            annotated_image,
                            hand_landmarks_proto,
                            solutions.hands.HAND_CONNECTIONS,
                            solutions.drawing_styles.get_default_hand_landmarks_style(),
                            solutions.drawing_styles.get_default_hand_connections_style(),
                        )

                cv2.imshow("Output", annotated_image)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

        self.cap.release()
        cv2.destroyAllWindows()
