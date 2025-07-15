import streamlit as st
import pandas as pd
from datetime import datetime
import base64
from pathlib import Path

# --- Configuración de la página ---
st.set_page_config(
    page_title="Gluten-Free Balance",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Función para cargar imágenes base64 ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- Función para establecer imagen de fondo ---
def set_bg_hack(main_bg):
    bin_str = get_base64_of_bin_file(main_bg)
    page_bg_img = f'''
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# --- Estilos CSS personalizados ---
st.markdown("""
    <style>
    /* Paleta de colores moderna */
    :root {
        --bg-color: #ffffff;
        --primary-color: #6C63FF;  /* Violeta moderno */
        --secondary-color: #00BFA6; /* Verde menta */
        --accent-color: #FF6584;   /* Rosa coral */
        --text-color: #2D3748;
        --card-bg: #ffffff;
        --hover-color: #f7fafc;
        --border-color: #E2E8F0;
    }
    
    .main {
        background-color: var(--bg-color);
        color: var(--text-color);
        padding: 2rem;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .stApp {
        background-color: var(--bg-color);
    }
    
    .stRadio > label {
        font-weight: 500;
        color: var(--text-color);
    }
    
    .landing-button {
        display: inline-block;
        padding: 1rem 2rem;
        margin: 0.5rem;
        border-radius: 8px;
        text-decoration: none;
        color: white;
        font-weight: 500;
        text-align: center;
        transition: all 0.3s ease;
        width: 200px;
        cursor: pointer;
        border: none;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    }
    
    .landing-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(108, 99, 255, 0.2);
    }
    
    .hero-section {
        text-align: center;
        padding: 4rem 2rem;
        border-radius: 20px;
        margin-bottom: 3rem;
        background: var(--card-bg);
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        border: 1px solid var(--border-color);
    }
    
    .feature-card {
        background: var(--card-bg);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        margin: 1rem;
        transition: all 0.3s ease;
        border: 1px solid var(--border-color);
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        background: var(--hover-color);
        border-color: var(--primary-color);
    }
    
    .meal-card {
        background: var(--card-bg);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border: 1px solid var(--border-color);
    }
    
    .sugar-low {
        color: var(--secondary-color);
    }
    
    .sugar-medium {
        color: #FFD93D;
    }
    
    .sugar-high {
        color: var(--accent-color);
    }

    .image-container {
        border-radius: 16px;
        overflow: hidden;
        margin: 1.5rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        aspect-ratio: 16/9;
    }

    .image-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }

    .image-container:hover img {
        transform: scale(1.05);
    }

    .benefits-section {
        background: var(--card-bg);
        padding: 3rem;
        border-radius: 20px;
        margin-top: 4rem;
        border: 1px solid var(--border-color);
    }

    .stat-card {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin: 1rem;
        backdrop-filter: blur(10px);
        flex: 1;
        min-width: 200px;
    }

    .stat-number {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .stat-label {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 500;
    }

    /* Grid system */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        padding: 1rem;
    }

    .stats-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 2rem;
        padding: 1rem;
    }

    /* Personalización de elementos Streamlit */
    .stSelectbox {
        background-color: var(--card-bg) !important;
    }

    .stTextInput > div > div > input {
        background-color: var(--card-bg);
        color: var(--text-color);
        border: 1px solid var(--border-color);
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color);
    }

    p {
        color: var(--text-color);
        opacity: 0.9;
    }

    /* Personalización del sidebar */
    .css-1d391kg {
        background-color: var(--card-bg);
    }

    /* Actualizar estilos de los botones */
    .nav-buttons-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
        margin: 3rem auto;
        max-width: 400px;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }

    .nav-button {
        width: 100%;
        padding: 1.5rem 2rem;
        border: none;
        border-radius: 12px;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        font-size: 1.2rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        margin: 0;
    }

    .nav-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(108, 99, 255, 0.25);
    }

    /* Ocultar los botones de Streamlit pero mantener su funcionalidad */
    .stButton {
        display: none;
    }

    </style>
""", unsafe_allow_html=True)

# --- Datos pre-cargados de comidas ---
preloaded_meals = [
    {"name": "Grilled Chicken Salad", "sugar_g": 2, "gluten_free": True},
    {"name": "Quinoa Veggie Bowl", "sugar_g": 4, "gluten_free": True},
    {"name": "Rice & Beans", "sugar_g": 1, "gluten_free": True},
    {"name": "Fruit Yogurt Parfait", "sugar_g": 12, "gluten_free": True},
    {"name": "Gluten-Free Pasta with Tomato Sauce", "sugar_g": 6, "gluten_free": True},
    {"name": "Turkey Lettuce Wraps", "sugar_g": 3, "gluten_free": True},
    {"name": "Omelette with Spinach", "sugar_g": 1, "gluten_free": True},
    {"name": "Chickpea Salad", "sugar_g": 2, "gluten_free": True},
    {"name": "Sweet Potato Bake", "sugar_g": 5, "gluten_free": True},
    {"name": "Gluten-Free Pancakes", "sugar_g": 8, "gluten_free": True},
]

# --- Función para clasificar el nivel de azúcar ---
def sugar_level(sugar_g):
    try:
        sugar_g = float(sugar_g)
        if sugar_g <= 3:
            return "Low", "🟢", "sugar-low"
        elif sugar_g <= 7:
            return "Medium", "🟠", "sugar-medium"
        else:
            return "High", "🔴", "sugar-high"
    except (ValueError, TypeError):
        return "Unknown", "⚪", ""

# --- Inicialización de sesión ---
if "meals" not in st.session_state:
    st.session_state["meals"] = preloaded_meals.copy()
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# --- Landing Page ---
if st.session_state["page"] == "Home":
    st.markdown("""
        <div class="hero-section">
            <h1 style="font-size: 3.5rem; margin-bottom: 1.5rem; background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Gluten-Free Balance
            </h1>
            <p style="font-size: 1.4rem; color: var(--text-color); margin-bottom: 2rem;">
                Your Smart Companion for a Balanced, Gluten-Free, and Low-Sugar Diet
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Estadísticas con mejor alineación
    st.markdown("""
        <div class="stats-container">
            <div class="stat-card">
                <div class="stat-number">100+</div>
                <div class="stat-label">Gluten-Free Recipes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">15k+</div>
                <div class="stat-label">Happy Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">24/7</div>
                <div class="stat-label">Meal Planning</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Características principales con grid system
    st.markdown("""
        <div class="grid-container">
            <div class="feature-card">
                <div class="image-container">
                    <img src="https://images.unsplash.com/photo-1546069901-ba9599a7e63c" alt="Meal Library">
                </div>
                <h3>Meal Library</h3>
                <p>Explore and manage your collection of gluten-free meals</p>
                <div style="margin-top: auto;">
                    <button class="landing-button">Open Library</button>
                </div>
            </div>
            <div class="feature-card">
                <div class="image-container">
                    <img src="https://images.unsplash.com/photo-1543340904-0b1d843bccda" alt="Weekly Planner">
                </div>
                <h3>Weekly Planner</h3>
                <p>Plan your meals for the week with our intuitive planner</p>
                <div style="margin-top: auto;">
                    <button class="landing-button">Start Planning</button>
                </div>
            </div>
            <div class="feature-card">
                <div class="image-container">
                    <img src="https://images.unsplash.com/photo-1490645935967-10de6ba17061" alt="Nutrition Tips">
                </div>
                <h3>Nutrition Tips</h3>
                <p>Get helpful advice for your gluten-free journey</p>
                <div style="margin-top: auto;">
                    <button class="landing-button">View Tips</button>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Beneficios con grid system
    st.markdown("""
        <div class="benefits-section">
            <h2 style="text-align: center; margin-bottom: 3rem; background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Why Choose Gluten-Free Balance?
            </h2>
            <div class="grid-container">
                <div class="feature-card">
                    <div class="image-container">
                        <img src="https://images.unsplash.com/photo-1494859802809-d069c3b71a8a" alt="Smart Filtering">
                    </div>
                    <h3>Smart Filtering</h3>
                    <p>Easily find meals that match your sugar preferences</p>
                </div>
                <div class="feature-card">
                    <div class="image-container">
                        <img src="https://images.unsplash.com/photo-1542010589005-d1eacc3918f2" alt="Visual Indicators">
                    </div>
                    <h3>Visual Indicators</h3>
                    <p>Clear sugar level indicators for informed choices</p>
                </div>
                <div class="feature-card">
                    <div class="image-container">
                        <img src="https://images.unsplash.com/photo-1466637574441-749b8f19452f" alt="Customizable">
                    </div>
                    <h3>Customizable</h3>
                    <p>Add your own meals and create personal plans</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Contenedor principal centrado
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; min-height: 50vh;">
            <div class="nav-buttons-container">
                <button class="nav-button" id="meal-library-btn">
                    Meal Library
                </button>
                <button class="nav-button" id="weekly-planner-btn">
                    Weekly Planner
                </button>
                <button class="nav-button" id="nutrition-tips-btn">
                    Nutrition Tips
                </button>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Botones de Streamlit para la funcionalidad (ocultos pero necesarios)
    if st.button("Meal Library", key="meal_lib"):
        st.session_state["page"] = "Meal Library"
        st.rerun()
    if st.button("Weekly Planner", key="weekly_plan"):
        st.session_state["page"] = "Weekly Planner"
        st.rerun()
    if st.button("Nutrition Tips", key="nutrition"):
        st.session_state["page"] = "Nutrition Tips"
        st.rerun()

else:
    # --- Menú de navegación ---
    menu = ["Meal Library", "Weekly Planner", "Nutrition Tips"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    # Botón para volver a la página principal
    if st.sidebar.button("Back to Home"):
        st.session_state["page"] = "Home"
        st.rerun()

    # --- Página principal: Meal Library ---
    if choice == "Meal Library":
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("🍽️ Meal Library")
            # Filtro por nivel de azúcar
            sugar_filter = st.radio(
                "Filter by sugar level:",
                ("All", "Low", "Medium", "High"),
                horizontal=True
            )
            
            # Filtrar comidas según selección
            def filter_meals(meals, level):
                if level == "All":
                    return meals
                return [m for m in meals if sugar_level(m["sugar_g"])[0] == level]

            filtered_meals = filter_meals(st.session_state["meals"], sugar_filter)

            # Mostrar comidas
            for idx, meal in enumerate(filtered_meals):
                level, emoji, color_class = sugar_level(meal["sugar_g"])
                st.markdown(f"""
                    <div class="meal-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h3>{meal['name']}</h3>
                                <p>✅ Gluten-free | <span class="{color_class}">{emoji} {level} sugar ({meal['sugar_g']}g)</span></p>
                            </div>
                            <div>
                                <button onclick="this.form.submit()">🗑️</button>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Delete", key=f"delete_{idx}"):
                    st.session_state["meals"].remove(meal)
                    st.rerun()

        with col2:
            st.header("➕ Add New Meal")
            with st.form("new_meal_form"):
                new_meal_name = st.text_input("Meal Name")
                new_meal_sugar = st.number_input("Sugar Content (g)", min_value=0.0, value=0.0, step=0.1)
                submitted = st.form_submit_button("Add Meal")
                
                if submitted:
                    if new_meal_name.strip():
                        new_meal = {
                            "name": new_meal_name,
                            "sugar_g": new_meal_sugar,
                            "gluten_free": True
                        }
                        st.session_state["meals"].append(new_meal)
                        st.success("Meal added successfully!")
                        st.rerun()
                    else:
                        st.error("Please enter a meal name.")

    # --- Página de planificador semanal ---
    elif choice == "Weekly Planner":
        st.header("🗓️ Weekly Meal Planner")
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        st.write("Select meals for each day:")
        
        for day in days:
            st.markdown(f"""
                <div class="feature-card">
                    <h3>{day}</h3>
            """, unsafe_allow_html=True)
            
            meal_options = ["Select a meal"] + [meal["name"] for meal in st.session_state["meals"]]
            selected_meal = st.selectbox(f"Meal for {day}", meal_options, key=f"meal_{day}")
            
            if selected_meal != "Select a meal":
                meal = next((m for m in st.session_state["meals"] if m["name"] == selected_meal), None)
                if meal:
                    level, emoji, color_class = sugar_level(meal["sugar_g"])
                    st.markdown(f"""
                        <p>✅ Gluten-free | <span class="{color_class}">{emoji} {level} sugar ({meal['sugar_g']}g)</span></p>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Página de consejos nutricionales ---
    elif choice == "Nutrition Tips":
        st.header("🛎️ Nutrition Tips & Warnings")
        
        tips = [
            {
                "title": "Hidden Sugars in Gluten-Free Products",
                "content": "Many gluten-free products contain added sugars to improve taste. Always check labels!",
                "icon": "🔍"
            },
            {
                "title": "Importance of Fiber",
                "content": "Gluten-free diets can be low in fiber. Include plenty of vegetables, legumes, and gluten-free whole grains.",
                "icon": "🥬"
            },
            {
                "title": "Cross-Contamination",
                "content": "Be careful with shared kitchen utensils and cooking surfaces to avoid gluten contamination.",
                "icon": "⚠️"
            }
        ]
        
        for tip in tips:
            st.markdown(f"""
                <div class="feature-card">
                    <h3>{tip['icon']} {tip['title']}</h3>
                    <p>{tip['content']}</p>
                </div>
            """, unsafe_allow_html=True) 