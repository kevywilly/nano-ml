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

    cam_width: int = 640
    cam_height: int = 360
    cam_fps: float = 30
    cam_capture_width: int = 1920
    cam_capture_height:int = 1080

    camera_model: CameraModel = None

settings = AppSettings()
