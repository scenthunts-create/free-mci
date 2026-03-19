import streamlit as st
import requests
import json
import os

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(
    page_title="Free-MCI AI Coach", 
    page_icon="🤖", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- 2. NUTZER-DATENBANK SETUP ---
# Wir nutzen eine lokale JSON-Datei als einfache, kostenlose Datenbank
USER_FILE = "user_data.json"

def load_data():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    # Startwerte beim allerersten Öffnen der App
    return {
        "gewicht": 80.0, 
        "ziel": "Muskelaufbau & Fettabbau", 
        "frequenz": 4
    }

def save_data(data):
    with open(USER_FILE, "w") as f:
        json.dump(data, f)

user_data = load_data()

# --- 3. BENUTZEROBERFLÄCHE (UI) ---
st.title("🏋️ Free-MCI AI Dashboard")
st.markdown("Willkommen in deinem persönlichen, adaptiven Fitness-System.")
st.divider()

# Sidebar für Profil-Einstellungen
st.sidebar.header("⚙️ Profil & Setup")
neues_gewicht = st.sidebar.number_input("Aktuelles Gewicht (kg)", value=user_data["gewicht"], step=0.5)
neue_frequenz = st.sidebar.slider("Trainingstage pro Woche", min_value=1, max_value=7, value=user_data["frequenz"])

if st.sidebar.button("Profil speichern"):
    user_data["gewicht"] = neues_gewicht
    user_data["frequenz"] = neue_frequenz
    save_data(user_data)
    st.sidebar.success("Daten erfolgreich gespeichert!")

# --- 4. ERNÄHRUNGS-MODUL (OPEN FOOD FACTS API) ---
st.header("🍎 Lebensmittel-Tracker (Live-Suche)")
st.write("Suche nach Lebensmitteln, um Kalorien und Makros zu checken. Die Daten kommen direkt aus der kostenlosen Open Food Facts Datenbank.")

suchbegriff = st.text_input("Lebensmittel eingeben (z.B. Magerquark, Haferflocken):")

if st.button("Suchen"):
    if suchbegriff:
        # Abruf der Daten über die kostenlose Schnittstelle
        url = f"https://de.openfoodfacts.org/cgi/search.pl?search_terms={suchbegriff}&search_simple=1&action=process&json=1&page_size=5"
        response = requests.get(url)
        
        if response.status_code == 200:
            daten = response.json()
            treffer = daten.get("products", [])
            
            if treffer:
                for produkt in treffer:
                    name = produkt.get("product_name", "Unbekanntes Produkt")
                    marke = produkt.get("brands", "Ohne Marke")
                    kalorien = produkt.get("nutriments", {}).get("energy-kcal_100g", "Keine Angabe")
                    protein = produkt.get("nutriments", {}).get("proteins_100g", "Keine Angabe")
                    
                    st.success(f"**{name}** ({marke})")
                    st.write(f"📊 **Energie:** {kalorien} kcal / 100g | **Protein:** {protein}g / 100g")
                    st.divider()
            else:
                st.warning("Kein Lebensmittel gefunden. Versuche einen anderen Begriff.")
        else:
            st.error("Fehler bei der Verbindung zur Server-Datenbank.")

# --- 5. ÜBUNGS-DATENBANK STRUKTUR ---
st.header("⚙️ Trainings-Datenbank (Vorschau)")
st.write("Hier wird der Algorithmus die 50 wichtigsten Übungen für Gym und Calisthenics verwalten.")

# Dies ist das Fundament, in das wir im nächsten Schritt die 50 Übungen injizieren
uebungen_struktur = {
    "Klimmzüge (Pull-Ups)": {"Typ": "Calisthenics", "Fokus": "Rücken/Bizeps", "Kategorie": "Pull"},
    "Kniebeugen (Squats)": {"Typ": "Gym/Barbell", "Fokus": "Beine/Core", "Kategorie": "Legs"},
    "Bankdrücken (Bench Press)": {"Typ": "Gym/Barbell", "Fokus": "Brust/Trizeps", "Kategorie": "Push"},
    "Muscle-Ups": {"Typ": "Calisthenics", "Fokus": "Ganzkörper", "Kategorie": "Funktional"}
}
st.json(uebungen_struktur)
