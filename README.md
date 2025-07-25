# to-off-an-ending-system
Recursive grief system with proximity-triggered thermal printer output

# To Off an Ending System

**A recursive grief engine modeled through proximity, sentence logic, and procedural degradation.**  
This is not a symbolic interface. It behaves.  
Once activated, it does not resolve — it redistributes.

---

## Overview

*To Off an Ending System* is a physical installation running on a Raspberry Pi that simulates the behavior of unresolved grief using a distributed printing system. Each of the five printers corresponds to one emotional subsystem. Proximity sensors trigger recursive activation — when you approach one node, the others respond.

---

## Subsystems

| Printer | Subsystem         | Triggered By                          |
|---------|-------------------|---------------------------------------|
| lp0     | Sense / Meaning   | Proximity to another subsystem node   |
| lp1     | Memory            | Recursive response to weight/silence |
| lp2     | Weight / Feeling  | Ritual absence                       |
| lp3     | Behaviour         | Emotional intervention               |
| lp4     | Narrative / Thread| Memory destabilization               |

> In the current version, **Sensor 4 (lp4) is deactivated due to hardware failure**. The system behaves recursively across the remaining 4.

---

## How It Works

- **Sensors:** 4 HC-SR04 ultrasonic sensors (TRIG/ECHO GPIO-paired)
- **Printers:** 5 USB thermal printers (`/dev/usb/lp0` … `lp4`)
- **Core Script:** `grief_loop.py`
- **Text Generation:** Uses [Markovify](https://github.com/jsvine/markovify) to build sentence models from `corpus_S*.txt`
- **Degradation Logic:** Structured sentences (SVO) collapse grammatically under recursion (e.g. → VO → O–O → residue)

---

## Conceptual Framework

- **Ian Bogost:** Procedural Rhetoric — systems argue through behavior, not representation
- **Victor Turner:** Ritual as suspended process — looping without closure
- **Ecological Model of Emotion:** Grief is distributed, non-linear, recursive
- **Christian Boltanski & Rafael Lozano-Hemmer:** Residue, illegibility, accumulation

---

## Files

- `grief_loop.py` – main logic loop (sensor read, print trigger, sentence selection)
- `corpus_S0.txt` … `corpus_S4.txt` – text corpora for each subsystem
- `demo_sequence.py` – optional one-off print sequences for testing sentence logic

---

## Requirements

- Raspberry Pi (3 or later)
- 4–5 USB thermal printers
- 4 HC-SR04 sensors
- Python 3.x
- Dependencies:

```bash
pip install markovify RPi.GPIO
