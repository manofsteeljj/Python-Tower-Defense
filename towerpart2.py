import pygame
import random
import math

pygame.init()

# Screen settings
WIDTH, HEIGHT = 600, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")

# Enemy Path (Waypoints)
path = [(50, 0), (50, 200), (200, 200), (200, 400), (350, 400), (350, HEIGHT)]

# Tower Data
TOWER_TYPES = [
    {"name": "Basic Tower", "cost": 100, "range": 100, "fire_rate": 0.02, "damage": 1},
    {"name": "Sniper Tower", "cost": 200, "range": 200, "fire_rate": 0.005, "damage": 3},
    {"name": "Rapid Tower", "cost": 150, "range": 80, "fire_rate": 0.05, "damage": 0.5},
    {"name": "Splash Tower", "cost": 250, "range": 120, "fire_rate": 0.015, "damage": 2},
    {"name": "Freeze Tower", "cost": 300, "range": 90, "fire_rate": 0.02, "damage": 1}
]

money = 100  # Starting money
wave = 1
enemies_per_wave = 3
enemies = []
towers = []
bullets = []

# Enemy Class
class Enemy:
    def __init__(self):
        self.path_index = 0
        self.rect = pygame.Rect(path[0][0], path[0][1], 20, 20)
        self.hp = 3
        self.speed = 2
        self.alive = True

    def move(self):
        if self.path_index < len(path) - 1:
            target_x, target_y = path[self.path_index + 1]
            dx = target_x - self.rect.x
            dy = target_y - self.rect.y
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 1:
                self.rect.x += (dx / distance) * self.speed
                self.rect.y += (dy / distance) * self.speed
            else:
                self.path_index += 1

    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, RED, self.rect)
            pygame.draw.rect(screen, (0, 0, 0), (self.rect.x, self.rect.y - 5, 20, 3))
            pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 5, (self.hp / 3) * 20, 3))

# Bullet Class
class Bullet:
    def __init__(self, x, y, target, damage, speed=5):
        self.pos = [x, y]
        self.target = target
        self.speed = speed
        self.damage = damage
        self.active = True  # Bullet disappears after hitting target

    def move(self):
        if not self.target.alive:
            self.active = False  # Stop if target is already dead
            return

        dx = self.target.rect.x - self.pos[0]
        dy = self.target.rect.y - self.pos[1]
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.pos[0] += (dx / distance) * self.speed
            self.pos[1] += (dy / distance) * self.speed

    def check_collision(self):
        if self.target.rect.collidepoint(self.pos):
            self.target.hp -= self.damage
            if self.target.hp <= 0:
                self.target.alive = False  # Correctly mark as dead
                global money
                money += 50  # Reward for killing enemy
            self.active = False  # Bullet disappears after hitting

    def draw(self):
        if self.active:
            pygame.draw.circle(screen, BLUE, (int(self.pos[0]), int(self.pos[1])), 5)

# Game loop
running = True
while running:
    screen.fill(WHITE)

    # Draw enemy path
    for i in range(len(path) - 1):
        pygame.draw.line(screen, GRAY, path[i], path[i + 1], 5)

    # Display money and wave
    font = pygame.font.Font(None, 30)
    money_text = font.render(f"Money: ${money}", True, (0, 0, 0))
    wave_text = font.render(f"Wave: {wave}", True, (0, 0, 0))
    screen.blit(money_text, (10, 10))
    screen.blit(wave_text, (10, 40))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if money >= 100:
                towers.append({"pos": event.pos, "type": TOWER_TYPES[0]})
                money -= 100

    # Spawn enemies based on wave count
    if not any(enemy.alive for enemy in enemies):  # Only start new wave if all are dead
        wave += 1
        enemies_per_wave += 2
        enemies = [Enemy() for _ in range(enemies_per_wave)]

    # Move and draw enemies
    for enemy in enemies:
        if enemy.alive:
            enemy.move()
            enemy.draw()
        else:
            enemies.remove(enemy)  # FIXED: Enemies are now removed properly

    # Tower shooting
    for tower in towers:
        pygame.draw.circle(screen, GREEN, tower["pos"], 10)
        tower_type = tower["type"]
        if random.random() < tower_type["fire_rate"] and any(enemy.alive for enemy in enemies):
            target = random.choice([e for e in enemies if e.alive])  # Pick a live enemy
            bullets.append(Bullet(tower["pos"][0], tower["pos"][1], target, tower_type["damage"]))

    # Move and draw bullets
    for bullet in bullets:
        if bullet.active:
            bullet.move()
            bullet.check_collision()
            bullet.draw()

    # Remove inactive bullets
    bullets = [bullet for bullet in bullets if bullet.active]

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
