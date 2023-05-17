from pydantic import BaseSettings
from typing import List
from pydantic import BaseModel
from typing import Optional, Any
import torchvision
from config import TrainingConfig
from config import Obstacle2dConfig, Obstacle3dConfig, Navigate2dConfig

class AppSettings(BaseSettings):

    left_motor_alpha: float = 1.0
    right_motor_alpha: float = 1.0

    robot_drive_speed: float = 0.25
    robot_turn_speed: float = 0.18

    default_model: TrainingConfig = Obstacle3dConfig

settings = AppSettings()
