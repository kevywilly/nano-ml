from pydantic import BaseSettings
from typing import List
from pydantic import BaseModel
from typing import Optional, Any
import torchvision

DATA_ROOT: str = "/ml_data"
DATASETS_ROOT: str = f"{DATA_ROOT}/datasets"
MODELS_ROOT: str = f"{DATA_ROOT}/models"
BEST_MODELS_ROOT: str =  f"{MODELS_ROOT}/best"

class TrainingConfig(BaseModel):
    name: str
    model_name: str
    categories: List[str] 
    model: Optional[Any]

    def get_best_model_path(self):
        return f"{BEST_MODELS_ROOT}/{self.name}.pth"
    
    def get_data_path(self):
        return f"{DATASETS_ROOT}/{self.name}"

    def num_categories(self):
        return len(self.categories)
    
    def load_model(self, *args, **kwargs):
        if self.model_name == "alexnet":
            return torchvision.models.alexnet(*args, **kwargs)
        if self.model_name == "resnet18":
            return torchvision.models.resnet18(*args, **kwargs)
    
Obstacle3dConfig = TrainingConfig(
        name="obstacle3d",
        model_name="alexnet",
        categories = ["turn_left","turn_right","forward"]
    )

Obstacle3dV2Config = TrainingConfig(
        name="obstacle3dV2",
        model_name="alexnet",
        categories = ["turn_left","turn_right","forward"]
    )

Obstacle2dConfig: TrainingConfig = TrainingConfig(
        name="obstacle2d",
        model_name="alexnet",
        categories = ["blocked","free"]
    )

Navigate2dConfig: TrainingConfig = TrainingConfig(
        name="navigate2d",
        model_name="alexnet",
        categories = ["turn_left","turn_right"]
    )