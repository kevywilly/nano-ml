from pydantic import BaseSettings
from typing import List
from pydantic import BaseModel
from typing import Optional, Any
import torchvision


class ModelSettings(BaseModel):
    model_name: str
    model_path: str
    data_path: str
    best_model_path: str
    categories: List[str] 
    model: Optional[Any]
    classifier: Optional[Any]

    def load_model(self, *args, **kwargs):
        if self.model is None:
            if self.model_name == "alexnet":
                self.model = torchvision.models.alextnet(*args, **kwargs)
            if self.model_name == "resnet18":
                self.model = torchvision.models.resnet18(*args, **kwargs)
        
        return self.model


class AppSettings(BaseSettings):

    left_motor_alpha: float = 1.0
    right_motor_alpha: float = 1.075

    default_model: ModelSettings = ModelSettings(
        model_name="alexnet",
        model_path = "/ml-data/models",
        data_path="datasets/flbr",
        best_model_file = "ml-data/models/best/flbr.pth"
        categories = ["blocked_center","blocked_left","blocked_right","free"]
    )

settings = AppSettings()
