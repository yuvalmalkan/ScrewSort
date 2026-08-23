import cv2

class Camera:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.capture = None

