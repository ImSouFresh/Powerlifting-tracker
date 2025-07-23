import streamlit as st
import datetime
import json
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
import numpy as np

# Configuration de la page pour mobile
st.set_page_config(
    page_title="💪 Powerlifting Pro",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS pour mobile et design moderne
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #ff6b6b;
        font-size: 2.5rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .page-header {
        text-align: center;
        color: #2c3e50;
        font-size: 2rem;
        margin-bottom: 1.5rem;
        border-bottom: 3px solid #ff6b6b;
        padding-bottom: 0.5rem;
    }
    .workout-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #ff6b6b;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stats-card {
        background: linear-gradient(135deg, #e8f4fd 0%, #d1ecf1 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #3498db;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .profile-card {
        background: linear-gradient(135deg, #f0f8e8 0%, #e8f5e8 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #28a745;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .exercise-name {
        font-weight: bold;
        font-size: 1.3rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .exercise-details {
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        margin: 0.2rem 0;
        border-radius: 10px;
        font-weight: bold;
    }
    .nav-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        margin: 0.5rem;
        cursor: pointer;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class Exercise:
    name: str
    sets: int
    reps: str
    weight: float
    notes: str = ""
    completed_sets: int = 0
    failed_sets: int = 0
    status: str = "pending"
    actual_sets: List[Dict] = None  # Pour tracking série par série

    def __post_init__(self):
        if self.actual_sets is None:
            self.actual_sets = []

@dataclass
class WorkoutSession:
    date: str
    workout_name: str
    week: int
    exercises: List[Exercise]
    completed: bool = False
    duration_minutes: int = 0
    notes: str = ""

@dataclass
class UserProfile:
    name: str = ""
    age: int = 25
    weight: float = 70.0
    height: int = 175
    experience_years: int = 1
    goals: Dict = None
    measurements: List[Dict] = None

    def __post_init__(self):
        if self.goals is None:
            self.goals = {
                "bench_1rm": 100.0,
                "squat_1rm": 120.0,
                "deadlift_1rm": 140.0
            }
        if self.measurements is None:
            self.measurements = []

class PowerliftingTracker:
    def __init__(self):
        self.data_file = "workout_data.json"
        self.profile_file = "user_profile.json"
        self.load_data()
        self.load_profile()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.start_date = datetime.datetime.strptime(data.get('start_date', str(datetime.date.today())), '%Y-%m-%d').date()
                    self.sessions = data.get('sessions', [])
            except:
                self.start_date = datetime.date.today()
                self.sessions = []
        else:
            self.start_date = datetime.date.today()
            self.sessions = []

    def load_profile(self):
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, 'r') as f:
                    data = json.load(f)
                    self.profile = UserProfile(**data)
            except:
                self.profile = UserProfile()
        else:
            self.profile = UserProfile()

    def save_data(self):
        data = {
            'start_date': str(self.start_date),
            'sessions': self.sessions
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def save_profile(self):
        with open(self.profile_file, 'w') as f:
            json.dump(asdict(self.profile), f, indent=2)

    def get_current_week(self) -> int:
        today = datetime.date.today()
        days_elapsed = (today - self.start_date).days
        week = (days_elapsed // 7) + 1
        return min(max(week, 1), 8)

    def calculate_1rm(self, weight: float, reps: int) -> float:
        """Calcule le 1RM avec la formule d'Epley"""
        if reps == 1:
            return weight
        return weight * (1 + reps / 30.0)

    def get_exercise_progression(self, exercise_name: str) -> List[Dict]:
        """Récupère la progression d'un exercice"""
        progression = []
        for session in self.sessions:
            for ex in session.get('exercises', []):
                if ex['name'] == exercise_name and ex['status'] == 'completed':
                    progression.append({
                        'date': session['date'],
                        'weight': ex['weight'],
                        'sets': ex['sets'],
                        'reps': ex['reps'],
                        'estimated_1rm': self.calculate_1rm(ex['weight'], int(ex['reps'].split('-')[0]) if '-' in ex['reps'] else int(ex['reps']))
                    })
        return progression

    def get_program_data(self):
        return {
            "SÉANCE A - LUNDI": {
                "semaine_1-2": [
                    Exercise("Bench Press", 5, "3", 85.0),
                    Exercise("Squat", 4, "5", 65.0),
                    Exercise("Bench Press Pause", 3, "3", 80.0),
                    Exercise("Front Squat", 3, "8", 50.0),
                    Exercise("Dips", 3, "8-12", 0.0, "poids du corps"),
                    Exercise("Bulgarian Split Squats", 3, "10", 15.0)
                ],
                "semaine_3-4": [
                    Exercise("Bench Press", 5, "3", 87.5),
                    Exercise("Squat", 4, "5", 67.5),
                    Exercise("Bench Press Pause", 3, "3", 82.5),
                    Exercise("Front Squat", 3, "8", 52.5),
                    Exercise("Dips", 3, "10-12", 0.0, "poids du corps"),
                    Exercise("Bulgarian Split Squats", 3, "10", 17.5)
                ],
                "semaine_5-6": [
                    Exercise("Bench Press", 5, "3", 90.0),
                    Exercise("Squat", 4, "5", 70.0),
                    Exercise("Bench Press Pause", 3, "3", 85.0),
                    Exercise("Front Squat", 3, "8", 55.0),
                    Exercise("Dips", 3, "12-15", 0.0, "poids du corps"),
                    Exercise("Bulgarian Split Squats", 3, "10", 20.0)
                ],
                "semaine_7-8": [
                    Exercise("Bench Press", 5, "2-3", 92.5),
                    Exercise("Squat", 4, "5", 72.5),
                    Exercise("Bench Press Pause", 3, "2", 87.5),
                    Exercise("Front Squat", 3, "6", 57.5),
                    Exercise("Dips", 3, "15", 0.0, "poids du corps"),
                    Exercise("Bulgarian Split Squats", 3, "8", 22.5)
                ]
            },
            "SÉANCE B - MARDI": {
                "semaine_1-2": [
                    Exercise("Deadlift", 5, "2", 125.0),
                    Exercise("Deficit Deadlift", 3, "3", 100.0),
                    Exercise("Romanian Deadlift", 4, "6", 85.0),
                    Exercise("Barbell Rows", 4, "8", 70.0),
                    Exercise("Good Mornings", 3, "10", 40.0),
                    Exercise("Plank", 3, "45 sec", 0.0)
                ],
                "semaine_3-4": [
                    Exercise("Deadlift", 5, "1-2", 130.0),
                    Exercise("Deficit Deadlift", 3, "3", 102.5),
                    Exercise("Romanian Deadlift", 4, "6", 87.5),
                    Exercise("Barbell Rows", 4, "8", 72.5),
                    Exercise("Good Mornings", 3, "10", 42.5),
                    Exercise("Plank", 3, "50 sec", 0.0)
                ],
                "semaine_5-6": [
                    Exercise("Deadlift", 5, "1", 135.0),
                    Exercise("Deficit Deadlift", 3, "3", 105.0),
                    Exercise("Romanian Deadlift", 4, "6", 90.0),
                    Exercise("Barbell Rows", 4, "8", 75.0),
                    Exercise("Good Mornings", 3, "10", 45.0),
                    Exercise("Plank", 3, "60 sec", 0.0)
                ],
                "semaine_7-8": [
                    Exercise("Deadlift", 1, "1RM", 140.0, "vise 140kg"),
                    Exercise("Romanian Deadlift", 3, "6", 92.5),
                    Exercise("Barbell Rows", 4, "6", 77.5),
                    Exercise("Good Mornings", 3, "8", 47.5)
                ]
            },
            "SÉANCE C - JEUDI": {
                "semaine_1-2": [
                    Exercise("Squat", 5, "2", 85.0),
                    Exercise("Pause Squat", 3, "3", 70.0),
                    Exercise("Box Squat", 4, "5", 65.0),
                    Exercise("Walking Lunges", 3, "12", 15.0),
                    Exercise("Leg Curls", 3, "12", 0.0, "machine"),
                    Exercise("Calf Raises", 4, "15", 0.0)
                ],
                "semaine_3-4": [
                    Exercise("Squat", 5, "1-2", 87.5),
                    Exercise("Pause Squat", 3, "3", 72.5),
                    Exercise("Box Squat", 4, "5", 67.5),
                    Exercise("Walking Lunges", 3, "12", 17.5),
                    Exercise("Leg Curls", 3, "12", 0.0, "machine"),
                    Exercise("Calf Raises", 4, "15", 0.0)
                ],
                "semaine_5-6": [
                    Exercise("Squat", 5, "1", 90.0),
                    Exercise("Pause Squat", 3, "3", 75.0),
                    Exercise("Box Squat", 4, "5", 70.0),
                    Exercise("Walking Lunges", 3, "12", 20.0),
                    Exercise("Leg Curls", 3, "12", 0.0, "machine"),
                    Exercise("Calf Raises", 4, "15", 0.0)
                ],
                "semaine_7-8": [
                    Exercise("Squat", 1, "1RM", 95.0, "vise 95kg"),
                    Exercise("Pause Squat", 3, "2", 77.5),
                    Exercise("Box Squat", 3, "5", 72.5),
                    Exercise("Walking Lunges", 3, "10", 22.5)
                ]
            },
            "SÉANCE D - VENDREDI": {
                "semaine_1-2": [
                    Exercise("Bench Press", 5, "2", 92.0),
                    Exercise("Deadlift", 4, "3", 105.0),
                    Exercise("Close Grip Bench", 4, "6", 75.0),
                    Exercise("Sumo Deadlift", 3, "5", 90.0),
                    Exercise("Incline DB Press", 3, "8", 30.0),
                    Exercise("Face Pulls", 3, "15", 0.0, "câble")
                ],
                "semaine_3-4": [
                    Exercise("Bench Press", 5, "1-2", 95.0),
                    Exercise("Deadlift", 4, "3", 110.0),
                    Exercise("Close Grip Bench", 4, "6", 77.5),
                    Exercise("Sumo Deadlift", 3, "5", 92.5),
                    Exercise("Incline DB Press", 3, "8", 32.5),
                    Exercise("Face Pulls", 3, "15", 0.0, "câble")
                ],
                "semaine_5-6": [
                    Exercise("Bench Press", 5, "1", 97.5),
                    Exercise("Deadlift", 4, "3", 112.5),
                    Exercise("Close Grip Bench", 4, "6", 80.0),
                    Exercise("Sumo Deadlift", 3, "5", 95.0),
                    Exercise("Incline DB Press", 3, "8", 35.0),
                    Exercise("Face Pulls", 3, "15", 0.0, "câble")
                ],
                "semaine_7-8": [
                    Exercise("Bench Press", 1, "1RM", 102.5, "vise 102.5kg"),
                    Exercise("Deadlift", 3, "3", 115.0),
                    Exercise("Close Grip Bench", 3, "6", 82.5),
                    Exercise("Incline DB Press", 3, "6", 37.5)
                ]
            }
        }

    def get_workout_by_day(self, target_date):
        """Retourne l'entraînement pour une date donnée"""
        day_of_week = target_date.weekday()

        workout_schedule = {
            0: "SÉANCE A - LUNDI",
            1: "SÉANCE B - MARDI", 
            3: "SÉANCE C - JEUDI",
            4: "SÉANCE D - VENDREDI"
        }

        if day_of_week not in workout_schedule:
            return None, [], 0

        workout_name = workout_schedule[day_of_week]

        # Calcul de la semaine pour cette date
        days_elapsed = (target_date - self.start_date).days
        week = (days_elapsed // 7) + 1
        week = min(max(week, 1), 8)

        if week <= 2:
            phase = "semaine_1-2"
        elif week <= 4:
            phase = "semaine_3-4"
        elif week <= 6:
            phase = "semaine_5-6"
        else:
            phase = "semaine_7-8"

        program_data = self.get_program_data()
        exercises = program_data[workout_name][phase]

        return workout_name, exercises, week

    def get_today_workout(self):
        today = datetime.date.today()
        return self.get_workout_by_day(today)

    def get_next_workouts(self, days_ahead=7):
        """Retourne les prochains entraînements"""
        today = datetime.date.today()
        next_workouts = []

        for i in range(1, days_ahead + 1):
            future_date = today + datetime.timedelta(days=i)
            workout_name, exercises, week = self.get_workout_by_day(future_date)

            if workout_name:  # Si c'est un jour d'entraînement
                next_workouts.append({
                    'date': future_date,
                    'day_name': future_date.strftime("%A"),
                    'workout_name': workout_name,
                    'exercises': exercises,
                    'week': week
                })

        return next_workouts

# Initialisation
if 'tracker' not in st.session_state:
    st.session_state.tracker = PowerliftingTracker()
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Accueil"

tracker = st.session_state.tracker

# Navigation
st.markdown('<h1 class="main-header">💪 Powerlifting Pro</h1>', unsafe_allow_html=True)

# Menu de navigation
col1, col2, col3, col4, col5 = st.columns(5)
pages = ["🏠 Accueil", "🏋️ Entraînement", "📊 Statistiques", "👤 Profil", "⚙️ Paramètres"]

for i, (col, page) in enumerate(zip([col1, col2, col3, col4, col5], pages)):
    with col:
        if st.button(page, key=f"nav_{i}", help=f"Aller à {page}"):
            st.session_state.current_page = page
            st.rerun()

# Indicateur de page active
st.markdown(f"---")
st.markdown(f'<h2 class="page-header">{st.session_state.current_page}</h2>', unsafe_allow_html=True)

# ==================== PAGE ACCUEIL ====================
if st.session_state.current_page == "🏠 Accueil":

    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📅 Semaine", f"{tracker.get_current_week()}/8")
    with col2:
        st.metric("📍 Aujourd'hui", datetime.date.today().strftime("%A"))
    with col3:
        days_left = 56 - (datetime.date.today() - tracker.start_date).days
        st.metric("⏳ Jours restants", max(0, days_left))
    with col4:
        completed_sessions = len([s for s in tracker.sessions if s.get('completed', False)])
        st.metric("✅ Séances faites", completed_sessions)

    # Entraînement du jour
    workout_name, exercises, week = tracker.get_today_workout()

    if workout_name:
        st.markdown(f'<div class="workout-card">', unsafe_allow_html=True)
        st.markdown(f"### 🏋️ {workout_name}")
        st.markdown(f"**Semaine {week}/8**")

        # Aperçu des exercices principaux
        for ex in exercises[:3]:
            weight_str = f" @ {ex.weight}kg" if ex.weight > 0 else ""
            notes_str = f" ({ex.notes})" if ex.notes else ""
            st.markdown(f"• **{ex.name}**: {ex.sets}×{ex.reps}{weight_str}{notes_str}")

        if len(exercises) > 3:
            st.markdown(f"• ... et {len(exercises) - 3} autres exercices")

        if st.button("🚀 Commencer l'entraînement", type="primary"):
            st.session_state.current_page = "🏋️ Entraînement"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="workout-card">', unsafe_allow_html=True)
        st.markdown("### 🛌 Jour de repos")
        st.info("Récupération active recommandée - Étirements, marche, mobilité")
        st.markdown('</div>', unsafe_allow_html=True)

    # Prochains entraînements
    st.markdown("### 📅 Prochains entraînements")
    next_workouts = tracker.get_next_workouts(7)

    if next_workouts:
        for workout in next_workouts[:2]:
            st.markdown(f'<div class="stats-card">', unsafe_allow_html=True)
            st.markdown(f"**{workout['day_name']} {workout['date'].strftime('%d/%m')} - {workout['workout_name']}**")
            st.markdown(f"*Semaine {workout['week']}/8*")

            for ex in workout['exercises'][:2]:
                weight_str = f" @ {ex.weight}kg" if ex.weight > 0 else ""
                st.markdown(f"• {ex.name}: {ex.sets}×{ex.reps}{weight_str}")

            st.markdown('</div>', unsafe_allow_html=True)

# ==================== PAGE ENTRAÎNEMENT ====================
elif st.session_state.current_page == "🏋️ Entraînement":

    workout_name, exercises, week = tracker.get_today_workout()

    if workout_name:
        st.markdown(f"### 🏋️ {workout_name}")
        st.markdown(f"**Semaine {week}/8**")

        # Timer d'entraînement
        if 'workout_start_time' not in st.session_state:
            st.session_state.workout_start_time = datetime.datetime.now()

        elapsed = datetime.datetime.now() - st.session_state.workout_start_time
        st.metric("⏱️ Temps écoulé", f"{elapsed.seconds // 60}min {elapsed.seconds % 60}s")

        # Initialisation de la session d'entraînement
        if 'current_workout' not in st.session_state:
            st.session_state.current_workout = exercises

        # Affichage des exercices avec tracking avancé
        for i, exercise in enumerate(st.session_state.current_workout):
            with st.container():
                st.markdown(f'<div class="workout-card">', unsafe_allow_html=True)

                # Nom et détails de l'exercice
                weight_str = f"{exercise.weight}kg" if exercise.weight > 0 else ""
                notes_str = f" ({exercise.notes})" if exercise.notes else ""

                st.markdown(f'<div class="exercise-name">{exercise.name}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="exercise-details">{exercise.sets} sets × {exercise.reps} reps {weight_str}{notes_str}</div>', unsafe_allow_html=True)

                # Tracking série par série
                st.markdown("**Tracking des séries:**")

                # Initialisation du tracking des séries
                if f'series_tracking_{i}' not in st.session_state:
                    st.session_state[f'series_tracking_{i}'] = [{"reps": 0, "weight": exercise.weight, "completed": False} for _ in range(exercise.sets)]

                series_data = st.session_state[f'series_tracking_{i}']

                # Affichage des séries
                for j in range(exercise.sets):
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

                    with col1:
                        st.write(f"**Série {j+1}:**")

                    with col2:
                        reps_done = st.number_input(
                            f"Reps", 
                            min_value=0, 
                            max_value=20, 
                            value=series_data[j]["reps"],
                            key=f"reps_{i}_{j}"
                        )
                        series_data[j]["reps"] = reps_done

                    with col3:
                        weight_used = st.number_input(
                            f"Poids (kg)", 
                            min_value=0.0, 
                            max_value=300.0, 
                            value=series_data[j]["weight"],
                            step=2.5,
                            key=f"weight_{i}_{j}"
                        )
                        series_data[j]["weight"] = weight_used

                    with col4:
                        if st.button(f"✅" if series_data[j]["completed"] else "⏳", key=f"complete_{i}_{j}"):
                            series_data[j]["completed"] = not series_data[j]["completed"]
                            st.rerun()

                # Résumé de l'exercice
                completed_series = sum(1 for s in series_data if s["completed"])
                st.progress(completed_series / exercise.sets)
                st.write(f"Séries complétées: {completed_series}/{exercise.sets}")

                # Boutons d'action rapide
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Tout réussi", key=f"all_success_{i}"):
                        for s in series_data:
                            s["completed"] = True
                        st.session_state.current_workout[i].status = "completed"
                        st.rerun()

                with col2:
                    if st.button(f"❌ Échec (-5kg)", key=f"fail_{i}"):
                        st.session_state.current_workout[i].status = "failed"
                        if exercise.weight > 0:
                            new_weight = max(0, exercise.weight - 5)
                            st.session_state.current_workout[i].weight = new_weight
                            for s in series_data:
                                s["weight"] = new_weight
                        st.warning(f"Poids ajusté: {st.session_state.current_workout[i].weight}kg (-5kg)")
                        st.rerun()

                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("---")

        # Bouton de fin d'entraînement
        if st.button("🏁 Terminer l'entraînement", type="primary"):
            # Calcul de la durée
            duration = (datetime.datetime.now() - st.session_state.workout_start_time).seconds // 60

            # Sauvegarde avec données détaillées
            detailed_exercises = []
            for i, ex in enumerate(st.session_state.current_workout):
                series_data = st.session_state.get(f'series_tracking_{i}', [])
                ex_dict = asdict(ex)
                ex_dict['actual_sets'] = series_data
                detailed_exercises.append(ex_dict)

            session = WorkoutSession(
                date=str(datetime.date.today()),
                workout_name=workout_name,
                week=week,
                exercises=detailed_exercises,
                completed=True,
                duration_minutes=duration
            )

            tracker.sessions.append(asdict(session))
            tracker.save_data()

            st.success(f"🎉 Entraînement terminé en {duration} minutes!")
            st.balloons()

            # Nettoyage des variables de session
            keys_to_remove = [key for key in st.session_state.keys() if key.startswith(('current_workout', 'series_tracking_', 'workout_start_time'))]
            for key in keys_to_remove:
                del st.session_state[key]

            st.session_state.current_page = "🏠 Accueil"
            st.rerun()

    else:
        st.info("🛌 Jour de repos - Pas d'entraînement prévu aujourd'hui")
        if st.button("🏠 Retour à l'accueil"):
            st.session_state.current_page = "🏠 Accueil"
            st.rerun()

# ==================== PAGE STATISTIQUES ====================
elif st.session_state.current_page == "📊 Statistiques":

    if not tracker.sessions:
        st.info("📈 Aucune donnée disponible. Complétez quelques entraînements pour voir vos statistiques !")
    else:
        # Statistiques générales
        st.markdown("### 📈 Vue d'ensemble")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_sessions = len(tracker.sessions)
            st.metric("🏋️ Séances totales", total_sessions)

        with col2:
            total_duration = sum(s.get('duration_minutes', 0) for s in tracker.sessions)
            st.metric("⏱️ Temps total", f"{total_duration}min")

        with col3:
            avg_duration = total_duration / total_sessions if total_sessions > 0 else 0
            st.metric("📊 Durée moyenne", f"{avg_duration:.0f}min")

        with col4:
            # Calcul du taux de réussite
            total_exercises = sum(len(s.get('exercises', [])) for s in tracker.sessions)
            completed_exercises = sum(sum(1 for ex in s.get('exercises', []) if ex.get('status') == 'completed') for s in tracker.sessions)
            success_rate = (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
            st.metric("✅ Taux de réussite", f"{success_rate:.1f}%")

        # Graphiques de progression
        st.markdown("### 📊 Progression par exercice")

        # Sélection d'exercice
        all_exercises = set()
        for session in tracker.sessions:
            for ex in session.get('exercises', []):
                all_exercises.add(ex['name'])

        if all_exercises:
            selected_exercise = st.selectbox("Choisir un exercice:", sorted(all_exercises))

            # Données de progression
            progression_data = tracker.get_exercise_progression(selected_exercise)

            if progression_data:
                df = pd.DataFrame(progression_data)
                df['date'] = pd.to_datetime(df['date'])

                # Graphique de progression du poids
                fig_weight = px.line(df, x='date', y='weight', 
                                   title=f'Progression du poids - {selected_exercise}',
                                   labels={'weight': 'Poids (kg)', 'date': 'Date'})
                fig_weight.update_traces(line_color='#ff6b6b', line_width=3)
                st.plotly_chart(fig_weight, use_container_width=True)

                # Graphique du 1RM estimé
                fig_1rm = px.line(df, x='date', y='estimated_1rm',
                                title=f'1RM estimé - {selected_exercise}',
                                labels={'estimated_1rm': '1RM estimé (kg)', 'date': 'Date'})
                fig_1rm.update_traces(line_color='#3498db', line_width=3)
                st.plotly_chart(fig_1rm, use_container_width=True)

                # Tableau des records
                st.markdown("### 🏆 Records personnels")

                col1, col2, col3 = st.columns(3)
                with col1:
                    max_weight = df['weight'].max()
                    st.metric("💪 Poids max", f"{max_weight}kg")

                with col2:
                    max_1rm = df['estimated_1rm'].max()
                    st.metric("🎯 1RM estimé max", f"{max_1rm:.1f}kg")

                with col3:
                    last_1rm = df['estimated_1rm'].iloc[-1] if len(df) > 0 else 0
                    st.metric("📊 1RM actuel", f"{last_1rm:.1f}kg")

        # Heatmap des entraînements
        st.markdown("### 🗓️ Calendrier des entraînements")

        # Création des données pour la heatmap
        session_dates = [datetime.datetime.strptime(s['date'], '%Y-%m-%d').date() for s in tracker.sessions]

        if session_dates:
            # Graphique de fréquence
            df_sessions = pd.DataFrame({'date': session_dates, 'count': 1})
            df_sessions['date'] = pd.to_datetime(df_sessions['date'])
            df_sessions = df_sessions.groupby('date').sum().reset_index()

            fig_freq = px.bar(df_sessions, x='date', y='count',
                            title='Fréquence des entraînements',
                            labels={'count': 'Nombre de séances', 'date': 'Date'})
            fig_freq.update_traces(marker_color='#28a745')
            st.plotly_chart(fig_freq, use_container_width=True)

# ==================== PAGE PROFIL ====================
elif st.session_state.current_page == "👤 Profil":

    st.markdown("### 👤 Informations personnelles")

    # Formulaire de profil
    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Nom", value=tracker.profile.name)
            age = st.number_input("Âge", min_value=15, max_value=80, value=tracker.profile.age)
            weight = st.number_input("Poids (kg)", min_value=40.0, max_value=200.0, value=tracker.profile.weight, step=0.5)

        with col2:
            height = st.number_input("Taille (cm)", min_value=140, max_value=220, value=tracker.profile.height)
            experience = st.number_input("Expérience (années)", min_value=0, max_value=50, value=tracker.profile.experience_years)

        st.markdown("### 🎯 Objectifs de force")

        col1, col2, col3 = st.columns(3)
        with col1:
            bench_goal = st.number_input("Bench Press 1RM (kg)", min_value=20.0, max_value=300.0, 
                                       value=tracker.profile.goals.get("bench_1rm", 100.0), step=2.5)
        with col2:
            squat_goal = st.number_input("Squat 1RM (kg)", min_value=30.0, max_value=400.0,
                                       value=tracker.profile.goals.get("squat_1rm", 120.0), step=2.5)
        with col3:
            deadlift_goal = st.number_input("Deadlift 1RM (kg)", min_value=40.0, max_value=500.0,
                                          value=tracker.profile.goals.get("deadlift_1rm", 140.0), step=2.5)

        if st.form_submit_button("💾 Sauvegarder le profil", type="primary"):
            tracker.profile.name = name
            tracker.profile.age = age
            tracker.profile.weight = weight
            tracker.profile.height = height
            tracker.profile.experience_years = experience
            tracker.profile.goals = {
                "bench_1rm": bench_goal,
                "squat_1rm": squat_goal,
                "deadlift_1rm": deadlift_goal
            }
            tracker.save_profile()
            st.success("✅ Profil sauvegardé avec succès!")
            st.rerun()

    # Affichage des métriques calculées
    st.markdown("### 📊 Métriques calculées")

    col1, col2, col3 = st.columns(3)

    with col1:
        # IMC
        if tracker.profile.height > 0:
            bmi = tracker.profile.weight / ((tracker.profile.height / 100) ** 2)
            st.metric("📏 IMC", f"{bmi:.1f}")

    with col2:
        # Wilks Score approximatif (formule simplifiée)
        if tracker.profile.weight > 0:
            # Estimation basée sur les objectifs
            total_goal = bench_goal + squat_goal + deadlift_goal
            wilks_approx = total_goal / tracker.profile.weight * 2.2  # Approximation
            st.metric("🏆 Wilks estimé", f"{wilks_approx:.0f}")

    with col3:
        # Niveau d'expérience
        if tracker.profile.experience_years < 1:
            level = "Débutant"
        elif tracker.profile.experience_years < 3:
            level = "Intermédiaire"
        elif tracker.profile.experience_years < 5:
            level = "Avancé"
        else:
            level = "Expert"
        st.metric("🎖️ Niveau", level)

    # Suivi du poids corporel
    st.markdown("### ⚖️ Suivi du poids corporel")

    col1, col2 = st.columns([3, 1])
    with col1:
        new_weight = st.number_input("Nouveau poids (kg)", min_value=40.0, max_value=200.0, 
                                   value=tracker.profile.weight, step=0.1, key="new_weight_input")
    with col2:
        if st.button("➕ Ajouter mesure"):
            measurement = {
                "date": str(datetime.date.today()),
                "weight": new_weight,
                "type": "weight"
            }
            tracker.profile.measurements.append(measurement)
            tracker.profile.weight = new_weight  # Met à jour le poids actuel
            tracker.save_profile()
            st.success("✅ Mesure ajoutée!")
            st.rerun()

    # Graphique d'évolution du poids
    if tracker.profile.measurements:
        weight_data = [m for m in tracker.profile.measurements if m.get('type') == 'weight']
        if weight_data:
            df_weight = pd.DataFrame(weight_data)
            df_weight['date'] = pd.to_datetime(df_weight['date'])

            fig_weight_evolution = px.line(df_weight, x='date', y='weight',
                                         title='Évolution du poids corporel',
                                         labels={'weight': 'Poids (kg)', 'date': 'Date'})
            fig_weight_evolution.update_traces(line_color='#28a745', line_width=3)
            st.plotly_chart(fig_weight_evolution, use_container_width=True)

# ==================== PAGE PARAMÈTRES ====================
elif st.session_state.current_page == "⚙️ Paramètres":

    st.markdown("### ⚙️ Configuration du programme")

    # Configuration de la date de début
    with st.expander("📅 Date de début du programme"):
        new_start_date = st.date_input("Date de début", tracker.start_date)
        if st.button("💾 Mettre à jour la date"):
            tracker.start_date = new_start_date
            tracker.save_data()
            st.success("✅ Date mise à jour!")
            st.rerun()

    # Gestion des données
    st.markdown("### 💾 Gestion des données")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Exporter les données", help="Télécharge tes données en JSON"):
            # Création du fichier d'export
            export_data = {
                "profile": asdict(tracker.profile),
                "workout_data": {
                    "start_date": str(tracker.start_date),
                    "sessions": tracker.sessions
                },
                "export_date": str(datetime.date.today())
            }

            st.download_button(
                label="⬇️ Télécharger",
                data=json.dumps(export_data, indent=2),
                file_name=f"powerlifting_data_{datetime.date.today()}.json",
                mime="application/json"
            )

    with col2:
        if st.button("🔄 Réinitialiser les données", help="Supprime toutes les données"):
            if st.button("⚠️ Confirmer la suppression", type="secondary"):
                # Suppression des fichiers
                if os.path.exists(tracker.data_file):
                    os.remove(tracker.data_file)
                if os.path.exists(tracker.profile_file):
                    os.remove(tracker.profile_file)

                st.success("✅ Données supprimées!")
                st.info("🔄 Rechargez la page pour recommencer")

    with col3:
        st.markdown("**📱 Version mobile**")
        st.info("Ajoutez cette page à votre écran d'accueil pour une expérience app native!")

    # Informations sur l'application
    st.markdown("### ℹ️ À propos")

    st.markdown("""
    **💪 Powerlifting Pro v2.0**

    **Fonctionnalités:**
    - 🏋️ Tracking complet des entraînements
    - 📊 Statistiques et graphiques de progression
    - 👤 Gestion du profil et objectifs
    - 📱 Interface optimisée mobile
    - 💾 Sauvegarde automatique des données
    - 🧮 Calcul automatique des 1RM

    **Développé avec ❤️ pour les passionnés de force**
    """)

    # Instructions d'utilisation mobile
    with st.expander("📱 Guide d'utilisation mobile"):
        st.markdown("""
        **Pour une expérience optimale sur smartphone:**

        1. **🌐 Ouvrir dans Safari/Chrome**
        2. **📱 Menu "Partager" → "Ajouter à l'écran d'accueil"**
        3. **🏋️ Lancer depuis l'icône sur votre écran d'accueil**

        **Pendant l'entraînement:**
        - ✅ Trackez chaque série individuellement
        - 📊 Suivez votre progression en temps réel
        - 💾 Sauvegarde automatique de vos performances

        **Conseils:**
        - 🔋 Gardez votre téléphone chargé
        - 📶 Connexion internet recommandée pour la sauvegarde
        - 🏋️ Utilisez un support pour poser votre téléphone
        """)

# Footer
st.markdown("---")
st.markdown("💪 **Powerlifting Pro** - Votre compagnon d'entraînement de force")
