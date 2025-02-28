import streamlit as st
import numpy as np
import matplotlib.pyplot as plt


st.title("TCC_QD EC5 Verification")

st.markdown(
    """
This app calculates the stresses in a Timber-Concrete Composite (TCC) element using the formulas from EN 1995-1-1 Annex B.
Below, you can adjust the input parameters from the sidebar.
"""
)

# Sidebar input parameters
st.sidebar.header("Input Parameters")

E_timber_g = st.sidebar.number_input(
    "Elastic Modulus of Timber (GPa)", value=11.0, format="%.1f", step=0.1
)
E_timber = E_timber_g*1000000000
E_concrete_g = st.sidebar.number_input(
    "Elastic Modulus of Concrete (GPa)", value=33.0, format="%.1f", step=0.1
)
E_concrete = E_concrete_g*1000000000
h_timber = st.sidebar.number_input("Height of Timber Section (m)", value=0.16)
b_timber = st.sidebar.number_input("Width of Timber Section (m)", value=0.12)
h_concrete = st.sidebar.number_input("Height of Concrete Section (m)", value=0.1)
b_concrete = st.sidebar.number_input("Width of Concrete Section (m)", value=0.4)

# Connector and load parameters
s = st.sidebar.number_input("Spacing between connectors (m)", value=0.8)
k_ser = st.sidebar.number_input("Slip Modulus per connector (N/m)", value=330000000, format="%.2e")

P = st.sidebar.number_input("Point Load (N)", value=80e3, format="%.2e")
L = st.sidebar.number_input("Span Length (m)", value=1.6)

# --- Calculated Section Properties ---
# Cross-sectional areas
A_timber = b_timber * h_timber
A_concrete = b_concrete * h_concrete

# Moments of inertia
I_timber = (b_timber * h_timber**3) / 12
I_concrete = (b_concrete * h_concrete**3) / 12

# Calculate bending moment at mid-span
M_mid = (P * L) / 4
V_max = P*L/2

# Compute gamma factor
gamma_concrete = 1 / (1 + (np.pi**2 * E_concrete * A_concrete * s) / (k_ser * L**2))

# Compute neutral axis distances
a_timber = (gamma_concrete * E_concrete * A_concrete * (h_concrete + h_timber)) / (2*(gamma_concrete * E_concrete * A_concrete) + (E_timber * A_timber))
a_concrete = (h_timber / 2) - a_timber + (h_concrete / 2)

# Elevation view
plt.figure(figsize=(8, 2))
plt.plot([0, L], [0, 0], color='black', linewidth=2, label='Beam')
plt.scatter([L/2], [0], color='blue', s=100, label='Point Load')
plt.scatter([0, L], [0, 0], color='black', marker='^', s=100, label='Supports')
plt.scatter(np.linspace(s/2, L - s/2, int(L/s)), np.zeros(int(L/s)), color='red', label='Connectors')
plt.xlabel("Beam Length (m)")
plt.ylabel("Elevation")
plt.title("Elevation View of TCC Element")
plt.legend()
plt.grid()
st.pyplot(plt)

# Cross-section plot
plt.figure(figsize=(8, 6))
plt.fill_between([-b_concrete/2, b_concrete/2], 0, h_concrete, color='gray', alpha=0.7, label='Concrete Slab')
plt.fill_between([-b_timber/2, b_timber/2], -h_timber, 0, color='saddlebrown', alpha=0.7, label='Timber Beam')
plt.scatter([0], [0], color='red', label='Connectors')
plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
plt.axhline(-h_timber/2 + a_timber, color='blue', linestyle='-', linewidth=2, label='Neutral Axis')
plt.xlabel("Width (m)")
plt.ylabel("Height (m)")
plt.title("Cross-section of TCC Element")
plt.legend()
plt.grid()
st.pyplot(plt)

# --- Effective Bending Stiffness ---
EI_eff = (E_timber * I_timber + 
          E_concrete * I_concrete + 
          E_timber * A_timber * a_timber**2 + 
          gamma_concrete * E_concrete * A_concrete * a_concrete**2)

# Deflection curve computation
x_left = np.linspace(0, L/2, 50)
x_right = np.linspace(L/2, L, 50)
delta_x_left = (P * x_left**3 / 12 - P * L**2 * x_left / 16) / EI_eff
delta_x_right = delta_x_left[::-1]  # Symmetric about mid-span

# Plot deflection shape
plt.figure(figsize=(8, 4))
plt.plot(x_left, delta_x_left * 1e3, label='Deflection (mm)', color='blue')
plt.plot(x_right, delta_x_right * 1e3, color='blue')
plt.axhline(0, color='black', linestyle='--', linewidth=0.8)
plt.xlabel("Beam Length (m)")
plt.ylabel("Deflection (mm)")
plt.title("Deflection of TCC Element using Gamma Method")
plt.legend()
plt.grid()
st.pyplot(plt)

# --- Output the Calculated Properties and Stresses ---
st.header("Calculated Section Properties")
st.markdown(f"- **A_timber**: {A_timber:.4f} m²")
st.markdown(f"- **I_timber**: {I_timber:.4e} m⁴")
st.markdown(f"- **A_concrete**: {A_concrete:.4f} m²")
st.markdown(f"- **I_concrete**: {I_concrete:.4e} m⁴")
st.markdown(f"- **Neutral Axis Distances**: a_timber = {a_timber:.4f} m, a_concrete = {a_concrete:.4f} m")
st.markdown(f"- **Effective Bending Stiffness (EI_eff)**: {EI_eff:.4e} Nm²")
st.markdown(f"- **Gamma_concrete)**: {gamma_concrete:.4f}")

# Calculate normal and bending stresses
sigma_timber = (E_timber * a_timber * M_mid) / EI_eff
sigma_m_timber = (0.5 * E_timber * h_timber * M_mid) / EI_eff

sigma_concrete = (gamma_concrete * E_timber * a_timber * M_mid) / EI_eff
sigma_m_concrete = (0.5 * E_timber * h_timber * M_mid) / EI_eff

# Calculate shear stress in Timber
# Note: This formula is taken from your script, but verify it since it appears non-standard.
tau_timber_max = (0.5 * E_timber * b_timber * h_timber**2) *V_max / (b_timber*EI_eff)
