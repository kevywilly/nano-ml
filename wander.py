import argparse
import traitlets
from jetbot.robot import Robot
import torch
import torchvision
import torch.nn.functional as F
import time
import cv2
import numpy as np
import signal
import PIL.Image
from settings import settings

torch.hub.set_dir(settings.default_model.model_path)

mean = torch.Tensor([0.485, 0.456, 0.406]).cuda()
std = torch.Tensor([0.229, 0.224, 0.225]).cuda()

def preprocess(image):
    device = torch.device('cuda')
    image = PIL.Image.fromarray(image)
    image = transforms.functional.to_tensor(image).to(device)
    image.sub_(mean[:, None, None]).div_(std[:, None, None])
    return image[None, ...]

class WanderApplication(traitlets.HasTraits):
    
    collision_model = traitlets.Unicode()
    robot = traitlets.Instance(Robot)
    
    def __init__(self, *args, **kwargs):
        super(WanderApplication, self).__init__(*args, **kwargs)
        self.mean = 255.0 * np.array([0.485, 0.456, 0.406])
        self.stdev = 255.0 * np.array([0.229, 0.224, 0.225])
        self.normalize = torchvision.transforms.Normalize(self.mean, self.stdev)
        self.robot = Robot()
        self.robot.log("Loading Wander App")
        
    
    def _preprocess(self, camera_value):
        x = camera_value
        x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB)
        x = x.transpose((2, 0, 1))
        x = torch.from_numpy(x).float()
        x = self.normalize(x)
        x = x.to(self.device)
        x = x[None, ...]
        return x
    
    def _update_test(self, change):
        print(change["new"])

    def _update(self, change):
        x = change['new'] 
        x = self._preprocess(x)
        y = self.model(x)
        y = F.softmax(y, dim=1)

        prob_blocked_center = float(y.flatten()[0])
        prob_blocked_left = float(y.flatten()[1])
        prob_blocked_right = float(y.flatten()[2])

        if prob_blocked_center:
            if prob_blocked_left <= prob_blocked_right:
                self.robot.log("turn left")
                self.robot.left(0.2)
            else:
                self.robot.log("turn right")
                self.robot.right(0.2)
        elif prob_blocked_right:
            self.robot.log("turn left")
            self.robot.left(0.2)
        elif prob_blocked_left:
            self.robot.log("turn right")
            self.robot.right(0.2)
        else:
            self.robot.log("forward")
            self.robot.forward(0.2)
            
    
    def start(self):
        self.device = torch.device('cuda')
        
        self.robot.log("Loading model...")
        
        # create model
        self.model = torchvision.models.alexnet(pretrained=False)
        self.model.classifier[6] = torch.nn.Linear(self.model.classifier[6].in_features, 4)
        self.model.load_state_dict(torch.load(self.collision_model))
        self.model = self.model.to(self.device)
    
        self.robot.log("Model loaded...")
        
        self.robot.log('Initializing camera...')
        # create camera
        
        self.robot.log('Running...')
        self.robot.camera.camera.observe(self._update, names='value')
        
        def kill(sig, frame):
            self.robot.log('Shutting down...')
            self.robot.camera.stop()
            
        signal.signal(signal.SIGINT, kill)
        
        # self.camera.thread.join()
        
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('collision_model', help='Path of the trained Alexnet collision model')
    args = parser.parse_args()
    
    application = WanderApplication(collision_model=args.collision_model)
    application.start()
    
    
    
    