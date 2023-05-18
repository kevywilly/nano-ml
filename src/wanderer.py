import traitlets
import cv2
from src.robot import Robot
import torch
import torchvision
import torch.nn.functional as F
import numpy as np
import signal
import PIL.Image
from config import TrainingConfig, MODELS_ROOT
from settings import settings
import sys

torch.hub.set_dir(MODELS_ROOT)

SPEED_DRIVE = settings.robot_drive_speed
SPEED_TURN = settings.robot_turn_speed

class Wanderer(traitlets.HasTraits):

    training_config = traitlets.Instance(TrainingConfig)
    robot = traitlets.Instance(Robot)

    def __init__(self, robot: Robot, training_config: TrainingConfig, *args, **kwargs):
        super(Wanderer,self).__init__(*args, **kwargs)
        self.robot = robot
        self.training_config = training_config
        self.mean = 255.0 * np.array([0.485, 0.456, 0.406])
        self.stdev = 255.0 * np.array([0.229, 0.224, 0.225])
        self.normalize = torchvision.transforms.Normalize(self.mean, self.stdev)
        self.robot.log("Loading wander app...")
        self.robot.log("Loading collision model...")
        self.model = training_config.load_model(pretrained=False)
        self.dir = 0

    
    def _preprocess(self, camera_value):
        x = camera_value
        x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
        x = x.transpose((2, 0, 1))
        x = torch.from_numpy(x).float()
        x = self.normalize(x)
        x = x.to(self.device)
        x = x[None, ...]
        return x
    
    def _handle_obstacle3d(self, y):
        
        forward = float(y.flatten()[0])
        left = float(y.flatten()[1])
        right = float(y.flatten()[2])

        print(f"f: {forward}, l: {left}, r: {right}")
        
        if (left + right) < 0.5:
            self.dir = 0
        elif left > right:
            self.dir = -1 if self.dir == 0 else self.dir
        else:
            self.dir = 1 if self.dir == 0 else self.dir

        if self.dir == 0:
            self.robot.forward(SPEED_DRIVE)
        elif self.dir == -1:
             self.robot.left(SPEED_TURN)
        else:
            self.robot.right(SPEED_TURN)


    def _handle_obstacle2d(self, y):
        prob_blocked = float(y.flatten()[0])
        if prob_blocked < 0.5:
            self.robot.forward(SPEED_DRIVE)
        else:
            self.robot.left(SPEED_TURN)

    def _update(self, change):
        x = change['new'] 
        x = self._preprocess(x)
        y = self.model(x)
        y = F.softmax(y, dim=1)

        if self.training_config.name.startswith("obstacle3d"):
            self._handle_obstacle3d(y)
        else:
            self._handle_obstacle2d(y)

    def start(self):
        self.device = torch.device('cuda')
        
        self.robot.log("Loading model...")

        num_categories = len(self.training_config.categories)
        
        # create model
        if self.training_config.model_name == "alexnet":
            self.model.classifier[6] = torch.nn.Linear(self.model.classifier[6].in_features, num_categories)
        elif self.training_config.model_name == "resnet18":
            self.model.fc = torch.nn.Linear(512, num_categories)
            self.model.eval().half()

        self.model.load_state_dict(torch.load(self.training_config.get_best_model_path()))
        self.model = self.model.to(self.device)
    
        self.robot.log("Model loaded...")
        
        self.robot.log('Running...')
        self.robot.camera.observe(self._update, names='value')

        self._update({"new": self.robot.camera.value})
        
        def kill(sig, frame):
            self.robot.log('Shutting down...')
            sys.exit("done") 

        signal.signal(signal.SIGINT, kill)
        
        # self.camera.thread.join()



    
    

