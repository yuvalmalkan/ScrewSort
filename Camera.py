__author__ = "Yuval Malkan"

import cv2

class Camera:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.capture = None


    def start(self):
        self.capture = cv2.VideoCapture(self.camera_id)
        if not self.capture.isOpened():
            raise RuntimeError(f"could not open camera {self.camera_id}")


    def readFrame(self):
        if self.capture is None or not self.capture.isOpened():
            return False, None

        try:
            success, frame = self.capture.read()
            if success and frame is not None:
                 frame = cv2.flip(frame, 1)
    
            return success, frame

        except Exception as e:
            print(f"failed to grab frame: {e}")
            return False, None

    def stop(self):
        if self.capture:
            self.capture.release()