from typing import Any

import cv2 as cv
from pydantic import BaseModel

from settings import settings


class Map3d(BaseModel):
    left_map_1: Any
    left_map_2: Any
    right_map_1: Any
    right_map_2: Any


class ImageMapper:

    def __init__(self):
        self.map3d = self.load_3d_map(settings.calibration_3d_map_file)

        # self.lm1 = cv.cuda_GpuMat(self.map3d.left_map_1)
        # self.lm2 = cv.cuda_GpuMat(self.map3d.left_map_2)
        # self.rm1 = cv.cuda_GpuMat(self.map3d.right_map_1)
        # self.rm2 = cv.cuda_GpuMat(self.map3d.right_map_2)

    def crop(self, img, pct: float):
        if pct == 1.0:
            return img

        (h, w) = img.shape[:2]
        fact = 1 - pct
        yfactor = int(h * fact / 2)
        xfactor = int(w * fact / 2)
        return img[yfactor:h - yfactor, xfactor:w - xfactor]

    def remap(self, img1, img2, pct=0.90):
        img1 = self.crop(cv.remap(img1, self.map3d.left_map_1, self.map3d.left_map_2, cv.INTER_LINEAR), pct)
        img2 = self.crop(cv.remap(img2, self.map3d.right_map_1, self.map3d.right_map_2, cv.INTER_LINEAR), pct)

        return img1, img2

    def merge_3d(self, img_l, img_r):
        out = img_r.copy()
        out[:, :, 0] = img_r[:, :, 0]
        out[:, :, 1] = img_r[:, :, 1]
        out[:, :, 2] = img_l[:, :, 2]

        return out

    def map_3d(self, img_l, img_r):
        # limage = cv.cuda_GpuMat(img_l)
        # rimage = cv.cuda_GpuMat(img_r)

        # mapped_l = cv.cuda.remap(limage, self.lm1, self.lm2, cv.INTER_LINEAR)
        # mapped_r = cv.cuda.remap(rimage, self.rm1, self.rm2, cv.INTER_LINEAR)

        # mapped_l = mapped_l.convertTo(mapped_l, 5, 1, 0);
        # mapped_r = mapped_r.convertTo(mapped_r, 5, 1, 0);

        mapped_l, mapped_r = self.remap(img_l, img_r, 1.0)
        mapped_r = cv.remap(img_r, self.map3d.right_map_1, self.map3d.right_map_2, cv.INTER_LINEAR)

        # out = mapped_r.copy()

        # out[:,:,0] = mapped_r[:,:,0]
        # out[:,:,1] = mapped_r[:,:,1]
        # out[:,:,2] = mapped_l[:,:,2]
        mapped_r[:, :, 2] = mapped_l[:, :, 2]

        return self.crop(mapped_r, 0.90)

    def load_3d_map(self, filename: str) -> Map3d:
        cv_file = cv.FileStorage(filename, cv.FILE_STORAGE_READ)
        cv_file
        m: Map3d = Map3d(
            left_map_1=cv_file.getNode("left_map_1").mat(),
            left_map_2=cv_file.getNode("left_map_2").mat(),
            right_map_1=cv_file.getNode("right_map_1").mat(),
            right_map_2=cv_file.getNode("right_map_2").mat(),
        )
        cv_file.release()
        return m
