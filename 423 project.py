from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random 

camera_mode = 1  # 1: behind car, 2: top-down, 3: side view
fovY = 60
GRID_SIZE = 800

# Car properties
car_x = 0
car_z = 0
car_angle = 0
car_speed = 0
max_speed = 8
acceleration = 0.5
friction = 0.9
turn_speed = 3

