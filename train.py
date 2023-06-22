#!/usr/bin/python3

from src.trainer import Trainer
from settings import settings
import os

retrain = os.path.exists(settings.default_model.get_best_model_path())

trainer = Trainer.instance(
    config=settings.default_model,
    epochs=settings.default_retrain_epochs if retrain else settings.default_epochs,
    retrain=retrain
)

trainer.train()
