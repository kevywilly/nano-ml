import os
from pathlib import Path
from uuid import uuid1
import cv2
import traitlets
from traitlets.config import SingletonConfigurable
from settings import settings
from src.config import TrainingConfig
from src.image import Image

class ImageCollector(SingletonConfigurable):
    counts = traitlets.Dict()
    config = traitlets.Instance(TrainingConfig, default_value=settings.default_model).tag(config=True)

    def __init__(self, *args, **kwargs):
        super(ImageCollector, self).__init__(*args, **kwargs)
        self._make_folders()
        self._generate_counts()

    def category_path(self, category: str, cam_index=1) -> str:
        return os.path.join(self.config.get_data_path(cam_index), category.replace(" ", "_"))

    def get_count(self, category: str) -> int:
        value = len(os.listdir(self.category_path(category, 1)))
        self.counts[category] = value
        return value

    def _generate_counts(self):
        for category in self.config.categories:
            self.get_count(category)

    def _make_folders(self):
        for category in self.config.categories:
            for i in range(self.config.num_cameras):
                try:
                    os.makedirs(self.category_path(category, i+1))
                except FileExistsError:
                    pass
                except Exception as ex:
                    print(ex)
                    raise ex

    def collect(self, category: str, images) -> int:
        print(f"collecting {len(images)} for {category}")
        
        if category in self.config.categories:
            name = str(uuid1()) + ".jpg"
            for index, image in enumerate(images):
                pth = os.path.join(
                    self.category_path(category, index+1),
                    name
                )
                
                with open(pth, 'wb') as f:
                    print(f"writing to {pth}")
                    try:
                        f.write(image.value)
                    except Exception as ex:
                        print(ex)

            return self.get_count(category)

        return -1

    def get_images(self, category):
        paths = sorted(Path(self.category_path(category)).iterdir(), key=os.path.getctime)
        return [p.name for p in paths]

    def load_image(self, category, name, cam_index = 1):
        im = cv2.imread(os.path.join(self.category_path(category, cam_index), name), cv2.IMREAD_ANYCOLOR)
        _, im_bytes_np = cv2.imencode('.jpeg', im)

        return im_bytes_np.tobytes()

    def delete_image(self, category, name):
        for i in range(self.config.num_cameras):
            try:
                os.remove(os.path.join(self.category_path(category, i+1), name))
            except:
                pass

        return True
