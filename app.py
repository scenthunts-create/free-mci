import streamlit as st
import requests
import json
import os
import pandas as pd

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Free-MCI AI Coach", 
    page_icon="🤖", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 2. DATENBANK SETUP (Kugelsicher) ---
USER_FILE = "user_data.json"

def load_data():
    # Standardwerte, falls die Datenbank neu ist oder Werte fehlen
    defaults = {
        "gewicht": 80.0, 
        "frequenz": 4, 
        "streak": 0,
        "alter": 30,
        "groesse": 180,
        "geschlecht": "Männlich",
        "ziel": "Muskelaufbau & Fettabbau"
    }
    
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            data = json.load(f)
            # Füllt fehlende Schlüssel (wie 'geschlecht') mit Standardwerten auf
            for key, value in defaults.items():
                if key not in data:
                    data[key] = value
            return data
            
    return defaults

def save_data(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f)

user_data = load_data()

# --- 3. BMR & KALORIEN LOGIK (Mifflin-St. Jeor) ---
def berechne_kalorien(daten):
    # Nutzt .get() zur Sicherheit, falls doch mal ein Wert fehlt
    geschlecht = daten.get("geschlecht", "Männlich")
    gewicht = float(daten.get("gewicht", 80.0))
    groesse = int(daten.get("groesse", 180))
    alter = int(daten.get("alter", 30))
    
    s = 5 if geschlecht == "Männlich" else -161
    bmr = (10 * gewicht) + (6.25 * groesse) - (5 * alter) + s
    
    # Aktivitätsfaktor 1.55 für 3-4 intensive Einheiten pro Woche
    tdee = bmr * 1.55 
    # Recomposition Ziel: Leichtes Defizit (-300 kcal) für Fettabbau bei Muskelaufbau
    ziel_kalorien = tdee - 300
    return int(ziel_kalorien)

ziel_kcal = berechne_kalorien(user_data)

# --- 4. ÜBUNGS-DATENBANK ---
exercises_data = [
    ["Kniebeugen (Squats)", "Kraft/Gym", "Beine Ganzheitlich", "Langhantel, Rack"],
    ["Bankdrücken (Bench Press)", "Kraft/Gym", "Brust, Trizeps", "Langhantel, Bank"],
    ["Kreuzheben (Deadlift)", "Kraft/Gym", "Rückenstrecker, Beine", "Langhantel"],
    ["Klimmzüge (Pull-Ups)", "Calisthenics", "Breiter Rücken, Bizeps", "Klimmzugstange/Kletterpark"],
    ["Dips (Barren- oder Ringe)", "Calisthenics", "Untere Brust, Trizeps", "Barren/Ringe/Kletterpark"],
    ["Liegestütze (Push-Ups)", "Calisthenics", "Brust, Trizeps", "Eigengewicht"],
    ["Muscle-Ups", "Calisthenics", "Ganzkörper Zug/Druck", "Stange/Kletterpark"],
    ["Plank", "Bodyweight", "Rumpf (Core)", "Eigengewicht"],
    ["Burpees", "Funktional/HiiT", "Ganzkörper", "Eigengewicht"],
    ["Ausfallschritte (Lunges)", "Kraft/Dynamisch", "Beine", "Eigengewicht/Kurzhantel"]
]
df_exercises = pd.DataFrame(exercises_data, columns=["Übung", "Typ", "Zielmuskel", "Equipment"])

@st.dialog("Übungs-Details & Ausführung")
def show_exercise_details(uebung, muskel, equipment):
    st.markdown(f"### {uebung}")
    st.info(f"**Fokus-Muskulatur:** {muskel}")
    st.write(f"**Benötigtes Equipment:** {equipment}")
    st.divider()
    search_query = uebung.replace(" ", "+") + "+tutorial+ausführung"
    st.markdown(f"[🎥 Klicke hier für Video-Anleitungen zu {uebung} auf YouTube](https://www.youtube.com/results?search_query={search_query})")
    if st.button("Schließen"): st.rerun()

# --- 5. UI & DASHBOARD ---
st.title("🏋️ FREE-MCI AI Coach")
st.markdown("*Adaptives Training & Recomposition Dashboard*")
st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric(label="Gewicht", value=f"{user_data['gewicht']} kg")
with col2: st.metric(label="Trainings/Woche", value=f"{user_data['frequenz']}")
with col3: st.metric(label="Tagesziel Kalorien", value=f"{ziel_kcal} kcal", delta="-300 kcal (Recomposition)", delta_color="inverse")
with col4: st.metric(label="Streak 🔥", value=f"{user_data['streak']} Tage")
st.divider()

tab_heute, tab_übungen, tab_ernährung, tab_profil = st.tabs([
    "📅 Mein Tag & Generator", "💪 Übungs-Datenbank", "🍎 Ernährung", "⚙️ Profil"
])

# --- TAB: HEUTE (WELLNESS & GENERATOR) ---
with tab_heute:
    st.header("1. Täglicher Wellness-Check")
    st.write("Wie fühlst du dich heute? Der Algorithmus passt dein Training an deine Eingaben an.")
    
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1: schlaf = st.slider("Schlafqualität (1=Mies, 10=Perfekt)", 1, 10, 7)
    with col_w2: muskelkater = st.slider("Muskelkater (1=Keiner, 10=Extreme Schmerzen)", 1, 10, 2)
    with col_w3: stress = st.slider("Stresslevel (1=Entspannt, 10=Burnout)", 1, 10, 3)
    
    st.divider()
    
    st.header("2. Quick-Workout Generator")
    col_zeit, col_ort = st.columns(2)
    with col_zeit: verfuegbare_zeit = st.select_slider("Wie viel Zeit hast du?", options=["15 Min", "30 Min", "45 Min", "1 Std", "1.5 Std+"], value="1 Std")
    with col_ort: trainings_ort = st.selectbox("Wo trainierst du heute?", ["All-Inclusive Gym", "Home-Workout (Eigengewicht)", "Kletterpark / Outdoor"])

    if st.button("🔥 Workout generieren"):
        # KI REGELKREISLAUF: Überprüfung der Wellness-Daten
        if muskelkater >= 8 or schlaf <= 3 or stress >= 8:
            st.error("🚨 RED FLAG: Dein Nervensystem ist überlastet. Der Coach verordnet aktive Regeneration!")
            st.markdown("### Dein angepasstes Recovery-Protokoll:")
            st.write("1. **10 Minuten lockeres Gehen / Spazieren**")
            st.write("2. **Mobility-Routine (Hüfte & Schultern aufdehnen)**")
            st.write("3. **Kein schweres Krafttraining heute.** Iss genug Protein und schlafe gut.")
        else:
            # Code für die Workouts
            saetze = "3 Sätze" if muskelkater >= 5 or schlaf <= 5 else "4 Sätze"
            if muskelkater < 5 and schlaf > 5 and stress < 5:
                st.success(f"System Check 🟢 | Plan für {verfuegbare_zeit} im {trainings_ort} erstellt!")
            else:
                st.warning(f"System Check 🟡 | Volumen leicht reduziert. Plan für {verfuegbare_zeit} im {trainings_ort} erstellt!")
                
            st.markdown("### Dein Workout für heute:")
            
            if trainings_ort == "All-Inclusive Gym":
                st.write(f"1. **Kniebeugen (Squats)** - {saetze}")
                st.write(f"2. **Bankdrücken** - {saetze}")
                st.write(f"3. **Latzug / Rudern am Kabelzug** - {saetze}")
                if verfuegbare_zeit in ["1 Std", "1.5 Std+"]:
                    st.write(f"4. **Kabelzug Trizeps & Bizeps Curls** - Jeweils 3 Sätze")
            elif trainings_ort == "Kletterpark / Outdoor":
                st.write("1. **Muscle-Up Progression / Versuche** - 10 Minuten")
                st.write(f"2. **Klimmzüge (Pull-Ups)** - {saetze}")
                st.write(f"3. **Dips an Ringen oder Stangen** - {saetze}")
            else:
                st.write(f"1. **Liegestütze (Push-Ups)** - {saetze}")
                st.write(f"2. **Ausfallschritte (Lunges)** - {saetze}")
                st.write("3. **Plank** - 3x auf Maximale Zeit")

# --- TAB: ÜBUNGEN ---
with tab_übungen:
    st.header("Die interaktive Datenbank")
    for index, row in df_exercises.iterrows():
        col_name, col_btn = st.columns([4, 1])
        with col_name: st.markdown(f"**{row['Übung']}** (*{row['Typ']}*)")
        with col_btn:
            if st.button("Details", key=f"btn_{index}"):
                show_exercise_details(row['Übung'], row['Zielmuskel'], row['Equipment'])
        st.divider()

# --- TAB: ERNÄHRUNG ---
with tab_ernährung:
    st.header("🍎 Lebensmittel Live-Suche")
    suchbegriff_food = st.text_input("Lebensmittel eingeben:", key="food_search")
    if st.button("Suchen"):
        if suchbegriff_food:
            with st.spinner('Suche...'):
                url = f"https://de.openfoodfacts.org/cgi/search.pl?search_terms={suchbegriff_food}&search_simple=1&action=process&json=1&page_size=5"
                response = requests.get(url)
                if response.status_code == 200:
                    daten = response.json()
                    treffer = daten.get("products", [])
                    if treffer:
                        for produkt in treffer:
                            name = produkt.get("product_name", "Unbekannt")
                            kalorien = produkt.get("nutriments", {}).get("energy-kcal_100g", "N/A")
                            protein = produkt.get("nutriments", {}).get("proteins_100g", "N/A")
                            with st.expander(f"📊 {name}"):
                                st.write(f"**{kalorien} kcal** / 100g | **Protein:** {protein}g / 100g")

# --- TAB: PROFIL ---
with tab_profil:
    st.header("⚙️ Körperdaten für den AI-Rechner")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        neues_gewicht = st.number_input("Gewicht (kg)", value=float(user_data["gewicht"]), step=0.1)
        neue_groesse = st.number_input("Größe (cm)", value=int(user_data.get("groesse", 180)), step=1)
    with col_p2:
        neues_alter = st.number_input("Alter", value=int(user_data.get("alter", 30)), step=1)
        neues_geschlecht = st.selectbox("Geschlecht", ["Männlich", "Weiblich"], index=0 if user_data.get("geschlecht", "Männlich") == "Männlich" else 1)
    
    neue_frequenz = st.slider("Trainingstage pro Woche", 1, 7, user_data["frequenz"])
    
    if st.button("Profil aktualisieren"):
        user_data.update({
            "gewicht": neues_gewicht, "groesse": neue_groesse,
            "alter": neues_alter, "geschlecht": neues_geschlecht,
            "frequenz": neue_frequenz
        })
        save_data(user_data)
        st.success("Daten und Kalorienziel aktualisiert!")
        st.rerun()
