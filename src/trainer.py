
import torch
import torch.optim as optim
import torch.nn.functional as F
import torchvision
import torchvision.datasets as datasets
import torchvision.models as models
import torchvision.transforms as transforms
from settings import settings as app_settings
from settings import ModelSettings
from src.collector import ImageCollector
import traitlets

torch.hub.set_dir(app_settings.default_model.model_path)


class Trainer(traitlets.HasTraits):

    model_settings = traitlets.Instance(ModelSettings)

    def __init__(self, model_settings: ModelSettings, retrain = False):
        self.model_settings = model_settings
        self.retrain = retrain
        self.model = model_settings.load_model(pretrained=(not retrain))

        

    def train(self):

        image_collector = ImageCollector(app_settings.default_model)

        print("loading datasets...")

        dataset = datasets.ImageFolder(
        self.model_settings.data_path,
        transforms.Compose([
            transforms.ColorJitter(0.1, 0.1, 0.1, 0.1),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]))

        counts = image_collector.counts
    
        data_set_len = int(sum(counts.values())/2)
        print(f"found {data_set_len} datapoints.")
            
        train_dataset, test_dataset = torch.utils.data.random_split(dataset, [len(dataset) - data_set_len, data_set_len])

        train_loader = torch.utils.data.DataLoader(
            train_dataset,
            batch_size=8,
            shuffle=True,
            num_workers=0
        )

        test_loader = torch.utils.data.DataLoader(
            test_dataset,
            batch_size=8,
            shuffle=True,
            num_workers=0
        )

        print(f"loading model...{self.model_settings.model_name}")

        num_cats = len(self.model_settings.categories)

        if self.model_settings.model_name == "alexnet":
            self.model.classifier[6] = torch.nn.Linear(self.model.classifier[6].in_features, num_cats)
        elif self.model_settings.model_name == "resnet18":
            self.model.fc = torch.nn.Linear(512, num_cats)

        print("training model...")

        if self.retrain:
            self.model.load_state_dict(torch.load(self.model_settings.best_model_path))

        device = torch.device('cuda')
        self.model = self.model.to(device)

        NUM_EPOCHS = 60
        BEST_MODEL_PATH = self.model_settings.best_model_path
        best_accuracy = 0.0

        optimizer = optim.SGD(self.model.parameters(), lr=0.001, momentum=0.6)

        for epoch in range(NUM_EPOCHS):
            
            for images, labels in iter(train_loader):
                images = images.to(device)
                labels = labels.to(device)
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = F.cross_entropy(outputs, labels)
                loss.backward()
                optimizer.step()
            
            test_error_count = 0.0
            for images, labels in iter(test_loader):
                images = images.to(device)
                labels = labels.to(device)
                outputs = self.model(images)
                test_error_count += float(torch.sum(torch.abs(labels - outputs.argmax(1))))
            
            test_accuracy = 1.0 - float(test_error_count) / float(len(test_dataset))
            print('%d: %f' % (epoch, test_accuracy))
            if test_accuracy > best_accuracy:
                torch.save(self.model.state_dict(), BEST_MODEL_PATH)
                best_accuracy = test_accuracy





if __name__ == "__main__":
    print("hello")