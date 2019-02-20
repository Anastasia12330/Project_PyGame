import pygame, os, random, sys

pygame.init()
size = width, height = 1000, 600
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

pygame.time.set_timer(pygame.USEREVENT, 3000)


def load_image(name, color_key=-1):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


# Анимация спрайтов
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


# создаем класс космических кораблей ПРОТИВНИКА
class SpaceShip(pygame.sprite.Sprite):
    image = load_image("fw190a8.jpg", -1)
    image = pygame.transform.scale(image, (100, 50))

    def __init__(self, group):
        super().__init__(group)
        self.image = SpaceShip.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = width
        self.rect.y = random.randint(30, height - y1)
        self.speed = 3
        self.kill()
        while pygame.sprite.spritecollideany(self, all_SpaceShip):
            self.rect.x = width
            self.rect.y = random.randrange(30, height - y1)
        all_SpaceShip.add(self)

    def update(self):
        if self.rect.x > 0:
            self.rect.x -= self.speed
        # убиваем, если корабль ушел за экран
        elif self.rect.x < 0:
            self.kill()


# создадим группу, содержащую все спрайты
all_sprites = pygame.sprite.Group()
all_dragon = pygame.sprite.Group()

helicopter = AnimatedSprite(load_image("helicopter.png", -1), 1, 4, 50, 150)
all_sprites = pygame.sprite.Group(helicopter)

# создадим группу, содержащую все корабли ПРОТИВНИКА
all_SpaceShip = pygame.sprite.Group()

SpaceShip_image = load_image("fw190a8.jpg", -1)
SpaceShip_image = pygame.transform.scale(SpaceShip_image, (100, 50))
x1, y1 = SpaceShip_image.get_rect().size

fon = pygame.transform.scale(load_image("Mountain.jpg"), (width, height))

running = True
while running:
    screen.blit(fon, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.USEREVENT:  # появление кораблей ПРОТИВНИКА
            for i in range(1):
                SpaceShip(all_SpaceShip)

    all_sprites.update()
    all_sprites.draw(screen)

    all_SpaceShip.draw(screen)
    all_SpaceShip.update()

    pygame.display.flip()
    clock.tick(20)
