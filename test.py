from pyk4a import PyK4APlayback
import os
import numpy as np

path = "video"
mkv_path = os.path.join(path, "test004.mkv")

playback = PyK4APlayback(mkv_path)
playback.open()
K_rgb = playback.calibration.get_camera_matrix(0)
print(f"K_rgb: {K_rgb}")
K_depth = playback.calibration.get_camera_matrix(1)
print(f"K_depth: {K_depth}")

playback.close()