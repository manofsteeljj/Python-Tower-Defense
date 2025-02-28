import pygame
import random


pygame.init()
WIDTH, HEIGHT = 400, 600
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tower Defense")

towers = []
enemies = [pygame.Rect(random.randint(0, WIDTH), 0, 20, 20) for _ in range(5)]

running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            towers.append(event.pos)
    for enemy in enemies:
        enemy.y += 1
        pygame.draw.rect(screen, RED, enemy)

    for tower in towers:
        pygame.draw.circle(screen, GREEN, tower, 10)    

    pygame.display.flip()
    pygame.time.delay(30)
pygame.quit()