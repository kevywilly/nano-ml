import traitlets
import cv2
from src.robot import Robot
import torch
import torchvision
import torch.nn.functional as F
import numpy as np
import signal
from config import TrainingConfig, MODELS_ROOT, Obstacle2dConfig, Navigate2dConfig
from settings import settings
import time

torch.hub.set_dir(MODELS_ROOT)

# mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
# std = torch.Tensor([0.229, 0.224, 0.225]).cuda()

SPEED_DRIVE = settings.robot_drive_speed
SPEED_TURN = settings.robot_turn_speed

COLLISION = Obstacle2dConfig
NAVIGATION = Navigate2dConfig

class Navigator(traitlets.HasTraits):

    robot = traitlets.Instance(Robot)

    def __init__(self, robot: Robot, *args, **kwargs):
        super(Navigator,self).__init__(*args, **kwargs)

        self.robot = robot
        self.mean = 255.0 * np.array([0.485, 0.456, 0.406])
        self.stdev = 255.0 * np.array([0.229, 0.224, 0.225])
        self.normalize = torchvision.transforms.Normalize(self.mean, self.stdev)

        self.robot.log("loading models ...")

        self.obs_config = Obstacle2dConfig
        self.nav_config = Navigate2dConfig
        self.obs_model = self.obs_config.load_model()
        self.nav_model = self.nav_config.load_model()
        self.dir = 0

    
    def _preprocess(self, camera_value, device = None):
        x = camera_value
        x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
        x = x.transpose((2, 0, 1))
        x = torch.from_numpy(x).float()
        x = self.normalize(x)
        if device:
            x = x.to(device)
        x = x[None, ...]
        return x
    


    def _handle_navigation(self, image):
        input = self._preprocess(image)
        output = self.nav_model(input)
        softmax = F.softmax(output, dim=1)

        prob_left = float(softmax.flatten()[0])
        if(prob_left > 0.5):
            self.dir = -1
            self.robot.left(SPEED_TURN)
        else:
            self.dir = 1
            self.robot.right(SPEED_TURN)

    def _update(self, change):
        image = change["new"]
        input = self._preprocess(image,self.device1)
        output = self.obs_model(input)
        softmax = F.softmax(output, dim=1)

        prob_blocked = softmax.flatten()[0]
        
        if(prob_blocked <= 0.5):
            self.dir = 0
            self.robot.forward(SPEED_DRIVE)
        else:
            if self.dir < 0:
                self.robot.left(SPEED_TURN)
            elif self.dir > 0:
                self.robot.right(SPEED_TURN)
            else:
                self._handle_navigation(image=image)


    def start(self):
        
        print("setting up cuda devices")
        
        self.device1 = torch.device('cuda')
        
        
        self.robot.log("Loading model...")

        obs_categories = len(self.obs_config.categories)
        nav_categories = len(self.nav_config.categories)
        
        # config model classifiers
        if self.obs_config.model_name == "alexnet":
            self.obs_model.classifier[6] = torch.nn.Linear(self.obs_model.classifier[6].in_features, obs_categories)
        elif self.obs_config.model_name == "resnet18":
            self.obs_model.fc = torch.nn.Linear(512, obs_categories)
            self.obs_model.eval().half()

        if self.nav_config.model_name == "alexnet":
            self.nav_model.classifier[6] = torch.nn.Linear(self.nav_model.classifier[6].in_features, nav_categories)
        elif self.nav_config.model_name == "resnet18":
            self.nav_model.fc = torch.nn.Linear(512, nav_categories)
            self.nav_model.eval().half()

        self.obs_model.load_state_dict(torch.load(self.obs_config.get_best_model_path()))
        self.nav_model.load_state_dict(torch.load(self.nav_config.get_best_model_path()))

        self.obs_model = self.obs_model.to(self.device1)

        
        self.robot.log('Running...')
        self._update({"new": self.robot.camera.value})
        self.robot.camera.observe(self._update, names='value')
   
        
        def kill(sig, frame):
            self.robot.log('Shutting down...')
            self.robot.camera.stop()
            
        signal.signal(signal.SIGINT, kill)
        
        # self.camera.thread.join()



    
    

