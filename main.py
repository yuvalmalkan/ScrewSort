__author__ = "Yuval Malkan"

import cv2
import serial
from Camera import Camera
from DetectionTools import *
import Stablizer
from Constants import CAPTURE_WIDTH_PX, CAPTURE_HEIGHT_PX

def main():
    camera = Camera(1)
    stabilizer = Stabilizer()

    try:
        camera.start()

        camera.capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH_PX)
        camera.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT_PX)

        while True:
            success, frame = camera.readFrame()
            if not success or frame is None:
                print("failed to read frame")
                break

            result = detectScrew(frame)
            raw_type = result["type"] if result is not None else None
            stable_type = stabilizer.update(raw_type)

            frame = drawRoi(frame)

            if result is not None:
                frame = drawScrewBox(frame, result["contour"])
                
            frame = drawScrewType(frame, stable_type)

            cv2.imshow('screw sort', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except RuntimeError as e:
        print(e)
    finally:
        camera.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()