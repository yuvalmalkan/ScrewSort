import cv2
import numpy as np
from Constants import (ROI, PIXELS_PER_MM, MIN_SCREW_AREA_PX, MAX_SCREW_AREA_PX, 
                       MIN_LENGTH_TO_DIAMETER_RATIO, STABLE_FRAMES_REQUIRED, 
                       DIAMETER_RANGES_MM, INVERT_THRESHOLD)

def cropToRoi(frame, roi=ROI):
    if roi is None:
        return frame, (0, 0)
        
    x, y, w, h = roi
    return frame[y:y + h, x:x + w], (x, y)

def findScrewContour(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    thresh_type = cv2.THRESH_BINARY_INV if INVERT_THRESHOLD else cv2.THRESH_BINARY
    _, thresh = cv2.threshold(blurred, 0, 255, thresh_type + cv2.THRESH_OTSU)

    kernel = np.ones((7, 7), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    # Filter out contours that are too small (noise) or too large (machine background)
    valid_contours = [cnt for cnt in contours if MIN_SCREW_AREA_PX < cv2.contourArea(cnt) < MAX_SCREW_AREA_PX]

    if not valid_contours:
        return None

    # Return the largest valid contour
    return max(valid_contours, key=cv2.contourArea)

def isScrewPresent(contour, min_area=MIN_SCREW_AREA_PX):
    if contour is None:
        return False
    return cv2.contourArea(contour) > min_area

def measureScrew(contour):
    rect = cv2.minAreaRect(contour)
    width, height = rect[1]
    return max(width, height), min(width, height)

def classifyScrew(contour):
    length_px, diameter_px = measureScrew(contour)
    length_mm = length_px / PIXELS_PER_MM
    diameter_mm = diameter_px / PIXELS_PER_MM

    if diameter_px <= 0 or (length_px / diameter_px) < MIN_LENGTH_TO_DIAMETER_RATIO:
        return {"type": "ERROR", "contour": contour}

    size = "ERROR"
    for key, (low, high) in DIAMETER_RANGES_MM.items():
        if low <= diameter_mm <= high:
            size = key
            break

    return {"type": size, "contour": contour}

def detectScrew(frame, roi=ROI):
    search_frame, offset = cropToRoi(frame, roi)
    contour = findScrewContour(search_frame)

    if not isScrewPresent(contour):
        return None

    result = classifyScrew(contour)
    result["contour"] = contour + [offset[0], offset[1]]
    return result

class TypeStabilizer:
    def __init__(self, required_frames=STABLE_FRAMES_REQUIRED):
        self.required_frames = required_frames
        self.stable_type = None
        self.candidate_type = None
        self.candidate_count = 0

    def update(self, new_type):
        if new_type == self.candidate_type:
            self.candidate_count += 1
        else:
            self.candidate_type = new_type
            self.candidate_count = 1

        if self.candidate_count >= self.required_frames:
            self.stable_type = self.candidate_type

        return self.stable_type

def drawRoi(frame, roi=ROI, color=(255, 0, 0)):
    if roi:
        x, y, w, h = roi
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
    return frame

def drawScrewBox(frame, contour, color=(0, 255, 0)):
    if contour is None:
        return frame
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = np.intp(box)
    cv2.drawContours(frame, [box], 0, color, 2)
    return frame

def drawScrewType(frame, screw_type):
    if screw_type is None:
        return frame
        
    color = (0, 200, 0) if screw_type != "ERROR" else (0, 0, 255)
    cv2.putText(frame, screw_type, (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 2.5, color, 5)
    
    return frame