#!/usr/bin/python3
from src.wanderer import Wanderer
from src.robot import Robot
from config import TrainingConfig, Obstacle2dConfig, Obstacle3dConfig
from settings import settings

robot = Robot()

application = Wanderer.instance(robot=robot)
application.start()