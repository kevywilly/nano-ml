import cv2 as cv
from cv2 import Mat

def bgr8_to_jpeg(value):
    return bytes(cv.imencode('.jpg', value)[1])

def crop(img: Mat, pct: float):
    if pct == 1.0:
        return img

    (h, w) = img.shape[:2]
    fact = 1 - pct
    yfactor = int(h * fact / 2)
    xfactor = int(w * fact / 2)
    return img[yfactor:h - yfactor, xfactor:w - xfactor]

def merge_3d(img_l, img_r):
    out = img_r.copy()
    # out[:, :, 0] = img_r[:, :, 0]
    # out[:, :, 1] = img_r[:, :, 1]
    out[:, :, 2] = img_l[:, :, 2]

    return out
