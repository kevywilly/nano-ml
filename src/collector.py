import traitlets
from traitlets.config import SingletonConfigurable
from typing import List
from uuid import uuid1
import os
from src.image import Image
from config import TrainingConfig, MODELS_ROOT
from settings import settings

class ImageCollector(SingletonConfigurable):

    counts = traitlets.Dict()
    config = traitlets.Instance(TrainingConfig, default_value=settings.default_model).tag(config=True)
 
    
    def __init__(self, *args, **kwargs):
        super(ImageCollector, self).__init__(*args, **kwargs)
        self._make_folders()
        self._generate_counts()

    def category_path(self, category: str) -> str:
        return os.path.join(self.config.get_data_path(),category.replace(" ","_"))
    
    def get_count(self,category: str) -> int:
        value = len(os.listdir(self.category_path(category)))
        self.counts[category] = value
        return value

    def _generate_counts(self):
        for category in self.config.categories:
            self.get_count(category)

    def _make_folders(self):
        for category in self.config.categories:
            try:
                os.makedirs(self.category_path(category))
            except FileExistsError:
                pass
            except Exception as ex:
                print(ex)
                raise ex
    
    def collect(self, category: str, image: Image) -> int:
        if category in self.config.categories:
            pth = os.path.join(
                self.category_path(category),
                str(uuid1())+".jpg"
                )
            with open(pth, 'wb') as f:
                f.write(image.value)
            
            return self.get_count(category)
        
        return -1


