
from traitlets.config import SingletonConfigurable
from uuid import uuid1
import os
from settings import settings
import cv2 as cv

class Calibrator():

    def __init__(self):
        self.stereo_count = 0
        self.left_count = 0
        self.right_count = 0

        self.right_folder = f"{settings.calibration_folder}/images/right"
        self.left_folder = f"{settings.calibration_folder}/images/left"
        self.stereo_right_folder = f"{settings.calibration_folder}/images/stereo/right"
        self.stereo_left_folder = f"{settings.calibration_folder}/images/stereo/left"
        
        self._make_folder(self.right_folder)
        self._make_folder(self.left_folder)
        self._make_folder(self.stereo_right_folder)
        self._make_folder(self.stereo_left_folder)
        
        self._get_counts()

    def _make_folder(self, folder):
        try:
            os.makedirs(folder)
        except FileExistsError:
            pass
        except Exception as ex:
            print(ex)
            raise ex

    def _get_counts(self):
        self.stereo_count = self._get_count(self.stereo_right_folder)
        self.right_count = self._get_count(self.right_folder)
        self.left_count = self._get_count(self.left_folder)

    def _get_count(self, folder):
        return len(os.listdir(folder))
    
    def _write_image(self, image, folder: str, filename: str):
        pth = os.path.join(folder, filename)
        cv.imwrite(pth, img=image)

    def _generate_filenamne(self):
        return f"{str(uuid1())}.png"
    
    def collect_stereo(self, image_right, image_left) -> int:
        print("collecting stereo")
        filename = self._generate_filenamne()
        self._write_image(image_right, self.stereo_right_folder, filename)
        self._write_image(image_left, self.stereo_left_folder, filename)
        self.stereo_count = self.stereo_count + 1
        return self.stereo_count
    
    def collect_single(self, image, cam_index: int) -> int:
        print(f"collecting single {cam_index}")
        folder = [self.right_folder, self.left_folder][cam_index]
        pth = os.path.join(folder, self._generate_filenamne())

        with open(pth, 'wb') as f:
            f.write(image.value)

        if cam_index == 0:
            self._write_image(image, self.right_folder, self._generate_filenamne())
            self.right_count += 1
            return self.right_count
        else:
            self._write_image(image, self.left_folder, self._generate_filenamne())
            self.left_count += 1
            return self.left_count

        


