import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import json
from datetime import datetime, date, timedelta
import requests
import openai
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Rep&Run - Hybrid Athlete Training",
    page_icon="🏃‍♂️💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# INITIALIZE SESSION STATE
# =============================================================================
if 'running_sessions' not in st.session_state:
    st.session_state.running_sessions = []

if 'strength_sessions' not in st.session_state:
    st.session_state.strength_sessions = []

if 'nutrition_log' not in st.session_state:
    st.session_state.nutrition_log = []

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': '',
        'age': 25,
        'weight': 70,
        'height': 170,
        'gender': 'Male',
        'max_hr': 195,
        'fitness_goal': 'Maintenance',
        'dietary_preferences': []
    }

if 'daily_nutrition_goals' not in st.session_state:
    st.session_state.daily_nutrition_goals = {
        'calories': 2000,
        'protein': 150,
        'carbs': 250,
        'fat': 65
    }

# =============================================================================
# DATABASES
# =============================================================================
RUNNING_TYPES = ['Fartlek', 'Intervals', 'Long Run', 'Recovery Run', 'Easy Run', 'Tempo Run']

EXERCISE_DATABASE = {
    'Compound': {
        'Squat': ['Quadriceps', 'Glutes', 'Hamstrings', 'Core'],
        'Deadlift': ['Hamstrings', 'Glutes', 'Lower Back', 'Core'],
        'Bench Press': ['Chest', 'Triceps', 'Shoulders'],
        'Overhead Press': ['Shoulders', 'Triceps', 'Core'],
        'Pull-ups': ['Back', 'Biceps', 'Shoulders'],
        'Rows': ['Back', 'Biceps', 'Shoulders']
    },
    'Isolation': {
        'Bicep Curls': ['Biceps'],
        'Tricep Extensions': ['Triceps'],
        'Leg Extensions': ['Quadriceps'],
        'Leg Curls': ['Hamstrings'],
        'Calf Raises': ['Calves'],
        'Lateral Raises': ['Shoulders']
    },
    'Functional': {
        'Burpees': ['Full Body'],
        'Mountain Climbers': ['Core', 'Cardio'],
        'Planks': ['Core'],
        'Push-ups': ['Chest', 'Triceps', 'Shoulders'],
        'Lunges': ['Quadriceps', 'Glutes', 'Hamstrings']
    }
}

MUSIC_PLAYLISTS = {
    'Intense': [
        'High Energy Workout',
        'Power Training',
        'HIIT Motivation',
        'Strength Training Beats'
    ],
    'Recovery': [
        'Chill Workout',
        'Recovery Flow',
        'Light Cardio',
        'Stretching Music'
    ],
    'Strength': [
        'Heavy Lifting',
        'Power Metal',
        'Gym Motivation',
        'Strength Anthems'
    ],
    'Long Cardio': [
        'Running Mix',
        'Endurance Training',
        'Long Distance',
        'Cardio Vibes'
    ]
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def calculate_max_hr(age):
    """Calculate maximum heart rate using 220-age formula"""
    return 220 - age

def get_hr_zones(max_hr):
    """Calculate heart rate zones"""
    return {
        'Zone 1 (Recovery)': (max_hr * 0.5, max_hr * 0.6),
        'Zone 2 (Aerobic)': (max_hr * 0.6, max_hr * 0.7),
        'Zone 3 (Tempo)': (max_hr * 0.7, max_hr * 0.8),
        'Zone 4 (Threshold)': (max_hr * 0.8, max_hr * 0.9),
        'Zone 5 (Anaerobic)': (max_hr * 0.9, max_hr)
    }

def calculate_bmr(weight, height, age, gender):
    """Calculate Basal Metabolic Rate"""
    if gender == 'Male':
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity_level):
    """Calculate Total Daily Energy Expenditure"""
    multipliers = {
        'Sedentary': 1.2,
        'Light': 1.375,
        'Moderate': 1.55,
        'Active': 1.725,
        'Very Active': 1.9
    }
    return bmr * multipliers.get(activity_level, 1.55)

def generate_meal_suggestion(goal, preferences, calories):
    """Generate AI meal suggestions that respect dietary preferences and randomize options"""
    forbidden = {
        'Vegan': ['chicken', 'salmon', 'beef', 'turkey', 'egg', 'eggs', 'yogurt', 'cottage cheese', 'tuna', 'greek yogurt', 'dairy', 'cheese', 'milk', 'honey'],
        'Vegetarian': ['chicken', 'salmon', 'beef', 'turkey', 'tuna'],
        'Gluten-Free': ['toast', 'bread', 'quinoa (ok)', 'whole grain bread'],
        'Dairy-Free': ['yogurt', 'greek yogurt', 'cottage cheese', 'cheese', 'milk', 'dairy'],
        'Keto': ['rice', 'quinoa', 'sweet potato', 'bread', 'toast', 'banana', 'dried fruits'],
        'Paleo': ['dairy', 'cheese', 'yogurt', 'greek yogurt', 'cottage cheese', 'bread', 'toast', 'rice', 'quinoa']
    }
    alternatives = {
        'Vegan': {
            'eggs': 'tofu scramble',
            'chicken': 'grilled tofu',
            'salmon': 'grilled tempeh',
            'beef': 'lentil loaf',
            'turkey': 'chickpea salad',
            'yogurt': 'soy yogurt',
            'cottage cheese': 'almond yogurt',
            'tuna': 'chickpea salad',
            'greek yogurt': 'coconut yogurt',
            'milk': 'almond milk',
            'honey': 'maple syrup'
        },
        'Vegetarian': {
            'chicken': 'grilled halloumi',
            'salmon': 'grilled halloumi',
            'beef': 'tofu steak',
            'turkey': 'egg salad',
            'tuna': 'egg salad'
        },
        'Gluten-Free': {
            'toast': 'gluten-free toast',
            'bread': 'gluten-free bread',
            'whole grain bread': 'gluten-free bread'
        },
        'Dairy-Free': {
            'yogurt': 'soy yogurt',
            'greek yogurt': 'coconut yogurt',
            'cottage cheese': 'almond yogurt',
            'cheese': 'vegan cheese',
            'milk': 'almond milk',
            'dairy': 'plant-based alternative'
        },
        'Keto': {
            'rice': 'cauliflower rice',
            'quinoa': 'cauliflower rice',
            'sweet potato': 'zucchini',
            'bread': 'keto bread',
            'toast': 'keto toast',
            'banana': 'berries',
            'dried fruits': 'nuts'
        },
        'Paleo': {
            'dairy': 'coconut yogurt',
            'cheese': 'nut cheese',
            'yogurt': 'coconut yogurt',
            'greek yogurt': 'coconut yogurt',
            'cottage cheese': 'coconut yogurt',
            'bread': 'sweet potato toast',
            'toast': 'sweet potato toast',
            'rice': 'cauliflower rice',
            'quinoa': 'cauliflower rice'
        }
    }
    # Multiple options for each meal type
    suggestions = {
        'Muscle Gain': {
            'Breakfast': [
                'Oatmeal with protein powder, banana, and almonds',
                'Scrambled eggs with spinach and whole grain toast',
                'Greek yogurt parfait with berries and granola',
                'Protein pancakes with peanut butter and fruit'
            ],
            'Lunch': [
                'Grilled chicken with quinoa and vegetables',
                'Turkey and avocado wrap with mixed greens',
                'Salmon bowl with brown rice and edamame',
                'Beef stir-fry with broccoli and bell peppers'
            ],
            'Dinner': [
                'Salmon with sweet potato and broccoli',
                'Chicken curry with brown rice and peas',
                'Beef chili with beans and corn',
                'Tofu stir-fry with mixed vegetables and rice'
            ],
            'Snack': [
                'Greek yogurt with berries',
                'Protein smoothie with almond milk and banana',
                'Cottage cheese with pineapple',
                'Mixed nuts and dried fruits'
            ]
        },
        'Fat Loss': {
            'Breakfast': [
                'Egg white omelette with spinach',
                'Chia pudding with almond milk and berries',
                'Smoothie bowl with spinach and protein powder',
                'Avocado toast with tomato'
            ],
            'Lunch': [
                'Turkey salad with mixed greens',
                'Grilled shrimp with quinoa and veggies',
                'Chicken breast with roasted vegetables',
                'Lentil soup with side salad'
            ],
            'Dinner': [
                'Lean beef with cauliflower rice',
                'Baked cod with asparagus and sweet potato',
                'Stuffed bell peppers with turkey and rice',
                'Zucchini noodles with tomato sauce and tofu'
            ],
            'Snack': [
                'Cottage cheese with cucumber',
                'Apple slices with almond butter',
                'Carrot sticks with hummus',
                'Rice cakes with peanut butter'
            ]
        },
        'Maintenance': {
            'Breakfast': [
                'Whole grain toast with avocado and eggs',
                'Overnight oats with chia seeds and berries',
                'Yogurt bowl with granola and fruit',
                'Banana pancakes with honey'
            ],
            'Lunch': [
                'Tuna salad with whole grain bread',
                'Chicken Caesar salad',
                'Vegetable stir-fry with tofu',
                'Quinoa bowl with roasted veggies'
            ],
            'Dinner': [
                'Baked chicken with brown rice and vegetables',
                'Grilled fish with sweet potato fries',
                'Vegetarian chili with beans',
                'Stuffed zucchini boats with turkey'
            ],
            'Snack': [
                'Mixed nuts and dried fruits',
                'Rice cakes with cottage cheese',
                'Fruit salad',
                'Protein bar'
            ]
        }
    }
    # Randomly select one meal for each type
    meal_plan = {}
    for meal_type, options in suggestions.get(goal, suggestions['Maintenance']).items():
        meal_plan[meal_type] = random.choice(options)
    # For each meal, check for forbidden ingredients and replace if needed
    for pref in preferences:
        for meal, desc in meal_plan.items():
            for item in forbidden.get(pref, []):
                if item in desc.lower():
                    alt = alternatives.get(pref, {}).get(item, None)
                    if alt:
                        desc = desc.lower().replace(item, alt)
                    else:
                        desc = desc.lower().replace(item, '')
            meal_plan[meal] = desc.capitalize()
    return meal_plan

def create_running_map(city="New York"):
    """Create a sample running route map for a specific city"""
    city_coords = {
        'New York': {
            'center': [40.7128, -74.0060],
            'route': [
                [40.7128, -74.0060],
                [40.7142, -74.0064],
                [40.7156, -74.0068],
                [40.7170, -74.0072],
                [40.7184, -74.0076],
                [40.7198, -74.0080]
            ]
        },
        'Los Angeles': {
            'center': [34.0522, -118.2437],
            'route': [
                [34.0522, -118.2437],
                [34.0536, -118.2441],
                [34.0550, -118.2445],
                [34.0564, -118.2449],
                [34.0578, -118.2453],
                [34.0592, -118.2457]
            ]
        },
        'Buenos Aires': {
            'center': [-34.6118, -58.3960],
            'route': [
                [-34.6118, -58.3960],
                [-34.6104, -58.3956],
                [-34.6090, -58.3952],
                [-34.6076, -58.3948],
                [-34.6062, -58.3944],
                [-34.6048, -58.3940]
            ]
        },
        'Valencia': {
            'center': [39.4699, -0.3763],
            'route': [
                [39.4699, -0.3763],
                [39.4713, -0.3759],
                [39.4727, -0.3755],
                [39.4741, -0.3751],
                [39.4755, -0.3747],
                [39.4769, -0.3743]
            ]
        },
        'London': {
            'center': [51.5074, -0.1278],
            'route': [
                [51.5074, -0.1278],
                [51.5088, -0.1274],
                [51.5102, -0.1270],
                [51.5116, -0.1266],
                [51.5130, -0.1262],
                [51.5144, -0.1258]
            ]
        }
    }
    
    city_data = city_coords.get(city, city_coords['New York'])
    route_coords = city_data['route']
    
    m = folium.Map(location=city_data['center'], zoom_start=15)
    
    folium.PolyLine(
        route_coords,
        weight=3,
        color='red',
        opacity=0.8
    ).add_to(m)
    
    folium.Marker(
        route_coords[0],
        popup='Start',
        icon=folium.Icon(color='green', icon='play')
    ).add_to(m)
    
    folium.Marker(
        route_coords[-1],
        popup='End',
        icon=folium.Icon(color='red', icon='stop')
    ).add_to(m)
    
    return m

def find_nearby_gyms(city):
    """Find gyms in a specific city (mock data)"""
    gyms = {
        'New York': [
            {'name': 'Planet Fitness', 'address': '123 Main St', 'rating': 4.2},
            {'name': 'LA Fitness', 'address': '456 Oak Ave', 'rating': 4.0},
            {'name': 'Gold\'s Gym', 'address': '789 Pine St', 'rating': 4.5}
        ],
        'Los Angeles': [
            {'name': '24 Hour Fitness', 'address': '321 Sunset Blvd', 'rating': 4.1},
            {'name': 'Equinox', 'address': '654 Beverly Dr', 'rating': 4.8},
            {'name': 'Crunch Fitness', 'address': '987 Wilshire Blvd', 'rating': 4.3}
        ],
        'Buenos Aires': [
            {'name': 'Gimnasio Central Buenos Aires', 'address': 'Calle Principal 123', 'rating': 4.4},
            {'name': 'Fitness Club Buenos Aires', 'address': 'Avenida Deportiva 456', 'rating': 4.1},
            {'name': 'Power Gym Buenos Aires', 'address': 'Plaza Central 789', 'rating': 4.6}
        ],
        'Valencia': [
            {'name': 'Gimnasio Valencia Centro', 'address': 'Carrer de la Pau 123', 'rating': 4.3},
            {'name': 'Fitness Valencia', 'address': 'Avinguda del Port 456', 'rating': 4.5},
            {'name': 'Gym Valencia Beach', 'address': 'Passeig Marítim 789', 'rating': 4.2}
        ],
        'London': [
            {'name': 'PureGym London', 'address': '123 Oxford Street', 'rating': 4.0},
            {'name': 'The Gym Group', 'address': '456 Regent Street', 'rating': 4.2},
            {'name': 'Fitness First', 'address': '789 Piccadilly', 'rating': 4.4}
        ]
    }
    return gyms.get(city, [])

def find_running_routes(city):
    """Find running routes in a specific city (mock data)"""
    routes = {
        'New York': [
            {'name': 'Central Park Loop', 'distance': '6.1 km', 'surface': 'Mixed', 'difficulty': 'Easy'},
            {'name': 'Brooklyn Bridge Run', 'distance': '3.2 km', 'surface': 'Paved', 'difficulty': 'Moderate'},
            {'name': 'Hudson River Greenway', 'distance': '8.5 km', 'surface': 'Paved', 'difficulty': 'Easy'}
        ],
        'Los Angeles': [
            {'name': 'Runyon Canyon Trail', 'distance': '4.8 km', 'surface': 'Trail', 'difficulty': 'Hard'},
            {'name': 'Santa Monica Beach Path', 'distance': '7.2 km', 'surface': 'Paved', 'difficulty': 'Easy'},
            {'name': 'Griffith Observatory Trail', 'distance': '5.6 km', 'surface': 'Trail', 'difficulty': 'Moderate'}
        ],
        'Buenos Aires': [
            {'name': 'Parque Central Buenos Aires', 'distance': '4.2 km', 'surface': 'Mixed', 'difficulty': 'Easy'},
            {'name': 'Ruta Costera Buenos Aires', 'distance': '7.8 km', 'surface': 'Paved', 'difficulty': 'Moderate'},
            {'name': 'Sendero Montaña Buenos Aires', 'distance': '5.5 km', 'surface': 'Trail', 'difficulty': 'Hard'}
        ],
        'Valencia': [
            {'name': 'Jardín del Turia', 'distance': '9.0 km', 'surface': 'Paved', 'difficulty': 'Easy'},
            {'name': 'Paseo Marítimo Valencia', 'distance': '6.3 km', 'surface': 'Paved', 'difficulty': 'Easy'},
            {'name': 'Ruta del Cabanyal', 'distance': '4.7 km', 'surface': 'Mixed', 'difficulty': 'Moderate'}
        ],
        'London': [
            {'name': 'Hyde Park Loop', 'distance': '7.2 km', 'surface': 'Mixed', 'difficulty': 'Easy'},
            {'name': 'Thames Path', 'distance': '8.9 km', 'surface': 'Paved', 'difficulty': 'Moderate'},
            {'name': 'Regent\'s Park Circuit', 'distance': '4.1 km', 'surface': 'Mixed', 'difficulty': 'Easy'}
        ]
    }
    return routes.get(city, [])

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
st.sidebar.title("🏃‍♂️💪 Rep&Run")
st.sidebar.write("Hybrid Athlete Training Platform")

page = st.sidebar.selectbox(
    "Navigate to:",
    [
        "🏠 Dashboard",
        "🏃‍♂️ Running Sessions",
        "💪 Strength Training",
        "🥗 Nutrition & AI Meals",
        "❤️ Heart Rate Zones",
        "🗺️ Routes & Gyms",
        "🎵 Music Recommendations",
        "👤 Profile & Settings"
    ]
)

# =============================================================================
# DASHBOARD PAGE
# =============================================================================
if page == "🏠 Dashboard":
    st.title("🏠 Rep&Run Dashboard")
    st.write("Welcome to your hybrid athlete training platform!")
    
    # User stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Running Sessions", len(st.session_state.running_sessions))
    
    with col2:
        st.metric("Strength Sessions", len(st.session_state.strength_sessions))
    
    with col3:
        total_distance = sum(session.get('distance', 0) for session in st.session_state.running_sessions)
        st.metric("Total Distance (km)", f"{total_distance:.1f}")
    
    with col4:
        total_weight = sum(session.get('total_weight', 0) for session in st.session_state.strength_sessions)
        st.metric("Total Weight Lifted (kg)", f"{total_weight:.0f}")
    
    # Recent activity
    st.subheader("📊 Recent Activity")
    
    if st.session_state.running_sessions or st.session_state.strength_sessions:
        all_sessions = []
        for session in st.session_state.running_sessions[-5:]:
            session['type'] = 'Running'
            all_sessions.append(session)
        
        for session in st.session_state.strength_sessions[-5:]:
            session['type'] = 'Strength'
            all_sessions.append(session)
        
        all_sessions.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        for session in all_sessions[:5]:
            if session['type'] == 'Running':
                st.write(f"🏃‍♂️ {session.get('type_name', 'Run')} - {session.get('distance', 0):.1f}km - {session.get('duration', 0)}min")
            else:
                st.write(f"💪 {session.get('routine_name', 'Workout')} - {session.get('total_weight', 0):.0f}kg - {session.get('duration', 0)}min")
    else:
        st.write("No sessions recorded yet. Start your training journey!")
    
    # Progress charts
    st.subheader("📈 Progress Overview")
    
    if st.session_state.running_sessions:
        running_data = pd.DataFrame(st.session_state.running_sessions)
        if not running_data.empty and 'pace' in running_data.columns:
            # Show only last 10 sessions, sorted by timestamp
            running_data = running_data.sort_values('date').tail(10)
            fig = px.bar(
                running_data,
                x='date',
                y='pace',
                title='Average Running Pace (min/km) - Last 10 Sessions',
                labels={'date': 'Date & Time', 'pace': 'Avg Pace (min/km)'}
            )
            fig.update_layout(xaxis_tickformat='%Y-%m-%d %H:%M', yaxis=dict(autorange='reversed'))  # Lower pace is better
            st.plotly_chart(fig, use_container_width=True)
    
    if st.session_state.strength_sessions:
        strength_data = pd.DataFrame(st.session_state.strength_sessions)
        if not strength_data.empty and 'total_weight' in strength_data.columns:
            # Show only last 10 sessions, sorted by timestamp
            strength_data = strength_data.sort_values('date').tail(10)
            fig = px.bar(
                strength_data,
                x='date',
                y='total_weight',
                title='Total Weight Lifted (kg) - Last 10 Sessions',
                labels={'date': 'Date & Time', 'total_weight': 'Total Weight (kg)'}
            )
            fig.update_layout(xaxis_tickformat='%Y-%m-%d %H:%M')
            st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# RUNNING SESSIONS PAGE
# =============================================================================
elif page == "🏃‍♂️ Running Sessions":
    st.title("🏃‍♂️ Running Session Management")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Session", "📊 View Sessions", "🗺️ Route Map"])
    
    with tab1:
        st.subheader("Create New Running Session")
        
        col1, col2 = st.columns(2)
        
        with col1:
            session_type = st.selectbox("Session Type", RUNNING_TYPES)
            duration = st.number_input("Duration (minutes)", min_value=1, value=30)
            distance = st.number_input("Distance (km)", min_value=0.1, value=5.0, step=0.1)
        
        with col2:
            # Calculate average pace (min/km) if distance > 0
            if distance > 0:
                avg_pace = duration / distance
            else:
                avg_pace = 0
            st.metric("Average Pace (min/km)", f"{avg_pace:.2f}")
            max_pace = st.number_input("Maximum Pace (min/km)", min_value=3.0, value=4.5, step=0.1)
            avg_hr = st.number_input("Average Heart Rate (BPM)", min_value=60, value=150)
            max_hr = st.number_input("Maximum Heart Rate (BPM)", min_value=60, value=170)
        
        notes = st.text_area("Session Notes")
        perceived_effort = st.slider("Perceived Effort (1-10)", min_value=1, max_value=10, value=5)
        
        if st.button("Save Running Session"):
            session = {
                'id': len(st.session_state.running_sessions) + 1,
                'date': datetime.now().isoformat(sep=' ', timespec='seconds'),
                'type_name': session_type,
                'duration': duration,
                'distance': distance,
                'pace': avg_pace,
                'max_pace': max_pace,
                'avg_hr': avg_hr,
                'max_hr': max_hr,
                'notes': notes,
                'perceived_effort': perceived_effort
            }
            st.session_state.running_sessions.append(session)
            st.success("Running session saved successfully!")
    
    with tab2:
        st.subheader("Running Sessions History")
        
        if st.session_state.running_sessions:
            df = pd.DataFrame(st.session_state.running_sessions)
            st.dataframe(df[['date', 'type_name', 'distance', 'duration', 'pace', 'avg_hr']])
            
            session_to_delete = st.selectbox(
                "Select session to delete:",
                options=[f"{s['date']} - {s['type_name']} - {s['distance']}km" for s in st.session_state.running_sessions],
                key="delete_running"
            )
            
            if st.button("Delete Selected Session"):
                idx = [f"{s['date']} - {s['type_name']} - {s['distance']}km" for s in st.session_state.running_sessions].index(session_to_delete)
                del st.session_state.running_sessions[idx]
                st.success("Session deleted!")
                st.rerun()
        else:
            st.write("No running sessions recorded yet.")
    
    with tab3:
        st.subheader("GPS Route Map")
        st.write("Sample running route visualization:")
        map_obj = create_running_map()
        folium_static(map_obj)

# =============================================================================
# STRENGTH TRAINING PAGE
# =============================================================================
elif page == "💪 Strength Training":
    st.title("💪 Strength Training Management")
    
    tab1, tab2, tab3 = st.tabs(["➕ Add Session", "📊 View Sessions", "🏋️ Exercise Database"])
    
    with tab1:
        st.subheader("Create New Strength Training Session")
        
        routine_name = st.text_input("Routine Name", value="Upper Body")
        
        exercise_type = st.selectbox("Exercise Type", list(EXERCISE_DATABASE.keys()))
        exercise_name = st.selectbox("Exercise", list(EXERCISE_DATABASE[exercise_type].keys()))
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sets = st.number_input("Sets", min_value=1, value=3)
            reps = st.number_input("Reps per Set", min_value=1, value=10)
        
        with col2:
            weight = st.number_input("Weight (kg)", min_value=0, value=50)
            rest_time = st.number_input("Rest Time (seconds)", min_value=30, value=60)
        
        with col3:
            rpe = st.slider("RPE (Rate of Perceived Exertion)", min_value=1, max_value=10, value=7)
            duration = st.number_input("Session Duration (minutes)", min_value=10, value=45)
        
        if st.button("Save Strength Session"):
            session = {
                'id': len(st.session_state.strength_sessions) + 1,
                'date': datetime.now().isoformat(sep=' ', timespec='seconds'),
                'routine_name': routine_name,
                'exercise_type': exercise_type,
                'exercise_name': exercise_name,
                'sets': sets,
                'reps': reps,
                'weight': weight,
                'rest_time': rest_time,
                'rpe': rpe,
                'duration': duration,
                'total_weight': sets * reps * weight,
                'targeted_muscles': EXERCISE_DATABASE[exercise_type][exercise_name]
            }
            st.session_state.strength_sessions.append(session)
            st.success("Strength training session saved successfully!")
    
    with tab2:
        st.subheader("Strength Training History")
        
        if st.session_state.strength_sessions:
            df = pd.DataFrame(st.session_state.strength_sessions)
            st.dataframe(df[['date', 'routine_name', 'exercise_name', 'sets', 'reps', 'weight', 'total_weight']])
            
            if len(st.session_state.strength_sessions) > 1:
                fig = px.line(df, x='date', y='total_weight', title='Strength Training Volume Progress')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No strength training sessions recorded yet.")
    
    with tab3:
        st.subheader("Exercise Database")
        
        for category, exercises in EXERCISE_DATABASE.items():
            with st.expander(f"{category} Exercises"):
                for exercise, muscles in exercises.items():
                    st.write(f"**{exercise}**: {', '.join(muscles)}")

# =============================================================================
# NUTRITION & AI MEALS PAGE
# =============================================================================
elif page == "🥗 Nutrition & AI Meals":
    st.title("🥗 Nutrition & AI Meal Suggestions")
    
    tab1, tab2, tab3 = st.tabs(["🤖 AI Meal Suggestions", "📝 Food Logging", "📊 Nutrition Tracking"])
    
    with tab1:
        st.subheader("AI-Powered Meal Suggestions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fitness_goal = st.selectbox("Fitness Goal", ["Muscle Gain", "Fat Loss", "Maintenance"])
            dietary_preferences = st.multiselect(
                "Dietary Preferences",
                ["Vegan", "Vegetarian", "Gluten-Free", "Dairy-Free", "Keto", "Paleo"]
            )
        
        with col2:
            target_calories = st.number_input("Target Calories", min_value=1200, value=2000, step=100)
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"])
        
        if st.button("Generate Meal Suggestion"):
            suggestion = generate_meal_suggestion(fitness_goal, dietary_preferences, target_calories)
            
            st.subheader(f"🍽️ {meal_type} Suggestion")
            st.write(f"**Meal**: {suggestion[meal_type]}")
            
            macros = {
                'Protein': np.random.randint(20, 40),
                'Carbs': np.random.randint(30, 60),
                'Fat': np.random.randint(10, 25),
                'Calories': np.random.randint(300, 600)
            }
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Protein (g)", macros['Protein'])
            with col2:
                st.metric("Carbs (g)", macros['Carbs'])
            with col3:
                st.metric("Fat (g)", macros['Fat'])
            with col4:
                st.metric("Calories", macros['Calories'])
    
    with tab2:
        st.subheader("Manual Food Logging")
        
        food_name = st.text_input("Food Name")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            calories = st.number_input("Calories", min_value=0, value=100)
        with col2:
            protein = st.number_input("Protein (g)", min_value=0.0, value=10.0, step=0.1)
        with col3:
            carbs = st.number_input("Carbs (g)", min_value=0.0, value=20.0, step=0.1)
        with col4:
            fat = st.number_input("Fat (g)", min_value=0.0, value=5.0, step=0.1)
        
        meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snack"], key="food_log")
        
        if st.button("Log Food"):
            food_entry = {
                'date': date.today().isoformat(),
                'food_name': food_name,
                'meal_type': meal_type,
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fat': fat
            }
            st.session_state.nutrition_log.append(food_entry)
            st.success("Food logged successfully!")
    
    with tab3:
        st.subheader("Daily Nutrition Summary")
        
        today = date.today().isoformat()
        today_foods = [f for f in st.session_state.nutrition_log if f['date'] == today]
        
        if today_foods:
            total_calories = sum(f['calories'] for f in today_foods)
            total_protein = sum(f['protein'] for f in today_foods)
            total_carbs = sum(f['carbs'] for f in today_foods)
            total_fat = sum(f['fat'] for f in today_foods)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Calories", f"{total_calories}/{st.session_state.daily_nutrition_goals['calories']}")
            with col2:
                st.metric("Protein (g)", f"{total_protein:.1f}/{st.session_state.daily_nutrition_goals['protein']}")
            with col3:
                st.metric("Carbs (g)", f"{total_carbs:.1f}/{st.session_state.daily_nutrition_goals['carbs']}")
            with col4:
                st.metric("Fat (g)", f"{total_fat:.1f}/{st.session_state.daily_nutrition_goals['fat']}")
            
            fig = go.Figure(data=[go.Pie(
                labels=['Protein', 'Carbs', 'Fat'],
                values=[total_protein * 4, total_carbs * 4, total_fat * 9],
                hole=0.4
            )])
            fig.update_layout(title="Macronutrient Distribution (Calories)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No food logged today.")

# =============================================================================
# HEART RATE ZONES PAGE
# =============================================================================
elif page == "❤️ Heart Rate Zones":
    st.title("❤️ Heart Rate Zones & Cardio Training")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Heart Rate Calculator")
        
        age = st.number_input("Age", min_value=10, max_value=100, value=25)
        max_hr = calculate_max_hr(age)
        
        st.metric("Maximum Heart Rate", f"{max_hr} BPM")
        
        hr_zones = get_hr_zones(max_hr)
        
        st.subheader("Heart Rate Zones")
        for zone, (min_hr, max_hr_zone) in hr_zones.items():
            st.write(f"**{zone}**: {min_hr:.0f} - {max_hr_zone:.0f} BPM")
    
    with col2:
        st.subheader("Zone Training Guide")
        
        zone_info = {
            'Zone 1 (Recovery)': 'Very light intensity, active recovery',
            'Zone 2 (Aerobic)': 'Light intensity, builds aerobic base',
            'Zone 3 (Tempo)': 'Moderate intensity, improves lactate threshold',
            'Zone 4 (Threshold)': 'Hard intensity, improves anaerobic capacity',
            'Zone 5 (Anaerobic)': 'Very hard intensity, improves sprint performance'
        }
        
        for zone, description in zone_info.items():
            with st.expander(zone):
                st.write(description)
    
    if st.session_state.running_sessions:
        st.subheader("Zone Analysis from Running Sessions")
        
        running_data = pd.DataFrame(st.session_state.running_sessions)
        if 'avg_hr' in running_data.columns and not running_data.empty:
            zone_times = {}
            for session in st.session_state.running_sessions:
                avg_hr = session.get('avg_hr', 0)
                duration = session.get('duration', 0)
                
                for zone, (min_hr, max_hr_zone) in hr_zones.items():
                    if min_hr <= avg_hr <= max_hr_zone:
                        zone_times[zone] = zone_times.get(zone, 0) + duration
                        break
            
            if zone_times:
                fig = px.pie(
                    values=list(zone_times.values()),
                    names=list(zone_times.keys()),
                    title="Time Spent in Each Heart Rate Zone"
                )
                st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# ROUTES & GYMS PAGE
# =============================================================================
elif page == "🗺️ Routes & Gyms":
    st.title("🗺️ Running Routes & Gyms")
    
    tab1, tab2 = st.tabs(["🏃‍♂️ Running Routes", "🏋️ Gyms"])
    
    with tab1:
        st.subheader("Find Running Routes by City")
        
        city = st.selectbox("Select City", ["New York", "Los Angeles", "Buenos Aires", "Valencia", "London"])
        
        if st.button("Search Routes"):
            routes = find_running_routes(city)
            
            if routes:
                st.subheader(f"Running Routes in {city}")
                
                for route in routes:
                    with st.expander(f"{route['name']} - {route['distance']}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Distance**: {route['distance']}")
                        with col2:
                            st.write(f"**Surface**: {route['surface']}")
                        with col3:
                            st.write(f"**Difficulty**: {route['difficulty']}")
                        
                        st.write("Route Preview:")
                        map_obj = create_running_map(city)
                        folium_static(map_obj, width=400, height=300)
            else:
                st.write(f"No routes found for {city}")
    
    with tab2:
        st.subheader("Find Gyms by City")
        
        city = st.selectbox("Select City", ["New York", "Los Angeles", "Buenos Aires", "Valencia", "London"], key="gym_city")
        
        if st.button("Search Gyms"):
            gyms = find_nearby_gyms(city)
            
            if gyms:
                st.subheader(f"Gyms in {city}")
                
                for gym in gyms:
                    with st.expander(f"{gym['name']} - ⭐ {gym['rating']}"):
                        st.write(f"**Address**: {gym['address']}")
                        st.write(f"**Rating**: ⭐ {gym['rating']}")
                        
                        st.write("Location:")
                        # Get city coordinates for gym location
                        city_coords = {
                            'New York': [40.7128, -74.0060],
                            'Los Angeles': [34.0522, -118.2437],
                            'Buenos Aires': [-34.6118, -58.3960],
                            'Valencia': [39.4699, -0.3763],
                            'London': [51.5074, -0.1278]
                        }
                        gym_location = city_coords.get(city, [40.7128, -74.0060])
                        
                        m = folium.Map(location=gym_location, zoom_start=13)
                        folium.Marker(
                            gym_location,
                            popup=gym['name'],
                            icon=folium.Icon(color='blue', icon='info-sign')
                        ).add_to(m)
                        folium_static(m, width=400, height=300)
            else:
                st.write(f"No gyms found for {city}")

# =============================================================================
# MUSIC RECOMMENDATIONS PAGE
# =============================================================================
elif page == "🎵 Music Recommendations":
    st.title("🎵 Music Recommendations for Training")
    
    st.subheader("Get Music Suggestions Based on Your Workout")
    
    workout_type = st.selectbox("Select Workout Type", list(MUSIC_PLAYLISTS.keys()))
    
    if st.button("Get Music Recommendations"):
        st.subheader(f"🎵 Music for {workout_type} Training")
        
        playlists = MUSIC_PLAYLISTS[workout_type]
        
        for i, playlist in enumerate(playlists, 1):
            with st.expander(f"{i}. {playlist}"):
                st.write("**Suggested Songs:**")
                
                songs = [
                    "High Energy Track 1 - Artist 1",
                    "Motivational Song 2 - Artist 2",
                    "Workout Anthem 3 - Artist 3",
                    "Power Beat 4 - Artist 4",
                    "Energy Boost 5 - Artist 5"
                ]
                
                for song in songs:
                    st.write(f"🎵 {song}")
                
                st.write("**Spotify Integration:**")
                st.write("Connect your Spotify account to automatically create playlists!")
                
                if st.button(f"Create Playlist: {playlist}", key=f"playlist_{i}"):
                    st.success(f"Playlist '{playlist}' created in Spotify!")
    
    st.subheader("🎧 Training Music Tips")
    
    tips = {
        'Intense': 'Choose high-tempo songs (140-160 BPM) with strong beats for maximum motivation.',
        'Recovery': 'Opt for slower, calming music (120-130 BPM) to maintain relaxed pace.',
        'Strength': 'Select heavy, powerful tracks that match your lifting rhythm.',
        'Long Cardio': 'Create varied playlists with different energy levels to maintain interest.'
    }
    
    for workout, tip in tips.items():
        with st.expander(f"💡 {workout} Training"):
            st.write(tip)

# =============================================================================
# PROFILE & SETTINGS PAGE
# =============================================================================
elif page == "👤 Profile & Settings":
    st.title("👤 Profile & Settings")
    
    st.subheader("User Profile")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.user_profile['name'] = st.text_input("Name", value=st.session_state.user_profile['name'])
        st.session_state.user_profile['age'] = st.number_input("Age", min_value=10, max_value=100, value=st.session_state.user_profile['age'])
        st.session_state.user_profile['weight'] = st.number_input("Weight (kg)", min_value=30, max_value=200, value=st.session_state.user_profile['weight'])
        st.session_state.user_profile['height'] = st.number_input("Height (cm)", min_value=100, max_value=250, value=st.session_state.user_profile['height'])
    
    with col2:
        st.session_state.user_profile['gender'] = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.user_profile['gender']))
        st.session_state.user_profile['fitness_goal'] = st.selectbox("Fitness Goal", ["Muscle Gain", "Fat Loss", "Maintenance"], index=["Muscle Gain", "Fat Loss", "Maintenance"].index(st.session_state.user_profile['fitness_goal']))
        st.session_state.user_profile['dietary_preferences'] = st.multiselect("Dietary Preferences", ["Vegan", "Vegetarian", "Gluten-Free", "Dairy-Free", "Keto", "Paleo"], default=st.session_state.user_profile['dietary_preferences'])
    
    max_hr = calculate_max_hr(st.session_state.user_profile['age'])
    bmr = calculate_bmr(
        st.session_state.user_profile['weight'],
        st.session_state.user_profile['height'],
        st.session_state.user_profile['age'],
        st.session_state.user_profile['gender']
    )
    tdee = calculate_tdee(bmr, "Moderate")
    
    st.subheader("Calculated Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Maximum Heart Rate", f"{max_hr} BPM")
    with col2:
        st.metric("BMR (Basal Metabolic Rate)", f"{bmr:.0f} calories")
    with col3:
        st.metric("TDEE (Total Daily Energy Expenditure)", f"{tdee:.0f} calories")
    
    st.subheader("Daily Nutrition Goals")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.session_state.daily_nutrition_goals['calories'] = st.number_input("Calories", min_value=1200, value=st.session_state.daily_nutrition_goals['calories'], step=100)
    with col2:
        st.session_state.daily_nutrition_goals['protein'] = st.number_input("Protein (g)", min_value=50, value=st.session_state.daily_nutrition_goals['protein'], step=5)
    with col3:
        st.session_state.daily_nutrition_goals['carbs'] = st.number_input("Carbs (g)", min_value=100, value=st.session_state.daily_nutrition_goals['carbs'], step=10)
    with col4:
        st.session_state.daily_nutrition_goals['fat'] = st.number_input("Fat (g)", min_value=30, value=st.session_state.daily_nutrition_goals['fat'], step=5)
    
    if st.button("Save Profile"):
        st.success("Profile saved successfully!")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🏃‍♂️💪 Rep&Run - Hybrid Athlete Training Platform</p>
        <p>Built with Streamlit, Plotly, Folium, and more!</p>
    </div>
    """,
    unsafe_allow_html=True
)
