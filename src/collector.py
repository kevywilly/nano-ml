import traitlets
from typing import List
from uuid import uuid1
import os
from src.image import Image

class ImageCollector(traitlets.HasTraits):

    counts = traitlets.Dict()
    categories = traitlets.List(trait=traitlets.Unicode())
    data_path = traitlets.Unicode(allow_none=False)
    
    def __init__(self, categories: List[str], data_path: str, *args, **kwargs):
        super(ImageCollector, self).__init__(*args, **kwargs)
        self.categories = categories
        self.data_path = data_path
        self._make_folders()
        self._generate_counts()

    def category_path(self, category: str) -> str:
        return os.path.join(self.data_path,category.replace(" ","_"))
    
    def get_count(self,category: str) -> int:
        value = len(os.listdir(self.category_path(category)))
        self.counts[category] = value
        return value

    def _generate_counts(self):
        for category in self.categories:
            self.get_count(category)

    def _make_folders(self):
        for category in self.categories:
            try:
                os.makedirs(self.category_path(category))
            except FileExistsError:
                pass
            except Exception as ex:
                print(ex)
                raise ex
    
    def collect(self, category: str, image: Image) -> int:
        if category in self.categories:
            pth = os.path.join(
                self.category_path(category),
                str(uuid1())+".jpg"
                )
            with open(pth, 'wb') as f:
                f.write(image.value)
            
            return self.get_count(category)
        
        return -1


