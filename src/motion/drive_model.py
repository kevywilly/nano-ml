import traitlets
from traitlets.config import SingletonConfigurable
import cv2
from src.robot import Robot
import torch
import torchvision
import torch.nn.functional as F
import numpy as np
from src.training.config import TrainingConfig, MODELS_ROOT
from settings import settings
import os
import atexit

torch.hub.set_dir(MODELS_ROOT)

SPEED_DRIVE = settings.robot_drive_speed
SPEED_TURN = settings.robot_turn_speed

class DriveModel(SingletonConfigurable):

    config = traitlets.Instance(TrainingConfig, default_value=settings.default_model).tag(config=True)

    def __init__(self, *args, **kwargs):
        super(DriveModel,self).__init__(*args, **kwargs)
        self.mean = 255.0 * np.array([0.485, 0.456, 0.406])
        self.stdev = 255.0 * np.array([0.229, 0.224, 0.225])
        self.normalize = torchvision.transforms.Normalize(self.mean, self.stdev)
        self._load_model()
        atexit.register(self.clear_cuda)

    def clear_cuda(self):
        torch.cuda.empty_cache()
       
    def _load_model(self):
        print("preparing model...")

        has_model = os.path.isfile(self.config.get_best_model_path())

        self.model = self.config.load_model(pretrained=(not has_model))
        self.device = torch.device('cuda')

        cat_count = len(self.config.categories)
        
        # create model
        if self.config.model_name == "alexnet":
            self.model.classifier[6] = torch.nn.Linear(self.model.classifier[6].in_features, cat_count)
        elif self.config.model_name == "resnet18":
            self.model.fc = torch.nn.Linear(512, cat_count)
            self.model.eval().half()

        if has_model:
            print("loading state...")
            self.model.load_state_dict(torch.load(self.config.get_best_model_path()))
        else:
            print("skipping state load - model does not exist yet")
            
        self.model = self.model.to(self.device)

        print("model ready...")

    def _preprocess(self, camera_value):
        x = camera_value
        x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
        x = cv2.resize(x, (224,224))
        x = x.transpose((2, 0, 1))
        x = torch.from_numpy(x).float()
        x = self.normalize(x)
        x = x.to(self.device)
        x = x[None, ...]
        return x
    
    def predict(self, camera_value):
        input = self._preprocess(camera_value=camera_value)
        output = self.model(input)
        output = F.softmax(output, dim=1)
        return output
