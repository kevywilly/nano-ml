#!/usr/bin/python3
from src.wanderer import Wanderer
from src.robot import Robot
from config import TrainingConfig, Obstacle2dConfig, Obstacle3dConfig

robot = Robot()

application = Wanderer(robot=robot, training_config = Obstacle3dConfig)
application.start()