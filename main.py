__author__ = "Yuval Malkan"

import cv2
from Camera import Camera
from DetectionTools import *
import Stabilizer
from Constants import CAPTURE_WIDTH_PX, CAPTURE_HEIGHT_PX

def main():
    camera = Camera(0)
    stabilizer = Stabilizer.Stabilizer()

    try:
        camera.start()

        camera.capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAPTURE_WIDTH_PX)
        camera.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAPTURE_HEIGHT_PX)

        while True:
            success, frame = camera.readFrame()
            if not success or frame is None:
                print("Failed to read frame")
                break

            result = detectScrew(frame)
            raw_type = result["type"] if result is not None else None
            stable_type = stabilizer.update(raw_type)

            frame = drawRoi(frame)

            if result is not None:
                frame = drawScrewBox(frame, result["contour"])
                
                # Extract dimensions if they were added to the result dictionary
                # This allows real-time visual debugging of the head and body measurements
                head_px = result.get("head_px", 0)
                body_px = result.get("body_px", 0)
                
                if head_px > 0 and body_px > 0:
                    # Display the measurements directly on the video feed
                    debug_text = f"Head: {head_px}px | Body: {body_px}px"
                    cv2.putText(frame, debug_text, (40, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

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