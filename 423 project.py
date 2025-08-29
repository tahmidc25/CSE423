from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

camera_pos = (0, 500, 500)
camera_rotation = 0  # For 360-degree ground rotation
fovY = 120
GRID_LENGTH = 500
rand_var = 423

# Game state
car_x = 0
car_z = 0
car_angle = 0
car_speed = 0
max_speed = 8
acceleration = 0.5
friction = 0.9
turn_speed = 3

collision_detected = False
reset_timer = 0
camera_mode = 1  # 1: behind car, 2: top-down, 3: side view
game_over = False

# Obstacles (x, z, width, depth, height)
obstacles = [
    [200, 200, 40, 80, 30],   # Parking barriers
    [-200, 200, 40, 80, 30],
    [200, -200, 40, 80, 30],
    [-200, -200, 40, 80, 30],
    [0, 300, 100, 40, 25],    # Building walls
    [300, 0, 40, 100, 25],
    [-300, 0, 40, 100, 25],
    [0, -300, 100, 40, 25],
    [150, 0, 30, 30, 20],     # Small obstacles
    [-150, 50, 30, 30, 20],
    [50, -150, 30, 30, 20],
]

def init_game():
    global car_x, car_z, car_angle, car_speed, collision_detected, reset_timer, game_over, camera_rotation
    
    car_x = 0
    car_z = 0
    car_angle = 0
    car_speed = 0
    collision_detected = False
    reset_timer = 0
    game_over = False
    camera_rotation = 0

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    # Draw the car
    glPushMatrix()
    
    glTranslatef(car_x, car_z, 0)
    glRotatef(car_angle, 0, 0, 1)
    
    # Car body (main chassis)
    glColor3f(0.8, 0.2, 0.2)  # Red car
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glScalef(60, 25, 15)
    glutSolidCube(1)
    glPopMatrix()
    
    # Car roof
    glColor3f(0.9, 0.3, 0.3)
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glScalef(40, 20, 10)
    glutSolidCube(1)
    glPopMatrix()
    
    # Front bumper
    glColor3f(0.7, 0.7, 0.7)
    glPushMatrix()
    glTranslatef(32, 0, 10)
    glScalef(4, 30, 8)
    glutSolidCube(1)
    glPopMatrix()
    
    # Rear bumper
    glPushMatrix()
    glTranslatef(-32, 0, 10)
    glScalef(4, 30, 8)
    glutSolidCube(1)
    glPopMatrix()
    
    # Wheels
    glColor3f(0.1, 0.1, 0.1)  # Black wheels
    
    # Front left wheel
    glPushMatrix()
    glTranslatef(20, 18, 8)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 6, 8, 8)
    glPopMatrix()
    
    # Front right wheel
    glPushMatrix()
    glTranslatef(20, -18, 8)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 6, 8, 8)
    glPopMatrix()
    
    # Rear left wheel
    glPushMatrix()
    glTranslatef(-20, 18, 8)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 6, 8, 8)
    glPopMatrix()
    
    # Rear right wheel
    glPushMatrix()
    glTranslatef(-20, -18, 8)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 6, 8, 8)
    glPopMatrix()
    
    # Headlights
    glColor3f(1, 1, 0.8)  # Yellow lights
    glPushMatrix()
    glTranslatef(30, 10, 15)
    glutSolidSphere(3, 8, 8)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(30, -10, 15)
    glutSolidSphere(3, 8, 8)
    glPopMatrix()
    
    glPopMatrix()

def draw_enemies():
    # Draw obstacles instead of enemies
    for obstacle in obstacles:
        x, z, width, depth, height = obstacle
        
        glPushMatrix()
        glTranslatef(x, z, height/2)
        
        # Different colors for different obstacle types
        if width == 40 and depth == 80:  # Parking barriers
            glColor3f(1, 1, 0)  # Yellow
        elif width == 100 or depth == 100:  # Building walls
            glColor3f(0.6, 0.6, 0.6)  # Gray
        else:  # Small obstacles
            glColor3f(0.8, 0.4, 0.2)  # Orange
            
        glScalef(width, depth, height)
        glutSolidCube(1)
        glPopMatrix()

def draw_bullets():
    # Draw parking spots instead of bullets
    glColor3f(1, 1, 1)  # White lines
    glLineWidth(3)
    
    # Parking spaces
    parking_spots = [
        [150, 150], [250, 150], [350, 150],
        [-150, 150], [-250, 150], [-350, 150],
        [150, -150], [250, -150], [350, -150],
        [-150, -150], [-250, -150], [-350, -150],
    ]
    
    for spot_x, spot_z in parking_spots:
        glBegin(GL_LINE_LOOP)
        glVertex3f(spot_x - 40, spot_z - 25, 1)
        glVertex3f(spot_x + 40, spot_z - 25, 1)
        glVertex3f(spot_x + 40, spot_z + 25, 1)
        glVertex3f(spot_x - 40, spot_z + 25, 1)
        glEnd()

def draw_grid():
    square_size = 100  
    
    glBegin(GL_QUADS)
    
    for i in range(-GRID_LENGTH, GRID_LENGTH, square_size):
        for j in range(-GRID_LENGTH, GRID_LENGTH, square_size):
            
            square_x = (i + GRID_LENGTH) // square_size
            square_z = (j + GRID_LENGTH) // square_size
            
            # Chess pattern
            if (square_x + square_z) % 2 == 0:
                glColor3f(0.3, 0.3, 0.3)  # Dark gray
            else:
                glColor3f(0.5, 0.5, 0.5)  # Light gray
            
            glVertex3f(i, j, 0)
            glVertex3f(i + square_size, j, 0)
            glVertex3f(i + square_size, j + square_size, 0)
            glVertex3f(i, j + square_size, 0)
    
    glEnd()
    
    # Boundary walls
    wall_height = 50
    
    # North wall
    glColor3f(0.2, 0.2, 0.8)  
    glPushMatrix()
    glTranslatef(0, GRID_LENGTH, wall_height/2)
    glScalef(GRID_LENGTH * 2, 10, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    # South wall  
    glColor3f(0.2, 0.8, 0.2)  
    glPushMatrix()
    glTranslatef(0, -GRID_LENGTH, wall_height/2)
    glScalef(GRID_LENGTH * 2, 10, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    # East wall 
    glColor3f(0.8, 0.2, 0.2)  
    glPushMatrix()
    glTranslatef(GRID_LENGTH, 0, wall_height/2)
    glScalef(10, GRID_LENGTH * 2, wall_height)
    glutSolidCube(1)
    glPopMatrix()
    
    # West wall 
    glColor3f(0.8, 0.8, 0.2)  
    glPushMatrix()
    glTranslatef(-GRID_LENGTH, 0, wall_height/2)
    glScalef(10, GRID_LENGTH * 2, wall_height)
    glutSolidCube(1)
    glPopMatrix()

def check_collision(new_x, new_z):
    """Check if car collides with obstacles or walls"""
    car_width = 60
    car_depth = 25
    
    # Check boundary walls
    if (abs(new_x) > GRID_LENGTH - car_width/2 or 
        abs(new_z) > GRID_LENGTH - car_depth/2):
        return True
    
    # Check obstacles
    for obstacle in obstacles:
        obs_x, obs_z, obs_width, obs_depth, obs_height = obstacle
        
        # Simple bounding box collision
        if (abs(new_x - obs_x) < (car_width + obs_width)/2 and
            abs(new_z - obs_z) < (car_depth + obs_depth)/2):
            return True
    
    return False

def update_bullets():
    # Update car physics instead of bullets
    global car_x, car_z, car_speed, collision_detected, reset_timer
    
    if reset_timer > 0:
        reset_timer -= 1
        collision_detected = reset_timer > 0
        return
    
    # Apply friction
    car_speed *= friction
    
    # Calculate new position
    if abs(car_speed) > 0.1:
        angle_rad = math.radians(car_angle)
        new_x = car_x + math.cos(angle_rad) * car_speed
        new_z = car_z + math.sin(angle_rad) * car_speed
        
        # Check for collisions
        if not check_collision(new_x, new_z):
            car_x = new_x
            car_z = new_z
            collision_detected = False
        else:
            # Stop the car and show collision
            car_speed = 0
            collision_detected = True
            reset_timer = 60  # Show collision for 1 second

def update_enemies():
    # Draw collision effect instead of updating enemies
    if collision_detected:
        glPushMatrix()
        glTranslatef(car_x, car_z, 40)
        
        # Flashing red effect
        if (reset_timer // 5) % 2 == 0:  # Flash every 5 frames
            glColor3f(1, 0, 0)
        else:
            glColor3f(1, 0.5, 0.5)
            
        glutSolidSphere(80, 8, 8)
        glPopMatrix()

def fire_bullet():
    # Not used in parking game
    pass

def cheat_mode_update():
    # Not used in parking game
    pass

def keyboardListener(key, x, y):
    global car_speed, car_angle, camera_mode, collision_detected
    
    if collision_detected and reset_timer <= 0:
        return
    
    # Car movement controls
    if key == b'w':  # Forward
        car_speed = min(car_speed + acceleration, max_speed)
    elif key == b's':  # Backward
        car_speed = max(car_speed - acceleration, -max_speed/2)
    elif key == b'a' and abs(car_speed) > 0.5:  # Turn left (only when moving)
        car_angle += turn_speed * (car_speed / max_speed)
        if car_angle >= 360:
            car_angle -= 360
    elif key == b'd' and abs(car_speed) > 0.5:  # Turn right (only when moving)
        car_angle -= turn_speed * (car_speed / max_speed)
        if car_angle < 0:
            car_angle += 360
    
    # Reset position
    elif key == b'r':
        init_game()
    
    # Camera controls
    elif key == b'1':
        camera_mode = 1  # Behind car
    elif key == b'2':
        camera_mode = 2  # Top-down
    elif key == b'3':
        camera_mode = 3  # Side view

def specialKeyListener(key, x, y):
    global camera_pos
    
    # Only allow camera movement in third person mode
    if camera_mode != 1:
        return
        
    x, y, z = camera_pos
    
    if key == GLUT_KEY_UP:
        z += 20

    if key == GLUT_KEY_DOWN:
        z -= 20

    if key == GLUT_KEY_LEFT:
        distance = math.sqrt(x**2 + y**2)
        if distance > 0:
            current_angle = math.atan2(y, x)
            new_angle = current_angle + math.radians(5)
            
            x = distance * math.cos(new_angle)
            y = distance * math.sin(new_angle)
  
    if key == GLUT_KEY_RIGHT:
        distance = math.sqrt(x**2 + y**2)
        if distance > 0:
            current_angle = math.atan2(y, x)
            new_angle = current_angle - math.radians(5)
            
            x = distance * math.cos(new_angle)
            y = distance * math.sin(new_angle)

    camera_pos = (x, y, z)

def mouseListener(button, state, x, y):
    global camera_rotation
    
    # Rotate ground 360 degrees with mouse buttons
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        camera_rotation += 15  # Rotate left
        if camera_rotation >= 360:
            camera_rotation -= 360
    
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        camera_rotation -= 15  # Rotate right
        if camera_rotation < 0:
            camera_rotation += 360

def setupCamera():
    global camera_mode, camera_rotation
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if camera_mode == 1:  # Behind car view
        angle_rad = math.radians(car_angle)
        cam_x = car_x - math.cos(angle_rad) * 150
        cam_z = car_z - math.sin(angle_rad) * 150
        cam_y = 80  # Height behind car
        
        target_x = car_x + math.cos(angle_rad) * 50
        target_z = car_z + math.sin(angle_rad) * 50
        
        gluLookAt(cam_x, cam_z, cam_y,
                  target_x, target_z, 15,
                  0, 0, 1)
                  
    elif camera_mode == 2:  # Top-down view
        gluLookAt(car_x, car_z, 400,
                  car_x, car_z, 0,
                  0, 1, 0)
                  
    elif camera_mode == 3:  # Side view
        gluLookAt(car_x + 200, car_z, 100,
                  car_x, car_z, 15,
                  0, 0, 1)
    
    # Apply 360-degree rotation for third person perspective
    if camera_mode == 1:  # Only rotate in behind car mode for 360 view
        glTranslatef(0, 0, 0)
        glRotatef(camera_rotation, 0, 0, 1)
        glTranslatef(0, 0, 0)

def idle():
    if not game_over:
        update_bullets()  # Updates car physics
        update_enemies()  # Draws collision effects
        
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)

    setupCamera()
    draw_grid()
    draw_bullets()  # Draws parking spots
    draw_enemies()  # Draws obstacles
    
    if not game_over:
        draw_player()
        update_enemies()  # Draw collision effects

    # UI Display
    camera_names = ["", "Behind Car", "Top-Down", "Side View"]
    draw_text(10, 770, f"Camera: {camera_names[camera_mode]} (1-3)")
    draw_text(10, 740, f"Speed: {abs(car_speed):.1f}")
    draw_text(10, 710, f"Position: ({car_x:.0f}, {car_z:.0f})")
    draw_text(10, 680, f"Angle: {car_angle:.0f}°")
    draw_text(10, 650, f"Ground Rotation: {camera_rotation:.0f}°")
    
    if collision_detected:
        draw_text(10, 620, "COLLISION! Press R to reset")
    
    # Controls help
    draw_text(10, 180, "Controls:")
    draw_text(10, 150, "W/S: Forward/Backward")
    draw_text(10, 120, "A/D: Turn Left/Right")
    draw_text(10, 90, "1/2/3: Camera Views")
    draw_text(10, 60, "R: Reset Position")
    draw_text(10, 30, "Mouse: Rotate Ground 360°")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"Car Parking 3D - Practice Game")
  
    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    
    # Set background color
    glClearColor(0.1, 0.1, 0.2, 1.0)
    
    init_game()

    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)

    print("=== 3D Car Parking Game ===")
    print("Controls:")
    print("W/S: Move Forward/Backward")
    print("A/D: Turn Left/Right (only when moving)")
    print("1/2/3: Switch camera views")
    print("R: Reset car position")
    print("Left Click: Rotate ground left")
    print("Right Click: Rotate ground right")
    print("\nObjective: Practice parking without hitting obstacles!")

    glutMainLoop()

if __name__ == "__main__":
    main()


