__author__ = "Yuval Malkan"

import cv2
import numpy as np
from Constants import *
from Stabilizer import Stabilizer



def cropToRoi(frame, roi=ROI):
    if roi is None:
        return frame, (0, 0)
        
    x, y, w, h = roi

    return frame[y:y + h, x:x + w], (x, y)




def findScrewContour(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)


    if INVERT_THRESHOLD:
        thresh_type = cv2.THRESH_BINARY_INV

    else:
        thresh_type = cv2.THRESH_BINARY


    _, thresh = cv2.threshold(blurred, 100, 255, thresh_type)

    
    kernel = np.ones((7, 7), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel)


    contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    valid_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > MIN_SCREW_AREA_PX and area < MAX_SCREW_AREA_PX:
            valid_contours.append(contour)

    if not valid_contours:
        return None

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
    # Extract separate measurements for the head and the threaded body
    length_px, head_diameter_px, body_diameter_px = measureHeadAndBody(contour)
    area = cv2.contourArea(contour)

    if body_diameter_px <= 0:
        return {"type": "ERROR", "contour": contour, "head_px": 0, "body_px": 0}
        
    # Calculate ratio and final millimeter diameter based on the body (thread) only
    ratio = length_px / body_diameter_px
    diameter_mm = body_diameter_px / PIXELS_PER_MM

    # Logs for classification and calibration
    print("\n--- Screw Detection Log ---")
    print(f"Area (px): {area:.1f}")
    print(f"Length (px): {length_px:.2f} | Head (px): {head_diameter_px:.2f} | Body (px): {body_diameter_px:.2f}")
    print(f"Current Calculated Thread Diameter (mm): {diameter_mm:.2f}")
    print(f"Ratio (Length/Body): {ratio:.2f}")

    if ratio < MIN_LENGTH_TO_DIAMETER_RATIO:
        print("Status: FAILED (Ratio too small)")
        return {"type": "ERROR", "contour": contour, "head_px": head_diameter_px, "body_px": body_diameter_px}

    for size_name, size_range in DIAMETER_RANGES_MM.items():
        min_diameter = size_range[0]
        max_diameter = size_range[1]
        
        if diameter_mm >= min_diameter and diameter_mm <= max_diameter:
            print(f"Status: SUCCESS ({size_name})")
            return {"type": size_name, "contour": contour, "head_px": head_diameter_px, "body_px": body_diameter_px}

    print("Status: FAILED (No matching size category)")
    return {"type": "ERROR", "contour": contour, "head_px": head_diameter_px, "body_px": body_diameter_px}

def detectScrew(frame, roi=ROI):
    search_frame, offset = cropToRoi(frame, roi)
    contour = findScrewContour(search_frame)

    if not isScrewPresent(contour):
        return None

    result = classifyScrew(contour)
    result["contour"] = contour + [offset[0], offset[1]]

    return result



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

    if screw_type == "ERROR":
        text_color = (0, 0, 255)

    else:
        text_color = (0, 200, 0)

    cv2.putText(frame, screw_type, (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 2.5, text_color, 5)

    return frame


def measureHeadAndBody(contour):
    x, y, w, h = cv2.boundingRect(contour)
    length_px = w
    
    # Create a black mask matching the bounding box dimensions
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Shift the contour to the mask's origin and draw it in white
    shifted_contour = contour - [x, y]
    cv2.drawContours(mask, [shifted_contour], 0, 255, -1)
    
    widths = []
    
    # Scan thickness along the X-axis
    for col in range(w):
        column_pixels = np.where(mask[:, col] > 0)[0]
        if len(column_pixels) > 0:
            width = column_pixels[-1] - column_pixels[0]
            widths.append(width)
                
    if not widths:
        return 0, 0, 0
        
    # The head is the widest part
    head_diameter_px = max(widths)
    
    # Sort widths and take the median of the narrower 70% to isolate the thread
    widths.sort()
    thread_widths = widths[:int(len(widths) * 0.7)]
    
    if not thread_widths:
        body_diameter_px = head_diameter_px
    else:
        body_diameter_px = np.median(thread_widths)
        
    return length_px, head_diameter_px, body_diameter_px