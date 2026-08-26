# ---- camera setup ----
CAPTURE_WIDTH_PX = 1280
CAPTURE_HEIGHT_PX = 720

# Updated based on M3 screw logs
PIXELS_PER_MM = 12.0

# ---- region of interest (ROI) ----
ROI = (440, 160, 400, 400)

# ---- detection tuning ----
MIN_SCREW_AREA_PX = 500
MAX_SCREW_AREA_PX = 18000  # Filters out large background machine parts

INVERT_THRESHOLD = True

# Updated to 2.5 to filter out round reflections and non-screw objects
MIN_LENGTH_TO_DIAMETER_RATIO = 2.5

STABLE_FRAMES_REQUIRED = 10

# ---- screw size classification ----
DIAMETER_RANGES_MM = {
    "M1": (0.5, 1.5),
    "M2": (1.5, 2.5),
    "M3": (2.5, 3.5),
    "M4": (3.5, 4.5),
    "M5": (4.5, 5.5),
    "M6": (5.5, 7.0), # Added a bit of safety margin for M6
}