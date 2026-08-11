# Azure Kinect DK Ubuntu Tools

中文：这是一个面向 Azure Kinect DK 的 Ubuntu 开发工具仓库，覆盖设备安装、视频录制、MKV 导出、相机内参保存、IMU 数据导出，以及基于深度和 IMU 的简单后处理脚本。

English: This repository contains Ubuntu-based tools for Azure Kinect DK, including device setup, video recording, MKV export, camera intrinsic export, IMU export, and lightweight post-processing utilities for depth and IMU data.

## 1. 项目内容 / What This Repository Provides

中文：仓库主要分成两条工作流。

- 基于 pyk4a 的录制与导出流程，适合直接在 Python 中访问彩色、深度、IR、点云和 IMU 数据。
- 基于 Open3D 的录制与导出流程，适合使用 Open3D 自带的 Azure Kinect MKV 读写接口。
- 若干辅助脚本，用于导出相机参数、统计深度图数据、以及从 IMU CSV 估计简单轨迹。

English: The repository is organized around two main workflows.

- A pyk4a-based recording and export pipeline for direct Python access to color, depth, IR, point-cloud, and IMU data.
- An Open3D-based recording and export pipeline using Open3D's Azure Kinect MKV interfaces.
- Several helper scripts for camera parameter export, depth-value inspection, and simple IMU trajectory estimation.

## 2. 系统依赖 / System Dependencies

中文：在运行任何 Python 脚本之前，需要先安装 Azure Kinect Sensor SDK 与命令行工具。当前仓库的原始说明基于 Ubuntu 26.04 使用 Ubuntu 18.04 的官方 deb 包进行安装。

English: Before running any Python script, install the Azure Kinect Sensor SDK and command-line tools. The original setup in this repository uses the official Ubuntu 18.04 deb packages on Ubuntu 26.04.

### 2.1 安装 K4A SDK / Install the K4A SDK

```bash
mkdir -p azure_kinect
cd azure_kinect

wget https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.4/libk4a1.4_1.4.1_amd64.deb
wget https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.4-dev/libk4a1.4-dev_1.4.1_amd64.deb
wget https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/k/k4a-tools/k4a-tools_1.4.1_amd64.deb
wget http://ftp.de.debian.org/debian/pool/main/libs/libsoundio/libsoundio1_1.1.0-1_amd64.deb

sudo dpkg -i ./libsoundio1_1.1.0-1_amd64.deb
sudo apt install ./libk4a1.4_1.4.1_amd64.deb
sudo apt install ./libk4a1.4-dev_1.4.1_amd64.deb
sudo apt install ./k4a-tools_1.4.1_amd64.deb

wget https://raw.githubusercontent.com/microsoft/Azure-Kinect-Sensor-SDK/develop/scripts/99-k4a.rules
sudo cp 99-k4a.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

中文：如果系统包版本发生变化，请优先以 Microsoft 官方文档为准。

English: If package versions change, prefer the Microsoft official documentation over this pinned example.

### 2.2 Python 依赖 / Python Dependencies

中文：建议使用独立虚拟环境或 conda 环境。按脚本用途安装依赖。

English: Use an isolated virtual environment or conda environment. Install dependencies based on the workflow you need.

```bash
pip install numpy opencv-python tqdm pyk4a
pip install pandas scipy matplotlib
pip install open3d
```

中文：其中：

- pyk4a 路线需要 pyk4a。
- Open3D 路线需要 open3d。
- IMU 轨迹分析脚本需要 pandas、scipy、matplotlib。

English:

- The pyk4a workflow requires pyk4a.
- The Open3D workflow requires open3d.
- The IMU trajectory script requires pandas, scipy, and matplotlib.

## 3. 仓库结构 / Repository Layout

```text
config/                  Azure Kinect 录制配置 JSON / Azure Kinect recording configs
Configuration details/   参考文档 / reference notes
data/                    实验数据目录 / experiment data
output/                  导出结果目录 / exported outputs
video/                   录制得到的 MKV 与 IMU CSV / recorded MKV files and IMU CSVs

recorder_pyk4a.py        使用 pyk4a 录制 MKV 和 IMU / record MKV + IMU via pyk4a
export_pyk4a.py          导出深度、RGB、IR、点云、内参 / export depth, RGB, IR, point cloud, intrinsics
recorder_open3d.py       使用 Open3D 录制 MKV / record MKV via Open3D
export_open3d.py         使用 Open3D 导出彩色和深度 / export color and depth via Open3D
imu_trajectory.py        从 IMU CSV 估计轨迹 / estimate trajectory from IMU CSV
read depth.py            统计 depth .npy 数据分布 / inspect depth .npy statistics
test.py                  读取并保存深度相机内参示例 / minimal intrinsic export example
```

## 4. 配置文件 / Configuration Files

中文：仓库当前提供三组配置：

- config/720p_NFOV_UNBINNED.json: 720P 彩色，NFOV_UNBINNED 深度，30 FPS。
- config/720p_WFOV_UNBINNED.json: 720P 彩色，WFOV_UNBINNED 深度，15 FPS。
- config/1080p_WFOV_UNBINNED.json: 1080P 彩色，WFOV_UNBINNED 深度，15 FPS。

English: The repository currently includes three camera presets:

- config/720p_NFOV_UNBINNED.json: 720P color, NFOV_UNBINNED depth, 30 FPS.
- config/720p_WFOV_UNBINNED.json: 720P color, WFOV_UNBINNED depth, 15 FPS.
- config/1080p_WFOV_UNBINNED.json: 1080P color, WFOV_UNBINNED depth, 15 FPS.

中文：WFOV_UNBINNED 模式下设备不支持超过 15 FPS，相关脚本已经做了基本检查。

English: In WFOV_UNBINNED mode the device does not support frame rates above 15 FPS, and the scripts already guard against that combination.

## 5. 快速开始 / Quick Start

### 5.1 使用 pyk4a 录制 / Record with pyk4a

中文：编辑 recorder_pyk4a.py 中 main 部分的 video_name 和 config_name，然后运行：

English: Edit video_name and config_name in the main block of recorder_pyk4a.py, then run:

```bash
python recorder_pyk4a.py
```

中文：脚本会生成：

- video/<scene>.mkv
- video/<scene>_imu.csv

English: The script writes:

- video/<scene>.mkv
- video/<scene>_imu.csv

### 5.2 使用 pyk4a 导出 / Export with pyk4a

中文：编辑 export_pyk4a.py 中的 SCENE_NAME，然后运行：

English: Edit SCENE_NAME in export_pyk4a.py, then run:

```bash
python export_pyk4a.py
```

中文：默认输出目录为 output/<scene>_export/，通常包含：

- depth_raw/: 原始深度 .npy
- depth_vis/: 深度伪彩图 .png
- rgb_raw/: 原始彩色图 .png
- rgb_aligned/: 对齐后的彩色图 .png
- ir_raw/: 红外图 .npy
- point_cloud/: 深度点云 .npy
- intrinsic_depth.txt / intrinsic_color.txt
- distortion_depth.txt / distortion_color.txt

English: The default output directory is output/<scene>_export/, typically containing:

- depth_raw/: raw depth .npy files
- depth_vis/: pseudo-colored depth .png files
- rgb_raw/: raw color .png files
- rgb_aligned/: aligned color .png files
- ir_raw/: IR .npy files
- point_cloud/: depth point-cloud .npy files
- intrinsic_depth.txt / intrinsic_color.txt
- distortion_depth.txt / distortion_color.txt

### 5.3 使用 Open3D 录制 / Record with Open3D

中文：编辑 recorder_open3d.py 中的 video_name 与 config_name，然后运行：

English: Edit video_name and config_name in recorder_open3d.py, then run:

```bash
python recorder_open3d.py
```

中文：录制结果会保存为 video/<scene>.mkv。

English: The recording is saved as video/<scene>.mkv.

### 5.4 使用 Open3D 导出 / Export with Open3D

中文：编辑 export_open3d.py 中的 video_name，然后运行：

English: Edit video_name in export_open3d.py, then run:

```bash
python export_open3d.py
```

中文：默认输出目录为 output/<scene>/，通常包含：

- color/: 彩色图像
- depth/: 深度原始 .npy 与伪彩图 .png
- K_rgb.txt / K_depth.txt

English: The default output directory is output/<scene>/, usually containing:

- color/: color images
- depth/: raw depth .npy files and pseudo-colored depth .png files
- K_rgb.txt / K_depth.txt

## 6. 辅助脚本 / Helper Scripts

### 6.1 IMU 轨迹估计 / IMU Trajectory Estimation

中文：imu_trajectory.py 读取 IMU CSV，进行简单的陀螺积分、重力补偿和 ZUPT 静止约束，输出：

- output/imu_trajectory_est.csv
- output/imu_trajectory_est.png

English: imu_trajectory.py reads an IMU CSV file, performs simple gyro integration, gravity compensation, and a basic ZUPT heuristic, then writes:

- output/imu_trajectory_est.csv
- output/imu_trajectory_est.png

中文：运行前请先修改脚本顶部的 csv_path。

English: Update csv_path near the top of the script before running it.

```bash
python imu_trajectory.py
```

### 6.2 深度数据检查 / Depth Data Inspection

中文：read depth.py 会遍历一个场景目录下的 .npy 深度图，打印每帧和整体统计量。运行前请先修改 SCENE。

English: read depth.py scans .npy depth files in a scene folder and reports per-file plus global statistics. Update SCENE before running.

```bash
python "read depth.py"
```

### 6.3 内参导出示例 / Intrinsic Export Example

中文：test.py 展示了如何直接通过 pyk4a 获取深度相机内参并写入文本文件。

English: test.py shows a minimal example of reading the depth-camera intrinsic matrix directly from pyk4a and saving it to a text file.

```bash
python test.py
```

## 7. K4A 命令行工具 / K4A Command-Line Tools

中文：安装 SDK 后，可以先用官方工具确认设备是否工作正常。

English: After installing the SDK, use the official tools to verify the device is working.

```bash
k4aviewer
k4aviewer -HighDPI
k4arecorder -h
k4arecorder -d NFOV_UNBINNED -c 1080p -r 5 output.mkv
```

## 8. 当前仓库的使用特点 / Current Usage Pattern in This Repository

中文：当前脚本以实验脚本风格为主，而不是通用 CLI 工具，因此有几个使用特征需要注意：

- 多数脚本在 main 中写死了场景名、配置名或输入路径。
- 输出目录命名并不完全统一，例如 Open3D 导出和 pyk4a 导出的目录结构不同。
- 脚本主要面向单机、本地数据处理，没有参数解析、日志系统或批处理封装。

English: The scripts are currently written more like lab utilities than polished CLI tools, so keep these traits in mind:

- Most scripts use hard-coded scene names, config names, or input paths in the main block.
- Output naming is not fully unified; the Open3D and pyk4a export layouts differ.
- The code is intended for local experimentation, without argument parsing, logging, or batch orchestration.

## 9. 参考资料 / References

- Azure Kinect Sensor SDK: https://github.com/microsoft/Azure-Kinect-Sensor-SDK
- pyk4a: https://github.com/etiennedub/pyk4a
- Open3D Azure Kinect docs: Configuration details/open3d_azure.markdown
- Depth mode note: Configuration details/depth_mode.markdown

##  TODO LIST

中文：如果你准备继续维护这个仓库，优先建议做以下改进：

- 给 recorder/export 脚本补充命令行参数，而不是手动改源码。
- 统一 output 目录结构与命名规则。
- 增加 requirements.txt 或 environment.yml。
- 在 README 中增加示例输入、示例输出截图与常见报错说明。