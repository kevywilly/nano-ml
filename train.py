#!/usr/bin/python3

from src.trainer import Trainer
from settings import settings
from config import Navigate2dConfig,Obstacle2dConfig, Obstacle3dConfig

trainer = Trainer(training_config=settings.default_model, retrain=settings.retrain_model)

trainer.train()
