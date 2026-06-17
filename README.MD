# Azure Kinect DK on Ubuntu 26.04

## Installation

The offical [installation](https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/develop/docs/usage.md) only supports Ubuntu 18.04, but you can use the 18.04 deb package in Ubuntu 26.04. 

However, Ubuntu 26.04 do not support libsoundio1_1.1.0 from offical iso-mirror (as I know, Ubuntu 20 & 22 & 24 also have this problem). But we can download this package from other source.

### 1. Create download folder:
```bash
mkdir ./azure_kinect
cd azure_kinect
```

### 2. Download Azure Kinect DK for Ubuntu 18.04 deb package:
```bash
wget https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.4/libk4a1.4_1.4.1_amd64.deb

wget https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.4-dev/libk4a1.4-dev_1.4.1_amd64.deb

wget https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/k/k4a-tools/k4a-tools_1.4.1_amd64.deb
```
### 3. Download libsoundio1_1.1.0:
```bash
wget http://ftp.de.debian.org/debian/pool/main/libs/libsoundio/libsoundio1_1.1.0-1_amd64.deb
```

### 4. Install package:
```bash
sudo dpkg -i ./libsoundio1_1.1.0-1_amd64.deb
sudo apt install ./libk4a1.4_1.4.1_amd64.deb
sudo apt install ./libk4a1.4-dev_1.4.1_amd64.deb
sudo apt install ./k4a-tools_1.4.1_amd64.deb    
```

### 5. Install udev
```bash
wget https://raw.githubusercontent.com/microsoft/Azure-Kinect-Sensor-SDK/develop/scripts/99-k4a.rules
sudo cp 99-k4a.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Configuration and usage
### 1. k4aviewer
```bash
k4aviewer
```

If the resolution fo your displayer is 2k or 4k, maybe the font size of k4aviewer will be too small to read. Please use:

```bash
k4aviewer -HighDPI
``` 

### 2. k4arecorder in termial
Check help document of k4arecorder:
```bash
k4arecorder -h
```
Depth mode can be found in this [link](./Configuration details/depth_mode.markdown)
Capture video using command line:
```bash
k4arecorder -d NFOV_UNBINNED -c 1080p -r 5 output.mkv
```

