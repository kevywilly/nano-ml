import traitlets
import cv2
from src.robot import Robot
import torch
import torchvision
import torch.nn.functional as F
import numpy as np
import signal
import PIL.Image
from settings import settings, ModelSettings

torch.hub.set_dir(settings.default_model.model_path)

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda()

class Wanderer(traitlets.HasTraits):

    model_settings = traitlets.Instance(ModelSettings)
    robot = traitlets.Instance(Robot)

    def __init__(self, robot: Robot, model_settings: ModelSettings, *args, **kwargs):
        super(Wanderer,self).__init__(*args, **kwargs)
        self.robot = robot
        self.model_settings = model_settings
        self.mean = 255.0 * np.array([0.485, 0.456, 0.406])
        self.stdev = 255.0 * np.array([0.229, 0.224, 0.225])
        self.normalize = torchvision.transforms.Normalize(self.mean, self.stdev)
        self.robot.log("Loading wander app...")
        self.robot.log("Loading collision model...")
        self.model = model_settings.load_model(pretrained=False)
    
    def _preprocess(self, camera_value):
        x = camera_value
        x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
        x = x.transpose((2, 0, 1))
        x = torch.from_numpy(x).float()
        x = self.normalize(x)
        x = x.to(self.device)
        x = x[None, ...]
        return x
    
    def _update(self, change):
        x = change['new'] 
        x = self._preprocess(x)
        y = self.model(x)
        y = F.softmax(y, dim=1)

        ff = """
        prob_blocked = float(y.flatten()[0])

        if prob_blocked < 0.5:
            self.robot.forward(0.2)
        else:
            self.robot.left(0.2)
        """
        flat = y.flatten()
        prob_blocked_center = float(flat[0])
        prob_blocked_left = float(flat[1])
        prob_blocked_right = float(flat[2])
        prob_free = float(flat[3])

        print(prob_blocked_center, prob_blocked_left, prob_blocked_right, prob_free)

        if prob_blocked_center >= 0.5:
            if prob_blocked_left <= prob_blocked_right:
                self.robot.log("turn left")
                self.robot.left(0.2)
            else:
                self.robot.log("turn right")
                self.robot.right(0.2)
        elif prob_blocked_right >= 0.5:
            self.robot.log("turn left")
            self.robot.left(0.2)
        elif prob_blocked_left >= 0.5:
            self.robot.log("turn right")
            self.robot.right(0.2)
        else:
            self.robot.log("forward")
            self.robot.forward(0.2)
       

    def start(self):
        self.device = torch.device('cuda')
        
        self.robot.log("Loading model...")
        
        # create model
        if self.model_settings.model_name == "alexnet":
            self.model.classifier[6] = torch.nn.Linear(self.model.classifier[6].in_features, self.model_settings.num_categories())
        elif self.model_settings.model_name == "resnet18":
            self.model.fc = torch.nn.Linear(512, self.model_settings.num_categories())

        self.model.load_state_dict(torch.load(self.model_settings.best_model_path))
        self.model = self.model.to(self.device)
    
        self.robot.log("Model loaded...")
        
        self.robot.log('Running...')
        self.robot.camera.observe(self._update, names='value')
        
        def kill(sig, frame):
            self.robot.log('Shutting down...')
            self.robot.camera.stop()
            
        signal.signal(signal.SIGINT, kill)
        
        # self.camera.thread.join()



    
    

