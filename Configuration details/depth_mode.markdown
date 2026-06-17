# DepthMode
Depth sensor capture modes.

See the hardware specification for additional details on the field of view, and supported frame rates for each mode. 

请参阅硬件规格以获取有关各模式视野范围和支持帧率的更多详细信息。

NFOV and WFOV denote Narrow and Wide Field Of View configurations. Binned modes reduce the captured camera resolution by combining adjacent sensor pixels into a bin.

NFOV 和 WFOV 分别表示窄视野和宽视野配置。合并模式通过将相邻的传感器像素组合成一个区块，从而降低相机捕获的分辨率

1. Off
 
Depth sensor will be turned off with this setting.

2. NFOV_2x2Binned

Depth and Passive IR are captured at 320x288.

3. NFOV_Unbinned

Depth and Passive IR are captured at 640x576.

4. WFOV_2x2Binned
   
Depth and Passive IR are captured at 512x512.

5. WFOV_Unbinned
    
Depth and Passive IR are captured at 1024x1024.

6. PassiveIR

Passive IR only is captured at 1024x1024.
