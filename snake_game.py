import streamlit as st
import random
import time
import numpy as np

# Game configuration
BOARD_SIZE = 20
CELL_SIZE = 25

# Initialize game state
def init_game():
    st.session_state.snake = [(10, 10), (10, 9), (10, 8)]
    st.session_state.food = generate_food()
    st.session_state.direction = "RIGHT"
    st.session_state.score = 0
    st.session_state.game_over = False
    st.session_state.game_started = False

def generate_food():
    while True:
        food = (random.randint(0, BOARD_SIZE-1), random.randint(0, BOARD_SIZE-1))
        if food not in st.session_state.snake:
            return food

def move_snake():
    if st.session_state.game_over:
        return
    
    head = st.session_state.snake[0]
    
    # Calculate new head position based on direction
    if st.session_state.direction == "UP":
        new_head = (head[0], head[1] - 1)
    elif st.session_state.direction == "DOWN":
        new_head = (head[0], head[1] + 1)
    elif st.session_state.direction == "LEFT":
        new_head = (head[0] - 1, head[1])
    elif st.session_state.direction == "RIGHT":
        new_head = (head[0] + 1, head[1])
    
    # Check wall collision
    if (new_head[0] < 0 or new_head[0] >= BOARD_SIZE or 
        new_head[1] < 0 or new_head[1] >= BOARD_SIZE):
        st.session_state.game_over = True
        return
    
    # Check self collision
    if new_head in st.session_state.snake:
        st.session_state.game_over = True
        return
    
    # Add new head
    st.session_state.snake.insert(0, new_head)
    
    # Check if food is eaten
    if new_head == st.session_state.food:
        st.session_state.score += 10
        st.session_state.food = generate_food()
    else:
        # Remove tail if no food eaten
        st.session_state.snake.pop()

def create_board():
    # Create empty board
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    
    # Add snake
    for segment in st.session_state.snake:
        board[segment[1], segment[0]] = 1
    
    # Add snake head (different color)
    if st.session_state.snake:
        head = st.session_state.snake[0]
        board[head[1], head[0]] = 2
    
    # Add food
    food = st.session_state.food
    board[food[1], food[0]] = 3
    
    return board

def board_to_html(board):
    html = '<div style="display: grid; grid-template-columns: repeat(20, 25px); gap: 1px; background-color: #000; padding: 10px; border-radius: 10px; justify-content: center;">'
    
    for row in board:
        for cell in row:
            if cell == 0:  # Empty
                color = "#333"
            elif cell == 1:  # Snake body
                color = "#0f0"
            elif cell == 2:  # Snake head
                color = "#090"
            elif cell == 3:  # Food
                color = "#f00"
            
            html += f'<div style="width: 23px; height: 23px; background-color: {color}; border-radius: 2px;"></div>'
    
    html += '</div>'
    return html

# Initialize session state
if 'snake' not in st.session_state:
    init_game()

# Page configuration
st.set_page_config(page_title="🐍 Snake Game", layout="centered")

# Title
st.title("🐍 Snake Game")

# Game info
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Score", st.session_state.score)
with col2:
    st.metric("Length", len(st.session_state.snake))
with col3:
    st.metric("High Score", st.session_state.get('high_score', 0))

# Control buttons
if not st.session_state.game_started:
    if st.button("🎮 Start Game", use_container_width=True):
        st.session_state.game_started = True
        st.rerun()

if st.session_state.game_started and not st.session_state.game_over:
    # Direction controls
    st.write("**Controls:**")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("⬅️ Left", key="left", use_container_width=True):
            if st.session_state.direction != "RIGHT":
                st.session_state.direction = "LEFT"
                move_snake()
                st.rerun()
    
    with col2:
        if st.button("⬆️ Up", key="up", use_container_width=True):
            if st.session_state.direction != "DOWN":
                st.session_state.direction = "UP"
                move_snake()
                st.rerun()
    
    with col3:
        if st.button("⬇️ Down", key="down", use_container_width=True):
            if st.session_state.direction != "UP":
                st.session_state.direction = "DOWN"
                move_snake()
                st.rerun()
    
    with col4:
        if st.button("➡️ Right", key="right", use_container_width=True):
            if st.session_state.direction != "LEFT":
                st.session_state.direction = "RIGHT"
                move_snake()
                st.rerun()
    
    with col5:
        if st.button("⏸️ Auto Move", key="auto", use_container_width=True):
            move_snake()
            st.rerun()

# Game board
if st.session_state.game_started:
    board = create_board()
    board_html = board_to_html(board)
    st.markdown(board_html, unsafe_allow_html=True)

# Game over screen
if st.session_state.game_over:
    st.error("🎮 Game Over!")
    
    # Update high score
    if st.session_state.score > st.session_state.get('high_score', 0):
        st.session_state.high_score = st.session_state.score
        st.success(f"🏆 New High Score: {st.session_state.score}!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Play Again", use_container_width=True):
            init_game()
            st.session_state.game_started = True
            st.rerun()
    
    with col2:
        if st.button("🏠 Main Menu", use_container_width=True):
            init_game()
            st.rerun()

# Auto-play mode
if st.session_state.game_started and not st.session_state.game_over:
    st.write("---")
    auto_play = st.checkbox("🤖 Auto-play mode (moves automatically every 0.5 seconds)")
    
    if auto_play:
        time.sleep(0.5)
        move_snake()
        st.rerun()

# Instructions
st.write("---")
st.markdown("""
**How to Play:**
1. Click "Start Game" to begin
2. Use the arrow buttons to control the snake
3. Eat the red food to grow and increase your score
4. Avoid hitting walls or yourself
5. Try to get the highest score possible!

**Tips:**
- The snake moves in the direction of the last button pressed
- You cannot move directly opposite to your current direction
- Use "Auto Move" for continuous movement in the current direction
- Enable "Auto-play mode" for automatic continuous movement

**Scoring:**
- Each food eaten = 10 points
- Try to beat your high score!
""")

# Game stats
if st.session_state.game_started:
    st.write("---")
    st.write("**Game Statistics:**")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"🎯 Current Score: {st.session_state.score}")
        st.write(f"📏 Snake Length: {len(st.session_state.snake)}")
    with col2:
        st.write(f"🥇 High Score: {st.session_state.get('high_score', 0)}")
        st.write(f"📍 Food Position: {st.session_state.food}") 