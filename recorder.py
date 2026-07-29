import time
import os
import json
import csv
import pyk4a
from pyk4a import PyK4A, PyK4ARecord, Config, ColorResolution, DepthMode, FPS, ImageFormat, WiredSyncMode
from pyk4a.errors import K4ATimeoutException

# 从 JSON 配置文件解析出 pyk4a.Config 和 fps 整数
_FPS_MAP = {"5": FPS.FPS_5, "15": FPS.FPS_15, "30": FPS.FPS_30}
_DEPTH_MAP = {
    "NFOV_2X2BINNED": DepthMode.NFOV_2X2BINNED,
    "NFOV_UNBINNED":  DepthMode.NFOV_UNBINNED,
    "WFOV_2X2BINNED": DepthMode.WFOV_2X2BINNED,
    "WFOV_UNBINNED":  DepthMode.WFOV_UNBINNED,
}
_RES_MAP = {
    "720P":  ColorResolution.RES_720P,
    "1080P": ColorResolution.RES_1080P,
    "1440P": ColorResolution.RES_1440P,
    "1536P": ColorResolution.RES_1536P,
    "2160P": ColorResolution.RES_2160P,
    "3072P": ColorResolution.RES_3072P,
}

def init_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)

    fps_str   = config_dict.get("camera_fps", "").split('_')[-1]          # "15"
    res_str   = config_dict.get("color_resolution", "").split('_')[-1]    # "720P"
    depth_str = "_".join(config_dict.get("depth_mode", "").split('_')[3:5])  # "NFOV_UNBINNED"

    fps_int  = int(fps_str)
    fps_enum = _FPS_MAP[fps_str]
    res_enum = _RES_MAP[res_str]
    dep_enum = _DEPTH_MAP[depth_str]

    print('=' * 80)
    print(f"FPS={fps_int}  Resolution={res_str}  DepthMode={depth_str}")
    print('=' * 80)

    if fps_int > 15 and "WFOV_UNBINNED" in depth_str:
        raise RuntimeError("Camera does not support >15 FPS in WFOV_UNBINNED mode.")

    config = Config(
        color_resolution=res_enum,
        depth_mode=dep_enum,
        camera_fps=fps_enum,
        color_format=ImageFormat.COLOR_MJPG,
        synchronized_images_only=True,
        wired_sync_mode=WiredSyncMode.STANDALONE,
    )
    return config, fps_int


def record(video_name, config, fps, exposure_us=None, auto_exposure=False):
    """
    录制视频和 IMU 数据
    
    参数：
      video_name: 视频名称（不含扩展名）
      config: pyk4a.Config 对象
      fps: 帧率（整数）
      exposure_us: 曝光时间（微秒），范围 500-133330，None 表示不改变默认值
      auto_exposure: 是否启用自动曝光（True 则忽略 exposure_us）
    """
    os.makedirs("video", exist_ok=True)
    mkv_path = os.path.join("video", video_name.strip() + ".mkv")
    imu_path = os.path.join("video", video_name.strip() + "_imu.csv")

    device = PyK4A(config=config, device_id=0)
    device.start()

    # 设置曝光
    if auto_exposure:
        device.exposure_mode_auto = True
        print(f"✓ Auto exposure enabled")
    elif exposure_us is not None:
        # 曝光范围: 500-133330 微秒，步长 100
        exposure_us = max(500, min(133330, exposure_us))
        device.exposure = exposure_us
        print(f"✓ Exposure set to {exposure_us} µs ({exposure_us/1000:.1f} ms)")
    else:
        print(f"✓ Exposure: default ({device.exposure} µs)")

    recorder = PyK4ARecord(path=mkv_path, config=config, device=device)
    recorder.create()
    recorder.write_header()

    FRAME_DURATION = 1.0 / fps
    frame_count = 0
    recording_start_time = time.time()

    print('=' * 80)
    print(f"Recording → {mkv_path}")
    print(f"IMU CSV   → {imu_path}")
    print("Press Ctrl+C to stop")
    print('=' * 80)

    imu_rows = []

    try:
        while True:
            start_time = time.time()

            # 采集一帧图像并写入 mkv
            capture = device.get_capture()
            recorder.write_capture(capture)
            frame_count += 1

            # 读取当前所有可用的 IMU 样本（IMU 频率远高于相机帧率）
            while True:
                try:
                    imu = device.get_imu_sample(timeout=0)
                except K4ATimeoutException:
                    break  # 当前没有更多样本，退出内层循环
                if imu is None:
                    break
                imu_rows.append({
                    "acc_timestamp_usec": imu["acc_timestamp"],
                    "acc_x": imu["acc_sample"][0],
                    "acc_y": imu["acc_sample"][1],
                    "acc_z": imu["acc_sample"][2],
                    "gyro_timestamp_usec": imu["gyro_timestamp"],
                    "gyro_x": imu["gyro_sample"][0],
                    "gyro_y": imu["gyro_sample"][1],
                    "gyro_z": imu["gyro_sample"][2],
                    "temperature": imu["temperature"],
                })

            total_duration = time.time() - recording_start_time
            print(f"\rFrame {frame_count:05d} | {total_duration:.2f}s | IMU samples: {len(imu_rows)}", end="", flush=True)

            elapsed = time.time() - start_time
            sleep_time = FRAME_DURATION - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                print(f"\n[Warning] Frame lag: {elapsed:.4f}s")

    except KeyboardInterrupt:
        print("\nStopping...")

    recorder.flush()
    recorder.close()
    device.stop()

    # 将 IMU 数据写入 CSV
    if imu_rows:
        fieldnames = ["acc_timestamp_usec", "acc_x", "acc_y", "acc_z",
                      "gyro_timestamp_usec", "gyro_x", "gyro_y", "gyro_z", "temperature"]
        with open(imu_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(imu_rows)
        print(f"IMU saved: {len(imu_rows)} samples → {imu_path}")
    else:
        print("No IMU samples captured.")

    print(f"MKV saved: {frame_count} frames → {mkv_path}")


if __name__ == "__main__":
    video_name  = "holes_wet_30p"
    config_name = "720p_NFOV_UNBINNED"
    config_path = os.path.join("config", config_name + ".json")
    config, fps = init_config(config_path)
    
    # 曝光设置选项（在这里修改）：
    # 选项 1: 手动曝光，单位微秒
    # exposure_us = 2500   # 1 ms
    # auto_exposure = False
    
    # 选项 2: 自动曝光
    exposure_us = None
    auto_exposure = True
    
    record(video_name, config, fps, exposure_us=exposure_us, auto_exposure=auto_exposure)
    