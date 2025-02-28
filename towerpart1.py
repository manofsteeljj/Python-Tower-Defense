import pygame
import random
import math

pygame.init()

# Screen settings
WIDTH, HEIGHT = 400, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")

# Enemy Path (Waypoints)
path = [(50, 0), (50, 200), (200, 200), (200, 400), (350, 400), (350, HEIGHT)]

# Enemy class
class Enemy:
    def __init__(self):
        self.path_index = 0
        self.rect = pygame.Rect(path[0][0], path[0][1], 20, 20)
        self.hp = 3  # Enemy health

    def move(self):
        if self.path_index < len(path) - 1:
            target_x, target_y = path[self.path_index + 1]
            dx = target_x - self.rect.x
            dy = target_y - self.rect.y
            distance = (dx**2 + dy**2) ** 0.5

            if distance > 1:
                self.rect.x += dx / distance * 2  # Move towards the waypoint
                self.rect.y += dy / distance * 2
            else:
                self.path_index += 1  # Move to next waypoint

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), (self.rect.x, self.rect.y - 5, 20, 3))  # Health bar outline
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 5, (self.hp / 3) * 20, 3))  # Health bar fill

# Bullet class
class Bullet:
    def __init__(self, x, y, target):
        self.pos = [x, y]
        self.target = target
        self.speed = 5

    def move(self):
        dx = self.target.rect.x - self.pos[0]
        dy = self.target.rect.y - self.pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            self.pos[0] += (dx / distance) * self.speed
            self.pos[1] += (dy / distance) * self.speed

    def draw(self):
        pygame.draw.circle(screen, BLUE, (int(self.pos[0]), int(self.pos[1])), 5)

# Initialize enemies, towers, and bullets
enemies = [Enemy() for _ in range(3)]
towers = []
bullets = []

# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Draw enemy path
    for i in range(len(path) - 1):
        pygame.draw.line(screen, GRAY, path[i], path[i + 1], 5)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            towers.append(event.pos)

    # Move and draw enemies
    for enemy in enemies[:]:  # Copy list to avoid modifying while iterating
        enemy.move()
        enemy.draw()
        if enemy.path_index == len(path) - 1:
            print("Game Over!")
            running = False
        if enemy.hp <= 0:
            enemies.remove(enemy)

    # Tower shooting mechanism
    for tower in towers:
        pygame.draw.circle(screen, GREEN, tower, 10)
        if random.random() < 0.02 and enemies:  # 2% chance to shoot
            target = random.choice(enemies)  # Pick a random enemy
            bullets.append(Bullet(tower[0], tower[1], target))

    # Move and draw bullets
    for bullet in bullets[:]:  # Copy list to avoid modifying while iterating
        bullet.move()
        bullet.draw()
        for enemy in enemies:
            if enemy.rect.collidepoint(bullet.pos):
                enemy.hp -= 1
                bullets.remove(bullet)
                break  # Stop checking after first hit

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
