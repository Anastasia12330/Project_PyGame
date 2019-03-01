import pygame, os, random, sys, time

pygame.init()
size = width, height = 1000, 600
screen = pygame.display.set_mode(size)

pygame.display.set_caption('ВОЗДУШНЫЙ БОЙ')
info_string = pygame.Surface((width, 30))
clock = pygame.time.Clock()

pygame.time.set_timer(pygame.USEREVENT, 3000)

screen_rect = (0, 0, width, height)

TEXT_MENU = ['Легкая игра', 'Сложная игра', 'Инструкции', 'РЕКОРД', 'ВЫХОД', 'Продолжить']
DURATION = 60  # ВРЕМЯ игры
SCORE = 0
LIFE = 100
N = 1
N_MENU = 5
TIME = TIME_END = TIME_BEGIN = DURATION  # ВРЕМЯ игры
TIMER = 0


def load_image(name, color_key=None):
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
        image = image.convert_alpha(screen)
    return image


# Анимация спрайтов
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_helicopters)
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
        global SCORE
        self.rect = self.rect.move(self.speed, self.vy)

        # если промах, то удаляется из группы
        if not self.rect.colliderect(screen_rect):
            self.kill()

        # если попадает в корабль, то удаляется из группы
        elif pygame.sprite.spritecollide(self, all_SpaceShip, True):
            all_bullets.remove(self)
            create_particles((self.rect.x, self.rect.y))
            SCORE += 1

        elif pygame.sprite.spritecollide(self, all_Bullet_Enemy, True):
            self.kill()
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
        global SCORE, LIFE
        self.rect = self.rect.move(self.speed, self.vy)

        # если промах, то удаляется из группы
        if not self.rect.colliderect(screen_rect):
            self.kill()

        elif pygame.sprite.spritecollideany(self, all_helicopters):
            all_Bullet_Enemy.remove(self)
            create_particles((self.rect.x, self.rect.y))
            LIFE -= 10


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
    numbers = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6]
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


# создаем класс самолетов ПРОТИВНИКА
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
        global LIFE, SCORE

        # если корабль сталкивается с вертолетом конец игры
        if pygame.sprite.spritecollideany(self, all_helicopters):
            all_SpaceShip.remove(self)
            create_particles((self.rect.x, self.rect.y))
            LIFE = 0
        elif self.rect.x > - x1:
            self.rect.x -= self.speed
        # убиваем, если корабль ушел за экран
        elif not self.rect.colliderect(screen_rect):
            self.kill()


# Преждевременный выход из игры ,«аварийное завершение»
def terminate():
    pygame.quit()
    sys.exit()


# ЗАСТАВКА
def begin_screen():
    fon = pygame.transform.scale(load_image('vertolet.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 60)
    text = font.render("ВОЗДУШНЫЙ БОЙ", 1, (100, 255, 100))
    text_x = width // 2 - text.get_width() // 2
    text_y = (height // 6) * 5 - text.get_height() // 2
    screen.blit(text, (text_x, text_y))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(50)


# создаем класс выбора меню
class Button(pygame.sprite.Sprite):
    def __init__(self, radius, x, y, i):
        super().__init__(all_Buttons)
        self.radius = radius
        self.image = pygame.Surface((2 * radius, 2 * radius),
                                    pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, pygame.Color("red"),
                           (radius, radius), radius)
        self.rect = pygame.Rect(x, y, 2 * radius, 2 * radius)
        self.text = TEXT_MENU[i]

    def get_event(self, event, bool=False):
        global MENU
        if self.rect.collidepoint(event.pos):
            pygame.draw.circle(self.image, pygame.Color("green"),
                               (self.radius, self.radius), self.radius)
            if bool:
                MENU = self.text
        else:
            pygame.draw.circle(self.image, pygame.Color("red"),
                               (self.radius, self.radius), self.radius)


# МЕНЮ игры
def menu_screen():
    global TEXT_MENU, MENU, N_MENU

    MENU = 'Меню'
    for i in range(N_MENU):
        Button(25, 40, i * 100 + 20, i)
    while True:
        screen.fill(pygame.Color("white"))
        for i in range(N_MENU):
            font = pygame.font.Font(None, 50)
            text1 = font.render(TEXT_MENU[i], 1, (0, 0, 0))
            text1_x = 150
            text1_y = i * 100 + 30
            screen.blit(text1, (text1_x, text1_y))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEMOTION:
                for enemy in all_Buttons:
                    enemy.get_event(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for enemy in all_Buttons:
                    enemy.get_event(event, True)
                return MENU
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'Продолжить'
        all_Buttons.draw(screen)
        all_Buttons.update()
        pygame.display.flip()
        clock.tick(20)


# ИНСТРУКЦИЯ, Правила игры
def rules_screen():
    intro_text = ["                       ПРАВИЛА ИГРЫ", "",
                  "Чтобы победить, Вы должны за 60 секунд сбить как можно больше",
                  "самолетов  противника, получая при этом очки. Уклоняйтесь от пуль противника",
                  "",
                  "Существует два уровня сложности : легкая и сложная игра",
                  "",
                  "Для движения налево нажмите клавишу <стрелка влево>,",
                  "Направо - <стрелка влево>,",
                  "Вверх   - <стрелка вверх>,",
                  "Вниз    - <стрелка вниз>,",
                  "Выстрел - <пробел>,",
                  "Выход из игры - ESCAPE",
                  "Вернуться в игру - ESCAPE"]

    screen.fill((255, 255, 0))
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
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(50)


# РЕКОРД
def records_screen():
    global SCORE

    filename = os.path.join('data', 'records.txt')
    with open(filename, 'r+') as File:
        data = File.readline().strip()
        if data == '' or int(data) < SCORE:
            data = str(SCORE)
            File.seek(0)
            File.write(data)

    fon = pygame.transform.scale(load_image('Winner_Banner.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 80)
    text = font.render("РЕКОРД : " + data, 1, (255, 0, 100))
    text_x = width // 2 - text.get_width() // 2
    text_y = (height // 3) - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    screen.blit(text, (text_x, text_y))
    pygame.draw.rect(screen, (255, 0, 100), (text_x - 10, text_y - 10,
                                             text_w + 20, text_h + 20), 2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(50)


# создаем класс конец игры
class GameOver(pygame.sprite.Sprite):
    def __init__(self, x, filename):
        super().__init__()
        self.image = load_image(filename)
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0
        self.dx = 4

    def update(self):
        self.rect.x -= self.dx
        if self.rect.x == width - x_image_game_over:
            self.dx = 0


# создаем функцию(ЭКРАН) конец игры
def gameover_screen():
    screen.fill(pygame.Color('blue'))
    font = pygame.font.Font(None, 24)
    pause = "                                                                       "
    text = font.render("SCORE : " + str(SCORE) + pause + "author : Stepina Anastasiia", 1, (255, 255, 255))
    text_y = (height // 6) * 5 - text.get_height() // 2
    gameover = GameOver(width, 'gameover.jpg')
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
        screen.blit(gameover.image, gameover.rect)
        gameover.update()
        screen.blit(text, (gameover.rect.x + width // 2 - text.get_width() // 2, text_y))
        pygame.display.flip()
        clock.tick(200)


# создаем функцию новой игры
def new_game():
    global TIME, TIME_END, TIME_BEGIN, SCORE, LIFE

    for group in ALL_GROUPS:
        for enemy in group:
            enemy.kill()
    TIME = TIME_END = TIME_BEGIN = DURATION
    SCORE = 0
    LIFE = 100
    helicopter.rect.x, helicopter.rect.y = 10, height // 2 - 50


# создадим группу, содержащую все спрайты вертолета
all_helicopters = pygame.sprite.Group()

# создадим группу, содержащую все пули
all_bullets = pygame.sprite.Group()

# создадим группу, содержащую все пули ПРОТИВНИКА
all_Bullet_Enemy = pygame.sprite.Group()

# создадим группу, разлетающугося взрыва
all_Particle = pygame.sprite.Group()

# создадим группу клавиш меню
all_Buttons = pygame.sprite.Group()

# создадим группу, содержащую все корабли ПРОТИВНИКА
all_SpaceShip = pygame.sprite.Group()

# создадим список всех групп
ALL_GROUPS = [all_bullets, all_Bullet_Enemy, all_Particle, all_SpaceShip]

SpaceShip_image = load_image("fw190a8.jpg", -1)
SpaceShip_image = pygame.transform.scale(SpaceShip_image, (100, 50))
x1, y1 = SpaceShip_image.get_rect().size

helicopter = AnimatedSprite(load_image("helicopter.png", -1), 1, 4, 10, height // 2 - 50)
all_helicopters = pygame.sprite.Group(helicopter)

# создадим подсчет количества ЖИЗНИ , счет сбитых самолетов и времени
SCORE_font = pygame.font.Font(None, 30)
LIFE_font = pygame.font.Font(None, 30)
TIME_font = pygame.font.Font(None, 30)

# создадим фон игрового экрана
fon = pygame.transform.scale(load_image("Mountain.jpg"), (width, height))

# создадим звуковую (фоновую) заставку
sound = os.path.join('data', '00545.mp3')
pygame.mixer.music.load(sound)
pygame.mixer.music.play(-1)

# создадим спрайт конец игры
image_game_over = load_image('gameover.jpg')
image_game_over = pygame.transform.scale(image_game_over, (width, height))
x_image_game_over, y_image_game_over = image_game_over.get_rect().size

running = running_begin = True
running_rules = running_menu = running_game = running_records = running_end = hard_game = False

while running:
    pygame.mixer.music.pause()
    # ЗАСТАВКА
    if running_begin:
        begin_screen()
        running_begin = False
        running_menu = True

    # МЕНЮ
    if running_menu:
        running_menu = False
        t_f = menu_screen()
        if t_f == 'Легкая игра':
            running_game = True
            hard_game = False
            new_game()
            start_time = time.clock()
        elif t_f == 'Сложная игра':
            running_game = True
            hard_game = True
            new_game()
            start_time = time.clock()
        elif t_f == 'Инструкции':
            running_rules = True
        elif t_f == 'РЕКОРД':
            running_records = True
        elif t_f == 'ВЫХОД':
            terminate()
        elif t_f == 'Продолжить':
            start_time = time.clock()
            running_game = True
        elif t_f == 'Меню':
            running_menu = True

    # Правила
    if running_rules:
        rules_screen()
        running_rules = False
        running_menu = True

    # РЕКОРДЫ
    if running_records:
        records_screen()
        running_records = False
        running_menu = True
        pass

    # КОНЕЦ игры
    if running_end:
        gameover_screen()
        LIFE = 100
        N_MENU = 5
        for enemy in all_Buttons:
            if enemy.text == 'Продолжить':
                enemy.kill()
        running_end = False
        running_menu = True

    # ИГРА
    while running_game:
        # откючаем мышку
        pygame.mouse.set_visible(False)

        # снимаем музыку с паузы
        pygame.mixer.music.unpause()
        screen.blit(fon, (0, 0))

        # отрисовка информационного табло
        info_string.fill((45, 80, 45))
        screen.blit(info_string, (0, 0))

        # задаем количество кораблей ПРОТИВНИКА от времени игры
        if N < 3:
            N = (TIME_BEGIN - TIME_END) // 20 + 1

        # если время истекло, конец игры
        if TIMER < int(time.clock()):
            TIME_END = TIME - int(time.clock() - start_time)
            TIMER += 1
        if TIME_END <= 0 or LIFE <= 0:
            running_end = True
            running_game = False
            pygame.mouse.set_visible(True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            elif event.type == pygame.KEYDOWN:  # выстрел
                if event.key == pygame.K_SPACE:
                    Bullet(all_bullets, (helicopter.rect.x + 150, helicopter.rect.y + 50))

            if event.type == pygame.USEREVENT:  # появление кораблей ПРОТИВНИКА
                for i in range(N):
                    SpaceShip(all_SpaceShip)
                if hard_game:  # сложный уровень противник начинает стрелять
                    for j in all_SpaceShip:  # выстрел кораблей ПРОТИВНИКА
                        Bullet_Enemy(all_Bullet_Enemy, (j.rect.x, j.rect.y + 15))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(True)
                    TIME = TIME - int(time.clock() - start_time)
                    N_MENU = 6
                    running_menu = True
                    running_game = False

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

        all_helicopters.update()
        all_helicopters.draw(screen)

        all_bullets.draw(screen)
        all_bullets.update()

        all_Bullet_Enemy.draw(screen)
        all_Bullet_Enemy.update()

        all_Particle.draw(screen)
        all_Particle.update()

        all_SpaceShip.draw(screen)
        all_SpaceShip.update()

        # отрисовка счета и ЖИЗНИ
        text_SCORE = SCORE_font.render('SCORE :   ' + str(SCORE), 1, (250, 250, 250))
        screen.blit(text_SCORE, (10, 5))
        text_LIFE = LIFE_font.render('LIFE :   ' + str(LIFE), 1, (250, 250, 250))
        screen.blit(text_LIFE, (width - 150, 5))
        text_TIME = TIME_font.render('TIME :   ' + str(TIME_END), 1, (250, 250, 250))
        screen.blit(text_TIME, (width // 2 - 50, 5))

        pygame.display.flip()
        clock.tick(20)
