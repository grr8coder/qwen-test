"""
Gravity Minigame - A 2D Pygame exploration of gravity mechanics

Controls:
- Click and drag to launch the ball
- Press 'R' to reset the ball
- Press 'SPACE' to toggle gravity on/off
- Press 'UP/DOWN' arrows to adjust gravity strength
- Press 'ESC' to quit

Features:
- Adjustable gravity strength
- Ball bouncing with energy loss
- Visual trajectory prediction
- Multiple platforms to bounce on
"""

import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Minigame")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60


class Ball:
    def __init__(self, x, y, radius=20):
        self.x = x
        self.y = y
        self.radius = radius
        self.vx = 0
        self.vy = 0
        self.gravity = 0.5
        self.bounce_factor = 0.7  # Energy retained after bounce
        self.is_gravity_on = True
        self.trail = []  # Store previous positions for visual effect
        self.max_trail_length = 50

    def update(self, platforms):
        # Apply gravity if enabled
        if self.is_gravity_on:
            self.vy += self.gravity

        # Update position
        self.x += self.vx
        self.y += self.vy

        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

        # Apply friction
        self.vx *= 0.995
        self.vy *= 0.995

        # Check collision with platforms
        self.check_platform_collisions(platforms)

        # Check boundary collisions
        self.check_boundary_collisions()

    def check_platform_collisions(self, platforms):
        for platform in platforms:
            # Simple AABB collision detection
            if (self.x + self.radius > platform.x and 
                self.x - self.radius < platform.x + platform.width and
                self.y + self.radius > platform.y and 
                self.y - self.radius < platform.y + platform.height):
                
                # Determine collision side
                dx = self.x - (platform.x + platform.width / 2)
                dy = self.y - (platform.y + platform.height / 2)
                
                width = (platform.width + self.radius * 2) / 2
                height = (platform.height + self.radius * 2) / 2
                
                cross_width = width * dy
                cross_height = height * dx
                
                if abs(cross_width) > abs(cross_height):
                    # Horizontal collision
                    if cross_width > 0:
                        self.x = platform.x + platform.width + self.radius
                    else:
                        self.x = platform.x - self.radius
                    self.vx *= -self.bounce_factor
                else:
                    # Vertical collision
                    if cross_height > 0:
                        self.y = platform.y + platform.height + self.radius
                    else:
                        self.y = platform.y - self.radius
                        # Only bounce if moving downward (hitting top of platform)
                        if self.vy > 0:
                            self.vy *= -self.bounce_factor
                        else:
                            self.vy = 0

    def check_boundary_collisions(self):
        # Left boundary
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -self.bounce_factor
        
        # Right boundary
        if self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -self.bounce_factor
        
        # Top boundary
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -self.bounce_factor
        
        # Bottom boundary
        if self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -self.bounce_factor

    def draw(self, surface):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_radius = max(1, int(self.radius * (i / len(self.trail))))
            color = (BLUE[0], BLUE[1], BLUE[2])
            pygame.draw.circle(surface, color, (int(pos[0]), int(pos[1])), trail_radius)
        
        # Draw ball
        pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), self.radius, 2)

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.trail = []

    def set_velocity(self, vx, vy):
        self.vx = vx
        self.vy = vy


class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, BLACK, (self.x, self.y, self.width, self.height), 2)


def draw_trajectory(ball, mouse_pos, start_pos):
    """Draw predicted trajectory based on launch velocity"""
    points = []
    vx = (start_pos[0] - mouse_pos[0]) * 0.15
    vy = (start_pos[1] - mouse_pos[1]) * 0.15
    
    sim_x, sim_y = start_pos
    sim_vx, sim_vy = vx, vy
    
    for _ in range(30):
        points.append((sim_x, sim_y))
        sim_vy += ball.gravity
        sim_x += sim_vx
        sim_y += sim_vy
    
    # Draw trajectory line
    if len(points) > 1:
        pygame.draw.lines(screen, ORANGE, False, points, 2)
        for point in points:
            pygame.draw.circle(screen, ORANGE, (int(point[0]), int(point[1])), 3)


def main():
    # Create ball
    ball = Ball(WIDTH // 2, 100)
    
    # Create platforms
    platforms = [
        Platform(100, 400, 200, 20),
        Platform(500, 350, 200, 20),
        Platform(200, 250, 150, 20),
        Platform(450, 500, 250, 20),
        Platform(50, 150, 180, 20),
    ]
    
    # Mouse state for launching
    is_dragging = False
    drag_start = None
    
    # Font for UI
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    ball.reset(WIDTH // 2, 100)
                elif event.key == pygame.K_SPACE:
                    ball.is_gravity_on = not ball.is_gravity_on
                elif event.key == pygame.K_UP:
                    ball.gravity = min(2.0, ball.gravity + 0.1)
                elif event.key == pygame.K_DOWN:
                    ball.gravity = max(0.0, ball.gravity - 0.1)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if clicking near the ball
                    dist = math.sqrt((mouse_pos[0] - ball.x)**2 + (mouse_pos[1] - ball.y)**2)
                    if dist < ball.radius * 2:
                        is_dragging = True
                        drag_start = (ball.x, ball.y)
                        ball.vx = 0
                        ball.vy = 0
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and is_dragging:
                    is_dragging = False
                    mouse_pos = pygame.mouse.get_pos()
                    # Launch the ball
                    launch_vx = (drag_start[0] - mouse_pos[0]) * 0.15
                    launch_vy = (drag_start[1] - mouse_pos[1]) * 0.15
                    ball.set_velocity(launch_vx, launch_vy)
        
        # Update
        ball.update(platforms)
        
        # Draw
        screen.fill(WHITE)
        
        # Draw platforms
        for platform in platforms:
            platform.draw(screen)
        
        # Draw trajectory if dragging
        if is_dragging:
            mouse_pos = pygame.mouse.get_pos()
            draw_trajectory(ball, mouse_pos, drag_start)
            
            # Draw drag line
            pygame.draw.line(screen, GRAY, drag_start, mouse_pos, 2)
            pygame.draw.circle(screen, GRAY, (int(mouse_pos[0]), int(mouse_pos[1])), 10)
        
        # Draw ball
        ball.draw(screen)
        
        # Draw UI
        ui_text = f"Gravity: {'ON' if ball.is_gravity_on else 'OFF'} | Strength: {ball.gravity:.2f}"
        ui_surface = font.render(ui_text, True, BLACK)
        screen.blit(ui_surface, (10, 10))
        
        instructions = [
            "Drag ball to launch | R: Reset | SPACE: Toggle Gravity",
            "UP/DOWN: Adjust Gravity | ESC: Quit"
        ]
        for i, text in enumerate(instructions):
            inst_surface = small_font.render(text, True, GRAY)
            screen.blit(inst_surface, (10, HEIGHT - 50 + i * 25))
        
        # Velocity display
        vel_text = f"Velocity: ({ball.vx:.2f}, {ball.vy:.2f})"
        vel_surface = small_font.render(vel_text, True, BLACK)
        screen.blit(vel_surface, (WIDTH - 200, 10))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    main()
