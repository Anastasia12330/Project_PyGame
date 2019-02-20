import pygame, os, random, sys

pygame.init()
size = width, height = 1000, 600
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()

pygame.time.set_timer(pygame.USEREVENT, 3000)

screen_rect = (0, 0, width, height)

def load_image(name, color_key = -1):
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
        if pygame.sprite.spritecollideany(self, all_sprites):
            all_SpaceShip.remove(self)
            create_particles((self.rect.x, self.rect.y))
        if self.rect.x > 0:
            self.rect.x -= self.speed
        # убиваем, если корабль ушел за экран
        elif self.rect.x < 0:
            self.kill()


# создаем класс пуль
class Bullet(pygame.sprite.Sprite):
    image = load_image("bullet.jpg", -1)
    image = pygame.transform.scale(image, (30, 20))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Bullet.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.vy = 0
        self.speed = 10

    def update(self):
        self.rect = self.rect.move(self.speed, self.vy)

        # если промах, то удаляется из группы
        if not self.rect.colliderect(screen_rect):
            self.kill()

        # если попадает в корабль, то удаляется из группы
        if pygame.sprite.spritecollide(self, all_SpaceShip, True):
            all_bullets.remove(self)
            create_particles((self.rect.x, self.rect.y))

# создаем класс пуль ПРОТИВНИКА
class Bullet_Enemy(pygame.sprite.Sprite):
    image = load_image("boom.png")
    image = pygame.transform.scale(image, (20, 20))

    def __init__(self, group, pos):
        super().__init__(group)
        self.image = Bullet_Enemy.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.vy = 0
        self.speed = -10

    def update(self):
        self.rect = self.rect.move(self.speed, self.vy)

        # если промах, то удаляется из группы
        if not self.rect.colliderect(screen_rect):
            self.kill()

        elif pygame.sprite.spritecollide(self, all_bullets, True):
            self.kill()
            create_particles((self.rect.x, self.rect.y))

        elif pygame.sprite.spritecollideany(self, all_sprites):
            all_Bullet_Enemy.remove(self)
            create_particles((self.rect.x, self.rect.y))

# создадим класс, разлетающугося взрыва
class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_Particle)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

    def update(self):
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6]  # range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))

# создадим группу, содержащую все спрайты
all_sprites = pygame.sprite.Group()
all_dragon = pygame.sprite.Group()

# создадим группу, содержащую все шарики(пули)
all_bullets = pygame.sprite.Group()

# создадим группу, содержащую все пули ПРОТИВНИКА
all_Bullet_Enemy = pygame.sprite.Group()

helicopter = AnimatedSprite(load_image("helicopter.png", -1), 1, 4, 50, 150)
all_sprites = pygame.sprite.Group(helicopter)

# создадим группу, содержащую все корабли ПРОТИВНИКА
all_SpaceShip = pygame.sprite.Group()

SpaceShip_image = load_image("fw190a8.jpg", -1)
SpaceShip_image = pygame.transform.scale(SpaceShip_image, (100, 50))
x1, y1 = SpaceShip_image.get_rect().size

# создадим группу, разлетающугося взрыва
all_Particle = pygame.sprite.Group()

fon = pygame.transform.scale(load_image("Mountain.jpg"), (width, height))

running = True
while running:
    screen.blit(fon, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:  # выстрел
            if event.key == pygame.K_SPACE:
                Bullet(all_bullets, (helicopter.rect.x + 150, helicopter.rect.y + 50))

        if event.type == pygame.USEREVENT:  # появление кораблей ПРОТИВНИКА
            for i in range(1):
                SpaceShip(all_SpaceShip)
            for j in all_SpaceShip:  # выстрел кораблей ПРОТИВНИКА
                Bullet_Enemy(all_Bullet_Enemy, (j.rect.x, j.rect.y + 15))

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        if helicopter.rect.x >= 0:
            helicopter.rect.x -= 6
    elif keys[pygame.K_RIGHT]:
        if helicopter.rect.x <= width - 180:
            helicopter.rect.x += 6
    elif keys[pygame.K_UP]:
        if helicopter.rect.y >= 30:
            helicopter.rect.y -= 6
    elif keys[pygame.K_DOWN]:
        if helicopter.rect.y <= height - 70:
            helicopter.rect.y += 6

    all_sprites.update()
    all_sprites.draw(screen)

    all_bullets.draw(screen)
    all_bullets.update()

    all_Bullet_Enemy.draw(screen)
    all_Bullet_Enemy.update()

    all_SpaceShip.draw(screen)
    all_SpaceShip.update()

    all_Particle.draw(screen)
    all_Particle.update()


    pygame.display.flip()
    clock.tick(20)