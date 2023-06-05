
from traitlets.config import SingletonConfigurable
from uuid import uuid1
import os
from src.image import Image
from settings import settings

class Calibrator():

    def __init__(self):
        self.count = 0
        self._collection_folders = [
            f"{settings.calibration_folder}/images/right",
            f"{settings.calibration_folder}/images/left"
        ]
        self._make_folders()

    def _make_folders(self):
        try:
            for folder in self._collection_folders:
                os.makedirs(folder)
        except FileExistsError:
            pass
        except Exception as ex:
            print(ex)
            raise ex
        
        self.count = len(os.listdir(self._collection_folders[0]))

    def collect(self, image_right: Image, image_left: Image) -> int:
        filename = f"{str(uuid1())}.jpg"
        images = [image_right, image_left]
        for idx, folder in enumerate(self._collection_folders):
            pth = os.path.join(folder, filename)
            with open(pth, 'wb') as f:
                f.write(images[idx].value)

        self.count = self.count + 1
        return self.count

        


