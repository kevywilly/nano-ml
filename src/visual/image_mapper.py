import cv2 as cv
from settings import settings
from pydantic import BaseModel
from typing import Any

class Map3d(BaseModel):
    left_map_1: Any
    left_map_2: Any
    right_map_1: Any
    right_map_2: Any

class ImageMapper:

    def __init__(self):
        self.map3d = self.load_3d_map(settings.calibration_3d_map_file)

    
    def map_3d(self, img_l, img_r):

        mapped_l = cv.remap(img_l, self.map3d.left_map_1, self.map3d.left_map_2, cv.INTER_LANCZOS4)
        mapped_r = cv.remap(img_r, self.map3d.right_map_1, self.map3d.right_map_2, cv.INTER_LANCZOS4)
 
        out = mapped_r.copy()
       
        out[:,:,0] = mapped_r[:,:,0]
        out[:,:,1] = mapped_r[:,:,1]
        out[:,:,2] = mapped_l[:,:,2]

        (h,w) = out.shape[:2]
        return out[18:h-18, 32:w-32]
    
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