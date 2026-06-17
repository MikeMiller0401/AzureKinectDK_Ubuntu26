from pyk4a import PyK4APlayback
import os
import numpy as np
import cv2
path = "video"
playback = PyK4APlayback(os.path.join(path, "output.mkv"))
playback.open()

i = 0

try:
    while True:
        capture = playback.get_next_capture()

        depth = capture.depth
        color = capture.color
        
        depth_path = os.path.join(path, "depth")
        if not os.path.exists(depth_path):
            os.mkdir(depth_path)
        np.save(os.path.join(depth_path, f"depth_{i:04d}.npy"), depth)
        i += 1

except EOFError:
    print("✔ Finished reading MKV")

finally:
    playback.close()