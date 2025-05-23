import pygame
import random
import math
import os

pygame.init()

# Get screen resolution
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h

# Screen settings
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (150, 150, 150)
SAND = (194, 178, 128)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tower Defense")

# Load images

# Background
background_image = pygame.image.load('assets/Terrains/new/background.png')

# Enemies
enemy_image = pygame.image.load('assets/Enemy/enemy.png')

# Basic Tower
basic_tower_image = pygame.image.load('assets/Blue/Bodies/body_tracks.png')
weapon_shooting_image = pygame.image.load('assets/Blue/New/turret_01_mk1shoot.png')
weapon_idle_image = pygame.image.load('assets/Blue/New/turret_01_mk1no.png')

# Sniper Tower
sniper_tower_image = pygame.image.load('assets/Red/Bodies/body_tracks.png')
sniper_weapon_shooting_image = pygame.image.load('assets/Red/New/turret_01_mk1redshoot.png')
sniper_weapon_idle_image = pygame.image.load('assets/Red/New/turret_01_mk1redno.png')

# Rapid Tower (Camo)
rapid_tower_image = pygame.image.load('assets/Camo/Bodies/body_tracks.png')
rapid_weapon_shooting_image = pygame.image.load('assets/Camo/New/turret_01_mk1camoshoot.png')
rapid_weapon_idle_image = pygame.image.load('assets/Camo/New/turret_01_mk1camono.png')

# Splash Tower (Desert)
splash_tower_image = pygame.image.load('assets/Desert/Bodies/body_tracks.png')
splash_weapon_shooting_image = pygame.image.load('assets/Desert/New/turret_02_mk4desshoot.png')
splash_weapon_idle_image = pygame.image.load('assets/Desert/New/turret_02_mk4desno.png')

# Freeze Tower (Purple)
freeze_tower_image = pygame.image.load('assets/Purple/Bodies/body_tracks.png')
freeze_weapon_shooting_image = pygame.image.load('assets/Purple/New/turret_02_mk1purpshoot.png')
freeze_weapon_idle_image = pygame.image.load('assets/Purple/New/turret_02_mk1purpno.png')

# Enemy Path (Waypoints)
path = [(WIDTH // 10, 0), (WIDTH // 10, HEIGHT // 2.5), (WIDTH // 2.5, HEIGHT // 2.5), (WIDTH // 2.5, HEIGHT * 0.8), (WIDTH * 0.7, HEIGHT * 0.8), (WIDTH * 0.7, HEIGHT)]

# Tower Data
TOWER_TYPES = [
    {"name": "Basic Tower", "cost": 100, "range": 100, "fire_rate": 0.05, "damage": 1, "color": BLUE, "image": basic_tower_image, "weapon_shooting_image": weapon_shooting_image, "weapon_idle_image": weapon_idle_image},  
    {"name": "Sniper Tower", "cost": 200, "range": 300, "fire_rate": 0.01, "damage": 3, "color": RED, "image": sniper_tower_image, "weapon_shooting_image": sniper_weapon_shooting_image, "weapon_idle_image": sniper_weapon_idle_image},
    {"name": "Rapid Tower", "cost": 150, "range": 80, "fire_rate": 0.05, "damage": 0.5, "color": GREEN, "image": rapid_tower_image, "weapon_shooting_image": rapid_weapon_shooting_image, "weapon_idle_image": rapid_weapon_idle_image},
    {"name": "Splash Tower", "cost": 250, "range": 120, "fire_rate": 0.015, "damage": 2, "color": SAND, "image": splash_tower_image, "weapon_shooting_image": splash_weapon_shooting_image, "weapon_idle_image": splash_weapon_idle_image},
    {"name": "Freeze Tower", "cost": 300, "range": 90, "fire_rate": 0.02, "damage": 1, "color": PURPLE, "image": freeze_tower_image, "weapon_shooting_image": freeze_weapon_shooting_image, "weapon_idle_image": freeze_weapon_idle_image}
]

tower_buttons = [pygame.Rect(WIDTH - 200, 10 + i * 110, 180, 100) for i in range(len(TOWER_TYPES))]
selected_tower = None
money = 100  # Starting money
wave = 1
enemies = []
towers = []
bullets = []

game_over = False
in_menu = True
difficulty_selected = False
difficulty = "Easy"

score = 0
high_scores = []

# Define tower slots
tower_slots = [
    (WIDTH // 10 - 50, HEIGHT // 6 - 50),
    (WIDTH // 4 - 50, HEIGHT // 6 - 50),
    (WIDTH // 2 - 50, HEIGHT // 6 - 50),
    (WIDTH * 3 // 4 - 50, HEIGHT // 6 - 50),
    (WIDTH // 10 - 50, HEIGHT // 3 - 50),
    (WIDTH // 4 - 50, HEIGHT // 3 - 50),
    (WIDTH // 2 - 50, HEIGHT // 3 - 50),
    (WIDTH * 3 // 4 - 50, HEIGHT // 3 - 50),
    (WIDTH // 10 - 50, HEIGHT // 2 - 50),
    (WIDTH // 4 - 50, HEIGHT // 2 - 50),
    (WIDTH // 2 - 50, HEIGHT // 2 - 50),
    (WIDTH * 3 // 4 - 50, HEIGHT // 2 - 50),
    (WIDTH // 10 - 50, HEIGHT * 2 // 3 - 50),
    (WIDTH // 4 - 50, HEIGHT * 2 // 3 - 50),
    (WIDTH // 2 - 50, HEIGHT * 2 // 3 - 50),
    (WIDTH * 3 // 4 - 50, HEIGHT * 2 // 3 - 50),
    (WIDTH // 10 - 50, HEIGHT * 5 // 6 - 50),
    (WIDTH // 4 - 50, HEIGHT * 5 // 6 - 50),
    (WIDTH // 2 - 50, HEIGHT * 5 // 6 - 50),
    (WIDTH * 3 // 4 - 50, HEIGHT * 5 // 6 - 50),
]

# Track which slots are occupied
occupied_slots = [False] * len(tower_slots)

class Enemy:
    def __init__(self, delay, hp):
        self.path_index = 0
        self.rect = pygame.Rect(path[0][0], path[0][1] - delay, 40, 40)
        self.hp = hp
        self.max_hp = hp
        self.speed = 2
        self.alive = True
        self.image = enemy_image
        self.angle = 0
    
    def move(self):
        if self.path_index < len(path) - 1:
            target_x, target_y = path[self.path_index + 1]
            dx = target_x - self.rect.x
            dy = target_y - self.rect.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 1:
                self.rect.x += (dx / distance) * self.speed
                self.rect.y += (dy / distance) * self.speed
                self.angle = math.degrees(math.atan2(dy, dx)) - 90
            else:
                self.path_index += 1
        else:
            global game_over
            game_over = True
    
    def draw(self):
        if self.alive:
            rotated_image = pygame.transform.rotate(self.image, self.angle)
            new_rect = rotated_image.get_rect(center=self.rect.center)
            screen.blit(rotated_image, new_rect.topleft)
            pygame.draw.rect(screen, (0, 0, 0), (self.rect.x, self.rect.y - 5, 40, 6))
            pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 5, (self.hp / self.max_hp) * 40, 6))

class Bullet:
    def __init__(self, x, y, target, damage, color, speed=10, is_sniper=False):
        self.pos = [x, y]
        self.target = target
        self.speed = speed
        self.damage = damage
        self.color = color
        self.active = True
        self.is_sniper = is_sniper
    
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
                global money, score
                money += 50
                score += 10  # Add points for defeating an enemy
            self.active = False
    
    def draw(self):
        if self.active:
            if self.is_sniper:
                pygame.draw.line(screen, self.color, (int(self.pos[0]), int(self.pos[1])), (self.target.rect.x, self.target.rect.y), 2)
            else:
                pygame.draw.circle(screen, self.color, (int(self.pos[0]), int(self.pos[1])), 10)

def spawn_enemies():
    if difficulty == "Easy":
        base_hp = 3 * (1 + 0.3 * (wave - 1))
        num_enemies = 3
    elif difficulty == "Medium":
        base_hp = 3 * (1 + 0.3 * (wave - 1)) + 1
        num_enemies = 4
    elif difficulty == "Hard":
        base_hp = 3 * (1 + 0.3 * (wave - 1)) + 2
        num_enemies = 5

    for i in range(num_enemies):
        enemies.append(Enemy(i * 80, base_hp))  # Increased delay to add space between enemies

def draw_menu():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 100)
    start_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 100, 300, 100)
    exit_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 100)
    pygame.draw.rect(screen, GRAY, start_button)
    pygame.draw.rect(screen, GRAY, exit_button)
    screen.blit(font.render("Start", True, BLACK), (start_button.x + 50, start_button.y + 10))
    screen.blit(font.render("Exit", True, BLACK), (exit_button.x + 50, exit_button.y + 10))
    pygame.display.flip()
    return start_button, exit_button

def draw_difficulty_menu():
    screen.fill(WHITE)
    font = pygame.font.Font(None, 100)
    easy_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 200, 300, 100)
    medium_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 100)
    hard_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 100)
    pygame.draw.rect(screen, GRAY, easy_button)
    pygame.draw.rect(screen, GRAY, medium_button)
    pygame.draw.rect(screen, GRAY, hard_button)
    screen.blit(font.render("Easy", True, BLACK), (easy_button.x + 50, easy_button.y + 10))
    screen.blit(font.render("Medium", True, BLACK), (medium_button.x + 50, medium_button.y + 10))
    screen.blit(font.render("Hard", True, BLACK), (hard_button.x + 50, hard_button.y + 10))
    pygame.display.flip()
    return easy_button, medium_button, hard_button

def draw_welcome_screen():
    screen.fill(WHITE)
    font_title = pygame.font.Font(None, 120)
    font_message = pygame.font.Font(None, 60)
    title_text = font_title.render("Tower Defense Game", True, BLACK)
    message_text = font_message.render("Press any key to continue", True, GRAY)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 3))
    screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

def load_high_scores():
    global high_scores
    if os.path.exists("scores.txt"):
        with open("scores.txt", "r") as file:
            high_scores = [int(line.strip()) for line in file.readlines()]
    else:
        high_scores = []

def save_high_scores():
    global high_scores
    with open("scores.txt", "w") as file:
        for score in high_scores:
            file.write(f"{score}\n")

def draw_leaderboard():
    screen.fill(WHITE)
    font_title = pygame.font.Font(None, 100)
    font_score = pygame.font.Font(None, 60)
    title_text = font_title.render("Leaderboard", True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    for i, score in enumerate(high_scores):
        score_text = font_score.render(f"{i + 1}. {score}", True, BLACK)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 150 + i * 50))

    pygame.display.flip()
    pygame.time.delay(5000)  # Display for 5 seconds

# Show the welcome screen
show_welcome = True
while show_welcome:
    draw_welcome_screen()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            show_welcome = False

# Proceed to the main menu
start_button, exit_button = draw_menu()

load_high_scores()

running = True
paused = False

while running:
    if in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    in_menu = False
                    difficulty_selected = True
                    easy_button, medium_button, hard_button = draw_difficulty_menu()
                if exit_button.collidepoint(event.pos):
                    running = False
    elif difficulty_selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    difficulty = "Easy"
                    difficulty_selected = False
                    spawn_enemies()
                if medium_button.collidepoint(event.pos):
                    difficulty = "Medium"
                    difficulty_selected = False
                    spawn_enemies()
                if hard_button.collidepoint(event.pos):
                    difficulty = "Hard"
                    difficulty_selected = False
                    spawn_enemies()
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Toggle pause with the 'P' key
                    paused = not paused

            if not paused:  # Only process events if the game is not paused
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if selected_tower and money >= selected_tower["cost"]:
                        for i, slot in enumerate(tower_slots):
                            slot_rect = pygame.Rect(slot[0], slot[1], 50, 50)
                            if slot_rect.collidepoint(event.pos):
                                # Replace the tower if the slot is already occupied
                                for j, tower in enumerate(towers):
                                    if tower["pos"] == slot:
                                        towers.pop(j)
                                        break
                                towers.append({"pos": slot, "type": selected_tower, "shooting": False})
                                money -= selected_tower["cost"]
                                selected_tower = None
                                occupied_slots[i] = True
                                break
                    else:
                        for i, button in enumerate(tower_buttons):
                            if button.collidepoint(event.pos):
                                selected_tower = TOWER_TYPES[i]

        if not paused:  # Only update the game if not paused
            screen.fill(WHITE)
            scaled_background = pygame.transform.scale(background_image, (WIDTH - 200, HEIGHT))
            screen.blit(scaled_background, (0, 0))  # Draw background image within game area
            pygame.draw.rect(screen, BLACK, (WIDTH - 200, 0, 200, HEIGHT))
            pygame.draw.rect(screen, BLACK, (0, 0, WIDTH - 200, HEIGHT), 5)
            
            for i in range(len(path) - 1):
                pygame.draw.line(screen, GRAY, path[i], path[i + 1], 10)
            
            font = pygame.font.Font(None, 60)
            screen.blit(font.render(f"Money: ${money}", True, (0, 0, 0)), (10, 10))
            screen.blit(font.render(f"Wave: {wave}", True, (0, 0, 0)), (10, 80))
            
            if game_over:
                high_scores.append(score)
                high_scores = sorted(high_scores, reverse=True)[:5]
                save_high_scores()
                draw_leaderboard()
                screen.blit(font.render("Game Over!", True, RED), (WIDTH // 2 - 100, HEIGHT // 2))
                pygame.display.flip()
                pygame.time.delay(2000)
                in_menu = True
                start_button, exit_button = draw_menu()
                continue
            
            for enemy in enemies[:]:
                if enemy.alive:
                    enemy.move()
                    enemy.draw()
                else:
                    enemies.remove(enemy)
            
            if not enemies and not game_over:
                wave += 1
                spawn_enemies()
            
            for tower in towers:
                if "image" in tower["type"]:
                    screen.blit(tower["type"]["image"], (tower["pos"][0] - tower["type"]["image"].get_width() // 2, tower["pos"][1] - tower["type"]["image"].get_height() // 2))
                    if tower["shooting"]:
                        screen.blit(tower["type"]["weapon_shooting_image"], (tower["pos"][0] - tower["type"]["weapon_shooting_image"].get_width() // 2, tower["pos"][1] - tower["type"]["weapon_shooting_image"].get_height() // 2))
                    else:
                        screen.blit(tower["type"]["weapon_idle_image"], (tower["pos"][0] - tower["type"]["weapon_idle_image"].get_width() // 2, tower["pos"][1] - tower["type"]["weapon_idle_image"].get_height() // 2))
                else:
                    pygame.draw.circle(screen, tower["type"]["color"], tower["pos"], 20)
                
                if random.random() < tower["type"]["fire_rate"] and any(enemy.alive for enemy in enemies):
                    target = next((e for e in enemies if e.alive), None)  # Select the first alive enemy
                    if target:
                        if tower["type"]["name"] == "Sniper Tower":
                            bullet_color = RED
                            bullets.append(Bullet(tower["pos"][0], tower["pos"][1], target, tower["type"]["damage"], bullet_color, speed=10, is_sniper=True))
                        else:
                            if tower["type"]["name"] == "Rapid Tower":
                                bullet_color = GREEN
                            elif tower["type"]["name"] == "Splash Tower":
                                bullet_color = SAND
                            elif tower["type"]["name"] == "Freeze Tower":
                                bullet_color = PURPLE
                            else:
                                bullet_color = BLUE
                            bullets.append(Bullet(tower["pos"][0], tower["pos"][1], target, tower["type"]["damage"], bullet_color))
                        tower["shooting"] = True
                else:
                    tower["shooting"] = False
            
            for bullet in bullets:
                if bullet.active:
                    bullet.move()
                    bullet.check_collision()
                    bullet.draw()

            # Corrected list comprehension
            bullets = [bullet for bullet in bullets if bullet.active]
            
            for i, tower in enumerate(TOWER_TYPES):
                rect = tower_buttons[i]
                pygame.draw.rect(screen, tower["color"], rect)
                font = pygame.font.Font(None, 30)  # Decrease font size to 30
                text = font.render(f'{tower["name"]} ${tower["cost"]}', True, (0, 0, 0))
                text_rect = text.get_rect(center=(rect.x + rect.width // 2, rect.y + rect.height // 2))
                screen.blit(text, text_rect)
            
            # Draw tower slots
            for slot in tower_slots:
                pygame.draw.rect(screen, GRAY, (slot[0], slot[1], 50, 50), 2)
        
        elif paused:  # Display pause message
            font = pygame.font.Font(None, 100)
            screen.blit(font.render("Paused", True, RED), (WIDTH // 2 - 100, HEIGHT // 2))
        
        pygame.display.flip()
        pygame.time.delay(10)

pygame.quit()