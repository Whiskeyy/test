import streamlit as st
import random
import time
import os
import csv
from datetime import datetime

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

CSV_RESULTS = "memorytest_results.csv"
CSV_QUESTIONNAIRE = "questionnaire_results.csv"

st.set_page_config(page_title="Memory Test", layout="wide")

def safe_upper_alpha(s):
    return "".join(ch for ch in s if ch.isalpha()).upper()

# --------------------------
# SVG Renderer (wie zuvor)
# --------------------------
def svg_for_shape(shape, size_px=80, fill="white", stroke="black", stroke_width=2, gray=False):
    s = size_px
    viewbox = "0 0 100 100"
    if gray:
        fill = "#BBBBBB"
        stroke = "#D3D3D3"
    is_hollow = shape.endswith("_h")
    if is_hollow:
        fill_color = "white" if not gray else fill
        stroke_color = stroke
    else:
        fill_color = fill
        stroke_color = stroke

    def poly(pts):
        return f'<polygon points="{" ".join([f"{x},{y}" for x,y in pts])}" fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}" />'

    # ---- shapes (identisch wie vorher) ----
    if shape.startswith("Kreis"):
        body = f'<circle cx="50" cy="50" r="40" fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}" />'
    elif shape.startswith("Quadrat"):
        body = f'<rect x="12" y="12" width="76" height="76" fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}" />'
    elif shape.startswith("Raute"):
        body = poly([(50,8),(88,50),(50,92),(12,50)])
    elif shape.startswith("Stern"):
        body = poly([(50,12),(58,34),(80,34),(62,50),
                     (68,74),(50,60),(32,74),(38,50),
                     (20,34),(42,34)])
    elif shape.startswith("Dreieck"):
        body = poly([(50,10),(90,80),(10,80)])
    elif shape == "PfeilOben":
        body = poly([(50,10),(78,50),(62,50),(62,90),(38,90),(38,50),(22,50)])
    elif shape == "PfeilUnten":
        body = poly([(50,90),(78,50),(62,50),(62,10),(38,10),(38,50),(22,50)])
    elif shape == "PfeilLinks":
        body = poly([(10,50),(50,10),(50,30),(90,30),(90,70),(50,70),(50,90)])
    elif shape == "PfeilRechts":
        body = poly([(90,50),(50,10),(50,30),(10,30),(10,70),(50,70),(50,90)])
    elif shape == "Doppelpfeil_H":
        body = (
            f'<line x1="18" y1="50" x2="82" y2="50" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
            + poly([(18,50),(30,40),(30,60)])
            + poly([(82,50),(70,40),(70,60)])
        )
    elif shape == "Doppelpfeil_V":
        body = (
            f'<line x1="50" y1="18" x2="50" y2="82" stroke="{stroke_color}" stroke-width="{stroke_width}"/>'
            + poly([(50,18),(40,30),(60,30)])
            + poly([(50,82),(40,70),(60,70)])
        )
    else:
        body = f'<circle cx="50" cy="50" r="40" fill="{fill_color}" stroke="{stroke_color}" stroke-width="{stroke_width}" />'

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" width="{s}" height="{s}">{body}</svg>'

def show_svg(svg):
    st.markdown(svg, unsafe_allow_html=True)

# --------------------------
# CSV Speichern
# --------------------------
def append_csv(path, row, header=None):
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists and header:
            writer.writerow(header)
        writer.writerow(row)

# --------------------------
# Session State Init
# --------------------------
defaults = {
    "stage": "start",
    "mother_var": "",
    "father_var": "",
    "birthyear_var": "",
    "age_var": "",
    "gender_var": "M",
    "test_variant": None,
    "current_test_index": 0,
    "sequence": [],
    "user_selections": [],
    "clicked": {},
    "merk_times": [],
    "response_times": [],
    "correct_counts": [],
    "memory_start": None,
    "memory_active": False,
    "participant_id": "",
    "participant_age": None,
    "participant_gender": "",
    "q_vars": [0]*7,
    "q8_text": "",
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_all():
    for k,v in defaults.items():
        st.session_state[k] = v
    st.rerun()
# ------------------------------------------------------------
# UI — Start Screen
# ------------------------------------------------------------
st.title("Memory Test für Studie")

# ---------------------------
# START SCREEN
# ---------------------------
if st.session_state.stage == "start":
    st.write("Bitte beantworten Sie folgende Fragen, damit wir eine anonyme Teilnehmer-ID bilden können.")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state.mother_var = st.text_input(
            "Die ersten zwei Buchstaben des Vornamens Ihrer Mutter:",
            st.session_state.mother_var
        )
        st.session_state.father_var = st.text_input(
            "Die letzten beiden Buchstaben des Vornamens Ihres Vaters:",
            st.session_state.father_var
        )

    with col2:
        st.session_state.birthyear_var = st.text_input(
            "Ihr Geburtsjahr:", st.session_state.birthyear_var, max_chars=4
        )
        st.session_state.age_var = st.text_input(
            "Alter:", st.session_state.age_var, max_chars=3
        )
        st.session_state.gender_var = st.radio(
            "Geschlecht:", ["M","W","D"],
            index=["M","W","D"].index(st.session_state.gender_var)
        )

    if st.button("Test starten"):
        mother = safe_upper_alpha(st.session_state.mother_var.strip())
        father = safe_upper_alpha(st.session_state.father_var.strip())
        birth = st.session_state.birthyear_var.strip()
        age = st.session_state.age_var.strip()
        gender = st.session_state.gender_var.strip()

        error = None
        if len(mother) < 2:
            error = "Vorname der Mutter muss mindestens 2 Buchstaben enthalten."
        elif len(father) < 2:
            error = "Vorname des Vaters muss mindestens 2 Buchstaben enthalten."
        elif not (birth.isdigit() and len(birth) == 4):
            error = "Geburtsjahr muss 4-stellig sein."
        elif not (age.isdigit() and 1 <= int(age) <= 130):
            error = "Bitte gültiges Alter eingeben."

        if error:
            st.error(error)
        else:
            st.session_state.participant_id = f"{mother[:2]}{father[-2:]}{birth}"
            st.session_state.participant_age = int(age)
            st.session_state.participant_gender = gender
            st.session_state.test_variant = random.choice(["color", "bw"])
            st.session_state.stage = "instructions"
            st.rerun()


# ---------------------------
# INSTRUCTIONS
# ---------------------------
if st.session_state.stage == "instructions":
    st.subheader("Instruktionen")
    st.write("""
    Sie erhalten gleich eine Reihe von Symbolen.  
    Bitte merken Sie sich deren Reihenfolge.  
    Sie haben pro Merkphase **30 Sekunden**.

    Sie können die Merkphase auch früher beenden durch Klick auf  
    **„Weiter (Merkphase beenden)“**.

    Danach klicken Sie die Symbole in der Reihenfolge an, die Sie sich gemerkt haben.
    """)

    if st.button("Weiter"):
        st.session_state.stage = "memory"
        st.session_state.sequence = []
        st.session_state.user_selections = []
        st.session_state.clicked = {}
        st.rerun()


# ------------------------------------------------------------
# MERKPHASE
# ------------------------------------------------------------
def start_test_round():
    size = TEST_SIZES[st.session_state.current_test_index]
    st.session_state.sequence = random.sample(SHAPES, size)
    st.session_state.user_selections = []
    st.session_state.clicked = {}
    st.session_state.memory_start = time.time()
    st.session_state.memory_active = True


if st.session_state.stage == "memory":
    # Start automatically if needed
    if not st.session_state.sequence:
        start_test_round()

    # Header
    st.subheader(
        f"Test {st.session_state.current_test_index + 1}: "
        f"Merke dir die Reihenfolge ({len(st.session_state.sequence)} Symbole)"
    )

    # Timer + Progress
    elapsed = time.time() - st.session_state.memory_start
    remaining = max(0, MEMORY_LIMIT_MS/1000 - elapsed)
    progress = min(1.0, elapsed / (MEMORY_LIMIT_MS/1000))

    st.progress(progress)
    st.write(f"Verbleibende Zeit: {int(remaining)} s")

    # Show SVG sequence
    cols = st.columns(len(st.session_state.sequence))
    for i, shape in enumerate(st.session_state.sequence):
        color = COLORS[SHAPES.index(shape)]
        draw = "black" if st.session_state.test_variant == "bw" else color
        svg = svg_for_shape(shape, 100,
                            fill=draw if not shape.endswith("_h") else "white",
                            stroke=draw)
        with cols[i]:
            st.markdown(svg, unsafe_allow_html=True)

    # EARLY END BUTTON
    if st.button("Weiter (Merkphase beenden)"):
        merk = round(min(elapsed, MEMORY_LIMIT_MS/1000), 3)
        st.session_state.merk_times.append(merk)
        st.session_state.stage = "input"
        st.session_state.test_response_start = time.time()
        st.rerun()

    # AUTO-END after timeout
    if elapsed * 1000 >= MEMORY_LIMIT_MS:
        merk = round(MEMORY_LIMIT_MS/1000, 3)
        st.session_state.merk_times.append(merk)
        st.session_state.stage = "input"
        st.session_state.test_response_start = time.time()
        st.rerun()

    # AUTO REFRESH during memory phase
    st.markdown('<meta http-equiv="refresh" content="0.7">', unsafe_allow_html=True)


# ------------------------------------------------------------
# EINGABEPHASE
# ------------------------------------------------------------
if st.session_state.stage == "input":
    st.subheader("Eingabephase: Klicke die Symbole in der richtigen Reihenfolge.")

    cols = st.columns(8)
    for i, shape in enumerate(SHAPES):
        col = cols[i % 8]
        clicked = st.session_state.clicked.get(shape, False)
        color = COLORS[i]
        draw = "black" if st.session_state.test_variant == "bw" else color

        svg = svg_for_shape(
            shape, size_px=80,
            fill=draw if not shape.endswith("_h") else "white",
            stroke=draw,
            gray=clicked
        )

        with col:
            st.markdown(svg, unsafe_allow_html=True)
            if not clicked:
                if st.button("Auswählen", key=f"sel_{shape}_{st.session_state.current_test_index}"):
                    st.session_state.user_selections.append(shape)
                    st.session_state.clicked[shape] = True

                    # Round finished?
                    if len(st.session_state.user_selections) == len(st.session_state.sequence):
                        resp = round(time.time() - st.session_state.test_response_start, 3)
                        st.session_state.response_times.append(resp)

                        correct = sum(
                            1 for a,b in zip(st.session_state.user_selections,
                                             st.session_state.sequence)
                            if a == b
                        )
                        st.session_state.correct_counts.append(correct)

                        st.session_state.current_test_index += 1

                        # Next test?
                        if st.session_state.current_test_index < len(TEST_SIZES):
                            st.session_state.stage = "memory"
                            st.session_state.sequence = []
                            st.session_state.user_selections = []
                            st.session_state.clicked = {}
                            st.rerun()
                        else:
                            # All tests done → Questionnaire
                            st.session_state.stage = "q_a"
                            st.rerun()
                    else:
                        st.rerun()
            else:
                st.button("Ausgewählt", disabled=True)

    # Reset Button
    st.write("---")
    if st.button("Reset / Startmenü"):
        reset_all()
# ------------------------------------------------------------
# FRAGEBOGEN TEIL A
# ------------------------------------------------------------
if st.session_state.stage == "q_a":
    st.header("Selbsteinschätzung — Teil A")
    st.write("Bitte bewerten Sie die folgenden Aussagen von 1 bis 7:")

    questions_a = [
        "1. Das Bearbeiten des Tests fiel mir leicht.",
        "2. Ich musste mich sehr konzentrieren, um mir die Informationen zu merken.",
        "3. Ich hatte Schwierigkeiten, mir mehrere Informationen gleichzeitig zu merken.",
        "4. Ich hatte Spaß an der Bearbeitung des Tests."
    ]

    for i, q in enumerate(questions_a):
        st.write(q)
        st.session_state.q_vars[i] = st.radio(
            f"q_a_{i}",
            [1,2,3,4,5,6,7],
            index=(st.session_state.q_vars[i] - 1) if st.session_state.q_vars[i] else 3,
            horizontal=True
        )

    st.write("---")
    if st.button("Weiter zu Teil B"):
        st.session_state.stage = "q_b"
        st.rerun()


# ------------------------------------------------------------
# FRAGEBOGEN TEIL B
# ------------------------------------------------------------
if st.session_state.stage == "q_b":
    st.header("Selbsteinschätzung — Teil B")

    questions_b = [
        "5. Ich bin mit meiner Leistung im Test zufrieden.",
        "6. Ich habe die korrekten Reihenfolgen reproduziert.",
        "7. Ich kann mir die angezeigte Reihenfolge für eine lange Zeit merken."
    ]

    for j, q in enumerate(questions_b, start=4):
        st.write(q)
        st.session_state.q_vars[j] = st.radio(
            f"q_b_{j}",
            [1,2,3,4,5,6,7],
            index=(st.session_state.q_vars[j]-1) if st.session_state.q_vars[j] else 3,
            horizontal=True
        )

    st.write("8. Haben Sie eine Merkhilfe/Gedächtnisbrücke/Tricks verwendet?")
    st.session_state.q8_text = st.text_area("", st.session_state.q8_text, height=120)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Fragebogen abschicken"):

            # ------------------------
            # SPEICHERN IN CSV
            # ------------------------
            answers = st.session_state.q_vars.copy()
            free_text = st.session_state.q8_text

            header = [
                "participant_id",
                "test_variant"
            ] + [f"Q{i+1}" for i in range(7)] + ["Q8_text", "timestamp"]

            row = [
                st.session_state.participant_id,
                st.session_state.test_variant
            ] + answers + [
                free_text,
                datetime.now().isoformat(timespec="seconds")
            ]

            append_csv(CSV_QUESTIONNAIRE, row, header)

            st.session_state.stage = "done"
            st.rerun()

    with col2:
        if st.button("Zurück zu Teil A"):
            st.session_state.stage = "q_a"
            st.rerun()


# ------------------------------------------------------------
# ABSCHLUSSBILDSCHIRM + CSV-SPEICHERUNG DER TESTERGEBNISSE
# ------------------------------------------------------------
if st.session_state.stage == "done":
    st.header("Vielen Dank für Ihre Teilnahme!")
    st.write("Der Test und Fragebogen sind abgeschlossen.")

    # ------------------------
    # SPEICHERN DER TESTERGEBNISSE
    # ------------------------
    result_header = ["participant_id", "age", "gender", "test_variant"]

    for size in TEST_SIZES:
        result_header += [
            f"{size}_merkzeit",
            f"{size}_reaktionszeit",
            f"{size}_korrekt"
        ]

    row = [
        st.session_state.participant_id,
        st.session_state.participant_age,
        st.session_state.participant_gender,
        st.session_state.test_variant,
    ]

    for i, size in enumerate(TEST_SIZES):
        row += [
            st.session_state.merk_times[i] if i < len(st.session_state.merk_times) else "",
            st.session_state.response_times[i] if i < len(st.session_state.response_times) else "",
            st.session_state.correct_counts[i] if i < len(st.session_state.correct_counts) else ""
        ]

    append_csv(CSV_RESULTS, row, result_header)

    # ------------------------
    # ERGEBNISTABELLE
    # ------------------------
    st.subheader("Ihre Ergebnisse")

    cols = st.columns(len(TEST_SIZES))
    for idx, size in enumerate(TEST_SIZES):
        with cols[idx]:
            st.write(f"**Test {idx+1}**")
            correct = st.session_state.correct_counts[idx]
            st.write(f"{correct}/{size}")

    st.write("---")
    if st.button("Zurück zum Start"):
        reset_all()
