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
    {"name": "Basic Tower", "cost": 100, "range": 100, "fire_rate": 0.05, "damage": 1, "color": (0, 255, 0)},  
    {"name": "Sniper Tower", "cost": 200, "range": 200, "fire_rate": 0.005, "damage": 3, "color": (255, 0, 0)},
    {"name": "Rapid Tower", "cost": 150, "range": 80, "fire_rate": 0.05, "damage": 0.5, "color": (0, 0, 255)},
    {"name": "Splash Tower", "cost": 250, "range": 120, "fire_rate": 0.015, "damage": 2, "color": (255, 165, 0)},
    {"name": "Freeze Tower", "cost": 300, "range": 90, "fire_rate": 0.02, "damage": 1,  "color": (0, 255, 255)}
]

tower_buttons = [pygame.Rect(10 + i * 120, HEIGHT - 50, 100, 40) for i in range(len(TOWER_TYPES))]
selected_tower = None
money = 100  # Starting money
wave = 1
enemies_per_wave = 3
enemies = []
towers = []
bullets = []

game_over = False

class Enemy:
    def __init__(self, delay):
        self.path_index = 0
        self.rect = pygame.Rect(path[0][0], path[0][1] - delay, 20, 20)
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
        else:
            global game_over
            game_over = True
    
    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, RED, self.rect)
            pygame.draw.rect(screen, (0, 0, 0), (self.rect.x, self.rect.y - 5, 20, 3))
            pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 5, (self.hp / 3) * 20, 3))

class Bullet:
    def __init__(self, x, y, target, damage, speed=5):
        self.pos = [x, y]
        self.target = target
        self.speed = speed
        self.damage = damage
        self.active = True
    
    def move(self):
        if not self.target.alive:
            self.active = False
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
                self.target.alive = False
                global money
                money += 50
            self.active = False
    
    def draw(self):
        if self.active:
            pygame.draw.circle(screen, BLUE, (int(self.pos[0]), int(self.pos[1])), 5)

def spawn_enemies():
    for i in range(enemies_per_wave):
        enemies.append(Enemy(i * 40))  # Increased delay to add space between enemies

running = True
spawn_enemies()  # Initial spawn of enemies

while running:
    screen.fill(WHITE)
    
    for i in range(len(path) - 1):
        pygame.draw.line(screen, GRAY, path[i], path[i + 1], 5)
    
    font = pygame.font.Font(None, 30)
    screen.blit(font.render(f"Money: ${money}", True, (0, 0, 0)), (10, 10))
    screen.blit(font.render(f"Wave: {wave}", True, (0, 0, 0)), (10, 40))
    
    if game_over:
        screen.blit(font.render("Game Over!", True, RED), (WIDTH // 2 - 50, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.delay(2000)
        break
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if selected_tower and money >= selected_tower["cost"]:
                towers.append({"pos": event.pos, "type": selected_tower})
                money -= selected_tower["cost"]
            else:
                for i, button in enumerate(tower_buttons):
                    if button.collidepoint(event.pos):
                        selected_tower = TOWER_TYPES[i]
    
    for enemy in enemies[:]:
        if enemy.alive:
            enemy.move()
            enemy.draw()
        else:
            enemies.remove(enemy)
    
    if not enemies and not game_over:
        wave += 1
        enemies_per_wave += 2  # Increase the number of enemies per wave
        spawn_enemies()
    
    for tower in towers:
        pygame.draw.circle(screen, tower["type"]["color"], tower["pos"], 10)
        if random.random() < tower["type"]["fire_rate"] and any(enemy.alive for enemy in enemies):
            target = random.choice([e for e in enemies if e.alive])
            bullets.append(Bullet(tower["pos"][0], tower["pos"][1], target, tower["type"]["damage"]))
    
    for bullet in bullets:
        if bullet.active:
            bullet.move()
            bullet.check_collision()
            bullet.draw()
    
    bullets = [bullet for bullet in bullets if bullet.active]
    
    for i, tower in enumerate(TOWER_TYPES):
        rect = tower_buttons[i]
        pygame.draw.rect(screen, tower["color"], rect)
        text = font.render(f'{tower["name"]} ${tower["cost"]}', True, (0, 0, 0))
        screen.blit(text, (rect.x + 5, rect.y + 10))
    
    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()