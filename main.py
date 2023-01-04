import os
import sys
import pygame
import random

pygame.init()  # предварительная инициализация
size = WIDTH, HEIGHT = 1200, 800  # размеры окна
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Побег из комнаты")
clock = pygame.time.Clock()
FPS = 60
music = True
fone = 'LOL.png'
key = False  # флаг для подбора ключа
prav = True  # флаг для правой двери комода
lev = True  # флаг для левой двери комода
screwdriver = False  # флаг для поднятия отвертки
otkr = False  # открыта ли вентиляция
zoom = False  # есть ли приближенные объекты
door = True  # открыта ли дверь
first_exit = True  # флаг для выхода из первой комнаты
flag = False  # флаг для лабиринта
end = False


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:  # Убрать фон у изображение при падачи параметра colorkey
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():
    intro_text = ["ROOM ESCAPE",
                  "Ваша цель: выбраться из места, в котором вы оказались",
                  "Используйте левую кнопку мыши",
                  "Нажмите для продолжения"]

    fon = pygame.transform.scale(load_image('LOL.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 240
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 460
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()


def room():
    fon = pygame.transform.scale(load_image(fone), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))


class Door(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('door.png'), (250, 440))

    def __init__(self, group):
        super().__init__(group)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (219, 225)

    def get_event(self, event):
        if not zoom:
            if self.rect.collidepoint(event.pos) and key:  # Проверка нажатия и наличие ключа
                global door
                self.kill()  # убираем спрайт двери
                door = False


class VentZoom(pygame.sprite.Sprite):  # вызов при нажатии на вентиляцию
    image = pygame.transform.scale(load_image('vent_zakr.png'), (500, 500))

    def __init__(self, group):
        global zoom
        zoom = True
        if otkr:
            self.image = pygame.transform.scale(load_image('vent_otkr.png'), (500, 500))
        super().__init__(group)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (350, 150)

    def get_event(self, event):
        global otkr
        if self.rect.collidepoint(event.pos):
            if not otkr:
                if screwdriver:  # Проверка на наличие отвертки
                    self.image = pygame.transform.scale(load_image('vent_otkr.png'), (500, 500))
                    otkr = True
                    Key(all_sprites, (193, 90), (400, 550))
        else:
            global zoom
            zoom = False
            self.kill()


class Ventilation(pygame.sprite.Sprite):  # Класс вентиляции
    image = pygame.transform.scale(load_image('vent.png'), (150, 150))

    def __init__(self, group):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (WIDTH / 3 * 2, HEIGHT / 6)

    def get_event(self, event):
        if otkr:
            self.image = pygame.transform.scale(load_image('vent_otkr.png'), (150, 150))
        if not zoom:
            if self.rect.collidepoint(event.pos):
                VentZoom(all_sprites)
                if otkr and not key:
                    Key(all_sprites, (193, 90), (400, 550))


class LeftDoorCommode(pygame.sprite.Sprite):  # левая дверь при приближении
    left_door = pygame.transform.scale(load_image('lev_dv.png'), (250, 500))

    def __init__(self, group):
        super().__init__(group)
        self.image = self.left_door
        self.rect = self.image.get_rect()
        self.rect.topleft = (350, 150)

    def get_event(self, event):
        global lev
        if self.rect.collidepoint(event.pos):
            self.kill()
            lev = False
            Otv(all_sprites)
        else:
            if not (350 < event.pos[0] < 850 and 150 < event.pos[1] < 650):
                self.kill()


class RightDoorCommode(pygame.sprite.Sprite):  # правая дверь при приближении
    right_door = pygame.transform.scale(load_image('prav_dv.png'), (250, 500))

    def __init__(self, group):
        super().__init__(group)
        self.image = self.right_door
        self.rect = self.image.get_rect()
        self.rect.topleft = (600, 150)

    def get_event(self, event):
        global prav
        if self.rect.collidepoint(event.pos):
            self.kill()
            prav = False
        else:
            if not (350 < event.pos[0] < 850 and 150 < event.pos[1] < 650):
                self.kill()


class CommodeZoom(pygame.sprite.Sprite):  # вызов при нажатии на комод
    image = pygame.transform.scale(load_image('kom_otk.png'), (500, 500))

    def __init__(self, group):
        global zoom
        zoom = True
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (350, 150)

    def get_event(self, event):
        if not self.rect.collidepoint(event.pos):
            global zoom
            self.kill()
            zoom = False


class Commode(pygame.sprite.Sprite):  # класс комода
    image = pygame.transform.scale(load_image('kom.png'), (300, 300))

    def __init__(self, group):
        super(Commode, self).__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (WIDTH / 5 * 3, HEIGHT / 2)

    def get_event(self, event):
        if not zoom:
            if self.rect.collidepoint(event.pos):
                CommodeZoom(all_sprites)
                if lev:
                    LeftDoorCommode(all_sprites)
                if prav:
                    RightDoorCommode(all_sprites)
                if not lev and not screwdriver:
                    Otv(all_sprites)
        if not prav and not lev:
            self.image = pygame.transform.scale(load_image('kom_otk.png'), (300, 300))
        elif not prav:
            self.image = pygame.transform.scale(load_image('kom_lev.png'), (300, 300))
        elif not lev:
            self.image = pygame.transform.scale(load_image('kom_pr.png'), (300, 300))


class Otv(pygame.sprite.Sprite):  # класс отвертки
    image = pygame.transform.scale(load_image('otv.png'), (100, 100))

    def __init__(self, group):
        super(Otv, self).__init__(group)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (450, 390)

    def get_event(self, event):
        global screwdriver
        if not screwdriver:
            if self.rect.collidepoint(event.pos):
                screwdriver = True
                self.kill()
            else:
                if not (350 < event.pos[0] < 850 and 150 < event.pos[1] < 650):
                    self.kill()


class Key(pygame.sprite.Sprite):  # вызов при нажатии на вентиляцию

    def __init__(self, group, razm, pos):
        image = pygame.transform.scale(load_image('key.png'), razm)
        super().__init__(group)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (pos)

    def get_event(self, event):
        global key
        if self.rect.collidepoint(event.pos):
            self.kill()
            key = True
        elif not (350 < event.pos[0] < 850 and 150 < event.pos[1] < 650):
            self.kill()


def second_room(event0, event1):   # вторая комната
    global door, first_exit, fone, key, end
    if 219 < event0 < 469 and 225 < event1 < 225 + 665 and not door and first_exit:
        first_exit = False
        fone = 'second_room.png'
        for sprite in all_sprites:
            sprite.kill()
        key = False
        door = True
        end = True
        Door(all_sprites)
        Shk(all_sprites)
        MusicPause(all_sprites)
        TurnDownTheSound(all_sprites)
        TurnUpTheSound(all_sprites)


class Shk(pygame.sprite.Sprite):   # приближение
    image = pygame.transform.scale(load_image('shk.png'), (80, 60))

    def __init__(self, group):
        super().__init__(group)
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.topleft = (650, 440)

    def get_event(self, event):
        if not zoom:
            if self.rect.collidepoint(event.pos):
                StolUp(all_sprites)
                ShkUp(all_sprites)
                if flag:
                    Box(all_sprites)
                    if not key:
                        Key(all_sprites, (80, 45), (460, 490))


class Labyrinth:
    def __init__(self, filename, free_tiles, finish_tile):
        self.map = []
        with open(f'maps/{filename}') as input_file:
            for line in input_file:
                self.map.append(list(map(int, line.split())))
        self.height = len(self.map)
        self.width = len(self.map[0])
        self.tile_size = 34
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile

    def render(self, screen):
        colors = {0: (71, 48, 32), 1: (149, 92, 62), 2: (71, 48, 32)}
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(345 + x * self.tile_size, 145 + y * self.tile_size,
                                   self.tile_size, self.tile_size)
                screen.fill(colors[self.get_tile_id((x, y))], rect)

    def get_tile_id(self, position):
        return self.map[position[1]][position[0]]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles

    def is_end(self, position):
        return self.get_tile_id(position) == self.finish_tile


class Hero:   # герой в лабиринте
    def __init__(self, position):
        self.x, self.y = position

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        center = 345 + self.x * 34 + 34 // 2, 145 + self.y * 34 + 34 // 2
        pygame.draw.circle(screen, (186, 121, 86), center, 34 // 2)


class Game:   # лабиринт
    def __init__(self, labyrinth, hero):
        self.labyrinth = labyrinth
        self.hero = hero

    def render(self, screen):
        self.labyrinth.render(screen)
        self.hero.render(screen)

    def update_hero(self):
        next_x, next_y = self.hero.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.labyrinth.is_free((next_x, next_y)):
            self.hero.set_position((next_x, next_y))

    def is_win(self):
        next_x, next_y = self.hero.get_position()
        if self.labyrinth.is_end((next_x, next_y)):
            return True
        return False


class StolUp(pygame.sprite.Sprite):   # приближенный стол на котором лабиринт
    image = pygame.transform.scale(load_image('stol_up.png'), (500, 500))

    def __init__(self, group):
        global zoom
        zoom = True
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (350, 150)

    def get_event(self, event):
        if not self.rect.collidepoint(event.pos):
            global zoom
            zoom = False
            self.kill()


class ShkUp(pygame.sprite.Sprite):   # лабиринт
    image = pygame.transform.scale(load_image('shk_up.png'), (166, 166))

    def __init__(self, group):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (433, 317)

    def get_event(self, event):
        global flag, running
        if 350 < event.pos[0] < 850 and 150 < event.pos[1] < 650:
            if not flag:
                labyrinth = Labyrinth('simple_map.txt', [0, 2], 2)
                hero = Hero((7, 7))
                game = Game(labyrinth, hero)
                clock = pygame.time.Clock()
                run = True
                while run:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            run = False
                            flag = False
                            running = False
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if not (350 < event.pos[0] < 850 and 150 < event.pos[1] < 650):
                                run = False
                    if game.is_win():
                        run = False
                        flag = True
                        Box(all_sprites)
                        Key(all_sprites, (80, 45), (460, 490))
                    game.update_hero()
                    pygame.display.flip()
                    clock.tick(15)
                    all_sprites.draw(screen)
                    game.render(screen)
                    pygame.display.flip()
        else:
            self.kill()


class Box(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('Box.png'), (166, 83))

    def __init__(self, group):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (433, 483)

    def get_event(self, event):
        if not (350 < event.pos[0] < 850 and 150 < event.pos[1] < 650):
            self.kill()


class TurnDownTheSound(pygame.sprite.Sprite):  # класс для уменьшение громкости фоновой музыки
    image = pygame.transform.scale(load_image('speaker-off.png'), (75, 75))

    def __init__(self, group):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (10, 10)

    def get_event(self, event):
        if self.rect.collidepoint(event.pos):  # при нажатии на кнопку уменьшаем громкость на 0.1
            volume = pygame.mixer.music.get_volume()
            if volume > 0.1:
                pygame.mixer.music.set_volume(volume - 0.1)
            else:
                pygame.mixer.music.set_volume(0)


class TurnUpTheSound(pygame.sprite.Sprite):  # класс для увелечение громкости фоновой музыки
    image = pygame.transform.scale(load_image('speaker.png'), (75, 75))

    def __init__(self, group):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (200, 10)

    def get_event(self, event):
        if self.rect.collidepoint(event.pos):  # при нажатии на кнопку увеличиваем громкость на 0.1
            volume = pygame.mixer.music.get_volume()
            if volume < 0.9:
                pygame.mixer.music.set_volume(volume + 0.1)
            else:
                pygame.mixer.music.set_volume(1)


class MusicPause(pygame.sprite.Sprite):  # Класс для остановки фоновой музыки
    image = pygame.transform.scale(load_image('button_music.png'), (75, 75))

    def __init__(self, group):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (100, 10)

    def get_event(self, event):
        global music
        if self.rect.collidepoint(event.pos):  # при нажатии на кнопку приостанавливаем музыку или включаем её
            music = not music
            if music:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()


def is_end(event0, event1):
    global end, fone, door
    if 219 < event0 < 469 and 225 < event1 < 225 + 665 and end and not door:
        end = False
        fone = 'end.png'
        for sprite in all_sprites:
            sprite.kill()
        End(all_sprites)


class End(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('konec.png'), (664, 166))

    def __init__(self, group):
        global running
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (200, -170)
        cl = pygame.time.Clock()
        run = True
        font = pygame.font.Font(None, 30)
        while run:
            room()
            text_coord = 500
            f_text = ["ПОЗДРАВЛЯЕМ",
                      "Вы смогли выбраться",
                      "Можете потыкать и появятся звездочки)"]
            for line in f_text:
                string_rendered = font.render(line, 1, pygame.Color('black'))
                intro_rect = string_rendered.get_rect()
                text_coord += 10
                intro_rect.top = text_coord
                intro_rect.x = 220
                text_coord += intro_rect.height
                screen.blit(string_rendered, intro_rect)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    create_particles(pygame.mouse.get_pos())
            all_sprites.update()
            self.rect.top += 2
            all_sprites.draw(screen)
            cl.tick(40)
            pygame.display.flip()

    def get_event(self, event):
        pass


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой
        self.gravity = 0.25

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect((0, 0, WIDTH, HEIGHT)):
            self.kill()

    def get_event(self):
        pass


def create_particles(position):
    particle_count = 20
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


pygame.mixer.music.load('data/music.mp3')
pygame.mixer.music.play(-1)  # бесконечное повторение музыки
pygame.mixer.music.set_volume(0.5)

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
start_screen()
Ventilation(all_sprites)
Door(all_sprites)
Commode(all_sprites)
MusicPause(all_sprites)
TurnDownTheSound(all_sprites)
TurnUpTheSound(all_sprites)
running = True
while running:
    room()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            is_end(event.pos[0], event.pos[1])
            second_room(event.pos[0], event.pos[1])
            for sprite in all_sprites:
                sprite.get_event(event)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
