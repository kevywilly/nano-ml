import cv2 as cv
from jetson_utils import cudaImage, cudaMemcpy, cudaToNumpy, cudaAllocMapped, cudaConvertColor, cudaDeviceSynchronize, cudaResize
from jetson_inference import detectNet
import sys
from settings import settings

overlay = "box,labels,conf"
model = "ssd-mobilenet-v2"
threshold = 0.5

# Load Detectnet
if settings.use_detctnet:
    net = detectNet(model, sys.argv, threshold)


def detect(img: cudaImage):
    try:
        if settings.use_detctnet:
            img2 = cudaMemcpy(img)
            detections = net.Detect(img2, overlay=settings.detectnet_overlay)
            print("detected {:d} objects in image".format(len(detections)))
            return cuda_to_jpeg(img2)
        return cuda_to_jpeg(img)
    except Exception as ex:
        print(ex)


def convert_color(img:cudaImage, output_format):
    converted_img = cudaAllocMapped(width=img.width, height=img.height, format=output_format)
    cudaConvertColor(img, converted_img)
    return converted_img


def resize(img: cudaImage, width, height):
    resized = cudaAllocMapped(width=width, height=height, format=img.format)
    cudaResize(img, resized)
    return resized
    

def cuda_to_jpeg(value: cudaImage):
    converted = convert_color(value, "bgr8")
    cudaDeviceSynchronize()
    return bgr8_to_jpeg(cudaToNumpy(converted))


def bgr8_to_jpeg(cvImage):
    return bytes(cv.imencode('.jpg', cvImage)[1])


def crop(img, pct: float):

    if pct == 1.0:
        return img

    (h, w) = img.shape[:2]
    fact = 1 - pct
    yfactor = int(h * fact / 2)
    xfactor = int(w * fact / 2)
    return img[yfactor:h - yfactor, xfactor:w - xfactor]


def merge_3d(img_l, img_r):
    right = cudaToNumpy(convert_color(img_l, "bgr8"))
    left = cudaToNumpy(convert_color(img_r, "bgr8"))
    out = right.copy()
    out[:, :, 2] = left[:, :, 2]

    return out

        
