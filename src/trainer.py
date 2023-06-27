import atexit

import torch
import torch.nn.functional as F
import torch.optim as optim
import torchvision.datasets as datasets
import torchvision.transforms as transforms
import traitlets
from traitlets.config import SingletonConfigurable
from settings import settings
from src.config import TrainingConfig, MODELS_ROOT
import os

torch.hub.set_dir(MODELS_ROOT)

class Trainer(SingletonConfigurable):
    config = traitlets.Instance(TrainingConfig, default_value=settings.default_model).tag(config=True)
    epochs = traitlets.Int(default_value=settings.default_epochs).tag(config=True)
    retrain = traitlets.Bool(default_value=False).tag(config=True)
    cam_index = traitlets.Int(defalt_value=1).tag(config=True)
    train_pct = traitlets.Float(default_value=0.6).tag(config=True)
    learning_rate = traitlets.Float(default_value=0.005).tag(config=True)
    momentum = traitlets.Float(default_value=0.9).tag(config=True)

    def __init__(self, *args, **kwargs):
        super(Trainer, self).__init__(*args, **kwargs)
        print(f"Trainer loaded: {self.config}, epochs: {self.epochs}, retrain: {self.retrain}")
        print(f"cam index = {self.cam_index}")
        
        self.model = self.config.load_model(pretrained=True)

        atexit.register(self.clear_cuda)

    @staticmethod
    def clear_cuda():
        torch.cuda.empty_cache()

    def train(self):

        print("loading datasets...")

        print(f"using path {self.config.get_data_path(self.cam_index)} for training data.")
        dataset = datasets.ImageFolder(
            self.config.get_data_path(self.cam_index),
            transforms.Compose([
                transforms.ColorJitter(0.1, 0.1, 0.1, 0.1),
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
            ]))

        datapoints = len(dataset)
        train_size = int(self.train_pct * datapoints)
        test_size = datapoints - train_size

        print(f"found {datapoints} datapoints.")

        train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size,test_size])

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

        print(f"loading model...{self.config.model_name}")

        num_cats = len(self.config.categories)

        print(f"Categories: {num_cats}")
        if self.config.model_name == "alexnet":
            self.model.classifier[6] = torch.nn.Linear(self.model.classifier[6].in_features, num_cats)
        elif self.config.model_name == "resnet18":
            self.model.fc = torch.nn.Linear(512, num_cats)

        print("training model...")

        BEST_MODEL_PATH = self.config.get_best_model_path(self.cam_index)

        NUM_EPOCHS = self.epochs
        best_accuracy = 0.0
        test_accuracy = 0.0
        goal = 0.98
        round = 0
        
        while test_accuracy < goal:

            print(f"============ ROUND {round}")

            if os.path.isfile(BEST_MODEL_PATH):
                print(f"loading best model from {BEST_MODEL_PATH}")
                self.model.load_state_dict(torch.load(BEST_MODEL_PATH))

            device = torch.device('cuda')
            self.model = self.model.to(device)

            optimizer = optim.SGD(self.model.parameters(), lr=self.learning_rate, momentum=self.momentum)

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
                    #test_error_count += float(torch.sum(torch.abs(labels - outputs.argmax(1))))
                    err = len(torch.nonzero(outputs.argmax(1) - labels).flatten())
                    test_error_count += err

                print(f"error_count: {test_error_count}, dataset_len: {len(test_dataset)}")

                test_accuracy = 1.0 - float(test_error_count) / float(len(test_dataset))
                print('%d: %f' % (epoch, test_accuracy))
                if test_accuracy > best_accuracy:
                    torch.save(self.model.state_dict(), BEST_MODEL_PATH)
                    best_accuracy = test_accuracy

                if test_accuracy >= goal:
                    print(f"Goal reached: {test_accuracy}")
                    break


if __name__ == "__main__":
    print("Hello Trainer")
