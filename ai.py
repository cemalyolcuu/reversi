import random
import time

class Game_ai (object):
    def __init__(self, game, difficulty="kolay"):
        super(Game_ai, self).__init__()
        self.game = game
        self.move = (-1,-1)
        self.difficulty = difficulty
    
    def make_move(self):
        time.sleep(0.1)
        
        changes = {}
        valid_moves = []
        
        for x in range(0,8):
            for y in range(0,8):
                if self.game.board[x][y] == 0:
                    c = self.game.place_piece(x, y, live_mode=False)
                    if c > 0:
                        changes[(x,y)] = c
                        valid_moves.append((x, y, c))
        
        if not changes:
            self.game.end_game()
            return
        
        if self.difficulty == "kolay":
            # Rastgele geçerli hamle
            move = random.choice(list(changes.keys()))
        elif self.difficulty == "orta":
            # En çok taş çeviren hamle
            max_key, max_val = (-1,-1), 0
            for k, v in changes.items():
                if v > max_val:
                    max_key = k
                    max_val = v
            move = max_key
        elif self.difficulty == "zor":
            # Öncelik köşe hamlelerinde, yoksa en çok taş çeviren
            corners = [(0,0), (0,7), (7,0), (7,7)]
            corner_moves = [m for m in changes.keys() if m in corners]
            if corner_moves:
                move = random.choice(corner_moves)
            else:
                max_key, max_val = (-1,-1), 0
                for k, v in changes.items():
                    if v > max_val:
                        max_key = k
                        max_val = v
                move = max_key
        else:
            # Varsayılan: orta
            max_key, max_val = (-1,-1), 0
            for k, v in changes.items():
                if v > max_val:
                    max_key = k
                    max_val = v
            move = max_key
        
        x, y = move
        self.game.perform_move(x, y)