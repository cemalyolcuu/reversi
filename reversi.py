import ai

class Game_error(Exception):
    """Oyunla ilgili genel hatalar"""
    pass

class Illegal_move(Game_error):
    """Geçersiz hamlelerden kaynaklanan hatalar"""
    pass

class Game_rule_error(Game_error):
    """Kural ihlallerinden kaynaklanan hatalar"""
    pass


class Reversi (object):
    """
    0 = Boş
    1 = Beyaz (oyuncu 1)
    2 = Siyah (oyuncu 2)
    """
	
    def __init__(self, difficulty="kolay"):
        super(Reversi, self).__init__()
        
        self.turn = 1
        self.player = 1
        self.victory = 0
        
        self.board = [[0 for x in range(8)] for x in range(8)]
        
        self.board[3][3] = 1
        self.board[3][4] = 2
        self.board[4][3] = 2
        self.board[4][4] = 1
        
        # Yapay zeka ayarları
        self.use_ai = True
        self.ai = ai.Game_ai(self, difficulty)
        
        self.has_changed = True
        self.ai_is_ready = False
        
        # Hamle geçmişi
        self.move_history = []
        self.board_history = []
        self.player_history = []
        
        # İlk durumu kaydet
        self.save_state()
    
    def save_state(self):
        # Mevcut tahta durumunu kaydet
        self.board_history.append([row[:] for row in self.board])
        # Mevcut oyuncuyu kaydet
        self.player_history.append(self.player)
    
    def player_move(self, x, y):
        # Eğer oyun bittiyse burada bir şey yapmamıza gerek yok
        if self.victory != 0:
            return
        
        # Yapay zekanın sırası mı?
        if self.use_ai and self.player != 1:
            return
        
        self.perform_move(x,y)
        
        # Belki yapay zeka bir hamle yapar
        if self.use_ai:
            self.ai_is_ready = True
    
    def perform_move(self, x, y):
        # Hamle yapmadan önce mevcut durumu kaydet
        self.save_state()
        
        # Önce karenin boş olduğunu kontrol et
        if self.board[x][y] != 0:
            raise Illegal_move("Oyuncu {0} {1},{2} konumuna bir taş koymaya çalıştı ama bu konum zaten {3} tarafından dolu".format(
                self.player,
                x, y,
                self.board[x][y]
            ))
        
        # Taşı yerleştir ve çevrilecek taşları hesapla
        flips = self.place_piece(x, y)
        if flips == 0:
            raise Illegal_move("Oyuncu {0} {1},{2} konumuna bir taş koymaya çalıştı ama bu hamle 0 çevirme ile sonuçlanacak".format(
                self.player,
                x, y
            ))
        
        # Hamleyi geçmişe ekle
        self.move_history.append((x, y, self.player))
        
        # Oyun bitti mi?
        all_tiles = [item for sublist in self.board for item in sublist]
        empty_tiles = sum(1 for tile in all_tiles if tile == 0)
        
        # Oyun sadece tüm kareler dolduğunda veya hiçbir oyuncunun hamle yapamadığı durumda biter
        if empty_tiles == 0:
            self.end_game()
            return
        
        # Sıradaki oyuncuya geç
        next_player = 3 - self.player
        self.player = next_player
        
        # Sıradaki oyuncunun hamle yapıp yapamayacağını kontrol et
        if not self.move_can_be_made():
            # Eğer sıradaki oyuncu hamle yapamıyorsa, önceki oyuncuya geri dön
            self.player = 3 - self.player
            
            # Eğer önceki oyuncunun da hamle yapabileceği yer yoksa oyun biter
            if not self.move_can_be_made():
                self.end_game()
                return
        
        self.has_changed = True
    
    def move_can_be_made(self):
        # Mevcut oyuncunun yapabileceği hamle var mı kontrol et
        for x in range(0,8):
            for y in range(0,8):
                if self.board[x][y] == 0:
                    try:
                        c = self.place_piece(x, y, live_mode=False)
                        if c > 0:
                            return True
                    except:
                        continue
        return False
    
    def ai_move(self):
        # Yapay zeka hamle yapmadan önce durumu kaydet
        self.save_state()
        self.ai.make_move()
        self.ai_is_ready = False
    
    def end_game(self):
        all_tiles = [item for sublist in self.board for item in sublist]
        
        white_tiles = sum(1 for tile in all_tiles if tile == 1)
        black_tiles = sum(1 for tile in all_tiles if tile == 2)
        empty_tiles = sum(1 for tile in all_tiles if tile == 0)
        
        # Oyun sadece tüm kareler dolduğunda veya hiçbir oyuncunun hamle yapamadığı durumda biter
        if empty_tiles == 0 or (not self.move_can_be_made() and not self.move_can_be_made_for_player(3 - self.player)):
            if white_tiles > black_tiles:
                self.victory = 1
            elif white_tiles < black_tiles:
                self.victory = 2
            else:
                self.victory = -1
            
            self.has_changed = True
    
    def place_piece(self, x, y, live_mode=True):
        if live_mode:
            self.board[x][y] = self.player
        change_count = 0
        
        # Yerleştirdiğimiz taşın bulunduğu satır ve sütuna referans al
        column = self.board[x]
        row = [self.board[i][y] for i in range(0,8)]
        
        # Önce yukarı gidebilir miyiz?
        if self.player in column[:y]:
            changes = []
            search_complete = False
            
            for i in range(y-1,-1,-1):
                if search_complete: continue
                
                counter = column[i]
                
                if counter == 0:
                    changes = []
                    search_complete = True
                elif counter == self.player:
                    search_complete = True
                else:
                    changes.append(i)
            
            # Değişiklikleri uygula
            if search_complete and changes:
                change_count += len(changes)
                if live_mode:
                    for i in changes:
                        self.board[x][i] = self.player
        
        # Aşağı?
        if self.player in column[y:]:
            changes = []
            search_complete = False
            
            for i in range(y+1,8,1):
                if search_complete: continue
                
                counter = column[i]
                
                if counter == 0:
                    changes = []
                    search_complete = True
                elif counter == self.player:
                    search_complete = True
                else:
                    changes.append(i)
            
            # Değişiklikleri uygula
            if search_complete and changes:
                change_count += len(changes)
                if live_mode:
                    for i in changes:
                        self.board[x][i] = self.player
        
        # Sol?
        if self.player in row[:x]:
            changes = []
            search_complete = False
            
            for i in range(x-1,-1,-1):
                if search_complete: continue
                
                counter = row[i]
                
                if counter == 0:
                    changes = []
                    search_complete = True
                elif counter == self.player:
                    search_complete = True
                else:
                    changes.append(i)
            
            # Değişiklikleri uygula
            if search_complete and changes:
                change_count += len(changes)
                if live_mode:
                    for i in changes:
                        self.board[i][y] = self.player
        
        # Sağ?
        if self.player in row[x:]:
            changes = []
            search_complete = False
            
            for i in range(x+1,8,1):
                if search_complete: continue
                
                counter = row[i]
                
                if counter == 0:
                    changes = []
                    search_complete = True
                elif counter == self.player:
                    search_complete = True
                else:
                    changes.append(i)
            
            # Değişiklikleri uygula
            if search_complete and changes:
                change_count += len(changes)
                if live_mode:
                    for i in changes:
                        self.board[i][y] = self.player
        
        # Çaprazlar biraz daha zor
        i, j = x-7, y+7
        bl_tr_diagonal = []
        
        for q in range(0, 16):
            if 0 <= i < 8 and 0 <= j < 8:
                bl_tr_diagonal.append(self.board[i][j])
            
            i += 1
            j -= 1
        
        i, j = x-7, y-7
        br_tl_diagonal = []
        for q in range(0, 16):
            if 0 <= i < 8 and 0 <= j < 8:
                br_tl_diagonal.append(self.board[i][j])
            
            i += 1
            j += 1
        
        # Yukarı Sağ
        if self.player in bl_tr_diagonal:
            changes = []
            search_complete = False
            i = 0
            lx, ly = x, y
            
            while 0 <= lx < 8 and 0 <= ly < 8:
                lx += 1
                ly -= 1
                
                if lx > 7 or ly < 0: break
                if search_complete: continue
                
                counter = self.board[lx][ly]
                
                if counter == 0:
                    changes = []
                    search_complete = True
                elif counter == self.player:
                    search_complete = True
                else:
                    changes.append((lx, ly))
            
            # Değişiklikleri uygula
            if search_complete and changes:
                change_count += len(changes)
                if live_mode:
                    for i, j in changes:
                        self.board[i][j] = self.player
        
        # Aşağı Sol
        if self.player in bl_tr_diagonal:
            changes = []
            search_complete = False
            i = 0
            lx, ly = x, y
            
            while 0 <= lx < 8 and 0 <= ly < 8:
                lx -= 1
                ly += 1
                
                if lx < 0 or ly > 7: break
                if search_complete: continue
                
                counter = self.board[lx][ly]
                
                if counter == 0:
                    changes = []
                    search_complete = True
                    break
                elif counter == self.player:
                    search_complete = True
                    break
                else:
                    changes.append((lx, ly))
            
            # Değişiklikleri uygula
            if search_complete and changes:
                change_count += len(changes)
                if live_mode:
                    for i, j in changes:
                        self.board[i][j] = self.player
        
        # Yukarı Sol
        if self.player in br_tl_diagonal:
            changes = []
            search_complete = False
            i = 0
            lx, ly = x, y
            
            while 0 <= lx < 8 and 0 <= ly < 8:
                lx -= 1
                ly -= 1
                
                if lx < 0 or ly < 0: break
                if search_complete: continue
                
                counter = self.board[lx][ly]
                
                if counter == 0:
                    changes = []
                    search_complete = True
                elif counter == self.player:
                    search_complete = True
                else:
                    changes.append((lx, ly))
            
            # Değişiklikleri uygula
            if search_complete and changes:
                change_count += len(changes)
                if live_mode:
                    for i, j in changes:
                        self.board[i][j] = self.player
        
        # Aşağı Sağ
        if self.player in br_tl_diagonal:
            changes = []
            search_complete = False
            i = 0
            lx, ly = x, y
            
            while 0 <= lx < 8 and 0 <= ly < 8:
                lx += 1
                ly += 1
                
                if lx > 7 or ly > 7: break
                if search_complete: continue
                
                counter = self.board[lx][ly]
                
                if counter == 0:
                    changes = []
                    search_complete = True
                elif counter == self.player:
                    search_complete = True
                else:
                    changes.append((lx, ly))
            
            # Değişiklikleri uygula
            if search_complete and changes:
                change_count += len(changes)
                if live_mode:
                    for i, j in changes:
                        self.board[i][j] = self.player
        
        if change_count == 0 and live_mode:
            self.board[x][y] = 0
            raise Illegal_move("Oyuncu {0} {1},{2} konumuna bir taş koymaya çalıştı ama bu hamle 0 çevirme ile sonuçlanacak".format(
                self.player,
                x, y,
            ))
        
        return change_count
    
    def ascii_board(self):
        """
        Tahtayı terminalde hata ayıklama için yazdır
        """
        for r in self.board:
            print("".join([str(t) for t in r]))
        print("")
    
    def undo_move(self):
        if len(self.move_history) > 0:
            # Son iki hamleyi geri al (oyuncu ve AI hamleleri)
            for _ in range(2):
                if len(self.move_history) > 0:
                    # Son hamleyi geçmişten al
                    last_move = self.move_history.pop()
                    # Son tahta durumunu al
                    self.board = [row[:] for row in self.board_history.pop()]
                    # Son oyuncu durumunu al
                    self.player = self.player_history.pop()
            
            # AI'nın hazır olduğunu işaretle
            if self.use_ai and self.player == 2:
                self.ai_is_ready = True
            
            self.has_changed = True
            return True
        return False
    
    def move_can_be_made_for_player(self, player):
        # Belirli bir oyuncunun yapabileceği hamle var mı kontrol et
        original_player = self.player
        self.player = player
        can_move = self.move_can_be_made()
        self.player = original_player
        return can_move
    
