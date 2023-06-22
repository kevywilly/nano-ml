import atexit
import os
import numpy as np
import torch
import torch.nn.functional as F
import torchvision
import traitlets
from traitlets.config import SingletonConfigurable
from src.utils import resize
from settings import settings
from src.config import TrainingConfig, MODELS_ROOT
from src.drivetrain import Drivetrain

torch.hub.set_dir(MODELS_ROOT)

SPEED_DRIVE = settings.robot_drive_speed
SPEED_TURN = settings.robot_turn_speed

class AutoDrive(SingletonConfigurable):
    config = traitlets.Instance(TrainingConfig, default_value=settings.default_model).tag(config=True)
    drivetrain = traitlets.Instance(Drivetrain)
    running = traitlets.Bool(default_value=False)

    def __init__(self, *args, **kwargs):
        super(AutoDrive, self).__init__(*args, **kwargs)
        self.drivetrain = Drivetrain.instance()
        self.direction = 0
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
        x = resize(camera_value, 224, 224)
        x = np.transpose(x, (2, 0, 1))
        x = torch.as_tensor(x, device='cuda').float()
        x = self.normalize(x)
        x = x[None, ...]
        return x

    def predict(self, camera_value):
        input = self._preprocess(camera_value=camera_value)
        output = self.model(input)
        output = F.softmax(output, dim=1)
        return output

    def drive(self, change):
        if not self.running:
            self.direction = 0
            return

        y = self.predict(change['new'])

        forward = float(y.flatten()[0])
        left = float(y.flatten()[1])
        right = float(y.flatten()[2])

        print(f"f: {forward}, l: {left}, r: {right}")

        if (left + right) < 0.5:
            self.direction = 0
        elif (left > right and self.direction == 0):
            self.direction = -1
        elif self.direction == 0:
            self.direction = 1

        if self.direction == 0:
            self.drivetrain.forward(settings.robot_drive_speed)
        elif self.direction == -1:
            self.drivetrain.left(settings.robot_turn_speed)
        else:
            self.drivetrain.right(settings.robot_turn_speed)
