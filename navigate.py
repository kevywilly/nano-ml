#!/usr/bin/python3

from src.navigator import Navigator
from src.robot import Robot
from config import TrainingConfig, Obstacle2dConfig, Obstacle3dConfig

robot = Robot()

application = Navigator(robot=robot)
application.start()