import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import json
from datetime import datetime, timedelta
import numpy as np
from streamlit_option_menu import option_menu
import os

# Page configuration
st.set_page_config(
    page_title="New Gym Tracker",
    page_icon="fitness",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Multi-language support
LANGUAGES = {
    "English": {
        "title": "New Gym Tracker",
        "gym_routine": "Gym Routine",
        "olympic_lifts": "Olympic Lifts",
        "running": "Running",
        "weight_tracking": "Weight Tracking",
        "diet_program": "Diet Program",
        "dashboard": "Dashboard",
        "settings": "Settings",
        "add_exercise": "Add Exercise",
        "exercise_name": "Exercise Name",
        "sets": "Sets",
        "reps": "Reps",
        "weight": "Weight (kg)",
        "save": "Save",
        "delete": "Delete",
        "edit": "Edit",
        "calories_burned": "Calories Burned",
        "total_weight": "Total Weight Lifted",
        "workout_duration": "Workout Duration",
        "weight_progress": "Weight Progress",
        "recent_workouts": "Recent Workouts",
        "language": "Language",
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "workout_date": "Workout Date",
        "start_time": "Start Time",
        "end_time": "End Time",
        "duration_minutes": "Duration (minutes)",
        "notes": "Notes",
        "add_workout": "Add Workout",
        "no_workouts": "No workouts found",
        "total_sets": "Total Sets",
        "total_reps": "Total Reps",
        "avg_weight": "Average Weight",
        "max_weight": "Max Weight",
        "progress_chart": "Progress Chart",
        "exercise_progress": "Exercise Progress",
        "overall_stats": "Overall Statistics",
        "weekly_progress": "Weekly Progress",
        "monthly_progress": "Monthly Progress",
        "strength_gains": "Strength Gains",
        "volume_tracking": "Volume Tracking",
        "max_weight_lifted": "Max Weight Lifted",
        "one_rep_max": "One Rep Max",
        "run_date": "Run Date",
        "distance": "Distance (km)",
        "duration": "Duration (minutes)",
        "pace": "Pace (min/km)",
        "body_weight": "Body Weight (kg)",
        "track_date": "Track Date",
        "calories": "Calories",
        "protein": "Protein (g)",
        "carbs": "Carbohydrates (g)",
        "fats": "Fats (g)",
        "food_log": "Food Log",
        "what_you_ate": "What did you eat today?",
        "add_food": "Add Food Entry",
        "stronglifts_program": "Stronglifts 5x5 Program",
        "workout_a": "Workout A",
        "workout_b": "Workout B",
        "squat": "Squat",
        "bench_press": "Bench Press",
        "barbell_row": "Barbell Row",
        "overhead_press": "Overhead Press",
        "deadlift": "Deadlift"
    },
    "Spanish": {
        "title": "Nuevo Rastreador de Gimnasio",
        "gym_routine": "Rutina de Gimnasio",
        "olympic_lifts": "Levantamientos Olímpicos",
        "running": "Correr",
        "weight_tracking": "Seguimiento de Peso",
        "diet_program": "Programa de Dieta",
        "dashboard": "Panel Principal",
        "settings": "Configuración",
        "add_exercise": "Agregar Ejercicio",
        "exercise_name": "Nombre del Ejercicio",
        "sets": "Series",
        "reps": "Repeticiones",
        "weight": "Peso (kg)",
        "save": "Guardar",
        "delete": "Eliminar",
        "edit": "Editar",
        "calories_burned": "Calorías Quemadas",
        "total_weight": "Peso Total Levantado",
        "workout_duration": "Duración del Entrenamiento",
        "weight_progress": "Progreso de Peso",
        "recent_workouts": "Entrenamientos Recientes",
        "language": "Idioma",
        "theme": "Tema",
        "light": "Claro",
        "dark": "Oscuro",
        "workout_date": "Fecha de Entrenamiento",
        "start_time": "Hora de Inicio",
        "end_time": "Hora de Fin",
        "duration_minutes": "Duración (minutos)",
        "notes": "Notas",
        "add_workout": "Agregar Entrenamiento",
        "no_workouts": "No se encontraron entrenamientos",
        "total_sets": "Series Totales",
        "total_reps": "Repeticiones Totales",
        "avg_weight": "Peso Promedio",
        "max_weight": "Peso Máximo",
        "progress_chart": "Gráfico de Progreso",
        "exercise_progress": "Progreso del Ejercicio",
        "overall_stats": "Estadísticas Generales",
        "weekly_progress": "Progreso Semanal",
        "monthly_progress": "Progreso Mensual",
        "strength_gains": "Ganancia de Fuerza",
        "volume_tracking": "Seguimiento de Volumen",
        "max_weight_lifted": "Peso Máximo Levantado",
        "one_rep_max": "Máximo de Una Repetición",
        "run_date": "Fecha de Carrera",
        "distance": "Distancia (km)",
        "duration": "Duración (minutos)",
        "pace": "Ritmo (min/km)",
        "body_weight": "Peso Corporal (kg)",
        "track_date": "Fecha de Seguimiento",
        "calories": "Calorías",
        "protein": "Proteína (g)",
        "carbs": "Carbohidratos (g)",
        "fats": "Grasas (g)",
        "food_log": "Registro de Comida",
        "what_you_ate": "¿Qué comiste hoy?",
        "add_food": "Agregar Entrada de Comida",
        "stronglifts_program": "Programa Stronglifts 5x5",
        "workout_a": "Entrenamiento A",
        "workout_b": "Entrenamiento B",
        "squat": "Sentadilla",
        "bench_press": "Press de Banca",
        "barbell_row": "Remo con Barra",
        "overhead_press": "Press Militar",
        "deadlift": "Peso Muerto"
    }
}

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = "English"
if 'theme' not in st.session_state:
    st.session_state.theme = "light"

# Database functions
def init_db():
    conn = sqlite3.connect('new_gym_tracker.db')
    c = conn.cursor()
    
    # Create gym routine workouts table
    c.execute('''CREATE TABLE IF NOT EXISTS gym_workouts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  start_time TEXT,
                  end_time TEXT,
                  duration INTEGER,
                  calories_burned INTEGER,
                  notes TEXT)''')
    
    # Create gym exercises table
    c.execute('''CREATE TABLE IF NOT EXISTS gym_exercises
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  workout_id INTEGER,
                  exercise_name TEXT,
                  sets INTEGER,
                  reps INTEGER,
                  weight REAL,
                  FOREIGN KEY (workout_id) REFERENCES gym_workouts (id))''')
    
    # Create Olympic lifts table
    c.execute('''CREATE TABLE IF NOT EXISTS olympic_lifts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  exercise_name TEXT,
                  max_weight REAL,
                  notes TEXT)''')
    
    # Create running logs table
    c.execute('''CREATE TABLE IF NOT EXISTS running_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  distance REAL,
                  duration INTEGER,
                  pace REAL,
                  calories_burned INTEGER,
                  notes TEXT)''')
    
    # Create weight tracking table
    c.execute('''CREATE TABLE IF NOT EXISTS weight_tracking
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  weight REAL)''')
    
    # Create diet program table
    c.execute('''CREATE TABLE IF NOT EXISTS diet_program
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  calories INTEGER,
                  protein REAL,
                  carbs REAL,
                  fats REAL,
                  food_log TEXT)''')
    
    conn.commit()
    conn.close()

def get_translation(key):
    return str(LANGUAGES[st.session_state.language].get(key, key))

# Initialize database
init_db()

# Add sample data if database is empty
def add_sample_data():
    conn = sqlite3.connect('new_gym_tracker.db')
    c = conn.cursor()
    
    # Check if data already exists
    c.execute("SELECT COUNT(*) FROM gym_workouts")
    if c.fetchone()[0] == 0:
        # Sample gym workouts (Stronglifts 5x5) - More realistic progression
        sample_workouts = [
            ('2024-01-15', '08:00', '09:15', 75, 420, 'Stronglifts 5x5 - Workout A - Felt strong today'),
            ('2024-01-17', '08:00', '09:20', 80, 450, 'Stronglifts 5x5 - Workout B - Deadlifts were challenging'),
            ('2024-01-19', '08:00', '09:10', 70, 400, 'Stronglifts 5x5 - Workout A - Good form on squats'),
            ('2024-01-21', '08:00', '09:25', 85, 480, 'Stronglifts 5x5 - Workout B - Overhead press getting heavy'),
            ('2024-01-23', '08:00', '09:15', 75, 430, 'Stronglifts 5x5 - Workout A - Bench press plateau'),
            ('2024-01-25', '08:00', '09:30', 90, 520, 'Stronglifts 5x5 - Workout B - Failed squat reps'),
            ('2024-01-27', '08:00', '09:20', 80, 460, 'Stronglifts 5x5 - Workout A - Deload week'),
            ('2024-01-29', '08:00', '09:25', 85, 490, 'Stronglifts 5x5 - Workout B - Back to normal'),
            ('2024-01-31', '08:00', '09:15', 75, 440, 'Stronglifts 5x5 - Workout A - Feeling stronger'),
            ('2024-02-02', '08:00', '09:30', 90, 510, 'Stronglifts 5x5 - Workout B - New PR on deadlift'),
            ('2024-02-04', '08:00', '09:20', 80, 470, 'Stronglifts 5x5 - Workout A - Bench press breakthrough'),
            ('2024-02-06', '08:00', '09:25', 85, 500, 'Stronglifts 5x5 - Workout B - Squats feeling solid'),
            ('2024-02-08', '08:00', '09:15', 75, 450, 'Stronglifts 5x5 - Workout A - Good session overall'),
            ('2024-02-10', '08:00', '09:30', 90, 530, 'Stronglifts 5x5 - Workout B - Overhead press PR'),
            ('2024-02-12', '08:00', '09:20', 80, 480, 'Stronglifts 5x5 - Workout A - Barbell rows improving')
        ]
        
        # Insert sample workouts
        for workout in sample_workouts:
            c.execute('''INSERT INTO gym_workouts (date, start_time, end_time, duration, calories_burned, notes)
                         VALUES (?, ?, ?, ?, ?, ?)''', workout)
        
        # Sample gym exercises (Stronglifts 5x5) - Realistic progression with plateaus and PRs
        sample_exercises = [
            # Workout 1 - A
            (1, 'Squat', 5, 5, 65.0),
            (1, 'Bench Press', 5, 5, 55.0),
            (1, 'Barbell Row', 5, 5, 50.0),
            
            # Workout 2 - B
            (2, 'Squat', 5, 5, 67.5),
            (2, 'Overhead Press', 5, 5, 40.0),
            (2, 'Deadlift', 1, 5, 85.0),
            
            # Workout 3 - A
            (3, 'Squat', 5, 5, 70.0),
            (3, 'Bench Press', 5, 5, 57.5),
            (3, 'Barbell Row', 5, 5, 52.5),
            
            # Workout 4 - B
            (4, 'Squat', 5, 5, 72.5),
            (4, 'Overhead Press', 5, 5, 42.5),
            (4, 'Deadlift', 1, 5, 90.0),
            
            # Workout 5 - A
            (5, 'Squat', 5, 5, 75.0),
            (5, 'Bench Press', 5, 5, 60.0),
            (5, 'Barbell Row', 5, 5, 55.0),
            
            # Workout 6 - B (Failed squat reps)
            (6, 'Squat', 5, 3, 77.5),  # Failed at 3 reps
            (6, 'Overhead Press', 5, 5, 45.0),
            (6, 'Deadlift', 1, 5, 95.0),
            
            # Workout 7 - A (Deload week)
            (7, 'Squat', 5, 5, 70.0),  # Deloaded
            (7, 'Bench Press', 5, 5, 57.5),  # Deloaded
            (7, 'Barbell Row', 5, 5, 52.5),  # Deloaded
            
            # Workout 8 - B (Back to normal)
            (8, 'Squat', 5, 5, 72.5),
            (8, 'Overhead Press', 5, 5, 42.5),
            (8, 'Deadlift', 1, 5, 90.0),
            
            # Workout 9 - A
            (9, 'Squat', 5, 5, 75.0),
            (9, 'Bench Press', 5, 5, 60.0),
            (9, 'Barbell Row', 5, 5, 55.0),
            
            # Workout 10 - B (New PR on deadlift)
            (10, 'Squat', 5, 5, 77.5),
            (10, 'Overhead Press', 5, 5, 45.0),
            (10, 'Deadlift', 1, 5, 100.0),  # New PR!
            
            # Workout 11 - A (Bench press breakthrough)
            (11, 'Squat', 5, 5, 80.0),
            (11, 'Bench Press', 5, 5, 62.5),  # Breakthrough!
            (11, 'Barbell Row', 5, 5, 57.5),
            
            # Workout 12 - B
            (12, 'Squat', 5, 5, 82.5),
            (12, 'Overhead Press', 5, 5, 47.5),
            (12, 'Deadlift', 1, 5, 102.5),
            
            # Workout 13 - A
            (13, 'Squat', 5, 5, 85.0),
            (13, 'Bench Press', 5, 5, 65.0),
            (13, 'Barbell Row', 5, 5, 60.0),
            
            # Workout 14 - B (Overhead press PR)
            (14, 'Squat', 5, 5, 87.5),
            (14, 'Overhead Press', 5, 5, 50.0),  # New PR!
            (14, 'Deadlift', 1, 5, 105.0),
            
            # Workout 15 - A (Barbell rows improving)
            (15, 'Squat', 5, 5, 90.0),
            (15, 'Bench Press', 5, 5, 67.5),
            (15, 'Barbell Row', 5, 5, 62.5)  # Improved!
        ]
        
        # Insert sample exercises
        for exercise in sample_exercises:
            c.execute('''INSERT INTO gym_exercises (workout_id, exercise_name, sets, reps, weight)
                         VALUES (?, ?, ?, ?, ?)''', exercise)
        
        # Sample Olympic lifts - Realistic progression with technique notes
        sample_olympic = [
            ('2024-01-16', 'Snatch', 65.0, 'Good form, need to work on receiving position'),
            ('2024-01-18', 'Clean & Jerk', 85.0, 'Jerks feeling stronger'),
            ('2024-01-20', 'Snatch', 67.5, 'Improved technique'),
            ('2024-01-22', 'Clean & Jerk', 87.5, 'Better jerk form'),
            ('2024-01-24', 'Snatch', 70.0, 'New PR! Receiving position much better'),
            ('2024-01-26', 'Clean & Jerk', 90.0, 'New PR! Jerk technique improving'),
            ('2024-01-28', 'Snatch', 72.5, 'Failed 75kg, need to work on pull'),
            ('2024-01-30', 'Clean & Jerk', 92.5, 'Failed jerk at 95kg'),
            ('2024-02-01', 'Snatch', 70.0, 'Back to working weight, focusing on form'),
            ('2024-02-03', 'Clean & Jerk', 90.0, 'Back to working weight'),
            ('2024-02-05', 'Snatch', 72.5, 'Success! Technique breakthrough'),
            ('2024-02-07', 'Clean & Jerk', 92.5, 'Success! New PR'),
            ('2024-02-09', 'Snatch', 75.0, 'New PR! Everything clicked today'),
            ('2024-02-11', 'Clean & Jerk', 95.0, 'New PR! Jerk was solid'),
            ('2024-02-13', 'Snatch', 77.5, 'Failed but close, need more practice'),
            ('2024-02-15', 'Clean & Jerk', 97.5, 'Failed but technique is there')
        ]
        
        for olympic in sample_olympic:
            c.execute('''INSERT INTO olympic_lifts (date, exercise_name, max_weight, notes)
                         VALUES (?, ?, ?, ?)''', olympic)
        
        # Sample running logs - Realistic progression with varied training
        sample_runs = [
            ('2024-01-16', 5.0, 25, 5.0, 325, 'Easy recovery run, legs felt fresh'),
            ('2024-01-18', 8.0, 40, 5.0, 520, 'Long run, felt good, negative split'),
            ('2024-01-20', 3.0, 12, 4.0, 195, 'Speed work, 8x400m intervals'),
            ('2024-01-22', 6.0, 30, 5.0, 390, 'Tempo run, challenging but sustainable'),
            ('2024-01-24', 4.0, 20, 5.0, 260, 'Easy run, recovery day'),
            ('2024-01-26', 10.0, 50, 5.0, 650, 'Long run, new distance PR'),
            ('2024-01-28', 5.0, 22, 4.4, 325, 'Progressive run, felt strong'),
            ('2024-01-30', 3.0, 11, 3.7, 195, 'Speed work, 6x800m intervals'),
            ('2024-02-01', 6.0, 28, 4.7, 390, 'Tempo run, pace felt comfortable'),
            ('2024-02-03', 4.0, 18, 4.5, 260, 'Easy run, focusing on form'),
            ('2024-02-05', 8.0, 36, 4.5, 520, 'Long run, negative split'),
            ('2024-02-07', 5.0, 20, 4.0, 325, 'Progressive run, new pace PR'),
            ('2024-02-09', 3.0, 10, 3.3, 195, 'Speed work, 10x400m intervals'),
            ('2024-02-11', 7.0, 32, 4.6, 455, 'Medium long run, felt good'),
            ('2024-02-13', 4.0, 17, 4.3, 260, 'Easy run, recovery'),
            ('2024-02-15', 6.0, 26, 4.3, 390, 'Tempo run, new pace PR')
        ]
        
        for run in sample_runs:
            c.execute('''INSERT INTO running_logs (date, distance, duration, pace, calories_burned, notes)
                         VALUES (?, ?, ?, ?, ?, ?)''', run)
        
        # Sample weight tracking - Realistic weight fluctuations
        sample_weights = [
            ('2024-01-15', 76.2),
            ('2024-01-17', 76.0),
            ('2024-01-19', 75.8),
            ('2024-01-21', 75.6),
            ('2024-01-23', 75.4),
            ('2024-01-25', 75.2),
            ('2024-01-27', 75.0),
            ('2024-01-29', 74.8),
            ('2024-01-31', 74.6),
            ('2024-02-02', 74.4),
            ('2024-02-04', 74.2),
            ('2024-02-06', 74.0),
            ('2024-02-08', 73.8),
            ('2024-02-10', 73.6),
            ('2024-02-12', 73.4),
            ('2024-02-14', 73.2),
            ('2024-02-16', 73.0)
        ]
        
        for weight in sample_weights:
            c.execute('''INSERT INTO weight_tracking (date, weight)
                         VALUES (?, ?)''', weight)
        
        # Sample diet program - Realistic daily variations
        sample_diet = [
            ('2024-01-15', 2400, 200, 220, 80, 'Breakfast: Protein oatmeal with berries and honey. Lunch: Grilled chicken breast with brown rice and steamed broccoli. Dinner: Salmon with quinoa and roasted vegetables. Snacks: Greek yogurt with almonds, apple with peanut butter.'),
            ('2024-01-16', 2350, 195, 215, 78, 'Breakfast: Scrambled eggs with whole grain toast and avocado. Lunch: Turkey sandwich with spinach and tomato. Dinner: Lean beef stir-fry with brown rice. Snacks: Protein shake with banana, mixed nuts.'),
            ('2024-01-17', 2500, 210, 230, 85, 'Breakfast: Protein pancakes with maple syrup. Lunch: Tuna pasta salad with mixed greens. Dinner: Chicken curry with brown rice and naan. Snacks: Cottage cheese with berries, almonds.'),
            ('2024-01-18', 2450, 205, 225, 82, 'Breakfast: Greek yogurt parfait with granola and berries. Lunch: Grilled salmon with sweet potato and asparagus. Dinner: Lean pork chops with mashed potatoes. Snacks: Protein bar, orange.'),
            ('2024-01-19', 2300, 190, 210, 75, 'Breakfast: Smoothie bowl with protein powder and fruits. Lunch: Chicken Caesar salad with croutons. Dinner: Shrimp stir-fry with brown rice. Snacks: Hummus with carrots, mixed nuts.'),
            ('2024-01-20', 2600, 220, 240, 90, 'Breakfast: Protein waffles with berries and whipped cream. Lunch: Beef burger with whole grain bun and sweet potato fries. Dinner: Grilled steak with roasted vegetables. Snacks: Protein shake, dark chocolate.'),
            ('2024-01-21', 2400, 200, 220, 80, 'Breakfast: Oatmeal with protein powder and banana. Lunch: Tuna salad with whole grain crackers. Dinner: Chicken fajitas with brown rice. Snacks: Greek yogurt, apple.'),
            ('2024-01-22', 2350, 195, 215, 78, 'Breakfast: Scrambled eggs with spinach and whole grain toast. Lunch: Turkey wrap with avocado and vegetables. Dinner: Grilled fish with quinoa and vegetables. Snacks: Protein shake, mixed nuts.'),
            ('2024-01-23', 2500, 210, 230, 85, 'Breakfast: Protein smoothie with oats and berries. Lunch: Chicken pasta with tomato sauce. Dinner: Lean beef with mashed potatoes and green beans. Snacks: Cottage cheese, almonds.'),
            ('2024-01-24', 2450, 205, 225, 82, 'Breakfast: Greek yogurt with honey and granola. Lunch: Salmon salad with mixed greens. Dinner: Pork tenderloin with roasted vegetables. Snacks: Protein bar, orange.'),
            ('2024-01-25', 2300, 190, 210, 75, 'Breakfast: Protein pancakes with maple syrup. Lunch: Tuna sandwich with whole grain bread. Dinner: Chicken stir-fry with brown rice. Snacks: Hummus with vegetables, mixed nuts.'),
            ('2024-01-26', 2600, 220, 240, 90, 'Breakfast: Protein waffles with berries. Lunch: Beef burger with sweet potato fries. Dinner: Grilled steak with roasted potatoes. Snacks: Protein shake, dark chocolate.'),
            ('2024-01-27', 2400, 200, 220, 80, 'Breakfast: Oatmeal with protein powder and fruits. Lunch: Chicken salad with whole grain crackers. Dinner: Fish tacos with brown rice. Snacks: Greek yogurt, apple.'),
            ('2024-01-28', 2350, 195, 215, 78, 'Breakfast: Eggs with avocado toast. Lunch: Turkey sandwich with vegetables. Dinner: Lean beef with quinoa and vegetables. Snacks: Protein shake, mixed nuts.'),
            ('2024-01-29', 2500, 210, 230, 85, 'Breakfast: Protein smoothie with banana and oats. Lunch: Tuna pasta with tomato sauce. Dinner: Chicken with mashed potatoes and green beans. Snacks: Cottage cheese, almonds.'),
            ('2024-01-30', 2450, 205, 225, 82, 'Breakfast: Greek yogurt parfait with berries. Lunch: Salmon with sweet potato and asparagus. Dinner: Pork chops with roasted vegetables. Snacks: Protein bar, orange.')
        ]
        
        for diet in sample_diet:
            c.execute('''INSERT INTO diet_program (date, calories, protein, carbs, fats, food_log)
                         VALUES (?, ?, ?, ?, ?, ?)''', diet)
        
        conn.commit()
        st.success("Sample data added successfully!")
    
    conn.close()

# Add sample data
add_sample_data()

# Sidebar for navigation and settings
with st.sidebar:
    st.title("🏋️ " + get_translation("title"))
    
    # Language selector
    language = st.selectbox(
        get_translation("language"),
        ["English", "Spanish"],
        index=0 if st.session_state.language == "English" else 1
    )
    if language != st.session_state.language:
        st.session_state.language = language
        st.rerun()
    
    # Theme selector
    theme = st.selectbox(
        get_translation("theme"),
        [get_translation("light"), get_translation("dark")],
        index=0 if st.session_state.theme == "light" else 1
    )
    if theme != st.session_state.theme:
        st.session_state.theme = theme
        st.rerun()
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=[
            get_translation("gym_routine"), 
            get_translation("olympic_lifts"), 
            get_translation("running"),
            get_translation("weight_tracking"),
            get_translation("diet_program"),
            get_translation("dashboard"), 
            get_translation("settings")
        ],
        icons=['dumbbell', 'trophy', 'run', 'scale', 'apple', 'bar-chart', 'gear'],
        menu_icon="cast",
        default_index=0,
    )

# Main content
if selected == get_translation("gym_routine"):
    st.header("💪 " + get_translation("gym_routine"))
    
    # Stronglifts 5x5 program display
    st.subheader(get_translation("stronglifts_program"))
    
    # Create two columns for the program
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### " + get_translation("workout_a"))
        st.markdown("- **" + get_translation("squat") + ":** 5x5")
        st.markdown("- **" + get_translation("bench_press") + ":** 5x5")
        st.markdown("- **" + get_translation("barbell_row") + ":** 5x5")
        
        st.markdown("### " + get_translation("workout_b"))
        st.markdown("- **" + get_translation("squat") + ":** 5x5")
        st.markdown("- **" + get_translation("overhead_press") + ":** 5x5")
        st.markdown("- **" + get_translation("deadlift") + ":** 1x5")
    
    with col2:
        st.info("**📈 Progression:** Start with empty bar, add 2.5kg each workout for upper body, 5kg for lower body")
        st.info("**⏰ Rest:** 3 minutes between sets")
        st.info("**📅 Frequency:** 3 times per week, alternating A and B")
    
    # Workout form
    st.markdown("---")
    st.subheader("📝 " + get_translation("add_workout"))
    
    with st.form("gym_workout_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            workout_date = st.date_input(get_translation("workout_date"), value=datetime.now().date())
            start_time = st.time_input(get_translation("start_time"), value=datetime.now().time())
        
        with col2:
            end_time = st.time_input(get_translation("end_time"), value=datetime.now().time())
            notes = st.text_area(get_translation("notes"))
        
        # Exercise tracking
        st.subheader(get_translation("add_exercise"))
        
        exercises = []
        for i in range(6):  # Allow up to 6 exercises (3 per workout)
            with st.expander(f"Exercise {i+1}"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    exercise_name = st.text_input(f"{get_translation('exercise_name')} {i+1}", key=f"gym_ex_name_{i}")
                
                with col2:
                    sets = st.number_input(f"{get_translation('sets')} {i+1}", min_value=0, value=5, key=f"gym_sets_{i}")
                
                with col3:
                    reps = st.number_input(f"{get_translation('reps')} {i+1}", min_value=0, value=5, key=f"gym_reps_{i}")
                
                with col4:
                    weight = st.number_input(f"{get_translation('weight')} {i+1}", min_value=0.0, value=50.0, step=2.5, key=f"gym_weight_{i}")
                
                if exercise_name:
                    exercises.append({
                        'name': exercise_name,
                        'sets': sets,
                        'reps': reps,
                        'weight': weight
                    })
        
        submitted = st.form_submit_button(get_translation("save"))
        
        if submitted and exercises:
            # Calculate duration and calories
            start_dt = datetime.combine(workout_date, start_time)
            end_dt = datetime.combine(workout_date, end_time)
            duration = int((end_dt - start_dt).total_seconds() / 60)
            
            # Calorie calculation for strength training
            total_weight_lifted = sum(ex['sets'] * ex['reps'] * ex['weight'] for ex in exercises)
            calories_burned = int(duration * 7 + total_weight_lifted * 0.2)
            
            # Save to database
            conn = sqlite3.connect('new_gym_tracker.db')
            c = conn.cursor()
            
            # Insert workout
            c.execute('''INSERT INTO gym_workouts (date, start_time, end_time, duration, calories_burned, notes)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (workout_date.strftime('%Y-%m-%d'), start_time.strftime('%H:%M'),
                       end_time.strftime('%H:%M'), duration, calories_burned, notes))
            
            workout_id = c.lastrowid
            
            # Insert exercises
            for exercise in exercises:
                c.execute('''INSERT INTO gym_exercises (workout_id, exercise_name, sets, reps, weight)
                             VALUES (?, ?, ?, ?, ?)''',
                          (workout_id, exercise['name'], exercise['sets'],
                           exercise['reps'], exercise['weight']))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Workout saved! Calories burned: {calories_burned}")

elif selected == get_translation("olympic_lifts"):
    st.header("🏆 " + get_translation("olympic_lifts"))
    
    # Olympic lifts form
    st.subheader("📊 " + get_translation("one_rep_max"))
    
    with st.form("olympic_lifts_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            lift_date = st.date_input("Lift Date", value=datetime.now().date())
            exercise_name = st.selectbox(
                "Exercise",
                ["Snatch", "Clean & Jerk", "Clean", "Jerk", "Snatch Pull", "Clean Pull"]
            )
        
        with col2:
            max_weight = st.number_input(get_translation("max_weight_lifted"), min_value=0.0, value=50.0, step=2.5)
            notes = st.text_area("Notes")
        
        submitted = st.form_submit_button(get_translation("save"))
        
        if submitted:
            # Calorie estimation for Olympic lifts
            calories_burned = int(max_weight * 1.2)  # Rough estimation
            
            # Save to database
            conn = sqlite3.connect('new_gym_tracker.db')
            c = conn.cursor()
            
            c.execute('''INSERT INTO olympic_lifts (date, exercise_name, max_weight, notes)
                         VALUES (?, ?, ?, ?)''',
                      (lift_date.strftime('%Y-%m-%d'), exercise_name, max_weight, notes))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Olympic lift saved! Estimated calories burned: {calories_burned}")

elif selected == get_translation("running"):
    st.header("🏃 " + get_translation("running"))
    
    # Running log form
    st.subheader("📝 Log Your Run")
    
    with st.form("running_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            run_date = st.date_input(get_translation("run_date"), value=datetime.now().date())
            distance = st.number_input(get_translation("distance"), min_value=0.1, value=5.0, step=0.1)
        
        with col2:
            duration = st.number_input(get_translation("duration"), min_value=1, value=30)
            notes = st.text_area("Notes")
        
        submitted = st.form_submit_button(get_translation("save"))
        
        if submitted:
            # Calculate pace and calories
            pace = duration / distance
            calories_burned = int(distance * 65)  # Rough estimation: 65 calories per km
            
            # Save to database
            conn = sqlite3.connect('new_gym_tracker.db')
            c = conn.cursor()
            
            c.execute('''INSERT INTO running_logs (date, distance, duration, pace, calories_burned, notes)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (run_date.strftime('%Y-%m-%d'), distance, duration, pace, calories_burned, notes))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Run logged! Calories burned: {calories_burned}")

elif selected == get_translation("weight_tracking"):
    st.header("⚖️ " + get_translation("weight_tracking"))
    
    # Weight tracking form
    st.subheader("📊 Track Your Weight")
    
    with st.form("weight_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            track_date = st.date_input(get_translation("track_date"), value=datetime.now().date())
        
        with col2:
            weight = st.number_input(get_translation("body_weight"), min_value=0.0, value=75.0, step=0.1)
        
        submitted = st.form_submit_button(get_translation("save"))
        
        if submitted:
            # Save to database
            conn = sqlite3.connect('new_gym_tracker.db')
            c = conn.cursor()
            
            c.execute('''INSERT INTO weight_tracking (date, weight)
                         VALUES (?, ?)''',
                      (track_date.strftime('%Y-%m-%d'), weight))
            
            conn.commit()
            conn.close()
            
            st.success(f"✅ Weight recorded: {weight} kg")

elif selected == get_translation("diet_program"):
    st.header("🍎 " + get_translation("diet_program"))
    
    # Diet program form
    st.subheader("📋 Daily Nutrition Tracker")
    
    with st.form("diet_form"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            diet_date = st.date_input("Diet Date", value=datetime.now().date())
            calories = st.number_input(get_translation("calories"), min_value=0, value=2400)
        
        with col2:
            protein = st.number_input(get_translation("protein"), min_value=0.0, value=200.0, step=5.0)
            protein_pct = (protein * 4 / calories * 100) if calories > 0 else 0
        
        with col3:
            carbs = st.number_input(get_translation("carbs"), min_value=0.0, value=220.0, step=5.0)
            carbs_pct = (carbs * 4 / calories * 100) if calories > 0 else 0
        
        with col4:
            fats = st.number_input(get_translation("fats"), min_value=0.0, value=80.0, step=5.0)
            fats_pct = (fats * 9 / calories * 100) if calories > 0 else 0
        
        # Display percentages
        st.markdown("### 📊 Macronutrient Breakdown")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Protein", f"{protein}g", f"{protein_pct:.1f}%")
        
        with col2:
            st.metric("Carbs", f"{carbs}g", f"{carbs_pct:.1f}%")
        
        with col3:
            st.metric("Fats", f"{fats}g", f"{fats_pct:.1f}%")
        
        food_log = st.text_area(get_translation("what_you_ate"), height=150, 
                               placeholder="Breakfast: Oatmeal with protein powder and berries\nLunch: Grilled chicken with brown rice and vegetables\nDinner: Salmon with quinoa and asparagus\nSnacks: Greek yogurt, almonds, apple")
        
        submitted = st.form_submit_button(get_translation("save"))
        
        if submitted:
            # Save to database
            conn = sqlite3.connect('new_gym_tracker.db')
            c = conn.cursor()
            
            c.execute('''INSERT INTO diet_program (date, calories, protein, carbs, fats, food_log)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (diet_date.strftime('%Y-%m-%d'), calories, protein, carbs, fats, food_log))
            
            conn.commit()
            conn.close()
            
            st.success("✅ Diet entry saved!")

elif selected == get_translation("dashboard"):
    st.header("📊 " + get_translation("dashboard"))
    
    # Get all data
    conn = sqlite3.connect('new_gym_tracker.db')
    gym_workouts_df = pd.read_sql_query("SELECT * FROM gym_workouts ORDER BY date DESC", conn)
    gym_exercises_df = pd.read_sql_query("SELECT * FROM gym_exercises", conn)
    olympic_lifts_df = pd.read_sql_query("SELECT * FROM olympic_lifts ORDER BY date DESC", conn)
    running_logs_df = pd.read_sql_query("SELECT * FROM running_logs ORDER BY date DESC", conn)
    weight_tracking_df = pd.read_sql_query("SELECT * FROM weight_tracking ORDER BY date DESC", conn)
    diet_program_df = pd.read_sql_query("SELECT * FROM diet_program ORDER BY date DESC", conn)
    
    if not gym_workouts_df.empty:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_workouts = len(gym_workouts_df)
            st.metric("💪 Total Gym Workouts", total_workouts)
        
        with col2:
            total_calories = gym_workouts_df['calories_burned'].sum()
            st.metric("🔥 Total Calories Burned", f"{total_calories:,}")
        
        with col3:
            total_weight = gym_exercises_df['weight'].sum() if not gym_exercises_df.empty else 0
            st.metric("🏋️ Total Weight Lifted", f"{total_weight:,.0f} kg")
        
        with col4:
            avg_duration = gym_workouts_df['duration'].mean()
            st.metric("⏱️ Avg Workout Duration", f"{avg_duration:.0f} min")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Gym Progress")
            if not gym_exercises_df.empty:
                exercise_progress = gym_exercises_df.groupby(['exercise_name', 'workout_id']).agg({
                    'weight': 'max',
                    'sets': 'sum',
                    'reps': 'sum'
                }).reset_index()
                
                workout_dates = pd.read_sql_query("SELECT id, date FROM gym_workouts", conn)
                exercise_progress = exercise_progress.merge(workout_dates, left_on='workout_id', right_on='id')
                
                fig = px.line(exercise_progress, x='date', y='weight', color='exercise_name',
                             title="Gym Exercise Progress")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("⚖️ Weight Tracking")
            if not weight_tracking_df.empty:
                fig = px.line(weight_tracking_df, x='date', y='weight',
                             title="Body Weight Progress")
                st.plotly_chart(fig, use_container_width=True)
        
        # Additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Olympic Lifts Progress")
            if not olympic_lifts_df.empty:
                fig = px.scatter(olympic_lifts_df, x='date', y='max_weight', color='exercise_name',
                                title="Olympic Lifts Max Weight")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🏃 Running Progress")
            if not running_logs_df.empty:
                fig = px.line(running_logs_df, x='date', y='distance',
                             title="Running Distance")
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info(get_translation("no_workouts"))
    
    # Close database connection
    conn.close()

elif selected == get_translation("settings"):
    st.header("⚙️ " + get_translation("settings"))
    
    # Settings content
    st.subheader("Application Settings")
    
    # Export data
    if st.button("📤 Export Data"):
        conn = sqlite3.connect('new_gym_tracker.db')
        gym_workouts_df = pd.read_sql_query("SELECT * FROM gym_workouts", conn)
        gym_exercises_df = pd.read_sql_query("SELECT * FROM gym_exercises", conn)
        olympic_lifts_df = pd.read_sql_query("SELECT * FROM olympic_lifts", conn)
        running_logs_df = pd.read_sql_query("SELECT * FROM running_logs", conn)
        weight_tracking_df = pd.read_sql_query("SELECT * FROM weight_tracking", conn)
        diet_program_df = pd.read_sql_query("SELECT * FROM diet_program", conn)
        conn.close()
        
        # Create Excel file
        with pd.ExcelWriter('new_gym_tracker_export.xlsx') as writer:
            gym_workouts_df.to_excel(writer, sheet_name='Gym_Workouts', index=False)
            gym_exercises_df.to_excel(writer, sheet_name='Gym_Exercises', index=False)
            olympic_lifts_df.to_excel(writer, sheet_name='Olympic_Lifts', index=False)
            running_logs_df.to_excel(writer, sheet_name='Running_Logs', index=False)
            weight_tracking_df.to_excel(writer, sheet_name='Weight_Tracking', index=False)
            diet_program_df.to_excel(writer, sheet_name='Diet_Program', index=False)
        
        st.success("✅ Data exported to new_gym_tracker_export.xlsx")
    
    # Clear data
    if st.button("🗑️ Clear All Data", type="secondary"):
        if st.checkbox("I confirm I want to delete all data"):
            conn = sqlite3.connect('new_gym_tracker.db')
            c = conn.cursor()
            c.execute("DELETE FROM gym_exercises")
            c.execute("DELETE FROM gym_workouts")
            c.execute("DELETE FROM olympic_lifts")
            c.execute("DELETE FROM running_logs")
            c.execute("DELETE FROM weight_tracking")
            c.execute("DELETE FROM diet_program")
            conn.commit()
            conn.close()
            st.success("✅ All data cleared!")

# Custom CSS for responsive design with proper theme switching
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
    }
    /* Custom styling for better UX */
    .stButton > button {
        border-radius: 10px;
        font-weight: bold;
    }
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Apply theme based on selection
if st.session_state.theme == "Dark":
    st.markdown("""
    <style>
        /* Dark mode styles - soft grey */
        [data-testid="stSidebar"] {
            background-color: #2d3748 !important;
        }
        .stApp {
            background-color: #1a202c !important;
            color: #e2e8f0 !important;
        }
        .stMarkdown {
            color: #e2e8f0 !important;
        }
        .stText {
            color: #e2e8f0 !important;
        }
        .stMetric {
            background-color: #2d3748 !important;
            color: #e2e8f0 !important;
        }
        /* Dark mode form elements */
        .stSelectbox > div > div {
            background-color: #2d3748 !important;
            color: #e2e8f0 !important;
        }
        .stTextInput > div > div > input {
            background-color: #2d3748 !important;
            color: #e2e8f0 !important;
        }
        .stTextArea > div > div > textarea {
            background-color: #2d3748 !important;
            color: #e2e8f0 !important;
        }
        .stNumberInput > div > div > input {
            background-color: #2d3748 !important;
            color: #e2e8f0 !important;
        }
        .stDateInput > div > div > input {
            background-color: #2d3748 !important;
            color: #e2e8f0 !important;
        }
        .stTimeInput > div > div > input {
            background-color: #2d3748 !important;
            color: #e2e8f0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        /* Light mode styles - default */
        [data-testid="stSidebar"] {
            background-color: #f0f2f6 !important;
        }
        .stApp {
            background-color: #ffffff !important;
            color: #262730 !important;
        }
        .stMarkdown {
            color: #262730 !important;
        }
        .stText {
            color: #262730 !important;
        }
        .stMetric {
            background-color: #f0f2f6 !important;
            color: #262730 !important;
        }
    </style>
    """, unsafe_allow_html=True) 