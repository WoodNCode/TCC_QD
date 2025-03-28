import streamlit as st
import numpy as np

# Import your newly-created modules
from TCC_EC5_calc import (
    compute_section_properties,
    compute_gamma_concrete,
    compute_neutral_axes,
    compute_effective_bending_stiffness,
    compute_bending_moment_and_shear,
    compute_deflection,
    compute_stresses_and_forces
)

from TCC_plots import (
    plot_elevation_view,
    plot_cross_section,
    plot_deflection_shape
)

from TCC_report import generate_pdf_report
st.title("TCC_QD EC5 Verification")

st.markdown(
    """
This app calculates the stresses in a Timber-Concrete Composite (TCC) element using the formulas from EN 1995-1-1 Annex B.
Below, you can adjust the input parameters from the sidebar.
"""
)

# Sidebar input parameters
st.sidebar.header("Input Parameters")

E_timber_G = st.sidebar.number_input("Elastic Modulus of Timber (GPa)", value=11.0, format="%.1f", step=0.1)
E_timber = E_timber_G*1000000000
E_concrete_G = st.sidebar.number_input("Elastic Modulus of Concrete (GPa)", value=33.0, format="%.1f", step=0.1)
E_concrete = E_concrete_G*1000000000
f_m_timber_M = st.sidebar.number_input("Bending Strength in MPa", value=24.0, format="%.1f", step=0.1)
f_m_timber = f_m_timber_M * 1000*1000
f_t_timber_M = st.sidebar.number_input("Tensile Strength in MPa", value=14.0, format="%.1f", step=0.1)
f_t_timber = f_t_timber_M * 1000*1000
h_timber = st.sidebar.number_input("Height of Timber Section (m)", value=0.16)
b_timber = st.sidebar.number_input("Width of Timber Section (m)", value=0.12)
h_concrete = st.sidebar.number_input("Height of Concrete Section (m)", value=0.1)
b_concrete = st.sidebar.number_input("Width of Concrete Section (m)", value=0.4)

# Connector and load parameters
s = st.sidebar.number_input("Spacing between connectors (m)", value=0.8)
k_ser_kN_mm = st.sidebar.slider("Slip Modulus per connector (kN/mm)", min_value=10, max_value=2500, value=90, step=10, format=None, key=None, help="165 N/m is the Value for 20 cm TiComTec", on_change=None, args=None, kwargs=None, disabled=False, label_visibility="visible")
k_ser = k_ser_kN_mm * 1000 * 1000
# k_ser_kN_mm = st.sidebar.number_input("Slip Modulus per connector (kN/mm)", value=330000000, format="%.2e")

P_kN = st.sidebar.number_input("Point Load (kN)", value=80)
P=P_kN*1000
L = st.sidebar.number_input("Span Length (m)", value=1.6)

# ------------------------
#    CALCULATIONS
# ------------------------

# 1) Section Properties
A_timber, I_timber, A_concrete, I_concrete = compute_section_properties(
    b_timber, h_timber, b_concrete, h_concrete
)

# 2) Gamma Factor
gamma_concrete = compute_gamma_concrete(E_concrete, A_concrete, s, k_ser, L)

# 3) Neutral Axes
a_timber, a_concrete = compute_neutral_axes(
    E_timber, A_timber, E_concrete, A_concrete, h_timber, h_concrete, gamma_concrete
)

# 4) Effective Bending Stiffness
EI_eff = compute_effective_bending_stiffness(
    E_timber, I_timber, A_timber, a_timber,
    E_concrete, I_concrete, A_concrete, a_concrete,
    gamma_concrete
)

# 5) Bending moment and shear
M_mid, V_max = compute_bending_moment_and_shear(P, L)

# 6) Deflection curve
x_left, delta_left, x_right, delta_right = compute_deflection(EI_eff, P, L, num_points=50)

# 7) Stresses & forces
results = compute_stresses_and_forces(
    E_timber, A_timber, h_timber, f_m_timber, f_t_timber,
    E_concrete, A_concrete, h_concrete, I_concrete,
    M_mid, V_max, a_timber, a_concrete, s, EI_eff,
    gamma_concrete
)

# ------------------------
#    PLOTTING
# ------------------------

# Elevation view plot
fig_elevation = plot_elevation_view(L, s, P)
st.pyplot(fig_elevation)

# Cross-section plot
fig_cross_sec = plot_cross_section(b_concrete, h_concrete, b_timber, h_timber, a_timber)
st.pyplot(fig_cross_sec)

# Deflection shape plot
fig_deflection = plot_deflection_shape(x_left, delta_left, x_right, delta_right)
st.pyplot(fig_deflection)

# ------------------------
#    DISPLAY RESULTS
# ------------------------
st.header("Calculated Section Properties")
st.markdown(f"- **A_timber**: {A_timber:.4f} m²")
st.markdown(f"- **I_timber**: {I_timber:.4e} m⁴")
st.markdown(f"- **A_concrete**: {A_concrete:.4f} m²")
st.markdown(f"- **I_concrete**: {I_concrete:.4e} m⁴")
st.markdown(f"- **Neutral Axis Distances**: a_timber = {a_timber:.4f} m, a_concrete = {a_concrete:.4f} m")
st.markdown(f"- **Effective Bending Stiffness (EI_eff)**: {EI_eff:.4e} Nm²")
st.markdown(f"- **Gamma_concrete**: {gamma_concrete:.4f}")

st.title("TCC Element Stress Verification Results")
st.markdown("## Timber")
st.write(f"**Normal Stress in Timber:** {results['sigma_timber'] / 1e6:.2f} MPa")
st.write(f"**Bending Stress in Timber:** {results['sigma_m_timber'] / 1e6:.2f} MPa")
st.write(f"**Utilisation factor in Timber:** {results['utilisation_timber']:.3f}")

st.markdown("## Concrete")
st.write(f"**Normal Stress in Concrete:** {results['sigma_concrete'] / 1e6:.2f} MPa")
st.write(f"**Bending Stress in Concrete:** {results['sigma_m_concrete'] / 1e6:.2f} MPa")
st.write(f"**Bending Moment in Concrete:** {results['M_concrete'] / 1e3:.2f} kNm")
st.write(f"**Normal Force in Concrete:** {results['N_concrete'] / 1e3:.2f} kN")

st.markdown("## Timber Shear")
st.write(f"**Maximum Shear Stress in Timber:** {results['tau_timber_max'] / 1e6:.2f} MPa")
st.markdown(f"- **Neutral Axis position from bottom (z) // h according to EC5 B.4:** {results['h_EC_tau']*1000:.2f} mm")

st.markdown("## Connectors")
st.write(f"**Force in Connector:** {results['F_connector'] / 1e3:.2f} kN")

if st.button("Generate PDF Report", key="generate_pdf_report"):
    pdf_data = generate_pdf_report(
        E_timber_G, E_concrete_G, h_timber, b_timber,
        h_concrete, b_concrete, s, k_ser, P, L,
        results['sigma_timber'], results['sigma_m_timber'],
        results['sigma_concrete'], results['sigma_m_concrete'],
        results['M_concrete'], results['N_concrete'],
        results['tau_timber_max'], results['F_connector']
    )
    st.download_button(
        label="Download PDF Report",
        data=pdf_data,
        file_name="TCC_Stress_Verification_Report.pdf",
        mime="application/pdf",
        key="download_pdf_button"
    )