import pygame
import math
import numpy as np

# --- Constants ---
WIDTH, HEIGHT = 800, 800
FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# --- Ball Class ---
class Ball:
    def __init__(self, x, y, radius, color, gravity, friction):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = gravity
        self.friction = friction

    def update(self):
        # Apply gravity
        self.vel_y += self.gravity

        # Apply friction
        self.vel_x *= self.friction
        self.vel_y *= self.friction

        # Update position
        self.x += self.vel_x
        self.y += self.vel_y

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

# --- Hexagon Class ---
class Hexagon:
    def __init__(self, center_x, center_y, size, color):
        self.center_x = center_x
        self.center_y = center_y
        self.size = size
        self.color = color
        self.angle = 0
        self.points = self.get_initial_points()

    def get_initial_points(self):
        points = []
        for i in range(6):
            angle_rad = math.pi / 3 * i
            x = self.center_x + self.size * math.cos(angle_rad)
            y = self.center_y + self.size * math.sin(angle_rad)
            points.append((x, y))
        return points

    def rotate(self, rotation_speed):
        self.angle += rotation_speed
        rad_angle = math.radians(self.angle)
        
        # Rotation matrix
        rotation_matrix = np.array([
            [math.cos(rad_angle), -math.sin(rad_angle)],
            [math.sin(rad_angle), math.cos(rad_angle)]
        ])
        
        new_points = []
        for point in self.points:
            # Translate point to origin
            translated_point = np.array([point[0] - self.center_x, point[1] - self.center_y])
            # Apply rotation
            rotated_point = np.dot(rotation_matrix, translated_point)
            # Translate back
            new_x = rotated_point[0] + self.center_x
            new_y = rotated_point[1] + self.center_y
            new_points.append((new_x, new_y))
            
        self.rotated_points = new_points

    def draw(self, screen):
        pygame.draw.polygon(screen, self.color, self.rotated_points, 5)

# --- Collision Functions ---
def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def normalize(v):
    mag = math.sqrt(v[0]**2 + v[1]**2)
    return (v[0] / mag, v[1] / mag)

def handle_collision(ball, hexagon):
    # Iterate through each edge of the hexagon
    for i in range(6):
        p1 = hexagon.rotated_points[i]
        p2 = hexagon.rotated_points[(i + 1) % 6]

        # Get edge vector
        edge_vec = (p2[0] - p1[0], p2[1] - p1[1])
        # Get vector from p1 to ball
        p1_to_ball = (ball.x - p1[0], ball.y - p1[1])

        # Project p1_to_ball onto the edge
        edge_len_sq = dot(edge_vec, edge_vec)
        if edge_len_sq == 0:
            continue
        
        t = dot(p1_to_ball, edge_vec) / edge_len_sq
        t = max(0, min(1, t))

        # Closest point on the edge to the ball
        closest_point_x = p1[0] + t * edge_vec[0]
        closest_point_y = p1[1] + t * edge_vec[1]
        
        # Distance from ball to closest point
        dist_x = ball.x - closest_point_x
        dist_y = ball.y - closest_point_y
        distance = math.sqrt(dist_x**2 + dist_y**2)
        
        # Check for collision
        if distance < ball.radius:
            # Calculate the collision normal vector
            normal = normalize((-edge_vec[1], edge_vec[0]))
            
            # Use dot product for reflection
            dot_product = dot((ball.vel_x, ball.vel_y), normal)
            
            # Reflect velocity
            reflected_vel_x = ball.vel_x - 2 * dot_product * normal[0]
            reflected_vel_y = ball.vel_y - 2 * dot_product * normal[1]

            # Update ball's velocity with a little extra kick to prevent sticking
            ball.vel_x = reflected_vel_x * 0.95 
            ball.vel_y = reflected_vel_y * 0.95
            
            # Nudge the ball away to prevent it from getting stuck
            overlap = ball.radius - distance
            ball.x += normal[0] * overlap
            ball.y += normal[1] * overlap

# --- Main Program ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Ball in a Spinning Hexagon")
    clock = pygame.time.Clock()

    # Create ball and hexagon
    ball = Ball(WIDTH // 2, HEIGHT // 2, 15, RED, gravity=0.5, friction=0.995)
    hexagon = Hexagon(WIDTH // 2, HEIGHT // 2, 300, WHITE)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update and rotate
        ball.update()
        hexagon.rotate(0.5)  # Rotate at 0.5 degrees per frame
        handle_collision(ball, hexagon)

        # Drawing
        screen.fill(BLACK)
        hexagon.draw(screen)
        ball.draw(screen)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()