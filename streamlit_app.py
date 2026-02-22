import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from app.models import calculate_slope_stability

st.set_page_config(page_title="Geophysics Stability Pro 2026", layout="wide")

st.title("🏗️ Tailings Dam Stability Analysis")
st.sidebar.header("Circle Parameters")

# Sidebar Controls
xc = st.sidebar.slider("Center X", 50.0, 120.0, 95.0)
yc = st.sidebar.slider("Center Y", 50.0, 100.0, 80.0)
r = st.sidebar.slider("Radius R", 30.0, 80.0, 60.0)

st.sidebar.header("Soil Properties")
c = st.sidebar.number_input("Cohesion (c')", value=15.0)
phi = st.sidebar.number_input("Friction Angle (phi')", value=25.0)

# Fixed Dam Geometry
dx = np.array([40, 70, 100, 130])
dy = np.array([10, 45, 45, 14])
wx = np.array([40, 85, 110, 130])
wy = np.array([10, 30, 40, 42])

# RUN CALCULATION
fs, slices = calculate_slope_stability(xc, yc, r, dx, dy, wx, wy, c=c, phi=phi)

# OUTPUT DISPLAY
col1, col2 = st.columns([1, 3])

with col1:
    st.metric(label="Final Factor of Safety", value=fs if fs else "N/A")
    if fs and fs < 1.0:
        st.error("DANGER: SLOPE FAILURE LIKELY")
    elif fs and fs < 1.5:
        st.warning("Caution: Marginal Stability")
    else:
        st.success("Stable Condition")

with col2:
    # Plotting Logic
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dx, dy, 'k-', linewidth=3, label="Dam Surface")
    ax.fill_between(dx, dy, color='brown', alpha=0.1)
    ax.plot(wx, wy, 'b--', label="Phreatic Line")
    
    if fs:
        # Plot Circle
        theta = np.linspace(0, 2*np.pi, 500)
        ax.plot(xc + r*np.cos(theta), yc + r*np.sin(theta), 'r--', alpha=0.3)
        ax.scatter([xc], [yc], color='red', marker='x')
        
        # Plot Slices
        for s in slices:
            ax.bar(s['x_mid'], s['h'], width=s['b'], bottom=s['y_bot'], 
                   color='orange', alpha=0.5, edgecolor='black', linewidth=0.5)

    ax.set_aspect('equal')
    ax.set_title(f"Stability Map (FS: {fs})")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)