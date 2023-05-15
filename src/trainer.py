
import torch
import torch.optim as optim
import torch.nn.functional as F
import torchvision
import torchvision.datasets as datasets
import torchvision.models as models
import torchvision.transforms as transforms
from settings import ModelSettings
from src.collector import ImageCollector

torch.hub.set_dir(settings.default_model.model_path)


class Trainer:

    def __init__(self, model_settings: ModelSettings):
        self.model_settings = ModelSettings
        self.model = model_settings.get_model()

    def train(self):

        image_collector = ImageCollector(model_settings=self.model_settings)

        dataset = datasets.ImageFolder(
        self.model_settings.data_path,
        transforms.Compose([
            transforms.ColorJitter(0.1, 0.1, 0.1, 0.1),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]))

        counts = image_collector.counts()
        data_set_len = sum(counts.values)/2
            
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

        if self.model_name == "alexnet":
            self.model.classifier[6] = torch.nn.Linear(model.classifier[6].in_features, len(self.model_settings))
        elif self.model_name == "resnet18":
            self.model.fc = torch.nn.Linear(512, 2)

        device = torch.device('cuda')
        model = model.to(device)

        NUM_EPOCHS = 30
        BEST_MODEL_PATH = self.model_settings.best_model_path
        best_accuracy = 0.0

        optimizer = optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

        for epoch in range(NUM_EPOCHS):
            
            for images, labels in iter(train_loader):
                images = images.to(device)
                labels = labels.to(device)
                optimizer.zero_grad()
                outputs = model(images)
                loss = F.cross_entropy(outputs, labels)
                loss.backward()
                optimizer.step()
            
            test_error_count = 0.0
            for images, labels in iter(test_loader):
                images = images.to(device)
                labels = labels.to(device)
                outputs = model(images)
                test_error_count += float(torch.sum(torch.abs(labels - outputs.argmax(1))))
            
            test_accuracy = 1.0 - float(test_error_count) / float(len(test_dataset))
            print('%d: %f' % (epoch, test_accuracy))
            if test_accuracy > best_accuracy:
                torch.save(model.state_dict(), BEST_MODEL_PATH)
                best_accuracy = test_accuracy





