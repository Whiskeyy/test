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
from streamlit_autorefresh import st_autorefresh

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
MEMORY_LIMIT_SECONDS = 30  # 30 Sekunden

# UI styling
ACCENT = "#4B7CDA"
ACCENT_LIGHT = "#e8f0ff"
SECONDARY = "#28a745"

# -----------------------
# Hilfsfunktionen
# -----------------------
def safe_upper_alpha(s):
    return "".join(ch for ch in s if ch.isalpha()).upper()

def create_shape_image(shape, color, size=80, variant="color", selected=False):
    """Erstellt ein Bild eines Symbols mit optionaler Hervorhebung"""
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    is_hollow = shape.endswith("_h")
    draw_color = "black" if variant == "bw" else color
    
    # Farbe für PIL konvertieren
    color_map = {
        "red": (255, 0, 0), "blue": (0, 0, 255), "green": (0, 128, 0),
        "orange": (255, 165, 0), "purple": (128, 0, 128), "brown": (165, 42, 42),
        "cyan": (0, 255, 255), "magenta": (255, 0, 255), "gold": (255, 215, 0),
        "darkgreen": (0, 100, 0), "darkblue": (0, 0, 139), "black": (0, 0, 0)
    }
    
    outline_color = color_map.get(draw_color, (0, 0, 0))
    fill_color = (255, 255, 255) if is_hollow else outline_color
    
    # Wenn ausgewählt, Hintergrund hervorheben
    if selected:
        # Hintergrundkreis für Hervorhebung
        bg_size = size + 8
        bg_img = Image.new('RGBA', (bg_size, bg_size), (255, 255, 255, 0))
        bg_draw = ImageDraw.Draw(bg_img)
        bg_draw.ellipse([4, 4, bg_size-4, bg_size-4], fill=(72, 124, 218, 30), outline=(72, 124, 218, 100), width=2)
        # Originalbild auf Hintergrund zeichnen
        offset = ((bg_size - size) // 2, (bg_size - size) // 2)
        bg_img.paste(img, offset, img)
        img = bg_img
        size = bg_size
        line_width = 4 if is_hollow else 3
    else:
        line_width = 3 if is_hollow else 2
    
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
    """Konvertiert PIL Image zu Base64"""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# -----------------------
# Streamlit App
# -----------------------
def main():
    # Set page config
    st.set_page_config(
        page_title="Memory Test Studie",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # CSS für modernes Aussehen
    st.markdown(f"""
    <style>
    /* Hauptstile */
    .main {{
        padding: 2rem;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: {ACCENT};
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 12px 24px;
        transition: all 0.3s ease;
        font-size: 16px;
    }}
    
    .stButton > button:hover {{
        background-color: #3a6bc5;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    .primary-button {{
        background-color: {SECONDARY} !important;
    }}
    
    .primary-button:hover {{
        background-color: #218838 !important;
    }}
    
    /* Titel */
    .main-title {{
        font-size: 42px;
        font-weight: 800;
        color: {ACCENT};
        text-align: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 3px solid {ACCENT};
        background: linear-gradient(135deg, {ACCENT}, #28a745);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .section-title {{
        font-size: 28px;
        font-weight: 700;
        color: #333;
        margin-top: 40px;
        margin-bottom: 25px;
        padding-left: 15px;
        border-left: 5px solid {ACCENT};
    }}
    
    .subsection-title {{
        font-size: 22px;
        font-weight: 600;
        color: #444;
        margin-top: 30px;
        margin-bottom: 20px;
    }}
    
    /* Boxen und Container */
    .info-card {{
        background: linear-gradient(145deg, #f8f9fa, #ffffff);
        padding: 30px;
        border-radius: 16px;
        margin-bottom: 30px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        transition: transform 0.3s ease;
    }}
    
    .info-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
    }}
    
    .question-card {{
        background: white;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 25px;
        border: 1px solid #e8e8e8;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    
    /* Symbol Container */
    .symbol-grid {{
        display: flex;
        justify-content: center;
        flex-wrap: wrap;
        gap: 20px;
        margin: 30px 0;
    }}
    
    .symbol-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid transparent;
        background: white;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    }}
    
    .symbol-container:hover {{
        border-color: {ACCENT};
        background-color: {ACCENT_LIGHT};
        transform: scale(1.05);
        box-shadow: 0 6px 15px rgba(72, 124, 218, 0.15);
    }}
    
    .symbol-container.selected {{
        border-color: {SECONDARY};
        background-color: #e8f5e9;
        box-shadow: 0 6px 15px rgba(40, 167, 69, 0.2);
    }}
    
    .symbol-number {{
        font-size: 20px;
        font-weight: bold;
        color: {ACCENT};
        margin-bottom: 10px;
    }}
    
    /* Timer */
    .timer-container {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 16px;
        margin: 30px 0;
        text-align: center;
        color: white;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }}
    
    .timer-text {{
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
    }}
    
    .timer-label {{
        font-size: 18px;
        opacity: 0.9;
    }}
    
    /* Radio Buttons */
    .radio-scale-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 25px 0;
        gap: 5px;
    }}
    
    .radio-label-left {{
        font-size: 16px;
        color: #666;
        text-align: right;
        min-width: 150px;
        padding-right: 20px;
        font-weight: 500;
    }}
    
    .radio-label-right {{
        font-size: 16px;
        color: #666;
        text-align: left;
        min-width: 150px;
        padding-left: 20px;
        font-weight: 500;
    }}
    
    .radio-option {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 10px 5px;
    }}
    
    .radio-number {{
        font-size: 18px;
        font-weight: 600;
        color: #333;
        margin-bottom: 5px;
    }}
    
    /* Eingabefelder */
    .stTextInput input, .stTextArea textarea {{
        border-radius: 10px !important;
        border: 2px solid #ddd !important;
        padding: 12px !important;
        font-size: 16px !important;
    }}
    
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {ACCENT} !important;
        box-shadow: 0 0 0 3px rgba(72, 124, 218, 0.2) !important;
    }}
    
    /* Progress Bar */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {ACCENT}, {SECONDARY});
    }}
    
    /* Ergebnisse Tabelle */
    .results-table-container {{
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin: 30px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, #f8f9fa, #ffffff);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #e0e0e0;
    }}
    
    /* Responsive Anpassungen */
    @media (max-width: 768px) {{
        .main-title {{
            font-size: 32px;
        }}
        
        .section-title {{
            font-size: 24px;
        }}
        
        .symbol-container {{
            padding: 15px;
        }}
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: #f1f1f1;
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {ACCENT};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: #3a6bc5;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Session State initialisieren
    init_session_state()
    
    # Auto-Refresh für Timer
    if st.session_state.get('timer_active', False):
        st_autorefresh(interval=100, limit=None, key="timer_refresh")
    
    # Seitensteuerung
    page_handlers = {
        'start': show_start_page,
        'instructions': show_instructions_page,
        'test': show_test_page,
        'questionnaire_intro': show_questionnaire_intro,
        'questionnaire_a': show_questionnaire_a,
        'questionnaire_b': show_questionnaire_b,
        'thank_you': show_thank_you_page
    }
    
    current_page = st.session_state.get('page', 'start')
    if current_page in page_handlers:
        page_handlers[current_page]()
    else:
        show_start_page()

def init_session_state():
    """Initialisiert den Session State"""
    defaults = {
        'page': 'start',
        'participant_data': {},
        'test_state': {
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
            'timer_start': None,
            'timer_end': None
        },
        'questionnaire_answers': [0] * 7,
        'questionnaire_text': "",
        'timer_active': False,
        'q_responses_a': [0] * 4,
        'q_responses_b': [0] * 3
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def show_start_page():
    st.markdown('<div class="main-title">🧠 Memory Test Studie</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="info-card">
        <h2 style="color: #333; margin-top: 0;">Willkommen zur wissenschaftlichen Studie</h2>
        <p style="font-size: 18px; line-height: 1.6; color: #555;">
        Diese Studie untersucht das visuelle Gedächtnis mit verschiedenen Symbolen. 
        Ihre Teilnahme hilft uns, die kognitiven Prozesse beim Erinnern von Sequenzen besser zu verstehen.
        </p>
        
        <div style="background: #e8f0ff; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4 style="color: #4B7CDA; margin-top: 0;">📋 Was Sie wissen sollten:</h4>
        <ul style="color: #555;">
            <li>Die Studie dauert etwa 10-15 Minuten</li>
            <li>Alle Daten werden <strong>anonym</strong> und vertraulich behandelt</li>
            <li>Sie können jederzeit pausieren oder abbrechen</li>
            <li>Es gibt keine richtigen oder falschen Antworten</li>
        </ul>
        </div>
        
        <p style="font-size: 16px; color: #666;">
        Bitte füllen Sie die folgenden Felder aus, damit wir eine anonyme Teilnehmer-ID generieren können.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    with st.form("participant_form"):
        st.markdown('<div class="subsection-title">Persönliche Informationen</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            mother = st.text_input(
                "**Erste zwei Buchstaben des Vornamens Ihrer Mutter:**",
                placeholder="z.B. MA für Maria",
                help="Nur Buchstaben, keine Zahlen oder Sonderzeichen"
            )
            
            father = st.text_input(
                "**Letzte zwei Buchstaben des Vornamens Ihres Vaters:**",
                placeholder="z.B. RT für Robert",
                help="Nur Buchstaben, keine Zahlen oder Sonderzeichen"
            )
        
        with col2:
            birthyear = st.text_input(
                "**Ihr Geburtsjahr:**",
                placeholder="1990",
                max_chars=4,
                help="Bitte im Format YYYY eingeben"
            )
            
            age = st.text_input(
                "**Ihr aktuelles Alter:**",
                placeholder="25",
                max_chars=3,
                help="In vollen Jahren"
            )
            
            st.markdown("**Geschlecht:**")
            gender = st.radio(
                "",
                ["Männlich", "Weiblich", "Divers"],
                horizontal=True,
                label_visibility="collapsed"
            )
            gender_code = {"Männlich": "M", "Weiblich": "W", "Divers": "D"}[gender]
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Studie beginnen",
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            # Validierung
            errors = []
            
            mother_clean = safe_upper_alpha(mother.strip())
            father_clean = safe_upper_alpha(father.strip())
            
            if len(mother_clean) < 2:
                errors.append("❌ Der Vorname Ihrer Mutter muss mindestens 2 Buchstaben enthalten.")
            if len(father_clean) < 2:
                errors.append("❌ Der Vorname Ihres Vaters muss mindestens 2 Buchstaben enthalten.")
            if not (birthyear.isdigit() and len(birthyear) == 4):
                errors.append("❌ Das Geburtsjahr muss 4-stellig sein (z.B. 1990).")
            if not (age.isdigit() and 0 < int(age) < 130):
                errors.append("❌ Bitte geben Sie ein gültiges Alter ein.")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Daten speichern
                participant_id = f"{mother_clean[:2]}{father_clean[-2:]}{birthyear}"
                st.session_state.participant_data = {
                    'id': participant_id,
                    'age': int(age),
                    'gender': gender_code
                }
                
                # Zufällige Testvariante wählen
                variant = random.choice(["color", "bw"])
                st.session_state.test_state = {
                    'variant': variant,
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
                    'timer_start': None,
                    'timer_end': None
                }
                
                # Session State für Fragebogen zurücksetzen
                st.session_state.questionnaire_answers = [0] * 7
                st.session_state.questionnaire_text = ""
                st.session_state.q_responses_a = [0] * 4
                st.session_state.q_responses_b = [0] * 3
                
                # Zur nächsten Seite
                st.session_state.page = 'instructions'
                st.rerun()

def show_instructions_page():
    st.markdown('<div class="main-title">📋 Testanleitung</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="info-card">
        <h2 style="color: #333; margin-top: 0;">So funktioniert der Test</h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin: 30px 0;">
            <div style="background: #f0f7ff; padding: 20px; border-radius: 10px;">
                <h3 style="color: #4B7CDA;">🎯 Phase 1: Merkphase</h3>
                <p>Eine Sequenz von Symbolen wird gezeigt. Merken Sie sich die <strong>Reihenfolge</strong>.</p>
                <ul>
                    <li><strong>Zeit:</strong> Maximal 30 Sekunden</li>
                    <li>Sie können früher mit "Weiter" fortfahren</li>
                    <li>Konzentrieren Sie sich auf die Abfolge</li>
                </ul>
            </div>
            
            <div style="background: #f0fff4; padding: 20px; border-radius: 10px;">
                <h3 style="color: #28a745;">🎮 Phase 2: Eingabephase</h3>
                <p>Klicken Sie die Symbole in der <strong>gemerkten Reihenfolge</strong> an.</p>
                <ul>
                    <li>Klicken Sie die Symbole der Reihe nach</li>
                    <li>Korrektur durch "Zurücksetzen" möglich</li>
                    <li>Keine Zeitbegrenzung in dieser Phase</li>
                </ul>
            </div>
        </div>
        
        <div style="background: #fff8e1; padding: 20px; border-radius: 10px; margin: 20px 0;">
        <h4 style="color: #ff9800;">📊 Teststruktur</h4>
        <p>Sie absolvieren <strong>5 Tests</strong> mit steigender Schwierigkeit:</p>
        <div style="display: flex; justify-content: space-between; margin-top: 15px;">
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: #4B7CDA;">Test 1</div>
                <div style="font-size: 18px;">3 Symbole</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: #4B7CDA;">Test 2</div>
                <div style="font-size: 18px;">4 Symbole</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: #4B7CDA;">Test 3</div>
                <div style="font-size: 18px;">5 Symbole</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: #4B7CDA;">Test 4</div>
                <div style="font-size: 18px;">6 Symbole</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 24px; font-weight: bold; color: #4B7CDA;">Test 5</div>
                <div style="font-size: 18px;">7 Symbole</div>
            </div>
        </div>
        </div>
        
        <p style="text-align: center; font-size: 20px; font-weight: 600; color: #4B7CDA; margin-top: 30px;">
        🎯 Konzentrieren Sie sich und geben Sie Ihr Bestes!
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶️ Ersten Test beginnen", type="primary", use_container_width=True):
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
    st.markdown(f'<div class="main-title">Test {current_test + 1} von {len(TEST_SIZES)}</div>', unsafe_allow_html=True)
    
    progress = current_test / len(TEST_SIZES)
    st.progress(progress, text=f"Fortschritt: {current_test}/{len(TEST_SIZES)} Tests")
    
    # Timer für Memory Phase
    if test_state['memory_phase'] and test_state.get('timer_start'):
        elapsed = time.time() - test_state['timer_start']
        remaining = max(0, MEMORY_LIMIT_SECONDS - elapsed)
        
        if remaining <= 0:
            end_memory_phase()
            return
        
        # Timer anzeigen
        st.markdown(f"""
        <div class="timer-container">
            <div class="timer-text">⏱️ {int(remaining)} Sekunden</div>
            <div class="timer-label">verbleibende Merkzeit</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Fortschrittsbalken
        progress_percent = 1 - (remaining / MEMORY_LIMIT_SECONDS)
        st.progress(progress_percent)
    
    # Statusanzeige
    if test_state['memory_phase']:
        show_memory_phase(size)
    elif test_state['input_phase']:
        show_input_phase(size)

def start_test():
    test_state = st.session_state.test_state
    current_test = test_state['current_test']
    size = TEST_SIZES[current_test]
    
    # Neue Sequenz generieren
    test_state['sequence'] = random.sample(SHAPES, size)
    test_state['user_selections'] = []
    test_state['memory_phase'] = True
    test_state['input_phase'] = False
    test_state['test_started'] = True
    test_state['timer_start'] = time.time()
    test_state['timer_end'] = test_state['timer_start'] + MEMORY_LIMIT_SECONDS
    
    # Timer aktivieren
    st.session_state.timer_active = True
    
    st.rerun()

def show_memory_phase(size):
    test_state = st.session_state.test_state
    sequence = test_state['sequence']
    variant = test_state['variant']
    
    st.markdown(f'<div class="section-title">Merkphase: {size} Symbole</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
    <h3 style="color: #333; margin-top: 0;">🎯 Merken Sie sich diese Symbole in der richtigen Reihenfolge</h3>
    <p style="font-size: 16px; color: #666;">
    Betrachten Sie die Symbole von links nach rechts. Konzentrieren Sie sich auf Position und Aussehen jedes Symbols.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Symbole anzeigen
    st.markdown('<div class="symbol-grid">', unsafe_allow_html=True)
    
    cols = st.columns(len(sequence))
    for i, shape in enumerate(sequence):
        with cols[i]:
            color = COLORS[SHAPES.index(shape)]
            img = create_shape_image(shape, color, size=140, variant=variant)
            
            st.markdown(f"""
            <div class="symbol-container">
                <div class="symbol-number">Position {i+1}</div>
            """, unsafe_allow_html=True)
            
            st.image(img, use_column_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Buttons
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        if st.button("✅ Weiter zur Eingabe", type="primary", use_container_width=True):
            end_memory_phase()

def end_memory_phase():
    test_state = st.session_state.test_state
    
    # Merkzeit berechnen
    if test_state.get('timer_start'):
        merk_time = round(min(time.time() - test_state['timer_start'], MEMORY_LIMIT_SECONDS), 3)
        test_state['merk_times'].append(merk_time)
    
    # Zur Eingabephase wechseln
    test_state['memory_phase'] = False
    test_state['input_phase'] = True
    test_state['response_start'] = time.time()
    
    # Timer deaktivieren
    st.session_state.timer_active = False
    
    st.rerun()

def show_input_phase(size):
    test_state = st.session_state.test_state
    variant = test_state['variant']
    user_selections = test_state['user_selections']
    
    st.markdown(f'<div class="section-title">Eingabephase: {size} Symbole</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
    <h3 style="color: #333; margin-top: 0;">🎮 Klicken Sie die Symbole in der gemerkten Reihenfolge</h3>
    <p style="font-size: 16px; color: #666;">
    Klicken Sie die Symbole <strong>der Reihe nach</strong> an. Ausgewählte Symbole werden hervorgehoben.
    </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Timer für Eingabephase
    if test_state.get('response_start'):
        elapsed = time.time() - test_state['response_start']
        col1, col2, col3 = st.columns(3)
        with col2:
            st.metric("⏱️ Eingabezeit", f"{elapsed:.1f} Sekunden")
    
    # Alle verfügbaren Symbole anzeigen
    st.markdown("### Verfügbare Symbole")
    
    # Erste Reihe
    cols1 = st.columns(8)
    for i in range(8):
        with cols1[i]:
            shape = SHAPES[i]
            color = COLORS[i]
            is_selected = shape in user_selections
            img = create_shape_image(shape, color, size=90, variant=variant, selected=is_selected)
            
            # Symbol anzeigen
            st.markdown(f'<div class="symbol-container {"selected" if is_selected else ""}">', unsafe_allow_html=True)
            
            # Button nur wenn nicht ausgewählt
            if not is_selected:
                if st.button("", key=f"shape1_{i}", help=shape):
                    if len(user_selections) < size:
                        test_state['user_selections'].append(shape)
                        st.rerun()
            
            st.image(img, use_column_width=True)
            
            # Symbol Status
            if is_selected:
                position = user_selections.index(shape) + 1
                st.markdown(f'<div style="color: {SECONDARY}; font-weight: bold;">✓ Position {position}</div>', unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Zweite Reihe
    cols2 = st.columns(8)
    for i in range(8, 16):
        with cols2[i-8]:
            shape = SHAPES[i]
            color = COLORS[i]
            is_selected = shape in user_selections
            img = create_shape_image(shape, color, size=90, variant=variant, selected=is_selected)
            
            # Symbol anzeigen
            st.markdown(f'<div class="symbol-container {"selected" if is_selected else ""}">', unsafe_allow_html=True)
            
            # Button nur wenn nicht ausgewählt
            if not is_selected:
                if st.button("", key=f"shape2_{i}", help=shape):
                    if len(user_selections) < size:
                        test_state['user_selections'].append(shape)
                        st.rerun()
            
            st.image(img, use_column_width=True)
            
            # Symbol Status
            if is_selected:
                position = user_selections.index(shape) + 1
                st.markdown(f'<div style="color: {SECONDARY}; font-weight: bold;">✓ Position {position}</div>', unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Ausgewählte Reihenfolge anzeigen
    if user_selections:
        st.markdown("### Ihre gewählte Reihenfolge")
        
        selected_cols = st.columns(len(user_selections))
        for i, shape in enumerate(user_selections):
            with selected_cols[i]:
                color = COLORS[SHAPES.index(shape)]
                img = create_shape_image(shape, color, size=100, variant=variant, selected=True)
                
                st.markdown(f"""
                <div style="text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                    <div style="font-size: 20px; font-weight: bold; color: {ACCENT}; margin-bottom: 10px;">
                        Position {i+1}
                    </div>
                """, unsafe_allow_html=True)
                
                st.image(img, use_column_width=True)
                
                # Korrektur anzeigen
                if i < len(test_state['sequence']):
                    if shape == test_state['sequence'][i]:
                        st.markdown(f'<div style="color: {SECONDARY}; font-weight: bold;">✓ Korrekt</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div style="color: #dc3545;">✗ Erwartet: {test_state["sequence"][i]}</div>', unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Auswahl zurücksetzen", use_container_width=True):
            test_state['user_selections'] = []
            st.rerun()
    
    with col2:
        if st.button("⏭️ Test überspringen", use_container_width=True):
            test_state['user_selections'] = []
            finish_test()
    
    with col3:
        if st.button("✅ Eingabe bestätigen", type="primary", use_container_width=True, disabled=len(user_selections) < size):
            if len(user_selections) == size:
                finish_test()
    
    # Automatische Überprüfung wenn alle ausgewählt
    if len(user_selections) == size:
        st.info(f"Alle {size} Symbole ausgewählt. Bitte bestätigen Sie Ihre Eingabe.")

def finish_test():
    test_state = st.session_state.test_state
    
    # Reaktionszeit speichern
    if test_state.get('response_start'):
        response_time = round(time.time() - test_state['response_start'], 3)
        test_state['response_times'].append(response_time)
    
    # Korrekte Antworten zählen
    correct = 0
    min_length = min(len(test_state['user_selections']), len(test_state['sequence']))
    for i in range(min_length):
        if test_state['user_selections'][i] == test_state['sequence'][i]:
            correct += 1
    
    test_state['correct_counts'].append(correct)
    
    # Feedback anzeigen
    size = TEST_SIZES[test_state['current_test']]
    if correct == size:
        st.success(f"🎉 Perfekt! Alle {correct} von {size} Symbolen korrekt!")
    else:
        st.info(f"Ergebnis: {correct} von {size} Symbolen korrekt ({correct/size*100:.0f}%)")
    
    # Zum nächsten Test
    test_state['current_test'] += 1
    test_state['test_started'] = False
    
    # Kurze Pause
    time.sleep(2)
    st.rerun()

def show_questionnaire_intro():
    st.markdown('<div class="main-title">📝 Fragebogen</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="info-card">
        <h2 style="color: #333; margin-top: 0;">Herzlichen Glückwunsch zum Testabschluss! 🎊</h2>
        
        <p style="font-size: 18px; line-height: 1.6; color: #555;">
        Sie haben alle Memory-Tests erfolgreich absolviert. Im letzten Teil der Studie möchten wir 
        gerne mehr über Ihre persönliche Erfahrung während der Tests erfahren.
        </p>
        
        <div style="background: #e8f0ff; padding: 25px; border-radius: 12px; margin: 25px 0;">
        <h3 style="color: #4B7CDA; margin-top: 0;">📊 Bewertungsskala</h3>
        <p>Bitte bewerten Sie auf einer Skala von <strong>1 bis 7</strong>:</p>
        
        <div style="display: flex; justify-content: center; align-items: center; margin: 20px 0; gap: 30px;">
            <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; min-width: 150px;">
                <div style="font-size: 24px; font-weight: bold; color: #dc3545;">1</div>
                <div style="font-size: 14px; color: #666;">stimme nicht zu</div>
            </div>
            
            <div style="font-size: 18px; color: #666;">→</div>
            
            <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; min-width: 150px;">
                <div style="font-size: 24px; font-weight: bold; color: {SECONDARY};">7</div>
                <div style="font-size: 14px; color: #666;">stimme voll zu</div>
            </div>
        </div>
        
        <p style="text-align: center; font-style: italic; color: #666;">
        Wählen Sie für jede Aussage den Wert, der am besten Ihre Erfahrung beschreibt.
        </p>
        </div>
        
        <p style="font-size: 16px; color: #666;">
        <strong>Hinweis:</strong> Es gibt keine richtigen oder falschen Antworten. Ihre ehrliche Einschätzung 
        hilft uns, die Tests zu verbessern.
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📋 Fragebogen starten", type="primary", use_container_width=True):
            st.session_state.page = 'questionnaire_a'
            st.rerun()

def show_questionnaire_a():
    st.markdown('<div class="main-title">Teil A: Subjektive Performance</div>', unsafe_allow_html=True)
    
    questions = [
        "1. Das Bearbeiten des Tests fiel mir leicht",
        "2. Ich musste mich sehr konzentrieren um mir die Informationen zu merken.",
        "3. Ich hatte Schwierigkeiten mir mehrere Informationen gleichzeitig zu merken.",
        "4. Ich hatte Spaß an der Bearbeitung des Tests"
    ]
    
    # Fragebogen als Formular
    with st.form("questionnaire_form_a"):
        for i, question in enumerate(questions):
            st.markdown(f'<div class="question-card"><h3>{question}</h3></div>', unsafe_allow_html=True)
            
            # Radio Buttons mit Skala 1-7
            st.markdown('<div class="radio-scale-container">', unsafe_allow_html=True)
            
            # Linkes Label
            st.markdown('<div class="radio-label-left">stimme nicht zu</div>', unsafe_allow_html=True)
            
            # Radio Buttons
            cols = st.columns(7)
            for j in range(7):
                with cols[j]:
                    value = j + 1
                    # Verwende st.radio für bessere Kontrolle
                    if st.radio(
                        f"Q{i+1}",
                        options=[value],
                        key=f"q_a_{i}_{j}",
                        label_visibility="collapsed",
                        horizontal=True
                    ):
                        st.session_state.q_responses_a[i] = value
            
            # Rechtes Label
            st.markdown('<div class="radio-label-right">stimme voll zu</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Aktuelle Auswahl anzeigen
            current_value = st.session_state.q_responses_a[i]
            if current_value > 0:
                st.markdown(f"""
                <div style="text-align: center; margin: 10px 0; padding: 10px; background: #f0f7ff; border-radius: 8px;">
                    <span style="font-weight: bold; color: {ACCENT};">Ausgewählter Wert: {current_value}</span>
                </div>
                """, unsafe_allow_html=True)
            
            if i < len(questions) - 1:
                st.markdown("---")
        
        # Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("⬅️ Zurück zur Einleitung", use_container_width=True):
                st.session_state.page = 'questionnaire_intro'
                st.rerun()
        with col2:
            if st.form_submit_button("Weiter zu Teil B ➡️", type="primary", use_container_width=True):
                # Alle Fragen beantwortet?
                if all(v > 0 for v in st.session_state.q_responses_a):
                    # Antworten speichern
                    for i in range(4):
                        st.session_state.questionnaire_answers[i] = st.session_state.q_responses_a[i]
                    
                    st.session_state.page = 'questionnaire_b'
                    st.rerun()
                else:
                    st.error("Bitte beantworten Sie alle Fragen, bevor Sie fortfahren.")

def show_questionnaire_b():
    st.markdown('<div class="main-title">Teil B: Weitere Einschätzung</div>', unsafe_allow_html=True)
    
    questions = [
        "5. Ich bin mit meiner Leistung im Test zufrieden",
        "6. Ich habe die korrekten Reihenfolgen reproduziert.",
        "7. Ich kann mir die angezeigte Reihenfolge für eine lange Zeit merken."
    ]
    
    # Fragebogen als Formular
    with st.form("questionnaire_form_b"):
        for i, question in enumerate(questions):
            st.markdown(f'<div class="question-card"><h3>{question}</h3></div>', unsafe_allow_html=True)
            
            # Radio Buttons mit Skala 1-7
            st.markdown('<div class="radio-scale-container">', unsafe_allow_html=True)
            
            # Linkes Label
            st.markdown('<div class="radio-label-left">stimme nicht zu</div>', unsafe_allow_html=True)
            
            # Radio Buttons
            cols = st.columns(7)
            for j in range(7):
                with cols[j]:
                    value = j + 1
                    # Verwende st.radio für bessere Kontrolle
                    if st.radio(
                        f"Q{i+5}",
                        options=[value],
                        key=f"q_b_{i}_{j}",
                        label_visibility="collapsed",
                        horizontal=True
                    ):
                        st.session_state.q_responses_b[i] = value
            
            # Rechtes Label
            st.markdown('<div class="radio-label-right">stimme voll zu</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Aktuelle Auswahl anzeigen
            current_value = st.session_state.q_responses_b[i]
            if current_value > 0:
                st.markdown(f"""
                <div style="text-align: center; margin: 10px 0; padding: 10px; background: #f0f7ff; border-radius: 8px;">
                    <span style="font-weight: bold; color: {ACCENT};">Ausgewählter Wert: {current_value}</span>
                </div>
                """, unsafe_allow_html=True)
            
            if i < len(questions) - 1:
                st.markdown("---")
        
        # Freitext Frage
        st.markdown(f'<div class="question-card"><h3>8. Haben Sie eine Merkhilfe/Gedächtnisbrücke/Tricks verwendet?</h3></div>', unsafe_allow_html=True)
        
        free_text = st.text_area(
            "Wenn ja, beschreiben Sie bitte kurz Ihre Strategie:",
            height=150,
            placeholder="Beispiele: 'Ich habe mir eine Geschichte zu den Symbolen ausgedacht', 'Ich habe die Symbole in Gruppen eingeteilt', 'Ich habe die Positionen gezählt', etc.\n\nWenn Sie keine spezielle Strategie verwendet haben, lassen Sie das Feld einfach frei.",
            help="Ihre Antwort hilft uns, die kognitiven Strategien der Teilnehmer besser zu verstehen."
        )
        
        st.markdown("---")
        
        # Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("⬅️ Zurück zu Teil A", use_container_width=True):
                st.session_state.page = 'questionnaire_a'
                st.rerun()
        with col2:
            if st.form_submit_button("✅ Fragebogen abschließen", type="primary", use_container_width=True):
                # Alle Fragen beantwortet?
                if all(v > 0 for v in st.session_state.q_responses_b):
                    # Antworten speichern
                    for i in range(3):
                        st.session_state.questionnaire_answers[i+4] = st.session_state.q_responses_b[i]
                    
                    st.session_state.questionnaire_text = free_text
                    
                    # Ergebnisse speichern
                    if save_results():
                        st.session_state.page = 'thank_you'
                        st.rerun()
                else:
                    st.error("Bitte beantworten Sie alle Fragen, bevor Sie den Fragebogen abschließen.")

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
        
        # Für jeden Test
        for i in range(len(TEST_SIZES)):
            test_data[f"Test_{i+1}_Symbole"] = [TEST_SIZES[i]]
            
            if i < len(st.session_state.test_state['merk_times']):
                test_data[f"Test_{i+1}_Merkzeit"] = [st.session_state.test_state['merk_times'][i]]
            else:
                test_data[f"Test_{i+1}_Merkzeit"] = [""]
                
            if i < len(st.session_state.test_state['response_times']):
                test_data[f"Test_{i+1}_Eingabezeit"] = [st.session_state.test_state['response_times'][i]]
            else:
                test_data[f"Test_{i+1}_Eingabezeit"] = [""]
                
            if i < len(st.session_state.test_state['correct_counts']):
                test_data[f"Test_{i+1}_Korrekt"] = [st.session_state.test_state['correct_counts'][i]]
            else:
                test_data[f"Test_{i+1}_Korrekt"] = [""]
        
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
        
        # Excel-Datei speichern
        excel_file = "memorytest_results.xlsx"
        
        if os.path.exists(excel_file):
            with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                sheet_name = "FARBIG" if st.session_state.test_state['variant'] == "color" else "FARBLOS"
                
                # Prüfen ob Sheet existiert
                if sheet_name in writer.book.sheetnames:
                    startrow = writer.book[sheet_name].max_row
                else:
                    startrow = 0
                    writer.book.create_sheet(sheet_name)
                
                # Test-Ergebnisse schreiben
                df_test.to_excel(
                    writer, 
                    sheet_name=sheet_name, 
                    index=False, 
                    header=(startrow == 0),
                    startrow=startrow
                )
                
                # QUESTIONNAIRE Sheet
                if "QUESTIONNAIRE" in writer.book.sheetnames:
                    startrow_q = writer.book["QUESTIONNAIRE"].max_row
                else:
                    startrow_q = 0
                    writer.book.create_sheet("QUESTIONNAIRE")
                
                df_questionnaire.to_excel(
                    writer,
                    sheet_name="QUESTIONNAIRE",
                    index=False,
                    header=(startrow_q == 0),
                    startrow=startrow_q
                )
                
                writer.save()
        else:
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                sheet_name = "FARBIG" if st.session_state.test_state['variant'] == "color" else "FARBLOS"
                df_test.to_excel(writer, sheet_name=sheet_name, index=False)
                df_questionnaire.to_excel(writer, sheet_name="QUESTIONNAIRE", index=False)
        
        st.session_state.saved_path = os.path.abspath(excel_file)
        return True
        
    except Exception as e:
        st.error(f"Fehler beim Speichern: {str(e)}")
        return False

def show_thank_you_page():
    st.markdown('<div class="main-title">🎉 Studie abgeschlossen!</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="info-card">
        <h2 style="color: #333; margin-top: 0;">Vielen Dank für Ihre Teilnahme! 🙏</h2>
        
        <p style="font-size: 18px; line-height: 1.6; color: #555;">
        Ihre Daten wurden erfolgreich gespeichert und werden einen wertvollen Beitrag zu unserer 
        Forschung über visuelles Gedächtnis leisten.
        </p>
        
        <div style="background: #e8f5e9; padding: 25px; border-radius: 12px; margin: 25px 0;">
        <h3 style="color: {SECONDARY}; margin-top: 0;">📊 Ihre persönliche Auswertung</h3>
        <p>Hier sehen Sie eine Zusammenfassung Ihrer Leistung in den Memory-Tests:</p>
        </div>
        </div>
        """.format(SECONDARY=SECONDARY), unsafe_allow_html=True)
    
    # Ergebnisse anzeigen
    test_state = st.session_state.test_state
    
    if test_state['correct_counts']:
        st.markdown('<div class="results-table-container">', unsafe_allow_html=True)
        
        results_data = []
        total_correct = 0
        total_possible = 0
        
        for i in range(len(TEST_SIZES)):
            if i < len(test_state['correct_counts']):
                correct = test_state['correct_counts'][i]
                size = TEST_SIZES[i]
                total_correct += correct
                total_possible += size
                
                percentage = (correct / size * 100) if size > 0 else 0
                
                merk_time = "-"
                if i < len(test_state['merk_times']):
                    merk_time = f"{test_state['merk_times'][i]:.1f}s"
                
                response_time = "-"
                if i < len(test_state['response_times']):
                    response_time = f"{test_state['response_times'][i]:.1f}s"
                
                results_data.append({
                    'Test': i + 1,
                    'Symbole': size,
                    'Korrekt': correct,
                    'Erfolgsrate': f"{percentage:.1f}%",
                    'Merkzeit': merk_time,
                    'Eingabezeit': response_time
                })
        
        # Tabelle anzeigen
        if results_data:
            df_results = pd.DataFrame(results_data)
            
            # Spalten konfigurieren
            column_config = {
                'Test': st.column_config.NumberColumn('Test', width='small'),
                'Symbole': st.column_config.NumberColumn('Symbole', width='small'),
                'Korrekt': st.column_config.NumberColumn('Korrekt', width='small'),
                'Erfolgsrate': st.column_config.ProgressColumn(
                    'Erfolgsrate',
                    format='%.1f%%',
                    min_value=0,
                    max_value=100,
                    width='medium'
                ),
                'Merkzeit': st.column_config.TextColumn('Merkzeit'),
                'Eingabezeit': st.column_config.TextColumn('Eingabezeit')
            }
            
            st.dataframe(
                df_results,
                use_container_width=True,
                hide_index=True,
                column_config=column_config
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Metriken
        if total_possible > 0:
            overall_percentage = (total_correct / total_possible * 100)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold; color: #333;">{}</div>
                    <div style="color: #666;">Gesamt korrekt</div>
                </div>
                """.format(f"{total_correct}/{total_possible}"), unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold; color: {SECONDARY};">{overall_percentage:.1f}%</div>
                    <div style="color: #666;">Gesamterfolgsrate</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                variant_name = "Farbig" if test_state['variant'] == "color" else "Farblos"
                variant_color = ACCENT if test_state['variant'] == "color" else "#666"
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold; color: {variant_color};">{variant_name}</div>
                    <div style="color: #666;">Testvariante</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_merk_time = "-"
                if test_state['merk_times']:
                    avg_merk = sum(test_state['merk_times']) / len(test_state['merk_times'])
                    avg_merk_time = f"{avg_merk:.1f}s"
                
                st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 24px; font-weight: bold; color: #ff9800;">{avg_merk_time}</div>
                    <div style="color: #666;">Durchschn. Merkzeit</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Abschluss
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; padding: 30px;">
        <h3 style="color: #333;">🎯 Ihre Teilnahme war erfolgreich!</h3>
        <p style="font-size: 16px; color: #666; max-width: 600px; margin: 0 auto;">
        Die Studie ist nun abgeschlossen. Sie können diese Seite schließen oder einen neuen Test starten.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Neuen Test starten", type="primary", use_container_width=True):
            # Session State zurücksetzen
            keys_to_keep = []
            for key in list(st.session_state.keys()):
                if key not in keys_to_keep:
                    del st.session_state[key]
            st.rerun()

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    main()
