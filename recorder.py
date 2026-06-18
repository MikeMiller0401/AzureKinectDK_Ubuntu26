import open3d as o3d
import time
import numpy as np
import os

video_name = "test003"
video_save_path = os.path.join("video")
# TODO: need fix path bug!!!
config_path = os.path.join(video_save_path, video_name + ".json")
config = o3d.io.AzureKinectSensorConfig()
o3d.io.write_azure_kinect_sensor_config("azure_kinect_config.json", config)

# 可选：修改分辨率 / 模式
# config.color_resolution = o3d.io.AzureKinectSensorConfig.ColorResolution.RES_1080P
# config.depth_mode = o3d.io.AzureKinectSensorConfig.DepthMode.NFOV_UNBINNED

# =========================
# 2. 创建 recorder
# =========================
recorder = o3d.io.AzureKinectRecorder(config, 0)

# =========================
# 3. 初始化相机
# =========================
recorder.init_sensor()


# =========================
# 4. 开始录制文件
# =========================
recorder.open_record(os.path.join(video_name, ".mkv"))

print("Start recording... Press Ctrl+C to stop")

try:
    while True:
        # 关键：每一帧调用一次
        rgbd = recorder.record_frame(
            enable_record=True,
            enable_align_depth_to_color=True
        )

        # 可选：显示帧率控制
        time.sleep(0.01)

except KeyboardInterrupt:
    print("Stopping recording...")

# =========================
# 5. 关闭
# =========================
recorder.close_record()

print("Saved to output.mkv")