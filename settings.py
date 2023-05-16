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

    def num_categories(self):
        return len(self.categories)
    
    def load_model(self, *args, **kwargs):
        if self.model is None:
            if self.model_name == "alexnet":
                self.model = torchvision.models.alexnet(*args, **kwargs)
            if self.model_name == "resnet18":
                self.model = torchvision.models.resnet18(*args, **kwargs)
        
        return self.model


class AppSettings(BaseSettings):

    left_motor_alpha: float = 1.0
    right_motor_alpha: float = 1.01

    data_root: str = "/ml_data"
    datasets_root: str = f"{data_root}/datasets"
    models_root: str = f"{data_root}/models"
    best_models_root: str =  f"{models_root}/best"


    default_model: ModelSettings = ModelSettings(
        model_name="resnet18",
        model_path = models_root,
        data_path=f"{datasets_root}/fb3",
        best_model_path = f"{best_models_root}/fb3.pth",
        categories = ["blocked","blocked_left","blocked_right","free"]
    )

    simple_model: ModelSettings = ModelSettings(
        model_name="alexnet",
        model_path = models_root,
        data_path=f"{datasets_root}/fb",
        best_model_path = f"{best_models_root}/fb.pth",
        categories = ["blocked","free"]
    )

settings = AppSettings()
