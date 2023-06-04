from pydantic import BaseSettings
from typing import List
from pydantic import BaseModel
from typing import Optional, Any
import torchvision
from config import TrainingConfig
from config import (
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

    default_model: TrainingConfig = MecanumConfig
    retrain_model: bool = True
    default_epochs: int = 30
    default_retrain_epochs: int = 10
    led_pins: List[int] = [200,38]

settings = AppSettings()
