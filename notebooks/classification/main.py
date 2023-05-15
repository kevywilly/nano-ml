import torch
import torchvision
import cv2
from PIL import Image
from torchvision import transforms
from typing import List
import PIL
from categories import _IMAGENET_CATEGORIES
from settings import settings

torch.hub.set_dir(settings.default_model.model_path)

# Define transforms to preprocess the image
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# Load the ResNet-18 pre-trained model
model = torchvision.models.resnet18(pretrained=True)
model.eval()
    
def get_image_tensor(filename):
    image = cv2.imread(f"images/{filename}", cv2.COLOR_BGR2RGB)
    image = PIL.Image.fromarray(image)
    return transform(image)

def predict(filename):
    
    input_batch = get_image_tensor(filename).unsqueeze(0) # create a mini-batch as expected by the model
    input_batch = input_batch.to('cuda')
    model.to('cuda')

    
    with torch.no_grad():
        output = model(input_batch)
        
    _, predicted = torch.topk(output, 2)
    
    print("-------------------------------------------------")
    print(filename)
    print("-------------------------------------------------")
    for num in predicted[0]:
        print('Predicted class: ', _IMAGENET_CATEGORIES[num])
        
    print("")
    
    return predicted

if __name__ == "__main__":
    print("")
    predicted = predict("image.jpg")
    predicted = predict("car.jpg")
    predicted = predict("horse.jpg")
    predicted = predict("cow.jpg")