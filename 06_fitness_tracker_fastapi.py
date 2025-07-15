from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel, Field, Session, create_engine, select
from pydantic import BaseModel
import uvicorn
import os
from sqlalchemy import desc

# --- Multi-language support ---
LANGUAGES = {
    "English": {
        "title": "FastAPI Gym Tracker",
        "dashboard": "Dashboard",
        "gym_routine": "Gym Routine",
        "add_workout": "Add Workout",
        "workout_date": "Workout Date",
        "duration": "Duration (min)",
        "notes": "Notes",
        "actions": "Actions",
        "delete": "Delete",
        "no_workouts": "No workouts found",
        "olympic_lifts": "Olympic Lifts",
        "add_exercise": "Add Exercise",
        "exercise_name": "Exercise Name",
        "max_weight": "Max Weight (kg)",
        "run_date": "Run Date",
        "distance": "Distance (km)",
        "pace": "Pace (min/km)",
        "calories_burned": "Calories Burned",
        "track_date": "Date",
        "body_weight": "Body Weight (kg)",
        "save": "Save",
        "weight_progress": "Weight Progress",
        "food_log": "Food Log",
        "add_food": "Add Food",
        "protein": "Protein (g)",
        "carbs": "Carbs (g)",
        "fats": "Fats (g)",
        "settings": "Settings",
        "progress_chart": "Progress Chart",
        "light": "Light",
        "dark": "Dark",
        "theme": "Theme",
        "diet_program": "Diet Program",
        "running": "Running"
    },
    "Spanish": {
        "title": "Rastreador de Gimnasio FastAPI",
        "dashboard": "Panel Principal",
        "gym_routine": "Rutina de Gimnasio",
        "add_workout": "Agregar Entrenamiento",
        "workout_date": "Fecha de Entrenamiento",
        "duration": "Duración (min)",
        "notes": "Notas",
        "actions": "Acciones",
        "delete": "Eliminar",
        "no_workouts": "No se encontraron entrenamientos",
        "olympic_lifts": "Levantamientos Olímpicos",
        "add_exercise": "Agregar Ejercicio",
        "exercise_name": "Nombre del Ejercicio",
        "max_weight": "Peso Máximo (kg)",
        "run_date": "Fecha de Carrera",
        "distance": "Distancia (km)",
        "pace": "Ritmo (min/km)",
        "calories_burned": "Calorías Quemadas",
        "track_date": "Fecha",
        "body_weight": "Peso Corporal (kg)",
        "save": "Guardar",
        "weight_progress": "Progreso de Peso",
        "food_log": "Registro de Comidas",
        "add_food": "Agregar Comida",
        "protein": "Proteína (g)",
        "carbs": "Carbohidratos (g)",
        "fats": "Grasas (g)",
        "settings": "Configuración",
        "progress_chart": "Gráfico de Progreso",
        "light": "Claro",
        "dark": "Oscuro",
        "theme": "Tema",
        "diet_program": "Programa de Dieta",
        "running": "Correr"
    }
}

# --- Database Models ---
class GymWorkout(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: str
    duration: int
    notes: str

class OlympicLift(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: str
    exercise_name: str
    max_weight: float
    notes: str

class Run(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: str
    distance: float
    duration: int
    pace: float
    calories_burned: int
    notes: str

class WeightEntry(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: str
    weight: float

class DietEntry(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    date: str
    calories: int
    protein: float
    carbs: float
    fats: float
    food_log: str

# --- App Setup ---
app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "fastapi_gym_tracker.db")
engine = create_engine(f"sqlite:///{db_path}", echo=False)
SQLModel.metadata.create_all(engine)

# --- Templates and Static Files ---
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Dependency for DB Session ---
def get_session():
    with Session(engine) as session:
        yield session

# --- Helper for Language ---
def get_translation(lang, key):
    return LANGUAGES.get(lang, LANGUAGES["English"]).get(key, key)

def insert_sample_data():
    with Session(engine) as session:
        # Gym Workouts
        if session.exec(select(GymWorkout)).first() is None:
            session.add_all([
                GymWorkout(date="2024-06-01", duration=60, notes="Stronglifts 5x5 - Workout A"),
                GymWorkout(date="2024-06-03", duration=65, notes="Stronglifts 5x5 - Workout B"),
                GymWorkout(date="2024-06-05", duration=62, notes="Stronglifts 5x5 - Workout A"),
            ])
        # Olympic Lifts
        if session.exec(select(OlympicLift)).first() is None:
            session.add_all([
                OlympicLift(date="2024-06-02", exercise_name="Snatch", max_weight=70.0, notes="Good form"),
                OlympicLift(date="2024-06-04", exercise_name="Clean & Jerk", max_weight=90.0, notes="PR!"),
            ])
        # Running
        if session.exec(select(Run)).first() is None:
            session.add_all([
                Run(date="2024-06-01", distance=5.0, duration=30, pace=6.0, calories_burned=350, notes="Morning run"),
                Run(date="2024-06-03", distance=7.0, duration=42, pace=6.0, calories_burned=500, notes="Evening run"),
            ])
        # Weight Tracking
        if session.exec(select(WeightEntry)).first() is None:
            session.add_all([
                WeightEntry(date="2024-06-01", weight=75.0),
                WeightEntry(date="2024-06-03", weight=74.8),
                WeightEntry(date="2024-06-05", weight=74.5),
            ])
        # Diet Program
        if session.exec(select(DietEntry)).first() is None:
            session.add_all([
                DietEntry(date="2024-06-01", calories=2200, protein=150, carbs=250, fats=70, food_log="Chicken, rice, veggies"),
                DietEntry(date="2024-06-02", calories=2100, protein=140, carbs=230, fats=65, food_log="Fish, potatoes, salad"),
            ])
        session.commit()

insert_sample_data()

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, lang: str = "English", theme: str = "light", session: Session = Depends(get_session)):
    workouts = session.exec(select(GymWorkout).order_by(desc(GymWorkout.date))).all()
    return templates.TemplateResponse("dashboard_fastapi.html", {
        "request": request,
        "t": lambda k: get_translation(lang, k),
        "lang": lang,
        "theme": theme,
        "workouts": workouts
    })

@app.get("/gym", response_class=HTMLResponse)
def gym_routine(request: Request, lang: str = "English", theme: str = "light", session: Session = Depends(get_session)):
    workouts = session.exec(select(GymWorkout).order_by(desc(GymWorkout.date))).all()
    return templates.TemplateResponse("gym_routine_fastapi.html", {
        "request": request,
        "t": lambda k: get_translation(lang, k),
        "lang": lang,
        "theme": theme,
        "workouts": workouts
    })

@app.post("/gym/add")
def add_workout(date: str = Form(...), duration: int = Form(...), notes: str = Form(""), lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    workout = GymWorkout(date=date, duration=duration, notes=notes)
    session.add(workout)
    session.commit()
    return RedirectResponse(url=f"/gym?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/gym/delete/{workout_id}")
def delete_workout(workout_id: int, lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    workout = session.get(GymWorkout, workout_id)
    if workout:
        session.delete(workout)
        session.commit()
    return RedirectResponse(url=f"/gym?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

# --- Olympic Lifts ---
@app.get("/olympic", response_class=HTMLResponse)
def olympic_lifts(request: Request, lang: str = "English", theme: str = "light", session: Session = Depends(get_session)):
    lifts = session.exec(select(OlympicLift).order_by(desc(OlympicLift.date))).all()
    return templates.TemplateResponse("olympic_lifts_fastapi.html", {
        "request": request,
        "t": lambda k: get_translation(lang, k),
        "lang": lang,
        "theme": theme,
        "lifts": lifts
    })

@app.post("/olympic/add")
def add_olympic_lift(date: str = Form(...), exercise_name: str = Form(...), max_weight: float = Form(...), notes: str = Form(""), lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    lift = OlympicLift(date=date, exercise_name=exercise_name, max_weight=max_weight, notes=notes)
    session.add(lift)
    session.commit()
    return RedirectResponse(url=f"/olympic?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/olympic/delete/{lift_id}")
def delete_olympic_lift(lift_id: int, lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    lift = session.get(OlympicLift, lift_id)
    if lift:
        session.delete(lift)
        session.commit()
    return RedirectResponse(url=f"/olympic?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

# --- Running Logs ---
@app.get("/running", response_class=HTMLResponse)
def running_logs(request: Request, lang: str = "English", theme: str = "light", session: Session = Depends(get_session)):
    runs = session.exec(select(Run).order_by(desc(Run.date))).all()
    return templates.TemplateResponse("running_fastapi.html", {
        "request": request,
        "t": lambda k: get_translation(lang, k),
        "lang": lang,
        "theme": theme,
        "runs": runs
    })

@app.post("/running/add")
def add_run(date: str = Form(...), distance: float = Form(...), duration: int = Form(...), pace: float = Form(...), calories_burned: int = Form(...), notes: str = Form(""), lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    run = Run(date=date, distance=distance, duration=duration, pace=pace, calories_burned=calories_burned, notes=notes)
    session.add(run)
    session.commit()
    return RedirectResponse(url=f"/running?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/running/delete/{run_id}")
def delete_run(run_id: int, lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    run = session.get(Run, run_id)
    if run:
        session.delete(run)
        session.commit()
    return RedirectResponse(url=f"/running?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

# --- Weight Tracking ---
@app.get("/weight", response_class=HTMLResponse)
def weight_tracking(request: Request, lang: str = "English", theme: str = "light", session: Session = Depends(get_session)):
    weights = session.exec(select(WeightEntry).order_by(desc(WeightEntry.date))).all()
    return templates.TemplateResponse("weight_tracking_fastapi.html", {
        "request": request,
        "t": lambda k: get_translation(lang, k),
        "lang": lang,
        "theme": theme,
        "weights": weights
    })

@app.post("/weight/add")
def add_weight(date: str = Form(...), weight: float = Form(...), lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    entry = WeightEntry(date=date, weight=weight)
    session.add(entry)
    session.commit()
    return RedirectResponse(url=f"/weight?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/weight/delete/{weight_id}")
def delete_weight(weight_id: int, lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    entry = session.get(WeightEntry, weight_id)
    if entry:
        session.delete(entry)
        session.commit()
    return RedirectResponse(url=f"/weight?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

# --- Diet Program ---
@app.get("/diet", response_class=HTMLResponse)
def diet_program(request: Request, lang: str = "English", theme: str = "light", session: Session = Depends(get_session)):
    diets = session.exec(select(DietEntry).order_by(desc(DietEntry.date))).all()
    return templates.TemplateResponse("diet_program_fastapi.html", {
        "request": request,
        "t": lambda k: get_translation(lang, k),
        "lang": lang,
        "theme": theme,
        "diets": diets
    })

@app.post("/diet/add")
def add_diet(date: str = Form(...), calories: int = Form(...), protein: float = Form(...), carbs: float = Form(...), fats: float = Form(...), food_log: str = Form(""), lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    entry = DietEntry(date=date, calories=calories, protein=protein, carbs=carbs, fats=fats, food_log=food_log)
    session.add(entry)
    session.commit()
    return RedirectResponse(url=f"/diet?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/diet/delete/{diet_id}")
def delete_diet(diet_id: int, lang: str = Form("English"), theme: str = Form("light"), session: Session = Depends(get_session)):
    entry = session.get(DietEntry, diet_id)
    if entry:
        session.delete(entry)
        session.commit()
    return RedirectResponse(url=f"/diet?lang={lang}&theme={theme}", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/settings", response_class=HTMLResponse)
def settings(request: Request, lang: str = "English", theme: str = "light"):
    return templates.TemplateResponse("settings_fastapi.html", {
        "request": request,
        "t": lambda k: get_translation(lang, k),
        "lang": lang,
        "theme": theme
    })

if __name__ == "__main__":
    uvicorn.run("fitness_tracker_fastapi:app", host="127.0.0.1", port=8000, reload=True) 