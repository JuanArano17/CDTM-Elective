import streamlit as st
import random
import time
import numpy as np
import streamlit.components.v1 as components

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
    st.session_state.last_key = None

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

def handle_key_input():
    """Handle keyboard input from JavaScript and update direction"""
    if not st.session_state.game_started or st.session_state.game_over:
        return False
    
    key = st.session_state.get('last_key', None)
    if not key:
        return False
    
    moved = False
    if key == "w" or key == "W":
        if st.session_state.direction != "DOWN":
            st.session_state.direction = "UP"
            moved = True
    elif key == "s" or key == "S":
        if st.session_state.direction != "UP":
            st.session_state.direction = "DOWN"
            moved = True
    elif key == "a" or key == "A":
        if st.session_state.direction != "RIGHT":
            st.session_state.direction = "LEFT"
            moved = True
    elif key == "d" or key == "D":
        if st.session_state.direction != "LEFT":
            st.session_state.direction = "RIGHT"
            moved = True
    elif key == " ":  # Spacebar for auto move
        moved = True
    
    if moved:
        move_snake()
        st.session_state.last_key = None  # Clear the key after processing
        return True
    
    return False

def create_keyboard_listener():
    """Create JavaScript keyboard event listener"""
    keyboard_js = """
    <script>
    document.addEventListener('keydown', function(event) {
        // Prevent default behavior for WASD keys and spacebar
        if(['w', 'W', 'a', 'A', 's', 'S', 'd', 'D', ' '].includes(event.key)) {
            event.preventDefault();
        }
        
        // Send key to Streamlit
        if(['w', 'W', 'a', 'A', 's', 'S', 'd', 'D', ' '].includes(event.key)) {
            // Use query parameter to send key to streamlit
            const url = new URL(window.location);
            url.searchParams.set('key', event.key);
            window.history.replaceState({}, '', url);
            
            // Trigger a rerun by dispatching a custom event
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: event.key
            }, '*');
        }
    });
    
    // Focus the window to capture keyboard events
    window.focus();
    </script>
    <div style="text-align: center; padding: 20px; background: #f0f0f0; border-radius: 10px; margin: 10px 0;">
        <h3>🎮 Game Controls Active</h3>
        <p>Use <strong>WASD Keys</strong> to control the snake!</p>
        <p><strong>W</strong> (up), <strong>A</strong> (left), <strong>S</strong> (down), <strong>D</strong> (right), or <strong>Spacebar</strong> to move forward</p>
        <small>Make sure this window is focused to capture key presses</small>
    </div>
    """
    return keyboard_js

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

# Check for keyboard input from URL parameters
query_params = st.query_params
if 'key' in query_params:
    st.session_state.last_key = query_params['key']
    # Clear the query parameter
    del st.query_params['key']

# Handle keyboard input
if handle_key_input():
    st.rerun()

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

# Keyboard controls (only show when game is active)
if st.session_state.game_started and not st.session_state.game_over:
    # JavaScript keyboard listener
    keyboard_html = create_keyboard_listener()
    components.html(keyboard_html, height=150)

if st.session_state.game_started and not st.session_state.game_over:
    # Direction controls (backup buttons)
    st.write("**Backup Button Controls:**")
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
2. **Use WASD keys to control the snake** ⌨️ (focus the controls area above)
3. Alternatively, use the backup buttons below
4. Eat the red food to grow and increase your score
5. Avoid hitting walls or yourself
6. Try to get the highest score possible!

**Keyboard Controls:**
- **WASD Keys**: W (up), A (left), S (down), D (right)
- **Spacebar**: Move forward in current direction

**Tips:**
- Make sure the browser window is focused to capture keyboard events
- The snake moves in the direction of the last key pressed
- You cannot move directly opposite to your current direction
- Use "Auto Move" button or spacebar for continuous movement in the current direction
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