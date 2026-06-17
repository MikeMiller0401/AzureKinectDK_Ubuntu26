import open3d as o3d
import numpy as np
import cv2
import os
from tqdm import tqdm

reader = o3d.io.AzureKinectMKVReader()

video_name = "test002"
video_path = os.path.join("video/" + video_name)
output_path = os.path.join("output/" + video_name)

success = reader.open(video_path + ".mkv")
print("open:", success)

if not success:
    raise RuntimeError("Failed to open mkv file")

color_path = os.path.join(output_path + "/color")
depth_path = os.path.join(output_path + "/depth")
os.makedirs(color_path, exist_ok=True)
os.makedirs(depth_path, exist_ok=True)

# =========================
# 关键：不知道总帧数 → 先用未知进度条
# =========================
pbar = tqdm(desc="Decoding MKV frames", unit="frame")

i = 0
while not reader.is_eof():
    rgbd = reader.next_frame()
    if rgbd is None:
        continue

    if reader.is_eof():
        break

    # RGB
    color = np.asarray(rgbd.color)
    color = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)
    cv2.imwrite(f"{color_path}/{i:06d}.png", color)

    # DEPTH
    depth = np.asarray(rgbd.depth)
    np.save(os.path.join(depth_path, f"{i:06d}.npy"), depth)

    depth_vis = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX)
    depth_vis = depth_vis.astype(np.uint8)
    cv2.imwrite(f"{depth_path}/{i:06d}.png", depth_vis)

    i += 1
    pbar.update(1)   # ✅ 更新进度条

pbar.close()
reader.close()

print("Done:", i, "frames")