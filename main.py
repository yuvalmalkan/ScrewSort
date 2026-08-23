import cv2
import numpy as np  
import serial

from Camera import Camera


def main():

    camera = Camera(1)
    
    try:

        camera.start()

        while True:
            success, frame = camera.readFrame()
            if not success or frame is None:
                print("failed to read frame")
                break

            cv2.imshow('Live Camera Feed', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Exiting...")
                break
                
    except RuntimeError as e:
        print(e)
        
    finally:
        camera.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

