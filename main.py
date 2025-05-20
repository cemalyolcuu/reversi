import pygame, random, sys, time, math
from pygame.locals import *
import ai, reversi, tests
import os

def quit():
    pygame.quit()
    sys.exit()

COUNTER_SIZE = 40
TILE_SIZE = 50
COUNTER_PADDING = 5
FPS = 40

WINDOWWIDTH = TILE_SIZE * 8
WINDOWHEIGHT = TILE_SIZE * 8

class Engine_v1 (object):
    def __init__(self):
        super(Engine_v1, self).__init__()
        self.resources = {}
        self.keys_down = {}
        self.game = None

    def startup(self):
        # set up pygame, the window, and the mouse cursor
        pygame.init()
        self.main_clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Reversi')
        # pygame.mouse.set_visible(False)

        # set up fonts
        font = pygame.font.SysFont(None, 48)

        # set up sounds
        # gameOverSound = pygame.mixer.Sound('gameover.wav')
        # pygame.mixer.music.load('background.mid')

        # set up images
        self.resources['board'] = pygame.image.load('media/board.png')
        self.resources['black'] = pygame.image.load('media/black.png')
        self.resources['white'] = pygame.image.load('media/white.png')

        # Zorluk seçimi
        self.difficulty = self.select_difficulty()
        self.new_game()

    def drawText(self, text, font, surface, x, y):
        textobj = font.render(text, 1, (0,0,0))
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def draw_board(self):
        # First the board
        the_board = pygame.Rect(0, 0, WINDOWWIDTH, WINDOWHEIGHT)
        self.surface.blit(self.resources['board'], the_board)

        # Now the tiles
        for x in range(0, 8):
            for y in range(0, 8):
                player = self.game.board[x][y]
                counter = pygame.Rect(x * TILE_SIZE + COUNTER_PADDING, y * TILE_SIZE + COUNTER_PADDING, COUNTER_SIZE, COUNTER_SIZE)

                if player == 1:
                    self.surface.blit(self.resources['white'], counter)
                elif player == 2:
                    self.surface.blit(self.resources['black'], counter)

        # Has a victory occurred?
        font = pygame.font.SysFont("Helvetica", 48)
        if self.game.victory == -1:
            self.drawText("Berabere!", font, self.surface, 95, 10)
        if self.game.victory == 1:
            self.drawText("Beyaz Kazandı!", font, self.surface, 38, 10)
        if self.game.victory == 2:
            self.drawText("Siyah Kazandı!", font, self.surface, 39, 10)

        # Oyun bittiyse çıkış talimatını göster
        if self.game.victory != 0:
            exit_font = pygame.font.SysFont("Helvetica", 24)
            self.drawText("Ana menüye dönmek için 'Q' tuşuna basın", exit_font, self.surface, 120, WINDOWHEIGHT - 40)
        else:
            exit_font = pygame.font.SysFont("Helvetica", 24)
            self.drawText("Çıkmak için 'F' tuşuna basın", exit_font, self.surface, 120, WINDOWHEIGHT - 40)
            self.drawText("Hamleyi geri almak için 'Z' tuşuna basın", exit_font, self.surface, 120, WINDOWHEIGHT - 70)

        pygame.display.update()

    def handle_keydown(self, event):
        self.keys_down[event.key] = time.time()
        self.test_for_keyboard_commands()

    def handle_keyup(self, event):
        if event.key in self.keys_down:
            del(self.keys_down[event.key])

    def handle_mousedown(self, event):
        pass

    def handle_mouseup(self, event):
        x, y = event.pos
        tx = int(math.floor(x/TILE_SIZE))
        ty = int(math.floor(y/TILE_SIZE))

        try:
            self.game.player_move(tx, ty)
        except reversi.Illegal_move as e:
            pass
        except Exception as e:
            raise

    def handle_mousemove(self, event):
        pass

    def test_for_keyboard_commands(self):
        # Q tuşu ile ana menüye dön (oyun bittiyse)
        if 113 in self.keys_down and self.game.victory != 0:  # 113 = 'q' tuşu
            self.startup()
            return

        # F tuşu ile çıkış
        if 102 in self.keys_down:  # 102 = 'f' tuşu
            quit()

        # Z tuşu ile hamle geri alma
        if 122 in self.keys_down:  # 122 = 'z' tuşu
            if self.game.undo_move():
                self.game.has_changed = True

        # Cmd + N
        if 106 in self.keys_down and 310 in self.keys_down:
            if self.keys_down[310] <= self.keys_down[106]:  # Cmd has to be pushed first
                self.new_game()

    def select_difficulty(self):
        font = pygame.font.SysFont(None, 48)
        options = ["Kolay", "Orta", "Zor"]
        selected = 0
        
        # Buton boyutları ve konumları
        button_width = 200
        button_height = 50
        button_x = (WINDOWWIDTH - button_width) // 2
        buttons = []
        
        for i, opt in enumerate(options):
            button_y = 150 + i * 70
            buttons.append(pygame.Rect(button_x, button_y, button_width, button_height))
        
        while True:
            self.surface.fill((0, 128, 0))  # Yeşil arka plan
            
            # Başlık
            title_font = pygame.font.SysFont(None, 48)
            title_text = title_font.render("Zorluk Seviyesi Seçin", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(WINDOWWIDTH//2, 80))
            self.surface.blit(title_text, title_rect)
            
            # Butonları çiz
            for i, (button, opt) in enumerate(zip(buttons, options)):
                # Buton arka planı
                pygame.draw.rect(self.surface, (50, 50, 50), button)
                pygame.draw.rect(self.surface, (255, 255, 255), button, 2)  # Beyaz kenarlık
                
                # Buton metni
                text = font.render(opt, True, (255, 255, 255))
                text_rect = text.get_rect(center=button.center)
                self.surface.blit(text, text_rect)
            
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    quit()
                elif event.type == MOUSEBUTTONUP:
                    # Mouse tıklamasını kontrol et
                    mouse_pos = pygame.mouse.get_pos()
                    for i, button in enumerate(buttons):
                        if button.collidepoint(mouse_pos):
                            return options[i].lower()
                elif event.type == KEYDOWN:
                    if event.key == K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == K_RETURN or event.key == K_KP_ENTER:
                        return options[selected].lower()

    def new_game(self):
        self.game = reversi.Reversi(difficulty=self.difficulty)

    def start(self):
        self.startup()
        self.new_game()

        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    self.handle_keydown(event)

                elif event.type == KEYUP:
                    self.handle_keyup(event)

                elif event.type == MOUSEBUTTONUP:
                    self.handle_mouseup(event)

                elif event.type == MOUSEBUTTONDOWN:
                    self.handle_mousedown(event)

                elif event.type == MOUSEMOTION:
                    self.handle_mousemove(event)

                else:
                    pass
                    # print(event)

            # Turn based game so we don't need to always update
            if self.game.has_changed:
                self.draw_board()
                self.game.has_changed = False

            if self.game.ai_is_ready:
                self.game.ai_move()

            self.main_clock.tick(FPS)

        quit()

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        os.system('python tests.py')
    else:
        ge = Engine_v1()
        ge.start()

