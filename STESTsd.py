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

# -----------------------
# Streamlit App
# -----------------------
def main():
    # CSS für besseres Aussehen
    st.markdown(f"""
    <style>
    .stButton>button {{
        background-color: {ACCENT};
        color: white;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
    }}
    .stButton>button:hover {{
        background-color: #3a6bc5;
    }}
    .title {{
        font-size: 32px;
        font-weight: bold;
        color: {ACCENT};
        text-align: center;
        margin-bottom: 30px;
        padding-bottom: 15px;
        border-bottom: 2px solid {ACCENT};
    }}
    .section {{
        font-size: 24px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 20px;
        color: #333;
    }}
    .subsection {{
        font-size: 20px;
        font-weight: bold;
        margin-top: 25px;
        margin-bottom: 15px;
        color: #444;
    }}
    .info-box {{
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 10px;
        margin-bottom: 25px;
        border-left: 5px solid {ACCENT};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    .question-box {{
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .shape-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }}
    .shape-container:hover {{
        border-color: {ACCENT};
        background-color: #f0f5ff;
    }}
    .shape-container.selected {{
        border-color: {ACCENT};
        background-color: #e6f0ff;
    }}
    .timer-box {{
        background-color: #e8f4f8;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0;
        text-align: center;
        border: 2px solid #b8d8e8;
    }}
    .radio-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 15px 0;
        padding: 10px;
    }}
    .radio-label {{
        font-size: 14px;
        color: #666;
        text-align: center;
        margin: 0 10px;
        min-width: 100px;
    }}
    .stTextArea textarea {{
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }}
    .stTextArea textarea:focus {{
        border-color: {ACCENT};
        box-shadow: 0 0 0 1px {ACCENT};
    }}
    .stTextInput input {{
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }}
    .stTextInput input:focus {{
        border-color: {ACCENT};
        box-shadow: 0 0 0 1px {ACCENT};
    }}
    .results-table {{
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin: 20px 0;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Session State initialisieren
    init_session_state()
    
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

def init_session_state():
    """Initialisiert den Session State"""
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
            'test_started': False,
            'memory_phase': False,
            'input_phase': False,
            'last_update': None
        }
    if 'questionnaire_answers' not in st.session_state:
        st.session_state.questionnaire_answers = [0] * 7
    if 'questionnaire_text' not in st.session_state:
        st.session_state.questionnaire_text = ""
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'timer_end' not in st.session_state:
        st.session_state.timer_end = None

# -----------------------
# Seiten
# -----------------------
def show_start_page():
    st.markdown('<div class="title">Memory Test für Studie</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3 style="margin-top: 0;">Willkommen zum Memory Test</h3>
    <p>Bitte beantworten Sie folgende Fragen, damit wir eine anonyme Teilnehmer-ID bilden können.</p>
    <p>Alle Daten werden vertraulich behandelt und nur für wissenschaftliche Zwecke verwendet.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("participant_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Persönliche Informationen**")
            mother = st.text_input(
                "Die ersten zwei Buchstaben des Vornamens Ihrer Mutter:",
                help="Bitte nur Buchstaben eingeben"
            )
            father = st.text_input(
                "Die letzten beiden Buchstaben des Vornamens Ihres Vaters:",
                help="Bitte nur Buchstaben eingeben"
            )
        
        with col2:
            st.markdown("**Demografische Daten**")
            birthyear = st.text_input(
                "Ihr Geburtsjahr:",
                max_chars=4,
                help="Format: YYYY (z.B. 1990)"
            )
            age = st.text_input(
                "Alter:",
                max_chars=3,
                help="Aktuelles Alter in Jahren"
            )
            st.markdown("**Geschlecht:**")
            gender_cols = st.columns(3)
            with gender_cols[0]:
                gender_m = st.radio("", ["M"], key="gender_m", label_visibility="collapsed")
            with gender_cols[1]:
                gender_w = st.radio("", ["W"], key="gender_w", label_visibility="collapsed")
            with gender_cols[2]:
                gender_d = st.radio("", ["D"], key="gender_d", label_visibility="collapsed")
            
            # Geschlecht bestimmen
            gender = "M"
        
        submitted = st.form_submit_button("Test starten", type="primary", use_container_width=True)
        
        if submitted:
            # Validierung
            mother_clean = safe_upper_alpha(mother.strip())
            father_clean = safe_upper_alpha(father.strip())
            
            errors = []
            if len(mother_clean) < 2:
                errors.append("❌ Vorname der Mutter muss mindestens 2 Buchstaben enthalten.")
            if len(father_clean) < 2:
                errors.append("❌ Vorname des Vaters muss mindestens 2 Buchstaben enthalten.")
            if not (birthyear.isdigit() and len(birthyear) == 4):
                errors.append("❌ Geburtsjahr muss 4-stellig sein (z.B. 1990).")
            if not (age.isdigit() and 0 < int(age) < 130):
                errors.append("❌ Bitte gültiges Alter eingeben.")
            
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
    ### 📋 Anleitung zum Test
    
    **Ablauf:**
    1. **Merkphase**: Ihnen wird eine Reihe von Symbolen gezeigt. Merken Sie sich deren Reihenfolge.
    2. **Eingabephase**: Klicken Sie die Symbole in der gemerkten Reihenfolge an.
    
    **Wichtige Hinweise:**
    - Sie haben **30 Sekunden** Zeit für jede Merkphase
    - Sie können die Merkphase vorzeitig mit dem "Weiter"-Button beenden
    - Klicken Sie in der Eingabephase die Symbole **in der richtigen Reihenfolge** an
    - Es gibt insgesamt 5 Tests mit unterschiedlicher Anzahl von Symbolen (3-7)
    
    **Tipp:** Konzentrieren Sie sich auf die Position und das Aussehen jedes Symbols.
    
    **Viel Erfolg!** 🎯
    """
    
    st.markdown(f'<div class="info-box">{instructions}</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶️ Test beginnen", type="primary", use_container_width=True):
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
    
    # Fortschrittsanzeige
    st.markdown('<div class="title">Memory Test</div>', unsafe_allow_html=True)
    
    progress = (current_test) / len(TEST_SIZES)
    st.progress(progress, text=f"Fortschritt: {current_test} von {len(TEST_SIZES)} Tests abgeschlossen")
    
    # Test starten wenn noch nicht gestartet
    if not test_state['test_started']:
        start_test()
        return
    
    size = TEST_SIZES[current_test]
    
    # Statusanzeige
    if test_state['memory_phase']:
        show_memory_phase(size)
    elif test_state['input_phase']:
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
    test_state['timer_start'] = time.time()
    
    st.rerun()

def show_memory_phase(size):
    test_state = st.session_state.test_state
    sequence = test_state['sequence']
    variant = test_state['variant']
    
    st.markdown(f'<div class="subsection">Test {test_state["current_test"] + 1}: Merke dir die Reihenfolge ({size} Symbole)</div>', unsafe_allow_html=True)
    
    # Timer-Anzeige
    if 'timer_start' in test_state:
        elapsed = time.time() - test_state['timer_start']
        remaining = max(0, MEMORY_LIMIT_MS/1000 - elapsed)
        
        st.markdown(f"""
        <div class="timer-box">
        <h3 style="margin: 0; color: #0c5460;">⏱️ Verbleibende Zeit: {int(remaining)} Sekunden</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Fortschrittsbalken
        progress = min(1.0, elapsed / (MEMORY_LIMIT_MS/1000))
        st.progress(progress)
    
    # Symbole anzeigen mit schöner Darstellung
    st.markdown("<div style='text-align: center; margin: 30px 0;'>", unsafe_allow_html=True)
    
    cols = st.columns(len(sequence))
    for i, shape in enumerate(sequence):
        with cols[i]:
            color = COLORS[SHAPES.index(shape)]
            img = create_shape_image(shape, color, size=120, variant=variant)
            st.image(img, use_column_width=True)
            st.markdown(f"<div style='text-align: center; font-weight: bold; margin-top: 5px;'>Position {i+1}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("✅ Weiter (Merkphase beenden)", type="primary", use_container_width=True):
            end_memory_phase()
    
    # Automatischer Übergang nach 30 Sekunden
    if 'timer_start' in test_state:
        elapsed = time.time() - test_state['timer_start']
        if elapsed >= MEMORY_LIMIT_MS/1000:
            end_memory_phase()

def end_memory_phase():
    test_state = st.session_state.test_state
    
    # Merkzeit berechnen und speichern
    if 'timer_start' in test_state:
        merk_time = round(min(time.time() - test_state['timer_start'], MEMORY_LIMIT_MS/1000), 3)
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
    
    st.markdown(f'<div class="subsection">Eingabephase: Klicken Sie die Symbole in der gemerkten Reihenfolge</div>', unsafe_allow_html=True)
    
    # Timer für Eingabephase
    if 'response_start' in test_state:
        elapsed = time.time() - test_state['response_start']
        st.markdown(f"<div style='text-align: center; color: #666; margin: 10px 0;'>Eingabezeit: {elapsed:.1f} Sekunden</div>", unsafe_allow_html=True)
    
    # Alle verfügbaren Symbole anzeigen (in 2 Reihen)
    st.markdown("### Verfügbare Symbole")
    
    # Erste Reihe (erste 8 Symbole)
    cols1 = st.columns(8)
    for i in range(8):
        with cols1[i]:
            shape = SHAPES[i]
            color = COLORS[i]
            img = create_shape_image(shape, color, size=80, variant=variant)
            
            # Prüfen ob Symbol bereits ausgewählt wurde
            is_selected = shape in user_selections
            
            # Container für Symbol mit Hover-Effekt
            container = st.container()
            with container:
                if is_selected:
                    st.markdown(f"<div class='shape-container selected'>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='shape-container'>", unsafe_allow_html=True)
                
                # Button zum Auswählen
                if not is_selected:
                    if st.button("", key=f"shape_{i}", help=f"Symbol auswählen: {shape}"):
                        if shape not in user_selections and len(user_selections) < size:
                            test_state['user_selections'].append(shape)
                            st.rerun()
                
                # Symbolbild anzeigen
                st.image(img, use_column_width=True)
                
                # Symbolname (nur für Debug)
                # st.markdown(f"<div style='text-align: center; font-size: 10px; color: #888;'>{shape}</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Zweite Reihe (restliche 8 Symbole)
    cols2 = st.columns(8)
    for i in range(8, 16):
        with cols2[i-8]:
            shape = SHAPES[i]
            color = COLORS[i]
            img = create_shape_image(shape, color, size=80, variant=variant)
            
            # Prüfen ob Symbol bereits ausgewählt wurde
            is_selected = shape in user_selections
            
            # Container für Symbol mit Hover-Effekt
            container = st.container()
            with container:
                if is_selected:
                    st.markdown(f"<div class='shape-container selected'>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='shape-container'>", unsafe_allow_html=True)
                
                # Button zum Auswählen
                if not is_selected:
                    if st.button("", key=f"shape_{i}", help=f"Symbol auswählen: {shape}"):
                        if shape not in user_selections and len(user_selections) < size:
                            test_state['user_selections'].append(shape)
                            st.rerun()
                
                # Symbolbild anzeigen
                st.image(img, use_column_width=True)
                
                # Symbolname (nur für Debug)
                # st.markdown(f"<div style='text-align: center; font-size: 10px; color: #888;'>{shape}</div>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Ausgewählte Symbole anzeigen
    if user_selections:
        st.markdown("### Ihre Auswahl (Reihenfolge)")
        
        selected_cols = st.columns(len(user_selections))
        for i, shape in enumerate(user_selections):
            with selected_cols[i]:
                color = COLORS[SHAPES.index(shape)]
                img = create_shape_image(shape, color, size=80, variant=variant)
                
                st.markdown(f"<div style='text-align: center;'>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-weight: bold; color: {ACCENT}; font-size: 18px;'>Position {i+1}</div>", unsafe_allow_html=True)
                st.image(img, use_column_width=True)
                
                # Korrekte Position prüfen
                if i < len(test_state['sequence']):
                    if shape == test_state['sequence'][i]:
                        st.markdown("✅ Korrekt", unsafe_allow_html=True)
                    else:
                        st.markdown("❌", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Auswahl zurücksetzen"):
            test_state['user_selections'] = []
            st.rerun()
    
    with col2:
        if st.button("⏭️ Test überspringen"):
            # Leere Auswahl für übersprungenen Test
            test_state['user_selections'] = []
            finish_test()
    
    with col3:
        if st.button("🏠 Test abbrechen"):
            st.session_state.page = 'start'
            st.rerun()
    
    # Automatische Beendigung wenn alle Symbole ausgewählt
    if len(user_selections) == size:
        finish_test()

def finish_test():
    test_state = st.session_state.test_state
    
    # Reaktionszeit speichern
    if 'response_start' in test_state:
        response_time = round(time.time() - test_state['response_start'], 3)
        test_state['response_times'].append(response_time)
    
    # Korrekte Antworten zählen
    correct = 0
    for i in range(min(len(test_state['user_selections']), len(test_state['sequence']))):
        if test_state['user_selections'][i] == test_state['sequence'][i]:
            correct += 1
    
    test_state['correct_counts'].append(correct)
    
    # Zum nächsten Test
    test_state['current_test'] += 1
    test_state['test_started'] = False
    
    # Erfolgsmeldung anzeigen
    if correct == len(test_state['sequence']):
        st.success(f"🎉 Perfekt! Alle {correct} Symbole korrekt!")
    else:
        st.info(f"Ergebnis: {correct} von {len(test_state['sequence'])} Symbolen korrekt")
    
    # Kurze Pause dann nächster Test
    time.sleep(1.5)
    st.rerun()

def show_questionnaire_intro():
    st.markdown('<div class="title">Selbsteinschätzung (Fragebogen)</div>', unsafe_allow_html=True)
    
    intro_text = """
    ### 📝 Fragebogen zur Selbsteinschätzung
    
    **Herzlichen Glückwunsch zum Abschluss der Tests!** 🎊
    
    Im folgenden Fragebogen schätzen Sie bitte Ihre eigene Erfahrung bei der Bearbeitung der Memory-Tests ein.
    
    **Wichtig:**
    - Beantworten Sie die Fragen bitte **ehrlich**
    - Es gibt **kein richtig oder falsch**
    - Ihre Antworten helfen uns, die Tests zu verbessern
    - Alle Angaben sind **anonym**
    
    **Skala:** Bitte bewerten Sie auf einer Skala von 1 bis 7, wobei:
    - **1 = "stimme nicht zu"**
    - **7 = "stimme voll zu"**
    
    Klicken Sie auf "Zum Fragebogen", um zu beginnen.
    """
    
    st.markdown(f'<div class="info-box">{intro_text}</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📋 Zum Fragebogen", type="primary", use_container_width=True):
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
    
    # Speichere Antworten in Session State
    if 'q_responses_a' not in st.session_state:
        st.session_state.q_responses_a = [0] * 4
    
    for i, question in enumerate(questions):
        st.markdown(f'<div class="question-box"><h4>{question}</h4></div>', unsafe_allow_html=True)
        
        # Radio Buttons mit Labels links und rechts
        cols = st.columns([2, 1, 1, 1, 1, 1, 1, 1, 2])
        
        with cols[0]:
            st.markdown('<div class="radio-label">stimme<br>nicht zu</div>', unsafe_allow_html=True)
        
        # Radio Buttons 1-7
        for j in range(1, 8):
            with cols[j]:
                if st.radio(
                    f"Q{i+1}_{j}",
                    options=[j],
                    key=f"q{i}_{j}",
                    label_visibility="collapsed",
                    horizontal=True
                ):
                    st.session_state.q_responses_a[i] = j
        
        with cols[8]:
            st.markdown('<div class="radio-label">stimme<br>voll zu</div>', unsafe_allow_html=True)
        
        # Angezeigter Wert
        if st.session_state.q_responses_a[i] > 0:
            st.markdown(f"<div style='text-align: center; color: {ACCENT}; font-weight: bold; margin: 10px 0;'>Ausgewählt: {st.session_state.q_responses_a[i]}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Zurück"):
            st.session_state.page = 'questionnaire_intro'
            st.rerun()
    with col2:
        if st.button("Weiter ➡️", type="primary"):
            # Fragebogen-Antworten speichern
            for i in range(4):
                if st.session_state.q_responses_a[i] > 0:
                    st.session_state.questionnaire_answers[i] = st.session_state.q_responses_a[i]
            
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
    
    # Speichere Antworten in Session State
    if 'q_responses_b' not in st.session_state:
        st.session_state.q_responses_b = [0] * 3
    
    for i, question in enumerate(questions):
        st.markdown(f'<div class="question-box"><h4>{question}</h4></div>', unsafe_allow_html=True)
        
        # Radio Buttons mit Labels links und rechts
        cols = st.columns([2, 1, 1, 1, 1, 1, 1, 1, 2])
        
        with cols[0]:
            st.markdown('<div class="radio-label">stimme<br>nicht zu</div>', unsafe_allow_html=True)
        
        # Radio Buttons 1-7
        for j in range(1, 8):
            with cols[j]:
                if st.radio(
                    f"Q{i+5}_{j}",
                    options=[j],
                    key=f"q{i+4}_{j}",
                    label_visibility="collapsed",
                    horizontal=True
                ):
                    st.session_state.q_responses_b[i] = j
        
        with cols[8]:
            st.markdown('<div class="radio-label">stimme<br>voll zu</div>', unsafe_allow_html=True)
        
        # Angezeigter Wert
        if st.session_state.q_responses_b[i] > 0:
            st.markdown(f"<div style='text-align: center; color: {ACCENT}; font-weight: bold; margin: 10px 0;'>Ausgewählt: {st.session_state.q_responses_b[i]}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Freitext Frage
    st.markdown(f'<div class="question-box"><h4>8. Haben Sie eine Merkhilfe/Gedächtnisbrücke/Tricks verwendet?</h4></div>', unsafe_allow_html=True)
    
    free_text = st.text_area(
        "Bitte beschreiben Sie Ihre Strategie:",
        height=150,
        placeholder="Wenn ja, welche Technik haben Sie verwendet? (z.B. Geschichten erzählen, Bilder verknüpfen, rhythmisches Merken...)\n\nWenn nein, lassen Sie das Feld einfach leer.",
        key="free_text_area"
    )
    
    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Zurück zu Teil A"):
            st.session_state.page = 'questionnaire_a'
            st.rerun()
    with col2:
        if st.button("✅ Fragebogen absenden", type="primary"):
            # Fragebogen-Antworten speichern
            for i in range(3):
                if st.session_state.q_responses_b[i] > 0:
                    st.session_state.questionnaire_answers[i+4] = st.session_state.q_responses_b[i]
            
            st.session_state.questionnaire_text = free_text
            
            # Ergebnisse speichern
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
            'Testvariante': [st.session_state.test_state['variant']],
            'Datum': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        }
        
        # Für jeden Test Größe und Ergebnisse
        for i in range(len(TEST_SIZES)):
            size = TEST_SIZES[i]
            
            test_data[f"Test_{i+1}_Größe"] = [size]
            if i < len(st.session_state.test_state['merk_times']):
                test_data[f"Test_{i+1}_Merkzeit"] = [st.session_state.test_state['merk_times'][i]]
            if i < len(st.session_state.test_state['response_times']):
                test_data[f"Test_{i+1}_Reaktionszeit"] = [st.session_state.test_state['response_times'][i]]
            if i < len(st.session_state.test_state['correct_counts']):
                test_data[f"Test_{i+1}_Korrekt"] = [st.session_state.test_state['correct_counts'][i]]
        
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
        
        if os.path.exists(excel_file):
            with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                # Test-Ergebnisse in entsprechendes Sheet
                sheet_name = "FARBIG" if st.session_state.test_state['variant'] == "color" else "FARBLOS"
                df_test.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Fragebogen in eigenes Sheet
                df_questionnaire.to_excel(writer, sheet_name="QUESTIONNAIRE", index=False)
        else:
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                # Test-Ergebnisse in entsprechendes Sheet
                sheet_name = "FARBIG" if st.session_state.test_state['variant'] == "color" else "FARBLOS"
                df_test.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Fragebogen in eigenes Sheet
                df_questionnaire.to_excel(writer, sheet_name="QUESTIONNAIRE", index=False)
        
        st.session_state.saved_path = os.path.abspath(excel_file)
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern: {e}")
        return False

def show_thank_you_page():
    st.markdown('<div class="title">Vielen Dank für Ihre Teilnahme! 🌟</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    <h3 style="color: #28a745;">Test erfolgreich abgeschlossen!</h3>
    <p>Ihre Daten wurden gespeichert und werden für die wissenschaftliche Auswertung verwendet.</p>
    <p><strong>Vielen Dank für Ihre wertvolle Zeit und Mühe!</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ergebnisse anzeigen
    st.markdown('<div class="section">📊 Ihre Testergebnisse</div>', unsafe_allow_html=True)
    
    results_data = []
    total_correct = 0
    total_possible = 0
    
    for i in range(len(TEST_SIZES)):
        if i < len(st.session_state.test_state['correct_counts']):
            correct = st.session_state.test_state['correct_counts'][i]
            size = TEST_SIZES[i]
            total_correct += correct
            total_possible += size
            
            merk_time = "-"
            response_time = "-"
            
            if i < len(st.session_state.test_state['merk_times']):
                merk_time = f"{st.session_state.test_state['merk_times'][i]:.1f}s"
            if i < len(st.session_state.test_state['response_times']):
                response_time = f"{st.session_state.test_state['response_times'][i]:.1f}s"
            
            results_data.append({
                'Test': i+1,
                'Symbole': size,
                'Korrekt': correct,
                'Merkzeit': merk_time,
                'Eingabezeit': response_time,
                'Prozent': f"{(correct/size*100):.0f}%"
            })
    
    if results_data:
        df_results = pd.DataFrame(results_data)
        
        # Tabelle mit CSS stylen
        st.markdown('<div class="results-table">', unsafe_allow_html=True)
        st.dataframe(
            df_results,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Test": st.column_config.NumberColumn("Test", width="small"),
                "Symbole": st.column_config.NumberColumn("Symbole", width="small"),
                "Korrekt": st.column_config.NumberColumn("Korrekt", width="small"),
                "Merkzeit": st.column_config.TextColumn("Merkzeit"),
                "Eingabezeit": st.column_config.TextColumn("Eingabezeit"),
                "Prozent": st.column_config.TextColumn("Erfolg")
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gesamtstatistik
    if total_possible > 0:
        percentage = (total_correct / total_possible * 100)
        
        st.markdown("### 📈 Gesamtstatistik")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Gesamt korrekt", 
                f"{total_correct}/{total_possible}",
                delta=f"{percentage:.1f}%"
            )
        
        with col2:
            avg_percentage = percentage
            st.metric(
                "Durchschnittliche Trefferquote",
                f"{avg_percentage:.1f}%"
            )
        
        with col3:
            variant_name = "Farbig" if st.session_state.test_state['variant'] == "color" else "Farblos"
            st.metric(
                "Testvariante",
                variant_name
            )
        
        with col4:
            avg_time = "-"
            if st.session_state.test_state['merk_times']:
                avg_merk = sum(st.session_state.test_state['merk_times']) / len(st.session_state.test_state['merk_times'])
                avg_time = f"{avg_merk:.1f}s"
            st.metric(
                "⏱️ Durchschn. Merkzeit",
                avg_time
            )
    
    # Download-Link für Ergebnisse
    if hasattr(st.session_state, 'saved_path'):
        st.markdown("---")
        st.info(f"📁 Ihre Ergebnisse wurden gespeichert unter: `{st.session_state.saved_path}`")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Neuen Test beginnen", type="primary", use_container_width=True):
            # Session State zurücksetzen
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    main()
