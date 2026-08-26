__author__ = "Yuval Malkan"
from Constants import *

class Stabilizer:
    #stabilizes the detected type over multiple frames to prevent flickering
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