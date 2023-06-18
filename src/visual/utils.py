import cv2 as cv
from jetson_utils import cudaImage, cudaMemcpy, cudaToNumpy, cudaAllocMapped, cudaConvertColor

def convert_color(img:cudaImage, output_format):
    converted_img = cudaAllocMapped(width=img.width, height=img.height, format=output_format)
    cudaConvertColor(img, converted_img)
    return converted_img

def cuda_to_jpeg(value: cudaImage):
    img = cudaToNumpy(convert_color(value, "bgr8"))
    return bytes(cv.imencode('.jpg', img)[1])

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



def resize(img:cudaImage, dims):
	resized_img = cudaAllocMapped(width=dims[0],
								  height=dims[0],
                                  format=img.format)
        
