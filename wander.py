#!/usr/bin/python3
from src.wanderer import Wanderer
from src.robot import Robot
from settings import settings

robot = Robot()

application = Wanderer(robot=robot, model_settings = settings.default_model)
application.start()