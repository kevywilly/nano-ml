from typing import List
from typing import Optional, Any
import torchvision
from pydantic import BaseModel

DATA_ROOT: str = "/home/nano/nano-ml/data"
DATASETS_ROOT: str = f"{DATA_ROOT}/datasets"
MODELS_ROOT: str = f"{DATA_ROOT}/models"
BEST_MODELS_ROOT: str = f"{MODELS_ROOT}/best"

class TrainingConfig(BaseModel):
    name: str
    model_name: str
    categories: List[str]
    model: Optional[Any]
    num_cameras: int = 1

    def get_best_model_path(self, cam_index=1):
        return f"{BEST_MODELS_ROOT}/{self.name}_{cam_index}.pth"

    def get_data_path(self, cam_index=1):
        return f"{DATASETS_ROOT}/{self.name}_{cam_index}"
    
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
    categories=["left", "right", "forward"]
)

Obstacle3dV2Config = TrainingConfig(
    name="obstacle3dV2",
    model_name="alexnet",
    categories=["left", "right", "forward"],
    num_cameras=2
)

Obstacle2dConfig: TrainingConfig = TrainingConfig(
    name="obstacle2d",
    model_name="alexnet",
    categories=["blocked", "free"]
)

Navigate2dConfig: TrainingConfig = TrainingConfig(
    name="navigate2d",
    model_name="alexnet",
    categories=["left", "right"]
)

Navigate5d = TrainingConfig(
    name="obstacle5d",
    model_name="alexnet",
    categories=["forward", "dleft", "dright", "left", "right"]
)

MecanumConfig = TrainingConfig(
    name="mecanum",
    model_name="alexnet",
    categories=["forward", "left", "right", "left", "right"],
    num_cameras=2
)
