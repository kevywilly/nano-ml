from jetson_inference import detectNet as net
import cv2 as cv
import numpy as np
import torch
import torch.nn.functional as F
import torchvision
import traitlets
from traitlets.config import SingletonConfigurable
from src.visual.utils import (convert_color)
from jetson_utils import cudaImage, cudaMemcpy, cudaToNumpy, cudaAllocMapped, cudaConvertColor, cudaDeviceSynchronize, cudaResize, videoSource
from src.visual.utils import resize

mean = 255.0 * np.array([0.485, 0.456, 0.406])
stdev = 255.0 * np.array([0.229, 0.224, 0.225])
normalize = torchvision.transforms.Normalize(mean, stdev)

device = torch.device('cuda')

camera = videoSource(argv=['--input-flip=rotate-180'])

camera_value = camera.Capture()

def _preprocess(camera_value):
    x = resize(camera_value, 224, 224)
    x = np.transpose(x, (2, 0, 1))
    x = torch.as_tensor(x, device='cuda').float()
    x = normalize(x)
    x = x[None, ...]
    return x

try:
    x = _preprocess(camera_value=camera_value)
    print(x)
except Exception as ex:
    print(f"==============ERROR ===============\n{ex}")
