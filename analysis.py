import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

def get_valid_idxs(arr, min_value, max_value):
    arr = np.asarray(arr)
    valid_idxs = (arr >= min_value) & (arr <= max_value)
    return valid_idxs

@dataclass
class TargetAudioDetector:
    target: float = 100
    tolerance: float = 5
    min_valid_counts: int = 15

    def __post_init__(self):
        self.min_value = self.target - self.tolerance
        self.max_value = self.target + self.tolerance

    def analyze_data(self, arr):
        valid_idxs = get_valid_idxs(arr, self.min_value, self.max_value)
        valid_counts = np.count_nonzero(valid_idxs)
        valid_bool = valid_counts >= self.min_valid_counts
        return valid_idxs, valid_counts, valid_bool

    
@dataclass
class ZigZagTracker:
    zz_low: float = 25
    zz_high: float = 75
    tolerance: float = 5
    n_jumps_to_stop: int = 4
    min_valid_counts: int = 15

    def __post_init__(self):
        self.zz_counts = 0
        self._targets = [self.zz_low, self.zz_high]
        low_detector = TargetAudioDetector(
            target=self.zz_low,
            tolerance=self.tolerance,
            min_valid_counts=self.min_valid_counts,
        )
        high_detector = TargetAudioDetector(
            target=self.zz_high,
            tolerance=self.tolerance,
            min_valid_counts=self.min_valid_counts,
        )
        self._detectors = [low_detector, high_detector]

    def analyze_data(self, arr):
        idx = int(self.zz_counts%2)
        detector = self._detectors[idx]
        valid_idxs, valid_count, valid_bool = detector.analyze_data(arr)
        if valid_bool:
            self.zz_counts += 1
        return valid_bool

    def is_zz_triggered(self):
        return self.zz_counts >= self.n_jumps_to_stop
            
    def reset(self):
        self.zz_counts = 0