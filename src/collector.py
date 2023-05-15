import traitlets
from typing import List
from uuid import uuid1
import os
from src.image import Image
from settings import ModelSettings

class ImageCollector(traitlets.HasTraits):

    counts = traitlets.Dict()
    model_settings = traitlets.Instance(ModelSettings)
 
    
    def __init__(self, model_settings: ModelSettings, *args, **kwargs):
        super(ImageCollector, self).__init__(*args, **kwargs)
        self.model_settings = model_settings
        self._make_folders()
        self._generate_counts()

    def category_path(self, category: str) -> str:
        return os.path.join(self.model_settings.data_path,category.replace(" ","_"))
    
    def get_count(self,category: str) -> int:
        value = len(os.listdir(self.category_path(category)))
        self.counts[category] = value
        return value

    def _generate_counts(self):
        for category in self.model_settings.categories:
            self.get_count(category)

    def _make_folders(self):
        for category in self.model_settings.categories:
            try:
                os.makedirs(self.category_path(category))
            except FileExistsError:
                pass
            except Exception as ex:
                print(ex)
                raise ex
    
    def collect(self, category: str, image: Image) -> int:
        if category in self.model_settings.categories:
            pth = os.path.join(
                self.category_path(category),
                str(uuid1())+".jpg"
                )
            with open(pth, 'wb') as f:
                f.write(image.value)
            
            return self.get_count(category)
        
        return -1


