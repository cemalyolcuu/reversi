import streamlit as st
import numpy as np
from reversi import Reversi
import time

def initialize_session_state():
    if 'game' not in st.session_state:
        st.session_state.game = Reversi(difficulty="kolay")
    if 'selected_difficulty' not in st.session_state:
        st.session_state.selected_difficulty = "kolay"
    if 'message' not in st.session_state:
        st.session_state.message = ""
    if 'message_time' not in st.session_state:
        st.session_state.message_time = 0
    if 'ai_move_start_time' not in st.session_state:
        st.session_state.ai_move_start_time = None

def draw_board():
    board = st.session_state.game.board
    cols = st.columns(8)
    
    for i in range(8):
        with cols[i]:
            for j in range(8):
                if board[i][j] == 0:
                    if st.button("", key=f"{i},{j}", use_container_width=True):
                        try:
                            st.session_state.game.player_move(i, j)
                            st.session_state.message = ""
                            # Yapay zeka hamle yapmaya hazırsa zamanı kaydet, UI yenileme kaldırıldı
                            if st.session_state.game.ai_is_ready:
                                st.session_state.ai_move_start_time = time.time()
                        except Exception as e:
                            st.session_state.message = str(e)
                            st.session_state.message_time = time.time()
                elif board[i][j] == 1:
                    st.button("⚪", key=f"{i},{j}", use_container_width=True)
                else:
                    st.button("⚫", key=f"{i},{j}", use_container_width=True)

def main():
    st.title("Reversi Oyunu")
    
    initialize_session_state()
    
    # Eğer yapay zeka hamle yapmaya hazırsa, hemen yapay zekanın hamlesini yap
    if st.session_state.game.ai_is_ready:
        st.session_state.game.ai_move()
        st.session_state.ai_move_start_time = None
        st.rerun()
    
    # Zorluk seçimi
    difficulty = st.selectbox(
        "Zorluk Seviyesi",
        ["kolay", "orta", "zor"],
        index=["kolay", "orta", "zor"].index(st.session_state.selected_difficulty)
    )
    
    if difficulty != st.session_state.selected_difficulty:
        st.session_state.selected_difficulty = difficulty
        st.session_state.game = Reversi(difficulty=difficulty)
        st.rerun()
    
    # Oyun tahtası
    draw_board()
    
    # Mesaj gösterimi
    if st.session_state.message and time.time() - st.session_state.message_time < 3:
        st.error(st.session_state.message)
    
    # Oyun durumu
    if st.session_state.game.victory != 0:
        if st.session_state.game.victory == 1:
            st.success("Beyaz Kazandı!")
        elif st.session_state.game.victory == 2:
            st.success("Siyah Kazandı!")
        else:
            st.info("Berabere!")
        
        if st.button("Yeni Oyun"):
            st.session_state.game = Reversi(difficulty=st.session_state.selected_difficulty)
            st.rerun()
    else:
        # Sıradaki oyuncu
        current_player = "Beyaz" if st.session_state.game.player == 1 else "Siyah"
        st.info(f"Sıra: {current_player}")
        
        # Hamle geri alma butonu
        if st.button("Hamleyi Geri Al (Z)"):
            if st.session_state.game.undo_move():
                st.rerun()
    
    # Oyun bilgileri
    st.sidebar.title("Oyun Bilgileri")
    st.sidebar.markdown("""
    ### Nasıl Oynanır?
    1. Beyaz taşlarla başlarsınız
    2. Rakibinizin taşlarını ele geçirmek için hamle yapın
    3. Hamle yapmak için boş bir kareye tıklayın
    4. Eğer geçerli bir hamle yoksa, sıra rakibe geçer
    5. Tüm kareler dolduğunda veya hiçbir oyuncunun hamlesi kalmadığında oyun biter
    
    ### Kontroller
    - Hamle yapmak için boş kareye tıklayın
    - Hamleyi geri almak için "Hamleyi Geri Al" butonuna basın
    - Yeni oyun başlatmak için "Yeni Oyun" butonuna basın
    """)

if __name__ == "__main__":
    main() 