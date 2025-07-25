#!/usr/bin/env python3
"""
grief_loop.py – 4‑Sensor / 5‑Printer Markov Grief Engine  (sensor‑only)
───────────────────────────────────────────────────────────────────────
• Sensors 0‑3  (GPIO17/18, 22/23, 24/25, 5/6)   → trigger other printers
• lp0‑lp3 print when *another* sensor fires
• lp4 has no sensor: it stays silent (can be used later)
• No periodic printing loop, so nothing prints unless a sensor fires.
"""

import re, sys, time
from pathlib import Path
from threading import Thread
import markovify
import RPi.GPIO as GPIO                              # pip install RPi.GPIO

# ───────────── USER SETTINGS ─────────────────────────────────────────── #
DEVICES = [f"/dev/usb/lp{i}" for i in range(5)]   # lp0‑lp4 (lp4 silent)
SENSOR_PINS = {                                  # idx : (TRIG, ECHO)
    0: (17, 18),
    1: (22, 23),
    2: (24, 25),
    3: (5, 6),
}

THRESH_CM          = 40
DEBOUNCE_SECONDS   = 3.0
WRITE_DELAY        = 0.06
SLOW_REVEAL        = True
REVEAL_DELAY       = 0.15
EXTRA_BLANK_LINES  = 12
SEEN_LIMIT         = 500
# ---------------------------------------------------------------------- #

ESC_INIT   = b"\x1B\x40"
ESC_UPS_ON = b"\x1B\x7B\x01"
ESC_BOLD_ON, ESC_BOLD_OFF = b"\x1B\x45\x01", b"\x1B\x45\x00"
ESC_FONT_A = b"\x1B\x4D\x00"
ESC_FEED_1 = b"\x1B\x64\x01"
SPEED_CM_S = 34300

BASE_DIR   = Path(__file__).parent
CORP_FILES = [BASE_DIR / f"corpus_S{i}.txt" for i in range(5)]

# ───── LOAD MARKOV MODELS ────────────────────────────────────────────── #
MODELS = []
for idx, path in enumerate(CORP_FILES):
    if not path.exists():
        print(f"[WARN] {path.name} missing → subsystem {idx} prints 'offline'.")
        MODELS.append(None)
    else:
        MODELS.append(markovify.Text(path.read_text(encoding="utf-8"), state_size=2))

recent: set[str] = set()
def pick_sentence(model):
    if model is None:
        return "Subsystem offline."
    for _ in range(120):
        s = model.make_sentence(max_words=80, tries=120)
        if s and s not in recent:
            break
    else:
        s = "Silent words fell softly."
    recent.add(s)
    if len(recent) > SEEN_LIMIT:
        recent.pop()
    return s

# ───── PRINTER OUTPUT ────────────────────────────────────────────────── #
def sentence_to_lines(sentence: str):
    words = re.findall(r"[a-z']+", sentence.lower()) or ["…"]
    words[0] = words[0].capitalize()
    return list(reversed(words))        # one word per line (upside‑down order)

def send(device: str, sentence: str):
    try:
        with open(device, "wb") as p:
            p.write(ESC_INIT + ESC_UPS_ON + ESC_BOLD_ON + ESC_FONT_A)
            for ln in sentence_to_lines(sentence):
                p.write(ln.encode() + b"\n"); p.flush()
                if SLOW_REVEAL:
                    time.sleep(REVEAL_DELAY)

            p.write(ESC_BOLD_OFF + ESC_FEED_1); p.flush()

            if SLOW_REVEAL:
                for _ in range(EXTRA_BLANK_LINES):
                    p.write(ESC_FEED_1); p.flush(); time.sleep(REVEAL_DELAY/2)
            else:
                p.write(ESC_FEED_1 * EXTRA_BLANK_LINES); p.flush()

            p.write(ESC_UPS_ON); p.flush()
            time.sleep(WRITE_DELAY)
    except Exception as e:
        print(f"[ERR] {device}: {e}")

# ───── SENSOR LOGIC ──────────────────────────────────────────────────── #
GPIO.setmode(GPIO.BCM)
for trig, echo in SENSOR_PINS.values():
    GPIO.setup(trig, GPIO.OUT); GPIO.output(trig, 0)
    GPIO.setup(echo, GPIO.IN)
time.sleep(0.1)

last_fire = {i: 0.0 for i in SENSOR_PINS}

def measure_cm(trig, echo):
    GPIO.output(trig, 1); time.sleep(1e-5); GPIO.output(trig, 0)
    start = time.time()
    while GPIO.input(echo) == 0:
        if time.time() - start > 0.03:
            return None
    pulse_start = time.time()
    while GPIO.input(echo) == 1:
        if time.time() - pulse_start > 0.03:
            return None
    return ((time.time() - pulse_start) * SPEED_CM_S) / 2

def fire_others(sensor_idx):
    for j in range(5):
        if j == sensor_idx or MODELS[j] is None:
            continue
        s = pick_sentence(MODELS[j])
        send(DEVICES[j], s)
        print(time.strftime("[%H:%M:%S]"),
              f"Sensor{sensor_idx} → lp{j} :", s)

def sensor_loop():
    try:
        while True:
            now = time.time()
            for idx, (trig, echo) in SENSOR_PINS.items():
                dist = measure_cm(trig, echo)
                if dist and dist < THRESH_CM and now - last_fire[idx] > DEBOUNCE_SECONDS:
                    last_fire[idx] = now
                    fire_others(idx)
            time.sleep(0.05)
    finally:
        GPIO.cleanup()

# ───── MAIN ──────────────────────────────────────────────────────────── #
if __name__ == "__main__":
    Thread(target=sensor_loop, daemon=True).start()
    print("Sensor loop active — prints only on proximity triggers.")
    try:
        while True:            # keep main thread alive
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting.")
