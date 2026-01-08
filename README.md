# AVERT – Airborne Vectoring & Emergency Routing Tool

🔗 **Live Demo:**  
https://avert-emergency-vectoring-vl9p349zbyss4ucbh7tfpn.streamlit.app/

AVERT is an **EFB-style aviation decision support prototype** designed to simulate emergency diversion scenarios such as engine-out situations. It helps visualize how altitude, wind speed, and wind direction influence diversion feasibility and airport prioritization.

> ⚠️ Simulation-only prototype. Not for real-world flight operations.

---

## ✈️ Why AVERT?

In real aviation emergencies, pilots must rapidly evaluate:
- Remaining altitude / energy
- Nearby airports
- Wind effects on turns and reachability
- Maneuvering difficulty

AVERT explores how **AI-assisted decision support** can help structure these decisions visually and intuitively.

---

## 🧩 Key Features

### 🗺 Interactive EFB-Style Map
- Aircraft position displayed on a navigation map
- Nearby airports plotted dynamically
- Wind vector visualization
- Turn arcs showing maneuver effort

### 🎛 Pilot Controls
- Altitude slider
- Wind speed slider
- Wind direction slider
- Live re-computation of feasibility

### 📊 Airport Ranking (Decision Support)
- Airports ranked using:
  - Distance
  - Wind component
  - Estimated maneuvering cost
- Rankings update live as conditions change

### 🧠 AI / ML Integration
- Lightweight ML-assisted scoring (simulation-level)
- Used for **ranking assistance**, not automation
- Fully explainable, rule-aligned logic

---

## 🛠 Tech Stack

- **Python**
- **Streamlit** – interactive UI
- **Folium / Leaflet** – aviation map visualization
- **Pandas / NumPy**
- **Scikit-learn** (light ML component)

---

## 📂 Project Structure

```
AVERT_EFB/
├── app.py
├── requirements.txt
└── data/
    └── airports.csv
```

---

## 🚀 Future Enhancements

- Real-time weather (METAR / GRIB)
- Aircraft-specific performance models
- Terrain awareness
- More advanced ML ranking models
- EFB-style tablet UI refinements

---

## 📌 Disclaimer

This project is intended **strictly for educational and portfolio purposes**.  
It does **not interface with certified avionics systems**.

---


