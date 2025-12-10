import pgzrun
from pygame import Rect
from pgzero.actor import Actor

# CONFIGURAÇÕES GLOBAIS

WIDTH = 800
HEIGHT = 600
TITLE = "Test for Tutor Game - Robson William Silva Abreu"

C_SKY = (100, 200, 255)
C_PLATFORM = (100, 100, 100)

GRAVITY = 0.8
JUMP_FORCE = -14
SPEED = 5
TILE_SIZE = 50 
GROUND_Y = 550 


# VARIÁVEIS DO JOGO

game_state = "menu"
music_on = True
win_timer = 0
WIN_DELAY = 3.0
score = 0
high_score = 0
game_timer = 0


# CLASSES


class Button:
    def __init__(self, rect, text, action, font_size=40, color=(255, 255, 255), bg_color=(0, 0, 0, 150)):
        self.rect = rect
        self.text = text
        self.action = action
        self.font_size = font_size
        self.color = color
        self.bg_color = bg_color

    def draw(self, screen):
        screen.draw.filled_rect(self.rect, self.bg_color)
        screen.draw.text(self.text, center=self.rect.center, fontsize=self.font_size, color=self.color)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Player:
    def __init__(self, pos):
        try:
            self.actor = Actor('player_idle0', pos=pos)
        except Exception:
            print("AVISO: Imagens do player não encontradas")
            self.actor = Actor('player_idle0', pos=pos)
            
        self.hitbox = Rect(self.actor.x - 15, self.actor.y - 15, 30, 30)
        self.vy = 0
        self.grounded = False
        self.alive = True
        self.can_double_jump = True
        self.dash_cooldown = 0
        self.dash_speed = 15
        self.jump_pressed = False

    def handle_input(self):
        if not self.alive: 
            return

        moving = False
        
        if keyboard.left or keyboard.a: 
            self.actor.x -= SPEED
            self.actor.flip_x = True
            moving = True
        if keyboard.right or keyboard.d: 
            self.actor.x += SPEED
            self.actor.flip_x = False
            moving = True
        
        if (keyboard.lshift or keyboard.rshift) and self.dash_cooldown <= 0:
            dash_direction = -1 if self.actor.flip_x else 1
            self.actor.x += self.dash_speed * dash_direction
            self.dash_cooldown = 0.5
            if music_on:
                try: 
                    sounds.sfx_jump.play()
                except: 
                    pass
        
        jump_key_down = keyboard.space or keyboard.up
        
        if jump_key_down and not self.jump_pressed:
            if self.grounded:
                if music_on: 
                    try: 
                        sounds.sfx_jump.play()
                    except: 
                        pass
                
                self.vy = JUMP_FORCE
                self.actor.image = 'player_jump0'
                self.grounded = False
                self.can_double_jump = True
                
            elif self.can_double_jump:
                if music_on: 
                    try: 
                        sounds.sfx_jump.play()
                    except: 
                        pass
                self.vy = JUMP_FORCE * 0.8
                self.can_double_jump = False
        
        self.jump_pressed = jump_key_down
            
        if not self.grounded: 
            self.actor.image = 'player_jump0'
        elif moving: 
            self.actor.image = 'player_run0'
        elif keyboard.down or keyboard.s:
            self.actor.image = 'player_down0'
        else:
            self.actor.image = 'player_idle0'
    
    def update_cooldowns(self, dt):
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt

    def apply_physics(self):
        if not self.alive:
            return

        self.vy += GRAVITY
        self.actor.y += self.vy
        self.hitbox.center = (self.actor.x, self.actor.y)
        
        if self.actor.left < 0: 
            self.actor.left = 0
        if self.actor.right > WIDTH: 
            self.actor.right = WIDTH

    def check_platform_collision(self, platform_rect, is_moving_platform=False, platform_vx=0):
        if not self.hitbox.colliderect(platform_rect):
            return False

        if self.vy > 0:
            if self.hitbox.bottom <= platform_rect.bottom:
                if music_on and self.vy > 2: 
                    try: 
                        sounds.sfx_bump.play()
                    except: 
                        pass

                self.hitbox.bottom = platform_rect.top
                self.actor.y = self.hitbox.center[1] 
                self.vy = 0
                self.grounded = True
                
                if is_moving_platform:
                    self.actor.x += platform_vx 
                    self.hitbox.center = (self.actor.x, self.actor.y)
                return True
        
        return False

    def draw(self):
        self.actor.draw()
        
    def reset(self):
        self.actor.pos = (50, 50)
        self.hitbox.center = (50, 50) 
        self.vy = 0
        self.actor.image = 'player_idle0'
        self.grounded = False
        self.alive = True
        self.can_double_jump = True
        self.dash_cooldown = 0
        self.jump_pressed = False
        

class Platform:
    def __init__(self, rect, color=C_PLATFORM, use_sprite=False):
        self.rect = rect
        self.color = color
        self.use_sprite = use_sprite
        
        if self.use_sprite:
            self.tiles = []
            tile_size = 50
            num_tiles_x = int(self.rect.width / tile_size)
            if self.rect.width % tile_size != 0:
                num_tiles_x += 1
            
            for i in range(num_tiles_x):
                tile_x = self.rect.x + (i * tile_size)
                tile_y = self.rect.y
                try:
                    tile = Actor('platformbg', topleft=(tile_x, tile_y))
                except:
                    print("AVISO: Sprite 'platformbg' não encontrado")
                    tile = None
                self.tiles.append(tile)

    def draw(self):
        if self.use_sprite and self.tiles:
            for tile in self.tiles:
                if tile:
                    tile.draw()
        else:
            screen.draw.filled_rect(self.rect, self.color)


class MovingPlatform(Platform):
    def __init__(self, x, y, width, height, vx, limit_left, limit_right, use_sprite=False):
        super().__init__(Rect(x, y, width, height), use_sprite=use_sprite)
        self.vx = vx
        self.limit_left = limit_left
        self.limit_right = limit_right

    def update(self):
        self.rect.x += self.vx
        if self.rect.left < self.limit_left:
            self.rect.left = self.limit_left
            self.vx *= -1
        elif self.rect.right > self.limit_right:
            self.rect.right = self.limit_right
            self.vx *= -1
        
        if self.use_sprite and self.tiles:
            tile_size = 50
            for i, tile in enumerate(self.tiles):
                if tile:
                    tile.x = self.rect.x + (i * tile_size) + (tile_size / 2)
                    tile.y = self.rect.y + (tile_size / 2)


class Enemy:
    def __init__(self, frames, frame_rate, pos, vx=0):
        try:
            self.actor = Actor(frames[0], pos=pos)
        except Exception:
            print(f"AVISO: Imagens do inimigo {frames[0]} não encontradas")
            self.actor = Actor('slime1', pos=pos) 
            
        self.frames = frames
        self.frame_rate = frame_rate
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.vx = vx

    def animate(self, dt):
        self.frame_timer += dt 
        if self.frame_timer >= self.frame_rate:
            self.frame_timer = 0.0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
            self.actor.image = self.frames[self.current_frame_index]
            
    def update(self, dt):
        self.animate(dt)

    def draw(self):
        self.actor.draw()
        
    def check_collision(self, player_hitbox):
        return player_hitbox.colliderect(self.actor._rect)
        
    def reset(self):
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.actor.image = self.frames[0]


class SlimeEnemy(Enemy):
    def __init__(self, frames, frame_rate, pos, vx, limit_left, limit_right):
        super().__init__(frames, frame_rate, pos, vx)
        self.initial_pos = pos
        self.limit_left = limit_left
        self.limit_right = limit_right
        
    def update(self, dt):
        super().update(dt)
        
        self.actor.x += self.vx
        
        if self.actor.x > self.limit_right:
            self.actor.x = self.limit_right
            self.vx *= -1
        elif self.actor.x < self.limit_left:
            self.actor.x = self.limit_left
            self.vx *= -1
            
        if self.vx > 0: 
            self.actor.flip_x = False 
        elif self.vx < 0: 
            self.actor.flip_x = True

    def reset(self):
        super().reset()
        self.actor.pos = self.initial_pos
        self.vx = abs(self.vx) 


class BeeEnemy(SlimeEnemy): 
    def __init__(self, frames, frame_rate, pos, vx, limit_left, limit_right, scale=1.0):
        super().__init__(frames, frame_rate, pos, vx, limit_left, limit_right)
        self.actor.scale = scale


# OBJETOS DO JOGO


player = Player((50, 50))

try:
    goal_actor = Actor('door1', pos=(720, 125))
    goal_actor.scale = 1.0
except Exception:
    print("AVISO: Sprite 'door1' não encontrado")
    goal_actor = Actor('door1', pos=(720, 125))

goal = Rect(700, 100, 40, 40)

platforms_static = [
    Platform(Rect(200, 450, 200, 20), use_sprite=True),
    Platform(Rect(500, 350, 200, 20), use_sprite=True),
    Platform(Rect(150, 250, 150, 20), use_sprite=True),
    Platform(Rect(420, 250, 50, 20), use_sprite=True),
    Platform(Rect(350, 150, 100, 20), use_sprite=True), 
    Platform(Rect(0, GROUND_Y, WIDTH, TILE_SIZE), C_PLATFORM, use_sprite=False)
]

moving_platform_obj = MovingPlatform(600, 150, 50, 20, 1.5, 550, 750, use_sprite=True)

bee_enemy = BeeEnemy(
    frames=['bee1', 'bee2', 'bee3', 'bee4'], 
    frame_rate=0.1, 
    pos=(500, 290), 
    vx=1.6, 
    limit_left=500, 
    limit_right=700,
    scale=1.2
)

slime_enemy = SlimeEnemy(
    frames=['slime1', 'slime2'], 
    frame_rate=0.25, 
    pos=(400, 130), 
    vx=1.0, 
    limit_left=360, 
    limit_right=440
)

lava_slime = SlimeEnemy(
    frames=['slime_red1', 'slime_red2'], 
    frame_rate=0.35, 
    pos=(WIDTH/2, GROUND_Y - 20), 
    vx=1.8, 
    limit_left=0, 
    limit_right=WIDTH
)

enemies = [bee_enemy, slime_enemy, lava_slime]


# FUNÇÕES DE MÚSICA


def play_menu_music():
    try:
        music.play('sound_bg1')
        music.set_volume(0.5)
    except Exception as e:
        print(f"AVISO: Música não carregada - {e}")


# FUNÇÕES DO MENU


def start_game():
    global game_state, win_timer, score, game_timer
    game_state = "playing"
    win_timer = 0
    score = 0
    game_timer = 0
    music.stop()
    if music_on: 
        play_menu_music()

def pause_game():
    global game_state
    if game_state == "playing":
        game_state = "paused"
        
def resume_game():
    global game_state
    game_state = "playing"

def show_controls():
    global game_state
    game_state = "controls"
    
def return_to_menu():
    global game_state
    reset_game()
    game_state = "menu"
    music.stop()
    if music_on:
        play_menu_music()

def toggle_sound():
    global music_on
    music_on = not music_on
    
    if not music_on:
        music.stop()
    elif game_state == "menu":
        play_menu_music()
    
    if music_on:
        try: 
            sounds.sfx_select.play() 
        except: 
            pass

def quit_game():
    import sys
    sys.exit()


# BOTÕES DOS MENUS


BUTTON_WIDTH = 300
BUTTON_HEIGHT = 50
BUTTON_Y_START = HEIGHT / 2 - 100
BUTTON_SPACING = 70

menu_buttons = [
    Button(Rect(WIDTH/2 - BUTTON_WIDTH/2, BUTTON_Y_START, BUTTON_WIDTH, BUTTON_HEIGHT), 
           "INICIAR JOGO", start_game),
    Button(Rect(WIDTH/2 - BUTTON_WIDTH/2, BUTTON_Y_START + BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT), 
           "SOM: ON/OFF", toggle_sound),
    Button(Rect(WIDTH/2 - BUTTON_WIDTH/2, BUTTON_Y_START + 2 * BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT), 
           "SAIR", quit_game)
]

pause_buttons = [
    Button(Rect(WIDTH/2 - BUTTON_WIDTH/2, BUTTON_Y_START, BUTTON_WIDTH, BUTTON_HEIGHT), 
           "CONTINUAR", resume_game),
    Button(Rect(WIDTH/2 - BUTTON_WIDTH/2, BUTTON_Y_START + BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT), 
           "CONTROLES", show_controls),
    Button(Rect(WIDTH/2 - BUTTON_WIDTH/2, BUTTON_Y_START + 2 * BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT), 
           "SOM: ON/OFF", toggle_sound),
    Button(Rect(WIDTH/2 - BUTTON_WIDTH/2, BUTTON_Y_START + 3 * BUTTON_SPACING, BUTTON_WIDTH, BUTTON_HEIGHT), 
           "MENU PRINCIPAL", return_to_menu)
]

controls_button = Button(
    Rect(WIDTH/2 - 100, HEIGHT - 100, 200, 50), 
    "VOLTAR", 
    lambda: setattr(__builtins__, 'game_state', "paused") or pause_game(),
    font_size=35
)

pause_button_ingame = Button(
    Rect(WIDTH - 120, 10, 110, 40), 
    "PAUSE", 
    pause_game,
    font_size=30,
    color=(255, 255, 255),
    bg_color=(0, 0, 0, 180)
)


# CALLBACKS PYGAME ZERO


def on_mouse_down(pos):
    global game_state
    
    if game_state == "menu":
        for button in menu_buttons:
            if button.is_clicked(pos):
                button.action()
                return
    
    elif game_state == "paused":
        for button in pause_buttons:
            if button.is_clicked(pos):
                button.action()
                return
    
    elif game_state == "controls":
        if controls_button.is_clicked(pos):
            game_state = "paused"
            return
    
    elif game_state == "playing":
        if pause_button_ingame.is_clicked(pos):
            pause_button_ingame.action()
            return

def update(dt):
    global game_state, music_on, win_timer, score, game_timer, high_score
    
    if game_state == "menu":
        if music_on and not music.is_playing("sound_bg1"):
             play_menu_music()
        elif not music_on and music.is_playing("sound_bg1"):
             music.stop()
        return
    
    elif game_state == "paused" or game_state == "controls":
        if keyboard.ESCAPE or keyboard.p:
            if game_state == "controls":
                game_state = "paused"
            else:
                resume_game()
        return
        
    elif game_state == "gameover":
        if keyboard.r: 
            if music_on: 
                try: 
                    sounds.sfx_select.play()
                except: 
                    pass
            reset_game()
        return
    
    elif game_state == "win":
        win_timer += dt
        
        if win_timer >= WIN_DELAY:
            return_to_menu()
            return
        
        if keyboard.r:
            if music_on: 
                try: 
                    sounds.sfx_select.play()
                except: 
                    pass
            reset_game()
        return

    game_timer += dt
    score = int(game_timer * 10)
    
    if keyboard.ESCAPE or keyboard.p:
        pause_game()
        return
    
    player.handle_input()
    player.update_cooldowns(dt)
    player.apply_physics()
    
    moving_platform_obj.update()
    player.grounded = False
    
    for plat_obj in platforms_static:
        if player.check_platform_collision(plat_obj.rect):
            player.can_double_jump = True
        
    if player.check_platform_collision(moving_platform_obj.rect, is_moving_platform=True, platform_vx=moving_platform_obj.vx):
        player.can_double_jump = True

    for enemy in enemies:
        enemy.update(dt)

    death_occurred = False
    if player.actor.top > HEIGHT: 
        death_occurred = True
        
    for enemy in enemies:
        if enemy.check_collision(player.hitbox):
            death_occurred = True
            
    if death_occurred:
        game_state = "gameover"
        if music_on: 
            try: 
                sounds.sfx_hurt.play()
            except: 
                pass
        music.stop()
        
    if player.hitbox.colliderect(goal):
        game_state = "win"
        win_timer = 0
        
        time_bonus = max(0, int((60 - game_timer) * 20))
        score += time_bonus + 1000
        
        if score > high_score:
            high_score = score
        
        if music_on: 
            try: 
                sounds.sfx_gem.play()
            except: 
                pass
        music.stop()


def draw_tiles():
    num_tiles = WIDTH // TILE_SIZE 
    if WIDTH % TILE_SIZE != 0: 
        num_tiles += 1
    for i in range(num_tiles):
        screen.blit('bg_ground', (i * TILE_SIZE, GROUND_Y))

def draw():
    global game_state
    
    if game_state == "menu":
        try:
            screen.blit('bg_menu', (0, 0))
        except:
            screen.fill((50, 50, 50))
            screen.draw.text(TITLE, center=(WIDTH/2, BUTTON_Y_START - 50), fontsize=70, color="white")
        
        if high_score > 0:
            screen.draw.text(f"HIGH SCORE: {high_score}", center=(WIDTH/2, BUTTON_Y_START - 14), 
                           fontsize=20, color="yellow")
            
        menu_buttons[1].text = f"SOM: {'ON' if music_on else 'OFF'}"
        
        for button in menu_buttons:
            button.draw(screen)
        
        return
    
    if game_state == "controls":
        screen.fill((30, 30, 50))
        
        screen.draw.text("CONTROLES", center=(WIDTH/2, 80), fontsize=60, color="white")
        
        controls_text = [
            ("MOVIMENTAÇÃO", ""),
            ("A / D  ou  Left / Right", "Mover para esquerda/direita"),
            ("", ""),
            ("PULO", ""),
            ("ESPAÇO  ou  Top", "Pular"),
            ("ESPAÇO (2x no ar)", "Pulo Duplo"),
            ("", ""),
            ("HABILIDADES", ""),
            ("SHIFT", "Dash (corrida rápida)"),
            ("", ""),
            ("SISTEMA", ""),
            ("ESC  ou  P", "Pausar jogo"),
        ]
        
        y_pos = 150
        for title, desc in controls_text:
            if title and not desc:
                screen.draw.text(title, center=(WIDTH/2, y_pos), fontsize=32, color="yellow")
                y_pos += 40
            elif title:
                screen.draw.text(title, midleft=(150, y_pos), fontsize=24, color=(100, 200, 255))
                screen.draw.text(desc, midleft=(380, y_pos), fontsize=20, color="white")
                y_pos += 30
            else:
                y_pos += 10
        
        controls_button.draw(screen)
        screen.draw.text("Pressione ESC para voltar", center=(WIDTH/2, HEIGHT - 40), fontsize=20, color="gray")
        return
    
    if game_state == "paused":
        screen.fill(C_SKY)
        draw_tiles()
        
        for platform_obj in platforms_static[:-1]: 
            platform_obj.draw()

        moving_platform_obj.draw()
        goal_actor.draw()
        
        for enemy in enemies:
            enemy.draw()
            
        player.draw()
        
        screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0, 180))
        screen.draw.text("PAUSADO", center=(WIDTH/2, BUTTON_Y_START - 50), fontsize=70, color="white")
        
        pause_buttons[2].text = f"SOM: {'ON' if music_on else 'OFF'}"
        
        for button in pause_buttons:
            button.draw(screen)
        
        screen.draw.text("Pressione ESC ou P para continuar", center=(WIDTH/2, HEIGHT - 40), fontsize=25, color="white")
        return
        
    screen.fill(C_SKY)
    draw_tiles()
    
    for platform_obj in platforms_static[:-1]: 
        platform_obj.draw()

    moving_platform_obj.draw()
    goal_actor.draw()
    
    for enemy in enemies:
        enemy.draw()
        
    player.draw()
    
    if game_state == "playing":
        pause_button_ingame.draw(screen)
        
        screen.draw.text(f"SCORE: {score}", topleft=(10, 10), fontsize=30, color="white", 
                        owidth=1, ocolor="black")
        screen.draw.text(f"TIME: {int(game_timer)}s", topleft=(10, 45), fontsize=25, color="white",
                        owidth=1, ocolor="black")
        
        if player.dash_cooldown > 0:
            dash_color = (255, 100, 100)
            dash_text = f"DASH: {player.dash_cooldown:.1f}s"
        else:
            dash_color = (100, 255, 100)
            dash_text = "DASH: PRONTO"
        
        screen.draw.text(dash_text, topleft=(10, 75), fontsize=20, color=dash_color,
                        owidth=1, ocolor="black")
        
        if player.can_double_jump and not player.grounded:
            screen.draw.text("PULO DUPLO OK", topleft=(10, 100), fontsize=20, 
                           color=(100, 200, 255), owidth=1, ocolor="black")
    
    if game_state == "gameover":
        screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (0, 0, 0, 150))
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2 - 60), fontsize=60, color="red")
        screen.draw.text(f"Score Final: {score}", center=(WIDTH/2, HEIGHT/2), fontsize=40, color="white")
        screen.draw.text(f"Tempo: {int(game_timer)}s", center=(WIDTH/2, HEIGHT/2 + 40), fontsize=30, color="white")
        screen.draw.text("Press R to Restart", center=(WIDTH/2, HEIGHT/2 + 80), fontsize=40, color="red")
        
    elif game_state == "win":
        screen.draw.filled_rect(Rect(0, 0, WIDTH, HEIGHT), (255, 255, 255, 150))
        screen.draw.text("VENCEU!", center=(WIDTH/2, HEIGHT/2 - 80), fontsize=60, color="green")
        screen.draw.text(f"Score Final: {score}", center=(WIDTH/2, HEIGHT/2 - 20), fontsize=40, color="green")
        screen.draw.text(f"Tempo: {int(game_timer)}s", center=(WIDTH/2, HEIGHT/2 + 20), fontsize=30, color="green")
        
        time_left = WIN_DELAY - win_timer
        if time_left > 0:
            screen.draw.text(f"Voltando ao menu em {time_left:.1f}s...", 
                           center=(WIDTH/2, HEIGHT/2 + 60), fontsize=30, color="green")
        
        screen.draw.text("Press R to Restart", center=(WIDTH/2, HEIGHT/2 + 100), fontsize=25, color="green")


# RESET DO JOGO

def reset_game():
    global game_state, win_timer, score, game_timer
    
    player.reset()
    win_timer = 0
    score = 0
    game_timer = 0

    if music_on:
        play_menu_music()

    moving_platform_obj.rect.x = moving_platform_obj.limit_left
    moving_platform_obj.vx = abs(moving_platform_obj.vx)
    
    for enemy in enemies:
        enemy.reset()

    game_state = "playing"


# THE START OF THE GAME

if music_on:
    play_menu_music()


pgzrun.go()
