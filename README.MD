# Install Azure Kinect DK on Ubuntu 26.04

The offical install (https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/develop/docs/usage.md) only supports Ubuntu 18, but we can use the 18.04 deb package in Ubuntu 26.04. 

However, Ubuntu 26.04 do not support libsoundio1_1.1.0 in offical iso-mirror ( as i know, ubuntu 20 & 22 & 24 also have this problem). But we can download from other source.

1. Create download folder:
```bash
mkdir ./azure_kinect
cd azure_kinect
```

2. Download Azure Kinect DK for Ubuntu 18.04 deb package:
```bash
wget https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.4/libk4a1.4_1.4.1_amd64.deb

wget https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/libk/libk4a1.4-dev/libk4a1.4-dev_1.4.1_amd64.deb

wget https://packages.microsoft.com/ubuntu/18.04/prod/pool/main/k/k4a-tools/k4a-tools_1.4.1_amd64.deb
```
3. Download libsoundio1_1.1.0:
```bash
wget http://ftp.de.debian.org/debian/pool/main/libs/libsoundio/libsoundio1_1.1.0-1_amd64.deb
```

4. Install package:
```bash
sudo dpkg -i ./libsoundio1_1.1.0-1_amd64.deb
sudo apt install ./libk4a1.4_1.4.1_amd64.deb
sudo apt install ./libk4a1.4-dev_1.4.1_amd64.deb
sudo apt install ./k4a-tools_1.4.1_amd64.deb    
```

5. Install udev
```bash
wget https://raw.githubusercontent.com/microsoft/Azure-Kinect-Sensor-SDK/develop/scripts/99-k4a.rules
sudo cp 99-k4a.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

6. Try to open k4aviewer
```bash
k4aviewer
```

If the resolution fo your displayer is 2k or 4k, maybe the font size of k4aviewer will be too small to read. You can use ``` k4aviewer -HighDPI ``` in terminal.


7. Try to use k4arecorder to capture Video

We can use ``` k4arecorder -h``` to check help of recorder.

