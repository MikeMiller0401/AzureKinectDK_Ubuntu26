"""
Export aligned depth and RGB from Azure Kinect DK MKV file.
导出 Azure Kinect 回放中的对齐深度与原始彩色帧。 

English:
This script reads {MKV_PATH} and exports data from each valid capture to output/{OUTPUT_DIR}/:
- depth_raw/: aligned raw depth frames (uint16 .npy)
- depth_transformed/: pseudo-color depth visualizations (.png)
- rgb_raw/: raw color images (.png)

中文：
该脚本会读取 {MKV_PATH}，并将每个有效 capture 的数据保存到 output/{OUTPUT_DIR}/ 下：
- depth_raw/: 对齐后的原始深度（uint16 .npy）
- depth_transformed/: 伪彩可视化深度图（.png）
- rgb_raw/: 原始彩色图像（.png）


"""

#TODO: Add export of RGB Intrinsic.


import os
import sys
import cv2
import numpy as np
from pyk4a import PyK4APlayback
SCENE_NAME = "dry_pyk4a"
MKV_PATH = os.path.join("video", f"{SCENE_NAME}.mkv")
OUTPUT_DIR = os.path.join("output", f"{SCENE_NAME}_export")
DEPTH_RAW_OUT_DIR = os.path.join(OUTPUT_DIR, "depth_raw")
DEPTH_VIS_OUT_DIR = os.path.join(OUTPUT_DIR, "depth_transformed")
RGB_OUT_DIR = os.path.join(OUTPUT_DIR, "rgb_raw")
os.makedirs(DEPTH_RAW_OUT_DIR, exist_ok=True)
os.makedirs(DEPTH_VIS_OUT_DIR, exist_ok=True)
os.makedirs(RGB_OUT_DIR, exist_ok=True)

def depth_to_colormap(depth: np.ndarray) -> np.ndarray:
    """Convert uint16 depth to a visible pseudo-color image."""
    valid = depth > 0  # 
    if not np.any(valid):
        return np.zeros((depth.shape[0], depth.shape[1], 3), dtype=np.uint8)

    values = depth[valid].astype(np.float32)
    lo = np.percentile(values, 2)
    hi = np.percentile(values, 98)
    if hi <= lo:
        hi = lo + 1.0


    scaled = ((depth.astype(np.float32) - lo) * 255.0 / (hi - lo)).clip(0, 255)
    scaled[~valid] = 0
    scaled_u8 = scaled.astype(np.uint8)
    return cv2.applyColorMap(scaled_u8, cv2.COLORMAP_TURBO)


def normalize_color_frame(color_raw: np.ndarray) -> np.ndarray | None:
    """Normalize color payload into a standard HxWx3 BGR image."""
    if color_raw is None:
        return None

    # Common in MKV playback: encoded color bytes stored as (N, 1) or (1, N).
    if color_raw.dtype == np.uint8 and (
        color_raw.ndim == 1
        or (color_raw.ndim == 2 and (color_raw.shape[0] == 1 or color_raw.shape[1] == 1))
    ):
        encoded = color_raw.reshape(-1)
        decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        if decoded is not None:
            return decoded

    if color_raw.ndim == 3 and color_raw.shape[2] == 4:
        return cv2.cvtColor(color_raw, cv2.COLOR_BGRA2BGR)

    if color_raw.ndim == 3 and color_raw.shape[2] == 3:
        return color_raw

    if color_raw.ndim == 2:
        # If this is already a single-channel image, keep it savable as 3-channel BGR.
        return cv2.cvtColor(color_raw, cv2.COLOR_GRAY2BGR)

    return None


if not os.path.exists(MKV_PATH):
    print(f"MKV not found: {MKV_PATH}")
    sys.exit(1)

playback = PyK4APlayback(MKV_PATH)
playback.open()

frame_idx = 0
saved_idx = 0
try:
    while True:
        try:
            capture = playback.get_next_capture()
        except EOFError:
            print("Reached end of MKV file.")
            break

        depth_aligned = capture.transformed_depth
        color_raw = capture.color
        if depth_aligned is None or color_raw is None:
            frame_idx += 1
            continue

        vis_aligned = depth_to_colormap(depth_aligned)
        rgb_to_save = normalize_color_frame(color_raw)
        if rgb_to_save is None:
            print(f"Skip frame {frame_idx}: unsupported color shape {color_raw.shape}")
            frame_idx += 1
            continue
        
        depthraw_out_path = os.path.join(DEPTH_RAW_OUT_DIR, f"{saved_idx:06d}.npy")
        depthvis_out_path = os.path.join(DEPTH_VIS_OUT_DIR, f"{saved_idx:06d}.png")
        rgb_out_path = os.path.join(RGB_OUT_DIR, f"{saved_idx:06d}.png")
        
        np.save(depthraw_out_path, depth_aligned)
        cv2.imwrite(depthvis_out_path, vis_aligned)
        cv2.imwrite(rgb_out_path, rgb_to_save)
        saved_idx += 1

        frame_idx += 1
finally:
    playback.close()

print(f"Processed {frame_idx} captures.")
print(f"Saved {saved_idx} raw depth npy files to: {DEPTH_RAW_OUT_DIR}")
print(f"Saved {saved_idx} transformed depth images to: {DEPTH_VIS_OUT_DIR}")
print(f"Saved {saved_idx} raw RGB images to: {RGB_OUT_DIR}")