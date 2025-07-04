import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import json

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Nutrition Tracker",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# INITIALIZE SESSION STATE
# =============================================================================
if 'food_log' not in st.session_state:
    st.session_state.food_log = []

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': '',
        'age': 25,
        'weight': 70,
        'height': 170,
        'gender': 'Male',
        'activity_level': 'Moderate',
        'goal': 'Maintain'
    }

if 'daily_goals' not in st.session_state:
    st.session_state.daily_goals = {
        'calories': 2000,
        'protein': 150,
        'carbs': 250,
        'fat': 65,
        'fiber': 25,
        'water': 8
    }

# =============================================================================
# FOOD DATABASE
# =============================================================================
FOOD_DATABASE = {
    # Fruits
    'Apple (medium)': {'calories': 95, 'protein': 0.5, 'carbs': 25, 'fat': 0.3, 'fiber': 4},
    'Banana (medium)': {'calories': 105, 'protein': 1.3, 'carbs': 27, 'fat': 0.4, 'fiber': 3},
    'Orange (medium)': {'calories': 80, 'protein': 2, 'carbs': 19, 'fat': 0.2, 'fiber': 3},
    'Avocado (half)': {'calories': 160, 'protein': 2, 'carbs': 9, 'fat': 15, 'fiber': 7},
    'Berries (1 cup)': {'calories': 85, 'protein': 1, 'carbs': 21, 'fat': 0.5, 'fiber': 8},
    
    # Vegetables
    'Broccoli (1 cup)': {'calories': 55, 'protein': 4, 'carbs': 11, 'fat': 0.6, 'fiber': 5},
    'Spinach (1 cup)': {'calories': 7, 'protein': 1, 'carbs': 1, 'fat': 0.1, 'fiber': 1},
    'Carrots (1 cup)': {'calories': 50, 'protein': 1, 'carbs': 12, 'fat': 0.3, 'fiber': 4},
    'Sweet Potato (medium)': {'calories': 115, 'protein': 2, 'carbs': 27, 'fat': 0.1, 'fiber': 4},
    
    # Proteins
    'Chicken Breast (100g)': {'calories': 165, 'protein': 31, 'carbs': 0, 'fat': 3.6, 'fiber': 0},
    'Salmon (100g)': {'calories': 208, 'protein': 20, 'carbs': 0, 'fat': 13, 'fiber': 0},
    'Eggs (2 large)': {'calories': 140, 'protein': 12, 'carbs': 1, 'fat': 10, 'fiber': 0},
    'Greek Yogurt (1 cup)': {'calories': 130, 'protein': 20, 'carbs': 9, 'fat': 0, 'fiber': 0},
    'Lentils (1 cup cooked)': {'calories': 230, 'protein': 18, 'carbs': 40, 'fat': 1, 'fiber': 16},
    'Tofu (100g)': {'calories': 76, 'protein': 8, 'carbs': 2, 'fat': 4.8, 'fiber': 1},
    
    # Grains & Carbs
    'Brown Rice (1 cup cooked)': {'calories': 220, 'protein': 5, 'carbs': 45, 'fat': 2, 'fiber': 4},
    'Quinoa (1 cup cooked)': {'calories': 220, 'protein': 8, 'carbs': 39, 'fat': 4, 'fiber': 5},
    'Oats (1 cup cooked)': {'calories': 150, 'protein': 5, 'carbs': 27, 'fat': 3, 'fiber': 4},
    'Whole Wheat Bread (2 slices)': {'calories': 160, 'protein': 8, 'carbs': 28, 'fat': 2, 'fiber': 6},
    
    # Nuts & Seeds
    'Almonds (28g/23 nuts)': {'calories': 160, 'protein': 6, 'carbs': 6, 'fat': 14, 'fiber': 3},
    'Walnuts (28g/14 halves)': {'calories': 185, 'protein': 4, 'carbs': 4, 'fat': 18, 'fiber': 2},
    'Chia Seeds (1 tbsp)': {'calories': 60, 'protein': 2, 'carbs': 5, 'fat': 4, 'fiber': 5},
    
    # Dairy
    'Milk (1 cup)': {'calories': 150, 'protein': 8, 'carbs': 12, 'fat': 8, 'fiber': 0},
    'Cheese (28g)': {'calories': 110, 'protein': 7, 'carbs': 1, 'fat': 9, 'fiber': 0},
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def calculate_bmr(weight, height, age, gender):
    """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
    if gender == 'Male':
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr

def calculate_tdee(bmr, activity_level):
    """Calculate Total Daily Energy Expenditure"""
    activity_multipliers = {
        'Sedentary': 1.2,
        'Light': 1.375,
        'Moderate': 1.55,
        'Active': 1.725,
        'Very Active': 1.9
    }
    return bmr * activity_multipliers[activity_level]

def adjust_calories_for_goal(tdee, goal):
    """Adjust calories based on goal"""
    if goal == 'Lose Weight':
        return tdee - 500  # 500 calorie deficit
    elif goal == 'Gain Weight':
        return tdee + 500  # 500 calorie surplus
    else:
        return tdee  # Maintain weight

def get_today_intake():
    """Get today's nutrition intake from food log"""
    today = date.today()
    today_log = [entry for entry in st.session_state.food_log if entry['date'] == today]
    
    total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
    for entry in today_log:
        for nutrient in total:
            total[nutrient] += entry.get(nutrient, 0)
    
    return total, today_log

def create_macro_pie_chart(protein, carbs, fat):
    """Create a pie chart for macronutrients"""
    protein_cals = protein * 4
    carbs_cals = carbs * 4
    fat_cals = fat * 9
    
    labels = ['Protein', 'Carbohydrates', 'Fat']
    values = [protein_cals, carbs_cals, fat_cals]
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        hole=0.4,
        marker=dict(colors=colors)
    )])
    
    fig.update_layout(
        title="Macronutrient Distribution (Calories)",
        showlegend=True,
        height=400
    )
    
    return fig

def create_progress_chart(current, goal, title):
    """Create a progress bar chart"""
    progress = min(current / goal * 100, 100)
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        delta = {'reference': goal},
        gauge = {
            'axis': {'range': [None, goal * 1.2]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, goal * 0.5], 'color': "lightgray"},
                {'range': [goal * 0.5, goal], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': goal
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
st.sidebar.title("🥗 Nutrition Tracker")
st.sidebar.write("Track your daily nutrition and reach your health goals!")

page = st.sidebar.selectbox(
    "Navigate to:",
    [
        "🏠 Dashboard",
        "👤 Profile Setup",
        "🍎 Add Food",
        "📊 Progress Analysis",
        "🥗 Meal Planner",
        "📱 Food Database"
    ]
)

# =============================================================================
# MAIN APP CONTENT
# =============================================================================

if page == "🏠 Dashboard":
    st.title("🏠 Nutrition Dashboard")
    
    # Calculate daily goals based on profile
    profile = st.session_state.user_profile
    bmr = calculate_bmr(profile['weight'], profile['height'], profile['age'], profile['gender'])
    tdee = calculate_tdee(bmr, profile['activity_level'])
    adjusted_calories = adjust_calories_for_goal(tdee, profile['goal'])
    
    # Update daily goals
    st.session_state.daily_goals['calories'] = int(adjusted_calories)
    
    # Get today's intake
    today_intake, today_log = get_today_intake()
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        calories_progress = today_intake['calories'] / st.session_state.daily_goals['calories'] * 100
        st.metric(
            "Calories",
            f"{today_intake['calories']:.0f}",
            f"{today_intake['calories'] - st.session_state.daily_goals['calories']:.0f}",
            delta_color="inverse"
        )
        st.progress(min(calories_progress / 100, 1.0))
        st.caption(f"Goal: {st.session_state.daily_goals['calories']}")
    
    with col2:
        protein_progress = today_intake['protein'] / st.session_state.daily_goals['protein'] * 100
        st.metric(
            "Protein (g)",
            f"{today_intake['protein']:.1f}",
            f"{today_intake['protein'] - st.session_state.daily_goals['protein']:.1f}",
            delta_color="inverse"
        )
        st.progress(min(protein_progress / 100, 1.0))
        st.caption(f"Goal: {st.session_state.daily_goals['protein']}g")
    
    with col3:
        carbs_progress = today_intake['carbs'] / st.session_state.daily_goals['carbs'] * 100
        st.metric(
            "Carbs (g)",
            f"{today_intake['carbs']:.1f}",
            f"{today_intake['carbs'] - st.session_state.daily_goals['carbs']:.1f}",
            delta_color="inverse"
        )
        st.progress(min(carbs_progress / 100, 1.0))
        st.caption(f"Goal: {st.session_state.daily_goals['carbs']}g")
    
    with col4:
        fat_progress = today_intake['fat'] / st.session_state.daily_goals['fat'] * 100
        st.metric(
            "Fat (g)",
            f"{today_intake['fat']:.1f}",
            f"{today_intake['fat'] - st.session_state.daily_goals['fat']:.1f}",
            delta_color="inverse"
        )
        st.progress(min(fat_progress / 100, 1.0))
        st.caption(f"Goal: {st.session_state.daily_goals['fat']}g")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        if today_intake['protein'] > 0 or today_intake['carbs'] > 0 or today_intake['fat'] > 0:
            st.plotly_chart(
                create_macro_pie_chart(today_intake['protein'], today_intake['carbs'], today_intake['fat']),
                use_container_width=True
            )
        else:
            st.info("Add some food to see your macronutrient distribution!")
    
    with col2:
        st.subheader("Today's Food Log")
        if today_log:
            for i, entry in enumerate(today_log):
                with st.expander(f"{entry['food']} - {entry['calories']:.0f} cal"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Protein:** {entry['protein']:.1f}g")
                        st.write(f"**Carbs:** {entry['carbs']:.1f}g")
                    with col_b:
                        st.write(f"**Fat:** {entry['fat']:.1f}g")
                        st.write(f"**Fiber:** {entry['fiber']:.1f}g")
                    
                    if st.button(f"Remove", key=f"remove_{i}"):
                        st.session_state.food_log.remove(entry)
                        st.rerun()
        else:
            st.info("No food logged today. Start by adding some meals!")

elif page == "👤 Profile Setup":
    st.title("👤 Profile Setup")
    st.write("Set up your profile to get personalized nutrition recommendations.")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", value=st.session_state.user_profile['name'])
            age = st.number_input("Age", min_value=10, max_value=100, value=st.session_state.user_profile['age'])
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=float(st.session_state.user_profile['weight']))
            height = st.number_input("Height (cm)", min_value=100, max_value=220, value=st.session_state.user_profile['height'])
        
        with col2:
            gender = st.selectbox("Gender", ["Male", "Female"], index=0 if st.session_state.user_profile['gender'] == 'Male' else 1)
            activity_level = st.selectbox(
                "Activity Level",
                ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
                index=["Sedentary", "Light", "Moderate", "Active", "Very Active"].index(st.session_state.user_profile['activity_level'])
            )
            goal = st.selectbox(
                "Goal",
                ["Lose Weight", "Maintain", "Gain Weight"],
                index=["Lose Weight", "Maintain", "Gain Weight"].index(st.session_state.user_profile['goal'])
            )
        
        submitted = st.form_submit_button("Save Profile")
        
        if submitted:
            st.session_state.user_profile = {
                'name': name,
                'age': age,
                'weight': weight,
                'height': height,
                'gender': gender,
                'activity_level': activity_level,
                'goal': goal
            }
            st.success("Profile updated successfully!")
    
    # Show calculated values
    if st.session_state.user_profile['name']:
        st.subheader("Your Calculated Nutrition Needs")
        profile = st.session_state.user_profile
        bmr = calculate_bmr(profile['weight'], profile['height'], profile['age'], profile['gender'])
        tdee = calculate_tdee(bmr, profile['activity_level'])
        adjusted_calories = adjust_calories_for_goal(tdee, profile['goal'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("BMR (Basal Metabolic Rate)", f"{bmr:.0f} cal/day")
        with col2:
            st.metric("TDEE (Total Daily Energy)", f"{tdee:.0f} cal/day")
        with col3:
            st.metric("Recommended Calories", f"{adjusted_calories:.0f} cal/day")
        
        st.info(f"Based on your profile, you should consume approximately **{adjusted_calories:.0f} calories** per day to {profile['goal'].lower()}.")

elif page == "🍎 Add Food":
    st.title("🍎 Add Food to Your Log")
    
    # Food search and selection
    search_term = st.text_input("Search for food:", placeholder="Type to search...")
    
    if search_term:
        filtered_foods = {k: v for k, v in FOOD_DATABASE.items() if search_term.lower() in k.lower()}
    else:
        filtered_foods = FOOD_DATABASE
    
    if filtered_foods:
        selected_food = st.selectbox("Select a food:", list(filtered_foods.keys()))
        
        # Show nutrition info
        food_info = filtered_foods[selected_food]
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Nutrition Information (per serving)")
            st.write(f"**Calories:** {food_info['calories']}")
            st.write(f"**Protein:** {food_info['protein']}g")
            st.write(f"**Carbohydrates:** {food_info['carbs']}g")
            st.write(f"**Fat:** {food_info['fat']}g")
            st.write(f"**Fiber:** {food_info['fiber']}g")
        
        with col2:
            st.subheader("Serving Size")
            multiplier = st.number_input("Number of servings:", min_value=0.1, max_value=10.0, value=1.0, step=0.1)
            
            # Calculate adjusted nutrition
            adjusted_nutrition = {k: v * multiplier for k, v in food_info.items()}
            
            st.write("**Adjusted Nutrition:**")
            for nutrient, value in adjusted_nutrition.items():
                if nutrient == 'calories':
                    st.write(f"**{nutrient.title()}:** {value:.0f}")
                else:
                    st.write(f"**{nutrient.title()}:** {value:.1f}g")
        
        # Add to log
        if st.button("Add to Today's Log", type="primary"):
            new_entry = {
                'date': date.today(),
                'food': f"{selected_food} (x{multiplier})",
                'calories': adjusted_nutrition['calories'],
                'protein': adjusted_nutrition['protein'],
                'carbs': adjusted_nutrition['carbs'],
                'fat': adjusted_nutrition['fat'],
                'fiber': adjusted_nutrition['fiber']
            }
            
            st.session_state.food_log.append(new_entry)
            st.success(f"Added {selected_food} to your food log!")
            st.balloons()
    
    # Custom food entry
    st.subheader("Add Custom Food")
    with st.expander("Enter nutrition information manually"):
        with st.form("custom_food_form"):
            food_name = st.text_input("Food name:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                calories = st.number_input("Calories:", min_value=0, value=0)
                protein = st.number_input("Protein (g):", min_value=0.0, value=0.0)
            with col2:
                carbs = st.number_input("Carbohydrates (g):", min_value=0.0, value=0.0)
                fat = st.number_input("Fat (g):", min_value=0.0, value=0.0)
            with col3:
                fiber = st.number_input("Fiber (g):", min_value=0.0, value=0.0)
            
            submitted = st.form_submit_button("Add Custom Food")
            
            if submitted and food_name:
                new_entry = {
                    'date': date.today(),
                    'food': food_name,
                    'calories': calories,
                    'protein': protein,
                    'carbs': carbs,
                    'fat': fat,
                    'fiber': fiber
                }
                
                st.session_state.food_log.append(new_entry)
                st.success(f"Added {food_name} to your food log!")

elif page == "📊 Progress Analysis":
    st.title("📊 Progress Analysis")
    
    if not st.session_state.food_log:
        st.info("Start logging food to see your progress analysis!")
    else:
        # Convert food log to DataFrame
        df = pd.DataFrame(st.session_state.food_log)
        
        # Date range selection
        min_date = df['date'].min()
        max_date = df['date'].max()
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From:", value=min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("To:", value=max_date, min_value=min_date, max_value=max_date)
        
        # Filter data
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        filtered_df = df.loc[mask]
        
        if not filtered_df.empty:
            # Daily totals
            daily_totals = filtered_df.groupby('date').agg({
                'calories': 'sum',
                'protein': 'sum',
                'carbs': 'sum',
                'fat': 'sum',
                'fiber': 'sum'
            }).reset_index()
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Calories over time
                fig_calories = px.line(
                    daily_totals, 
                    x='date', 
                    y='calories',
                    title="Daily Calories Over Time",
                    markers=True
                )
                fig_calories.add_hline(
                    y=st.session_state.daily_goals['calories'], 
                    line_dash="dash", 
                    line_color="red",
                    annotation_text="Goal"
                )
                st.plotly_chart(fig_calories, use_container_width=True)
            
            with col2:
                # Macronutrients over time
                fig_macros = go.Figure()
                fig_macros.add_trace(go.Scatter(x=daily_totals['date'], y=daily_totals['protein'], mode='lines+markers', name='Protein'))
                fig_macros.add_trace(go.Scatter(x=daily_totals['date'], y=daily_totals['carbs'], mode='lines+markers', name='Carbs'))
                fig_macros.add_trace(go.Scatter(x=daily_totals['date'], y=daily_totals['fat'], mode='lines+markers', name='Fat'))
                fig_macros.update_layout(title="Daily Macronutrients Over Time", xaxis_title="Date", yaxis_title="Grams")
                st.plotly_chart(fig_macros, use_container_width=True)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_calories = daily_totals['calories'].mean()
                st.metric("Average Daily Calories", f"{avg_calories:.0f}")
            
            with col2:
                avg_protein = daily_totals['protein'].mean()
                st.metric("Average Daily Protein", f"{avg_protein:.1f}g")
            
            with col3:
                avg_carbs = daily_totals['carbs'].mean()
                st.metric("Average Daily Carbs", f"{avg_carbs:.1f}g")
            
            with col4:
                avg_fat = daily_totals['fat'].mean()
                st.metric("Average Daily Fat", f"{avg_fat:.1f}g")
            
            # Goal achievement
            st.subheader("Goal Achievement")
            goals = st.session_state.daily_goals
            achievements = {
                'Calories': (daily_totals['calories'] >= goals['calories'] * 0.9) & (daily_totals['calories'] <= goals['calories'] * 1.1),
                'Protein': daily_totals['protein'] >= goals['protein'],
                'Carbs': daily_totals['carbs'] <= goals['carbs'] * 1.2,
                'Fat': daily_totals['fat'] <= goals['fat'] * 1.2
            }
            
            for goal_name, achievement in achievements.items():
                success_rate = (achievement.sum() / len(daily_totals)) * 100
                st.write(f"**{goal_name} Goal Achievement:** {success_rate:.1f}% of days")

elif page == "🥗 Meal Planner":
    st.title("🥗 Meal Planner")
    st.write("Plan your meals for the week!")
    
    # Meal suggestions based on goals
    st.subheader("Meal Suggestions")
    
    goal = st.session_state.user_profile['goal']
    
    if goal == "Lose Weight":
        st.info("💡 **Weight Loss Tips:** Focus on high-protein, high-fiber foods to stay full while maintaining a calorie deficit.")
        
        breakfast_suggestions = [
            "Greek yogurt with berries and chia seeds",
            "Oats with protein powder and fruit",
            "Eggs with spinach and whole wheat toast"
        ]
        lunch_suggestions = [
            "Chicken salad with mixed vegetables",
            "Lentil soup with side salad",
            "Quinoa bowl with roasted vegetables"
        ]
        dinner_suggestions = [
            "Grilled salmon with broccoli",
            "Chicken breast with sweet potato",
            "Tofu stir-fry with brown rice"
        ]
    
    elif goal == "Gain Weight":
        st.info("💡 **Weight Gain Tips:** Include calorie-dense, nutrient-rich foods like nuts, healthy fats, and protein.")
        
        breakfast_suggestions = [
            "Oats with nuts, seeds, and banana",
            "Eggs with avocado toast",
            "Protein smoothie with fruit and nut butter"
        ]
        lunch_suggestions = [
            "Quinoa bowl with chicken and nuts",
            "Salmon with brown rice and vegetables",
            "Lentil curry with whole wheat bread"
        ]
        dinner_suggestions = [
            "Chicken with quinoa and roasted vegetables",
            "Salmon with sweet potato and greens",
            "Tofu with brown rice and stir-fried vegetables"
        ]
    
    else:  # Maintain
        st.info("💡 **Maintenance Tips:** Focus on balanced meals with a good mix of protein, carbs, and healthy fats.")
        
        breakfast_suggestions = [
            "Balanced smoothie with protein, fruit, and oats",
            "Eggs with whole grain toast and fruit",
            "Greek yogurt parfait with granola"
        ]
        lunch_suggestions = [
            "Balanced bowl with protein, grains, and vegetables",
            "Sandwich with lean protein and side salad",
            "Soup with whole grain bread"
        ]
        dinner_suggestions = [
            "Grilled protein with vegetables and grains",
            "Stir-fry with lean protein and brown rice",
            "Baked fish with roasted vegetables"
        ]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🌅 Breakfast Ideas")
        for suggestion in breakfast_suggestions:
            st.write(f"• {suggestion}")
    
    with col2:
        st.subheader("🌞 Lunch Ideas")
        for suggestion in lunch_suggestions:
            st.write(f"• {suggestion}")
    
    with col3:
        st.subheader("🌙 Dinner Ideas")
        for suggestion in dinner_suggestions:
            st.write(f"• {suggestion}")
    
    # Quick meal builder
    st.subheader("Quick Meal Builder")
    st.write("Build a balanced meal by selecting components:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        protein_options = [food for food in FOOD_DATABASE.keys() if any(keyword in food.lower() for keyword in ['chicken', 'salmon', 'eggs', 'yogurt', 'lentils', 'tofu'])]
        selected_protein = st.selectbox("Choose a protein:", protein_options)
    
    with col2:
        carb_options = [food for food in FOOD_DATABASE.keys() if any(keyword in food.lower() for keyword in ['rice', 'quinoa', 'oats', 'bread'])]
        selected_carb = st.selectbox("Choose a carb:", carb_options)
    
    with col3:
        veggie_options = [food for food in FOOD_DATABASE.keys() if any(keyword in food.lower() for keyword in ['broccoli', 'spinach', 'carrots', 'sweet potato'])]
        selected_veggie = st.selectbox("Choose vegetables:", veggie_options)
    
    if st.button("Calculate Meal Nutrition"):
        total_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
        
        for food in [selected_protein, selected_carb, selected_veggie]:
            food_data = FOOD_DATABASE[food]
            for nutrient in total_nutrition:
                total_nutrition[nutrient] += food_data[nutrient]
        
        st.subheader("Meal Nutrition Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Calories", f"{total_nutrition['calories']:.0f}")
        with col2:
            st.metric("Protein", f"{total_nutrition['protein']:.1f}g")
        with col3:
            st.metric("Carbs", f"{total_nutrition['carbs']:.1f}g")
        with col4:
            st.metric("Fat", f"{total_nutrition['fat']:.1f}g")
        with col5:
            st.metric("Fiber", f"{total_nutrition['fiber']:.1f}g")

elif page == "📱 Food Database":
    st.title("📱 Food Database")
    st.write("Browse the complete food database with nutrition information.")
    
    # Search functionality
    search = st.text_input("Search foods:", placeholder="Search by name...")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        min_protein = st.slider("Minimum protein (g):", 0, 50, 0)
    with col2:
        max_calories = st.slider("Maximum calories:", 0, 500, 500)
    
    # Create DataFrame from food database
    foods_data = []
    for food_name, nutrition in FOOD_DATABASE.items():
        if search.lower() in food_name.lower() or not search:
            if nutrition['protein'] >= min_protein and nutrition['calories'] <= max_calories:
                foods_data.append({
                    'Food': food_name,
                    'Calories': nutrition['calories'],
                    'Protein (g)': nutrition['protein'],
                    'Carbs (g)': nutrition['carbs'],
                    'Fat (g)': nutrition['fat'],
                    'Fiber (g)': nutrition['fiber']
                })
    
    if foods_data:
        df = pd.DataFrame(foods_data)
        
        # Sort options
        sort_by = st.selectbox("Sort by:", ['Food', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)', 'Fiber (g)'])
        ascending = st.checkbox("Ascending order", value=True)
        
        df_sorted = df.sort_values(by=sort_by, ascending=ascending)
        
        # Display the data
        st.dataframe(df_sorted, use_container_width=True, height=400)
        
        # Quick stats
        st.subheader("Database Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Foods", len(df_sorted))
        with col2:
            st.metric("Avg Calories", f"{df_sorted['Calories'].mean():.0f}")
        with col3:
            st.metric("Highest Protein", f"{df_sorted['Protein (g)'].max():.1f}g")
        with col4:
            st.metric("Highest Fiber", f"{df_sorted['Fiber (g)'].max():.1f}g")
    
    else:
        st.info("No foods match your search criteria. Try adjusting your filters.")

# =============================================================================
# FOOTER
# =============================================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
today_intake, _ = get_today_intake()
st.sidebar.metric("Today's Calories", f"{today_intake['calories']:.0f}")
st.sidebar.metric("Foods Logged", len([entry for entry in st.session_state.food_log if entry['date'] == date.today()]))

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    Made with ❤️ using Streamlit<br>
    🥗 Nutrition Tracker v1.0
</div>
""", unsafe_allow_html=True)