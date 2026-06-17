from pyk4a import PyK4APlayback
import os
import numpy as np
import cv2

path = "video"
mkv_path = os.path.join(path, "output.mkv")

playback = PyK4APlayback(mkv_path)
playback.open()
K_rgb = playback.calibration.get_camera_matrix(0)
print(f"K_rgb: {K_rgb}")
K_depth = playback.calibration.get_camera_matrix(1)
print(f"K_depth: {K_depth}")

rgb_dir = os.path.join(path, "rgb")
depth_dir = os.path.join(path, "depth")
os.makedirs(rgb_dir, exist_ok=True)
os.makedirs(depth_dir, exist_ok=True)

i = 0

try:
    while True:
        capture = playback.get_next_capture()
        color = capture.color    
        if color is not None:
            print(color.shape)
            color = cv2.cvtColor(color, cv2.COLOR_BGRA2BGR)
            cv2.imwrite(os.path.join(rgb_dir, f"{i:04d}.png"), color)
            
        depth = capture.depth  # uint16 mm
        if depth is not None:
            np.save(os.path.join(depth_dir, f"{i:04d}.npy"), depth)

            # 可选：可视化depth
            depth_vis = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
            depth_vis = depth_vis.astype(np.uint8)
            cv2.imwrite(os.path.join(depth_dir, f"{i:04d}.png"), depth_vis)

        i += 1

except EOFError:
    print("✔ Finished reading MKV")

finally:
    playback.close()