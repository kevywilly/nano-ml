#!/usr/bin/python3

from src.trainer import Trainer
from settings import settings
import os
import argparse

parser = argparse.ArgumentParser(description="Train for obstacle avoidance.")
parser.add_argument("-e","--epochs", type=int, default=30, required=False, help="number of epochs")
parser.add_argument("-r","--retrain", action="store_true", help="retrain the network")
parser.add_argument("-p", "--train_pct", type=float, required=False, help="pct of data to use for training dataset i.e., 50, 60, etc.")
parser.add_argument("-m","--momentum", type=float, required=False, default=0.9, help="momentum")
parser.add_argument("-l", "--learning_rate", type=float, required=False, default=0.001, help="momentum")

parser.add_argument("--camera", type=int, required=False, default=1, help="train using images from camera by index i.e., 1, 2.")

retrain = os.path.exists(settings.default_model.get_best_model_path())

args = parser.parse_args()
print(args)
if args.epochs:
    epochs = args.epochs
else:
    epochs = settings.default_retrain_epochs if retrain else settings.default_epochs

tp = args.train_pct / 100.0 if args.train_pct else 0.60

print(f"training with max {epochs} epochs.")

trainer = Trainer.instance(
    config=settings.default_model,
    epochs=epochs,
    retrain=retrain,
    cam_index=args.camera,
    train_pct=tp,
    learning_rate=args.learning_rate,
    momentum=args.momentum
)

trainer.train()
