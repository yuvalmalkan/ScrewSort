__author__ = "Yuval Malkan"

CAPTURE_WIDTH_PX = 1280
CAPTURE_HEIGHT_PX = 720


#region of interest
ROI = (440, 160, 400, 400)


MIN_SCREW_AREA_PX = 500
MAX_SCREW_AREA_PX = 18000

INVERT_THRESHOLD = True

#filter out round reflections
MIN_LENGTH_TO_DIAMETER_RATIO = 2.5

STABLE_FRAMES_REQUIRED = 10


PIXELS_PER_MM = 5.8

#screw size classification
DIAMETER_RANGES_MM = {
    "M1": (0.5, 1.5),
    "M2": (1.5, 2.5),
    "M3": (2.5, 3.5),
    "M4": (3.5, 4.5),
    "M5": (4.5, 5.5),
    "M6": (5.5, 6.5),
}