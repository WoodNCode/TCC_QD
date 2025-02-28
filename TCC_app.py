# Save this as app.py and run with: streamlit run app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Example input parameters
E_timber = 11000e6  # Elastic modulus of timber (Pa)
h_timber = 0.180  # Height of timber section (m)
P = 150e3  # Point load (N)
L = 2  # Span length (m)
a_timber = 0.05  # Example distance from neutral axis (m)
gamma_concrete = 0.85  # Example factor for concrete
EI_eff = 1e9  # Example effective bending stiffness (Nm²)
M_mid = (P * L) / 4  # Mid-span moment

# Calculate stresses
sigma_timber = (E_timber * a_timber * M_mid) / EI_eff
sigma_m_timber = (0.5 * E_timber * h_timber * M_mid) / EI_eff
sigma_concrete = (gamma_concrete * E_timber * a_timber * M_mid) / EI_eff
sigma_m_concrete = (0.5 * E_timber * h_timber * M_mid) / EI_eff

# Streamlit app interface
st.title("TCC Element Stress Analysis")
st.header("Input Parameters")
P = st.number_input("Point Load (N)", value=150e3)
L = st.number_input("Span Length (m)", value=2.0)
E_timber = st.number_input("Elastic Modulus of Timber (Pa)", value=11000e6)
h_timber = st.number_input("Timber Height (m)", value=0.180)
a_timber = st.number_input("Distance a_timber (m)", value=0.05)
EI_eff = st.number_input("Effective Bending Stiffness (Nm²)", value=1e9)
gamma_concrete = st.number_input("Gamma Concrete", value=0.85)

if st.button("Calculate"):
    M_mid = (P * L) / 4
    sigma_timber = (E_timber * a_timber * M_mid) / EI_eff
    sigma_m_timber = (0.5 * E_timber * h_timber * M_mid) / EI_eff
    sigma_concrete = (gamma_concrete * E_timber * a_timber * M_mid) / EI_eff
    sigma_m_concrete = (0.5 * E_timber * h_timber * M_mid) / EI_eff

    st.subheader("Stress Verification Results")
    st.write(f"**Normal Stress in Timber:** {sigma_timber/1e6:.2f} MPa")
    st.write(f"**Bending Stress in Timber:** {sigma_m_timber/1e6:.2f} MPa")
    st.write(f"**Normal Stress in Concrete:** {sigma_concrete/1e6:.2f} MPa")
    st.write(f"**Bending Stress in Concrete:** {sigma_m_concrete/1e6:.2f} MPa")
