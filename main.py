import os
import sys

import pygame

pygame.init()
step = 50
size = WIDTH, HEIGHT = 1500, 1000
screen = pygame.display.set_mode(size)
pygame.display.set_caption("ПЕРЕМЕЩЕНИЕ ГЕРОЯ")
clock = pygame.time.Clock()
key = False


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def start_screen():
    intro_text = ["room escape",
                  "Нажмите для продолжения"]

    fon = pygame.transform.scale(load_image('LOL.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def first_room():
    fon = pygame.transform.scale(load_image('LOL.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))


class Door(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('door.png'), (400, 580))

    def __init__(self, group):
        super().__init__(group)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (150, 288)

    def get_event(self, event):
        if self.rect.collidepoint(event.pos) and key:
            self.kill()


class Vent_zoom(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('vent1.png'), (500, 500))

    def __init__(self, group):
        if key:
            self.image = pygame.transform.scale(load_image('vent.png'), (500, 500))
        super().__init__(group)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (500, 300)

    def get_event(self, event):
        global key
        if self.rect.collidepoint(event.pos):
            key = True
            self.image = pygame.transform.scale(load_image('vent.png'), (500, 500))
        else:
            self.kill()


class Ventilation(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('vent.png'), (200, 200))

    def __init__(self, group):
        super().__init__(group)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (1200, 200)

    def get_event(self, event):
        if self.rect.collidepoint(event.pos):
            Vent_zoom(all_sprites)


start_screen()
first_room()
Ventilation(all_sprites)
Door(all_sprites)
running = True
while running:
    first_room()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for sprite in all_sprites:
                sprite.get_event(event)
    if pygame.mouse.get_focused():
        all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
