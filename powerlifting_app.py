import streamlit as st
import datetime
import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

# Configuration de la page pour mobile
st.set_page_config(
    page_title="💪 Powerlifting Tracker",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS pour mobile
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #ff6b6b;
        font-size: 2rem;
        margin-bottom: 1rem;
    }
    .workout-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff6b6b;
    }
    .next-workout-card {
        background: #e8f4fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #3498db;
    }
    .exercise-name {
        font-weight: bold;
        font-size: 1.2rem;
        color: #2c3e50;
    }
    .exercise-details {
        color: #7f8c8d;
        font-size: 1rem;
    }
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        margin: 0.2rem 0;
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

@dataclass
class WorkoutSession:
    date: str
    workout_name: str
    week: int
    exercises: List[Exercise]
    completed: bool = False

class PowerliftingTracker:
    def __init__(self):
        self.data_file = "workout_data.json"
        self.load_data()

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

    def save_data(self):
        data = {
            'start_date': str(self.start_date),
            'sessions': self.sessions
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_current_week(self) -> int:
        today = datetime.date.today()
        days_elapsed = (today - self.start_date).days
        week = (days_elapsed // 7) + 1
        return min(max(week, 1), 8)

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

tracker = st.session_state.tracker

# Interface principale
st.markdown('<h1 class="main-header">💪 Powerlifting Tracker</h1>', unsafe_allow_html=True)

# Informations du programme
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📅 Semaine", f"{tracker.get_current_week()}/8")
with col2:
    st.metric("📍 Jour", datetime.date.today().strftime("%A"))
with col3:
    days_left = 56 - (datetime.date.today() - tracker.start_date).days
    st.metric("⏳ Jours restants", max(0, days_left))

# Configuration de la date de début
with st.expander("⚙️ Configuration"):
    new_start_date = st.date_input("Date de début du programme", tracker.start_date)
    if new_start_date != tracker.start_date:
        tracker.start_date = new_start_date
        tracker.save_data()
        st.rerun()

# Entraînement du jour
workout_name, exercises, week = tracker.get_today_workout()

if workout_name:
    st.markdown(f"## 🏋️ {workout_name}")
    st.markdown(f"**Semaine {week}/8**")

    # Initialisation de la session d'entraînement
    if 'current_workout' not in st.session_state:
        st.session_state.current_workout = exercises

    # Affichage des exercices
    for i, exercise in enumerate(st.session_state.current_workout):
        with st.container():
            st.markdown(f'<div class="workout-card">', unsafe_allow_html=True)

            # Nom et détails de l'exercice
            weight_str = f"{exercise.weight}kg" if exercise.weight > 0 else ""
            notes_str = f" ({exercise.notes})" if exercise.notes else ""

            st.markdown(f'<div class="exercise-name">{exercise.name}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="exercise-details">{exercise.sets} sets × {exercise.reps} reps {weight_str}{notes_str}</div>', unsafe_allow_html=True)

            # Boutons de tracking
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                if st.button(f"✅ Réussi", key=f"success_{i}", help="Marquer comme réussi"):
                    st.session_state.current_workout[i].completed_sets = exercise.sets
                    st.session_state.current_workout[i].status = "completed"
                    st.rerun()

            with col2:
                if st.button(f"❌ Raté", key=f"fail_{i}", help="Marquer comme raté (-5kg)"):
                    st.session_state.current_workout[i].failed_sets = exercise.sets
                    st.session_state.current_workout[i].status = "failed"
                    if exercise.weight > 0:
                        st.session_state.current_workout[i].weight = max(0, exercise.weight - 5)
                    st.warning(f"Poids ajusté: {st.session_state.current_workout[i].weight}kg (-5kg)")
                    st.rerun()

            with col3:
                # Indicateur de statut
                if exercise.status == "completed":
                    st.success("✅")
                elif exercise.status == "failed":
                    st.error("❌")
                else:
                    st.info("⏳")

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

    # Bouton de fin d'entraînement
    if st.button("🏁 Terminer l'entraînement", type="primary"):
        session = WorkoutSession(
            date=str(datetime.date.today()),
            workout_name=workout_name,
            week=week,
            exercises=[asdict(ex) for ex in st.session_state.current_workout],
            completed=True
        )
        tracker.sessions.append(asdict(session))
        tracker.save_data()

        st.success("🎉 Entraînement terminé et sauvegardé!")
        st.balloons()

        if 'current_workout' in st.session_state:
            del st.session_state.current_workout

else:
    st.markdown("## 🛌 Jour de repos")
    st.info("Récupération active recommandée - Étirements, marche, mobilité")

# Aperçu des prochains entraînements
st.markdown("## 📅 Prochains entraînements")
next_workouts = tracker.get_next_workouts(7)

if next_workouts:
    for workout in next_workouts[:3]:  # Affiche les 3 prochains
        with st.container():
            st.markdown(f'<div class="next-workout-card">', unsafe_allow_html=True)

            st.markdown(f"**{workout['day_name']} {workout['date'].strftime('%d/%m')} - {workout['workout_name']}**")
            st.markdown(f"*Semaine {workout['week']}/8*")

            # Affiche les 3 premiers exercices
            for ex in workout['exercises'][:3]:
                weight_str = f" @ {ex.weight}kg" if ex.weight > 0 else ""
                notes_str = f" ({ex.notes})" if ex.notes else ""
                st.markdown(f"• {ex.name}: {ex.sets}×{ex.reps}{weight_str}{notes_str}")

            if len(workout['exercises']) > 3:
                st.markdown(f"• ... et {len(workout['exercises']) - 3} autres exercices")

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
else:
    st.info("Aucun entraînement prévu dans les 7 prochains jours")

# Historique
if tracker.sessions:
    with st.expander("📊 Historique des entraînements"):
        for session in reversed(tracker.sessions[-5:]):
            st.markdown(f"**{session['date']} - {session['workout_name']}**")
            completed_exercises = sum(1 for ex in session['exercises'] if ex['status'] == 'completed')
            total_exercises = len(session['exercises'])
            st.progress(completed_exercises / total_exercises if total_exercises > 0 else 0)
            st.markdown(f"Exercices réussis: {completed_exercises}/{total_exercises}")
            st.markdown("---")

# Instructions d'utilisation
with st.expander("📱 Comment utiliser sur iPhone"):
    st.markdown("""
    **Pour une expérience optimale sur iPhone:**

    1. 🌐 Ouvre cette page dans Safari
    2. 📱 Appuie sur le bouton "Partager" 
    3. ➕ Sélectionne "Ajouter à l'écran d'accueil"
    4. 🏋️ Lance l'app depuis ton écran d'accueil

    **Pendant l'entraînement:**
    - ✅ Appuie sur "Réussi" si tu complètes toutes les séries
    - ❌ Appuie sur "Raté" si tu n'arrives pas (poids ajusté automatiquement)
    - 🏁 Termine l'entraînement pour sauvegarder
    """)
