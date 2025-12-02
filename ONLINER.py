# streamlit_app.py
import streamlit as st
import pandas as pd
import random
import time
import os
from datetime import datetime
from PIL import Image, ImageDraw
import io
import base64

# -----------------------
# Konfiguration / Symbole
# -----------------------
SHAPES = [
    "Kreis_f", "Quadrat_f", "Raute_f", "Stern_f",
    "PfeilOben", "PfeilUnten", "PfeilLinks", "PfeilRechts",
    "Dreieck_f", "Doppelpfeil_H", "Doppelpfeil_V",
    "Kreis_h", "Quadrat_h", "Dreieck_h", "Stern_h", "Raute_h"
]

COLORS = [
    "red", "blue", "green", "orange",
    "purple", "brown", "cyan",
    "magenta", "gold", "darkgreen", "darkblue",
    "red", "blue", "gold", "magenta", "green"
]

TEST_SIZES = [3, 4, 5, 6, 7]
MEMORY_LIMIT_MS = 30000  # 30 Sekunden

# UI styling
ACCENT = "#4B7CDA"

# -----------------------
# Hilfsfunktionen
# -----------------------
def safe_upper_alpha(s):
    return "".join(ch for ch in s if ch.isalpha()).upper()

def create_shape_image(shape, color, size=80, variant="color"):
    """Erstellt ein Bild eines Symbols"""
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    is_hollow = shape.endswith("_h")
    draw_color = "black" if variant == "bw" else color
    
    # Farbe für Streamlit konvertieren
    color_map = {
        "red": (255, 0, 0), "blue": (0, 0, 255), "green": (0, 128, 0),
        "orange": (255, 165, 0), "purple": (128, 0, 128), "brown": (165, 42, 42),
        "cyan": (0, 255, 255), "magenta": (255, 0, 255), "gold": (255, 215, 0),
        "darkgreen": (0, 100, 0), "darkblue": (0, 0, 139), "black": (0, 0, 0)
    }
    
    outline_color = color_map.get(draw_color, (0, 0, 0))
    fill_color = (255, 255, 255) if is_hollow else outline_color
    line_width = 4 if is_hollow else 2
    
    # Koordinaten skalieren
    def scale(coords):
        return [coord * size / 100 for coord in coords]
    
    # --- Kreis ---
    if shape.startswith("Kreis"):
        bbox = [size*0.1, size*0.1, size*0.9, size*0.9]
        draw.ellipse(bbox, fill=fill_color, outline=outline_color, width=line_width)
    
    # --- Quadrat ---
    elif shape.startswith("Quadrat"):
        bbox = [size*0.12, size*0.12, size*0.88, size*0.88]
        draw.rectangle(bbox, fill=fill_color, outline=outline_color, width=line_width)
    
    # --- Raute ---
    elif shape.startswith("Raute"):
        coords = scale([50, 8, 88, 50, 50, 92, 12, 50])
        draw.polygon(coords, fill=fill_color, outline=outline_color, width=line_width)
    
    # --- Stern ---
    elif shape.startswith("Stern"):
        coords = scale([50, 12, 58, 34, 80, 34, 62, 50, 68, 74, 50, 60, 32, 74, 38, 50, 20, 34, 42, 34])
        draw.polygon(coords, fill=fill_color, outline=outline_color, width=line_width)
    
    # --- Dreieck ---
    elif shape.startswith("Dreieck"):
        coords = scale([50, 10, 90, 80, 10, 80])
        draw.polygon(coords, fill=fill_color, outline=outline_color, width=line_width)
    
    # --- Pfeil Oben ---
    elif shape == "PfeilOben":
        coords = scale([50, 10, 78, 50, 62, 50, 62, 90, 38, 90, 38, 50, 22, 50])
        draw.polygon(coords, fill=fill_color, outline=outline_color, width=line_width)
    
    # --- Pfeil Unten ---
    elif shape == "PfeilUnten":
        coords = scale([50, 90, 78, 50, 62, 50, 62, 10, 38, 10, 38, 50, 22, 50])
        draw.polygon(coords, fill=fill_color, outline=outline_color, width=line_width)
    
    # --- Pfeil Links ---
    elif shape == "PfeilLinks":
        coords = scale([10, 50, 50, 10, 50, 30, 90, 30, 90, 70, 50, 70, 50, 90])
        draw.polygon(coords, fill=fill_color, outline=outline_color, width=line_width)
    
    # --- Pfeil Rechts ---
    elif shape == "PfeilRechts":
        coords = scale([90, 50, 50, 10, 50, 30, 10, 30, 10, 70, 50, 70, 50, 90])
        draw.polygon(coords, fill=fill_color, outline=outline_color, width=line_width)
    
    # --- Doppelpfeil horizontal ---
    elif shape == "Doppelpfeil_H":
        draw.line(scale([18, 50, 82, 50]), fill=outline_color, width=line_width)
        draw.polygon(scale([18, 50, 30, 40, 30, 60]), fill=outline_color, outline=outline_color)
        draw.polygon(scale([82, 50, 70, 40, 70, 60]), fill=outline_color, outline=outline_color)
    
    # --- Doppelpfeil vertikal ---
    elif shape == "Doppelpfeil_V":
        draw.line(scale([50, 18, 50, 82]), fill=outline_color, width=line_width)
        draw.polygon(scale([50, 18, 40, 30, 60, 30]), fill=outline_color, outline=outline_color)
        draw.polygon(scale([50, 82, 40, 70, 60, 70]), fill=outline_color, outline=outline_color)
    
    # Fallback zu Kreis
    else:
        bbox = [size*0.1, size*0.1, size*0.9, size*0.9]
        draw.ellipse(bbox, fill=fill_color, outline=outline_color, width=line_width)
    
    return img

def image_to_base64(img):
    """Konvertiert ein PIL Image zu Base64 für Streamlit"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# -----------------------
# Streamlit App
# -----------------------
def main():
    # Session State initialisieren
    if 'page' not in st.session_state:
        st.session_state.page = 'start'
    if 'participant_data' not in st.session_state:
        st.session_state.participant_data = {}
    if 'test_state' not in st.session_state:
        st.session_state.test_state = {
            'variant': None,
            'current_test': 0,
            'sequence': [],
            'user_selections': [],
            'memory_start': None,
            'merk_times': [],
            'response_times': [],
            'correct_counts': [],
            'test_started': False
        }
    if 'questionnaire_answers' not in st.session_state:
        st.session_state.questionnaire_answers = [0] * 7
    if 'questionnaire_text' not in st.session_state:
        st.session_state.questionnaire_text = ""
    
    # CSS für besseres Aussehen
    st.markdown(f"""
    <style>
    .stButton>button {{
        background-color: {ACCENT};
        color: white;
        font-weight: bold;
    }}
    .title {{
        font-size: 28px;
        font-weight: bold;
        color: {ACCENT};
        text-align: center;
        margin-bottom: 20px;
    }}
    .section {{
        font-size: 20px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }}
    .info-box {{
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Seitensteuerung
    if st.session_state.page == 'start':
        show_start_page()
    elif st.session_state.page == 'instructions':
        show_instructions_page()
    elif st.session_state.page == 'test':
        show_test_page()
    elif st.session_state.page == 'questionnaire_intro':
        show_questionnaire_intro()
    elif st.session_state.page == 'questionnaire_a':
        show_questionnaire_a()
    elif st.session_state.page == 'questionnaire_b':
        show_questionnaire_b()
    elif st.session_state.page == 'thank_you':
        show_thank_you_page()

# -----------------------
# Seiten
# -----------------------
def show_start_page():
    st.markdown('<div class="title">Memory Test für Studie</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="info-box">Bitte beantworten Sie folgende Fragen, damit wir eine anonyme Teilnehmer-ID bilden können.</div>', unsafe_allow_html=True)
    
    with st.form("participant_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            mother = st.text_input("Die ersten zwei Buchstaben des Vornamens Ihrer Mutter:")
            father = st.text_input("Die letzten beiden Buchstaben des Vornamens Ihres Vaters:")
        
        with col2:
            birthyear = st.text_input("Ihr Geburtsjahr:", max_chars=4)
            age = st.text_input("Alter:", max_chars=3)
            gender = st.radio("Geschlecht:", ["M", "W", "D"], horizontal=True)
        
        submitted = st.form_submit_button("Test starten")
        
        if submitted:
            # Validierung
            mother_clean = safe_upper_alpha(mother.strip())
            father_clean = safe_upper_alpha(father.strip())
            
            errors = []
            if len(mother_clean) < 2:
                errors.append("Vorname der Mutter muss mindestens 2 Buchstaben enthalten.")
            if len(father_clean) < 2:
                errors.append("Vorname des Vaters muss mindestens 2 Buchstaben enthalten.")
            if not (birthyear.isdigit() and len(birthyear) == 4):
                errors.append("Geburtsjahr muss 4-stellig sein (z.B. 1990).")
            if not (age.isdigit() and 0 < int(age) < 130):
                errors.append("Bitte gültiges Alter eingeben.")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Daten speichern
                participant_id = f"{mother_clean[:2]}{father_clean[-2:]}{birthyear}"
                st.session_state.participant_data = {
                    'id': participant_id,
                    'age': int(age),
                    'gender': gender
                }
                
                # Zufällige Testvariante wählen
                st.session_state.test_state['variant'] = random.choice(["color", "bw"])
                st.session_state.test_state['current_test'] = 0
                st.session_state.test_state['merk_times'] = []
                st.session_state.test_state['response_times'] = []
                st.session_state.test_state['correct_counts'] = []
                st.session_state.test_state['test_started'] = False
                
                # Zur nächsten Seite
                st.session_state.page = 'instructions'
                st.rerun()

def show_instructions_page():
    st.markdown('<div class="title">Memory Test für Studie</div>', unsafe_allow_html=True)
    
    instructions = """
    **Anleitung:**
    
    Sie erhalten gleich eine Reihe von Symbolen. Bitte merken Sie sich deren Reihenfolge. 
    Sie haben für jede Merkphase 30 Sekunden Zeit.
    
    Sie können die Merkphase vor Ablauf auch durch Klick auf den „Weiter“-Button beenden, 
    ansonsten endet sie automatisch nach 30 Sekunden.
    
    Nach der Merkphase klicken Sie die Symbole in der Reihenfolge an, die Sie sich gemerkt haben.
    
    **Viel Erfolg!**
    """
    
    st.markdown(f'<div class="info-box">{instructions}</div>', unsafe_allow_html=True)
    
    if st.button("Weiter zum Test"):
        st.session_state.page = 'test'
        st.rerun()

def show_test_page():
    test_state = st.session_state.test_state
    current_test = test_state['current_test']
    
    # Prüfen ob alle Tests abgeschlossen
    if current_test >= len(TEST_SIZES):
        st.session_state.page = 'questionnaire_intro'
        st.rerun()
        return
    
    # Test starten wenn noch nicht gestartet
    if not test_state['test_started']:
        start_test()
        return
    
    size = TEST_SIZES[current_test]
    
    # Fortschrittsanzeige
    progress = (current_test + 1) / len(TEST_SIZES)
    st.progress(progress, text=f"Test {current_test + 1} von {len(TEST_SIZES)}")
    
    # Statusanzeige
    if 'memory_phase' in test_state and test_state['memory_phase']:
        show_memory_phase(size)
    elif 'input_phase' in test_state and test_state['input_phase']:
        show_input_phase(size)
    else:
        st.error("Fehler: Unbekannte Testphase")
        if st.button("Zurück zum Start"):
            st.session_state.page = 'start'
            st.rerun()

def start_test():
    test_state = st.session_state.test_state
    current_test = test_state['current_test']
    size = TEST_SIZES[current_test]
    
    # Neue Sequenz generieren
    test_state['sequence'] = random.sample(SHAPES, size)
    test_state['user_selections'] = []
    test_state['memory_start'] = time.time()
    test_state['memory_phase'] = True
    test_state['input_phase'] = False
    test_state['test_started'] = True
    
    st.rerun()

def show_memory_phase(size):
    test_state = st.session_state.test_state
    sequence = test_state['sequence']
    variant = test_state['variant']
    
    st.markdown(f'<div class="section">Test {test_state["current_test"] + 1}: Merke dir die Reihenfolge ({size} Symbole)</div>', unsafe_allow_html=True)
    
    # Symbole anzeigen
    cols = st.columns(len(sequence))
    for i, shape in enumerate(sequence):
        with cols[i]:
            color = COLORS[SHAPES.index(shape)]
            img = create_shape_image(shape, color, size=100, variant=variant)
            st.image(img, use_column_width=True)
    
    # Timer und Fortschrittsbalken
    elapsed = time.time() - test_state['memory_start']
    remaining = max(0, MEMORY_LIMIT_MS/1000 - elapsed)
    
    # Fortschrittsbalken
    progress = min(1.0, elapsed / (MEMORY_LIMIT_MS/1000))
    st.progress(progress, text=f"Verbleibende Zeit: {int(remaining)} Sekunden")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Weiter (Merkphase beenden)"):
            end_memory_phase()
    with col2:
        if st.button("Test abbrechen"):
            st.session_state.page = 'start'
            st.rerun()
    
    # Automatischer Übergang nach 30 Sekunden
    if elapsed >= MEMORY_LIMIT_MS/1000:
        end_memory_phase()

def end_memory_phase():
    test_state = st.session_state.test_state
    
    # Merkzeit berechnen und speichern
    merk_time = round(min(time.time() - test_state['memory_start'], MEMORY_LIMIT_MS/1000), 3)
    test_state['merk_times'].append(merk_time)
    
    # Zur Eingabephase wechseln
    test_state['memory_phase'] = False
    test_state['input_phase'] = True
    test_state['response_start'] = time.time()
    
    st.rerun()

def show_input_phase(size):
    test_state = st.session_state.test_state
    variant = test_state['variant']
    user_selections = test_state['user_selections']
    
    st.markdown('<div class="section">Eingabephase: Klicke die Symbole in der richtigen Reihenfolge</div>', unsafe_allow_html=True)
    
    # Alle verfügbaren Symbole anzeigen (in 2 Reihen)
    st.markdown("**Verfügbare Symbole:**")
    
    # Erste Reihe (erste 8 Symbole)
    cols1 = st.columns(8)
    for i in range(8):
        with cols1[i]:
            shape = SHAPES[i]
            color = COLORS[i]
            img = create_shape_image(shape, color, size=80, variant=variant)
            
            # Prüfen ob Symbol bereits ausgewählt wurde
            disabled = shape in user_selections
            
            if st.button("", key=f"shape_{i}", disabled=disabled):
                if shape not in user_selections:
                    test_state['user_selections'].append(shape)
                    st.rerun()
            st.image(img, use_column_width=True)
    
    # Zweite Reihe (restliche 8 Symbole)
    cols2 = st.columns(8)
    for i in range(8, 16):
        with cols2[i-8]:
            shape = SHAPES[i]
            color = COLORS[i]
            img = create_shape_image(shape, color, size=80, variant=variant)
            
            # Prüfen ob Symbol bereits ausgewählt wurde
            disabled = shape in user_selections
            
            if st.button("", key=f"shape_{i}", disabled=disabled):
                if shape not in user_selections:
                    test_state['user_selections'].append(shape)
                    st.rerun()
            st.image(img, use_column_width=True)
    
    # Ausgewählte Symbole anzeigen
    if user_selections:
        st.markdown("**Deine Auswahl:**")
        selected_cols = st.columns(len(user_selections))
        for i, shape in enumerate(user_selections):
            with selected_cols[i]:
                color = COLORS[SHAPES.index(shape)]
                img = create_shape_image(shape, color, size=60, variant=variant)
                st.image(img, use_column_width=True)
                st.markdown(f"**{i+1}.**")
    
    # Reset-Button
    if st.button("Auswahl zurücksetzen"):
        test_state['user_selections'] = []
        st.rerun()
    
    # Prüfen ob alle Symbole ausgewählt wurden
    if len(user_selections) == size:
        # Test beenden
        response_time = round(time.time() - test_state['response_start'], 3)
        test_state['response_times'].append(response_time)
        
        # Korrekte Antworten zählen
        correct = sum(1 for a, b in zip(user_selections, test_state['sequence']) if a == b)
        test_state['correct_counts'].append(correct)
        
        # Zum nächsten Test
        test_state['current_test'] += 1
        test_state['test_started'] = False
        
        # Kurze Pause dann nächster Test
        time.sleep(0.5)
        st.rerun()

def show_questionnaire_intro():
    st.markdown('<div class="title">Selbsteinschätzung (Fragebogen)</div>', unsafe_allow_html=True)
    
    intro_text = """
    **Vielen Dank, Sie haben die Tests geschafft!**
    
    Im folgenden Fragebogen schätzen Sie bitte Ihre eigene Erfahrung bei der Bearbeitung ein.
    
    Beantworten Sie bitte die Fragen ehrlich — es gibt kein richtig oder falsch.
    
    Klicken Sie auf „Zum Fragebogen“, um zu beginnen.
    """
    
    st.markdown(f'<div class="info-box">{intro_text}</div>', unsafe_allow_html=True)
    
    if st.button("Zum Fragebogen"):
        st.session_state.page = 'questionnaire_a'
        st.rerun()

def show_questionnaire_a():
    st.markdown('<div class="title">Selbsteinschätzung (Fragebogen)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section">Teil A — Subjektive Performance</div>', unsafe_allow_html=True)
    
    questions = [
        "1. Das Bearbeiten des Tests fiel mir leicht",
        "2. Ich musste mich sehr konzentrieren um mir die Informationen zu merken.",
        "3. Ich hatte Schwierigkeiten mir mehrere Informationen gleichzeitig zu merken.",
        "4. Ich hatte Spaß an der Bearbeitung des Tests"
    ]
    
    with st.form("questionnaire_a"):
        for i, question in enumerate(questions):
            st.markdown(f"**{question}**")
            
            # Skala 1-7 mit Beschriftungen
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            
            with col1:
                st.markdown("1<br>stimme<br>nicht zu", unsafe_allow_html=True)
                selected = st.radio(f"q{i}_1", [1], key=f"q{i}_1", label_visibility="collapsed")
            
            with col2:
                st.markdown("2", unsafe_allow_html=True)
                selected = st.radio(f"q{i}_2", [2], key=f"q{i}_2", label_visibility="collapsed")
            
            with col3:
                st.markdown("3", unsafe_allow_html=True)
                selected = st.radio(f"q{i}_3", [3], key=f"q{i}_3", label_visibility="collapsed")
            
            with col4:
                st.markdown("4", unsafe_allow_html=True)
                selected = st.radio(f"q{i}_4", [4], key=f"q{i}_4", label_visibility="collapsed")
            
            with col5:
                st.markdown("5", unsafe_allow_html=True)
                selected = st.radio(f"q{i}_5", [5], key=f"q{i}_5", label_visibility="collapsed")
            
            with col6:
                st.markdown("6", unsafe_allow_html=True)
                selected = st.radio(f"q{i}_6", [6], key=f"q{i}_6", label_visibility="collapsed")
            
            with col7:
                st.markdown("7<br>stimme<br>voll zu", unsafe_allow_html=True)
                selected = st.radio(f"q{i}_7", [7], key=f"q{i}_7", label_visibility="collapsed")
            
            # Wert speichern (hier vereinfacht - in realer App müsste der State gemanagt werden)
            if f"q{i}_selected" not in st.session_state:
                st.session_state[f"q{i}_selected"] = 4  # Default Wert
            
            st.divider()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("Zurück"):
                st.session_state.page = 'questionnaire_intro'
                st.rerun()
        with col2:
            if st.form_submit_button("Weiter"):
                # Hier sollten die Antworten gespeichert werden
                st.session_state.page = 'questionnaire_b'
                st.rerun()

def show_questionnaire_b():
    st.markdown('<div class="title">Selbsteinschätzung (Fragebogen)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section">Teil B — Weitere Einschätzung</div>', unsafe_allow_html=True)
    
    questions = [
        "5. Ich bin mit meiner Leistung im Test zufrieden",
        "6. Ich habe die korrekten Reihenfolgen reproduziert.",
        "7. Ich kann mir die angezeigte Reihenfolge für eine lange Zeit merken."
    ]
    
    with st.form("questionnaire_b"):
        for i, question in enumerate(questions, start=4):
            st.markdown(f"**{question}**")
            
            # Skala 1-7
            cols = st.columns(7)
            values = list(range(1, 8))
            
            for idx, col in enumerate(cols):
                with col:
                    value = values[idx]
                    if st.button(str(value), key=f"q{i}_{value}", use_container_width=True):
                        st.session_state.questionnaire_answers[i] = value
            
            # Aktuellen Wert anzeigen
            current_value = st.session_state.questionnaire_answers[i]
            if current_value > 0:
                st.info(f"Aktuelle Auswahl: {current_value}")
            
            st.divider()
        
        # Freitext Frage
        st.markdown("**8. Haben Sie eine Merkhilfe/Gedächtnisbrücke/Tricks verwendet?**")
        free_text = st.text_area("Ihre Antwort:", key="free_text", height=150)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button("Zurück"):
                st.session_state.page = 'questionnaire_a'
                st.rerun()
        with col2:
            if st.form_submit_button("Fragebogen abschicken"):
                # Antworten speichern
                st.session_state.questionnaire_text = free_text
                
                # Ergebnisse speichern (Excel-Datei)
                save_results()
                
                # Zur Danke-Seite
                st.session_state.page = 'thank_you'
                st.rerun()

def save_results():
    """Speichert Ergebnisse in Excel-Datei"""
    try:
        # Test-Ergebnisse
        test_data = {
            'ID': [st.session_state.participant_data['id']],
            'Alter': [st.session_state.participant_data['age']],
            'Geschlecht': [st.session_state.participant_data['gender']],
            'Testvariante': [st.session_state.test_state['variant']]
        }
        
        # Für jeden Test Größe und Ergebnisse
        for i in range(len(TEST_SIZES)):
            size = TEST_SIZES[i]
            prefix = f"Test_{i+1}"
            
            test_data[f"{prefix}_Größe"] = [size]
            if i < len(st.session_state.test_state['merk_times']):
                test_data[f"{prefix}_Merkzeit"] = [st.session_state.test_state['merk_times'][i]]
            if i < len(st.session_state.test_state['response_times']):
                test_data[f"{prefix}_Reaktionszeit"] = [st.session_state.test_state['response_times'][i]]
            if i < len(st.session_state.test_state['correct_counts']):
                test_data[f"{prefix}_Korrekt"] = [st.session_state.test_state['correct_counts'][i]]
        
        # Fragebogen-Daten
        q_data = {
            'ID': [st.session_state.participant_data['id']],
            'Testvariante': [st.session_state.test_state['variant']],
            'Datum': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        for i in range(7):
            q_data[f"Q{i+1}"] = [st.session_state.questionnaire_answers[i]]
        
        q_data['Q8_Freitext'] = [st.session_state.questionnaire_text]
        
        # DataFrames erstellen
        df_test = pd.DataFrame(test_data)
        df_questionnaire = pd.DataFrame(q_data)
        
        # In Excel speichern
        excel_file = "memorytest_results.xlsx"
        
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a' if os.path.exists(excel_file) else 'w') as writer:
            # Test-Ergebnisse in entsprechendes Sheet
            sheet_name = "FARBIG" if st.session_state.test_state['variant'] == "color" else "FARBLOS"
            df_test.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Fragebogen in eigenes Sheet
            df_questionnaire.to_excel(writer, sheet_name="QUESTIONNAIRE", index=False)
        
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False

def show_thank_you_page():
    st.markdown('<div class="title">Vielen Dank!</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3>Der Test ist beendet. Vielen Dank für Ihre Teilnahme!</h3>
    <p>Ihre Daten wurden gespeichert.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ergebnisse anzeigen
    st.markdown('<div class="section">Ihre Ergebnisse</div>', unsafe_allow_html=True)
    
    results_data = []
    for i in range(len(TEST_SIZES)):
        if i < len(st.session_state.test_state['correct_counts']):
            results_data.append({
                'Test': i+1,
                'Anzahl Symbole': TEST_SIZES[i],
                'Korrekt': st.session_state.test_state['correct_counts'][i],
                'Merkzeit (s)': st.session_state.test_state['merk_times'][i] if i < len(st.session_state.test_state['merk_times']) else "-",
                'Reaktionszeit (s)': st.session_state.test_state['response_times'][i] if i < len(st.session_state.test_state['response_times']) else "-"
            })
    
    if results_data:
        df_results = pd.DataFrame(results_data)
        st.dataframe(df_results, use_container_width=True, hide_index=True)
    
    # Gesamtstatistik
    if st.session_state.test_state['correct_counts']:
        total_correct = sum(st.session_state.test_state['correct_counts'])
        total_possible = sum(TEST_SIZES[:len(st.session_state.test_state['correct_counts'])])
        percentage = (total_correct / total_possible * 100) if total_possible > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamt korrekt", f"{total_correct}/{total_possible}")
        with col2:
            st.metric("Prozent korrekt", f"{percentage:.1f}%")
        with col3:
            variant = "farbig" if st.session_state.test_state['variant'] == "color" else "farblos"
            st.metric("Testvariante", variant)
    
    if st.button("Neuer Test starten"):
        # Session State zurücksetzen
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    main()