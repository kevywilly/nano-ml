#!/usr/bin/python3

from src.trainer import Trainer
from settings import settings

trainer = Trainer(model_settings=settings.default_model, retrain=True)

trainer.train()