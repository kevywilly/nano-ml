from pydantic import BaseSettings
from typing import List

from src.config import TrainingConfig


from src.config import (
    Obstacle2dConfig, 
    Obstacle3dConfig, 
    Navigate2dConfig, 
    Obstacle3dV2Config, 
    Obstacle5dConfig,
    MecanumConfig
)

class CalibrationSettings(BaseSettings):
    base_folder: str = "/home/nano/nano-ml/data/calibration"
    model_folder: str = "/home/nano/nano-ml/data/calibration/models"
    model_file: str = "/home/nano/nano-ml/data/calibration/models/camera_model.xml"
    rectification_model_file: str = "/home/nano/nano-ml/data/calibration/models/rectification_model.xml"
    d3_map_file: str = "/home/nano/nano-ml/data/calibration/models/3dmap.xml"

    output_folder = f"{base_folder}/images/output"
    right_folder = f"{base_folder}/images/stereo/right"
    left_folder = f"{base_folder}/images/stereo/left"

class AppSettings(BaseSettings):

    # Drivetrain Settings

    reverse_motors: bool = True

    m1_alpha: float = 1.0
    m2_alpha: float = 1.0
    m3_alpha: float = 1.0
    m4_alpha: float = 1.0

    robot_drive_speed: float = 0.65
    robot_turn_speed: float = 0.65

    # Training Settings

    default_model: TrainingConfig = Obstacle3dV2Config
    retrain_model: bool = True
    default_epochs: int = 60
    default_retrain_epochs: int = 10
    led_pins: List[int] = [200,38]

    # Input Settings

    cam_width: int = 1280
    cam_height: int = 720
    cam_fps: float = 30
    cam_capture_width: int = 1280
    cam_capture_height:int = 720

    # Detectnet Settings
    
    use_detctnet: bool = False
    detectnet_overlay: str = "box,labels,conf"
    detect_net_model: str = "ssd-mobilenet-v2"
    detect_net_threshold: float = 0.5

settings = AppSettings()
calibration_settings = CalibrationSettings()
