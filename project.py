import pygame
import random
from copy import deepcopy

# загрузка констант - номера клавиш "вверх", "вниз" и т.п.
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

step = 5
# размер панели информации (показ уровня, количества жизней)
panel_height = 100
SCREEN_WIDTH = 70*12
SCREEN_HEIGHT = panel_height + 70*8

# спрайт игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_site = 50
        self.surf = pygame.Surface((player_site, player_site))
        self.surf = pygame.transform.scale(pygame.image.load("player.png").convert(),(player_site,player_site))
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(center=(100, 200))

    # обновление координат игрока в зависимости от нажатия клавиш (вверх, вниз и т.п.)
    def update(self, pressed_keys):
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -step)
        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, step)
        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-step, 0)
        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(step, 0)

# спрайт врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        enemy_size = 50
        self.surf = pygame.Surface((enemy_size, enemy_size))
        self.surf = pygame.transform.scale(pygame.image.load("enemy.png").convert(),(enemy_size,enemy_size))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect(topleft = (random.randint(0, SCREEN_WIDTH - enemy_size), random.randint(panel_height, SCREEN_HEIGHT - enemy_size)))

    # обновление позиции спрайта врага
    def update(self, player):
        self.rect.move_ip(random.randint(-3, 3) + (player.rect.x - self.rect.x) // 100, random.randint(-3, 3) + (player.rect.y - self.rect.y) // 100)

# спрайт кристалла
class Crystal(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        crystal_size = 30
        self.surf = pygame.Surface((crystal_size, crystal_size))
        # случайным образом выбираем показывать золотой или синий кристалл
        if random.randint(0, 1) == 1:
            self.is_gold = True
            crystal_file = "crystal-gold.png"
        else:
            self.is_gold = False
            crystal_file = "crystal-blue.png"
        self.surf = pygame.transform.scale(pygame.image.load(crystal_file).convert(),(crystal_size,crystal_size)).convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(center = (random.randint(0, SCREEN_WIDTH), random.randint(panel_height, SCREEN_HEIGHT)))

# спрайт дверь
class Door(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((100, 100))
        self.surf = pygame.transform.scale(pygame.image.load("door.png").convert(),(100,100)).convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(center = (random.randint(0, SCREEN_WIDTH), random.randint(panel_height, SCREEN_HEIGHT)))

# спрайт стена
class Wall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        wall_size = 70
        self.surf = pygame.Surface((wall_size, wall_size))
        self.surf = pygame.transform.scale(pygame.image.load("wall.png").convert(),(wall_size,wall_size)).convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        # вычисления количества возможных блоков типа стена по горизонтали и вертикали
        # т.к. блоки могут показываться только в определенных позициях, чтобы они не перекрывались
        size_h = (SCREEN_HEIGHT - panel_height) // wall_size
        size_w = SCREEN_WIDTH // wall_size
        self.rect = self.surf.get_rect(topleft = (random.randint(0, size_w)*wall_size,
                                                  panel_height + random.randint(0, size_h)*wall_size))

# спрайт картинки начальной сцены
class IntroductionPhoto(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((100,100))
        self.surf = pygame.image.load("introduction.png").convert()
        self.surf.set_colorkey((0, 0, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center = (SCREEN_WIDTH / 2 , SCREEN_HEIGHT / 2 - 100))

# спрайт картинки конца игры
class GameOverPhoto(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((100,100))
        self.surf = pygame.image.load("gameover.png").convert()
        self.surf.set_colorkey((0, 0, 255), RLEACCEL)
        self.rect = self.surf.get_rect(center = (SCREEN_WIDTH / 2 , SCREEN_HEIGHT / 2 - 100))

# спрайт кнопки новая игра
class ButtonNewGame(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((100, 100))
        self.surf = pygame.image.load("button-new-game.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(topleft = (100,500))

# спрайт кнопки конец игры
class ButtonExitGame(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.surf = pygame.Surface((100, 100))
        self.surf = pygame.image.load("button-exit-game.png").convert()
        self.surf.set_colorkey((0, 0, 0), RLEACCEL)
        self.rect = self.surf.get_rect(topleft = (500,500))

# класс игра
class Game:
    # установка началтных значений
    def first_level(self):
        self.points = 0
        self.level = 0
        self.lives = 5

    def __init__(self):
        pygame.mixer.init()
        pygame.init()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        pygame.display.set_caption("Game")
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        self.running = True
        self.first_level()
        self.need_next_level = False
        self.scene_number = 0
        self.button_new_game = ButtonNewGame()
        self.button_exit_game = ButtonExitGame()
        self.introduction_photo = IntroductionPhoto()
        self.game_over_photo = GameOverPhoto()

    # функция начала нового уровня
    def next_level(self):
        self.need_next_level = False
        self.pickup_crystal_sound = pygame.mixer.Sound("pickup_crystal.mp3")
        self.live_loss_sound = pygame.mixer.Sound("live_loss.mp3")
        self.live_new_sound = pygame.mixer.Sound("live_new.mp3")
        self.door_sound = pygame.mixer.Sound("door.mp3")
        self.enemy_attack_sound = pygame.mixer.Sound("enemy_attack.ogg")
        self.level += 1
        self.lives_collisions = 0
        self.all_sprites = pygame.sprite.Group()
        # игрок и другие спрайты задаются заново на новых позициях
        self.player = Player()
        self.all_sprites.add(self.player)

        self.door = Door()
        while pygame.sprite.spritecollideany(self.door, self.all_sprites):
            self.door = Door()
        self.all_sprites.add(self.door)

        self.walls = pygame.sprite.Group()
        for _ in range(20):
            wall = Wall()
            if not pygame.sprite.spritecollideany(wall, self.all_sprites):
                self.walls.add(wall)
                self.all_sprites.add(wall)

        self.crystals = pygame.sprite.Group()
        for _ in range(10):
            crystal = Crystal()
            while pygame.sprite.spritecollideany(crystal, self.all_sprites):
                crystal = Crystal()
            self.crystals.add(crystal)
            self.all_sprites.add(crystal)

        self.enemies = pygame.sprite.Group()
        for _ in range(self.level):
            enemy = Enemy()
            while pygame.sprite.spritecollideany(enemy, self.all_sprites):
                enemy = Enemy()
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    # проверка что спрайт вышел за границы экрана
    def out_of_game_area(self, rect):
        return rect.left < 0 or rect.right > SCREEN_WIDTH or rect.top < panel_height or rect.bottom > SCREEN_HEIGHT

    # рисование вводной сцены
    def draw_introduction_scene(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.introduction_photo.surf, self.introduction_photo.rect)
        self.screen.blit(self.button_new_game.surf, self.button_new_game.rect)
        self.screen.blit(self.button_exit_game.surf, self.button_exit_game.rect)

    # рисование сцены конца игры
    def draw_game_over_scene(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.game_over_photo.surf, self.game_over_photo.rect)
        self.screen.blit(self.button_new_game.surf, self.button_new_game.rect)
        self.screen.blit(self.button_exit_game.surf, self.button_exit_game.rect)

    # рисование главной сцены
    def draw_main_scene(self):
        if self.need_next_level:
            self.next_level()

        # заливка всего экрана белым цветом
        self.screen.fill((255, 255, 255))
        pressed_keys = pygame.key.get_pressed()

        # рисование стен
        for wall in self.walls:
            self.screen.blit(wall.surf, wall.rect)

        # рисование кристалов
        for crystal in self.crystals:
            self.screen.blit(crystal.surf, crystal.rect)
            if self.player.rect.colliderect(crystal.rect):
                # коснулись кристалла
                self.pickup_crystal_sound.play()
                if crystal.is_gold:
                    # за золотой кристалл получаем 10 очков
                    self.points += 10
                else:
                    self.points += 5
                # убираем кристалл
                # он удаляется из списка всех спрайтов
                crystal.kill()
                if self.points >= 100:
                    self.lives += 1
                    self.points -= 100
                    self.live_new_sound.play()

        # запоминаем область игрока
        rect = deepcopy(self.player.rect)
        self.player.update(pressed_keys)
        # если игрок сделал неверный ход (например коснулся стены или вышел за границы экрана)
        if pygame.sprite.spritecollideany(self.player, self.walls) or self.out_of_game_area(self.player.rect):
            # восстанавливаем старые координаты
            self.player.rect = rect

        # отрисовка двери и игрока
        self.screen.blit(self.door.surf, self.door.rect)
        self.screen.blit(self.player.surf, self.player.rect)

        # если игрок вошел в дверь, то переход на новый уровень
        if self.player.rect.colliderect(self.door.rect):
            self.door_sound.play()
            self.next_level()

        # отрисовка спрайтов врагов
        for enemy in self.enemies:
            rect = deepcopy(enemy.rect)
            enemy.update(self.player)
            # проверка что враг не врезался в стену или вышел за границы экрана
            if pygame.sprite.spritecollideany(enemy, self.walls) or self.out_of_game_area(enemy.rect):
                enemy.rect = rect
            self.screen.blit(enemy.surf, enemy.rect)

        # проверка что игрок коснулся врага
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            # lives_collisions - это количество "укусов"
            self.lives_collisions += 1
            if self.lives_collisions > 40:
                # если больше 40 укусов - то уменьшаем жизнь на одну
                self.lives -= 1
                self.lives_collisions = 0
                self.live_loss_sound.play()
                if self.lives == 0:
                    # если нет больше жизней - то конец игры
                    self.game_over_sound = pygame.mixer.Sound("game_over.mp3")
                    self.game_over_sound.play()
                    self.scene_number = 2
            else:
                # играем звук укуса каждые 10 укусов (чтобы звуки не накладывались друг на друга)
                if self.lives_collisions % 10 == 0:
                    self.enemy_attack_sound.play()

        # рисуем панель информации
        pygame.draw.rect(self.screen, (100, 100, 255), pygame.Rect(0, 0, SCREEN_WIDTH, panel_height))

        # рисуем очки
        img_point = self.font.render(f'Points: {self.points}', True, (200, 100, 100))
        self.screen.blit(img_point, (40, 30))

        # рисуем уровни
        img_level = self.font.render(f'Level: {self.level}', True, (100, 200, 100))
        self.screen.blit(img_level, (330, 30))

        # рисуем количество жизней
        img_lives = self.font.render(f'Lives: {self.lives}', True, (100, 100, 100))
        self.screen.blit(img_lives, (570, 30))

    def run(self):
        # загружаем и играем фоновую музыку
        pygame.mixer.music.load("background.mp3")
        pygame.mixer.music.play(loops=-1)

        # начало главного игрового цикла
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # событие - нажата кнопка мыши
                    if self.button_new_game.rect.collidepoint(pygame.mouse.get_pos()):
                        # нажата кнопка New Game
                        self.scene_number = 1
                        self.first_level()
                        self.need_next_level = True
                    elif self.button_exit_game.rect.collidepoint(pygame.mouse.get_pos()):
                        # нажата кнопка Exit Game
                        self.running = False
            # зависимости он номера сцены показываем сцену
            if self.scene_number == 0:
                self.draw_introduction_scene()
            elif self.scene_number == 2:
                self.draw_game_over_scene()
            else:
                self.draw_main_scene()
            pygame.display.flip()

            # устанавливаем количество кадров в секунду, чтобы игра не была очень быстрой
            self.clock.tick(30)

        # выход
        pygame.quit()

if __name__ == '__main__':
    Game().run()
