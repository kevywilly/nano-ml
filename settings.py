from pydantic import BaseSettings
from typing import List
from src.training.config import TrainingConfig
from src.visual.camera_model import CameraModel
from numpy import array

from src.training.config import (
    Obstacle2dConfig, 
    Obstacle3dConfig, 
    Navigate2dConfig, 
    Obstacle3dV2Config, 
    Obstacle5dConfig,
    MecanumConfig
)

class AppSettings(BaseSettings):

    reverse_motors: bool = True

    m1_alpha: float = 1.0
    m2_alpha: float = 1.0
    m3_alpha: float = 1.0
    m4_alpha: float = 1.0

    robot_drive_speed: float = 0.55
    robot_turn_speed: float = 0.45

    default_model: TrainingConfig = Obstacle3dV2Config
    retrain_model: bool = True
    default_epochs: int = 30
    default_retrain_epochs: int = 10
    led_pins: List[int] = [200,38]

    calibration_folder: str = "/ml_data/calibration"
    calibration_model_folder: str = "/ml_data/calibration/models"
    calibration_camera_model_file: str = "/ml_data/calibration/models/camera_model.xml"
    calibration_rectification_model_file: str = "/ml_data/calibration/models/rectification_model.xml"
    calibration_3d_map_file: str = "/ml_data/calibration/models/3dmap.xml"

    calibration_image_output_folder = f"{calibration_folder}/images/output"
    calibration_stereo_right_folder = f"{calibration_folder}/images/stereo/right"
    calibration_stereo_left_folder = f"{calibration_folder}/images/stereo/left"

    cam_width: int = 960
    cam_height: int = 540
    cam_fps: int = 30
    cam_capture_width: int = 1280
    cam_capture_height:int = 720

    camera_model: CameraModel = CameraModel.parse_obj({'M1': array([[872.37278861,   0.        , 448.23723854],
       [  0.        , 872.90500479, 275.56641959],
       [  0.        ,   0.        ,   1.        ]]), 'M2': array([[860.81147084,   0.        , 434.4724981 ],
       [  0.        , 861.28050352, 309.49877691],
       [  0.        ,   0.        ,   1.        ]]), 'dist1': array([[-0.11631838,  0.80460205,  0.00432939,  0.00235266, -1.70611155]]), 'dist2': array([[-1.79460570e-01,  2.08975471e+00,  1.07847284e-03,
        -5.16870870e-03, -8.13784488e+00]]), 'rvecs1': [array([[ 0.24025567],
       [-0.16470154],
       [ 1.62415281]]), array([[ 0.20309746],
       [-0.33675631],
       [ 1.56088769]]), array([[ 0.17348998],
       [-0.31134   ],
       [ 1.57421665]]), array([[ 0.05956476],
       [-0.24136777],
       [ 1.52241203]]), array([[ 0.17710151],
       [-0.265335  ],
       [ 1.56867396]]), array([[ 0.15119507],
       [-0.24785676],
       [ 1.56841735]]), array([[-0.32956123],
       [-0.0109262 ],
       [ 1.47182315]]), array([[ 0.19782912],
       [-0.21542165],
       [ 1.59100277]]), array([[ 0.47866468],
       [-0.06567737],
       [ 1.62912895]]), array([[ 0.33694854],
       [-0.45779708],
       [ 1.57283909]]), array([[ 0.08968597],
       [-0.28777778],
       [ 1.54887126]]), array([[-0.11572443],
       [-0.16374579],
       [ 1.57283072]]), array([[ 0.00474852],
       [-0.28051802],
       [ 1.51532016]]), array([[-0.16576603],
       [-0.43316805],
       [ 1.4786565 ]])], 'rvecs2': [array([[ 0.24577773],
       [-0.16138967],
       [ 1.62946186]]), array([[ 0.20927242],
       [-0.32854338],
       [ 1.56622738]]), array([[ 0.18133657],
       [-0.30463203],
       [ 1.57974795]]), array([[ 0.06587236],
       [-0.23071489],
       [ 1.52884493]]), array([[ 0.18403739],
       [-0.25702871],
       [ 1.57390794]]), array([[ 0.16108954],
       [-0.23597115],
       [ 1.57439486]]), array([[-0.32540408],
       [-0.00353862],
       [ 1.47861294]]), array([[ 0.2048795 ],
       [-0.21486832],
       [ 1.59550858]]), array([[ 0.48043987],
       [-0.05789281],
       [ 1.6332763 ]]), array([[ 0.34367626],
       [-0.45052157],
       [ 1.57731969]]), array([[ 0.09414235],
       [-0.27330733],
       [ 1.55472223]]), array([[-0.10956573],
       [-0.15435804],
       [ 1.57965909]]), array([[ 0.00983746],
       [-0.27842791],
       [ 1.5204727 ]]), array([[-0.15474134],
       [-0.42713353],
       [ 1.4844449 ]])], 'R': array([[ 9.99933525e-01, -6.32187699e-03,  9.64262709e-03],
       [ 6.32711952e-03,  9.99979852e-01, -5.13274066e-04],
       [-9.63918795e-03,  5.74250000e-04,  9.99953377e-01]]), 'T': array([[-2.948623  ],
       [ 0.02436695],
       [-0.09942187]]), 'E': array([[ 3.94176492e-04,  9.94338609e-02,  2.43147791e-02],
       [-1.27837593e-01,  2.32177960e-03,  2.94752683e+00],
       [-4.30216161e-02, -2.94840954e+00,  1.27849034e-03]]), 'F': array([[-4.20971940e-09, -1.06128459e-06,  6.78065789e-05],
       [ 1.36453426e-06, -2.47674888e-08, -2.80512319e-02],
       [-2.49829264e-05,  2.75577917e-02,  1.00000000e+00]])})

settings = AppSettings()
