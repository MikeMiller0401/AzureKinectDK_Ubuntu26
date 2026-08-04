import os
import numpy as np

from pyk4a import PyK4A, Config, ColorResolution, DepthMode
from pyk4a.calibration import CalibrationType

k4a = PyK4A(
    Config(
        color_resolution=ColorResolution.RES_720P,
        depth_mode=DepthMode.NFOV_UNBINNED,
    )
)

k4a.open()

dist_depth = k4a.calibration.get_distortion_coefficients(
    CalibrationType.DEPTH
)

print(dist_depth)

try:
    K_depth = k4a.calibration.get_camera_matrix(
        CalibrationType.DEPTH
    )

    os.makedirs(
        "data/AzureKinect/tunnel01/intrinsic",
        exist_ok=True,
    )

    np.savetxt(
        "data/AzureKinect/tunnel01/intrinsic/intrinsic_depth.txt",
        K_depth,
        fmt="%.9f",
    )

    print(K_depth)

finally:
    k4a.close()