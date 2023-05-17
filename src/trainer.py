
import torch
import torch.optim as optim
import torch.nn.functional as F
import torchvision.datasets as datasets
import torchvision.models as models
import torchvision.transforms as transforms
from config import TrainingConfig, MODELS_ROOT
import traitlets

torch.hub.set_dir(MODELS_ROOT)


class Trainer(traitlets.HasTraits):

    training_config = traitlets.Instance(TrainingConfig)

    def __init__(self, training_config: TrainingConfig, retrain = False):
        self.training_config = training_config
        self.retrain = retrain
        self.model = training_config.load_model(pretrained=(not retrain))

        

    def train(self):

        print("loading datasets...")

        dataset = datasets.ImageFolder(
        self.training_config.get_data_path(),
        transforms.Compose([
            transforms.ColorJitter(0.1, 0.1, 0.1, 0.1),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ]))
    
        data_set_len = len(dataset)
        test_len = int(data_set_len/3)
        print(f"found {data_set_len} datapoints.")
            
        train_dataset, test_dataset = torch.utils.data.random_split(dataset, [len(dataset) - test_len, test_len])

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

        print(f"loading model...{self.training_config.model_name}")

        num_cats = len(self.training_config.categories)


        print(f"Categories: {num_cats}")
        if self.training_config.model_name == "alexnet":
            self.model.classifier[6] = torch.nn.Linear(self.model.classifier[6].in_features, num_cats)
        elif self.training_config.model_name == "resnet18":
            self.model.fc = torch.nn.Linear(512, num_cats)

        print("training model...")

        BEST_MODEL_PATH = self.training_config.get_best_model_path()
        NUM_EPOCHS = 30
        best_accuracy = 0.0
        
        print(f"best model path: {BEST_MODEL_PATH}")

        if self.retrain:
            self.model.load_state_dict(torch.load(BEST_MODEL_PATH))

        device = torch.device('cuda')
        self.model = self.model.to(device)

        optimizer = optim.SGD(self.model.parameters(), lr=0.001, momentum=0.9)

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