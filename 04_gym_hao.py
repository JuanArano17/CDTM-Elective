import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import time
import requests
import json
from PIL import Image
import io

# =============================================================================
# CONFIGURATION AND TRANSLATIONS
# =============================================================================

st.set_page_config(
    page_title="GymHao - Your Fitness Companion",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Multi-language support
TRANSLATIONS = {
    'en': {
        'title': 'GymHao - Your Fitness Companion',
        'sidebar_title': 'Navigation',
        'home': 'Home',
        'register_workout': 'Register Workout',
        'training_planner': 'Training Planner',
        'stats_evolution': 'Stats Evolution',
        'gym_ranking': 'Gym Ranking',
        'anime_zone': 'Anime Zone',
        'select_language': 'Select Language',
        'welcome': 'Welcome to GymHao!',
        'your_fitness_journey': 'Your comprehensive fitness journey starts here.',
        'todays_stats': "Today's Stats",
        'calories_burned': 'Calories Burned',
        'exercises_completed': 'Exercises Completed',
        'time_spent': 'Time Spent (minutes)',
        'current_streak': 'Current Streak (days)',
        'quick_workout': 'Quick Workout Registration',
        'exercise_name': 'Exercise Name',
        'duration_minutes': 'Duration (minutes)',
        'intensity': 'Intensity Level',
        'low': 'Low',
        'medium': 'Medium',
        'high': 'High',
        'extreme': 'Extreme',
        'register': 'Register Exercise',
        'exercise_registered': 'Exercise registered successfully!',
        'workout_session': 'Workout Session Registration',
        'select_exercises': 'Select Exercises',
        'sets': 'Sets',
        'reps': 'Reps per Set',
        'weight_kg': 'Weight (kg)',
        'rest_time': 'Rest Time (seconds)',
        'total_calories': 'Total Calories Burned',
        'session_duration': 'Session Duration',
        'register_session': 'Register Session',
        'session_registered': 'Workout session registered successfully!',
        'training_plan': 'Training Plan Generator',
        'fitness_goal': 'Fitness Goal',
        'weight_loss': 'Weight Loss',
        'muscle_gain': 'Muscle Gain',
        'endurance': 'Endurance',
        'strength': 'Strength',
        'general_fitness': 'General Fitness',
        'current_fitness': 'Current Fitness Level',
        'beginner': 'Beginner',
        'intermediate': 'Intermediate',
        'advanced': 'Advanced',
        'expert': 'Expert',
        'available_time': 'Available Time (minutes per day)',
        'generate_plan': 'Generate Training Plan',
        'your_plan': 'Your Personalized Training Plan',
        'day': 'Day',
        'exercise': 'Exercise',
        'recommended_plan': 'Recommended Training Plan',
        'progress_tracking': 'Progress Tracking',
        'weight_progress': 'Weight Progress',
        'strength_progress': 'Strength Progress',
        'endurance_progress': 'Endurance Progress',
        'monthly_calories': 'Monthly Calories Burned',
        'gym_leaderboard': 'Gym Leaderboard',
        'user_name': 'User Name',
        'total_workouts': 'Total Workouts',
        'avg_calories': 'Avg Calories/Session',
        'rank': 'Rank',
        'your_rank': 'Your Current Rank',
        'compete_message': 'Keep working out to climb the leaderboard!',
        'anime_motivation': 'Anime Motivation Zone',
        'motivational_quotes': 'Motivational Anime Quotes',
        'training_music': 'Training Playlist',
        'character_inspiration': 'Character Inspiration',
        'add_custom_exercise': 'Add Custom Exercise',
        'custom_exercise_name': 'Custom Exercise Name',
        'muscle_groups': 'Target Muscle Groups',
        'chest': 'Chest',
        'back': 'Back',
        'shoulders': 'Shoulders',
        'arms': 'Arms',
        'legs': 'Legs',
        'core': 'Core',
        'full_body': 'Full Body',
        'add_exercise': 'Add Exercise',
        'exercise_added': 'Custom exercise added successfully!'
    },
    'es': {
        'title': 'GymHao - Tu Compañero de Fitness',
        'sidebar_title': 'Navegación',
        'home': 'Inicio',
        'register_workout': 'Registrar Entrenamiento',
        'training_planner': 'Planificador de Entrenamiento',
        'stats_evolution': 'Evolución de Estadísticas',
        'gym_ranking': 'Ranking del Gimnasio',
        'anime_zone': 'Zona Anime',
        'select_language': 'Seleccionar Idioma',
        'welcome': '¡Bienvenido a GymHao!',
        'your_fitness_journey': 'Tu viaje integral de fitness comienza aquí.',
        'todays_stats': 'Estadísticas de Hoy',
        'calories_burned': 'Calorías Quemadas',
        'exercises_completed': 'Ejercicios Completados',
        'time_spent': 'Tiempo Invertido (minutos)',
        'current_streak': 'Racha Actual (días)',
        'quick_workout': 'Registro Rápido de Entrenamiento',
        'exercise_name': 'Nombre del Ejercicio',
        'duration_minutes': 'Duración (minutos)',
        'intensity': 'Nivel de Intensidad',
        'low': 'Bajo',
        'medium': 'Medio',
        'high': 'Alto',
        'extreme': 'Extremo',
        'register': 'Registrar Ejercicio',
        'exercise_registered': '¡Ejercicio registrado exitosamente!',
        'workout_session': 'Registro de Sesión de Entrenamiento',
        'select_exercises': 'Seleccionar Ejercicios',
        'sets': 'Series',
        'reps': 'Repeticiones por Serie',
        'weight_kg': 'Peso (kg)',
        'rest_time': 'Tiempo de Descanso (segundos)',
        'total_calories': 'Total de Calorías Quemadas',
        'session_duration': 'Duración de la Sesión',
        'register_session': 'Registrar Sesión',
        'session_registered': '¡Sesión de entrenamiento registrada exitosamente!',
        'training_plan': 'Generador de Plan de Entrenamiento',
        'fitness_goal': 'Objetivo de Fitness',
        'weight_loss': 'Pérdida de Peso',
        'muscle_gain': 'Ganancia Muscular',
        'endurance': 'Resistencia',
        'strength': 'Fuerza',
        'general_fitness': 'Fitness General',
        'current_fitness': 'Nivel Actual de Fitness',
        'beginner': 'Principiante',
        'intermediate': 'Intermedio',
        'advanced': 'Avanzado',
        'expert': 'Experto',
        'available_time': 'Tiempo Disponible (minutos por día)',
        'generate_plan': 'Generar Plan de Entrenamiento',
        'your_plan': 'Tu Plan de Entrenamiento Personalizado',
        'day': 'Día',
        'exercise': 'Ejercicio',
        'recommended_plan': 'Plan de Entrenamiento Recomendado',
        'progress_tracking': 'Seguimiento de Progreso',
        'weight_progress': 'Progreso de Peso',
        'strength_progress': 'Progreso de Fuerza',
        'endurance_progress': 'Progreso de Resistencia',
        'monthly_calories': 'Calorías Mensuales Quemadas',
        'gym_leaderboard': 'Tabla de Clasificación del Gimnasio',
        'user_name': 'Nombre de Usuario',
        'total_workouts': 'Entrenamientos Totales',
        'avg_calories': 'Calorías Promedio/Sesión',
        'rank': 'Rango',
        'your_rank': 'Tu Rango Actual',
        'compete_message': '¡Sigue entrenando para subir en la clasificación!',
        'anime_motivation': 'Zona de Motivación Anime',
        'motivational_quotes': 'Frases Motivacionales de Anime',
        'training_music': 'Lista de Reproducción de Entrenamiento',
        'character_inspiration': 'Inspiración de Personajes',
        'add_custom_exercise': 'Agregar Ejercicio Personalizado',
        'custom_exercise_name': 'Nombre del Ejercicio Personalizado',
        'muscle_groups': 'Grupos Musculares Objetivo',
        'chest': 'Pecho',
        'back': 'Espalda',
        'shoulders': 'Hombros',
        'arms': 'Brazos',
        'legs': 'Piernas',
        'core': 'Core',
        'full_body': 'Cuerpo Completo',
        'add_exercise': 'Agregar Ejercicio',
        'exercise_added': '¡Ejercicio personalizado agregado exitosamente!'
    }
}

# Initialize session state
def init_session_state():
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    if 'user_name' not in st.session_state:
        st.session_state.user_name = 'GymHao User'
    if 'workouts' not in st.session_state:
        st.session_state.workouts = []
    if 'custom_exercises' not in st.session_state:
        st.session_state.custom_exercises = []
    if 'user_stats' not in st.session_state:
        st.session_state.user_stats = {
            'total_workouts': 0,
            'total_calories': 0,
            'current_streak': 0,
            'weight_data': [],
            'strength_data': [],
            'endurance_data': []
        }
    if 'gym_users' not in st.session_state:
        # Simulated gym users for ranking
        st.session_state.gym_users = [
            {'name': 'Goku_Saiyan', 'workouts': 150, 'avg_calories': 450},
            {'name': 'Saitama_Hero', 'workouts': 120, 'avg_calories': 500},
            {'name': 'Vegeta_Prince', 'workouts': 140, 'avg_calories': 430},
            {'name': 'All_Might', 'workouts': 100, 'avg_calories': 480},
            {'name': 'Natsu_Dragon', 'workouts': 90, 'avg_calories': 400},
        ]

def get_text(key):
    return TRANSLATIONS[st.session_state.language].get(key, key)

# =============================================================================
# EXERCISE DATABASE
# =============================================================================

EXERCISE_DATABASE = {
    'Cardio': {
        'Running': {'calories_per_minute': 12, 'muscle_groups': ['legs', 'core']},
        'Cycling': {'calories_per_minute': 10, 'muscle_groups': ['legs']},
        'Swimming': {'calories_per_minute': 14, 'muscle_groups': ['full_body']},
        'Jump Rope': {'calories_per_minute': 15, 'muscle_groups': ['legs', 'arms']},
        'Burpees': {'calories_per_minute': 16, 'muscle_groups': ['full_body']},
        'Mountain Climbers': {'calories_per_minute': 12, 'muscle_groups': ['core', 'arms']},
    },
    'Strength': {
        'Bench Press': {'calories_per_minute': 8, 'muscle_groups': ['chest', 'arms']},
        'Squat': {'calories_per_minute': 10, 'muscle_groups': ['legs', 'core']},
        'Deadlift': {'calories_per_minute': 12, 'muscle_groups': ['back', 'legs']},
        'Pull-ups': {'calories_per_minute': 9, 'muscle_groups': ['back', 'arms']},
        'Push-ups': {'calories_per_minute': 7, 'muscle_groups': ['chest', 'arms']},
        'Shoulder Press': {'calories_per_minute': 6, 'muscle_groups': ['shoulders', 'arms']},
        'Bicep Curls': {'calories_per_minute': 4, 'muscle_groups': ['arms']},
        'Tricep Dips': {'calories_per_minute': 5, 'muscle_groups': ['arms']},
        'Lunges': {'calories_per_minute': 8, 'muscle_groups': ['legs']},
        'Plank': {'calories_per_minute': 3, 'muscle_groups': ['core']},
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_calories(exercise, duration, intensity='medium'):
    base_calories = EXERCISE_DATABASE.get('Cardio', {}).get(exercise, 
                   EXERCISE_DATABASE.get('Strength', {}).get(exercise, {'calories_per_minute': 8}))['calories_per_minute']
    
    intensity_multiplier = {'low': 0.7, 'medium': 1.0, 'high': 1.3, 'extreme': 1.6}
    return int(base_calories * duration * intensity_multiplier.get(intensity, 1.0))

def generate_training_plan(goal, fitness_level, available_time):
    plans = {
        'weight_loss': {
            'beginner': ['Walking: 20 min', 'Bodyweight squats: 2x10', 'Push-ups: 2x5', 'Plank: 2x30s'],
            'intermediate': ['Running: 25 min', 'Squats: 3x12', 'Push-ups: 3x8', 'Burpees: 3x5'],
            'advanced': ['HIIT Running: 30 min', 'Jump squats: 4x15', 'Push-ups: 4x12', 'Mountain climbers: 4x20'],
            'expert': ['Sprint intervals: 35 min', 'Plyometric squats: 5x20', 'Burpees: 5x10', 'Battle ropes: 5x45s']
        },
        'muscle_gain': {
            'beginner': ['Bench press: 3x8', 'Squats: 3x8', 'Rows: 3x8', 'Shoulder press: 3x8'],
            'intermediate': ['Bench press: 4x10', 'Squats: 4x10', 'Deadlifts: 3x8', 'Pull-ups: 3x6'],
            'advanced': ['Bench press: 5x12', 'Squats: 5x12', 'Deadlifts: 4x10', 'Weighted pull-ups: 4x8'],
            'expert': ['Heavy bench: 6x15', 'Heavy squats: 6x15', 'Heavy deadlifts: 5x12', 'Weighted dips: 5x10']
        },
        'endurance': {
            'beginner': ['Light jogging: 15 min', 'Cycling: 20 min', 'Swimming: 15 min', 'Yoga: 10 min'],
            'intermediate': ['Running: 30 min', 'Cycling: 40 min', 'Swimming: 25 min', 'Circuit training: 20 min'],
            'advanced': ['Long run: 45 min', 'Cycling: 60 min', 'Swimming: 40 min', 'CrossFit: 30 min'],
            'expert': ['Marathon training: 60+ min', 'Century ride prep: 90+ min', 'Open water swim: 60 min', 'Ultra endurance: 90+ min']
        }
    }
    
    base_plan = plans.get(goal, plans['general_fitness'])
    return base_plan.get(fitness_level, base_plan['beginner'])

def get_anime_quotes():
    quotes = [
        "The moment you give up is the moment you let someone else win! - Kobe Bryant x Vegeta",
        "Hard work is what makes your dreams come true! - Rock Lee",
        "I don't want to conquer anything. I just think the guy with the most freedom in this whole ocean is the Pirate King! - Monkey D. Luffy",
        "If you don't take risks, you can't create a future! - Monkey D. Luffy",
        "Power comes in response to a need, not a desire! - Goku",
        "Push through the pain, giving up hurts more! - Vegeta",
        "The way to get started is to quit talking and begin doing! - All Might",
        "A real man never dies, even when he's killed! - Kamina"
    ]
    return quotes

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    init_session_state()
    
    # Language selector in sidebar
    st.sidebar.selectbox(
        get_text('select_language'),
        options=['en', 'es'],
        format_func=lambda x: 'English' if x == 'en' else 'Español',
        key='language'
    )
    
    # Sidebar navigation
    st.sidebar.title(f"💪 {get_text('sidebar_title')}")
    
    # User name input
    st.session_state.user_name = st.sidebar.text_input("Your Name:", value=st.session_state.user_name)
    
    page = st.sidebar.selectbox(
        "Choose a section:",
        [
            f"🏠 {get_text('home')}",
            f"📝 {get_text('register_workout')}",
            f"📅 {get_text('training_planner')}",
            f"📈 {get_text('stats_evolution')}",
            f"🏆 {get_text('gym_ranking')}",
            f"🎌 {get_text('anime_zone')}"
        ]
    )

    # Main title
    st.title(get_text('title'))

    # =============================================================================
    # HOME PAGE
    # =============================================================================
    
    if page == f"🏠 {get_text('home')}":
        st.header(get_text('welcome'))
        st.write(get_text('your_fitness_journey'))
        
        # Today's stats dashboard
        col1, col2, col3, col4 = st.columns(4)
        
        today_workouts = [w for w in st.session_state.workouts if w['date'] == datetime.now().date()]
        today_calories = sum([w.get('calories', 0) for w in today_workouts])
        today_exercises = len(today_workouts)
        today_time = sum([w.get('duration', 0) for w in today_workouts])
        
        with col1:
            st.metric(get_text('calories_burned'), today_calories, delta="+50")
        with col2:
            st.metric(get_text('exercises_completed'), today_exercises, delta="+2")
        with col3:
            st.metric(get_text('time_spent'), today_time, delta="+15")
        with col4:
            st.metric(get_text('current_streak'), st.session_state.user_stats['current_streak'], delta="+1")
        
        st.markdown("---")
        
        # Quick workout registration
        st.subheader(get_text('quick_workout'))
        
        col1, col2 = st.columns(2)
        with col1:
            quick_exercise = st.selectbox(
                get_text('exercise_name'),
                list(EXERCISE_DATABASE['Cardio'].keys()) + list(EXERCISE_DATABASE['Strength'].keys())
            )
            quick_duration = st.number_input(get_text('duration_minutes'), min_value=1, max_value=180, value=30)
        
        with col2:
            quick_intensity = st.selectbox(
                get_text('intensity'),
                ['low', 'medium', 'high', 'extreme'],
                format_func=lambda x: get_text(x)
            )
            
        if st.button(get_text('register')):
            calories = calculate_calories(quick_exercise, quick_duration, quick_intensity)
            workout = {
                'exercise': quick_exercise,
                'duration': quick_duration,
                'intensity': quick_intensity,
                'calories': calories,
                'date': datetime.now().date(),
                'timestamp': datetime.now()
            }
            st.session_state.workouts.append(workout)
            st.session_state.user_stats['total_workouts'] += 1
            st.session_state.user_stats['total_calories'] += calories
            st.success(f"{get_text('exercise_registered')} 🔥 {calories} calories burned!")
            st.rerun()

    # =============================================================================
    # REGISTER WORKOUT PAGE
    # =============================================================================
    
    elif page == f"📝 {get_text('register_workout')}":
        st.header(get_text('workout_session'))
        
        # Exercise selection
        all_exercises = list(EXERCISE_DATABASE['Cardio'].keys()) + list(EXERCISE_DATABASE['Strength'].keys())
        if st.session_state.custom_exercises:
            all_exercises.extend([ex['name'] for ex in st.session_state.custom_exercises])
            
        selected_exercises = st.multiselect(
            get_text('select_exercises'),
            all_exercises
        )
        
        session_data = []
        total_session_calories = 0
        total_session_time = 0
        
        for exercise in selected_exercises:
            # Check if exercise is cardio or strength
            is_cardio = exercise in EXERCISE_DATABASE['Cardio']
            is_custom = exercise in [ex['name'] for ex in st.session_state.custom_exercises]
            
            if is_cardio:
                st.subheader(f"🏃 {exercise}")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    duration = st.number_input(f"{get_text('duration_minutes')} ({exercise})", min_value=1, max_value=180, value=30, key=f"duration_{exercise}")
                with col2:
                    intensity = st.selectbox(f"{get_text('intensity')} ({exercise})", 
                                           ['low', 'medium', 'high', 'extreme'],
                                           format_func=lambda x: get_text(x),
                                           key=f"intensity_{exercise}")
                with col3:
                    distance = st.number_input(f"Distance (km) ({exercise})", min_value=0.0, max_value=50.0, value=0.0, step=0.1, key=f"distance_{exercise}")
                
                # Calculate calories for cardio
                calories = calculate_calories(exercise, duration, intensity)
                estimated_duration = duration
                
                session_data.append({
                    'exercise': exercise,
                    'duration': estimated_duration,
                    'intensity': intensity,
                    'distance': distance,
                    'calories': calories,
                    'type': 'cardio'
                })
                
            else:
                st.subheader(f"🏋️ {exercise}")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    sets = st.number_input(f"{get_text('sets')} ({exercise})", min_value=1, max_value=10, value=3, key=f"sets_{exercise}")
                with col2:
                    reps = st.number_input(f"{get_text('reps')} ({exercise})", min_value=1, max_value=50, value=10, key=f"reps_{exercise}")
                with col3:
                    weight = st.number_input(f"{get_text('weight_kg')} ({exercise})", min_value=0, max_value=500, value=0, key=f"weight_{exercise}")
                with col4:
                    rest_time = st.number_input(f"{get_text('rest_time')} ({exercise})", min_value=30, max_value=300, value=60, key=f"rest_{exercise}")
                
                # Calculate estimated duration and calories for strength
                estimated_duration = sets * 2 + (sets - 1) * (rest_time / 60)  # 2 minutes per set + rest time
                calories = calculate_calories(exercise, estimated_duration)
                
                session_data.append({
                    'exercise': exercise,
                    'sets': sets,
                    'reps': reps,
                    'weight': weight,
                    'rest_time': rest_time,
                    'duration': estimated_duration,
                    'calories': calories,
                    'type': 'strength'
                })
            
            total_session_calories += calories
            total_session_time += estimated_duration
            
            st.info(f"Estimated: {estimated_duration:.1f} min, {calories} calories")
        
        if selected_exercises:
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(get_text('total_calories'), f"{total_session_calories}")
            with col2:
                st.metric(get_text('session_duration'), f"{total_session_time:.1f} min")
            
            if st.button(get_text('register_session')):
                for exercise_data in session_data:
                    exercise_data['date'] = datetime.now().date()
                    exercise_data['timestamp'] = datetime.now()
                    st.session_state.workouts.append(exercise_data)
                
                st.session_state.user_stats['total_workouts'] += len(session_data)
                st.session_state.user_stats['total_calories'] += total_session_calories
                
                st.success(f"{get_text('session_registered')} 🔥")
                st.balloons()
                st.rerun()
        
        # Custom exercise addition
        st.markdown("---")
        st.subheader(get_text('add_custom_exercise'))
        
        col1, col2 = st.columns(2)
        with col1:
            custom_name = st.text_input(get_text('custom_exercise_name'))
            custom_muscle_groups = st.multiselect(
                get_text('muscle_groups'),
                ['chest', 'back', 'shoulders', 'arms', 'legs', 'core', 'full_body'],
                format_func=lambda x: get_text(x)
            )
        
        with col2:
            custom_calories = st.number_input("Calories per minute", min_value=1, max_value=30, value=8)
            
        if st.button(get_text('add_exercise')) and custom_name:
            new_exercise = {
                'name': custom_name,
                'calories_per_minute': custom_calories,
                'muscle_groups': custom_muscle_groups
            }
            st.session_state.custom_exercises.append(new_exercise)
            st.success(get_text('exercise_added'))
            st.rerun()

    # =============================================================================
    # TRAINING PLANNER PAGE
    # =============================================================================
    
    elif page == f"📅 {get_text('training_planner')}":
        st.header(get_text('training_plan'))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fitness_goal = st.selectbox(
                get_text('fitness_goal'),
                ['weight_loss', 'muscle_gain', 'endurance', 'strength', 'general_fitness'],
                format_func=lambda x: get_text(x)
            )
        
        with col2:
            fitness_level = st.selectbox(
                get_text('current_fitness'),
                ['beginner', 'intermediate', 'advanced', 'expert'],
                format_func=lambda x: get_text(x)
            )
        
        with col3:
            available_time = st.number_input(
                get_text('available_time'),
                min_value=15, max_value=180, value=60
            )
        
        if st.button(get_text('generate_plan')):
            plan = generate_training_plan(fitness_goal, fitness_level, available_time)
            
            st.subheader(get_text('your_plan'))
            
            # Display plan in a nice format
            for i, exercise in enumerate(plan, 1):
                st.write(f"**{get_text('day')} {i}:** {exercise}")
            
            # Weekly schedule visualization
            df_plan = pd.DataFrame({
                'Day': [f"Day {i}" for i in range(1, len(plan) + 1)],
                'Exercise': plan,
                'Estimated_Calories': [np.random.randint(200, 500) for _ in plan]
            })
            
            fig = px.bar(df_plan, x='Day', y='Estimated_Calories', 
                        title=get_text('recommended_plan'),
                        color='Estimated_Calories',
                        color_continuous_scale='viridis')
            st.plotly_chart(fig, use_container_width=True)

    # =============================================================================
    # STATS EVOLUTION PAGE
    # =============================================================================
    
    elif page == f"📈 {get_text('stats_evolution')}":
        st.header(get_text('progress_tracking'))
        
        if not st.session_state.workouts:
            st.info("Start working out to see your progress! 💪")
            return
        
        # Create sample progression data if none exists
        if not st.session_state.user_stats['weight_data']:
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
            st.session_state.user_stats['weight_data'] = [
                {'date': date, 'weight': 75 - np.random.normal(0, 0.5)} for date in dates
            ]
            st.session_state.user_stats['strength_data'] = [
                {'date': date, 'bench_press': 60 + np.random.normal(0, 2)} for date in dates
            ]
            st.session_state.user_stats['endurance_data'] = [
                {'date': date, 'running_time': 20 + np.random.normal(0, 1)} for date in dates
            ]
        
        # Workout frequency over time
        workout_df = pd.DataFrame(st.session_state.workouts)
        if not workout_df.empty:
            workout_df['date'] = pd.to_datetime(workout_df['date'])
            daily_workouts = workout_df.groupby(workout_df['date'].dt.date).size().reset_index()
            daily_workouts.columns = ['date', 'workouts']
            
            fig = px.line(daily_workouts, x='date', y='workouts', 
                         title="Daily Workout Frequency",
                         markers=True)
            st.plotly_chart(fig, use_container_width=True)
            
            # Calories burned over time
            daily_calories = workout_df.groupby(workout_df['date'].dt.date)['calories'].sum().reset_index()
            fig2 = px.bar(daily_calories, x='date', y='calories',
                         title=get_text('monthly_calories'),
                         color='calories',
                         color_continuous_scale='reds')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Progress metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader(get_text('weight_progress'))
            weight_df = pd.DataFrame(st.session_state.user_stats['weight_data'])
            fig = px.line(weight_df, x='date', y='weight', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader(get_text('strength_progress'))
            strength_df = pd.DataFrame(st.session_state.user_stats['strength_data'])
            fig = px.line(strength_df, x='date', y='bench_press', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.subheader(get_text('endurance_progress'))
            endurance_df = pd.DataFrame(st.session_state.user_stats['endurance_data'])
            fig = px.line(endurance_df, x='date', y='running_time', markers=True)
            st.plotly_chart(fig, use_container_width=True)

    # =============================================================================
    # GYM RANKING PAGE
    # =============================================================================
    
    elif page == f"🏆 {get_text('gym_ranking')}":
        st.header(get_text('gym_leaderboard'))
        
        # Add current user to ranking
        user_avg_calories = (st.session_state.user_stats['total_calories'] / 
                           max(st.session_state.user_stats['total_workouts'], 1))
        
        current_user = {
            'name': st.session_state.user_name,
            'workouts': st.session_state.user_stats['total_workouts'],
            'avg_calories': user_avg_calories
        }
        
        all_users = st.session_state.gym_users + [current_user]
        
        # Sort by total score (workouts * avg_calories)
        for user in all_users:
            user['score'] = user['workouts'] * user['avg_calories']
        
        all_users.sort(key=lambda x: x['score'], reverse=True)
        
        # Add rank
        for i, user in enumerate(all_users, 1):
            user['rank'] = i
        
        # Display leaderboard
        df_ranking = pd.DataFrame(all_users)
        df_ranking = df_ranking[['rank', 'name', 'workouts', 'avg_calories', 'score']]
        df_ranking.columns = [get_text('rank'), get_text('user_name'), 
                             get_text('total_workouts'), get_text('avg_calories'), 'Score']
        
        # Highlight current user
        def highlight_user(row):
            if row[get_text('user_name')] == st.session_state.user_name:
                return ['background-color: #FFD700'] * len(row)
            return [''] * len(row)
        
        styled_df = df_ranking.style.apply(highlight_user, axis=1)
        st.dataframe(styled_df, use_container_width=True)
        
        # User's current rank
        user_rank = next((user['rank'] for user in all_users if user['name'] == st.session_state.user_name), 999)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(get_text('your_rank'), f"#{user_rank}")
        with col2:
            st.metric("Score", f"{current_user['score']:.1f}")
        
        st.info(get_text('compete_message'))
        
        # Ranking visualization
        fig = px.bar(df_ranking.head(10), x=get_text('user_name'), y='Score',
                    title="Top 10 Gym Members",
                    color='Score',
                    color_continuous_scale='viridis')
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # =============================================================================
    # ANIME ZONE PAGE
    # =============================================================================
    
    elif page == f"🎌 {get_text('anime_zone')}":
        st.header(get_text('anime_motivation'))
        
        # Motivational quotes
        st.subheader(get_text('motivational_quotes'))
        quotes = get_anime_quotes()
        
        if st.button("Get New Quote! 🔥"):
            quote = np.random.choice(quotes)
            st.success(f"💪 {quote}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(get_text('training_music'))
            st.write("🎵 **Epic Training Playlist:**")
            music_list = [
                "🔥 Dragon Ball Z - Vegeta's Theme",
                "⚡ Naruto - The Raising Fighting Spirit",
                "💪 Attack on Titan - You See Big Girl",
                "🌟 One Piece - Overtaken",
                "⚔️ Bleach - Number One",
                "🥊 Hajime no Ippo - Inner Light",
                "🏃 Haikyuu!! - Karasuno Fight",
                "💥 My Hero Academia - You Say Run"
            ]
            
            for song in music_list:
                st.write(song)
                
        with col2:
            st.subheader(get_text('character_inspiration'))
            
            characters = {
                "🥋 Goku (Dragon Ball)": "Never stops training, always pushes limits",
                "💪 All Might (My Hero Academia)": "Symbol of strength and determination",
                "🏃 Rock Lee (Naruto)": "Hard work beats talent",
                "⚡ Saitama (One Punch Man)": "100 push-ups, 100 sit-ups, 100 squats, 10km run EVERY DAY!",
                "🔥 Natsu (Fairy Tail)": "Never gives up, burns with passion",
                "⚔️ Tanjiro (Demon Slayer)": "Discipline and constant improvement"
            }
            
            selected_character = st.selectbox("Choose your inspiration:", list(characters.keys()))
            st.info(f"**Motivation:** {characters[selected_character]}")
        
        # Training timer with anime motivation
        st.markdown("---")
        st.subheader("🏋️ Anime Training Timer")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            timer_minutes = st.number_input("Training time (minutes):", min_value=1, max_value=120, value=25)
        with col2:
            if st.button("Start Training! 💪"):
                st.session_state.training_start = time.time()
                st.session_state.training_duration = timer_minutes * 60
        
        if 'training_start' in st.session_state:
            elapsed = time.time() - st.session_state.training_start
            remaining = max(0, st.session_state.training_duration - elapsed)
            
            if remaining > 0:
                minutes_left = int(remaining // 60)
                seconds_left = int(remaining % 60)
                st.write(f"⏰ Time remaining: {minutes_left:02d}:{seconds_left:02d}")
                
                progress = 1 - (remaining / st.session_state.training_duration)
                st.progress(progress)
                
                if progress > 0.5:
                    st.write("🔥 You're over halfway! Keep pushing like Goku!")
                
                # Auto-refresh every second
                time.sleep(1)
                st.rerun()
            else:
                st.success("🎉 Training complete! You're getting stronger like your favorite anime heroes!")
                st.balloons()
                if 'training_start' in st.session_state:
                    del st.session_state.training_start

if __name__ == "__main__":
    main()
