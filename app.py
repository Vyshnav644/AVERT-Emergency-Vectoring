import math
import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.ensemble import RandomForestRegressor

# ------------------------------------------------
# PAGE CONFIG (EFB STYLE)
# ------------------------------------------------
st.set_page_config(
    page_title="AVERT – Emergency Vectoring",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0f172a; }
    h1, h2, h3, p, label { color: #e5e7eb; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("AVERT – Airborne Vectoring & Emergency Routing")
st.caption("EFB-style simulation • Decision support only • ML-assisted ranking")

# ------------------------------------------------
# AIRCRAFT POSITIONS (SIMULATED GPS)
# ------------------------------------------------
aircraft_positions = {
    "Bengaluru (VOBL)": (12.9716, 77.5946),
    "Hyderabad (VOHS)": (17.2403, 78.4294),
    "Chennai (VOMM)": (12.9941, 80.1709),
    "Mumbai (VABB)": (19.0896, 72.8656),
}

# ------------------------------------------------
# LOAD AIRPORT DATA (CSV)
# ------------------------------------------------
airports_df = pd.read_csv("data/airports.csv")

# ------------------------------------------------
# LAYOUT
# ------------------------------------------------
left_col, right_col = st.columns([1.2, 3])

# ------------------------------------------------
# CONTROLS (LEFT PANEL)
# ------------------------------------------------
with left_col:
    st.subheader("Aircraft State")

    selected_pos = st.selectbox(
        "Aircraft Position (Simulated)",
        list(aircraft_positions.keys())
    )
    aircraft_lat, aircraft_lon = aircraft_positions[selected_pos]

    altitude = st.slider("Altitude (ft)", 5000, 25000, 18000, step=500)
    wind_speed = st.slider("Wind Speed (kt)", 0, 50, 30, step=5)
    wind_dir = st.slider("Wind Direction (°)", 0, 360, 270, step=10)

    st.markdown("---")
    ml_enabled = st.toggle("Enable ML-assisted ranking", value=True)

# ------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------
def distance_nm(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 60

def bearing_deg(lat1, lon1, lat2, lon2):
    return (math.degrees(math.atan2(lon2 - lon1, lat2 - lat1)) + 360) % 360

# ------------------------------------------------
# TRAIN ML MODEL (SIMULATED SCENARIOS)
# ------------------------------------------------
np.random.seed(42)

X, y = [], []

for _ in range(800):
    alt = np.random.uniform(5000, 25000)
    dist = np.random.uniform(30, 400)
    wind = np.random.uniform(-40, 40)
    X.append([alt, dist, wind])
    y.append((alt / 12000) + (wind / 45) - (dist / 180))

ml_model = RandomForestRegressor(n_estimators=150, random_state=42)
ml_model.fit(X, y)

# ------------------------------------------------
# MAP + AVERT LOGIC
# ------------------------------------------------
with right_col:
    st.subheader("Navigation Display")

    m = folium.Map(
        location=[aircraft_lat, aircraft_lon],
        zoom_start=6,
        tiles="CartoDB positron"
    )

    # Aircraft marker
    folium.Marker(
        [aircraft_lat, aircraft_lon],
        tooltip="Aircraft",
        icon=folium.Icon(color="blue", icon="plane", prefix="fa")
    ).add_to(m)

    # ---------------- WIND VECTOR ----------------
    wind_rad = math.radians(wind_dir + 180)
    arrow_scale = 0.25 + wind_speed / 120

    wind_lat = aircraft_lat + arrow_scale * math.cos(wind_rad)
    wind_lon = aircraft_lon + arrow_scale * math.sin(wind_rad)

    folium.PolyLine(
        [[wind_lat, wind_lon], [aircraft_lat, aircraft_lon]],
        color="lime",
        weight=4,
        tooltip=f"Wind {wind_dir}° / {wind_speed} kt"
    ).add_to(m)

    rankings = []

    # ---------------- AIRPORT LOOP ----------------
    for _, row in airports_df.iterrows():
        ap_lat, ap_lon = row["lat"], row["lon"]
        dist = distance_nm(aircraft_lat, aircraft_lon, ap_lat, ap_lon)
        brg = bearing_deg(aircraft_lat, aircraft_lon, ap_lat, ap_lon)

        # Wind component (tailwind positive)
        rel = abs((brg - wind_dir + 180) % 360 - 180)
        wind_comp = wind_speed * math.cos(math.radians(rel))

        # Rule-based score
        rule_score = (altitude / 12000) + (wind_comp / 45) - (dist / 160)

        # ML score
        ml_score = ml_model.predict([[altitude, dist, wind_comp]])[0]

        final_score = (
            0.6 * rule_score + 0.4 * ml_score
            if ml_enabled else rule_score
        )

        # Altitude-based reach limit
        max_range = altitude / 90

        if dist > max_range:
            status, color = "UNREACHABLE", "red"
        elif final_score > 1.1:
            status, color = "HIGH", "green"
        elif final_score > 0.8:
            status, color = "MEDIUM", "orange"
        else:
            status, color = "LOW", "red"

        rankings.append((row["icao"], row["name"], final_score, status, dist, brg))

        # Airport marker
        folium.CircleMarker(
            [ap_lat, ap_lon],
            radius=7,
            color=color,
            fill=True,
            fill_opacity=0.85,
            tooltip=f"{row['icao']} – {row['name']} | {int(dist)} nm | {status}"
        ).add_to(m)

        # ---------------- TURN ARC ----------------
        turn_radius = max(0.25, altitude / 70000)
        arc = []

        for t in range(20):
            a = math.radians(brg - 90 + t * 9)
            arc.append([
                aircraft_lat + turn_radius * math.cos(a),
                aircraft_lon + turn_radius * math.sin(a)
            ])

        folium.PolyLine(arc, color=color, weight=2, opacity=0.6).add_to(m)

    st_folium(m, width=980, height=640)

# ------------------------------------------------
# RANKING PANEL
# ------------------------------------------------
st.markdown("---")
st.subheader("AVERT – Ranked Diversion Options")

rankings.sort(key=lambda x: x[2], reverse=True)

for i, (icao, name, score, status, dist, brg) in enumerate(rankings, start=1):
    st.write(
        f"**{i}. {icao} – {name}** | {status} | {int(dist)} nm | "
        f"Bearing {int(brg)}° | Score {score:.2f}"
    )
