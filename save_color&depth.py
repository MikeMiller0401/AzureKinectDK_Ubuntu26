import open3d as o3d
import numpy as np
import cv2
import os
from tqdm import tqdm
from pyk4a import PyK4APlayback

def save_color(capture, color_path):
    color = np.asarray(capture.color)
    color = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)
    cv2.imwrite(f"{color_path}/{i:06d}.png", color)


def save_depth(capture, depth_path):
    depth = np.asarray(capture.depth)
    # 1. 先保存原始深度数据（这个数据本身是稳定的，单位是毫米 mm）
    np.save(os.path.join(depth_path, f"{i:06d}.npy"), depth)

    # 2. 设定固定的可视化范围（例如：500mm 到 4000mm，根据你的拍摄场景调整）
    min_distance = 400
    max_distance = 4000

    # 3. 裁剪数据并将其固定映射到 0-255
    # 将超出范围的值截断
    depth_clipped = np.clip(depth, min_distance, max_distance)
    # 线性映射到 0-255: (val - min) / (max - min) * 255
    depth_vis = ((depth_clipped - min_distance) / (max_distance - min_distance) * 255).astype(np.uint8)

    # 4. 如果你想让无效像素（0mm）显示为黑色，可以加这一步：
    depth_vis[depth == 0] = 0 

    # 5. 生成伪彩色并保存
    depth_heatmap = cv2.applyColorMap(depth_vis, cv2.COLORMAP_JET)
    cv2.imwrite(f"{depth_path}/{i:06d}.png", depth_heatmap)

def save_camera(video_path, save_path):
    playback = PyK4APlayback(video_path)
    playback.open()

    K_rgb = playback.calibration.get_camera_matrix(0)
    K_depth = playback.calibration.get_camera_matrix(1)
    
    np.savetxt(os.path.join(save_path, "K_rgb.txt"), K_rgb, fmt="%.8f")
    np.savetxt(os.path.join(save_path, "K_depth.txt"), K_depth, fmt="%.8f")

    playback.close()

    print("Saved K_rgb.txt and K_depth.txt")
  
if __name__ == "__main__":
    # config = o3d.io.read_azure_kinect_mkv_metadata("/home/tcy/PycharmProjects/AzureKinectDK_Ubuntu26/video/test003.mkv")
    # print(config["device_metadata"]["serial_number"])

    reader = o3d.io.AzureKinectMKVReader()
    # metadate = reader.get_metadata()
    video_name = "tian-cave5"
    video_path = os.path.join("video", video_name + ".mkv")
    output_path = os.path.join("output", video_name)
    success = reader.open(video_path)
    print("open:", success)

    if not success:
        raise RuntimeError("Failed to open mkv file")

    color_path = os.path.join(output_path, "color")
    depth_path = os.path.join(output_path,"depth")
    os.makedirs(color_path, exist_ok=True)
    os.makedirs(depth_path, exist_ok=True)

    pbar = tqdm(desc="Decoding MKV frames", unit="frame")

    i = 0
    while not reader.is_eof():
        rgbd = reader.next_frame()
        if rgbd is None:
            continue

        if reader.is_eof():
            break
        save_color(rgbd, color_path)
        save_depth(rgbd, depth_path)

        i += 1
        pbar.update(1)   # ✅ 更新进度条

    pbar.close()
    reader.close()
    save_camera(video_path, output_path)
    print("Done:", i, "frames")